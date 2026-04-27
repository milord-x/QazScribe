# QazScribe Conference AI Notes

QazScribe is an MVP web system for conference and meeting audio. The target pipeline is:

```text
audio -> speech recognition -> Kazakh translation -> structured notes -> document export
```

This repository currently contains a runnable FastAPI backend, static frontend, health endpoint, and Stage 2 upload/task status flow.

## Project Structure

```text
backend/     FastAPI application
frontend/    Static HTML, CSS, and JavaScript
deploy/      Deployment files and notes for later stages
data/        Local runtime storage, ignored by git
TASK.md      Full implementation task
```

## Local Development

```bash
cd ~/Projects/QazScribe

python3 -m venv .venv
source .venv/bin/activate

pip install -r backend/requirements.txt

uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

Then open:

```text
http://127.0.0.1:8000
```

Health check:

```text
http://127.0.0.1:8000/api/health
```

Upload endpoint:

```text
POST http://127.0.0.1:8000/api/upload
```

Task status endpoint:

```text
GET http://127.0.0.1:8000/api/tasks/{task_id}
```

## Configuration

Copy the example environment file if local overrides are needed:

```bash
cp backend/.env.example backend/.env
```

The default Stage 1 app runs without `.env`.

## Deployment Notes

Target Ubuntu checks for the later deployment machine:

```bash
nvidia-smi
python3 --version
ffmpeg -version
git --version
```

Later stages will add browser recording, ffmpeg conversion, faster-whisper transcription, Kazakh translation, document exports, cleanup, and Ubuntu deployment files.
