let keyboardEvents = 0;
let mouseEvents = 0;

let activeSeconds = 0;
let idleSeconds = 0;

let lastActivity = Date.now();

const IDLE_LIMIT = 60 * 1000; // 60 seconds


function registerKeyboardActivity() {
    keyboardEvents += 1;
    lastActivity = Date.now();
}


function registerMouseActivity() {
    mouseEvents += 1;
    lastActivity = Date.now();
}


// We count activity only.
// We DO NOT store which keys were pressed.
document.addEventListener("keydown", registerKeyboardActivity);

document.addEventListener("mousemove", registerMouseActivity);

document.addEventListener("click", registerMouseActivity);

document.addEventListener("scroll", function () {
    lastActivity = Date.now();
});


// Check activity every second.
setInterval(function () {

    const inactiveFor = Date.now() - lastActivity;

    if (inactiveFor < IDLE_LIMIT) {
        activeSeconds += 1;
    } else {
        idleSeconds += 1;
    }

}, 1000);


// Send accumulated activity to Flask every 30 seconds.
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

        if (response.ok) {
            activeSeconds = 0;
            idleSeconds = 0;
            keyboardEvents = 0;
            mouseEvents = 0;
        }

    } catch (error) {
        console.error("Activity tracking error:", error);
    }
}


setInterval(sendActivityData, 30000);


// Try to save remaining activity before the employee leaves.
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
        new Blob(
            [payload],
            { type: "application/json" }
        )
    );

});