document.querySelectorAll("[data-copy]").forEach((button) => {
  button.addEventListener("click", () => {
    const target = document.querySelector(button.dataset.copy);
    if (!target) return;
    navigator.clipboard.writeText(target.textContent || "");
    button.textContent = "Copied!";
    setTimeout(() => (button.textContent = "Copy"), 1500);
  });
});

