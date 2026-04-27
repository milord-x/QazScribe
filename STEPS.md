# QazScribe Development Steps

This file is the execution plan from the current MVP skeleton to the finished prototype.

Work rule:

```text
One request = one small stage or one clearly bounded sub-step.
After each stable change: test, commit, push.
Do not jump ahead unless the user explicitly changes the priority.
```

## Current State

Completed:

- Git repository exists and is connected to GitHub.
- Stage 1 skeleton exists.
- FastAPI app starts.
- Static frontend opens.
- `GET /api/health` works.
- Basic project structure exists.

Current next stage:

```text
Stage 2 — File Upload and Task Creation
```

## Stage 2 — File Upload and Task Creation

Goal:

User can upload an existing audio/video file and receive a task ID.

Steps:

1. Create shared task status storage.
2. Define task statuses and response schemas.
3. Implement `POST /api/upload`.
4. Validate supported extensions: `mp3`, `wav`, `m4a`, `ogg`, `webm`, `mp4`.
5. Validate empty files and max upload size.
6. Save uploaded file to `data/uploads/{task_id}/`.
7. Implement `GET /api/tasks/{task_id}`.
8. Connect upload form in `frontend/app.js`.
9. Show task ID, status, progress, and error messages in the UI.
10. Verify upload with a small sample file.
11. Commit and push.

Acceptance:

```text
User uploads a file.
Backend stores it safely under a UUID task ID.
Frontend shows the created task and current status.
No Whisper yet.
```

## Stage 3 — Browser Recording

Goal:

User can record audio in the browser and upload it as a task.

Steps:

1. Implement `MediaRecorder` setup in frontend.
2. Add recording state handling: idle, recording, ready, uploading.
3. Wire start, stop, and upload recording buttons.
4. Upload recorded `.webm` blob through the same `/api/upload` endpoint.
5. Show recording errors clearly if microphone access is denied.
6. Test in browser over localhost.
7. Commit and push.

Acceptance:

```text
User records audio.
Recording uploads to backend.
Task ID is created.
```

## Stage 4 — Audio Conversion

Goal:

Normalize uploaded/recorded audio before ASR.

Steps:

1. Add `ffmpeg` requirement to README and deployment notes.
2. Implement safe subprocess conversion in `audio_service.py`.
3. Convert to mono 16 kHz WAV.
4. Store converted audio in `data/processed/{task_id}/`.
5. Add conversion status: `converting_audio`.
6. Handle missing `ffmpeg` with clear task failure.
7. Handle unsupported/corrupt audio with clear task failure.
8. Trigger conversion after upload.
9. Verify conversion with small audio files.
10. Commit and push.

Acceptance:

```text
Uploaded audio becomes normalized WAV.
Failures are visible in task status and frontend.
```

## Stage 5 — Whisper Transcription

Goal:

Transcribe converted audio using `faster-whisper`.

Steps:

1. Add `faster-whisper` dependency.
2. Extend config for `ASR_MODEL_SIZE`, `ASR_DEVICE`, `ASR_COMPUTE_TYPE`.
3. Implement `asr_service.py`.
4. Support CPU defaults for laptop development.
5. Keep CUDA configurable for Ubuntu RTX deployment.
6. Return detected language, timestamped segments, and full transcript.
7. Save transcript metadata under task output/state.
8. Add status: `transcribing`.
9. Show transcript preview and detected language in frontend.
10. Test with a short file on CPU.
11. Commit and push.

Acceptance:

```text
Audio is transcribed.
Detected language and transcript preview are visible.
App still runs on CPU.
```

## Stage 6 — Translation and Structuring

Goal:

Generate Kazakh translation and structured notes.

Steps:

1. Add translation provider config placeholders to `.env.example`.
2. Implement provider-independent `translation_service.py`.
3. Return clear fallback text when no API key/provider is configured.
4. Implement `summary_service.py`.
5. Generate structured fields: title, summaries, key points, decisions, action items, speakers, risks, final notes.
6. Add statuses: `translating`, `summarizing`.
7. Show translation and summary preview in frontend.
8. Test both fallback mode and configured-provider mode if credentials are provided.
9. Commit and push.

Acceptance:

```text
Kazakh translation is generated or fallback is shown.
Structured notes are generated.
No API key is committed.
App does not crash without API credentials.
```

Decision needed before provider implementation:

```text
Which external LLM/translation API should be used first, if any?
```

## Stage 7 — Document Export

Goal:

Generate downloadable result files.

Steps:

1. Add document generation dependencies.
2. Implement TXT export.
3. Implement HTML export.
4. Implement DOCX export.
5. Implement PDF export.
6. Save files to `data/outputs/{task_id}/`.
7. Add `GET /api/download/{task_id}/txt`.
8. Add `GET /api/download/{task_id}/html`.
9. Add `GET /api/download/{task_id}/docx`.
10. Add `GET /api/download/{task_id}/pdf`.
11. Add status: `generating_documents`.
12. Add download buttons in frontend.
13. Verify all four files download.
14. Commit and push.

