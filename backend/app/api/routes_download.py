from pathlib import Path

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse

from backend.app.config import get_settings
from backend.app.storage.task_store import get_task


router = APIRouter(prefix="/api", tags=["download"])
settings = get_settings()

FORMAT_TO_FILE = {
    "txt": ("qazscribe_result.txt", "text/plain"),
    "html": ("qazscribe_result.html", "text/html"),
    "docx": (
        "qazscribe_result.docx",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ),
    "pdf": ("qazscribe_result.pdf", "application/pdf"),
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


@router.get("/download/{task_id}/{file_format}")
def download_file(task_id: str, file_format: str) -> FileResponse:
    task = get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    if file_format not in FORMAT_TO_FILE:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unsupported download format",
        )

    filename, media_type = FORMAT_TO_FILE[file_format]
    path = _safe_output_path(task_id, filename)
    if not path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generated document not found",
        )

    return FileResponse(path, media_type=media_type, filename=filename)
