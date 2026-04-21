from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Identity Document PII Extractor"
    upload_dir: Path = Path(__file__).resolve().parents[3] / "uploads"
    allowed_extensions: set[str] = {"jpg", "jpeg", "png", "webp", "pdf"}
    max_upload_size_mb: int = 10
    mongodb_url: str = "mongodb://localhost:27017"  # Default for local testing
    mongodb_db_name: str = "PII_extractor"


settings = Settings()
settings.upload_dir.mkdir(parents=True, exist_ok=True)
