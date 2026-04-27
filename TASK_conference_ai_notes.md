344# TASK: Conference AI Notes — MVP Web System

## 0. Context

We are building a fast MVP web system for a paid university-related project.

The system is for conferences, meetings, academic sessions, and similar events.  
Its purpose is to convert speech/audio into a structured Kazakh-language document.

Main pipeline:

```text
Audio conference / recorded speech
→ speech recognition
→ text transcription
→ Kazakh translation
→ structured summary / meeting notes
→ export to multiple document formats
```

The user will mainly develop on their own laptop and push all work to GitHub.  
The target deployment machine is a separate Ubuntu desktop PC with RTX 4070 Ti.  
Do not assume we are coding directly on that Ubuntu machine right now.

Current workflow:

1. Project already exists inside `~/Projects`.
2. GitHub repository is already connected.
3. Development happens locally on the user's laptop.
4. Every meaningful change must be committed/pushed to GitHub.
5. After the first working prototype is ready, it will be cloned/deployed on the Ubuntu RTX machine.
6. Then GPU/Whisper/CUDA deployment will be configured and tested there.

Do not build a huge enterprise system.  
The immediate goal is a working MVP prototype that can be shown quickly.

---

## 1. Target Deployment Machine

Target machine specs:

```text
OS: Ubuntu 24.04.1 LTS
CPU: Intel Core i5-13400F
GPU: NVIDIA GeForce RTX 4070 Ti
RAM: 16 GB
Disk: NVMe, but root partition has limited free space
NVIDIA driver: 535.230.02
```

Important:

- The target Ubuntu machine has RTX 4070 Ti, so ASR should be designed to support GPU acceleration.
- But the first prototype must also run on the developer laptop without requiring GPU.
- GPU-specific setup should be isolated and documented.
- Do not hard-code machine-specific paths.
- Do not assume permanent large storage.
- Uploaded audio and generated files must be temporary and automatically cleaned.

---

## 2. Product Goal

Build a public web application for processing conference audio.

User can:

1. Open a website.
2. Upload an audio file.
3. Or record audio directly in the browser.
4. Send the audio to the backend.
5. Backend transcribes speech using Whisper/faster-whisper.
6. Backend translates or normalizes the result into Kazakh.
7. Backend generates:
   - full transcript,
   - Kazakh translation,
   - short summary,
   - structured meeting notes,
   - decisions,
   - action items,
   - key points.
8. User downloads the result in 4 formats:
   - TXT,
   - DOCX,
   - PDF,
   - HTML.

No login/auth is needed for MVP.

---

## 3. Critical Constraint

This is a short-deadline MVP.

Do not over-engineer.

Avoid:

- complex user accounts,
- roles/permissions,
- admin panels,
- heavy database design,
- microservices,
- Docker-only dependency if it slows progress,
- Next.js/React complexity unless already present,
- fancy UI before backend works,
- complicated offline LLM stack at the first stage.

Prefer:

- simple backend,
- simple frontend,
- clear working pipeline,
- local filesystem storage,
- SQLite only if needed for task status,
- clean modular Python code,
- easy deployment instructions.

---

## 4. Preferred Stack

Use this unless the existing project already has a different clear structure:

```text
Backend: Python + FastAPI
Frontend: plain HTML/CSS/JavaScript
ASR: faster-whisper
Audio conversion: ffmpeg
Document generation:
  - TXT: plain file
  - DOCX: python-docx
  - PDF: HTML-to-PDF or ReportLab
  - HTML: Jinja2 template
Storage: local filesystem
Task status: in-memory or SQLite
Deployment: uvicorn + systemd + nginx or Cloudflare Tunnel later
```

Reason:

- FastAPI is fast to build.
- Plain frontend is easier to deploy.
- No need for npm complexity for MVP.
- Python ecosystem is good for ASR and document generation.

---

## 5. Required Project Structure

If structure is absent, create this:

```text
conference-ai-notes/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── api/
│   │   │   ├── routes_upload.py
│   │   │   ├── routes_tasks.py
│   │   │   └── routes_download.py
│   │   ├── services/
│   │   │   ├── audio_service.py
│   │   │   ├── asr_service.py
│   │   │   ├── translation_service.py
│   │   │   ├── summary_service.py
│   │   │   ├── document_service.py
│   │   │   └── cleanup_service.py
│   │   ├── schemas/
│   │   ├── storage/
│   │   └── utils/
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
│
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── app.js
│
├── deploy/
│   ├── install_ubuntu.sh
│   ├── conference-ai.service
│   ├── nginx.conf
│   └── cloudflare-tunnel-notes.md
│
├── data/
│   ├── uploads/
│   ├── processed/
│   └── outputs/
│
├── .gitignore
├── README.md
└── TASK.md
```

