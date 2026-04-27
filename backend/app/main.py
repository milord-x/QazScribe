from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.app.config import get_settings


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="MVP web system for conference audio processing and Kazakh meeting notes.",
)

frontend_path = settings.frontend_path
assets_path = frontend_path

if assets_path.exists():
    app.mount("/static", StaticFiles(directory=assets_path), name="static")


@app.get("/")
def index() -> FileResponse:
    index_file = frontend_path / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="Frontend index.html not found")
    return FileResponse(index_file)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": settings.app_name,
        "environment": settings.app_env,
    }
