import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse

from backend.app.config import get_settings
from backend.app.services.document_service import (
    DOCUMENT_FILENAMES,
    DocumentGenerationError,
    generate_document,
)
from backend.app.storage.task_store import get_task


router = APIRouter(prefix="/api", tags=["download"])
settings = get_settings()

FORMAT_TO_MEDIA_TYPE = {
    "txt": "text/plain",
    "srt": "application/x-subrip",
    "vtt": "text/vtt",
    "json": "application/json",
    "html": "text/html",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "pdf": "application/pdf",
}


def _safe_output_path(task_id: str, filename: str) -> Path:
    output_root = settings.outputs_path.resolve()
    path = (output_root / task_id / filename).resolve()
    if output_root not in path.parents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid download path",
        )
    return path


def _stored_path(value: str | None) -> Path | None:
    if not value:
        return None

    path = Path(value)
    if path.is_absolute():
        return path
    return settings.project_root / path


def _read_json_document(task: dict, key: str) -> dict:
    path = _stored_path(task.get(key))
    if not path or not path.exists():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Task is missing {key}",
        )

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cannot read {key}",
        ) from exc


def _ensure_document(task_id: str, file_format: str, task: dict) -> Path:
    filename = DOCUMENT_FILENAMES[file_format]
    path = _safe_output_path(task_id, filename)
    if path.exists():
        return path

    transcript = _read_json_document(task, "transcript_path")
    translation = _read_json_document(task, "translation_path")
    summary = _read_json_document(task, "summary_path")

    try:
        return generate_document(
            task_id,
            path,
            file_format,
            task.get("detected_language"),
            transcript,
            translation,
            summary,
            {
                "recording_started_at": task.get("recording_started_at") or task.get("created_at"),
                "recording_duration_seconds": task.get("recording_duration_seconds"),
                "speaker_count": task.get("speaker_count"),
            },
        )
    except DocumentGenerationError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc


@router.get("/download/{task_id}/{file_format}")
def download_file(task_id: str, file_format: str) -> FileResponse:
    task = get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    if file_format not in DOCUMENT_FILENAMES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unsupported download format",
        )

    if task.get("status") != "completed":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Task is not completed yet",
        )

    filename = DOCUMENT_FILENAMES[file_format]
    media_type = FORMAT_TO_MEDIA_TYPE[file_format]
    path = _ensure_document(task_id, file_format, task)
    return FileResponse(path, media_type=media_type, filename=filename)
