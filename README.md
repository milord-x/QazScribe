# QazScribe Conference AI Notes

QazScribe is an MVP web system for conference and meeting audio. The target pipeline is:

```text
audio -> speech recognition -> Kazakh translation -> structured notes -> document export
```

This repository currently contains a runnable FastAPI backend, static frontend, upload/recording flow, Whisper transcription, fallback translation/summary, document export, cleanup, and Docker-oriented deployment files.

## Project Structure

```text
backend/     FastAPI application
frontend/    Static HTML, CSS, and JavaScript
deploy/      Ubuntu, systemd, and nginx deployment files
scripts/     Server initialization and health check helpers
data/        Local runtime storage, ignored by git
```

## Local Development

```bash
cd ~/Projects/QazScribe

python3 -m venv .venv
source .venv/bin/activate

pip install -r backend/requirements.txt

# Required for audio conversion
sudo apt install -y ffmpeg

./scripts/run_local_dev.sh
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

The local dev script uses `ASR_FAKE_TRANSCRIPT` by default. This means upload,
progress, fallback notes, and document downloads can be tested quickly without
downloading a Whisper model and without paid API keys.

Run the HTTP smoke test while the local server is running:

```bash
./scripts/smoke_upload.py
```

For a real local Whisper test, disable fake ASR and use a small CPU model:

```bash
ASR_FAKE_TRANSCRIPT= ASR_MODEL_SIZE=tiny ASR_DEVICE=cpu ASR_COMPUTE_TYPE=int8 \
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

External translation and structuring are optional. They can be configured with an
OpenAI-compatible chat completions endpoint:

```text
LLM_PROVIDER=openai_compatible
LLM_API_BASE_URL=https://example.com/v1
LLM_API_KEY=your_key_here
LLM_MODEL=your_model_name
```

Without those values, QazScribe runs in free fallback mode and still generates
result documents.

Runtime files are temporary. Uploads and processed audio are deleted after `UPLOAD_RETENTION_HOURS`; generated documents are deleted after `OUTPUT_RETENTION_HOURS`. Cleanup runs on startup and in a background loop.

## Configuration

Copy the example environment file if local overrides are needed:

```bash
cp backend/.env.example backend/.env
```

The default local app runs without `.env`.

## New GPU Server Deployment

The current target machine is a local GPU workstation/server:

```text
Ubuntu 24.04.3 LTS
Intel Core i9-14900KF
128 GB RAM
NVIDIA RTX 4090 24 GB VRAM
```

Important storage rule:

```text
Do not store uploads, outputs, models, logs, or temp files on /.
Use /media/proart/ssd/qazscribe.
```

Initialize server directories:

```bash
cd /media/proart/ssd/qazscribe/repo
./scripts/init_server_dirs.sh
```

Or run the broader Ubuntu helper:

```bash
./deploy/install_ubuntu.sh
```

Recommended server `.env`:

```bash
cp backend/.env.example backend/.env
```

Then set:

```text
QAZSCRIBE_BASE_DIR=/media/proart/ssd/qazscribe
QAZSCRIBE_DATA_DIR=/media/proart/ssd/qazscribe/data
QAZSCRIBE_UPLOADS_DIR=/media/proart/ssd/qazscribe/uploads
QAZSCRIBE_PROCESSED_DIR=/media/proart/ssd/qazscribe/processed
QAZSCRIBE_OUTPUTS_DIR=/media/proart/ssd/qazscribe/outputs
QAZSCRIBE_MODELS_DIR=/media/proart/ssd/qazscribe/models
QAZSCRIBE_LOGS_DIR=/media/proart/ssd/qazscribe/logs
QAZSCRIBE_TMP_DIR=/media/proart/ssd/qazscribe/tmp

ASR_MODEL_SIZE=large-v3
ASR_DEVICE=cuda
ASR_COMPUTE_TYPE=float16
```

Model cache variables for the server:

```text
HF_HOME=/media/proart/ssd/qazscribe/models/huggingface
TRANSFORMERS_CACHE=/media/proart/ssd/qazscribe/models/huggingface
TORCH_HOME=/media/proart/ssd/qazscribe/models/torch
XDG_CACHE_HOME=/media/proart/ssd/qazscribe/models/cache
```

Start with Docker Compose:

```bash
docker compose up -d --build
```

Stop:

```bash
docker compose down
```

Logs:

```bash
docker compose logs -f
```

Health checks:

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/health/storage
http://127.0.0.1:8000/health/ai
```

Server checks:

```bash
nvidia-smi
python3 --version
ffmpeg -version
git --version
docker --version
docker compose version
./scripts/check_server.sh
```

Network note: the new server has a 10G-capable adapter, but the observed Ethernet link was only 100 Mbps. For large uploads, check cable, wall port, switch, and `ethtool eno1`.

## Public Access

For MVP public access, put Nginx or Cloudflare Tunnel in front of the Docker stack:

```text
Internet user -> HTTPS URL -> Cloudflare Tunnel/Nginx -> QazScribe backend
```

Do not expose the workstation directly without HTTPS, upload limits, and access controls.
