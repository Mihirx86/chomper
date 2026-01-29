//xxxxxxxxxxxxChompxxxxxxxxxxxxChompxxxxxxxxxxxx//

/**
 * Chomper Ad Blocker – Content Logic
 *
 * This file contains the core runtime logic responsible for
 * detecting, skipping, and removing intrusive advertising
 * elements, as well as recovering from playback stalls.
 * 
 * All logic is event-driven and guarded by a global
 * enable/disable flag for safe shutdown.
 */

let observer = null;
let intervalId = null;
let reloaded = false;
let lastTime = 0;
let stallCount = 0;
let isBlockingEnabled = true; // Global flag to control blocking

/* -----------------------------
   Core ad handling
------------------------------*/

/**
 * Attempts to fast-forward short promotional video segments
 * and activates any visible skip controls when available.
 */
function skipAds() {
  if (!isBlockingEnabled) return;
  
  const video = document.querySelector("video");
  if (!video) return;

  // Skip short promotional video segments
  if (video.duration && video.duration < 70 && !video.ended) {
    video.currentTime = video.duration;
  }

  // Click skip control if present
  const skipBtn = document.querySelector(
    ".ytp-ad-skip-button, .ytp-ad-skip-button-modern"
  );
  if (skipBtn) skipBtn.click();
}

/**
 * Removes known promotional containers from the document
 * tree using predefined selectors.
 */
function removeAds() {
  if (!isBlockingEnabled) return;
  
  [
    ".video-ads",
    ".ytp-ad-module",
    "#player-ads",
    "ytd-display-ad-renderer",
    "ytd-promoted-video-renderer",
    "ytd-companion-slot-renderer",
    "ytd-action-companion-ad-renderer"
  ].forEach(sel => {
    document.querySelectorAll(sel).forEach(el => el.remove());
  });
}

/**
 * Detects stalled playback states and performs a single
 * recovery reload if a hard stall persists.
 */
function detectAndRecover() {
  if (!isBlockingEnabled) return;
  
  const video = document.querySelector("video");
  if (!video) return;

  if (video.currentTime === lastTime && !video.paused) {
    stallCount++;
  } else {
    stallCount = 0;
  }

  lastTime = video.currentTime;

  // Reload once if a hard stall is detected
  if (stallCount > 6 && !reloaded) {
    reloaded = true;
    location.reload();
  }
}

/* -----------------------------
   START blocking logic
------------------------------*/

/**
 * Initializes observers and timers required for
 * continuous ad detection and removal.
 */
function startBlocking() {
  if (observer || intervalId) return;
  
  isBlockingEnabled = true;
  reloaded = false;
  stallCount = 0;
  lastTime = 0;

  observer = new MutationObserver(() => {
    skipAds();
    removeAds();
  });

  observer.observe(document.documentElement, {
    childList: true,
    subtree: true
  });

  intervalId = setInterval(() => {
    skipAds();
    removeAds();
    detectAndRecover();
    chomperAdBlock(); // Run Chomper universal cleanup pass
  }, 500);
}

/* -----------------------------
   STOP blocking logic
------------------------------*/

/**
 * Fully disables all blocking behavior and
 * cleans up observers and timers.
 */
function stopBlocking() {
  isBlockingEnabled = false;
  
  if (observer) {
    observer.disconnect();
    observer = null;
  }

  if (intervalId) {
    clearInterval(intervalId);
    intervalId = null;
  }
}

/* -----------------------------
   CHOMPER universal ad blocker
------------------------------*/

/**
 * Performs a broad cleanup pass against common
 * advertising, banner, overlay, and promotional
 * element patterns across the page.
 */
