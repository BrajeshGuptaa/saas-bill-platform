from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="BILLING_")

    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/billing"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret_key: str = "dev-secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
    environment: str = "local"
    metrics_port: int = 9000
    idempotency_ttl_seconds: int = 60 * 60 * 24
    testing: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
