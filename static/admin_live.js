(() => {
    function render(id, rows) {
        const target = document.getElementById(id);
        target.replaceChildren();
        for (const text of rows) {
            const item = document.createElement("p");
            item.textContent = text;
            target.appendChild(item);
        }
    }
    async function refresh() {
        try {
            const response = await fetch("/admin/live", { headers: { Accept: "application/json" } });
            if (!response.ok) throw new Error("Unavailable");
            const data = await response.json();
            render("live-projects", data.projects.length ? data.projects.map(p => `${p.name} · ${p.status} · ${p.progress}% task progress`) : ["No projects created."]);
            render("live-presence", data.employees.length ? data.employees.map(e => `${e.name} · ${e.online ? 'Online' : 'No recent heartbeat'} · ${e.status} · ${e.project} · ${Math.floor(e.net_seconds / 60)} min net work`) : ["No open work sessions."]);
            render("live-events", data.events.length ? data.events.map(e => `${new Date(e.timestamp).toLocaleTimeString()} · ${e.employee}: ${e.active_seconds}s active, ${e.idle_seconds}s idle · ${e.keyboard_events} keyboard / ${e.mouse_events} mouse events`) : ["No activity intervals recorded."]);
            document.getElementById("live-status").textContent = `Updated ${new Date().toLocaleTimeString()} · refreshes every 10 seconds`;
        } catch (_) {
            document.getElementById("live-status").textContent = "Live update unavailable. Retrying…";
        }
    }
    refresh(); setInterval(refresh, 10000);
})();
