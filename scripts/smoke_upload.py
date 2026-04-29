#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
from pathlib import Path
import struct
import sys
import time
import wave

import httpx


def write_test_wav(path: Path, duration_seconds: float = 1.0) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    sample_rate = 16_000
    amplitude = 0.2
    frequency = 440
    frames = int(sample_rate * duration_seconds)

    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        for index in range(frames):
            value = int(32767 * amplitude * math.sin(2 * math.pi * frequency * index / sample_rate))
            wav_file.writeframes(struct.pack("<h", value))


def main() -> int:
    parser = argparse.ArgumentParser(description="Run QazScribe upload smoke test.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--timeout", type=int, default=180, help="Seconds to wait for completion.")
    parser.add_argument("--audio", type=Path, default=Path("/tmp/qazscribe-smoke.wav"))
    args = parser.parse_args()

    write_test_wav(args.audio)

    with httpx.Client(base_url=args.base_url, timeout=30) as client:
        health = client.get("/api/health")
        health.raise_for_status()
        print(f"health: {health.json()}")

        with args.audio.open("rb") as audio_file:
            upload = client.post(
                "/api/upload",
                files={"file": ("qazscribe-smoke.wav", audio_file, "audio/wav")},
            )
        upload.raise_for_status()
        task_id = upload.json()["task_id"]
        print(f"task: {task_id}")

        deadline = time.monotonic() + args.timeout
        task = {}
        while time.monotonic() < deadline:
            task_response = client.get(f"/api/tasks/{task_id}")
            task_response.raise_for_status()
            task = task_response.json()
            print(f"{task['status']}: {task['progress']}% - {task['message']}")
            if task["status"] in {"completed", "failed"}:
                break
            time.sleep(1)

        if task.get("status") != "completed":
            print(f"smoke test failed: {task}", file=sys.stderr)
            return 1

        downloads = task.get("downloads") or {}
        expected_formats = {"txt", "html", "docx", "pdf"}
        missing = expected_formats - set(downloads)
        if missing:
            print(f"missing downloads: {sorted(missing)}", file=sys.stderr)
            return 1

        for file_format, url in sorted(downloads.items()):
            download = client.get(url)
            download.raise_for_status()
            print(f"download {file_format}: {len(download.content)} bytes")

    print("smoke test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
