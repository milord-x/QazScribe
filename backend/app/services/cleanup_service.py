from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
import shutil
import time

from backend.app.config import Settings


class CleanupError(RuntimeError):
    """Raised when cleanup is asked to operate outside the data directory."""


@dataclass
class CleanupReport:
    deleted_uploads: int = 0
    deleted_processed: int = 0
    deleted_outputs: int = 0

    @property
    def total_deleted(self) -> int:
        return self.deleted_uploads + self.deleted_processed + self.deleted_outputs


def _is_safe_child(path: Path, parent: Path) -> bool:
    resolved_parent = parent.resolve()
    resolved_path = path.resolve()
    return resolved_path != resolved_parent and resolved_parent in resolved_path.parents


def _delete_expired_children(directory: Path, retention: timedelta) -> int:
    directory.mkdir(parents=True, exist_ok=True)
    cutoff = datetime.now().timestamp() - retention.total_seconds()
    deleted = 0

    for child in directory.iterdir():
        if child.name == ".gitkeep":
            continue
        if not _is_safe_child(child, directory):
            raise CleanupError(f"Refusing to delete unsafe path: {child}")
        try:
            child_mtime = child.stat().st_mtime
        except FileNotFoundError:
            continue

        if child_mtime > cutoff:
            continue

        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()
        deleted += 1

    return deleted


def run_cleanup(settings: Settings) -> CleanupReport:
    settings.data_path.mkdir(parents=True, exist_ok=True)

    report = CleanupReport()
    upload_retention = timedelta(hours=settings.upload_retention_hours)
    output_retention = timedelta(hours=settings.output_retention_hours)

    report.deleted_uploads = _delete_expired_children(
        settings.uploads_path,
        upload_retention,
    )
    report.deleted_processed = _delete_expired_children(
        settings.processed_path,
        upload_retention,
    )
    report.deleted_outputs = _delete_expired_children(
        settings.outputs_path,
        output_retention,
    )
    return report


def cleanup_loop(settings: Settings, stop_event) -> None:
    interval_seconds = max(settings.cleanup_interval_minutes, 1) * 60
    while not stop_event.wait(interval_seconds):
        try:
            run_cleanup(settings)
        except Exception:
            time.sleep(1)
