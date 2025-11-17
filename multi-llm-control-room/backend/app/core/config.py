"""Application configuration"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    # Application
    app_name: str = "Multi-LLM Control Room"
    app_env: str = "development"
    debug: bool = True
    secret_key: str = "change-this-secret-key"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Database
    database_url: str = "postgresql+asyncpg://controlroom:controlroom@localhost:5432/controlroom"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # CORS
    cors_origins: List[str] = ["http://localhost:3000"]

    # Provider API Keys
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    azure_openai_key: str = ""
    azure_openai_endpoint: str = ""
    nvidia_api_key: str = ""
    huggingface_api_key: str = ""

    # Local Model Servers
    ollama_base_url: str = "http://localhost:11434"
    lmstudio_base_url: str = "http://localhost:1234/v1"
    oobabooga_base_url: str = "http://localhost:5000"

    # Observability
    prometheus_enabled: bool = True
    log_level: str = "INFO"


settings = Settings()
