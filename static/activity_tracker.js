// Counts only: no key values, coordinates, clipboard or external application data.
(() => {
    let state = { session_id: null, status: "Stopped" };
    let counts = empty();
    let lastInput = 0;
    let lastTick = Date.now();
    let inFlight = null;
    let leader = false;
    const channel = typeof BroadcastChannel === "function" ? new BroadcastChannel("workai-input-counts") : null;
    if (channel) channel.onmessage = event => {
        if (working() && ["keyboard_events", "mouse_events"].includes(event.data)) {
            counts[event.data] += 1;
            lastInput = Date.now();
        }
    };
    function empty() {
        return { active_seconds: 0, idle_seconds: 0, keyboard_events: 0, mouse_events: 0 };
    }
    const working = () => leader && state.status === "Working";
    function input(kind) {
        if (!leader && channel) { channel.postMessage(kind); return; }
        if (!working()) return;
        counts[kind] += 1;
        lastInput = Date.now();
    }
    document.addEventListener("keydown", () => input("keyboard_events"), { passive: true });
    for (const event of ["mousemove", "click", "scroll", "touchstart"]) {
        document.addEventListener(event, () => input("mouse_events"), { passive: true });
    }
    function tick() {
        const now = Date.now();
        const elapsed = Math.floor((now - lastTick) / 1000);
        if (elapsed <= 0) return;
        if (working()) {
            const active = Math.min(elapsed, Math.max(0, Math.floor((lastInput + 60000 - lastTick) / 1000)));
            counts.active_seconds += active;
            counts.idle_seconds += elapsed - active;
        }
        lastTick += elapsed * 1000;
        const label = document.getElementById("trackerPulseText");
        if (label) label.textContent = !leader ? "Monitoring in another tab" : state.status !== "Working" ? "Monitoring paused" : now - lastInput < 60000 ? "Live Monitoring Active" : "Idle State Detected";
        const counter = document.getElementById("trackerLiveCounter");
        if (counter) counter.textContent = `${counts.active_seconds}s active · ${counts.idle_seconds}s idle`;
    }
    async function syncState() {
        try {
            const response = await fetch("/employee/work/state");
            if (!response.ok) { state.status = "Stopped"; counts = empty(); return; }
            const next = await response.json();
            if (next.session_id !== state.session_id || next.status !== state.status) {
                counts = empty(); lastTick = Date.now(); lastInput = 0;
            }
            state = next;
        } catch (_) { /* Retry on next poll. */ }
    }
    async function flush() {
        if (inFlight) return inFlight;
        tick();
        if (!working() || counts.active_seconds + counts.idle_seconds === 0) return;
        const batch = counts;
        counts = empty();
        if (batch.active_seconds + batch.idle_seconds > 300) {
            await syncState(); return;
        }
        inFlight = (async () => {
            try {
                const response = await fetch("/employee/activity", {
                    method: "POST", headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ ...batch, session_id: state.session_id })
                });
                if (!response.ok) await syncState();
                const note = document.getElementById("trackerSyncNote");
                if (note) note.textContent = response.ok ? `Synced: ${new Date().toLocaleTimeString()}` : "Sync rejected; state refreshed";
            } catch (_) {
                // Do not retry an ambiguous write and double-count its interval.
                const note = document.getElementById("trackerSyncNote");
                if (note) note.textContent = "Connection lost; this interval may be missing";
            } finally { inFlight = null; }
        })();
        return inFlight;
    }
    window.workaiTracker = { flush };
    // Web Locks serializes monitoring across tabs for this browser/origin.
    if (navigator.locks) {
        navigator.locks.request("workai-activity", async () => {
            leader = true;
            await syncState();
            await new Promise(() => {});
        });
    } else {
        leader = true;
        syncState();
    }
    setInterval(tick, 1000);
    setInterval(syncState, 5000);
    setInterval(flush, 30000);
    document.addEventListener("visibilitychange", () => {
        if (document.visibilityState === "hidden") flush();
    });
    window.addEventListener("pagehide", () => {
        tick();
        if (!working() || counts.active_seconds + counts.idle_seconds === 0 || counts.active_seconds + counts.idle_seconds > 300) return;
        navigator.sendBeacon("/employee/activity", new Blob([JSON.stringify({
            ...counts, session_id: state.session_id,
            csrf_token: document.querySelector('meta[name="csrf-token"]')?.content
        })], { type: "application/json" }));
        counts = empty();
    });
})();
