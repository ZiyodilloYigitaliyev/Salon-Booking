# app/core/config.py
from typing import Optional, Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
import os

def _normalize_db_url(url: str) -> str:
    """
    Heroku ko'pincha postgres:// beradi.
    SQLAlchemy 2.x uchun postgresql+psycopg2:// ga almashtiramiz.
    SSL kerak bo'lsa, sslmode=require qo'shib qo'yamiz (agar yo'q bo'lsa).
    """
    if not url:
        return url
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg2://", 1)
    # sslmode qo'shish (agar allaqachon yo'q bo'lsa)
    if "sslmode=" not in url:
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}sslmode=require"
    return url

class Settings(BaseSettings):
    # --- App ---
    PROJECT_NAME: str = "App"
    ENVIRONMENT: Literal["development", "staging", "production"] = "production"

    # --- DB ---
    DATABASE_URL: str

    # --- Auth ---
    SECRET_KEY: Optional[str] = None
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # --- CLICK (optional qildik) ---
    CLICK_SERVICE_ID: Optional[int] = None
    CLICK_MERCHANT_ID: Optional[int] = None
    CLICK_SECRET_KEY: Optional[str] = None
    CLICK_MERCHANT_USER_ID: Optional[int] = None
    CLICK_API_URL: Optional[str] = None

    # Pydantic v2 settings config
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def _fix_db_url(cls, v: str) -> str:
        v = v or os.getenv("DATABASE_URL", "")
        if not v:
            raise ValueError("DATABASE_URL is missing (ENV yoki .env da bo'lishi kerak).")
        return _normalize_db_url(v)

    @field_validator("SECRET_KEY", mode="before")
    @classmethod
    def _require_secret_in_prod(cls, v: Optional[str], values: dict) -> Optional[str]:
        env = values.get("ENVIRONMENT", "production")
        if env == "production" and not v:
            # Prod muhitida SECRET_KEY majburiy
            raise ValueError("SECRET_KEY is required in production environment.")
        # Dev/Stagingda bo'sh bo'lsa ham ishlayveradi (lekin tavsiya ETILMAYDI)
        return v

    # Sync URL (Alembic uchun ham ishlatish oson)
    @property
    def SYNC_DATABASE_URL(self) -> str:
        # Agar async driver ishlatayotgan bo'lsang ham, Alembic uchun sync URL kerak bo'ladi.
        return _normalize_db_url(self.DATABASE_URL)

settings = Settings()
