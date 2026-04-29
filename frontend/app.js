const healthStatus = document.querySelector("#health-status");
const navButtons = document.querySelectorAll("[data-screen-target]");
const screens = document.querySelectorAll(".screen");
const modeButtons = document.querySelectorAll("[data-mode-target]");
const modePanels = document.querySelectorAll(".input-panel");
const uploadForm = document.querySelector("#upload-form");
const audioFileInput = document.querySelector("#audio-file");
const uploadButton = document.querySelector("#upload-button");
const recordStartButton = document.querySelector("#record-start");
const recordStopButton = document.querySelector("#record-stop");
const recordUploadButton = document.querySelector("#record-upload");
const recordStatusEl = document.querySelector("#record-status");
const recordPreview = document.querySelector("#record-preview");
const micSelect = document.querySelector("#mic-select");
const settingsMicSelect = document.querySelector("#settings-mic-select");
const refreshMicsButton = document.querySelector("#refresh-mics");
const requestMicAccessButton = document.querySelector("#request-mic-access");
const micHelpEl = document.querySelector("#mic-help");
const liveTranscriptEl = document.querySelector("#live-transcript");
const speechStatusEl = document.querySelector("#speech-status");
const taskIdEl = document.querySelector("#task-id");
const taskStatusEl = document.querySelector("#task-status");
const taskProgressEl = document.querySelector("#task-progress");
const taskDurationEl = document.querySelector("#task-duration");
const taskSpeakersEl = document.querySelector("#task-speakers");
const taskMessageEl = document.querySelector("#task-message");
const taskErrorEl = document.querySelector("#task-error");
const progressBar = document.querySelector("#progress-bar");
const detectedLanguageEl = document.querySelector("#detected-language");
const transcriptPreviewEl = document.querySelector("#transcript-preview");
const speakerPreviewEl = document.querySelector("#speaker-preview");
const translationPreviewEl = document.querySelector("#translation-preview");
const detailedSummaryPreviewEl = document.querySelector("#detailed-summary-preview");
const summaryPreviewEl = document.querySelector("#summary-preview");
const downloadLinksEl = document.querySelector("#download-links");

let pollTimer = null;
let mediaRecorder = null;
let recordedChunks = [];
let recordedBlob = null;
let recordingStream = null;
let speechRecognition = null;
let speechFinalText = "";

const MIC_STORAGE_KEY = "qazscribe.selectedMicrophoneId";

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
  generating_documents: "Формируем документы.",
  completed: "Готово. Документы можно скачать ниже.",
  failed: "Обработка остановилась с ошибкой.",
};

