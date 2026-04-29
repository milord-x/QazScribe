from contextlib import asynccontextmanager
from pathlib import Path
import shutil
import subprocess
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


@app.middleware("http")
async def prevent_frontend_cache(request, call_next):
    response = await call_next(request)
    if request.url.path in {"/", "/logo.png", "/favicon.ico"} or request.url.path.startswith("/static/"):
        response.headers["Cache-Control"] = "no-store"
    return response


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


@app.get("/logo.png")
def logo() -> FileResponse:
    logo_file = settings.project_root / "logo.png"
    if not logo_file.exists():
        raise HTTPException(status_code=404, detail="Logo not found")
    return FileResponse(logo_file, media_type="image/png")


@app.get("/favicon.ico")
def favicon() -> FileResponse:
    logo_file = settings.project_root / "logo.png"
    if not logo_file.exists():
        raise HTTPException(status_code=404, detail="Favicon not found")
    return FileResponse(logo_file, media_type="image/png")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": settings.app_name,
        "environment": settings.app_env,
    }


@app.get("/health")
def root_health() -> dict[str, str]:
    return {
        "status": "ok",
        "backend": "ok",
        "storage": "ok" if settings.data_path.exists() else "missing",
    }


def _is_writable(path: Path) -> bool:
    try:
        path.mkdir(parents=True, exist_ok=True)
        test_file = path / ".qazscribe_write_test"
        test_file.write_text("ok", encoding="utf-8")
        test_file.unlink(missing_ok=True)
        return True
    except OSError:
        return False


def _disk_usage_path(path: Path) -> Path:
    usage_path = path
    while not usage_path.exists() and usage_path != usage_path.parent:
        usage_path = usage_path.parent
    return usage_path if usage_path.exists() else Path.cwd()


@app.get("/health/storage")
def storage_health() -> dict[str, object]:
    paths = {
        "data": settings.data_path,
        "uploads": settings.uploads_path,
        "processed": settings.processed_path,
        "outputs": settings.outputs_path,
        "models": settings.models_path,
        "logs": settings.logs_path,
        "tmp": settings.tmp_path,
    }
    writable = {name: _is_writable(path) for name, path in paths.items()}
    usage_path = _disk_usage_path(settings.data_path)
    usage = shutil.disk_usage(usage_path)
    return {
        "status": "ok" if all(writable.values()) else "failed",
        "paths": {name: str(path) for name, path in paths.items()},
        "writable": writable,
        "disk_usage_path": str(usage_path),
        "free_gb": round(usage.free / 1024**3, 2),
        "total_gb": round(usage.total / 1024**3, 2),
        "root_partition_warning": str(settings.data_path).startswith("/home")
        or str(settings.data_path).startswith("/var"),
    }


@app.get("/health/ai")
def ai_health() -> dict[str, object]:
    cuda_available = False
    gpu_name = None
    vram_total_gb = None

    try:
        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=name,memory.total",
                "--format=csv,noheader,nounits",
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            first_line = result.stdout.strip().splitlines()[0]
            parts = [part.strip() for part in first_line.split(",")]
            gpu_name = parts[0]
            if len(parts) > 1:
                vram_total_gb = round(float(parts[1]) / 1024, 2)
            cuda_available = True
    except Exception:
        cuda_available = False

    return {
        "cuda_available": cuda_available,
        "gpu_name": gpu_name,
        "vram_total_gb": vram_total_gb,
        "asr_model_size": settings.asr_model_size,
        "asr_device": settings.asr_device,
        "asr_compute_type": settings.asr_compute_type,
        "model_dir": str(settings.models_path),
        "model_dir_writable": _is_writable(settings.models_path),
        "uploads_dir_writable": _is_writable(settings.uploads_path),
        "outputs_dir_writable": _is_writable(settings.outputs_path),
    }
