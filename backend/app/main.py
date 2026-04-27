from contextlib import asynccontextmanager
from pathlib import Path
from threading import Event, Thread

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.app.api.routes_download import router as download_router
from backend.app.api.routes_tasks import router as tasks_router
from backend.app.api.routes_upload import router as upload_router
from backend.app.config import get_settings
from backend.app.services.cleanup_service import cleanup_loop, run_cleanup


settings = get_settings()
cleanup_stop_event = Event()
cleanup_thread: Thread | None = None


@asynccontextmanager
async def lifespan(_: FastAPI):
    global cleanup_thread

    run_cleanup(settings)
    cleanup_thread = Thread(
        target=cleanup_loop,
        args=(settings, cleanup_stop_event),
        daemon=True,
    )
    cleanup_thread.start()

    yield

    cleanup_stop_event.set()
    if cleanup_thread and cleanup_thread.is_alive():
        cleanup_thread.join(timeout=2)


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="MVP web system for conference audio processing and Kazakh meeting notes.",
    lifespan=lifespan,
)

frontend_path = settings.frontend_path
assets_path = frontend_path

if assets_path.exists():
    app.mount("/static", StaticFiles(directory=assets_path), name="static")

app.include_router(upload_router)
app.include_router(tasks_router)
app.include_router(download_router)


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
