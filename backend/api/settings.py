from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SEEWEE_", extra="ignore")

    db_path: str = "/data/seewee.db"
    cors_origins: str = "http://localhost:3000"
    llm_mode: str = "both"
    hosted_api_key: str | None = None
    ollama_base_url: str = "http://ollama:11434"

    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()


