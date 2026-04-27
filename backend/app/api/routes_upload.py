from pathlib import Path
import re
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile, status

from backend.app.config import get_settings
from backend.app.schemas.tasks import UploadResponse
from backend.app.services.audio_service import AudioConversionError, convert_to_wav_16khz_mono
from backend.app.storage.task_store import create_task, update_task


router = APIRouter(prefix="/api", tags=["upload"])
settings = get_settings()

ALLOWED_EXTENSIONS = {".mp3", ".wav", ".m4a", ".ogg", ".webm", ".mp4"}
CHUNK_SIZE = 1024 * 1024


def _safe_filename(filename: str) -> str:
    raw_name = Path(filename).name
    stem = Path(raw_name).stem
    suffix = Path(raw_name).suffix.lower()
    safe_stem = re.sub(r"[^A-Za-z0-9._-]+", "_", stem).strip("._")
    return f"{safe_stem or 'audio'}{suffix}"


def _process_uploaded_audio(task_id: str, source_path: Path) -> None:
    output_path = settings.processed_path / task_id / "audio_16khz_mono.wav"

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
            status="completed",
            progress=100,
            message="Audio conversion completed. Transcription will be added in Stage 5.",
            result_available=False,
            processed_path=str(converted_path.relative_to(settings.project_root)),
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

    create_task(task_id, safe_name, str(destination.relative_to(settings.project_root)))
    background_tasks.add_task(_process_uploaded_audio, task_id, destination)
    return UploadResponse(task_id=task_id, status="queued")