function showScreen(screenName) {
  screens.forEach((screen) => {
    screen.classList.toggle("active", screen.id === `screen-${screenName}`);
  });
  document.querySelectorAll(".nav-tab").forEach((button) => {
    button.classList.toggle("active", button.dataset.screenTarget === screenName);
  });
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function showMode(panelId) {
  modePanels.forEach((panel) => {
    panel.classList.toggle("active", panel.id === panelId);
  });
  modeButtons.forEach((button) => {
    button.classList.toggle("active", button.dataset.modeTarget === panelId);
  });
}

function setTextValue(element, value, fallback) {
  if (!element) {
    return;
  }
  element.value = value || fallback;
}

function formatDuration(seconds) {
  if (!seconds) {
    return "Пока нет";
  }
  const total = Math.round(seconds);
  const minutes = Math.floor(total / 60);
  const rest = total % 60;
  return `${minutes}:${String(rest).padStart(2, "0")}`;
}

async function readResponsePayload(response) {
  const contentType = response.headers.get("content-type") || "";
  if (contentType.includes("application/json")) {
    return response.json();
  }

  const text = await response.text();
  return {
    detail: text || `Сервер вернул ${response.status}`,
  };
}

async function loadHealth() {
  try {
    const response = await fetch("/api/health");
    if (!response.ok) {
      throw new Error(`Проверка сервера вернула ${response.status}`);
    }

    const data = await readResponsePayload(response);
    healthStatus.textContent = data.status === "ok" ? "Сервер работает" : data.status;
    healthStatus.classList.remove("error");
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
  detailedSummaryPreview,
  speakerPreview,
  recordingDurationSeconds,
  speakerCount,
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
  if (recordingDurationSeconds !== undefined) {
    taskDurationEl.textContent = formatDuration(recordingDurationSeconds);
  }
  if (speakerCount !== undefined) {
    taskSpeakersEl.textContent = speakerCount ? `${speakerCount}` : "Пока нет";
  }
  if (message !== undefined) {
    taskMessageEl.textContent = message || "";
  }
  if (detectedLanguage !== undefined) {
    detectedLanguageEl.textContent = detectedLanguage || "Пока нет";
  }
  if (transcriptPreview !== undefined) {
    setTextValue(
      transcriptPreviewEl,
      transcriptPreview,
      "Текст появится после обработки Whisper.",
    );
  }
  if (translationPreview !== undefined) {
    setTextValue(translationPreviewEl, translationPreview, "Перевод появится после обработки.");
  }
  if (speakerPreview !== undefined) {
    setTextValue(speakerPreviewEl, speakerPreview, "Спикеры появятся после обработки.");
  }
  if (detailedSummaryPreview !== undefined) {
    setTextValue(
      detailedSummaryPreviewEl,
      detailedSummaryPreview,
      "Конспект появится после обработки.",
    );
  }
  if (summaryPreview !== undefined) {
    setTextValue(summaryPreviewEl, summaryPreview, "Краткое резюме появится после обработки.");
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
    srt: "SRT",
    vtt: "VTT",
    json: "JSON",
    pdf: "PDF",
    docx: "DOCX",
    html: "HTML",
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

  const task = await readResponsePayload(response);
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
    detailedSummaryPreview: task.detailed_summary_preview,
    speakerPreview: task.speaker_preview,
    recordingDurationSeconds: task.recording_duration_seconds,
    speakerCount: task.speaker_count,
    downloads: task.downloads,
  });

  if (task.status === "completed" || task.status === "failed") {
    clearInterval(pollTimer);
    pollTimer = null;
    showScreen("results");
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
  showScreen("capture");
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

    const data = await readResponsePayload(response);
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
    showScreen("capture");
    showMode("file-panel");
    return;
  }

  await uploadFile(file, uploadButton, "Загружаю файл на сервер...");
}

function selectedMicId() {
  return micSelect.value || settingsMicSelect.value || "";
}

function saveSelectedMic(deviceId) {
  if (deviceId) {
    localStorage.setItem(MIC_STORAGE_KEY, deviceId);
  } else {
    localStorage.removeItem(MIC_STORAGE_KEY);
  }
}

function syncMicSelects(deviceId) {
  [micSelect, settingsMicSelect].forEach((select) => {
    if (select.value !== deviceId) {
      select.value = deviceId;
    }
  });
}

function renderMicOptions(devices) {
  const rememberedId = localStorage.getItem(MIC_STORAGE_KEY) || "";
  const audioInputs = devices.filter((device) => device.kind === "audioinput");
  const options = audioInputs.length
    ? audioInputs
    : [{ deviceId: "", label: "Микрофон по умолчанию" }];

  [micSelect, settingsMicSelect].forEach((select) => {
    select.innerHTML = "";
    options.forEach((device, index) => {
      const option = document.createElement("option");
      option.value = device.deviceId;
      option.textContent = device.label || `Микрофон ${index + 1}`;
      select.appendChild(option);
    });
  });

  const selected = options.some((device) => device.deviceId === rememberedId)
    ? rememberedId
    : options[0].deviceId;
  syncMicSelects(selected);
  saveSelectedMic(selected);
}

async function loadMicrophones() {
  if (!navigator.mediaDevices?.enumerateDevices) {
    micHelpEl.textContent = "Этот браузер не показывает список микрофонов.";
    return;
  }

  try {
    const devices = await navigator.mediaDevices.enumerateDevices();
    renderMicOptions(devices);
    micHelpEl.textContent = "Выбранный микрофон сохранится в этом браузере.";
  } catch (error) {
    micHelpEl.textContent = `Не удалось получить список микрофонов: ${error.message}`;
  }
}

async function requestMicrophoneAccess() {
  if (!navigator.mediaDevices?.getUserMedia) {
    micHelpEl.textContent = "Браузер не поддерживает доступ к микрофону.";
    return;
  }

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    stream.getTracks().forEach((track) => track.stop());
    await loadMicrophones();
  } catch (error) {
    micHelpEl.textContent = `Доступ к микрофону не получен: ${error.message}`;
  }
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

function normalizeSpeechText(text) {
  return text
    .replace(/\bточка\b/gi, ".")
    .replace(/\bзапятая\b/gi, ",")
    .replace(/\bновый абзац\b/gi, "\n\n")
    .replace(/\s+([.,!?])/g, "$1")
    .replace(/[ \t]+\n/g, "\n")
    .trim();
}

function createSpeechRecognition() {
  const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!Recognition) {
    speechStatusEl.textContent = "не поддерживается";
    return null;
  }

  const recognition = new Recognition();
  recognition.continuous = true;
  recognition.interimResults = true;
  recognition.lang = "ru-RU";
  recognition.addEventListener("result", (event) => {
    let interimText = "";
    for (let index = event.resultIndex; index < event.results.length; index += 1) {
      const text = event.results[index][0].transcript;
      if (event.results[index].isFinal) {
        speechFinalText = `${speechFinalText} ${text}`;
      } else {
        interimText = `${interimText} ${text}`;
      }
    }
    liveTranscriptEl.textContent = normalizeSpeechText(`${speechFinalText} ${interimText}`);
  });
  recognition.addEventListener("start", () => {
    speechStatusEl.textContent = "слушает";
  });
  recognition.addEventListener("end", () => {
    speechStatusEl.textContent = "остановлено";
  });
  recognition.addEventListener("error", () => {
    speechStatusEl.textContent = "черновик недоступен";
  });
  return recognition;
}

