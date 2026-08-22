from pathlib import Path

from pydantic import Field, RedisDsn, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    POSTGRES_URL : PostgresDsn
    REDIS_URL : RedisDsn 
    TOKEN_ALGO: str
    TOKEN_EXP_H: int
    TOKEN_KEY: str
    sqlalchemy_url: str = Field(validation_alias="sqlalchemy.url")
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    

settings = Settings()