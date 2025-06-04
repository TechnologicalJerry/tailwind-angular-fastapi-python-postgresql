from sqlalchemy import Column, String, Boolean
from app.database import Base

class User(Base):
    __tablename__ = "users"
    phone = Column(String, primary_key=True, index=True)
    is_verified = Column(Boolean, default=False)
