#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${QAZSCRIBE_BASE_URL:-http://127.0.0.1:8000}"

echo "== System =="
python3 --version || true
ffmpeg -version | head -n 1 || true
git --version || true

echo "== Docker =="
docker --version || true
docker compose version || true

echo "== GPU =="
nvidia-smi || true

echo "== Storage =="
df -h
python3 scripts/check_storage.py

echo "== Network =="
ethtool eno1 || true
ethtool eno2 || true

echo "== App health =="
curl -fsS "${BASE_URL}/health" || true
echo
curl -fsS "${BASE_URL}/health/storage" || true
echo
curl -fsS "${BASE_URL}/health/ai" || true
echo
