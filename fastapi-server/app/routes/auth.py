from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse
from app.database import SessionLocal
from app import models, schemas
from app.utils.otp import generate_otp
from app.config import settings
from fastapi_jwt_auth import AuthJWT
from slowapi import Limiter
from slowapi.util import get_remote_address
from twilio.rest import Client

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Simulate OTP store (use Redis in production)
otp_store = {}

# Twilio client setup
twilio_client = Client(settings.twilio_account_sid, settings.twilio_auth_token)

@router.post("/send-otp")
@limiter.limit("3/minute")
def send_otp(payload: schemas.PhoneRequest, db: Session = Depends(get_db)):
    otp = generate_otp()

    # Save OTP temporarily
    otp_store[payload.phone] = otp

    # Send via Twilio (or simulate in logs)
    try:
        message = twilio_client.messages.create(
            body=f"Your OTP is: {otp}",
            from_=settings.twilio_phone_number,
            to=payload.phone
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error sending OTP")

    # Create user if not exists
    user = db.query(models.User).filter_by(phone=payload.phone).first()
    if not user:
        user = models.User(phone=payload.phone)
        db.add(user)
        db.commit()
    return {"msg": "OTP sent successfully"}

@router.post("/verify-otp")
def verify_otp(payload: schemas.OTPVerify, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    otp = otp_store.get(payload.phone)
    if not otp or otp != payload.otp:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    # Mark user as verified
    user = db.query(models.User).filter_by(phone=payload.phone).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_verified = True
    db.commit()

    # Create and return JWT token
    access_token = Authorize.create_access_token(subject=payload.phone)
    return {"access_token": access_token, "token_type": "bearer"}
