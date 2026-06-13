from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import os

from backend.models.database import get_db, User, UserProfile

router      = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2      = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

SECRET_KEY = os.getenv("SECRET_KEY", "changethisinproduction123456789abc")
ALGORITHM  = "HS256"
EXPIRE_MIN = 60 * 24  # 24 hours


# ── Schemas ───────────────────────────────────────────────────────────────────

class RegisterIn(BaseModel):
    email:     str
    username:  str
    password:  str
    full_name: Optional[str] = None

class UserOut(BaseModel):
    id:        int
    email:     str
    username:  str
    full_name: Optional[str]
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type:   str
    user:         UserOut


# ── Helpers ───────────────────────────────────────────────────────────────────
def hash_pw(pw: str) -> str:
    return pwd_context.hash(pw)

def verify_pw(pw: str, h: str) -> bool:
    try:
        return pwd_context.verify(pw, h)
    except Exception:
        return False

def make_token(user_id: int) -> str:
    exp  = datetime.utcnow() + timedelta(minutes=EXPIRE_MIN)
    return jwt.encode({"sub": str(user_id), "exp": exp}, SECRET_KEY, ALGORITHM)

async def get_current_user(
    token: str = Depends(oauth2),
    db:    Session = Depends(get_db)
) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
    except (JWTError, TypeError):
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("/register", response_model=Token, status_code=201)
def register(data: RegisterIn, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(400, "Email already registered")
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(400, "Username already taken")
    user = User(
        email=data.email, username=data.username,
        hashed_password=hash_pw(data.password), full_name=data.full_name,
    )
    db.add(user)
    db.flush()
    db.add(UserProfile(user_id=user.id))
    db.commit()
    db.refresh(user)
    return Token(access_token=make_token(user.id), token_type="bearer", user=user)


@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form.username).first()
    if not user or not verify_pw(form.password, user.hashed_password):
        raise HTTPException(400, "Incorrect email or password")
    return Token(access_token=make_token(user.id), token_type="bearer", user=user)


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user