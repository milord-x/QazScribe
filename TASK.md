# QazScribe — Full Project Brief and Agent Task Plan

## 0. Project Name

**QazScribe**

Meaning:

- **Qaz** = Kazakhstan / Kazakh language context
- **Scribe** = a person/system that turns speech into written records

QazScribe is a web-based speech-to-document system for meetings, conferences, academic sessions, and university events.

---

## 1. What This Project Is

QazScribe is a public web application that processes speech/audio and converts it into a structured Kazakh-language document.

The system is intended for university-related use. It should help process long conferences, meetings, and spoken sessions where a lot of information is said in different languages.

The core pipeline is:

```text
Audio conference / speech file
→ speech recognition
→ raw transcript
→ translation to Kazakh
→ structured notes
→ short summary
→ final document export
```

The project is not a large enterprise product at this stage. It is a fast MVP prototype that must be good enough to demonstrate how the system works.

---

## 2. Why This Project Exists

The customer needs to show a working program soon. The original responsible person had a deadline approaching, so this MVP needs to be built quickly.

The system does not need to be perfect for long-term enterprise deployment yet. The immediate goal is to create a working public prototype that can:

1. Accept audio.
2. Recognize speech.
3. Convert speech to text.
4. Translate or produce the result in Kazakh.
5. Generate a structured document.
6. Export the result in multiple formats.
7. Run on the customer's Ubuntu PC with RTX GPU.
8. Be accessible through the internet, not only locally.

---

## 3. Important Development Context

The project already exists inside:

```text
~/Projects
```

The project is connected to GitHub.

Development workflow:

1. Main development is done on the developer's own laptop.
2. Work must be pushed to GitHub regularly.
3. The Ubuntu RTX machine is the target deployment machine, not the main development machine.
4. Do not assume the developer wants to code directly on the Ubuntu machine.
5. First build a working prototype locally.
6. Then clone/pull the repository on the Ubuntu machine.
7. Then configure GPU/Whisper/CUDA and public access.

Reason:

The developer does not want to work directly on the customer's Ubuntu PC. GitHub is the source of truth.

---

## 4. Target Deployment Machine

The target machine is a desktop PC with Ubuntu.

Known specs:

```text
OS: Ubuntu 24.04.1 LTS
Kernel: 6.11.0-26-generic
Desktop: GNOME 46
CPU: Intel Core i5-13400F
Cores: 10 physical class, 16 threads
GPU: NVIDIA GeForce RTX 4070 Ti
NVIDIA driver: 535.230.02
RAM: 16 GB
Storage: 1 TB NVMe total
Root partition: about 296 GB
Root used: about 266 GB
Free root space: limited, around 30 GB
Network: Ethernet + Wi-Fi
```

Important notes:

- The RTX 4070 Ti is strong enough for local Whisper/faster-whisper processing.
- RAM is 16 GB. This is not the same as disk storage.
- Root partition has limited free storage, so data cleanup is mandatory.
- The system must not store large files forever.
- GPU setup will be tested later on the Ubuntu machine.

Before GPU deployment, check:

```bash
nvidia-smi
python3 --version
ffmpeg -version
git --version
```

---

## 5. Public Server Requirement

A local-only website is not enough.

The site must be publicly accessible because conferences may happen in another part of the city. Users may need to open the website from outside the university network.

Required deployment idea:

```text
Public internet user
→ public HTTPS URL
→ tunnel / reverse proxy
→ Ubuntu PC
→ QazScribe backend
→ RTX Whisper processing
```

Preferred public access option for MVP:

```text
Cloudflare Tunnel
```

Reason:

- It does not require a public static IP.
- It does not require router port forwarding.
- It can expose a local service through a public HTTPS URL.
- It is suitable for a fast prototype.
- The Ubuntu PC remains the compute server.

Alternative options:

1. **ngrok** — fast for demos, but less ideal for stable delivery.
2. **VPS reverse proxy** — possible, but more work.
3. **Tailscale Funnel** — possible but not the first choice for a public website.
4. **Public IP + nginx** — good if the university network allows it, but likely slower to arrange.

Do not implement Cloudflare Tunnel inside the application code. Put deployment instructions in `deploy/cloudflare-tunnel-notes.md`.

---

## 6. Main Functional Requirements

QazScribe must support two main input modes.

### 6.1 Upload Existing Audio File

The user can upload a recorded conference or meeting audio file.

Supported initial formats:

```text
mp3, wav, m4a, ogg, webm, mp4
```

Backend must:

1. Validate file type.
2. Validate file size.
3. Save file temporarily.
4. Create a unique task ID.
5. Process the task.
6. Return task status and final downloads.

This is the most stable and highest-priority mode.

---

### 6.2 Record Audio in Browser

The user can record speech directly from the website.

Frontend should provide:

