from datetime import UTC, datetime
from threading import Lock
from typing import Any

from backend.app.schemas.tasks import TaskStatus


_tasks: dict[str, dict[str, Any]] = {}
_lock = Lock()


def create_task(task_id: str, filename: str, stored_path: str) -> dict[str, Any]:
    now = datetime.now(UTC).isoformat()
    task = {
        "task_id": task_id,
        "status": "queued",
        "progress": 0,
        "message": "File uploaded and queued for processing",
        "result_available": False,
        "filename": filename,
        "stored_path": stored_path,
        "processed_path": None,
        "transcript_path": None,
        "translation_path": None,
        "summary_path": None,
        "detected_language": None,
        "transcript_preview": None,
        "translation_preview": None,
        "summary_preview": None,
        "detailed_summary_preview": None,
        "speaker_preview": None,
        "recording_started_at": now,
        "recording_duration_seconds": None,
        "speaker_count": None,
        "error": None,
        "downloads": None,
        "created_at": now,
        "updated_at": now,
    }

    with _lock:
        _tasks[task_id] = task

    return task.copy()


def get_task(task_id: str) -> dict[str, Any] | None:
    with _lock:
        task = _tasks.get(task_id)
        return task.copy() if task else None


def update_task(
    task_id: str,
    *,
    status: TaskStatus | None = None,
    progress: int | None = None,
    message: str | None = None,
    result_available: bool | None = None,
    error: str | None = None,
    downloads: dict[str, str] | None = None,
    processed_path: str | None = None,
    transcript_path: str | None = None,
    translation_path: str | None = None,
    summary_path: str | None = None,
    detected_language: str | None = None,
    transcript_preview: str | None = None,
    translation_preview: str | None = None,
    summary_preview: str | None = None,
    detailed_summary_preview: str | None = None,
    speaker_preview: str | None = None,
    recording_started_at: str | None = None,
    recording_duration_seconds: float | None = None,
    speaker_count: int | None = None,
) -> dict[str, Any] | None:
    with _lock:
        task = _tasks.get(task_id)
        if not task:
            return None

        if status is not None:
            task["status"] = status
        if progress is not None:
            task["progress"] = progress
        if message is not None:
            task["message"] = message
        if result_available is not None:
            task["result_available"] = result_available
        if error is not None:
            task["error"] = error
        if downloads is not None:
            task["downloads"] = downloads
        if processed_path is not None:
            task["processed_path"] = processed_path
        if transcript_path is not None:
            task["transcript_path"] = transcript_path
        if translation_path is not None:
            task["translation_path"] = translation_path
        if summary_path is not None:
            task["summary_path"] = summary_path
        if detected_language is not None:
            task["detected_language"] = detected_language
        if transcript_preview is not None:
            task["transcript_preview"] = transcript_preview
        if translation_preview is not None:
            task["translation_preview"] = translation_preview
        if summary_preview is not None:
            task["summary_preview"] = summary_preview
        if detailed_summary_preview is not None:
            task["detailed_summary_preview"] = detailed_summary_preview
        if speaker_preview is not None:
            task["speaker_preview"] = speaker_preview
        if recording_started_at is not None:
            task["recording_started_at"] = recording_started_at
        if recording_duration_seconds is not None:
            task["recording_duration_seconds"] = recording_duration_seconds
        if speaker_count is not None:
            task["speaker_count"] = speaker_count

        task["updated_at"] = datetime.now(UTC).isoformat()
        return task.copy()
