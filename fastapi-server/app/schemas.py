from pydantic import BaseModel

class PhoneRequest(BaseModel):
    phone: str

class OTPVerify(BaseModel):
    phone: str
    otp: str
