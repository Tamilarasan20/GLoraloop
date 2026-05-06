from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Laraloop Brand DNA Extractor"
    artifacts_dir: Path = Path("artifacts")
    scrape_timeout_ms: int = 30_000
    max_images: int = 20
    database_url: str = "sqlite:///./laraloop.db"
    redis_url: str = "redis://localhost:6379/0"
    celery_always_eager: bool = False
    ai_provider: str = "heuristic"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-1.5-pro"
    r2_endpoint_url: str | None = None
    r2_access_key_id: str | None = None
    r2_secret_access_key: str | None = None
    r2_bucket: str | None = None
    r2_public_base_url: str | None = None
    fal_api_key: str | None = None
    photoroom_api_key: str | None = None
    remove_bg_api_key: str | None = None
    meta_access_token: str | None = None
    linkedin_access_token: str | None = None
    tiktok_access_token: str | None = None
    frontend_origin: str = "http://127.0.0.1:3000"

    model_config = SettingsConfigDict(env_prefix="LARALOOP_", env_file=".env")


settings = Settings()