Do not commit generated audio files, output documents, virtual environments, cache files, or secrets.

---

## 6. MVP Features

### 6.1 Audio Upload

Implement a frontend upload form.

Supported file types:

```text
mp3, wav, m4a, ogg, webm, mp4
```

Backend must:

- validate extension,
- validate size,
- store file under `data/uploads/{task_id}/`,
- create task ID,
- start processing,
- return task ID.

For MVP, synchronous processing is acceptable only for short files.  
Prefer background task if simple.

Recommended endpoint:

```text
POST /api/upload
```

Response:

```json
{
  "task_id": "...",
  "status": "queued"
}
```

---

### 6.2 Browser Recording

Frontend must support recording from microphone using `MediaRecorder`.

Buttons:

```text
Start recording
Stop recording
Upload recording
```

The browser recording can produce `.webm`.

Backend treats it like uploaded audio.

Do not overcomplicate live streaming in MVP.  
This is not required:

```text
real-time transcription while speaking
```

MVP recording flow:

```text
record in browser → save blob → upload to backend → process
```

---

### 6.3 Audio Conversion

Use `ffmpeg`.

Convert input to a standard temporary format:

```text
mono, 16 kHz WAV
```

Example conceptual target:

```text
ffmpeg -i input -ac 1 -ar 16000 output.wav
```

Implement through Python subprocess safely.

Do not concatenate shell strings unsafely.

---

### 6.4 Speech Recognition

Use `faster-whisper`.

Create `asr_service.py`.

Requirements:

- support CPU mode for development laptop;
- support CUDA mode for target RTX machine;
- configurable model size;
- configurable compute type;
- language auto-detection by default.

Configuration should be in `.env` or `config.py`.

Example config keys:

```text
ASR_MODEL_SIZE=small
ASR_DEVICE=cpu
ASR_COMPUTE_TYPE=int8
```

For RTX deployment later:

```text
ASR_MODEL_SIZE=medium
ASR_DEVICE=cuda
ASR_COMPUTE_TYPE=float16
```

Do not hard-code CUDA in the first version.

The ASR result must include:

```text
detected language
segments with timestamps
full transcript
```

---

### 6.5 Translation to Kazakh

For MVP, implement a replaceable translation service.

Do not lock the whole project to one provider.

Create `translation_service.py` with one public function like:

```python
translate_to_kazakh(text: str) -> str
```

Initial implementation can be:

1. API-based LLM translation if API key is configured.
2. Fallback dummy/no-op mode if no API key exists.

The app must still run without API keys, but it should clearly mark translation as unavailable or fallback.

Important:

- Do not invent API keys.
- Do not hard-code secrets.
- Use `.env.example`.
- If no provider is configured, return a clear message in result.

---

### 6.6 Summary and Structured Notes

Create `summary_service.py`.

Input:

```text
transcript
kazakh translation if available
detected language
```

Output structure:

```json
{
  "title": "...",
  "short_summary": "...",
  "detailed_summary": "...",
  "key_points": [],
  "decisions": [],
  "action_items": [],
  "participants_or_speakers": [],
  "risks_or_open_questions": [],
  "final_notes": "..."
}
```

For MVP, use LLM API if configured.  
If not configured, produce a basic extractive fallback:

- first N sentences as summary,
- simple section placeholders.

Again:

- no fake API key,
- no secret in code,
- no dependency on one provider unless abstracted.

---

### 6.7 Document Export

Create `document_service.py`.

Generate four formats:

```text
TXT
DOCX
PDF
HTML
```

Required contents:

1. Project/system title
2. Processing date/time
3. Detected language
4. Original transcript
5. Kazakh translation
6. Short summary
7. Structured meeting notes
8. Key points
9. Decisions
10. Action items

Output directory:

```text
data/outputs/{task_id}/
```

Download endpoints:

```text
GET /api/download/{task_id}/txt
GET /api/download/{task_id}/docx
GET /api/download/{task_id}/pdf
GET /api/download/{task_id}/html
```

