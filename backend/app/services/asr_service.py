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
FASTER_WHISPER_LANGUAGE_HINTS = {"kk"}
KYRGYZ_MODEL_ID = "nineninesix/kyrgyz-whisper-medium"
MMS_MODEL_ID = "facebook/mms-1b-all"
MMS_LANGUAGE_ADAPTERS = {
    "kk": "kaz",
    "ky": "kir",
}


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


def _read_wav_mono_float32(audio_path: Path):
    try:
        import numpy as np

        with wave.open(str(audio_path), "rb") as wav_file:
            sample_width = wav_file.getsampwidth()
            channels = wav_file.getnchannels()
            frames = wav_file.readframes(wav_file.getnframes())

        if sample_width != 2:
            raise ASRError("MMS ASR expects 16-bit PCM WAV after conversion")

        audio = np.frombuffer(frames, dtype=np.int16).astype("float32") / 32768.0
        if channels > 1:
            audio = audio.reshape(-1, channels).mean(axis=1)
        return audio
    except ASRError:
        raise
    except Exception as exc:
        raise ASRError(f"Could not read WAV audio for MMS ASR: {exc}") from exc


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
                # Some fine-tuned Whisper checkpoints cover languages that are
                # not in the base Whisper tokenizer language list.
                if settings.asr_transformers_language and settings.asr_transformers_language not in {
                    "kyrgyz",
                    "ky",
                }:
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


def _load_mms_model(settings: Settings, target_lang: str):
    global _model, _model_key

    model_key = (
        "mms_ctc",
        MMS_MODEL_ID,
        target_lang,
        settings.asr_device,
        settings.asr_compute_type,
    )

    with _model_lock:
        if _model is not None and _model_key == model_key:
            return _model

        try:
            import torch
            from transformers import AutoProcessor, Wav2Vec2ForCTC

            cuda_requested = settings.asr_device.startswith("cuda")
            device = "cuda:0" if cuda_requested and torch.cuda.is_available() else "cpu"
            torch_dtype = (
                torch.float16
                if device.startswith("cuda") and "float16" in settings.asr_compute_type
                else torch.float32
            )

            processor = AutoProcessor.from_pretrained(MMS_MODEL_ID, target_lang=target_lang)
            model = Wav2Vec2ForCTC.from_pretrained(
                MMS_MODEL_ID,
                target_lang=target_lang,
                ignore_mismatched_sizes=True,
                torch_dtype=torch_dtype,
            )
            if hasattr(processor, "tokenizer") and hasattr(processor.tokenizer, "set_target_lang"):
                processor.tokenizer.set_target_lang(target_lang)
            if hasattr(model, "load_adapter"):
                model.load_adapter(target_lang)
            model.to(device)
            model.eval()
            _model = (processor, model, device)
            _model_key = model_key
            return _model
        except Exception as exc:
            raise ASRError(f"Could not load MMS ASR model: {exc}") from exc


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


def _transcribe_with_transformers(
    audio_path: Path,
    settings: Settings,
    language_hint: str | None = None,
) -> TranscriptionResult:
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
    detected_language = language_hint or settings.asr_language or settings.asr_transformers_language

    return TranscriptionResult(
        detected_language=detected_language,
        language_probability=None,
        full_transcript=full_transcript,
        segments=segments,
    )


def _transcribe_with_mms(
    audio_path: Path,
    settings: Settings,
    language_hint: str | None,
) -> TranscriptionResult:
    if language_hint not in MMS_LANGUAGE_ADAPTERS:
        raise ASRError("MMS ASR requires Kazakh or Kyrgyz language selection")

    try:
        import torch

        target_lang = MMS_LANGUAGE_ADAPTERS[language_hint]
        processor, model, device = _load_mms_model(settings, target_lang)
        audio = _read_wav_mono_float32(audio_path)
        inputs = processor(audio, sampling_rate=16_000, return_tensors="pt")
        inputs = {key: value.to(device) for key, value in inputs.items()}

        with torch.no_grad():
            logits = model(**inputs).logits

        predicted_ids = torch.argmax(logits, dim=-1)[0]
        text = processor.decode(predicted_ids).strip()
    except ASRError:
        raise
    except Exception as exc:
        raise ASRError(f"MMS ASR transcription failed: {exc}") from exc

    duration = round(_wav_duration_seconds(audio_path), 3)
    segments = [
        TranscriptionSegment(start=0.0, end=duration, text=text)
    ] if text else []
    segments = _assign_speakers(segments)

    return TranscriptionResult(
        detected_language=language_hint,
        language_probability=None,
        full_transcript=text,
        segments=segments,
    )


def transcribe_audio(
    audio_path: Path,
    settings: Settings,
    language_hint: str | None = None,
    asr_profile: str | None = None,
) -> TranscriptionResult:
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

    normalized_language_hint = (language_hint or "").strip().lower() or None
    normalized_asr_profile = (asr_profile or "").strip().lower() or "auto"

    if normalized_asr_profile == "mms":
        return _transcribe_with_mms(audio_path, settings, normalized_language_hint)

    if (
        normalized_language_hint == "ky"
        and settings.asr_backend.strip().lower() == "faster_whisper"
        and normalized_asr_profile in {"auto", "whisper"}
    ):
        kyrgyz_settings = settings.model_copy(
            update={
                "asr_backend": "transformers_whisper",
                "asr_model_id": KYRGYZ_MODEL_ID,
                "asr_transformers_language": "",
                "asr_trust_remote_code": True,
            }
        )
        return _transcribe_with_transformers(audio_path, kyrgyz_settings, normalized_language_hint)

    if settings.asr_backend.strip().lower() != "faster_whisper":
        return _transcribe_with_transformers(audio_path, settings, normalized_language_hint)

    model = _load_faster_whisper_model(settings)

    try:
        segments_iter, info = model.transcribe(
            str(audio_path),
            beam_size=settings.asr_beam_size,
            vad_filter=settings.asr_vad_filter,
            language=(
                normalized_language_hint
                if normalized_language_hint in FASTER_WHISPER_LANGUAGE_HINTS
                else settings.asr_language or None
            ),
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
        detected_language=normalized_language_hint or getattr(info, "language", None),
        language_probability=getattr(info, "language_probability", None),
        full_transcript=full_transcript,
        segments=segments,
    )
