# Backend

FastAPI backend for the Qtranscript Kazakh-Kyrgyz speech recognition MVP.

## Run Locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000`.

## Current Stage

Implemented:

- `GET /`
- `GET /api/health`
- `POST /api/upload`
- `GET /api/tasks/{task_id}`
- static frontend serving from `frontend/`
- browser recording upload through the same upload endpoint
- ffmpeg conversion to mono 16 kHz WAV
- faster-whisper transcription with CPU/CUDA configuration
- Kazakh translation and structured notes with fallback mode
- TXT, HTML, DOCX, and PDF document export
- retention cleanup for uploads, processed files, and outputs
- configurable server storage paths for `/media/proart/ssd/qazscribe`

Deployment is handled through the repository `Dockerfile`, `docker-compose.yml`, `deploy/`, and `scripts/` directories.
