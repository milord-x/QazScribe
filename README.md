# QazScribe Conference AI Notes

QazScribe is an MVP web system for conference and meeting audio. The target pipeline is:

```text
audio -> speech recognition -> Kazakh translation -> structured notes -> document export
```

This repository currently contains a runnable FastAPI backend, static frontend, health endpoint, upload/task status flow, and browser recording upload.

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

# Required for audio conversion
sudo apt install -y ffmpeg

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

Download endpoints:

```text
GET http://127.0.0.1:8000/api/download/{task_id}/txt
GET http://127.0.0.1:8000/api/download/{task_id}/html
GET http://127.0.0.1:8000/api/download/{task_id}/docx
GET http://127.0.0.1:8000/api/download/{task_id}/pdf
```

For the first local Whisper test, use a small model setting:

```bash
ASR_MODEL_SIZE=tiny ASR_DEVICE=cpu ASR_COMPUTE_TYPE=int8 \
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

External translation and structuring can be configured with an OpenAI-compatible chat completions endpoint:

```text
LLM_PROVIDER=openai_compatible
LLM_API_BASE_URL=https://example.com/v1
LLM_API_KEY=your_key_here
LLM_MODEL=your_model_name
```

Without those values, QazScribe runs in fallback mode and clearly marks translation as unavailable.

Runtime files are temporary. Uploads and processed audio are deleted after `UPLOAD_RETENTION_HOURS`; generated documents are deleted after `OUTPUT_RETENTION_HOURS`. Cleanup runs on startup and in a background loop.

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

Later stages will add Ubuntu deployment files.
