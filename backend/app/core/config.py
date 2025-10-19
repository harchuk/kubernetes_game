from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Kubernetes Cluster Clash Online"
    database_url: str = "postgresql+asyncpg://postgres:postgres@db:5432/kubeclash"
    redis_url: str = "redis://redis:6379/0"
    cors_origins: List[str] = ["http://localhost:5173"]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