```text
Start recording
Stop recording
Upload recording
```

Implementation:

```text
Browser MediaRecorder API
→ creates audio blob, usually webm
→ upload blob to backend
→ process like normal audio file
```

Do not implement live real-time transcription in the first MVP.

MVP recording is:

```text
record first → upload → process → show result
```

---

## 7. Processing Pipeline

The complete planned pipeline:

```text
1. User uploads or records audio.
2. Backend stores audio temporarily.
3. Audio is converted with ffmpeg.
4. Whisper/faster-whisper transcribes speech.
5. System detects language if possible.
6. Transcript is cleaned/normalized.
7. Text is translated to Kazakh.
8. Summary is generated.
9. Structured meeting notes are generated.
10. Final documents are generated in TXT, DOCX, PDF, HTML.
11. User downloads the result.
12. Old data is automatically deleted.
```

---

## 8. Language Requirements

The customer is especially interested in:

```text
Kazakh
Russian
English
Turkic languages
```

They were interested in Whisper, so Whisper/faster-whisper should be the main ASR engine first.

Expected behavior:

- Auto-detect language when possible.
- Support Kazakh, Russian, English as primary practical targets.
- Be realistic about other Turkic languages: quality may vary depending on audio quality and model support.
- Mixed-language speech may be less accurate.

For MVP, use automatic language detection by default.

Optional UI selector later:

```text
Auto
Kazakh
Russian
English
Turkish
Uzbek
Kyrgyz
Other
```

---

## 9. Output Requirements

The system must generate four output formats:

```text
TXT
DOCX
PDF
HTML
```

Each output should include:

1. Project/system title.
2. Processing date and time.
3. Detected language.
4. Original transcript.
5. Kazakh translation.
6. Short summary.
7. Detailed summary or structured notes.
8. Key points.
9. Decisions.
10. Action items.
11. Open questions or risks if available.

Download endpoints should exist for each format.

---

## 10. No Authentication for MVP

The MVP does not need login, accounts, roles, or admin panels.

Do not add authentication unless explicitly requested later.

Reason:

- Deadline is short.
- It is mainly a demonstration prototype.
- Auth would slow down the first working version.

---

## 11. Data Storage and Cleanup Requirement

The customer does not need permanent storage.

Files should remain on the server only temporarily during and shortly after processing.

This is important because disk space is limited.

Correct storage model:

```text
temporary uploads
temporary processed files
temporary generated documents
automatic cleanup after expiration
```

Recommended retention policy for MVP:

```text
Uploaded original audio: delete after 6 hours
Converted audio: delete after 6 hours
Generated documents: delete after 24 hours
Task metadata: delete after 7 days or reset on restart if in-memory
```

Configurable settings:

```text
MAX_UPLOAD_MB=300
UPLOAD_RETENTION_HOURS=6
OUTPUT_RETENTION_HOURS=24
TASK_RETENTION_DAYS=7
```

Must be implemented safely:

- Never delete outside the project `data/` directory.
- Use safe path handling.
- Do not follow dangerous user-provided paths.
- Cleanup should run on app startup and optionally in a background loop.

---

## 12. Recommended Technical Stack

Use a simple MVP-oriented stack.

Preferred:

```text
Backend: Python + FastAPI
Frontend: plain HTML/CSS/JavaScript
ASR: faster-whisper
Audio conversion: ffmpeg
Document generation: python-docx, HTML template, PDF generator
Storage: local filesystem
Task status: in-memory or SQLite
Deployment: uvicorn + systemd + nginx + optional Cloudflare Tunnel
```

Avoid heavy frontend frameworks unless already present and necessary.

Reason:

- Plain HTML/CSS/JS is easier and faster for MVP.
- FastAPI is simple and suitable for file upload + processing.
- Python is best for Whisper and document generation.
- Deployment is easier without complex Node/React builds.

---

## 13. ASR / Whisper Plan

Use `faster-whisper` as the main ASR engine.

Design requirement:

- It must run in CPU mode on the developer laptop.
- It must support CUDA mode on the RTX 4070 Ti Ubuntu machine.
- Device and model must be configurable.
- Do not hard-code GPU.

Example development config:

```text
ASR_MODEL_SIZE=small
ASR_DEVICE=cpu
ASR_COMPUTE_TYPE=int8
```

Example target Ubuntu GPU config:

```text
ASR_MODEL_SIZE=medium
ASR_DEVICE=cuda
ASR_COMPUTE_TYPE=float16
```

Possible later upgrade:

```text
ASR_MODEL_SIZE=large-v3
```

But do not start with the heaviest model. First make the pipeline work.

ASR output should include:

```text
detected language
segments with timestamps
full transcript
```

---

## 14. Translation and Summary Plan

For the first MVP, use a replaceable service architecture.

Create separate modules:

```text
translation_service.py
summary_service.py
```

