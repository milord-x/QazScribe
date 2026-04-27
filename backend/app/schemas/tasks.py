from typing import Literal

from pydantic import BaseModel, Field


TaskStatus = Literal[
    "queued",
    "processing",
    "converting_audio",
    "transcribing",
    "translating",
    "summarizing",
    "generating_documents",
    "completed",
    "failed",
]


class TaskResponse(BaseModel):
    task_id: str
    status: TaskStatus
    progress: int = Field(ge=0, le=100)
    message: str
    result_available: bool = False
    filename: str | None = None
    detected_language: str | None = None
    transcript_preview: str | None = None
    translation_preview: str | None = None
    summary_preview: str | None = None
    error: str | None = None
    downloads: dict[str, str] | None = None


class UploadResponse(BaseModel):
    task_id: str
    status: TaskStatus
