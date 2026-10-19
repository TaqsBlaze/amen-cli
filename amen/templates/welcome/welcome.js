/* Progressive enhancement for the generated welcome page. No runtime dependencies. */
(() => {
  "use strict";

  const root = document.documentElement;
  const themeKey = "amen:theme";
  const systemTheme = window.matchMedia("(prefers-color-scheme: dark)");
  const readTheme = () => {
    try {
      const value = localStorage.getItem(themeKey);
      return value === "light" || value === "dark" ? value : null;
    } catch (_) {
      return null;
    }
  };
  root.dataset.theme = readTheme() || (systemTheme.matches ? "dark" : "light");

  document.addEventListener("DOMContentLoaded", () => {
    const themeButton = document.getElementById("theme-toggle");
    const updateThemeButton = () => {
      const dark = root.dataset.theme === "dark";
      themeButton.setAttribute("aria-pressed", String(dark));
      themeButton.setAttribute("aria-label", `Switch to ${dark ? "light" : "dark"} theme`);
    };
    if (themeButton) {
      themeButton.disabled = false;
      updateThemeButton();
      themeButton.addEventListener("click", () => {
        root.dataset.theme = root.dataset.theme === "dark" ? "light" : "dark";
        try { localStorage.setItem(themeKey, root.dataset.theme); } catch (_) { /* Storage may be disabled. */ }
        updateThemeButton();
      });
      systemTheme.addEventListener("change", (event) => {
        if (!readTheme()) {
          root.dataset.theme = event.matches ? "dark" : "light";
          updateThemeButton();
        }
      });
    }

    const commandSearch = document.getElementById("command-search");
    if (commandSearch) {
      const cards = Array.from(document.querySelectorAll("[data-command-name]"));
      const searchText = cards.map((card) => card.textContent.toLocaleLowerCase());
      const commandResults = document.getElementById("command-results");
      const commandEmpty = document.getElementById("command-empty");
      commandSearch.closest(".command-search").hidden = false;
      const filterCommands = () => {
        const query = commandSearch.value.trim().toLocaleLowerCase();
        let visible = 0;
        cards.forEach((card, index) => {
          card.hidden = !searchText[index].includes(query);
          if (!card.hidden) visible += 1;
        });
        commandResults.textContent = `${visible} command ${visible === 1 ? "example" : "examples"}${query ? ` matching “${commandSearch.value.trim()}”` : ""}`;
        commandEmpty.hidden = visible > 0;
        document.getElementById("command-list").hidden = visible === 0;
      };
      commandSearch.addEventListener("input", filterCommands);
      filterCommands();
    }

    const toast = document.getElementById("toast");
    let toastTimer;
    const announce = (message) => {
      if (!toast) return;
      clearTimeout(toastTimer);
      toast.textContent = message;
      toast.hidden = false;
      toastTimer = setTimeout(() => { toast.hidden = true; }, 3500);
    };
    document.querySelectorAll("[data-copy]").forEach((button) => {
      const target = document.getElementById(button.dataset.copy);
      if (!target) return;
      button.disabled = false;
      const originalLabel = button.getAttribute("aria-label");
      let resetTimer;
      button.addEventListener("click", async () => {
        const text = target.textContent.trim();
        button.disabled = true;
        let copied = false;
        try {
          if (navigator.clipboard && navigator.clipboard.writeText) {
            await navigator.clipboard.writeText(text);
            copied = true;
          }
        } catch (_) { /* Fall back to selecting the visible command. */ }
        if (!copied) {
          const selection = window.getSelection();
          const range = document.createRange();
          range.selectNodeContents(target);
          selection.removeAllRanges();
          selection.addRange(range);
          try { copied = document.execCommand("copy"); } catch (_) { /* Manual copy remains available. */ }
        }
        button.disabled = false;
        if (copied) {
          clearTimeout(resetTimer);
          button.dataset.copied = "true";
          button.setAttribute("aria-label", "Command copied");
          button.querySelector("[data-copy-label]").textContent = "Copied";
          announce("Command copied to clipboard.");
          resetTimer = setTimeout(() => {
            delete button.dataset.copied;
            button.setAttribute("aria-label", originalLabel);
            button.querySelector("[data-copy-label]").textContent = "Copy";
          }, 1800);
        } else {
          announce("Clipboard unavailable. The command is selected; copy it manually.");
        }
      });
    });

    const checkButton = document.getElementById("health-check");
    const healthPanel = document.querySelector("[data-health-state]");
    const healthLabel = document.getElementById("health-label");
    const healthTiming = document.getElementById("health-timing");
    const healthHttp = document.getElementById("health-http");
    const healthResponse = document.getElementById("health-response");
    if (!checkButton || !healthPanel) return;
    let checking = false;
    const checkHealth = async () => {
      if (checking) return;
      checking = true;
      checkButton.disabled = true;
      checkButton.setAttribute("aria-busy", "true");
      healthPanel.dataset.healthState = "checking";
      healthLabel.textContent = "Checking your application…";
      healthTiming.textContent = "Requesting /health";
      healthHttp.textContent = "Checking…";
      healthResponse.textContent = "Waiting for a response from /health…";
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 8000);
      const start = performance.now();
      let status = null;
      let hasPayload = false;
      try {
        const response = await fetch("/health", {
          cache: "no-store", headers: { "Accept": "application/json" }, signal: controller.signal,
        });
        status = response.status;
        healthHttp.textContent = `${response.status} ${response.statusText}`.trim();
        const payload = await response.json();
        hasPayload = true;
        const serialized = JSON.stringify(payload, null, 2);
        healthResponse.textContent = serialized.length > 12000 ? `${serialized.slice(0, 12000)}\n…response truncated` : serialized;
        if (!response.ok) throw new Error(`The health endpoint returned HTTP ${response.status}.`);
        if (!payload || payload.status !== "healthy") throw new Error("The endpoint returned an unexpected health response.");
        healthPanel.dataset.healthState = "healthy";
        healthLabel.textContent = "Your application is healthy";
        const elapsed = Math.max(1, Math.round(performance.now() - start));
        healthTiming.textContent = `${elapsed} ms round trip · checked ${new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`;
      } catch (error) {
        healthPanel.dataset.healthState = "error";
        healthLabel.textContent = error.name === "AbortError" ? "Health check timed out" : "Health check unsuccessful";
        healthTiming.textContent = "Check the server and try again.";
        if (status === null) healthHttp.textContent = error.name === "AbortError" ? "Timed out" : "Connection error";
        if (!hasPayload) {
          healthResponse.textContent = error.name === "AbortError" ? "No response within 8 seconds." : "Could not read a valid JSON response from /health.";
        }
      } finally {
        clearTimeout(timeout);
        checking = false;
        checkButton.disabled = false;
        checkButton.removeAttribute("aria-busy");
      }
    };
    checkButton.addEventListener("click", checkHealth);
    checkHealth();
  });
})();
