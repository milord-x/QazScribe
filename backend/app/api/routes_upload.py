from pathlib import Path
import json
import re
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile, status

from backend.app.config import get_settings
from backend.app.schemas.tasks import UploadResponse
from backend.app.services.asr_service import ASRError, transcribe_audio
from backend.app.services.audio_service import AudioConversionError, convert_to_wav_16khz_mono
from backend.app.services.document_service import DocumentGenerationError, generate_documents
from backend.app.services.summary_service import generate_structured_notes
from backend.app.services.translation_service import translate_to_kazakh
from backend.app.storage.task_store import create_task, get_task, update_task


router = APIRouter(prefix="/api", tags=["upload"])
settings = get_settings()

ALLOWED_EXTENSIONS = {".mp3", ".wav", ".m4a", ".ogg", ".webm", ".mp4"}
CHUNK_SIZE = 1024 * 1024


def _stored_path(path: Path) -> str:
    try:
        return str(path.relative_to(settings.project_root))
    except ValueError:
        return str(path)


def _safe_filename(filename: str) -> str:
    raw_name = Path(filename).name
    stem = Path(raw_name).stem
    suffix = Path(raw_name).suffix.lower()
    safe_stem = re.sub(r"[^A-Za-z0-9._-]+", "_", stem).strip("._")
    return f"{safe_stem or 'audio'}{suffix}"


def _format_speaker_preview(transcription_dict: dict) -> str:
    lines = []
    for segment in transcription_dict.get("segments") or []:
        speaker = segment.get("speaker") or "Спикер 1"
        start = float(segment.get("start") or 0)
        text = str(segment.get("text") or "").strip()
        if text:
            lines.append(f"[{start:06.2f}] {speaker}: {text}")
    return "\n".join(lines)


def _duration_seconds(transcription_dict: dict) -> float:
    segments = transcription_dict.get("segments") or []
    if not segments:
        return 0.0
    return max(float(segment.get("end") or 0) for segment in segments)


def _speaker_count(transcription_dict: dict) -> int:
    speakers = {
        str(segment.get("speaker") or "Спикер 1")
        for segment in transcription_dict.get("segments") or []
        if str(segment.get("text") or "").strip()
    }
    return len(speakers) if speakers else 0


def _process_uploaded_audio(task_id: str, source_path: Path) -> None:
    output_path = settings.processed_path / task_id / "audio_16khz_mono.wav"
    transcript_path = settings.processed_path / task_id / "transcript.json"
    translation_path = settings.processed_path / task_id / "translation.json"
    summary_path = settings.processed_path / task_id / "summary.json"

    try:
        update_task(
            task_id,
            status="converting_audio",
            progress=20,
            message="Converting audio to mono 16 kHz WAV",
            error="",
        )
        converted_path = convert_to_wav_16khz_mono(source_path, output_path)
        update_task(
            task_id,
            status="transcribing",
            progress=55,
            message="Transcribing audio with Whisper",
            processed_path=_stored_path(converted_path),
            error="",
        )
        transcription = transcribe_audio(converted_path, settings)
        transcription_dict = transcription.to_dict()
        speaker_preview = _format_speaker_preview(transcription_dict)
        duration_seconds = _duration_seconds(transcription_dict)
        speaker_count = _speaker_count(transcription_dict)
        transcript_path.write_text(
            json.dumps(transcription_dict, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        update_task(
            task_id,
            status="translating",
            progress=72,
            message="Translating transcript to Kazakh",
            transcript_path=_stored_path(transcript_path),
            detected_language=transcription.detected_language,
            transcript_preview=transcription.full_transcript[:1200],
            speaker_preview=speaker_preview[:1600],
            recording_duration_seconds=duration_seconds,
            speaker_count=speaker_count,
            error="",
        )
        translation = translate_to_kazakh(transcription.full_transcript, settings)
        translation_path.write_text(
            json.dumps(translation.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        update_task(
            task_id,
            status="summarizing",
            progress=86,
            message="Generating structured meeting notes",
            translation_path=_stored_path(translation_path),
            translation_preview=translation.translated_text[:1200],
            error="",
        )
        notes = generate_structured_notes(
            transcription.full_transcript,
            "" if translation.fallback_used else translation.translated_text,
            transcription.detected_language,
            settings,
        )
        summary_path.write_text(
            json.dumps(notes.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        update_task(
            task_id,
            status="generating_documents",
            progress=94,
            message="Generating TXT, HTML, DOCX, and PDF documents",
            result_available=True,
            summary_path=_stored_path(summary_path),
            summary_preview=notes.short_summary[:1200],
            detailed_summary_preview=notes.detailed_summary[:2000],
            error="",
        )
        task = get_task(task_id) or {}
        document_paths = generate_documents(
            task_id,
            settings.outputs_path / task_id,
            transcription.detected_language,
            transcription_dict,
            translation.to_dict(),
            notes.to_dict(),
            {
                "recording_started_at": task.get("created_at"),
                "recording_duration_seconds": duration_seconds,
                "speaker_count": speaker_count,
            },
        )
        downloads = {
            file_format: f"/api/download/{task_id}/{file_format}"
            for file_format in document_paths
        }
        update_task(
            task_id,
            status="completed",
            progress=100,
            message="Processing completed. Documents are ready for download.",
            result_available=True,
            downloads=downloads,
            error="",
        )
    except AudioConversionError as exc:
        update_task(
            task_id,
            status="failed",
            progress=100,
            message="Audio conversion failed",
            error=str(exc),
        )
    except ASRError as exc:
        update_task(
            task_id,
            status="failed",
            progress=100,
            message="Whisper transcription failed",
            error=str(exc),
        )
    except DocumentGenerationError as exc:
        update_task(
            task_id,
            status="failed",
            progress=100,
            message="Document generation failed",
            error=str(exc),
        )
    except Exception as exc:
        update_task(
            task_id,
            status="failed",
            progress=100,
            message="Unexpected audio processing failure",
            error=str(exc),
        )


@router.post("/upload", response_model=UploadResponse)
async def upload_audio(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
) -> UploadResponse:
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Audio file is required",
        )

    original_suffix = Path(file.filename).suffix.lower()
    if original_suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type",
        )

    task_id = str(uuid4())
    task_dir = settings.uploads_path / task_id
    task_dir.mkdir(parents=True, exist_ok=False)

    safe_name = _safe_filename(file.filename)
    destination = task_dir / safe_name
    total_size = 0

    try:
        with destination.open("wb") as output:
            while chunk := await file.read(CHUNK_SIZE):
                total_size += len(chunk)
                if total_size > settings.max_upload_bytes:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"Upload exceeds {settings.max_upload_mb} MB limit",
                    )
                output.write(chunk)
    except HTTPException:
        destination.unlink(missing_ok=True)
        task_dir.rmdir()
        raise
    finally:
        await file.close()

    if total_size == 0:
        destination.unlink(missing_ok=True)
        task_dir.rmdir()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty",
        )

    create_task(task_id, safe_name, _stored_path(destination))
    background_tasks.add_task(_process_uploaded_audio, task_id, destination)
    return UploadResponse(task_id=task_id, status="queued")
