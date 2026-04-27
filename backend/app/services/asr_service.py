from dataclasses import asdict, dataclass
from pathlib import Path
from threading import Lock
from typing import Any

from backend.app.config import Settings


class ASRError(RuntimeError):
    """Raised when speech recognition fails."""


@dataclass
class TranscriptionSegment:
    start: float
    end: float
    text: str


@dataclass
class TranscriptionResult:
    detected_language: str | None
    language_probability: float | None
    full_transcript: str
    segments: list[TranscriptionSegment]

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["segments"] = [asdict(segment) for segment in self.segments]
        return data


_model = None
_model_key: tuple[str, str, str] | None = None
_model_lock = Lock()


def _load_model(settings: Settings):
    global _model, _model_key

    model_key = (
        settings.asr_model_size,
        settings.asr_device,
        settings.asr_compute_type,
    )

    with _model_lock:
        if _model is not None and _model_key == model_key:
            return _model

        try:
            from faster_whisper import WhisperModel

            _model = WhisperModel(
                settings.asr_model_size,
                device=settings.asr_device,
                compute_type=settings.asr_compute_type,
            )
            _model_key = model_key
            return _model
        except Exception as exc:
            raise ASRError(f"Could not load Whisper model: {exc}") from exc


def transcribe_audio(audio_path: Path, settings: Settings) -> TranscriptionResult:
    if not audio_path.exists():
        raise ASRError("Converted audio file does not exist")

    model = _load_model(settings)

    try:
        segments_iter, info = model.transcribe(
            str(audio_path),
            beam_size=5,
            vad_filter=False,
        )
        segments = [
            TranscriptionSegment(
                start=round(segment.start, 3),
                end=round(segment.end, 3),
                text=segment.text.strip(),
            )
            for segment in segments_iter
            if segment.text.strip()
        ]
    except Exception as exc:
        raise ASRError(f"Whisper transcription failed: {exc}") from exc

    full_transcript = " ".join(segment.text for segment in segments).strip()

    return TranscriptionResult(
        detected_language=getattr(info, "language", None),
        language_probability=getattr(info, "language_probability", None),
        full_transcript=full_transcript,
        segments=segments,
    )
