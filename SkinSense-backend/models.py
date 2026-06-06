from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from database import Base

class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    benefits = Column(String, nullable=True)
    concerns = Column(String, nullable=True)
    is_comedogenic = Column(Boolean, default=False)
    skin_type_compatibility = Column(String, nullable=True)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String) 
    skin_type = Column(String, default="Normal") 
    sensitivities = Column(String, nullable=True) 
    
    # Kullanıcının geçmiş taramalarıyla olan bağı
    histories = relationship("ScanHistory", back_populates="user")

class ScanHistory(Base):
    __tablename__ = "scan_histories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    barcode = Column(String)
    product_name = Column(String)
    uyum_skoru = Column(Integer)
    
    # Geçmiş taramanın sahibi olan kullanıcıyla bağı
    user = relationship("User", back_populates="histories")
    created_at = Column(DateTime, server_default=func.now())
    