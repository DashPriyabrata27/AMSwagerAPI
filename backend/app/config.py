from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# ============================================================
# PROJECT PATHS
# ============================================================

# config.py -> app/ -> backend/ -> project root

BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_DIR.parent
ENV_FILE = PROJECT_ROOT / ".env"


# ============================================================
# APPLICATION SETTINGS
# ============================================================

class Settings(BaseSettings):

    APP_ENV: str = "development"

    OPENALEX_BASE_URL: str = "https://api.openalex.org"
    OPENALEX_API_KEY: str = ""

    REQUEST_TIMEOUT_SECONDS: float = Field(
        default=30.0,
        gt=0,
    )

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# ============================================================
# SETTINGS FACTORY
# ============================================================

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()