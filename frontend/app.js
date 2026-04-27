const healthStatus = document.querySelector("#health-status");
const uploadForm = document.querySelector("#upload-form");
const audioFileInput = document.querySelector("#audio-file");
const uploadButton = document.querySelector("#upload-button");
const recordStartButton = document.querySelector("#record-start");
const recordStopButton = document.querySelector("#record-stop");
const recordUploadButton = document.querySelector("#record-upload");
const recordStatusEl = document.querySelector("#record-status");
const recordPreview = document.querySelector("#record-preview");
const taskIdEl = document.querySelector("#task-id");
const taskStatusEl = document.querySelector("#task-status");
const taskProgressEl = document.querySelector("#task-progress");
const taskMessageEl = document.querySelector("#task-message");
const taskErrorEl = document.querySelector("#task-error");
const detectedLanguageEl = document.querySelector("#detected-language");
const transcriptPreviewEl = document.querySelector("#transcript-preview");

let pollTimer = null;
let mediaRecorder = null;
let recordedChunks = [];
let recordedBlob = null;
let recordingStream = null;

async function loadHealth() {
  try {
    const response = await fetch("/api/health");
    if (!response.ok) {
      throw new Error(`Health check failed with ${response.status}`);
    }

    const data = await response.json();
    healthStatus.textContent = `${data.service}: ${data.status}`;
  } catch (error) {
    healthStatus.textContent = "Backend health check failed";
    healthStatus.classList.add("error");
    console.error(error);
  }
}

function setTaskView({
  taskId,
  status,
  progress,
  message,
  error,
  detectedLanguage,
  transcriptPreview,
}) {
  if (taskId !== undefined) {
    taskIdEl.textContent = taskId || "No task yet";
  }
  if (status !== undefined) {
    taskStatusEl.textContent = status || "Idle";
  }
  if (progress !== undefined) {
    taskProgressEl.textContent = `${progress || 0}%`;
  }
  if (message !== undefined) {
    taskMessageEl.textContent = message || "";
  }
  if (detectedLanguage !== undefined) {
    detectedLanguageEl.textContent = detectedLanguage || "Not available yet";
  }
  if (transcriptPreview !== undefined) {
    transcriptPreviewEl.textContent =
      transcriptPreview || "Transcript will appear after Whisper processing.";
  }

  if (error) {
    taskErrorEl.textContent = error;
    taskErrorEl.hidden = false;
  } else {
    taskErrorEl.textContent = "";
    taskErrorEl.hidden = true;
  }
}

async function loadTask(taskId) {
  const response = await fetch(`/api/tasks/${taskId}`);
  if (!response.ok) {
    throw new Error(`Task status failed with ${response.status}`);
  }

  const task = await response.json();
  setTaskView({
    taskId: task.task_id,
    status: task.status,
    progress: task.progress,
    message: task.message,
    error: task.error,
    detectedLanguage: task.detected_language,
    transcriptPreview: task.transcript_preview,
  });

  if (task.status === "completed" || task.status === "failed") {
    clearInterval(pollTimer);
    pollTimer = null;
  }
}

function startPolling(taskId) {
  if (pollTimer) {
    clearInterval(pollTimer);
  }

  loadTask(taskId).catch((error) => {
    setTaskView({ error: error.message });
  });

  pollTimer = setInterval(() => {
    loadTask(taskId).catch((error) => {
      clearInterval(pollTimer);
      pollTimer = null;
      setTaskView({ error: error.message });
    });
  }, 1500);
}

async function uploadFile(file, button, uploadMessage) {
  const formData = new FormData();
  formData.append("file", file);

  button.disabled = true;
  setTaskView({
    taskId: "",
    status: "Uploading",
    progress: 0,
    message: uploadMessage,
    error: "",
  });

  try {
    const response = await fetch("/api/upload", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || `Upload failed with ${response.status}`);
    }

    setTaskView({
      taskId: data.task_id,
      status: data.status,
      progress: 0,
      message: "Upload complete. Task created.",
      error: "",
    });
    startPolling(data.task_id);
  } catch (error) {
    setTaskView({
      status: "Failed",
      message: "Upload failed.",
      error: error.message,
    });
  } finally {
    button.disabled = false;
  }
}

async function uploadAudio(event) {
  event.preventDefault();

  const file = audioFileInput.files[0];
  if (!file) {
    setTaskView({ error: "Choose an audio file first." });
    return;
  }

  await uploadFile(file, uploadButton, "Uploading audio file...");
}

function setRecordingState(state, message) {
  recordStatusEl.textContent = message;

  if (state === "unsupported") {
    recordStartButton.disabled = true;
    recordStopButton.disabled = true;
    recordUploadButton.disabled = true;
    return;
  }

  recordStartButton.disabled = state === "recording" || state === "uploading";
  recordStopButton.disabled = state !== "recording";
  recordUploadButton.disabled = state !== "ready";
}

function getRecorderOptions() {
  const preferredTypes = [
    "audio/webm;codecs=opus",
    "audio/webm",
    "audio/ogg;codecs=opus",
  ];

  const mimeType = preferredTypes.find((type) => MediaRecorder.isTypeSupported(type));
  return mimeType ? { mimeType } : undefined;
}

async function startRecording() {
  if (!navigator.mediaDevices?.getUserMedia || typeof MediaRecorder === "undefined") {
    setRecordingState("unsupported", "Browser recording is not supported here.");
    return;
  }

  try {
    recordedChunks = [];
    recordedBlob = null;
    recordPreview.hidden = true;
    recordPreview.removeAttribute("src");

    recordingStream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(recordingStream, getRecorderOptions());

    mediaRecorder.addEventListener("dataavailable", (event) => {
      if (event.data.size > 0) {
        recordedChunks.push(event.data);
      }
    });

    mediaRecorder.addEventListener("stop", () => {
      const mimeType = mediaRecorder.mimeType || "audio/webm";
      recordedBlob = new Blob(recordedChunks, { type: mimeType });
      const previewUrl = URL.createObjectURL(recordedBlob);
      recordPreview.src = previewUrl;
      recordPreview.hidden = false;

      recordingStream.getTracks().forEach((track) => track.stop());
      recordingStream = null;
      mediaRecorder = null;

      setRecordingState("ready", "Recording ready for upload.");
    });

    mediaRecorder.start();
    setRecordingState("recording", "Recording...");
  } catch (error) {
    setRecordingState("idle", "Microphone access failed.");
    setTaskView({ error: error.message });
  }
}

function stopRecording() {
  if (mediaRecorder && mediaRecorder.state !== "inactive") {
    mediaRecorder.stop();
    setRecordingState("stopping", "Stopping recording...");
  }
}

async function uploadRecording() {
  if (!recordedBlob) {
    setTaskView({ error: "Record audio before uploading." });
    return;
  }

  const extension = recordedBlob.type.includes("ogg") ? "ogg" : "webm";
  const file = new File([recordedBlob], `browser-recording.${extension}`, {
    type: recordedBlob.type || "audio/webm",
  });

  setRecordingState("uploading", "Uploading recording...");
  await uploadFile(file, recordUploadButton, "Uploading browser recording...");
  setRecordingState("ready", "Recording uploaded. You can upload it again or record a new one.");
}

uploadForm.addEventListener("submit", uploadAudio);
recordStartButton.addEventListener("click", startRecording);
recordStopButton.addEventListener("click", stopRecording);
recordUploadButton.addEventListener("click", uploadRecording);

if (!navigator.mediaDevices?.getUserMedia || typeof MediaRecorder === "undefined") {
  setRecordingState("unsupported", "Browser recording is not supported here.");
}

loadHealth();