function chomperAdBlock() {
  if (!isBlockingEnabled) return;
  
  const universalSelectors = [
  ".ad-banner",
  ".ad-container",
  ".popup-ad",
  ".overlay-ad",
  ".sponsored-content",
  ".ad-frame",
  ".ad-slot",
  ".ad-box",
  ".ad-label",
  ".sponsored-ad",
  ".ad-marketing",
  ".ad-wrapper",
  ".promotional-ad",
  ".ad-section",
  ".ad-feature",
  ".ad-display",
  ".ad-unit",
  ".ad-placeholder",
  ".promoted-content",
  ".sponsored-link",
  ".ad-strip",
  ".ad-panel",
  ".popup-banner",
  ".ad-modal",
  ".ad-top",
  ".ad-bottom",
  ".ad-left",
  ".ad-right",
  ".ad-inline",
  ".ad-sidebar",
  ".ad-footer",
  ".ad-header",
  ".ad-middle",
  ".ad-background",
  ".ad-target",
  ".ad-click",
  ".ad-img",
  ".ad-text",
  ".ad-video",
  ".ad-iframe",
  ".ad-popout",
  ".ad-expand",
  ".ad-collapse",
  ".ad-hover",
  ".ad-hover-effect",
  ".ad-banner-top",
  ".ad-banner-bottom",
  ".ad-banner-left",
  ".ad-banner-right",
  ".ad-banner-inline",
  ".ad-banner-sidebar",
  ".ad-banner-footer",
  ".ad-banner-header",
  ".ad-overlay-top",
  ".ad-overlay-bottom",
  ".ad-overlay-left",
  ".ad-overlay-right",
  ".ad-overlay-inline",
  ".ad-overlay-sidebar",
  ".ad-overlay-footer",
  ".ad-overlay-header",
  ".sponsored-top",
  ".sponsored-bottom",
  ".sponsored-left",
  ".sponsored-right",
  ".sponsored-inline",
  ".sponsored-sidebar",
  ".sponsored-footer",
  ".sponsored-header",
  ".promotional-top",
  ".promotional-bottom",
  ".promotional-left",
  ".promotional-right",
  ".promotional-inline",
  ".promotional-sidebar",
  ".promotional-footer",
  ".promotional-header",
  ".ad-feature-top",
  ".ad-feature-bottom",
  ".ad-feature-left",
  ".ad-feature-right",
  ".ad-feature-inline",
  ".ad-feature-sidebar",
  ".ad-feature-footer",
  ".ad-feature-header",
  ".ad-section-top",
  ".ad-section-bottom",
  ".ad-section-left",
  ".ad-section-right",
  ".ad-section-inline",
  ".ad-section-sidebar",
  ".ad-section-footer",
  ".ad-section-header",
  ".ad-box-top",
  ".ad-box-bottom",
  ".ad-box-left",
  ".ad-box-right",
  ".ad-box-inline",
  ".ad-box-sidebar",
  ".ad-box-footer",
  ".ad-box-header",
  ".ad-wrapper-top",
  ".ad-wrapper-bottom",
  ".ad-wrapper-left",
  ".ad-wrapper-right",
  ".ad-wrapper-inline",
  ".ad-wrapper-sidebar",
  ".ad-wrapper-footer",
  ".ad-wrapper-header",
  ".ad-unit-top",
  ".ad-unit-bottom",
  ".ad-unit-left",
  ".ad-unit-right",
  ".ad-unit-inline",
  ".ad-unit-sidebar",
  ".ad-unit-footer",
  ".ad-unit-header",
  ".ad-placeholder-top",
  ".ad-placeholder-bottom",
  ".ad-placeholder-left",
  ".ad-placeholder-right",
  ".ad-placeholder-inline",
  ".ad-placeholder-sidebar",
  ".ad-placeholder-footer",
  ".ad-placeholder-header",
  ".ad-marketing-top",
  ".ad-marketing-bottom",
  ".ad-marketing-left",
  ".ad-marketing-right",
  ".ad-marketing-inline",
  ".ad-marketing-sidebar",
  ".ad-marketing-footer",
  ".ad-marketing-header",
  ".ad-strip-top",
  ".ad-strip-bottom",
  ".ad-strip-left",
  ".ad-strip-right",
  ".ad-strip-inline",
  ".ad-strip-sidebar",
  ".ad-strip-footer",
  ".ad-strip-header",
  ".popup-ad-top",
  ".popup-ad-bottom",
  ".popup-ad-left",
  ".popup-ad-right",
  ".popup-ad-inline",
  ".popup-ad-sidebar",
  ".popup-ad-footer",
  ".popup-ad-header",
  ".popup-banner-top",
  ".popup-banner-bottom",
  ".popup-banner-left",
  ".popup-banner-right",
  ".popup-banner-inline",
  ".popup-banner-sidebar",
  ".popup-banner-footer",
  ".popup-banner-header",
  ".ad-modal-top",
  ".ad-modal-bottom",
  ".ad-modal-left",
  ".ad-modal-right",
  ".ad-modal-inline",
  ".ad-modal-sidebar",
  ".ad-modal-footer",
  ".ad-modal-header",
  ".sponsored-modal",
  ".promoted-modal",
  ".ad-floating",
  ".ad-sticky",
  ".ad-fixed",
  ".ad-slide",
  ".ad-carousel",
  ".ad-scroll",
  ".ad-animate",
  ".ad-rotate",
  ".ad-expandable",
  ".ad-interstitial",
  ".ad-infeed",
  ".ad-native",
  ".ad-sponsored",
  ".ad-promoted",
  ".ad-clickable",
  ".ad-popular",
  ".ad-recommended",
  ".ad-related",
  ".ad-featured",
  ".ad-highlight",
  ".ad-trending",
  ".ad-topbanner",
  ".ad-bottombanner",
  ".ad-leftbanner",
  ".ad-rightbanner",
  ".ad-inlinebanner",
  ".ad-sidebarbanner",
  ".ad-footerbanner",
  ".ad-headerbanner",
  ".ad-popupbanner",
  ".ad-overlaybanner",
  ".ad-topslot",
  ".ad-bottomslot",
  ".ad-leftslot",
  ".ad-rightslot",
  ".ad-inlineslot",
  ".ad-sidebarslot",
  ".ad-headerslot",
  ".ad-footerslot",
  ".ad-main",
  ".ad-secondary",
  ".ad-tertiary",
  ".ad-mini",
  ".ad-small",
  ".ad-medium",
  ".ad-large",
  ".ad-extra",
  ".ad-huge",
  ".ad-super",
  ".ad-ultimate",
  ".ad-ultra",
  ".ad-premium",
  ".ad-elite",
  ".ad-gold",
  ".ad-silver",
  ".ad-bronze",
  ".ad-sponsored-top",
  ".ad-sponsored-bottom",
  ".ad-sponsored-left",
  ".ad-sponsored-right"
  ];

  universalSelectors.forEach(sel => {
    document.querySelectorAll(sel).forEach(el => {
      // Prevent removal of protected playback containers
      if (!el.closest("#movie_player, .video-ads, ytd-display-ad-renderer")) {
        el.remove();
      }
    });
  });

  

  // Remove high z-index overlays and pop-up layers
  document.querySelectorAll(
    "div[style*='position: fixed'], div[style*='position: absolute']"
  ).forEach(el => {
    if (!el.closest("#movie_player, .ytp-ad-module")) {
      const zIndex = window.getComputedStyle(el).zIndex;
      if (zIndex && parseInt(zIndex) > 1000) {
        el.remove();
      }
    }
  });
}

/* -----------------------------
   State synchronization
------------------------------*/

/**
 * Initializes blocking state based on stored
 * enable/disable preference.
 */
chrome.storage.local.get(["enabled"], res => {
  const enabled = res.enabled !== undefined ? res.enabled : true;
  
  if (enabled) {
    startBlocking();
  } else {
    stopBlocking();
  }
});

/**
 * Reacts to runtime enable/disable changes
 * and performs a clean transition.
 */
chrome.storage.onChanged.addListener(changes => {
  if (!changes.enabled) return;

  if (changes.enabled.newValue === true) {
    location.reload();
  } else {
    stopBlocking();
  }
});

//xxxxxxxxxxxxChompxxxxxxxxxxxxChompxxxxxxxxxxxx//
