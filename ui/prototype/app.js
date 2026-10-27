(() => {
  const root = document;
  const code = root.getElementById("exam-code");
  const continueButton = root.getElementById("continue-button");
  const rerunButton = root.getElementById("rerun-button");
  const status = root.getElementById("overall-status");
  const checks = root.getElementById("checks");
  const dialog = root.getElementById("simple-dialog");
  const dialogTitle = root.getElementById("dialog-title");
  const dialogText = root.getElementById("dialog-text");

  function showDialog(title, text) {
    dialogTitle.textContent = title;
    dialogText.textContent = text;
    if (typeof dialog.showModal === "function") dialog.showModal();
  }

  continueButton.addEventListener("click", () => {
    const value = code.value.trim();
    if (!value) {
      code.focus();
      showDialog("Exam code required", "Enter an exam code before continuing.");
      return;
    }
    showDialog("Prototype only", "The launcher UI is working. Exam retrieval is not implemented yet.");
  });

  root.getElementById("file-button").addEventListener("click", () => {
    showDialog("Open .seb file", "File loading will be connected to the SafeExamOS configuration service in a later milestone.");
  });

  root.getElementById("url-button").addEventListener("click", () => {
    showDialog("Enter URL", "Direct URL entry will be available only when institution policy allows it.");
  });

  rerunButton.addEventListener("click", () => {
    status.textContent = "Checking…";
    status.dataset.state = "checking";

    const indicators = checks.querySelectorAll(".indicator");
    indicators.forEach((indicator) => {
      indicator.textContent = "•";
      indicator.className = "indicator pending";
    });

    window.setTimeout(() => {
      indicators.forEach((indicator) => {
        indicator.textContent = "✓";
        indicator.className = "indicator ok";
      });
      status.textContent = "System ready";
      status.dataset.state = "ready";
    }, 650);
  });
})();
