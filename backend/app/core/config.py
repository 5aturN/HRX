"""Настройки приложения (рус.). Токен бота — только из локального .env, в git не попадает."""
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    BOT_TOKEN: str = ""
    DATABASE_URL: str = "sqlite+aiosqlite:///./hrx.db"
    DEV_ALLOW_UNAUTH: bool = True
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_MB: int = 10

settings = Settings()
