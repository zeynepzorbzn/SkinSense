import pandas as pd
from database import SessionLocal, engine
import models

# Veritabanı tablolarını (Eğer yoksa) oluştur
models.Base.metadata.create_all(bind=engine)

def import_cosing_to_db():
    db = SessionLocal()
    print("⏳ CosIng Devasa Veri Seti Okunuyor (Avrupa Birliği Veritabanı)...")
    
    try:
        # skiprows=9 ile baştaki o gereksiz başlık kısımlarını atlıyoruz!
        df = pd.read_csv('cosing.csv', skiprows=9)
    except FileNotFoundError:
        print("❌ HATA: 'cosing.csv' dosyası bulunamadı. İsmini doğru değiştirdiğinden emin ol.")
        return

    print("🚀 30.000 satırlık veritabanına aktarım başlıyor (Bu birkaç dakika sürebilir)...")
    
    eklenen_sayi = 0
    atlanan_sayi = 0
    
    for index, row in df.iterrows():
        madde_adi = str(row['INCI name']).strip()
        
        # Boş satırları atla
        if not madde_adi or pd.isna(row['INCI name']) or madde_adi == 'nan':
            continue
            
        # Daha önce eklediysek atla (Çift kayıt olmasın)
        if db.query(models.Ingredient).filter(models.Ingredient.name == madde_adi).first():
            atlanan_sayi += 1
            continue

        # Verileri toparla
        faydalar = str(row['Function']).strip()
        faydalar = faydalar if faydalar != 'nan' else "Genel kozmetik formül bileşeni."
        
        kisitlama = str(row['Restriction']).strip()
        riskler = f"AB Kısıtlaması: {kisitlama}" if kisitlama != 'nan' and kisitlama != '' else "Düşük risk (Avrupa Birliği onaylı)"
        
        # Yeni Madde Modeli
        yeni_madde = models.Ingredient(
            name=madde_adi,
            benefits=faydalar.capitalize(),
            concerns=riskler,
            is_comedogenic=False, # CosIng bu detayı vermez, varsayılan olarak güvenli kabul ediyoruz
            skin_type_compatibility="Tüm Ciltler"
        )
        
        db.add(yeni_madde)
        eklenen_sayi += 1
        
        # Bilgisayarın belleği (RAM) şişmesin diye her 2000 maddede bir veritabanına kaydet
        if eklenen_sayi % 2000 == 0:
            db.commit()
            print(f"🔄 Şu ana kadar {eklenen_sayi} madde başarıyla içeri aktarıldı...")

    # Geride kalan son partiyi de kaydet
    db.commit()
    db.close()
    print(f"✅ BÜYÜK AKTARIM TAMAMLANDI! Toplam {eklenen_sayi} yeni içerik eklendi, {atlanan_sayi} içerik zaten mevcuttu.")

if __name__ == "__main__":
    import_cosing_to_db()