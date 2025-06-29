# app/core/config.py

from pathlib import Path
from typing import List, Dict, Optional

from pydantic import AnyHttpUrl, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine.url import make_url

# Compute project root (two levels up from this file)
ROOT_DIR = Path(__file__).parents[2]


class Settings(BaseSettings):
    # Pydantic v2 config: point to the project-root .env
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    # Core settings
    APP_NAME: str = "Gym-App"

    # API Info
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Gym Progress Tracker"
    VERSION: str = "1.0.0"

    # JWT / Auth settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    # Email service (Resend)
    RESEND_API_KEY: Optional[str] = None
    RESEND_FROM_EMAIL: Optional[str] = None

    # CORS origins
    FRONTEND_URL: AnyHttpUrl
    ADMIN_URL: AnyHttpUrl

    # Database settings
    DATABASE_URL: PostgresDsn

    @property
    def BACKEND_CORS_ORIGINS(self) -> List[str]:
        # Cast AnyHttpUrl back to plain strings for CORS middleware
        return [str(self.FRONTEND_URL), str(self.ADMIN_URL)]

    # Security headers
    SECURITY_HEADERS: Dict[str, str] = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'",
    }


# Instantiate settings on import
settings = Settings()

