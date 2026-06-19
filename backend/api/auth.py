from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
import hashlib, random, os

from backend.models.database import get_db, User, UserProfile

router     = APIRouter()
oauth2     = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
SECRET_KEY = os.getenv("SECRET_KEY", "changethisinproduction123456789abc")
ALGORITHM  = "HS256"
EXPIRE_MIN = 60 * 24

# In-memory OTP store (replace with Redis in production)
_otp_store = {}   # {email: {"otp": "123456", "expires": datetime}}


# ── Schemas ───────────────────────────────────────────────────────────────────

class RegisterIn(BaseModel):
    email:     str
    username:  str
    password:  str
    full_name: Optional[str] = None

class OTPVerifyIn(BaseModel):
    email: str
    otp:   str

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


# ── Password helpers ──────────────────────────────────────────────────────────

def hash_pw(pw: str) -> str:
    return hashlib.sha256(("jobrecommender_salt_" + pw).encode()).hexdigest()

def verify_pw(pw: str, hashed: str) -> bool:
    return hash_pw(pw) == hashed

def make_token(user_id: int) -> str:
    exp = datetime.utcnow() + timedelta(minutes=EXPIRE_MIN)
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


# ── OTP helpers (placeholder — wire to SendGrid/SMTP for production) ──────────

def generate_otp() -> str:
    return str(random.randint(100000, 999999))

def store_otp(email: str, otp: str):
    _otp_store[email] = {
        "otp":     otp,
        "expires": datetime.utcnow() + timedelta(minutes=10),
    }

def verify_otp(email: str, otp: str) -> bool:
    record = _otp_store.get(email)
    if not record:
        return False
    if datetime.utcnow() > record["expires"]:
        del _otp_store[email]
        return False
    if record["otp"] != otp:
        return False
    del _otp_store[email]
    return True

def send_otp_email(email: str, otp: str):
    """
    TODO: Replace with real email sending.
    Options:
      - SendGrid: pip install sendgrid
      - Gmail SMTP: smtplib
      - Resend: pip install resend
    For now, we print to console (works for demo).
    """
    print(f"\n{'='*40}")
    print(f"OTP for {email}: {otp}")
    print(f"(In production this would be emailed)")
    print(f"{'='*40}\n")


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("/register", response_model=Token, status_code=201)
def register(data: RegisterIn, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(400, "Email already registered")
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(400, "Username already taken")
    user = User(
        email=data.email, username=data.username,
        hashed_password=hash_pw(data.password),
        full_name=data.full_name,
    )
    db.add(user)
    db.flush()
    db.add(UserProfile(user_id=user.id))
    db.commit()
    db.refresh(user)
    return Token(
        access_token=make_token(user.id),
        token_type="bearer", user=user
    )


@router.post("/login", response_model=Token)
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db:   Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == form.username).first()
    if not user or not verify_pw(form.password, user.hashed_password):
        raise HTTPException(400, "Incorrect email or password")
    return Token(
        access_token=make_token(user.id),
        token_type="bearer", user=user
    )


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


# ── OTP endpoints (ready for future wiring) ───────────────────────────────────

@router.post("/send-otp")
def send_otp(email: str, db: Session = Depends(get_db)):
    """Send OTP to email for verification (future: wire to email service)."""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(404, "Email not registered")
    otp = generate_otp()
    store_otp(email, otp)
    send_otp_email(email, otp)
    return {
        "message": f"OTP sent to {email}",
        "note":    "Check server console for OTP (demo mode)",
    }


@router.post("/verify-otp")
def verify_otp_route(data: OTPVerifyIn):
    """Verify OTP — returns token if valid."""
    if not verify_otp(data.email, data.otp):
        raise HTTPException(400, "Invalid or expired OTP")
    return {"message": "OTP verified", "verified": True}


@router.post("/forgot-password")
def forgot_password(email: str, db: Session = Depends(get_db)):
    """Send password reset OTP."""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(404, "Email not registered")
    otp = generate_otp()
    store_otp(email, otp)
    send_otp_email(email, otp)
    return {"message": "Password reset OTP sent"}


@router.post("/reset-password")
def reset_password(
    email:        str,
    otp:          str,
    new_password: str,
    db:           Session = Depends(get_db)
):
    """Reset password after OTP verification."""
    if not verify_otp(email, otp):
        raise HTTPException(400, "Invalid or expired OTP")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(404, "User not found")
    user.hashed_password = hash_pw(new_password)
    db.commit()
    return {"message": "Password reset successfully"}