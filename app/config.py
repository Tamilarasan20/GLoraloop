from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Laraloop Brand DNA Extractor"
    artifacts_dir: Path = Path("artifacts")
    scrape_timeout_ms: int = 30_000
    max_images: int = 20

    model_config = SettingsConfigDict(env_prefix="LARALOOP_", env_file=".env")


settings = Settings()
