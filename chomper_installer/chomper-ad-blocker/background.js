//xxxxxxxxxxxxChompxxxxxxxxxxxxChompxxxxxxxxxxxx//
/**
 * Chomper Ad Blocker – Background Initialization
 *
 * This file handles startup and installation behavior.
 * It ensures the blocker is enabled by default and
 * refreshes open tabs when the extension starts,
 * allowing rules to take effect immediately.
 */

/**
 * Runs once when the extension is first installed or updated.
 * Sets the enabled flag to true so the blocker is active by default.
 */
chrome.runtime.onInstalled.addListener(() => {
  // Always set enabled to true by default
  chrome.storage.local.set({ enabled: true });
});

/**
 * Runs whenever the browser starts and the extension is loaded.
 * If the blocker is enabled, all open tabs are reloaded
 * so blocking rules are applied consistently.
 */
chrome.runtime.onStartup.addListener(() => {
  chrome.storage.local.get(["enabled"], (res) => {
    if (res.enabled) {
      // Reload all tabs when extension starts
      chrome.tabs.query({}, (tabs) => {
        tabs.forEach(tab => chrome.tabs.reload(tab.id));
      });
    }
  });
});

//xxxxxxxxxxxxChompxxxxxxxxxxxxChompxxxxxxxxxxxx//