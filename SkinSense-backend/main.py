from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
import requests
import difflib
import re
import io
import os
import tempfile
import pytesseract
from PIL import Image, ImageEnhance
from pillow_heif import register_heif_opener

import models
import auth
from database import engine, get_db

# Mac için Apple Fotoğraf formatı (.heic) okuyucusunu aktif et
register_heif_opener()

# Mac için Tesseract'ın tam konumu
pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'

# Tabloları oluşturur
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SkinSense API",
    description="Barkod, Fotoğraf ve NLP Destekli Kişiselleştirilmiş İçerik Analiz Motoru",
    version="3.0.0"
)

# API'nin React'ten gelen isteklere izin vermesini sağlar
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router)

# --- İSTEK FORMATLARI (PYDANTIC MODELLERİ) ---
class AnalyzeRequest(BaseModel):
    ingredients_text: str
    skin_type: str = "Normal"
    skin_concern: str = "Yok"

class BarcodeRequest(BaseModel):
    barcode: str
    skin_type: str
    skin_concern: str = "Yok"

class ManualRequest(BaseModel):
    ingredients: str
    skin_type: str
    skin_concern: str = "Yok"

class HistoryCreate(BaseModel):
    barcode: str
    product_name: str
    uyum_skoru: int

class ProductNameRequest(BaseModel):
    product_name: str
    skin_type: str
    skin_concern: str = "Yok"

# --- KÖK DİZİN ---
@app.get("/")
def read_root():
    return {"mesaj": "SkinSense Yapay Zeka Motoru Aktif! 🚀"}


