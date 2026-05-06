# qTranscript Kazakh-Kyrgyz Speech Recognition

qTranscript is a local GPU-based speech recognition system focused on Kazakh and
Kyrgyz institutional audio. The target pipeline is:

```text
audio -> Kazakh/Kyrgyz speech recognition -> speaker transcript -> document export
```

This repository contains a runnable FastAPI backend, static frontend,
upload/recording flow, Whisper transcription, document export, cleanup, and
Docker-oriented deployment files. Internal translation and structuring code is
kept in the backend for future use, but the public frontend is focused on
transcription and export.

## Project Structure

```text
backend/     FastAPI application
frontend/    Static HTML, CSS, and JavaScript
deploy/      Ubuntu, systemd, and nginx deployment files
docs/        Architecture, model, deployment, and evaluation notes
scripts/     Server initialization and health check helpers
data/        Local runtime storage, ignored by git
```

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Speech and Language Models](docs/MODELS.md)
- [Deployment Notes](docs/DEPLOYMENT.md)
- [qtranscript.kz Domain Setup](docs/DOMAIN.md)
- [Evaluation Plan](docs/EVALUATION.md)

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
downloading a Whisper model or connecting an external LLM service.

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

Without those values, QazScribe runs in local fallback mode and still generates
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
ASR_BACKEND=faster_whisper
ASR_MODEL_ID=
ASR_DEVICE=cuda
ASR_COMPUTE_TYPE=float16
ASR_LANGUAGE=
ASR_BEAM_SIZE=5
ASR_VAD_FILTER=true
ASR_INITIAL_PROMPT=Это запись лекции, конференции или заседания. Речь может быть на казахском или кыргызском языке. Эти языки похожи, поэтому сначала внимательно определи язык речи, затем точно распознай текст. Сохраняй имена, термины, числа и смысл фраз.
ASR_TRANSFORMERS_LANGUAGE=
ASR_TRUST_REMOTE_CODE=false
ASR_CHUNK_LENGTH_SECONDS=30
```

For the first public demo, `ASR_MODEL_SIZE=small` or `medium` starts faster and
uses less VRAM. Switch back to `large-v3` when the pipeline is stable.

The Docker image installs the CUDA 12 cuBLAS and cuDNN libraries required by
`faster-whisper` GPU inference.

qTranscript can also run experimental Hugging Face ASR models through
`transformers`:

```text
# Kazakh Whisper Large V3 model
ASR_BACKEND=transformers_whisper
ASR_MODEL_ID=InflexionLab/sybyrla
ASR_TRANSFORMERS_LANGUAGE=kazakh
ASR_TRUST_REMOTE_CODE=false

# Kyrgyz / Russian / English Whisper model
ASR_BACKEND=transformers_whisper
ASR_MODEL_ID=nineninesix/kyrgyz-whisper-medium
ASR_TRANSFORMERS_LANGUAGE=kyrgyz
ASR_TRUST_REMOTE_CODE=true

# Kyrgyz Wav2Vec2 CTC model
ASR_BACKEND=wav2vec2_ctc
ASR_MODEL_ID=kyrgyz-ai/Wav2vec-Kyrgyz
ASR_TRUST_REMOTE_CODE=false
```

The Whisper-based Kyrgyz model is better suited for Kyrgyz speech and
code-switching. The Wav2Vec2 model is Kyrgyz-only and should be treated as an
experimental comparison model. The browser recording screen exposes only Kazakh,
Kyrgyz, and auto mode.

For local translation and notes without external cloud services, run an OpenAI-compatible
local model server such as Ollama on the host and set:

```text
LLM_PROVIDER=ollama
LLM_API_BASE_URL=http://host.docker.internal:11434/v1
LLM_API_KEY=
LLM_MODEL=qwen2.5:7b
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
docker compose --env-file backend/.env up -d --build
```

If you use a custom logo, place `logo.png` in the repository root before
building the container. The app serves it as the site logo and favicon.

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
Internet user -> qtranscript.kz -> Nginx/Cloudflare -> qTranscript backend
```

Do not expose the workstation directly without HTTPS, upload limits, and access controls.
