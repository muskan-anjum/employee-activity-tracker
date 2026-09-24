// WorkAI Client-Side Activity Monitoring Engine
// Captures non-invasive interaction signals (keystroke counts and mouse movements)
// Does NOT capture key characters, clipboard, screen, or sensitive content.

let keyboardEvents = 0;
let mouseEvents = 0;

let activeSeconds = 0;
let idleSeconds = 0;

let lastActivity = Date.now();
const IDLE_LIMIT = 60 * 1000; // 60 seconds of inactivity triggers idle state

function updateLiveTrackerUI(isCurrentlyActive) {
    const pulseEl = document.getElementById("trackerPulseDot");
    const labelEl = document.getElementById("trackerPulseText");
    const countEl = document.getElementById("trackerLiveCounter");

    if (pulseEl && labelEl) {
        if (isCurrentlyActive) {
            pulseEl.className = "pulse-dot active";
            labelEl.textContent = "Live Monitoring Active";
        } else {
            pulseEl.className = "pulse-dot idle";
            labelEl.textContent = "Idle State Detected";
        }
    }

    if (countEl) {
        countEl.textContent = `${activeSeconds}s active · ${idleSeconds}s idle`;
    }
}

function registerKeyboardActivity() {
    keyboardEvents += 1;
    lastActivity = Date.now();
    updateLiveTrackerUI(true);
}

function registerMouseActivity() {
    mouseEvents += 1;
    lastActivity = Date.now();
    updateLiveTrackerUI(true);
}

// Global DOM interaction event listeners
document.addEventListener("keydown", registerKeyboardActivity, { passive: true });
document.addEventListener("mousemove", registerMouseActivity, { passive: true });
document.addEventListener("click", registerMouseActivity, { passive: true });
document.addEventListener("scroll", function () {
    lastActivity = Date.now();
    updateLiveTrackerUI(true);
}, { passive: true });

// Check activity state every second
setInterval(function () {
    const inactiveFor = Date.now() - lastActivity;

    if (inactiveFor < IDLE_LIMIT) {
        activeSeconds += 1;
        updateLiveTrackerUI(true);
    } else {
        idleSeconds += 1;
        updateLiveTrackerUI(false);
    }
}, 1000);

// Transmit accumulated interaction metrics to WorkAI backend every 30 seconds
async function sendActivityData() {
    if (activeSeconds === 0 &&
        idleSeconds === 0 &&
        keyboardEvents === 0 &&
        mouseEvents === 0) {
        return;
    }

    const payload = {
        active_seconds: activeSeconds,
        idle_seconds: idleSeconds,
        keyboard_events: keyboardEvents,
        mouse_events: mouseEvents
    };

    try {
        const response = await fetch("/employee/activity", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        if (response.ok || response.status === 400) {
            activeSeconds = 0;
            idleSeconds = 0;
            keyboardEvents = 0;
            mouseEvents = 0;

            const syncEl = document.getElementById("trackerSyncNote");
            if (syncEl) {
                const now = new Date();
                syncEl.textContent = `Synced: ${now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}`;
            }
        }
    } catch (error) {
        console.warn("WorkAI activity tracking network note:", error);
    }
}

setInterval(sendActivityData, 30000);

// Transmit remaining metrics via Beacon API before navigation/unload
window.addEventListener("beforeunload", function () {
    if (activeSeconds === 0 &&
        idleSeconds === 0 &&
        keyboardEvents === 0 &&
        mouseEvents === 0) {
        return;
    }

    const payload = JSON.stringify({
        active_seconds: activeSeconds,
        idle_seconds: idleSeconds,
        keyboard_events: keyboardEvents,
        mouse_events: mouseEvents
    });

    navigator.sendBeacon(
        "/employee/activity",
        new Blob([payload], { type: "application/json" })
    );
});