# --- ANA NLP VE DERMATOLOJİ MOTORU ---
def perform_analysis(ingredients_text: str, user_skin_type: str, user_skin_concern: str, db: Session):

    
    # 1. OCR Metin Temizleyici
    temiz_metin = ingredients_text.replace('\n', ',').replace('\r', ',').replace('.', ',').replace('/', ',')
    temiz_metin = re.sub(r'[^\w\s,\-]', ' ', temiz_metin)
    ingredients_list = [ing.strip().lower() for ing in temiz_metin.split(',') if len(ing.strip()) > 2]
    if not ingredients_list:
        return {
            "uyum_skoru": 0, 
            "kisisel_uyarilar": ["İçerik listesi okunamadı, lütfen daha net bir fotoğraf çekin."], 
            "risk_skoru": {}, 
            "icerik_detaylari": []
        }
    db_ingredients = db.query(models.Ingredient).all()

    eslesme_sayisi = 0
    # -----------------------------------------------

    for ing_name in ingredients_list:
        # Veritabanında ismi eşleşen maddeyi buluyoruz (Büyük/küçük harf duyarsız)
        secilen_madde = next((item for item in db_ingredients if item.name.lower() == ing_name), None)
        
        # Sadece eşleşme bulunduysa işlemlerimizi yapıyoruz
    if secilen_madde:
            eslesme_sayisi += 1
            
    # --- SONUÇ KONTROLÜ ---
    # Eğer hiç içerik bulamadıysak veya eşleşme oranı çok düşükse 100 verme!
    if eslesme_sayisi == 0 or (eslesme_sayisi / len(ingredients_list) < 0.2):
        return {
            "uyum_skoru": 0,
            "kisisel_uyarilar": ["Ürün içeriği net okunamadı veya veritabanımızla eşleşmedi. Lütfen etiketi daha net çekin."],
            "icerik_detaylari": []
        }

    analiz_sonucu = {
        "uyum_skoru": 100,
        "kisisel_uyarilar": [],
        "risk_skoru": {},
        "icerik_detaylari": []
    }

    # 2. Cilt Problemi & Risk Sözlükleri
    leke_karsiti = ["niacinamide", "vitamin c", "ascorbic acid", "arbutin", "tranexamic acid", "licorice", "glycolic acid"]
    akne_karsiti = ["salicylic acid", "zinc", "tea tree", "niacinamide", "sulfur", "centella"]
    yaslanma_karsiti = ["retinol", "peptide", "collagen", "bakuchiol", "adenosine", "hyaluronic acid"]
    
    komedojenikler = ["oil", "butter", "stearate", "myristate", "palmitate", "cetearyl alcohol", "ceteareth", "wax", "lanolin", "mineral oil", "petrolatum"]
    kurutucu_alkoller = ["alcohol denat", "isopropyl alcohol", "ethanol", "sd alcohol"]
    nemlendirici_ve_onarici = ["ceramide", "hyaluronic acid", "sodium hyaluronate", "glycerin", "panthenol", "allantoin", "squalane", "peptide"]

    nem_destegi_sayaci = 0
    hedef_cozum_sayaci = 0

    # 3. Eşleştirme Döngüsü (Slug Sistemi)
    for ing_name in ingredients_list:
        saf_isim = ing_name.strip().lower()
        ultra_temiz_isim = re.sub(r'[^a-z]', '', saf_isim) # Boşlukları siler
        
        if len(ultra_temiz_isim) < 3:
            continue

        secilen_madde = None
        en_yuksek_skor = 0

        for ing_data in db_ingredients:
            db_isim = ing_data.name.lower()
            ultra_temiz_db = re.sub(r'[^a-z]', '', db_isim)

            if ultra_temiz_isim == ultra_temiz_db or ultra_temiz_db in ultra_temiz_isim:
                secilen_madde = ing_data
                break
            
            benzerlik = difflib.SequenceMatcher(None, ultra_temiz_isim, ultra_temiz_db).ratio()
            if benzerlik > 0.82 and benzerlik > en_yuksek_skor: 
                en_yuksek_skor = benzerlik
                secilen_madde = ing_data

        if secilen_madde:
            madde_ismi = secilen_madde.name.lower()
            uzman_yorumu = secilen_madde.benefits if secilen_madde.benefits != "Genel kozmetik formül bileşeni." else "Standart formül bileşeni."
            madde_riski = "Düşük"
            puan_cezasi = 0

            # Cilt Problemine Özel Yorumlar
            if user_skin_concern == "Leke/Renk Eşitsizliği" and any(k in madde_ismi for k in leke_karsiti):
                hedef_cozum_sayaci += 1
                uzman_yorumu = "🌟 HARİKA: Leke probleminiz için aydınlatıcı içerik!"
            elif user_skin_concern == "Akne/Sivilce" and any(k in madde_ismi for k in akne_karsiti):
                hedef_cozum_sayaci += 1
                uzman_yorumu = "🌟 HARİKA: Akne probleminizle savaşacak aktif bileşen!"
            elif user_skin_concern == "Kırışıklık/Yaşlanma" and any(k in madde_ismi for k in yaslanma_karsiti):
                hedef_cozum_sayaci += 1
                uzman_yorumu = "🌟 HARİKA: Anti-aging ve hücre yenileyici içerik!"

            # Klasik Risk Analizleri
            if any(kelime in madde_ismi for kelime in komedojenikler) and "tea tree" not in madde_ismi:
                if user_skin_type in ["Yağlı", "Karma"]:
                    puan_cezasi += 10
                    madde_riski = "Yüksek"
                    uzman_yorumu += " (DİKKAT: Gözenek tıkayıcıdır. Yağlı ciltte sivilce yapabilir.)"
                else:
                    puan_cezasi += 2
                    madde_riski = "Orta"

            if any(kelime in madde_ismi for kelime in kurutucu_alkoller):
                if user_skin_type in ["Kuru", "Hassas"]:
                    puan_cezasi += 15
                    madde_riski = "Yüksek"
                    uzman_yorumu += " (DİKKAT: Cildi ciddi oranda kurutur ve bariyeri zedeler!)"

            if any(kelime in madde_ismi for kelime in nemlendirici_ve_onarici):
                nem_destegi_sayaci += 1

            analiz_sonucu["uyum_skoru"] -= puan_cezasi

            analiz_sonucu["icerik_detaylari"].append({
                "madde_adi": secilen_madde.name.title(),
                "fayda": secilen_madde.benefits,
                "risk_seviyesi": madde_riski,
                "degerlendirme": uzman_yorumu
            })
                
        else:
            analiz_sonucu["icerik_detaylari"].append({
                "madde_adi": ing_name.title(),
                "fayda": "Bilinmiyor",
                "risk_seviyesi": "Bilinmiyor",
                "degerlendirme": "Geniş veritabanımızda net bir eşleşme bulunamadı."
            })

    # 4. Genel Rapor
    if user_skin_type == "Kuru" and nem_destegi_sayaci < 2:
        analiz_sonucu["uyum_skoru"] -= 15
        if "Kuru cildiniz için yeterli nemlendirici içerik bulunmuyor." not in analiz_sonucu["kisisel_uyarilar"]:
            analiz_sonucu["kisisel_uyarilar"].append("Kuru cildiniz için yeterli nemlendirici içerik bulunmuyor.")

    if user_skin_concern != "Yok" and hedef_cozum_sayaci > 0:
        analiz_sonucu["kisisel_uyarilar"].append(f"🎯 Ürün, '{user_skin_concern}' probleminize yönelik {hedef_cozum_sayaci} adet faydalı aktif içeriyor.")
    elif user_skin_concern != "Yok" and hedef_cozum_sayaci == 0:
        analiz_sonucu["uyum_skoru"] -= 5
        analiz_sonucu["kisisel_uyarilar"].append(f"ℹ️ '{user_skin_concern}' probleminizi çözecek spesifik bir aktif içerik bulunamadı.")

    if analiz_sonucu["uyum_skoru"] < 0:
        analiz_sonucu["uyum_skoru"] = 0

    return analiz_sonucu