async function startRecording() {
  if (!navigator.mediaDevices?.getUserMedia || typeof MediaRecorder === "undefined") {
    setRecordingState("unsupported", "Браузер не поддерживает запись с микрофона.");
    return;
  }

  try {
    recordedChunks = [];
    recordedBlob = null;
    speechFinalText = "";
    liveTranscriptEl.textContent = "Говорите. Если браузер поддерживает распознавание, текст появится здесь.";
    recordPreview.hidden = true;
    recordPreview.removeAttribute("src");

    const deviceId = selectedMicId();
    const audio = deviceId ? { deviceId: { exact: deviceId } } : true;
    recordingStream = await navigator.mediaDevices.getUserMedia({ audio });
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

      if (speechRecognition) {
        try {
          speechRecognition.stop();
        } catch (error) {
          console.debug("Speech recognition was already stopped.", error);
        }
      }

      setRecordingState("ready", "Запись готова к загрузке.");
    });

    mediaRecorder.start();
    speechRecognition = createSpeechRecognition();
    if (speechRecognition) {
      speechRecognition.start();
    }
    setRecordingState("recording", "Идёт запись. Говорите в выбранный микрофон.");
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

navButtons.forEach((button) => {
  button.addEventListener("click", () => showScreen(button.dataset.screenTarget));
});

modeButtons.forEach((button) => {
  button.addEventListener("click", () => showMode(button.dataset.modeTarget));
});

uploadForm.addEventListener("submit", uploadAudio);
recordStartButton.addEventListener("click", startRecording);
recordStopButton.addEventListener("click", stopRecording);
recordUploadButton.addEventListener("click", uploadRecording);
refreshMicsButton.addEventListener("click", loadMicrophones);
requestMicAccessButton.addEventListener("click", requestMicrophoneAccess);

[micSelect, settingsMicSelect].forEach((select) => {
  select.addEventListener("change", () => {
    saveSelectedMic(select.value);
    syncMicSelects(select.value);
  });
});

if (!navigator.mediaDevices?.getUserMedia || typeof MediaRecorder === "undefined") {
  setRecordingState("unsupported", "Браузер не поддерживает запись с микрофона.");
}

loadHealth();
loadMicrophones();
