# SkinSense 🧴✨

SkinSense, kozmetik ürünlerin içeriklerini barkod veya ürün ismi üzerinden analiz eden, kullanıcı sağlığını ön planda tutan **AI destekli bir cross-platform** uygulamadır. Proje, görüntü işleme, veri eşleme ve modern web teknolojilerini bir araya getiren bir mühendislik çözümüdür.

---

## 🛠 Teknik Mimari (Tech Stack)

### Backend & API
*   **Dil:** Python
*   **Framework:** FastAPI (Asenkron request handling ile yüksek performans)
*   **Sunucu:** Uvicorn (ASGI server)
*   **Veritabanı Yönetimi:** PostgreSQL, SQLAlchemy (ORM ile güvenli veri sorgulama)

### AI, ML & Veri Bilimi
*   **OCR (Optik Karakter Tanıma):** PyTesseract (Ürün etiketlerindeki içerik listesini metne dönüştürme)
*   **Görüntü İşleme:** OpenCV (OCR öncesi görüntü optimizasyonu ve preprocessing)
*   **Veri Analizi & İşleme:** Pandas, NumPy (İçerik verilerinin temizlenmesi ve yapılandırılması)
*   **Derin Öğrenme:** PyTorch (Model eğitme ve tahminleme pipeline'ı)
*   **Makine Öğrenmesi:** Scikit-learn (İçerik kategorizasyon modelleri)

### Frontend & Mobil
*   **Web Framework:** Next.js (SEO ve performans odaklı yapı)
*   **UI/UX:** React, Tailwind CSS (Modern ve responsive tasarım)
*   **Cross-Platform Yapı:** Mobil uyumlu arayüz yönetimi

### Geliştirme & Araçlar
*   **Versiyon Kontrol:** Git, GitHub
*   **API Test:** Postman
*   **Environment Management:** Python Virtual Environments (venv)
*   **Containerization:** Docker (Deployment hazırlığı)

---

## 🚀 Temel Özellikler

*   **Akıllı OCR Motoru:** Ürün etiketlerini saniyeler içinde dijital metne çevirir.
*   **İçerik Analiz Sistemi:** Ürün içeriklerini veritabanı ile eşleyerek riskli maddeleri tespit eder.
*   **Yüksek Performanslı API:** Asenkron mimari sayesinde çoklu kullanıcı isteklerini yönetebilir.
*   **Cross-Platform Tasarım:** Web ve mobil cihazlarda kesintisiz kullanıcı deneyimi sunar.

---

## ⚙️ Kurulum & Çalıştırma (Quick Start)

1.  **Repoyu klonlayın:**

    git clone [https://github.com/zeynepzorbzn/SkinSense.git](https://github.com/zeynepzorbzn/SkinSense.git)
    cd SkinSense
    ```

2.  **Sanal ortamı oluşturun ve aktifleştirin:**

    python -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
    ```

3.  **Bağımlılıkları yükleyin:**

    pip install -r requirements.txt
    ```

4.  **Uygulamayı başlatın:**

    uvicorn main:app --reload
    ```

---

## 📂 Proje Yapısı
- `/backend`: FastAPI uygulama kodları, model dosyaları ve veritabanı bağlantıları.
- `/frontend`: Next.js ve React bileşenleri.
- `/data`: İçerik analizine yönelik veri setleri ve örnek dosyalar.
- `requirements.txt`: Tüm proje bağımlılıkları.

---
*Proje Geliştiricisi: Zeynep Nur Zorbozan*
