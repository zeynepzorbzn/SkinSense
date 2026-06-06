from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
import models
from database import get_db
from pydantic import BaseModel


SECRET_KEY = "skinsense_super_gizli_anahtar"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 # Oturum 1 saat açık kalacak

# Passlib ve Mac Bcrypt uyumsuzluğunu çözen özel ayar
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__ident="2b",
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

router = APIRouter(prefix="/auth", tags=["Yetkilendirme"])

# Dışarıdan gelecek veri formatı
class UserCreate(BaseModel):
    username: str
    password: str
    skin_type: str = "Normal"

# Şifre Kriptolama Fonksiyonları
def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Token (Giriş Kartı) Üretme Fonksiyonu
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# --- UÇ NOKTALAR (ENDPOINTS) ---

@router.post("/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Kullanıcı adı daha önce alınmış mı kontrol et
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Bu kullanıcı adı zaten kullanımda.")
    
    # Şifreyi kriptola ve veritabanına kaydet
    hashed_pw = get_password_hash(user.password)
    new_user = models.User(username=user.username, hashed_password=hashed_pw, skin_type=user.skin_type)
    
    db.add(new_user)
    db.commit()
    
    return {"mesaj": "Aramıza hoş geldin! Kayıt işlemi başarılı."}

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Kullanıcıyı bul ve şifresini doğrula
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Kullanıcı adı veya şifre hatalı.")
    
    # Her şey doğruysa kullanıcıya sisteme giriş kartını (Token) ver
    access_token = create_access_token(data={"sub": user.username}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}

# Gelen token'ı çözüp o anki kullanıcıyı bulan fonksiyon
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Geçersiz kimlik kartı")
    except JWTError:
        raise HTTPException(status_code=401, detail="Geçersiz kimlik kartı")
    
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Kullanıcı bulunamadı")
    return user