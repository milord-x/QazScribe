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
    task_retention_days: int = Field(default=7, alias="TASK_RETENTION_DAYS")
    cleanup_interval_minutes: int = Field(default=30, alias="CLEANUP_INTERVAL_MINUTES")
    asr_model_size: str = Field(default="small", alias="ASR_MODEL_SIZE")
    asr_device: str = Field(default="cpu", alias="ASR_DEVICE")
    asr_compute_type: str = Field(default="int8", alias="ASR_COMPUTE_TYPE")
    llm_provider: str = Field(default="none", alias="LLM_PROVIDER")
    llm_api_base_url: str | None = Field(default=None, alias="LLM_API_BASE_URL")
    llm_api_key: str | None = Field(default=None, alias="LLM_API_KEY")
    llm_model: str | None = Field(default=None, alias="LLM_MODEL")
    llm_timeout_seconds: int = Field(default=120, alias="LLM_TIMEOUT_SECONDS")

    model_config = SettingsConfigDict(env_file=BACKEND_DIR / ".env", extra="ignore")

    @property
    def project_root(self) -> Path:
        return PROJECT_ROOT

    @property
    def frontend_path(self) -> Path:
        return PROJECT_ROOT / self.frontend_dir

    @property
    def data_path(self) -> Path:
        return PROJECT_ROOT / "data"

    @property
    def uploads_path(self) -> Path:
        return self.data_path / "uploads"

    @property
    def processed_path(self) -> Path:
        return self.data_path / "processed"

    @property
    def outputs_path(self) -> Path:
        return self.data_path / "outputs"

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    return Settings()
