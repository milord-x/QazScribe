# Backend

FastAPI backend for the QazScribe Conference AI Notes MVP.

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

Browser recording, ASR, translation, summaries, exports, and cleanup are planned for later stages.
