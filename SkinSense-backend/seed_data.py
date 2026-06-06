from database import SessionLocal
from models import Ingredient

# Veritabanı kapısını açıyoruz
db = SessionLocal()

# Örnek kozmetik içeriklerimiz ve risk skorları
ornek_icerikler = [
    {"name": "aqua", "risk_level": "Safe", "comedogenic_rating": 0, "description": "Temel çözücü, su. Tüm cilt tipleri için güvenlidir."},
    {"name": "glycerin", "risk_level": "Safe", "comedogenic_rating": 0, "description": "Harika bir nemlendirici. Nemi cilde hapseder."},
    {"name": "sodium laureth sulfate", "risk_level": "Moderate", "comedogenic_rating": 3, "description": "Sert bir temizleyici. Kuru ve hassas ciltleri tahriş edebilir."},
    {"name": "paraben", "risk_level": "High", "comedogenic_rating": 0, "description": "Tartışmalı bir koruyucu madde. Hassas ciltlerde reaksiyon yapabilir."},
    {"name": "salicylic acid", "risk_level": "Safe", "comedogenic_rating": 0, "description": "BHA türü asit. Yağlı ve akneye eğilimli ciltler için gözenek temizleyicidir."}
]

print("Veritabanına içerikler ekleniyor...")

# İçerikleri tek tek veritabanına işliyoruz
for icerik in ornek_icerikler:
    # Eğer bu içerik daha önce eklendiyse (hata vermemesi için) kontrol ediyoruz
    mevcut_mu = db.query(Ingredient).filter(Ingredient.name == icerik["name"]).first()
    if not mevcut_mu:
        yeni_madde = Ingredient(**icerik)
        db.add(yeni_madde)

# Değişiklikleri kaydedip kapıyı kapatıyoruz
db.commit()
db.close()

print("✅ Kozmetik veri tabanı başarıyla güncellendi!")