---

### 6.8 Task Status

Frontend needs to poll task status.

Endpoint:

```text
GET /api/tasks/{task_id}
```

Possible statuses:

```text
queued
processing
transcribing
translating
summarizing
generating_documents
completed
failed
```

Response example:

```json
{
  "task_id": "...",
  "status": "processing",
  "progress": 40,
  "message": "Transcribing audio",
  "result_available": false
}
```

When completed:

```json
{
  "task_id": "...",
  "status": "completed",
  "progress": 100,
  "downloads": {
    "txt": "/api/download/.../txt",
    "docx": "/api/download/.../docx",
    "pdf": "/api/download/.../pdf",
    "html": "/api/download/.../html"
  }
}
```

---

## 7. Data Retention and Cleanup

This is mandatory.

The server has limited free storage.  
Do not keep user audio forever.

Implement automatic cleanup.

Policy for MVP:

```text
Uploaded audio: delete after 6 hours
Processed temporary WAV: delete after 6 hours
Generated documents: delete after 24 hours
Task metadata: delete after 7 days or on restart if in-memory
```

Add config:

```text
UPLOAD_RETENTION_HOURS=6
OUTPUT_RETENTION_HOURS=24
MAX_UPLOAD_MB=300
```

Implement:

- cleanup on app startup;
- cleanup endpoint only if safe;
- optional background cleanup loop.

Never delete outside the project data directory.

Be careful with paths.  
Use safe path handling.

---

## 8. Public Website Plan

The target deployment should eventually be public.

Do not implement Cloudflare Tunnel directly in app code.

But create deployment notes:

```text
deploy/cloudflare-tunnel-notes.md
```

Explain that final deployment can expose local FastAPI/nginx using Cloudflare Tunnel:

```text
Internet user
→ Cloudflare HTTPS URL
→ Cloudflare Tunnel
→ Ubuntu PC
→ nginx
→ FastAPI app
```

The app itself should simply listen on localhost or 0.0.0.0 depending on deployment.

For first prototype:

```text
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

---

## 9. UI Requirements

Frontend must be simple but usable.

Pages/sections:

1. Header:
   - project name
   - short description

2. Upload section:
   - file input
   - upload button

3. Recording section:
   - start recording
   - stop recording
   - upload recording

4. Processing status:
   - status text
   - progress percentage
   - error message if failed

5. Results:
   - detected language
   - transcript preview
   - Kazakh translation preview
   - summary preview
   - download buttons for TXT/DOCX/PDF/HTML

6. Mobile responsive:
   - usable on phone
   - no horizontal overflow
   - large buttons

Do not waste time on premium UI.  
The first goal is working functionality.

---

## 10. Security and Safety Basics

Implement basic protections:

- limit upload size;
- allow only expected audio/video extensions;
- never execute uploaded file;
- use safe filenames;
- generate UUID task IDs;
- do not expose raw filesystem paths;
- do not store secrets in Git;
- reject missing or empty files;
- handle failed ffmpeg/ASR gracefully;
- return clear errors to frontend.

---

## 11. Git Workflow

Use Git carefully.

Before changes:

```bash
git status
```

After meaningful changes:

```bash
git add .
git commit -m "clear message"
git push
```

Do not commit:

```text
venv/
__pycache__/
.env
data/uploads/
data/outputs/
data/processed/
*.mp3
*.wav
*.m4a
*.webm
*.docx
*.pdf
```

Add these to `.gitignore`.

Every stage should leave the repo runnable.

---

## 12. Development Stages

### Stage 1 — Skeleton

Create working FastAPI backend and static frontend.

Acceptance:

```text
Backend starts.
Frontend opens.
Health endpoint works.
Git push done.
```

Endpoints:

```text
GET /
GET /api/health
```

---

### Stage 2 — Upload + Task

Implement upload and task status.

Acceptance:

```text
User uploads audio.
Backend saves it under task_id.
Task status can be queried.
Frontend shows task_id/status.
```

---

### Stage 3 — ffmpeg Conversion

Implement audio conversion.

Acceptance:

```text
Uploaded audio is converted to mono 16kHz WAV.
Errors are handled.
```

---

### Stage 4 — Whisper Transcription

Implement faster-whisper service.

Acceptance:

```text
Audio gets transcribed.
Transcript is saved.
Detected language is shown.
CPU mode works locally.
```

---

### Stage 5 — Translation + Summary

Implement abstract translation and summary services.

Acceptance:

```text
If API key is configured, translation/summary is generated.
If no API key, fallback still produces a result and app does not crash.
```

---

### Stage 6 — Document Export

Implement TXT, DOCX, PDF, HTML outputs.

Acceptance:

```text
All four files are generated and downloadable.
```

---

### Stage 7 — Cleanup

Implement retention cleanup.

Acceptance:

```text
Old uploads and outputs are deleted safely.
Configurable retention exists.
```

---

### Stage 8 — Deployment Docs

Write Ubuntu deployment instructions.

Acceptance:

```text
README explains:
- install dependencies,
- create venv,
- install Python packages,
- install ffmpeg,
- run app,
- configure systemd,
- optional nginx,
- optional Cloudflare Tunnel.
```

---

## 13. Do Not Do These Yet

Do not implement unless explicitly requested:

- login system;
- user dashboard;
- payment;
- permanent database;
- admin panel;
- multi-tenant support;
- live streaming transcription;
- speaker diarization;
- complex agent UI;
- Kubernetes;
- Docker-only deployment;
- advanced design system;
- mobile app.

Speaker diarization can be added later, but not now.

---

## 14. Agent Naming for Presentation

Internally, these are Python services.

But in UI/documentation we can describe them as agents:

```text
ASR Agent: converts speech to text
Language Agent: detects language and normalizes text
Translation Agent: converts content into Kazakh
Summary Agent: creates short and detailed summaries
Protocol Agent: structures meeting notes
Document Agent: exports TXT/DOCX/PDF/HTML
Cleanup Agent: deletes expired files
```

Do not create unnecessary autonomous agent frameworks.  
Simple deterministic service modules are enough.

---

## 15. Expected First Prototype Result

At the end of first prototype, the user should be able to:

1. Run backend locally.
2. Open website.
3. Upload an audio file.
4. Wait for processing.
5. See transcript/summary.
6. Download TXT/DOCX/PDF/HTML.
7. Push all code to GitHub.
8. Later clone and deploy on Ubuntu RTX machine.

---

## 16. Commands to Include in README

Local development example:

```bash
cd ~/Projects/conference-ai-notes