Acceptance:

```text
User can download TXT, HTML, DOCX, and PDF.
Files contain transcript, Kazakh translation, summary, and structured notes.
```

## Stage 8 — Cleanup System

Goal:

Prevent the Ubuntu machine from filling its limited root partition.

Steps:

1. Add `TASK_RETENTION_DAYS` config.
2. Implement safe cleanup helpers in `cleanup_service.py`.
3. Delete expired uploads after configured hours.
4. Delete expired processed files after configured hours.
5. Delete expired outputs after configured hours.
6. Ensure cleanup never deletes outside project `data/`.
7. Run cleanup on app startup.
8. Optionally add a background cleanup loop.
9. Add logs for deleted task directories.
10. Verify cleanup with temporary test folders.
11. Commit and push.

Acceptance:

```text
Expired files are removed safely.
Cleanup cannot escape the data directory.
```

## Stage 9 — Frontend MVP Polish

Goal:

Make the first demo usable on desktop and mobile.

Steps:

1. Improve upload and recording states.
2. Add progress/status area.
3. Add result preview area.
4. Add clear error display.
5. Add responsive mobile layout checks.
6. Keep the UI simple and avoid heavy frameworks.
7. Test on browser width close to mobile.
8. Commit and push.

Acceptance:

```text
The app is understandable for a demo.
No horizontal overflow on mobile.
Main workflow is visible from one page.
```

## Stage 10 — Ubuntu Deployment Files

Goal:

Prepare files needed to install and run the app on the target Ubuntu PC.

Steps:

1. Create `deploy/install_ubuntu.sh`.
2. Create `deploy/qazscribe.service`.
3. Create `deploy/nginx.conf`.
4. Create `deploy/cloudflare-tunnel-notes.md`.
5. Document CPU mode and CUDA mode.
6. Document `ffmpeg`, Python venv, and dependency install.
7. Document `nvidia-smi` and driver checks.
8. Document storage cleanup expectations.
9. Commit and push.

Acceptance:

```text
User can clone the repo on Ubuntu and follow deployment docs.
```

## Stage 11 — Ubuntu RTX Setup and Test

Goal:

Run the prototype on the customer Ubuntu machine with RTX 4070 Ti.

Steps:

1. Clone/pull GitHub repository on Ubuntu.
2. Create venv and install dependencies.
3. Install/check `ffmpeg`.
4. Check NVIDIA driver with `nvidia-smi`.
5. Configure `.env` for CUDA:

```text
ASR_DEVICE=cuda
ASR_COMPUTE_TYPE=float16
ASR_MODEL_SIZE=medium
```

6. Run local server on Ubuntu.
7. Upload a short audio file and test full pipeline.
8. Watch disk usage during processing.
9. Adjust model size if memory or speed is bad.
10. Commit deployment documentation fixes if needed and push.

Acceptance:

```text
Ubuntu machine processes audio with GPU or documented fallback.
Full MVP pipeline works on the target machine.
```

## Stage 12 — Public Access

Goal:

Expose the Ubuntu-hosted app through a public HTTPS URL.

Steps:

1. Choose final public access method.
2. Prefer Cloudflare Tunnel for MVP unless blocked.
3. Install and authenticate `cloudflared` on Ubuntu.
4. Route public domain/subdomain to local app or nginx.
5. Confirm upload size behavior through tunnel.
6. Test from another network or mobile data.
7. Document final public URL and startup commands.
8. Commit final deployment notes and push.

Acceptance:

```text
The site is reachable from outside the local network.
Audio upload and result download work through the public URL.
```

Decision needed before this stage:

```text
Which domain or Cloudflare account will be used?
```

## Stage 13 — Demo Readiness

Goal:

Prepare a stable demonstration build.

Steps:

1. Prepare one short demo audio file outside git.
2. Test upload-to-download workflow end to end.
3. Check all output formats.
4. Check cleanup does not remove active files.
5. Confirm no secrets are committed.
6. Confirm GitHub has latest code.
7. Write final demo instructions in README.
8. Commit and push.

Acceptance:

```text
The system can be demonstrated without explaining unfinished internals.
```

## Information To Ask From User When Needed

Ask only when the step requires information not present in markdown files.

Likely questions:

1. Which LLM/translation provider should be used for Kazakh translation and summaries?
2. Is there an API key available, or should fallback mode be used for the first demo?
3. What public domain/subdomain should be used for Cloudflare Tunnel?
4. What maximum audio duration should be allowed for the first demo?
5. Should the UI language be Russian, Kazakh, English, or mixed for the demo?

## Command Pattern For Future Requests

Recommended user request format:

```text
Выполни следующий шаг из STEPS.md
```

or:

```text
Выполни Stage 2 из STEPS.md
```

Each completed stage should end with:

```text
tests/checks done
git commit done
git push done
next stage named
```
