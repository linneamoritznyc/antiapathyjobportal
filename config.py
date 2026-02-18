"""
Configuration management using pydantic-settings
Loads settings from environment variables and .env file
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Supabase Authentication
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""

    # Gmail Configuration
    gmail_user: str = ""
    gmail_app_password: str = ""

    # CORS Configuration
    allowed_origins: str = "http://localhost:8000,http://localhost:3000"

    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds

    # Anthropic API
    anthropic_api_key: str = ""

    @property
    def cors_origins(self) -> List[str]:
        """Parse comma-separated origins into a list"""
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance - loads once per process"""
    return Settings()
