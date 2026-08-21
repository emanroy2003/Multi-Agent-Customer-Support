"""
Application configuration.

Loads all settings from environment variables (see .env.example).
Uses pydantic-settings so values are validated and typed.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application
    app_name: str = "Customer Support AI"
    app_env: str = "development"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    frontend_url: str = "http://localhost:5173"

    # Database
    database_type: str = "postgres"  # "postgres", "sqlite" (local dev), or "mongo" (future)
    postgres_url: str = "postgresql://postgres:password@localhost:5432/customer_support_ai"
    sqlite_url: str = "sqlite:///./app.db"
    mongo_url: str = "mongodb://localhost:27017"
    mongo_db_name: str = "customer_support_ai"

    @property
    def database_url(self) -> str:
        """Resolve the active SQLAlchemy connection string based on database_type."""
        if self.database_type == "sqlite":
            return self.sqlite_url
        return self.postgres_url

    # JWT
    jwt_secret_key: str = "change_this_to_a_long_random_secret_key"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    jwt_refresh_token_expire_days: int = 7

    # LLM
    llm_provider: str = "openai"  # "openai" or "anthropic"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-6"

    # RAG
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    faiss_index_path: str = "backend/vectorstore/faiss_index"
    knowledge_base_path: str = "knowledge_base"
    chunk_size: int = 500
    chunk_overlap: int = 50
    top_k_results: int = 4

    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/app.log"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance so we don't re-read .env on every call."""
    return Settings()


settings = get_settings()
