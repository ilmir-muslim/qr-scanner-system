import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    # База данных
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "postgresql://user:password@db:5432/qr_scanner"
    )

    # Настройки приложения
    APP_TITLE: str = "QR Scanner System"
    APP_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"

    # Пути
    UPLOAD_DIR: str = "static/uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB

    # Печать
    DEFAULT_PRINTER: Optional[str] = None

    # QR код
    QR_CODE_SIZE: int = 10
    QR_CODE_VERSION: int = 1




settings = Settings()
