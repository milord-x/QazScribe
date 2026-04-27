from fastapi import APIRouter, HTTPException, status

from backend.app.schemas.tasks import TaskResponse
from backend.app.storage.task_store import get_task


router = APIRouter(prefix="/api", tags=["tasks"])


@router.get("/tasks/{task_id}", response_model=TaskResponse)
def read_task(task_id: str) -> TaskResponse:
    task = get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return TaskResponse(**task)
