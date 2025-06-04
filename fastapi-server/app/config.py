# from pydantic import BaseSettings
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    jwt_secret_key: str
    twilio_account_sid: str
    twilio_auth_token: str
    twilio_phone_number: str

    class Config:
        env_file = ".env"

settings = Settings()
