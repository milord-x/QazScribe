# Deployment Notes

## Target Server

The current deployment target is a local GPU workstation with:

```text
Ubuntu 24.04
NVIDIA RTX 4090
Docker
NVIDIA Container Toolkit
SSD-backed runtime storage
```

The Docker stack expects runtime data under `/srv/qazscribe` inside the
container. Host directories are mounted from the SSD storage path configured in
`docker-compose.yml`.

## Recommended Production Environment

Use `SERVER-ENV.txt` as the local template for `backend/.env` on the server.
This file is intentionally ignored by Git.

Main production mode:

```text
ASR_BACKEND=faster_whisper
ASR_MODEL_SIZE=large-v3
ASR_DEVICE=cuda
ASR_COMPUTE_TYPE=float16
```

## Update Procedure

```bash
cd /media/proart/ssd/qazscribe/repo/QazScribe
docker compose down
git pull
docker compose --env-file backend/.env up -d --build
docker compose logs backend --tail=80
```

## Health Checks

```bash
curl -s http://127.0.0.1/health
curl -s http://127.0.0.1/health/storage
curl -s http://127.0.0.1/health/ai
```

## Public Demonstration

For a short-term demonstration without DNS, forward the configured local HTTP
port with a tunnel:

```bash
ngrok http 80
```

This provides HTTPS access, which is important for browser microphone
permissions on mobile devices.

## Operational Notes

- The first ASR run may be slow because model weights are downloaded into the
  server cache.
- `large-v3` gives better quality but starts slower than `small` or `medium`.
- Hugging Face transformer backends add larger Python dependencies and should be
  used deliberately.
- Runtime files are removed by the cleanup service according to retention
  settings.
