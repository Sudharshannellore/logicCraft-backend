from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration, read from environment variables and `.env`."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Logicraft API"
    environment: Literal["development", "test", "production"] = "development"
    log_level: str = "INFO"
    api_prefix: str = "/api/v1"
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db: str = "codequest"
    seed_on_startup: bool = True

    # Signs access tokens. Must be set (and kept secret) in production; in development a random one is
    # generated at startup, which signs everyone out on every restart.
    jwt_secret: str = ""
    access_token_minutes: int = 30
    refresh_token_days: int = 14
    # Failed logins allowed per email before it's locked for `login_lockout_minutes`.
    login_max_failures: int = 5
    login_lockout_minutes: int = 15

    http_timeout_seconds: float = 6.0
    http_user_agent: str = "Logicraft/0.1 (learning platform; contact: dev@logicraft.local)"
    tutorial_cache_ttl_seconds: int = 12 * 60 * 60
    stackexchange_key: str = ""
    # Optional: raises GitHub's API limit from 60 to 5,000 requests/hour (framework courses list docs repositories).
    github_token: str = ""
    youtube_api_key: str = ""

    code_executor: Literal["local", "disabled"] = "local"
    code_timeout_seconds: float = 5.0
    code_memory_limit_mb: int = 256
    code_max_output_bytes: int = 64_000
    code_max_concurrent: int = 4
    # A whole Exercism test suite gets longer than a single run.
    exercise_timeout_seconds: float = 20.0


@lru_cache
def get_settings() -> Settings:
    return Settings()
