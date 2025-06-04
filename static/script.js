const freqSlider = document.getElementById("freq-slider");
const freqValue = document.getElementById("freq-value");
const setFreqBtn = document.getElementById("set-freq-btn");
const toggleBtn = document.getElementById("toggle-btn");
const responseElement = document.getElementById("response");

// Status display
const pulseStatusDisplay = document.getElementById("pulse-status");
const currentFreqDisplay = document.getElementById("current-freq");
const pulseWidthDisplay = document.getElementById("pulse-width");

// Update displayed frequency when slider moves
freqSlider.addEventListener("input", () => {
  freqValue.textContent = freqSlider.value;
});

// Set frequency
setFreqBtn.addEventListener("click", async () => {
  const freq = freqSlider.value;
  try {
    const response = await fetch(`/set?freq=${freq}`);
    const text = await response.text();
    responseElement.textContent = text;
    responseElement.style.color = response.ok ? "green" : "red";
    updateStatus();
  } catch {
    responseElement.textContent = "Error setting frequency.";
    responseElement.style.color = "red";
  }
});

// Toggle pulses
toggleBtn.addEventListener("click", async () => {
  const enable = toggleBtn.textContent === "Enable";
  try {
    const response = await fetch(`/toggle?enable=${enable}`);
    const text = await response.text();
    toggleBtn.textContent = enable ? "Disable" : "Enable";
    responseElement.textContent = text;
    responseElement.style.color = response.ok ? "green" : "red";
    updateStatus();
  } catch {
    responseElement.textContent = "Error toggling pulses.";
    responseElement.style.color = "red";
  }
});

// Fetch status (pulse enabled, frequency, width)
async function updateStatus() {
  try {
    const res = await fetch("/status");
    const data = await res.json();
    pulseStatusDisplay.textContent = data.enabled ? "Enabled" : "Disabled";
    currentFreqDisplay.textContent = data.frequency;
    pulseWidthDisplay.textContent = data.totalPulseWidth;
  } catch {
    pulseStatusDisplay.textContent = "Unavailable";
    currentFreqDisplay.textContent = "--";
    pulseWidthDisplay.textContent = "--";
  }
}

updateStatus();
setInterval(updateStatus, 5000); // Refresh every 5s
