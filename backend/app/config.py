from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BACKEND_DIR.parent
load_dotenv(BACKEND_DIR / ".env")

SUPPORTED_SPEECH_LANGUAGES = [
    {"code": "ru", "browser_code": "ru-RU", "name": "Русский"},
    {"code": "kk", "browser_code": "kk-KZ", "name": "Қазақша"},
    {"code": "ky", "browser_code": "ky-KG", "name": "Кыргызча"},
    {"code": "uz", "browser_code": "uz-UZ", "name": "O'zbekcha"},
    {"code": "tt", "browser_code": "tt-RU", "name": "Татарча"},
    {"code": "tg", "browser_code": "tg-TJ", "name": "Тоҷикӣ"},
    {"code": "az", "browser_code": "az-AZ", "name": "Azərbaycanca"},
    {"code": "tk", "browser_code": "tk-TM", "name": "Türkmençe"},
    {"code": "be", "browser_code": "be-BY", "name": "Беларуская"},
    {"code": "uk", "browser_code": "uk-UA", "name": "Українська"},
]

SUPPORTED_ASR_MODELS = [
    {
        "language": "multilingual",
        "language_name": "General multilingual",
        "backend": "faster_whisper",
        "model": "large-v3",
        "model_id": "openai/whisper-large-v3",
        "recommended": True,
        "notes": "Default production model for mixed CIS speech and formal recordings.",
    },
    {
        "language": "ru",
        "language_name": "Russian",
        "backend": "faster_whisper",
        "model": "large-v3",
        "model_id": "openai/whisper-large-v3",
        "recommended": True,
        "notes": "Use the default large-v3 mode for Russian meetings and mixed Russian/CIS speech.",
    },
    {
        "language": "kk",
        "language_name": "Kazakh",
        "backend": "transformers_whisper",
        "model": "InflexionLab/sybyrla",
        "model_id": "InflexionLab/sybyrla",
        "recommended": True,
        "notes": "Whisper Large V3 fine-tuned for Kazakh with Russian auxiliary data.",
    },
    {
        "language": "ky",
        "language_name": "Kyrgyz",
        "backend": "transformers_whisper",
        "model": "nineninesix/kyrgyz-whisper-medium",
        "model_id": "nineninesix/kyrgyz-whisper-medium",
        "recommended": True,
        "notes": "Whisper Medium fine-tuned for Kyrgyz, Russian, and English code-switching.",
    },
    {
        "language": "ky",
        "language_name": "Kyrgyz",
        "backend": "wav2vec2_ctc",
        "model": "kyrgyz-ai/Wav2vec-Kyrgyz",
        "model_id": "kyrgyz-ai/Wav2vec-Kyrgyz",
        "recommended": False,
        "notes": "Kyrgyz-only Wav2Vec2 comparison model.",
    },
    {
        "language": "uz",
        "language_name": "Uzbek",
        "backend": "transformers_whisper",
        "model": "Uzbekswe/uzbek_stt_v1",
        "model_id": "Uzbekswe/uzbek_stt_v1",
        "recommended": True,
        "notes": "Whisper Medium Uzbek model reported by its card at 16.7% overall WER.",
    },
    {
        "language": "tt",
        "language_name": "Tatar",
        "backend": "transformers_whisper",
        "model": "501Good/whisper-tiny-tt",
        "model_id": "501Good/whisper-tiny-tt",
        "recommended": False,
        "notes": "Small experimental Tatar model; keep large-v3 as fallback for real demonstrations.",
    },
    {
        "language": "tg",
        "language_name": "Tajik",
        "backend": "transformers_whisper",
        "model": "muhtasham/whisper-tg",
        "model_id": "muhtasham/whisper-tg",
        "recommended": True,
        "notes": "Whisper Small Tajik model reported by its card at 18.9518% WER.",
    },
    {
        "language": "az",
        "language_name": "Azerbaijani",
        "backend": "transformers_whisper",
        "model": "LocalDoc/azerbaijani-whisper-turbo",
        "model_id": "LocalDoc/azerbaijani-whisper-turbo",
        "recommended": True,
        "notes": "Whisper Turbo Azerbaijani model reported by its card at 13.17% WER.",
    },
    {
        "language": "tk",
        "language_name": "Turkmen",
        "backend": "transformers_whisper",
        "model": "Atamyrat2005/whisper-base-tk-finetuned",
        "model_id": "Atamyrat2005/whisper-base-tk-finetuned",
        "recommended": True,
        "notes": "Whisper model fine-tuned for Turkmen on Common Voice 17.0.",
    },
    {
        "language": "be",
        "language_name": "Belarusian",
        "backend": "transformers_whisper",
        "model": "Aleton/whisper-small-be-custom",
        "model_id": "Aleton/whisper-small-be-custom",
        "recommended": True,
        "notes": "Whisper Small model optimized for Belarusian speech recognition.",
    },
    {
        "language": "uk",
        "language_name": "Ukrainian",
        "backend": "transformers_whisper",
        "model": "vumenira/whisper-small-uk",
        "model_id": "vumenira/whisper-small-uk",
        "recommended": True,
        "notes": "Whisper Small Ukrainian model reported by its card at 17.2136% WER.",
    },
]


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
    asr_backend: str = Field(default="faster_whisper", alias="ASR_BACKEND")
    asr_model_id: str | None = Field(default=None, alias="ASR_MODEL_ID")
    asr_device: str = Field(default="cpu", alias="ASR_DEVICE")
    asr_compute_type: str = Field(default="int8", alias="ASR_COMPUTE_TYPE")
    asr_language: str | None = Field(default=None, alias="ASR_LANGUAGE")
    asr_beam_size: int = Field(default=5, alias="ASR_BEAM_SIZE")
    asr_vad_filter: bool = Field(default=True, alias="ASR_VAD_FILTER")
    asr_initial_prompt: str | None = Field(default=None, alias="ASR_INITIAL_PROMPT")
    asr_transformers_language: str | None = Field(default=None, alias="ASR_TRANSFORMERS_LANGUAGE")
    asr_trust_remote_code: bool = Field(default=False, alias="ASR_TRUST_REMOTE_CODE")
    asr_chunk_length_seconds: int = Field(default=30, alias="ASR_CHUNK_LENGTH_SECONDS")
    asr_fake_transcript: str | None = Field(default=None, alias="ASR_FAKE_TRANSCRIPT")
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
