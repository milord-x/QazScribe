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
    qazscribe_base_dir: str | None = Field(default=None, alias="QAZSCRIBE_BASE_DIR")
    qazscribe_data_dir: str | None = Field(default=None, alias="QAZSCRIBE_DATA_DIR")
    qazscribe_uploads_dir: str | None = Field(default=None, alias="QAZSCRIBE_UPLOADS_DIR")
    qazscribe_processed_dir: str | None = Field(default=None, alias="QAZSCRIBE_PROCESSED_DIR")
    qazscribe_outputs_dir: str | None = Field(default=None, alias="QAZSCRIBE_OUTPUTS_DIR")
    qazscribe_models_dir: str | None = Field(default=None, alias="QAZSCRIBE_MODELS_DIR")
    qazscribe_logs_dir: str | None = Field(default=None, alias="QAZSCRIBE_LOGS_DIR")
    qazscribe_tmp_dir: str | None = Field(default=None, alias="QAZSCRIBE_TMP_DIR")
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
        if self.qazscribe_data_dir:
            return Path(self.qazscribe_data_dir)
        if self.qazscribe_base_dir:
            return Path(self.qazscribe_base_dir) / "data"
        return PROJECT_ROOT / "data"

    @property
    def uploads_path(self) -> Path:
        if self.qazscribe_uploads_dir:
            return Path(self.qazscribe_uploads_dir)
        return self.data_path / "uploads"

    @property
    def processed_path(self) -> Path:
        if self.qazscribe_processed_dir:
            return Path(self.qazscribe_processed_dir)
        return self.data_path / "processed"

    @property
    def outputs_path(self) -> Path:
        if self.qazscribe_outputs_dir:
            return Path(self.qazscribe_outputs_dir)
        return self.data_path / "outputs"

    @property
    def models_path(self) -> Path:
        if self.qazscribe_models_dir:
            return Path(self.qazscribe_models_dir)
        if self.qazscribe_base_dir:
            return Path(self.qazscribe_base_dir) / "models"
        return PROJECT_ROOT / "models"

    @property
    def logs_path(self) -> Path:
        if self.qazscribe_logs_dir:
            return Path(self.qazscribe_logs_dir)
        if self.qazscribe_base_dir:
            return Path(self.qazscribe_base_dir) / "logs"
        return PROJECT_ROOT / "logs"

    @property
    def tmp_path(self) -> Path:
        if self.qazscribe_tmp_dir:
            return Path(self.qazscribe_tmp_dir)
        if self.qazscribe_base_dir:
            return Path(self.qazscribe_base_dir) / "tmp"
        return PROJECT_ROOT / "tmp"

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    return Settings()
