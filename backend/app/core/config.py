"""Настройки: секреты только из локального .env, в git их нет."""
from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "HRXWarehouse"
    APP_VERSION: str = "2.0.0"
    ENV: str = "prod"
    LOG_LEVEL: str = "INFO"
    LOG_DIR: str = "./logs"

    BOT_TOKEN: str = ""
    DATABASE_URL: str = "sqlite+aiosqlite:///./hrx.db"
    DEV_ALLOW_UNAUTH: bool = False

    UPLOAD_DIR: str = "./uploads"
    BACKUP_DIR: str = "./backups"
    MAX_UPLOAD_MB: int = 10
    MAX_IMAGE_PIXELS: int = 40_000_000

    RATE_LIMIT_PER_MIN: int = 120
    TELEGRAM_NOTIFY_TIMEOUT: int = 10

    @property
    def is_sqlite(self) -> bool:
        return self.DATABASE_URL.startswith("sqlite")

    @property
    def upload_path(self) -> Path:
        return Path(self.UPLOAD_DIR)

    @property
    def backup_path(self) -> Path:
        return Path(self.BACKUP_DIR)

    @property
    def log_path(self) -> Path:
        return Path(self.LOG_DIR)


settings = Settings()
