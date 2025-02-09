from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Keboola Storage API Configuration
    storage_token: str
    storage_api_host: str = "connection.keboola.com"  # Default value, can be overridden

    # Application Configuration
    app_env: str = "development"
    log_level: str = "INFO"

    # Database Configuration
    db_path: str = "data/credentials.db"

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings() 