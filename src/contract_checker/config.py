from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_env: str = "development"
    max_upload_mb: int = 10
    top_k: int = 5

    llm_provider: str = "mock"
    llm_base_url: str = ""
    llm_model: str = ""
    llm_api_key: str = ""
    llm_timeout_seconds: float = 60.0
    llm_temperature: float = 0.01
    llm_max_output_tokens: int = 900

    gigachat_credentials: str = ""
    gigachat_scope: str = "GIGACHAT_API_PERS"
    gigachat_model: str = "GigaChat-2"
    gigachat_base_url: str = "https://api.giga.chat/v1"
    gigachat_auth_url: str = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    gigachat_verify_ssl: bool = True
    gigachat_ca_bundle_file: Path | None = None

    embedding_provider: str = "hashing"
    embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

    regulations_dir: Path = Field(default=Path("data/regulations"))
    analysis_db_path: Path = Field(default=Path("data/analyses.sqlite3"))

    @field_validator("gigachat_ca_bundle_file", mode="before")
    @classmethod
    def empty_ca_bundle_is_none(cls, value):
        if value in (None, ""):
            return None
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
