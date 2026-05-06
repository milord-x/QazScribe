#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="${QAZSCRIBE_BASE_DIR:-/media/proart/ssd/qazscribe}"
OWNER="${QAZSCRIBE_OWNER:-proart:proart}"

echo "Creating Qtranscript directories under ${BASE_DIR}"
sudo mkdir -p \
  "${BASE_DIR}/repo" \
  "${BASE_DIR}/data" \
  "${BASE_DIR}/uploads" \
  "${BASE_DIR}/processed" \
  "${BASE_DIR}/outputs" \
  "${BASE_DIR}/models/huggingface" \
  "${BASE_DIR}/models/torch" \
  "${BASE_DIR}/models/cache" \
  "${BASE_DIR}/logs" \
  "${BASE_DIR}/tmp" \
  "${BASE_DIR}/postgres" \
  "${BASE_DIR}/redis" \
  "${BASE_DIR}/backups"

sudo chown -R "${OWNER}" "${BASE_DIR}"

echo "Installing OS packages"
sudo apt update
sudo apt install -y git curl ffmpeg nginx ethtool ca-certificates

echo "Checking Docker"
docker --version
docker compose version

echo "Checking NVIDIA GPU"
nvidia-smi

echo "Done. Clone or pull the repository in ${BASE_DIR}/repo and run docker compose up -d --build."
