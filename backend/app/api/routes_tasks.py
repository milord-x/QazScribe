import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, status

from backend.app.config import get_settings
from backend.app.schemas.tasks import TaskResponse
from backend.app.storage.task_store import get_task


router = APIRouter(prefix="/api", tags=["tasks"])
settings = get_settings()


def _resolve_stored_path(stored_path: str | None) -> Path | None:
    if not stored_path:
        return None

    path = Path(stored_path)
    if path.is_absolute():
        return path
    return settings.project_root / path


def _with_full_translation_preview(task: dict) -> dict:
    hydrated_task = dict(task)
    translation_path = _resolve_stored_path(hydrated_task.get("translation_path"))
    if not translation_path or not translation_path.exists():
        return hydrated_task

    try:
        translation_data = json.loads(translation_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return hydrated_task

    translated_text = str(translation_data.get("translated_text") or "").strip()
    if translated_text:
        hydrated_task["translation_preview"] = translated_text
    target_language = str(translation_data.get("target_language") or "").strip()
    if target_language:
        hydrated_task["translation_target_language"] = target_language

    return hydrated_task


@router.get("/tasks/{task_id}", response_model=TaskResponse)
def read_task(task_id: str) -> TaskResponse:
    task = get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return TaskResponse(**_with_full_translation_preview(task))