# --- APİ ROTALARI (ENDPOINTS) ---

@app.post("/analyze/text")
def analyze_by_text(request: AnalyzeRequest, db: Session = Depends(get_db)):
    return perform_analysis(request.ingredients_text, request.skin_type, request.skin_concern, db)

@app.post("/analyze/barcode")
def analyze_by_barcode(request: BarcodeRequest, db: Session = Depends(get_db)):
    api_url = f"https://world.openbeautyfacts.org/api/v2/product/{request.barcode}.json"
    headers = {"User-Agent": "SkinSenseApp/1.0"}
    
    response = requests.get(api_url, headers=headers, timeout=20)
    
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="Bu barkod OpenBeautyFacts veritabanında henüz kayıtlı değil.")
    elif response.status_code != 200:
        raise HTTPException(status_code=500, detail="OpenBeautyFacts sunucusuna şu an ulaşılamıyor.")
        
    data = response.json()
    product_data = data.get("product", {})
    
    ingredients_text = product_data.get("ingredients_text", "")
    if not ingredients_text:
        ingredients_text = product_data.get("ingredients_text_en", "") 
        
    if not ingredients_text:
        raise HTTPException(status_code=400, detail="Ürün bulundu ancak veritabanında içerik listesi (ingredients) girilmemiş.")

    return {
        "urun_adi": product_data.get("product_name", "Bilinmeyen Ürün"),
        "marka": product_data.get("brands", "Bilinmeyen Marka"),
        "analiz_raporu": perform_analysis(ingredients_text, request.skin_type, request.skin_concern, db)
    }

@app.post("/analyze/manual")
def analyze_manual(request: ManualRequest, db: Session = Depends(get_db)):
    if not request.ingredients.strip():
        raise HTTPException(status_code=400, detail="Lütfen analiz edilecek içerik listesini girin.")
        
    return {
        "urun_adi": "Özel İçerik Analizi",
        "marka": "Manuel Giriş",
        "analiz_raporu": perform_analysis(request.ingredients, request.skin_type, request.skin_concern, db)
    }

@app.post("/analyze/image")
async def analyze_image(file: UploadFile = File(...), skin_type: str = Form("Normal"), skin_concern: str = Form("Yok"), db: Session = Depends(get_db)):
    
    try:
        contents = await file.read()
        
        try:
            image = Image.open(io.BytesIO(contents))
            # Görüntü iyileştirme
            image = image.convert('L')
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.0)
            sharp_enhancer = ImageEnhance.Sharpness(image)
            image = sharp_enhancer.enhance(1.5)
        except Exception:
            raise HTTPException(status_code=400, detail="Bu dosya formatı desteklenmiyor. Lütfen JPG, PNG veya HEIC yükleyin.")

        temp_path = ""
        try:
            with tempfile.NamedTemporaryFile(suffix=".bmp", delete=False) as temp_file:
                temp_path = temp_file.name
                image.save(temp_path, format="BMP")
            
            extracted_text = pytesseract.image_to_string(temp_path, lang='eng', config='--psm 6')
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Tesseract Okuma Hatası: {str(e)}")
        finally:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
        
        if len(extracted_text.strip()) < 20:
            raise HTTPException(status_code=400, detail="Fotoğraftan okunabilir içerik listesi bulunamadı.")

        return {
            "urun_adi": "Fotoğraf Analizi",
            "marka": "Kamera Taraması",
            "analiz_raporu": perform_analysis(extracted_text, skin_type, skin_concern, db),
            "okunan_metin": extracted_text 
        }
        
    except HTTPException as custom_error:
        raise custom_error
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bilinmeyen bir hata: {str(e)}")