python3 -m venv .venv
source .venv/bin/activate

pip install -r backend/requirements.txt

sudo apt update
sudo apt install -y ffmpeg

uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

Then open:

```text
http://127.0.0.1:8000
```

Target Ubuntu checks:

```bash
nvidia-smi
python3 --version
ffmpeg -version
git --version
```

---

## 17. Important Behavior Rules

Before editing:

1. Inspect the existing repository structure.
2. Read existing README/TASK files if present.
3. Do not overwrite unrelated files.
4. Do not invent missing files without checking.
5. Make minimal but complete changes.
6. Keep code runnable after every stage.
7. Use full file rewrites only when necessary.
8. Explain what changed after each step.
9. Commit/push after stable milestones if Git is configured.
10. If something is missing, state exactly what is missing.

---

## 18. Immediate First Action

Start with repository inspection:

```bash
pwd
ls -la
find . -maxdepth 3 -type f | sort | sed 's#^\./##'
git status
```

Then report:

```text
1. Current project structure
2. Existing files
3. Missing files
4. Proposed first implementation step
```

After that, implement Stage 1 skeleton.

Do not jump directly into advanced features before the skeleton runs.

---

# Short Command for the Agent

After placing this file into the repository as `TASK.md`, give the agent this command:

```text
Read TASK.md completely. First inspect the repository structure and git status. Then implement Stage 1 only: working FastAPI backend, static frontend, health endpoint, correct .gitignore, and README run instructions. Do not implement Whisper yet. Keep the project runnable and push changes to GitHub if git remote is configured.
```

---

# Development Order

Do not ask the agent to build everything in one step. Use this order:

```text
Stage 1: skeleton
Stage 2: audio upload
Stage 3: ffmpeg conversion
Stage 4: Whisper transcription
Stage 5: translation/summary
Stage 6: documents
Stage 7: cleanup
Stage 8: Ubuntu deployment
```

---

# Final Principle

This is a fast MVP, not a full enterprise product.

Development happens on the user's laptop.  
GitHub is the source of truth.  
The Ubuntu RTX machine is the deployment and GPU test target.  
The first task is to create a stable runnable skeleton, not to overbuild the system.
