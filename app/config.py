import os

from passlib.context import CryptContext
from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
    SENDGRID_API_KEY: str = os.environ.get("SENDGRID_API_KEY")
    ALLOWED_HOSTS: str = os.environ.get("ALLOWED_HOSTS").split(",")
    SENDGRID_FROM_EMAIL: str = os.environ.get("SENDGRID_FROM_EMAIL")
    SECRET_KEY: str = os.environ.get("SECRET_KEY")
    FROM_EMAIL: str = os.environ.get("FROM_EMAIL")
    FRONTEND_LINK: str = os.environ.get("FRONTEND_LINK")


class JWTSettings(BaseSettings):
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRATION_TIME: int = 3600  # 1 hour
    REFRESH_TOKEN_EXPIRATION_TIME: int = 86400  # 1 day


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

settings = Settings()
jwt_settings = JWTSettings()
