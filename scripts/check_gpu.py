import json
import subprocess


def main() -> None:
    result = {
        "cuda_available": False,
        "gpu_name": None,
        "vram_total_gb": None,
        "nvidia_smi": "missing",
    }

    try:
        completed = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=name,memory.total,driver_version",
                "--format=csv,noheader,nounits",
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
        result["nvidia_smi"] = "ok" if completed.returncode == 0 else "failed"
        if completed.returncode == 0 and completed.stdout.strip():
            first_line = completed.stdout.strip().splitlines()[0]
            name, memory_mb, driver = [part.strip() for part in first_line.split(",")]
            result.update(
                {
                    "cuda_available": True,
                    "gpu_name": name,
                    "vram_total_gb": round(float(memory_mb) / 1024, 2),
                    "driver_version": driver,
                }
            )
    except Exception as exc:
        result["error"] = str(exc)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
