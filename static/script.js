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
