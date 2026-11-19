from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT / ".env",
        extra="ignore",
    )

    openai_api_key: str = ""
    google_api_key: str = ""
    openai_model: str = "gpt-6-luna"
    gemini_model: str = "gemini-3.8-flash"

    liberty_database_url: str = ""
    galle_face_database_url: str = ""
    pettah_database_url: str = ""
    auth_database_url: str = ""

    owner_username: str = "owner"
    owner_password: str = ""
    jwt_secret: str = ""
    cookie_secure: bool = False
    allowed_origin: str = "http://localhost:5173"
    max_demo_requests_per_hour: int = 35

    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_base_url: str = "https://cloud.langfuse.com"
    langfuse_tracing_enabled: bool = False


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
