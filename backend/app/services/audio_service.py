from pathlib import Path
import shutil
import subprocess


class AudioConversionError(RuntimeError):
    """Raised when ffmpeg cannot convert an uploaded audio file."""


def convert_to_wav_16khz_mono(input_path: Path, output_path: Path) -> Path:
    ffmpeg_path = shutil.which("ffmpeg")
    if not ffmpeg_path:
        raise AudioConversionError("ffmpeg is not installed or not available in PATH")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    command = [
        ffmpeg_path,
        "-y",
        "-i",
        str(input_path),
        "-vn",
        "-ac",
        "1",
        "-ar",
        "16000",
        "-f",
        "wav",
        str(output_path),
    ]

    try:
        result = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=1800,
        )
    except subprocess.TimeoutExpired as exc:
        raise AudioConversionError("Audio conversion timed out") from exc
    except OSError as exc:
        raise AudioConversionError(f"Could not run ffmpeg: {exc}") from exc

    if result.returncode != 0:
        error_output = result.stderr.strip().splitlines()
        detail = error_output[-1] if error_output else "Unknown ffmpeg error"
        raise AudioConversionError(f"Audio conversion failed: {detail}")

    if not output_path.exists() or output_path.stat().st_size == 0:
        raise AudioConversionError("Audio conversion produced an empty file")

    return output_path
