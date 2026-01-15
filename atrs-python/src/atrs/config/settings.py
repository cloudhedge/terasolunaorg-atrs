"""Application settings using Pydantic Settings"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_name: str = "ATRS"
    debug: bool = False

    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/atrs"
    db_pool_min_size: int = 5
    db_pool_max_size: int = 20

    # Redis (for sessions and background tasks)
    redis_url: str = "redis://localhost:6379"

    # Security
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Business Rules
    reserve_interval_time: int = 30  # days ahead booking allowed
    default_flight_type: str = "RT"  # round trip


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