# --- GEÇMİŞ (HISTORY) ROTALARI ---
@app.post("/history/save")
def save_scan_history(item: HistoryCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    yeni_tarama = models.ScanHistory(
        user_id=current_user.id,
        barcode=item.barcode,
        product_name=item.product_name,
        uyum_skoru=item.uyum_skoru
    )
    db.add(yeni_tarama)
    db.commit()
    return {"mesaj": "Ürün tarama geçmişine başarıyla eklendi!"}

@app.get("/history/me")
def get_my_history(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    # Kullanıcının geçmişini, en son taradığı en üstte olacak şekilde getiriyoruz
    gecmis = db.query(models.ScanHistory).filter(models.ScanHistory.user_id == current_user.id).order_by(models.ScanHistory.id.desc()).all()
    
    # Kullanıcıya sadece isim ve skor değil, tarihi de verelim ki günlüğü olsun
    return [{"id": h.id, "urun_adi": h.product_name, "uyum_skoru": h.uyum_skoru, "tarih": h.created_at} for h in gecmis]

import urllib.parse # Bunu importlara eklemene gerek yok, doğrudan fonksiyon içinde kullanacağız ama istersen en üste de yazabilirsin.

@app.post("/analyze/name")
def analyze_by_name(request: ProductNameRequest, db: Session = Depends(get_db)):
    # Kullanıcının girdiği terime "creme" veya "cream" gibi yaygın ekler ekleyebiliriz
    # Veya sadece "Bioderma Atoderm" gibi anahtar kelimelerle arama yaptırabiliriz
    
    # KÜÇÜK BİR İPUCU: Kullanıcı "krem" yazarsa onu "cream" ile değiştirerek şansını artırıyoruz
    arama_terimi = request.product_name.lower().replace("krem", "cream")
    
    encoded_name = urllib.parse.quote(arama_terimi)
    api_url = f"https://world.openbeautyfacts.org/cgi/search.pl?search_terms={encoded_name}&search_simple=1&action=process&json=1"
    
    headers = {"User-Agent": "SkinSenseApp/1.0"}
    
    response = requests.get(api_url, headers=headers, timeout=20)
    
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="OpenBeautyFacts sunucusuna şu an ulaşılamıyor.")
        
    data = response.json()
    products = data.get("products", [])
    
    if not products:
        raise HTTPException(status_code=404, detail=f"'{request.product_name}' adında bir ürün bulunamadı. İsmi İngilizce veya orijinal markasıyla yazmayı deneyin.")
        
    # Akıllı Seçici: Gelen sonuçlar arasında içerik listesi (ingredients) GİRİLMİŞ olan ilk ürünü bul
    selected_product = None
    ingredients_text = ""
    
    for prod in products:
        ingredients_text = prod.get("ingredients_text", "") or prod.get("ingredients_text_en", "")
        if ingredients_text:
            selected_product = prod
            break
            
    if not selected_product:
        raise HTTPException(status_code=400, detail="Ürün bulundu ancak OpenBeautyFacts veritabanında içerik listesi henüz girilmemiş.")

    # Ürünü ve içeriğini bulduysak doğrudan kendi Dermatolog motorumuza yolluyoruz!
    return {
        "urun_adi": selected_product.get("product_name", request.product_name),
        "marka": selected_product.get("brands", "Bilinmeyen Marka"),
        "analiz_raporu": perform_analysis(ingredients_text, request.skin_type, request.skin_concern, db)
    }