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

  // Send frequency to Flask server
  freqSlider.addEventListener("change", async () => {
    const freq = freqSlider.value;
    try {
      const res = await fetch("/set", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({freq: parseFloat(freq)})
      });
      const data = await res.json();
      responseElement.textContent = data.message;
      responseElement.style.color = res.ok ? "green" : "red";
    } catch {
      responseElement.textContent = "Error connecting to server.";
      responseElement.style.color = "red";
    }
  });

  // Toggle enable/disable pulses
  toggleBtn.addEventListener("click", async () => {
    const enable = toggleBtn.textContent === "Enable";
    try {
      const res = await fetch("/toggle", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({enable})
      });
      const data = await res.json();
      toggleBtn.textContent = enable ? "Disable" : "Enable";
      responseElement.textContent = data.message;
      responseElement.style.color = res.ok ? "green" : "red";
    } catch {
      responseElement.textContent = "Error connecting to server.";
      responseElement.style.color = "red";
    }
  });

  // Fetch stimulator status
  async function fetchStatus() {
    try {
      const res = await fetch("/status");
      const data = await res.json();
      freqStatus.textContent = data.frequency.toFixed(2);
      pulseWidthStatus.textContent = data.totalPulseWidth.toFixed(0);
      enableStatus.textContent = data.enabled ? "Enabled" : "Disabled";
    } catch {
      freqStatus.textContent = "--";
      pulseWidthStatus.textContent = "--";
      enableStatus.textContent = "Unavailable";
    }
  }

  fetchStatus();
  setInterval(fetchStatus, 5000);

  // --- Sinewave Visualization via Chart.js ---
  const sineCanvas = document.getElementById("sineChart");
  if (sineCanvas) {
    const ctx = sineCanvas.getContext("2d");
    const sineChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: Array.from({length: 50}, (_, i) => i),  // X-axis labels
        datasets: [{
          label: 'Sinewave (MATLAB)',
          data: new Array(50).fill(0),  // Initial zero values
          borderColor: 'blue',
          borderWidth: 2,
          tension: 0.3
        }]
      },
      options: {
        responsive: true,
        animation: false,
        scales: {
          y: {
            min: -1.2,
            max: 1.2,
            title: {
              display: true,
              text: "Amplitude"
            }
          },
          x: {
            display: false
          }
        }
      }
    });

    // Fetch sinewave data from Flask
    async function updateSinewave() {
      try {
        const res = await fetch("/sinewave");
        const data = await res.json();
        const sine = data.sine;
        if (Array.isArray(sine)) {
          sineChart.data.datasets[0].data = sine.map(v => parseFloat(v));
          sineChart.update();
        }
      } catch (err) {
        console.error("❌ Failed to fetch sinewave:", err);
      }
    }

    updateSinewave();
    setInterval(updateSinewave, 1000); // Update every second
  }
});
