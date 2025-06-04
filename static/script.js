document.getElementById("freq-form").addEventListener("submit", async (e) => {
  e.preventDefault();

  const freq = document.getElementById("freq").value;
  const responseElement = document.getElementById("response");

  try {
    const response = await fetch(`/set?freq=${freq}`);
    const text = await response.text();

    responseElement.textContent = text;
    responseElement.style.color = response.ok ? "green" : "red";
  } catch (error) {
    responseElement.textContent = "Error connecting to server.";
    responseElement.style.color = "red";
  }
});

document.getElementById("toggle-btn").addEventListener("click", async () => {
  const button = document.getElementById("toggle-btn");
  const enable = button.textContent === "Enable";
  const responseElement = document.getElementById("response");

  try {
    const response = await fetch(`/toggle?enable=${enable}`);
    const text = await response.text();

    button.textContent = enable ? "Disable" : "Enable";
    responseElement.textContent = text;
    responseElement.style.color = response.ok ? "green" : "red";
  } catch (error) {
    responseElement.textContent = "Error connecting to server.";
    responseElement.style.color = "red";
  }
});
