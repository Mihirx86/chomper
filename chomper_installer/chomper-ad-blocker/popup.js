/**
 * Chomper Popup Controller
 * Controls the toggle button and synchronizes visual state
 */

const btn = document.getElementById("toggleBtn");
const statusText = document.getElementById("status");

function updateButton(enabled) {
  if (enabled) {
    btn.textContent = "STOP";
    btn.classList.add("stop");
    statusText.innerHTML =
      'Blocking is <span class="status-on">ACTIVE</span>';
  } else {
    btn.textContent = "START";
    btn.classList.remove("stop");
    statusText.innerHTML =
      'Blocking is <span class="status-off">INACTIVE</span>';
  }
}

chrome.storage.local.get(["enabled"], (res) => {
  const isEnabled = res.enabled !== undefined ? res.enabled : true;
  updateButton(isEnabled);
});

btn.addEventListener("click", () => {
  chrome.storage.local.get(["enabled"], (res) => {
    const currentState = res.enabled !== undefined ? res.enabled : true;
    const newState = !currentState;

    chrome.storage.local.set({ enabled: newState }, () => {
      updateButton(newState);

      if (newState) {
        chrome.tabs.query({}, (tabs) => {
          tabs.forEach(tab => {
            if (
              tab.url &&
              !tab.url.startsWith("chrome://") &&
              !tab.url.startsWith("chrome-extension://")
            ) {
              chrome.tabs.reload(tab.id);
            }
          });
        });
      }
    });
  });
});