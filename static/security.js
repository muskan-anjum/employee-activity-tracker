(() => {
    const token = document.querySelector('meta[name="csrf-token"]').content;
    const originalFetch = window.fetch.bind(window);
    window.fetch = (resource, options = {}) => {
        const url = new URL(typeof resource === "string" ? resource : resource.url, location.href);
        const method = (options.method || resource.method || "GET").toUpperCase();
        if (url.origin === location.origin && !["GET", "HEAD", "OPTIONS"].includes(method)) {
            const headers = new Headers(options.headers || resource.headers);
            headers.set("X-CSRF-Token", token);
            options = { ...options, headers };
        }
        return originalFetch(resource, options);
    };
    document.addEventListener("DOMContentLoaded", () => {
        for (const form of document.forms) {
            if (form.method.toLowerCase() !== "post" || form.querySelector('[name="csrf_token"]')) continue;
            const field = document.createElement("input");
            field.type = "hidden"; field.name = "csrf_token"; field.value = token;
            form.appendChild(field);
        }
        for (const link of document.querySelectorAll('a[href="/logout"]')) {
            link.addEventListener("click", async event => {
                event.preventDefault();
                if (window.workaiTracker) await window.workaiTracker.flush();
                await fetch("/logout", { method: "POST" });
                location.href = "/login";
            });
        }
    });
})();
