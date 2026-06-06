from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Mac üzerinde Homebrew ile kurulan PostgreSQL için en temiz yerel bağlantı adresi:
SQLALCHEMY_DATABASE_URL = "postgresql://localhost/skinsense"

# Veritabanı motorumuzla köprüyü kuruyoruz
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# API'mizin veritabanı ile güvenli bir şekilde konuşmasını sağlayacak oturum (session) ayarı
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Tablolarımızın (modellerimizin) miras alacağı ana sınıf
Base = declarative_base()

# Her API isteğinde veritabanı kapısını açıp, işlem bitince güvenlice kapatan fonksiyon
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()