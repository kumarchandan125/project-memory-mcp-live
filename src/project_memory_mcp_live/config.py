from functools import lru_cache
from typing import Literal

from dotenv import load_dotenv
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "Project Memory MCP Server"

    app_env: Literal[
        "development",
        "test",
        "production",
    ] = "production"

    host: str = "127.0.0.1"
    port: int = 8000

    log_level: str = "INFO"

    database_url: SecretStr | None = None
    test_database_url: SecretStr | None = None
    auth_token: SecretStr | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()
