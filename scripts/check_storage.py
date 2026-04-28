import json
import os
from pathlib import Path
import shutil


def writable(path: Path) -> bool:
    try:
        path.mkdir(parents=True, exist_ok=True)
        test_file = path / ".qazscribe_write_test"
        test_file.write_text("ok", encoding="utf-8")
        test_file.unlink(missing_ok=True)
        return True
    except OSError:
        return False


def main() -> None:
    base_dir = Path(os.environ.get("QAZSCRIBE_BASE_DIR", "/media/proart/ssd/qazscribe"))
    usage_path = base_dir
    while not usage_path.exists() and usage_path != usage_path.parent:
        usage_path = usage_path.parent
    if not usage_path.exists():
        usage_path = Path.cwd()

    usage = shutil.disk_usage(usage_path)
    result = {
        "base_dir": str(base_dir),
        "disk_usage_path": str(usage_path),
        "base_dir_writable": writable(base_dir),
        "free_gb": round(usage.free / 1024**3, 2),
        "total_gb": round(usage.total / 1024**3, 2),
        "root_partition_warning": str(base_dir).startswith("/home") or str(base_dir).startswith("/var"),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
