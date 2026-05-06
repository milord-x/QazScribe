#!/usr/bin/env bash
set -euo pipefail

export APP_ENV="${APP_ENV:-development}"
export ASR_MODEL_SIZE="${ASR_MODEL_SIZE:-tiny}"
export ASR_DEVICE="${ASR_DEVICE:-cpu}"
export ASR_COMPUTE_TYPE="${ASR_COMPUTE_TYPE:-int8}"
export ASR_FAKE_TRANSCRIPT="${ASR_FAKE_TRANSCRIPT:-Это локальный тест Qtranscript. Сайт принимает аудио, показывает статусы и готовит документы локально.}"
export LLM_PROVIDER="${LLM_PROVIDER:-none}"

exec .venv/bin/uvicorn backend.app.main:app --reload --host 127.0.0.1 --port "${PORT:-8000}"
