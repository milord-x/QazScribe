#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="${QAZSCRIBE_BASE_DIR:-/media/proart/ssd/qazscribe}"
OWNER="${QAZSCRIBE_OWNER:-proart:proart}"

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
ls -lah "${BASE_DIR}"
