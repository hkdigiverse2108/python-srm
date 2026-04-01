# backend/app/core/config.py
import os
from pydantic_settings import BaseSettings, SettingsConfigDict

# Get the absolute path to the backend directory where .env lives
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
env_file_path = os.path.join(backend_dir, ".env")

class Settings(BaseSettings):
    PROJECT_NAME: str = "SRM AI SETU"
    MONGODB_URI: str = "mongodb://localhost:27017/aisetu_srm"
    SECRET_KEY: str = "your-secret-key-for-development!"  # Change in production!
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    encryption_key: str = "default_placeholder_if_missing"
    google_api_key: str = "default_placeholder_if_missing"

    # WhatsApp Cloud API (Meta) — uncomment gateway code in billing/service.py to activate
    WHATSAPP_TOKEN: str = ""
    WHATSAPP_TOKEN_FALLBACK: str = ""
    WHATSAPP_PHONE_NUMBER_ID: str = ""

    # PhonePe Payment Gateway — uncomment gateway code in billing/service.py to activate
    # Test credentials (switch to production keys before go-live)
    PHONEPE_MERCHANT_ID: str = "M22QDSISBR7LX_2511271619"
    PHONEPE_SALT_KEY: str = "MTQyYmNmZGItZDFiNC00NzFjLWEzYzgtMWM0YjkxMTNjNmVm"
    PHONEPE_SALT_INDEX: str = "1"
    PHONEPE_ENV: str = "sandbox"          # change to "production" for live
    PHONEPE_CALLBACK_BASE_URL: str = ""   # e.g. https://yourdomain.com (must be public)

    # SMTP Settings
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SENDER_EMAIL: str = ""

    model_config = SettingsConfigDict(
        env_file=env_file_path,
        extra="allow"
    )

settings = Settings()

# Global API Configuration (Networking)
HOST = os.getenv("SRM_HOST", "0.0.0.0")
PORT = int(os.getenv("SRM_PORT", os.getenv("PORT", "8000")))

_env_api_url = os.getenv("API_BASE_URL")
if _env_api_url:
    API_BASE_URL = _env_api_url
else:
    _display_host = "localhost" if HOST == "0.0.0.0" else HOST
    API_BASE_URL = f"http://{_display_host}:{PORT}/api"
