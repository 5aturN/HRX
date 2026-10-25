"""Настройки: секреты только из локального .env, в git их нет."""
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    BOT_TOKEN: str = ""
    DATABASE_URL: str = "sqlite+aiosqlite:///./hrx.db"
    DEV_ALLOW_UNAUTH: bool = False
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_MB: int = 10
    RATE_LIMIT_PER_MIN: int = 120

settings = Settings()