Do not hard-code one provider deeply into the code.

Translation target:

```text
Kazakh
```

Summary/structuring output:

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

Important:

- Do not invent API keys.
- Do not commit secrets.
- Use `.env.example`.
- If no API key is configured, the app must still run with fallback text.
- Fallback can produce simple placeholder summary instead of crashing.

Best MVP approach:

```text
Whisper local
Translation and structured notes through an external LLM API if configured
Fallback mode if not configured
```

Reason:

- Local Whisper uses RTX GPU.
- Translation and Kazakh summarization quality is better with a strong LLM API.
- Fully local LLM on 16 GB RAM may be limited and may produce weaker Kazakh output.

---

## 15. Agent Concept for Presentation

The customer mentioned adding multiple agents later. We can present the backend modules as agents without building a complicated autonomous agent framework.

Use these names in documentation/UI if useful:

```text
ASR Agent: converts speech to text
Language Agent: detects language and normalizes transcript
Translation Agent: translates content into Kazakh
Summary Agent: creates short and detailed summaries
Protocol Agent: structures meeting notes
Document Agent: exports TXT/DOCX/PDF/HTML
Cleanup Agent: deletes expired files
```

Important:

Do not create unnecessary LangChain/autonomous-agent complexity in MVP. Simple Python service modules are enough.

---

## 16. Required Project Structure

If the existing repository does not already have a good structure, use this:

```text
QazScribe/
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
│   ├── qazscribe.service
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

Do not commit generated data files.

---

## 17. Backend API Plan

### Health

```text
GET /api/health
```

Returns:

```json
{
  "status": "ok",
  "service": "QazScribe"
}
```

---

### Upload

```text
POST /api/upload
```

Input:

- audio/video file

Returns:

```json
{
  "task_id": "...",
  "status": "queued"
}
```

---

### Task Status

```text
GET /api/tasks/{task_id}
```

Possible statuses:

```text
queued
processing
converting_audio
transcribing
translating
summarizing
generating_documents
completed
failed
```

Example response:

```json
{
  "task_id": "...",
  "status": "transcribing",
  "progress": 35,
  "message": "Transcribing audio",
  "result_available": false
}
```

Completed response:

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

### Downloads

```text
GET /api/download/{task_id}/txt
GET /api/download/{task_id}/docx
GET /api/download/{task_id}/pdf
GET /api/download/{task_id}/html
```

---

## 18. Frontend Requirements

The first UI does not need to be beautiful. It must be usable and responsive.

Required sections:

1. Header with project name: QazScribe.
2. Short explanation of what it does.
3. File upload block.
4. Browser recording block.
5. Processing status block.
6. Result preview block.
7. Download buttons for TXT, DOCX, PDF, HTML.
8. Error display.
9. Mobile-responsive layout.

Important:

- Large buttons.
- Clear status messages.
- No horizontal overflow on phone.
- Works on desktop and mobile browser.

---

## 19. Security and Reliability Basics

Implement basic protections:

1. Limit upload size.
2. Allow only expected file extensions.
3. Generate UUID task IDs.
4. Never execute uploaded files.
5. Use safe filenames.
6. Do not expose filesystem paths.
7. Do not store secrets in Git.
8. Reject empty files.
9. Handle ffmpeg errors clearly.
10. Handle Whisper errors clearly.
11. Handle missing API key gracefully.
12. Clean up expired files.

---

## 20. Git Workflow

Use Git consistently.

Before work:

```bash
git status
```

After stable changes:

```bash
git add .
git commit -m "clear message"
git push
```

Do not commit:

```text
.venv/
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
*.mp4
*.docx
*.pdf
```

Add these to `.gitignore`.

Every milestone should leave the repo runnable.

---

## 21. Development Roadmap

This is the correct order. Do not jump ahead.

### Stage 1 — Project Skeleton

Goal:

Create a runnable backend and frontend skeleton.

Tasks:

1. Inspect current repository.
2. Create/adjust structure.
3. Add FastAPI backend.
4. Add static frontend.
5. Add health endpoint.
6. Add README run instructions.
7. Add correct `.gitignore`.

Acceptance:

```text
Backend starts.
Frontend opens.
GET /api/health works.
No Whisper yet.
Repo is pushed to GitHub.
```

---

### Stage 2 — File Upload and Task Creation

Goal:

Implement audio file upload before Whisper.

Tasks:

1. Add upload form.
2. Add `/api/upload` endpoint.
3. Validate file type and size.
4. Save uploaded file under task ID.
5. Add task status endpoint.
6. Show status in frontend.

Acceptance:

```text
User uploads audio.
Backend stores it safely.
Task ID is created.
Frontend shows task status.
```

---

### Stage 3 — Browser Recording

Goal:

Allow recording from microphone.

Tasks:

1. Implement MediaRecorder in frontend.
2. Add start/stop recording buttons.
3. Upload recorded blob to backend.
4. Reuse same upload processing path.

Acceptance:

```text
User records audio in browser.
Recording is uploaded.
Task is created.
```

---

### Stage 4 — Audio Conversion

Goal:

Normalize audio before ASR.

Tasks:

1. Use ffmpeg.
2. Convert to mono 16 kHz WAV.
3. Store processed audio temporarily.
4. Handle ffmpeg errors.

Acceptance:

```text
Uploaded/recorded audio converts successfully.
Errors are shown clearly if conversion fails.
```

---

### Stage 5 — Whisper Transcription

Goal:

Transcribe audio using faster-whisper.

Tasks:

1. Add ASR service.
2. CPU config for local development.
3. CUDA config option for target server.
4. Save transcript.
5. Return detected language and transcript preview.

Acceptance:

```text
Audio becomes text.
Detected language is saved.
Frontend shows transcript preview.
```

---

### Stage 6 — Translation and Structuring

Goal:

Translate and summarize text.

Tasks:

1. Add translation service.
2. Add summary service.
3. Use external API only if configured.
4. Provide fallback if no API key.
5. Produce structured JSON-like result.

Acceptance:

```text
Kazakh translation is generated or fallback is shown.
Summary and structured notes are generated.
App does not crash without API key.
```

---

### Stage 7 — Document Export

Goal:

Generate four output formats.

Tasks:

1. Generate TXT.
2. Generate DOCX.
3. Generate PDF.
4. Generate HTML.
5. Add download endpoints.
6. Add frontend download buttons.

Acceptance:

```text
User can download TXT, DOCX, PDF, HTML.
Each document contains transcript, translation, summary, and structured notes.
```

---

### Stage 8 — Cleanup System

Goal:

Prevent disk from filling.

Tasks:

1. Add retention config.
2. Delete expired uploads.
3. Delete expired processed files.
4. Delete expired outputs.
5. Run cleanup on startup.
6. Optional background cleanup loop.

Acceptance:

```text
Old files are deleted safely.
Cleanup never deletes outside data directory.
```

---

### Stage 9 — Ubuntu Deployment

Goal:

Prepare target server deployment.

Tasks:

1. Write `deploy/install_ubuntu.sh`.
2. Write systemd service.
3. Write nginx config.
4. Write Cloudflare Tunnel notes.
5. Document GPU/CUDA config.
6. Test on Ubuntu RTX machine after prototype works.

Acceptance:

```text
Project can be cloned from GitHub and run on Ubuntu.
Service can start automatically.
Public tunnel can expose the site.
```

---

## 22. What Not To Do Yet

Do not implement these unless explicitly requested:

```text
login system
admin panel
roles and permissions
payment system
permanent user database
complex React/Next.js frontend
mobile app
live transcription streaming
speaker diarization
advanced analytics
Kubernetes
Docker-only deployment
large autonomous agent framework
```

These may be future improvements, but not first MVP requirements.

---

## 23. README Must Include

Local development commands:

```bash
cd ~/Projects/QazScribe
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
sudo apt update
sudo apt install -y ffmpeg
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

