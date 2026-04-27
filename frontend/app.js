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
const progressBar = document.querySelector("#progress-bar");
const detectedLanguageEl = document.querySelector("#detected-language");
const transcriptPreviewEl = document.querySelector("#transcript-preview");
const translationPreviewEl = document.querySelector("#translation-preview");
const summaryPreviewEl = document.querySelector("#summary-preview");
const downloadLinksEl = document.querySelector("#download-links");

let pollTimer = null;
let mediaRecorder = null;
let recordedChunks = [];
let recordedBlob = null;
let recordingStream = null;

const statusLabels = {
  queued: "В очереди",
  processing: "Обработка",
  converting_audio: "Конвертация аудио",
  transcribing: "Распознавание речи",
  translating: "Перевод",
  summarizing: "Резюме",
  generating_documents: "Подготовка документов",
  completed: "Готово",
  failed: "Ошибка",
  Uploading: "Загрузка",
  Failed: "Ошибка",
};

const statusMessages = {
  queued: "Файл принят. Задача ожидает обработки.",
  converting_audio: "Приводим аудио к формату mono 16 kHz WAV.",
  transcribing: "Whisper распознаёт речь.",
  translating: "Готовим казахскую версию текста.",
  summarizing: "Собираем краткое резюме и структуру.",
  generating_documents: "Формируем TXT, HTML, DOCX и PDF.",
  completed: "Готово. Документы можно скачать ниже.",
  failed: "Обработка остановилась с ошибкой.",
};

async function loadHealth() {
  try {
    const response = await fetch("/api/health");
    if (!response.ok) {
      throw new Error(`Проверка сервера вернула ${response.status}`);
    }

    const data = await response.json();
    healthStatus.textContent = data.status === "ok" ? "Сервер работает" : data.status;
  } catch (error) {
    healthStatus.textContent = "Сервер недоступен";
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
  translationPreview,
  summaryPreview,
  downloads,
}) {
  if (taskId !== undefined) {
    taskIdEl.textContent = taskId || "Пока нет";
  }
  if (status !== undefined) {
    taskStatusEl.textContent = statusLabels[status] || status || "Ожидание";
  }
  if (progress !== undefined) {
    const value = progress || 0;
    taskProgressEl.textContent = `${value}%`;
    progressBar.style.width = `${value}%`;
  }
  if (message !== undefined) {
    taskMessageEl.textContent = message || "";
  }
  if (detectedLanguage !== undefined) {
    detectedLanguageEl.textContent = detectedLanguage || "Пока нет";
  }
  if (transcriptPreview !== undefined) {
    transcriptPreviewEl.textContent =
      transcriptPreview || "Текст появится после обработки Whisper.";
  }
  if (translationPreview !== undefined) {
    translationPreviewEl.textContent =
      translationPreview || "Перевод появится после обработки.";
  }
  if (summaryPreview !== undefined) {
    summaryPreviewEl.textContent =
      summaryPreview || "Резюме появится после обработки.";
  }
  if (downloads !== undefined) {
    renderDownloads(downloads);
  }

  if (error) {
    taskErrorEl.textContent = error;
    taskErrorEl.hidden = false;
  } else {
    taskErrorEl.textContent = "";
    taskErrorEl.hidden = true;
  }
}

function renderDownloads(downloads) {
  downloadLinksEl.innerHTML = "";

  if (!downloads || Object.keys(downloads).length === 0) {
    const placeholder = document.createElement("span");
    placeholder.className = "muted";
    placeholder.textContent = "Документы появятся после завершения обработки.";
    downloadLinksEl.appendChild(placeholder);
    return;
  }

  const labels = {
    txt: "TXT",
    html: "HTML",
    docx: "DOCX",
    pdf: "PDF",
  };

  Object.entries(labels).forEach(([format, label]) => {
    if (!downloads[format]) {
      return;
    }

    const link = document.createElement("a");
    link.className = "download-link";
    link.href = downloads[format];
    link.textContent = label;
    link.target = "_blank";
    link.rel = "noopener";
    downloadLinksEl.appendChild(link);
  });
}

async function loadTask(taskId) {
  const response = await fetch(`/api/tasks/${taskId}`);
  if (!response.ok) {
    throw new Error(`Не удалось получить статус задачи: ${response.status}`);
  }

  const task = await response.json();
  setTaskView({
    taskId: task.task_id,
    status: task.status,
    progress: task.progress,
    message: statusMessages[task.status] || task.message,
    error: task.error,
    detectedLanguage: task.detected_language,
    transcriptPreview: task.transcript_preview,
    translationPreview: task.translation_preview,
    summaryPreview: task.summary_preview,
    downloads: task.downloads,
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
    downloads: null,
  });

  try {
    const response = await fetch("/api/upload", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || `Загрузка не прошла: ${response.status}`);
    }

    setTaskView({
      taskId: data.task_id,
      status: data.status,
      progress: 0,
      message: "Файл принят. Обработка началась.",
      error: "",
    });
    startPolling(data.task_id);
  } catch (error) {
    setTaskView({
      status: "Failed",
      message: "Загрузка не прошла.",
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
    setTaskView({ error: "Сначала выберите аудио или видеофайл." });
    return;
  }

  await uploadFile(file, uploadButton, "Загружаю файл на сервер...");
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
    setRecordingState("unsupported", "Браузер не поддерживает запись с микрофона.");
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

      setRecordingState("ready", "Запись готова к загрузке.");
    });

    mediaRecorder.start();
    setRecordingState("recording", "Идёт запись. Говорите в микрофон.");
  } catch (error) {
    setRecordingState("idle", "Не удалось получить доступ к микрофону.");
    setTaskView({ error: error.message });
  }
}

function stopRecording() {
  if (mediaRecorder && mediaRecorder.state !== "inactive") {
    mediaRecorder.stop();
    setRecordingState("stopping", "Останавливаю запись...");
  }
}

async function uploadRecording() {
  if (!recordedBlob) {
    setTaskView({ error: "Сначала запишите аудио." });
    return;
  }

  const extension = recordedBlob.type.includes("ogg") ? "ogg" : "webm";
  const file = new File([recordedBlob], `browser-recording.${extension}`, {
    type: recordedBlob.type || "audio/webm",
  });

  setRecordingState("uploading", "Загружаю запись...");
  await uploadFile(file, recordUploadButton, "Загружаю запись с микрофона...");
  setRecordingState("ready", "Запись загружена. Можно записать заново или отправить ещё раз.");
}

uploadForm.addEventListener("submit", uploadAudio);
recordStartButton.addEventListener("click", startRecording);
recordStopButton.addEventListener("click", stopRecording);
recordUploadButton.addEventListener("click", uploadRecording);

if (!navigator.mediaDevices?.getUserMedia || typeof MediaRecorder === "undefined") {
  setRecordingState("unsupported", "Браузер не поддерживает запись с микрофона.");
}

loadHealth();
