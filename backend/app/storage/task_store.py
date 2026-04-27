from datetime import UTC, datetime
from threading import Lock
from typing import Any

from backend.app.schemas.tasks import TaskStatus


_tasks: dict[str, dict[str, Any]] = {}
_lock = Lock()


def create_task(task_id: str, filename: str, stored_path: str) -> dict[str, Any]:
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
        "detected_language": None,
        "transcript_preview": None,
        "error": None,
        "downloads": None,
        "created_at": datetime.now(UTC).isoformat(),
        "updated_at": datetime.now(UTC).isoformat(),
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
    detected_language: str | None = None,
    transcript_preview: str | None = None,
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
        if detected_language is not None:
            task["detected_language"] = detected_language
        if transcript_preview is not None:
            task["transcript_preview"] = transcript_preview

        task["updated_at"] = datetime.now(UTC).isoformat()
        return task.copy()
