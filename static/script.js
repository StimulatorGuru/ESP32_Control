const form = document.getElementById("freq-form");
const responseElement = document.getElementById("response");
const freqInput = document.getElementById("freq");

// Gauge initialization
const gauge = new Gauge(document.getElementById("freq-gauge")).setOptions({
  angle: 0,
  lineWidth: 0.3,
  radiusScale: 1,
  pointer: {
    length: 0.6,
    strokeWidth: 0.035,
    color: "#00aaff"
  },
  limitMax: false,
  limitMin: false,
  colorStart: "#6f6",
  colorStop: "#0f0",
  strokeColor: "#eee",
  generateGradient: true
});

gauge.maxValue = 150;
gauge.setMinValue(0);
gauge.animationSpeed = 32;
gauge.set(0); // Initial value

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const freq = parseFloat(freqInput.value);

  try {
    const response = await fetch(`/set?freq=${freq}`);
    const text = await response.text();

    responseElement.textContent = text;
    responseElement.style.color = response.ok ? "lightgreen" : "red";

    if (response.ok) {
      gauge.set(freq);
    }
  } catch (error) {
    responseElement.textContent = "Error connecting to server.";
    responseElement.style.color = "red";
  }
});
