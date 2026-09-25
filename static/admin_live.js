(() => {
    function setContent(id, fragment) {
        const target = document.getElementById(id);
        if (!target) return;
        target.replaceChildren(fragment);
    }

    async function refresh() {
        const statusEl = document.getElementById("live-status");
        try {
            const response = await fetch("/admin/live", { headers: { Accept: "application/json" } });
            if (!response.ok) throw new Error("Unavailable");
            const data = await response.json();

            // 1. Projects Progress
            const projFrag = document.createDocumentFragment();
            if (data.projects && data.projects.length) {
                const list = document.createElement("div");
                list.className = "live-list";
                data.projects.forEach(p => {
                    const item = document.createElement("div");
                    item.className = "live-item";
                    item.style.flexDirection = "column";
                    item.style.alignItems = "stretch";
                    item.style.gap = "6px";

                    item.innerHTML = `
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <strong style="color: var(--text); font-size: 13.5px;">${escapeHtml(p.name)}</strong>
                            <span class="badge ${p.status === 'Active' ? 'badge-success' : 'badge-neutral'}">${escapeHtml(p.status)}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; font-size: 12px; color: var(--text-muted);">
                            <span>Task Velocity</span>
                            <span style="font-weight: 600; color: var(--text);">${p.progress}%</span>
                        </div>
                        <div class="progress-container">
                            <div class="progress-bar" style="width: ${Math.min(100, Math.max(0, p.progress))}%;"></div>
                        </div>
                    `;
                    list.appendChild(item);
                });
                projFrag.appendChild(list);
            } else {
                const empty = document.createElement("div");
                empty.className = "stat-note";
                empty.style.padding = "8px 0";
                empty.textContent = "No project workspaces created.";
                projFrag.appendChild(empty);
            }
            setContent("live-projects", projFrag);

            // 2. Employee Live Presence
            const presFrag = document.createDocumentFragment();
            if (data.employees && data.employees.length) {
                const list = document.createElement("div");
                list.className = "live-list";
                data.employees.forEach(e => {
                    const item = document.createElement("div");
                    item.className = "live-item";
                    const initial = (e.name && e.name[0]) ? e.name[0].toUpperCase() : "U";
                    const mins = Math.floor((e.net_seconds || 0) / 60);

                    item.innerHTML = `
                        <div class="live-item-content">
                            <div class="avatar" style="width: 32px; height: 32px; font-size: 12px;">${initial}</div>
                            <div>
                                <div style="font-weight: 600; color: var(--text);">${escapeHtml(e.name)}</div>
                                <div class="stat-note">${escapeHtml(e.project || 'General Workspace')} &bull; ${mins}m net work</div>
                            </div>
                        </div>
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <span class="badge ${e.status === 'Working' ? 'badge-success' : 'badge-warning'}">${escapeHtml(e.status)}</span>
                            <span class="badge ${e.online ? 'badge-info' : 'badge-neutral'}">
                                <span class="live-dot ${e.online ? 'online' : 'offline'}"></span>
                                ${e.online ? 'Active' : 'No heartbeat'}
                            </span>
                        </div>
                    `;
                    list.appendChild(item);
                });
                presFrag.appendChild(list);
            } else {
                const empty = document.createElement("div");
                empty.className = "stat-note";
                empty.style.padding = "8px 0";
                empty.textContent = "No open employee work sessions.";
                presFrag.appendChild(empty);
            }
            setContent("live-presence", presFrag);

            // 3. Latest Activity Intervals
            const evtFrag = document.createDocumentFragment();
            if (data.events && data.events.length) {
                const list = document.createElement("div");
                list.className = "live-list";
                data.events.forEach(ev => {
                    const item = document.createElement("div");
                    item.className = "live-item";
                    const timeStr = ev.timestamp ? new Date(ev.timestamp).toLocaleTimeString() : "";

                    item.innerHTML = `
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <span style="font-family: monospace; font-size: 11px; background: var(--surface); padding: 2px 6px; border: 1px solid var(--border); border-radius: 4px; color: var(--text-muted);">${timeStr}</span>
                            <strong style="color: var(--text);">${escapeHtml(ev.employee)}</strong>
                        </div>
                        <div style="display: flex; gap: 6px; flex-wrap: wrap;">
                            <span class="badge badge-info">${ev.active_seconds}s active</span>
                            <span class="badge badge-neutral">${ev.keyboard_events} keys / ${ev.mouse_events} mouse</span>
                        </div>
                    `;
                    list.appendChild(item);
                });
                evtFrag.appendChild(list);
            } else {
                const empty = document.createElement("div");
                empty.className = "stat-note";
                empty.style.padding = "8px 0";
                empty.textContent = "No activity intervals recorded.";
                evtFrag.appendChild(empty);
            }
            setContent("live-events", evtFrag);

            if (statusEl) {
                statusEl.textContent = `Live updated at ${new Date().toLocaleTimeString()} (refreshes every 10s)`;
            }
        } catch (_) {
            if (statusEl) {
                statusEl.textContent = "Live update connection retrying…";
            }
        }
    }

    function escapeHtml(str) {
        if (!str) return "";
        return String(str)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    refresh();
    setInterval(refresh, 10000);
})();
