(function () {
    const KEYS = {
        apiKey: "pnp.assistant.apiKey",
        model: "pnp.assistant.model",
        provider: "pnp.assistant.provider",
        session: "pnp.assistant.session"
    };

    function $(id) { return document.getElementById(id); }
    function escapeHtml(v) {
        return String(v ?? "")
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#39;");
    }

    function getSessionId() {
        return $("assistantSession").value.trim() || "default";
    }

    function restoreSettings() {
        $("assistantApiKey").value = localStorage.getItem(KEYS.apiKey) || "";
        $("assistantModel").value = localStorage.getItem(KEYS.model) || "gemini-3-flash-preview";
        $("assistantProvider").value = localStorage.getItem(KEYS.provider) || "gemini";
        $("assistantSession").value = localStorage.getItem(KEYS.session) || "default";
        applyProviderDefaultModel(false);
    }

    function persistSettings() {
        localStorage.setItem(KEYS.apiKey, $("assistantApiKey").value.trim());
        localStorage.setItem(KEYS.model, $("assistantModel").value.trim() || "gemini-3-flash-preview");
        localStorage.setItem(KEYS.provider, $("assistantProvider").value.trim() || "gemini");
        localStorage.setItem(KEYS.session, getSessionId());
    }

    function applyProviderDefaultModel(force) {
        const provider = $("assistantProvider").value.trim().toLowerCase();
        const defaults = {
            openai: "gpt-4o-mini",
            openrouter: "openai/gpt-4o-mini",
            anthropic: "claude-3-5-sonnet-latest",
            gemini: "gemini-3-flash-preview"
        };
        const nextModel = defaults[provider] || "gpt-4o-mini";
        const modelInput = $("assistantModel");
        const current = modelInput.value.trim();
        if (force || !current) {
            modelInput.value = nextModel;
        }
    }

    function renderHistory(history) {
        const box = $("assistantHistory");
        if (!Array.isArray(history) || !history.length) {
            box.innerHTML = '<div class="text-sm text-white/60">No chat history yet.</div>';
            return;
        }
        box.innerHTML = history.map((item) => {
            const role = String(item.role || "assistant");
            const color = role === "user" ? "text-cyan-200" : "text-emerald-200";
            return `
                <div class="rounded-xl border border-white/10 bg-black/20 p-3 mb-2">
                    <div class="text-xs ${color} mb-1">${escapeHtml(role)}</div>
                    <div class="text-sm text-white/90 whitespace-pre-wrap">${escapeHtml(item.content || "")}</div>
                </div>
            `;
        }).join("");
        box.scrollTop = box.scrollHeight;
    }

    function renderMemory(memory) {
        const list = $("assistantMemory");
        const items = (memory && Array.isArray(memory.items)) ? memory.items : [];
        if (!items.length) {
            list.innerHTML = '<li class="text-white/60">No memory items yet.</li>';
            return;
        }
        list.innerHTML = items.slice(-30).map((i) => `<li>${escapeHtml(i)}</li>`).join("");
    }

    async function loadHistory() {
        persistSettings();
        const sessionId = encodeURIComponent(getSessionId());
        const res = await fetch(`/api/assistant/history?session_id=${sessionId}`);
        const data = await res.json();
        renderHistory(data.history || []);
        renderMemory(data.memory || {});
    }

    async function sendMessage() {
        persistSettings();
        const input = $("assistantInput");
        const message = input.value.trim();
        if (!message) return;

        $("assistantStatus").textContent = "Thinking...";
        const payload = {
            message,
            api_key: $("assistantApiKey").value.trim(),
            model: $("assistantModel").value.trim() || "gemini-3-flash-preview",
            provider: $("assistantProvider").value.trim() || "gemini",
            session_id: getSessionId(),
            scope: {
                query: $("assistantScopeQuery").value.trim(),
                playlist_id: $("assistantScopePlaylist").value.trim(),
                limit: Number($("assistantScopeLimit").value || 120)
            }
        };

        try {
            const res = await fetch("/api/assistant/llm-chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            renderHistory(data.history || []);
            renderMemory(data.memory || {});
            $("assistantStatus").textContent = data.warning ? `Fallback used: ${data.warning}` : `Mode: ${data.mode}`;
            input.value = "";
        } catch (err) {
            $("assistantStatus").textContent = `Error: ${err.message}`;
        }
    }

    async function clearHistory(clearMemory) {
        persistSettings();
        const sessionId = encodeURIComponent(getSessionId());
        const res = await fetch(`/api/assistant/history?session_id=${sessionId}&clear_memory=${clearMemory ? "true" : "false"}`, {
            method: "DELETE"
        });
        if (res.ok) {
            await loadHistory();
            $("assistantStatus").textContent = clearMemory ? "History + memory cleared." : "History cleared.";
        }
    }

    function generateSessionId() {
        return Math.random().toString(36).substring(2, 10);
    }

    function newChat() {
        $("assistantSession").value = "session-" + generateSessionId();
        persistSettings();
        renderHistory([]);
        renderMemory({});
        $("assistantStatus").textContent = "New chat initialized.";
    }

    document.addEventListener("DOMContentLoaded", async () => {
        restoreSettings();
        $("assistantSend").addEventListener("click", sendMessage);
        $("assistantNewChat").addEventListener("click", newChat);
        $("assistantInput").addEventListener("keydown", (e) => {
            if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
        $("assistantReload").addEventListener("click", loadHistory);
        $("assistantClearHistory").addEventListener("click", () => clearHistory(false));
        $("assistantClearAll").addEventListener("click", () => clearHistory(true));
        ["assistantApiKey", "assistantModel", "assistantProvider", "assistantSession"].forEach((id) => {
            $(id).addEventListener("change", persistSettings);
            $(id).addEventListener("blur", persistSettings);
        });
        $("assistantProvider").addEventListener("change", () => {
            applyProviderDefaultModel(true);
            persistSettings();
        });
        await loadHistory();
    });
})();
