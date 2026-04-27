from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BACKEND_DIR.parent
load_dotenv(BACKEND_DIR / ".env")


class Settings(BaseSettings):
    app_name: str = Field(default="QazScribe Conference AI Notes", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    frontend_dir: str = Field(default="frontend", alias="FRONTEND_DIR")
    max_upload_mb: int = Field(default=300, alias="MAX_UPLOAD_MB")
    upload_retention_hours: int = Field(default=6, alias="UPLOAD_RETENTION_HOURS")
    output_retention_hours: int = Field(default=24, alias="OUTPUT_RETENTION_HOURS")
    asr_model_size: str = Field(default="small", alias="ASR_MODEL_SIZE")
    asr_device: str = Field(default="cpu", alias="ASR_DEVICE")
    asr_compute_type: str = Field(default="int8", alias="ASR_COMPUTE_TYPE")

    model_config = SettingsConfigDict(env_file=BACKEND_DIR / ".env", extra="ignore")

    @property
    def project_root(self) -> Path:
        return PROJECT_ROOT

    @property
    def frontend_path(self) -> Path:
        return PROJECT_ROOT / self.frontend_dir


@lru_cache
def get_settings() -> Settings:
    return Settings()
