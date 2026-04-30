from dataclasses import asdict, dataclass
from pathlib import Path
from threading import Lock
from typing import Any
import wave

from backend.app.config import Settings


class ASRError(RuntimeError):
    """Raised when speech recognition fails."""


@dataclass
class TranscriptionSegment:
    start: float
    end: float
    text: str
    speaker: str = "Спикер 1"


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
_model_key: tuple[str, ...] | None = None
_model_lock = Lock()


def _assign_speakers(segments: list[TranscriptionSegment]) -> list[TranscriptionSegment]:
    speaker_index = 1
    previous_end = None

    for segment in segments:
        if previous_end is not None and segment.start - previous_end >= 1.8:
            speaker_index = 2 if speaker_index == 1 else 1
        segment.speaker = f"Спикер {speaker_index}"
        previous_end = segment.end

    return segments


def _wav_duration_seconds(audio_path: Path) -> float:
    try:
        with wave.open(str(audio_path), "rb") as wav_file:
            frames = wav_file.getnframes()
            rate = wav_file.getframerate()
            return frames / float(rate) if rate else 0.0
    except wave.Error:
        return 0.0


def _load_faster_whisper_model(settings: Settings):
    global _model, _model_key

    model_key = (
        "faster_whisper",
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


def _load_transformers_pipeline(settings: Settings):
    global _model, _model_key

    model_id = settings.asr_model_id or settings.asr_model_size
    backend = settings.asr_backend.strip().lower()
    model_key = (
        backend,
        model_id,
        settings.asr_device,
        settings.asr_compute_type,
        settings.asr_transformers_language or "",
        str(settings.asr_trust_remote_code),
    )

    with _model_lock:
        if _model is not None and _model_key == model_key:
            return _model

        try:
            import torch
            from transformers import (
                AutoModelForCTC,
                AutoModelForSpeechSeq2Seq,
                AutoProcessor,
                AutoTokenizer,
                WhisperFeatureExtractor,
                pipeline,
            )

            cuda_requested = settings.asr_device.startswith("cuda")
            device = "cuda:0" if cuda_requested and torch.cuda.is_available() else "cpu"
            device_index = 0 if device.startswith("cuda") else -1
            torch_dtype = (
                torch.float16
                if device.startswith("cuda") and "float16" in settings.asr_compute_type
                else torch.float32
            )

            common_kwargs = {"trust_remote_code": settings.asr_trust_remote_code}
            if backend == "transformers_whisper":
                model = AutoModelForSpeechSeq2Seq.from_pretrained(
                    model_id,
                    torch_dtype=torch_dtype,
                    low_cpu_mem_usage=True,
                    use_safetensors=True,
                    **common_kwargs,
                )
                model.to(device)
                tokenizer_kwargs = dict(common_kwargs)
                if settings.asr_transformers_language:
                    tokenizer_kwargs.update(
                        {
                            "language": settings.asr_transformers_language,
                            "task": "transcribe",
                        }
                    )
                tokenizer = AutoTokenizer.from_pretrained(model_id, **tokenizer_kwargs)
                feature_extractor = WhisperFeatureExtractor.from_pretrained(
                    model_id,
                    **common_kwargs,
                )
                _model = pipeline(
                    "automatic-speech-recognition",
                    model=model,
                    tokenizer=tokenizer,
                    feature_extractor=feature_extractor,
                    torch_dtype=torch_dtype,
                    device=device_index,
                )
            elif backend == "wav2vec2_ctc":
                processor = AutoProcessor.from_pretrained(model_id, **common_kwargs)
                model = AutoModelForCTC.from_pretrained(
                    model_id,
                    torch_dtype=torch_dtype,
                    **common_kwargs,
                )
                model.to(device)
                _model = pipeline(
                    "automatic-speech-recognition",
                    model=model,
                    tokenizer=processor.tokenizer,
                    feature_extractor=processor.feature_extractor,
                    torch_dtype=torch_dtype,
                    device=device_index,
                )
            else:
                raise ASRError(f"Unsupported ASR backend: {settings.asr_backend}")

            _model_key = model_key
            return _model
        except Exception as exc:
            raise ASRError(f"Could not load Hugging Face ASR model: {exc}") from exc


def _segments_from_transformers_result(
    result: dict[str, Any],
    audio_path: Path,
) -> list[TranscriptionSegment]:
    chunks = result.get("chunks") if isinstance(result, dict) else None
    segments: list[TranscriptionSegment] = []

    if chunks:
        for chunk in chunks:
            text = str(chunk.get("text") or "").strip()
            timestamp = chunk.get("timestamp") or (0.0, 0.0)
            start = timestamp[0] if timestamp[0] is not None else 0.0
            end = timestamp[1] if len(timestamp) > 1 and timestamp[1] is not None else start
            if text:
                segments.append(
                    TranscriptionSegment(
                        start=round(float(start), 3),
                        end=round(float(end), 3),
                        text=text,
                    )
                )

    if segments:
        return segments

    text = str(result.get("text") or "").strip() if isinstance(result, dict) else ""
    if not text:
        return []
    return [
        TranscriptionSegment(
            start=0.0,
            end=round(_wav_duration_seconds(audio_path), 3),
            text=text,
        )
    ]


def _transcribe_with_transformers(audio_path: Path, settings: Settings) -> TranscriptionResult:
    pipe = _load_transformers_pipeline(settings)

    try:
        call_kwargs: dict[str, Any] = {
            "chunk_length_s": settings.asr_chunk_length_seconds,
        }
        if settings.asr_backend.strip().lower() == "transformers_whisper":
            call_kwargs["return_timestamps"] = True
        result = pipe(str(audio_path), **call_kwargs)
    except TypeError:
        result = pipe(str(audio_path))
    except Exception as exc:
        raise ASRError(f"Hugging Face ASR transcription failed: {exc}") from exc

    if not isinstance(result, dict):
        raise ASRError("Hugging Face ASR returned an unexpected result")

    segments = _assign_speakers(_segments_from_transformers_result(result, audio_path))
    full_transcript = " ".join(segment.text for segment in segments).strip()
    detected_language = settings.asr_language or settings.asr_transformers_language

    return TranscriptionResult(
        detected_language=detected_language,
        language_probability=None,
        full_transcript=full_transcript,
        segments=segments,
    )


def transcribe_audio(audio_path: Path, settings: Settings) -> TranscriptionResult:
    if not audio_path.exists():
        raise ASRError("Converted audio file does not exist")

    if settings.asr_fake_transcript:
        text = settings.asr_fake_transcript.strip()
        return TranscriptionResult(
            detected_language="dev",
            language_probability=1.0,
            full_transcript=text,
            segments=[TranscriptionSegment(start=0.0, end=1.0, text=text)],
        )

    if settings.asr_backend.strip().lower() != "faster_whisper":
        return _transcribe_with_transformers(audio_path, settings)

    model = _load_faster_whisper_model(settings)

    try:
        segments_iter, info = model.transcribe(
            str(audio_path),
            beam_size=settings.asr_beam_size,
            vad_filter=settings.asr_vad_filter,
            language=settings.asr_language or None,
            initial_prompt=settings.asr_initial_prompt or None,
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
        segments = _assign_speakers(segments)
    except Exception as exc:
        raise ASRError(f"Whisper transcription failed: {exc}") from exc

    full_transcript = " ".join(segment.text for segment in segments).strip()

    return TranscriptionResult(
        detected_language=getattr(info, "language", None),
        language_probability=getattr(info, "language_probability", None),
        full_transcript=full_transcript,
        segments=segments,
    )
