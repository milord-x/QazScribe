const healthStatus = document.querySelector("#health-status");

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

loadHealth();