Open:

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

Target Ubuntu GPU config example:

```text
ASR_DEVICE=cuda
ASR_COMPUTE_TYPE=float16
ASR_MODEL_SIZE=medium
```

---

## 24. Immediate Instruction to Agent

Start by inspecting the repository.

Run:

```bash
pwd
ls -la
find . -maxdepth 3 -type f | sort | sed 's#^./##'
git status
```

Then report:

```text
1. Current project structure
2. Existing files
3. Missing files
4. Proposed first implementation step
```

After inspection, implement **Stage 1 only**.

Do not implement Whisper yet.
Do not implement translation yet.
Do not implement document export yet.

Stage 1 must create a clean runnable skeleton first.

---

## 25. Short Command After This File

After this `TASK.md` is added to the repository, the developer can tell the agent:

```text
Read TASK.md completely. First inspect the repository structure and git status. Then implement Stage 1 only: working FastAPI backend, static frontend, health endpoint, correct .gitignore, and README run instructions. Do not implement Whisper yet. Keep the project runnable and push changes to GitHub if git remote is configured.
```

---

## 26. Final Summary

QazScribe is a fast MVP public web system for converting conference speech/audio into structured Kazakh-language documents.

The first prototype must focus on the correct foundation:

```text
simple web UI
FastAPI backend
file upload
browser recording
Whisper transcription
Kazakh translation
structured summary
TXT/DOCX/PDF/HTML export
automatic cleanup
Ubuntu RTX deployment
public access through Cloudflare Tunnel or similar
```

The project must stay simple, runnable, and GitHub-based. The Ubuntu RTX machine is the deployment target, not the main development environment.
