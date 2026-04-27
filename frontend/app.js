const healthStatus = document.querySelector("#health-status");
const uploadForm = document.querySelector("#upload-form");
const audioFileInput = document.querySelector("#audio-file");
const uploadButton = document.querySelector("#upload-button");
const taskIdEl = document.querySelector("#task-id");
const taskStatusEl = document.querySelector("#task-status");
const taskProgressEl = document.querySelector("#task-progress");
const taskMessageEl = document.querySelector("#task-message");
const taskErrorEl = document.querySelector("#task-error");

let pollTimer = null;

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

function setTaskView({ taskId, status, progress, message, error }) {
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

async function uploadAudio(event) {
  event.preventDefault();

  const file = audioFileInput.files[0];
  if (!file) {
    setTaskView({ error: "Choose an audio file first." });
    return;
  }

  const formData = new FormData();
  formData.append("file", file);

  uploadButton.disabled = true;
  setTaskView({
    taskId: "",
    status: "Uploading",
    progress: 0,
    message: "Uploading audio file...",
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
    uploadButton.disabled = false;
  }
}

uploadForm.addEventListener("submit", uploadAudio);
loadHealth();
