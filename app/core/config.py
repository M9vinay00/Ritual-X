"""Environment-backed configuration for the application."""

import os

from dotenv import load_dotenv

load_dotenv(override=True)


class Settings:
    """Expose application settings through simple class attributes."""

    PROJECT_NAME = os.getenv("PROJECT_NAME", "Pandit Hub")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    SMTP_HOST = os.getenv("SMTP_HOST", "")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD = (os.getenv("SMTP_PASSWORD", "") or "").replace(" ", "")
    SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", "")
    SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
    APP_BASE_URL = os.getenv("APP_BASE_URL", "http://127.0.0.1:8000")
    FORGOT_PASSWORD_EXPIRE_MINUTES = int(os.getenv("FORGOT_PASSWORD_EXPIRE_MINUTES", "15"))
    ADMIN_SEED_ON_STARTUP = os.getenv("ADMIN_SEED_ON_STARTUP", "false").lower() == "true"
    ADMIN_NAME = os.getenv("ADMIN_NAME", "Super Admin")
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
    ADMIN_PHONE = os.getenv("ADMIN_PHONE")


settings = Settings()
