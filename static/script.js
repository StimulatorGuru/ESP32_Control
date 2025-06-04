document.addEventListener("DOMContentLoaded", () => {
  const freqSlider = document.getElementById("freq");
  const freqValue = document.getElementById("freq-value");
  const toggleBtn = document.getElementById("toggle-btn");
  const responseElement = document.getElementById("response");
  const freqStatus = document.getElementById("freqStatus");
  const pulseWidthStatus = document.getElementById("pulseWidthStatus");
  const enableStatus = document.getElementById("enableStatus");

  // Update frequency display
  freqSlider.addEventListener("input", () => {
    freqValue.textContent = freqSlider.value;
  });

  // Send frequency to server
  freqSlider.addEventListener("change", async () => {
    const freq = freqSlider.value;
    try {
      const response = await fetch("/set", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ freq: parseFloat(freq) })
      });
      const data = await response.json();
      responseElement.textContent = data.message;
      responseElement.style.color = response.ok ? "green" : "red";
    } catch (error) {
      responseElement.textContent = "Error connecting to server.";
      responseElement.style.color = "red";
    }
  });

  // Toggle enable/disable
  toggleBtn.addEventListener("click", async () => {
    const enable = toggleBtn.textContent === "Enable";
    try {
      const response = await fetch("/toggle", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ enable })
      });
      const data = await response.json();
      toggleBtn.textContent = enable ? "Disable" : "Enable";
      responseElement.textContent = data.message;
      responseElement.style.color = response.ok ? "green" : "red";
    } catch (error) {
      responseElement.textContent = "Error connecting to server.";
      responseElement.style.color = "red";
    }
  });

  // Fetch status periodically
  async function fetchStatus() {
    try {
      const response = await fetch("/status");
      const data = await response.json();
      freqStatus.textContent = data.frequency.toFixed(2);
      pulseWidthStatus.textContent = data.totalPulseWidth.toFixed(0);
      enableStatus.textContent = data.enabled ? "Enabled" : "Disabled";
    } catch (error) {
      freqStatus.textContent = "--";
      pulseWidthStatus.textContent = "--";
      enableStatus.textContent = "Unavailable";
    }
  }

  fetchStatus();
  setInterval(fetchStatus, 5000);
});
