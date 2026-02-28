(function () {
    const KEYS = {
        apiKey: "pnp.assistant.apiKey",
        model: "pnp.assistant.model",
        provider: "pnp.assistant.provider",
        session: "pnp.assistant.session"
    };

    function esc(v) {
        return String(v ?? "")
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#39;");
    }

    function ensureUi() {
        if (document.getElementById("assistantWidgetRoot")) return;
        const root = document.createElement("div");
        root.id = "assistantWidgetRoot";
        root.innerHTML = `
            <style>
                #assistantFab {
                    position: fixed; right: 18px; bottom: 18px; z-index: 9999;
                    width: 56px; height: 56px; border-radius: 999px;
                    border: 1px solid rgba(255,255,255,.3); background: rgba(96, 52, 204, .82); color: #fff;
                    box-shadow: 0 8px 24px rgba(0,0,0,.35); cursor: pointer;
                }
                #assistantPanel {
                    position: fixed; right: 18px; bottom: 84px; z-index: 9999;
                    width: min(420px, calc(100vw - 24px)); max-height: 72vh; display: none;
                    border: 1px solid rgba(255,255,255,.2); border-radius: 16px;
                    background: rgba(9, 13, 27, .95); color: #fff; overflow: hidden;
                    box-shadow: 0 20px 44px rgba(0,0,0,.45);
                }
                #assistantPanel.open { display: block; }
                #assistantPanel .hd { padding: 10px 12px; border-bottom: 1px solid rgba(255,255,255,.12); display:flex; justify-content:space-between; align-items:center; }
                #assistantPanel .bd { padding: 10px 12px; display:flex; flex-direction:column; gap:8px; }
                #assistantMessages { overflow:auto; max-height: 290px; padding-right: 4px; }
                .assistant-msg { border:1px solid rgba(255,255,255,.12); border-radius: 10px; padding: 8px; margin-bottom:6px; }
                .assistant-msg .r { font-size: 11px; opacity:.75; margin-bottom: 4px; }
                #assistantSettings details { border:1px solid rgba(255,255,255,.12); border-radius:10px; padding:8px; }
                #assistantSettings input, #assistantSettings select, #assistantInput {
                    width: 100%; border:1px solid rgba(255,255,255,.16); border-radius:8px;
                    background: rgba(255,255,255,.05); color:#fff; padding:8px;
                }
                #assistantInput { min-height: 40px; }
                #assistantPanel button.small { border:1px solid rgba(255,255,255,.2); background: rgba(255,255,255,.08); color:#fff; border-radius:8px; padding:6px 10px; cursor:pointer; }
                #assistantPanel .row { display:flex; gap:8px; }
                #assistantPanel .row > * { flex:1; }
                #assistantOpenPage { font-size: 12px; color: #c9b8ff; text-decoration:none; }
            </style>
            <button id="assistantFab" title="Open assistant">AI</button>
            <div id="assistantPanel">
                <div class="hd">
                    <strong>Assistant</strong>
                    <div class="row" style="flex:0 0 auto; gap:6px;">
                        <a id="assistantOpenPage" href="/assistant" target="_blank" rel="noopener">Open page</a>
                        <button id="assistantClose" class="small" style="flex:0 0 auto;">x</button>
                    </div>
                </div>
                <div class="bd">
                    <div id="assistantMessages"></div>
                    <div id="assistantSettings">
                        <details>
                            <summary style="cursor:pointer;">Settings</summary>
                            <div style="display:flex; flex-direction:column; gap:8px; margin-top:8px;">
                                <input id="assistantApiKey" type="password" placeholder="LLM API key (optional)">
                                <div class="row">
                                    <select id="assistantProvider">
                                        <option value="gemini" selected>gemini</option>
                                        <option value="openai">openai</option>
                                        <option value="openrouter">openrouter</option>
                                        <option value="anthropic">anthropic</option>
                                    </select>
                                    <input id="assistantModel" value="gemini-3-flash-preview" placeholder="model">
                                </div>
                                <input id="assistantSession" placeholder="session id" value="default">
                                <div class="row">
                                    <button id="assistantReload" class="small">Reload history</button>
                                    <button id="assistantClear" class="small">Clear history</button>
                                </div>
                            </div>
                        </details>
                    </div>
                    <textarea id="assistantInput" placeholder="Ask about playlists/videos..."></textarea>
                    <div class="row">
                        <button id="assistantSend" class="small">Send</button>
                        <div id="assistantStatus" style="font-size:12px; opacity:.75; padding-top:8px;">Ready</div>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(root);
    }

    function getSession() {
        const val = document.getElementById("assistantSession")?.value.trim();
        return val || "default";
    }

    function restoreSettings() {
        document.getElementById("assistantApiKey").value = localStorage.getItem(KEYS.apiKey) || "";
        document.getElementById("assistantModel").value = localStorage.getItem(KEYS.model) || "gemini-3-flash-preview";
        document.getElementById("assistantProvider").value = localStorage.getItem(KEYS.provider) || "gemini";
        const fallbackSession = `widget:${window.location.pathname || "/"}`;
        document.getElementById("assistantSession").value = localStorage.getItem(KEYS.session) || fallbackSession;
        applyProviderDefaultModel(false);
    }

    function persistSettings() {
        localStorage.setItem(KEYS.apiKey, document.getElementById("assistantApiKey").value.trim());
        localStorage.setItem(KEYS.model, document.getElementById("assistantModel").value.trim() || "gemini-3-flash-preview");
        localStorage.setItem(KEYS.provider, document.getElementById("assistantProvider").value.trim() || "gemini");
        localStorage.setItem(KEYS.session, getSession());
    }

    function applyProviderDefaultModel(force) {
        const provider = document.getElementById("assistantProvider").value.trim().toLowerCase();
        const defaults = {
            openai: "gpt-4o-mini",
            openrouter: "openai/gpt-4o-mini",
            anthropic: "claude-3-5-sonnet-latest",
            gemini: "gemini-3-flash-preview"
        };
        const modelInput = document.getElementById("assistantModel");
        if (force || !modelInput.value.trim()) {
            modelInput.value = defaults[provider] || "gpt-4o-mini";
        }
    }

    function renderHistory(history) {
        const box = document.getElementById("assistantMessages");
        if (!Array.isArray(history) || !history.length) {
            box.innerHTML = '<div class="assistant-msg"><div class="r">assistant</div><div>No history yet.</div></div>';
            return;
        }
        box.innerHTML = history.slice(-20).map((item) => `
            <div class="assistant-msg">
                <div class="r">${esc(item.role || "assistant")}</div>
                <div style="white-space:pre-wrap;">${esc(item.content || "")}</div>
            </div>
        `).join("");
        box.scrollTop = box.scrollHeight;
    }

    async function loadHistory() {
        persistSettings();
        const sessionId = encodeURIComponent(getSession());
        const res = await fetch(`/api/assistant/history?session_id=${sessionId}`);
        const data = await res.json();
        renderHistory(data.history || []);
    }

    async function clearHistory() {
        persistSettings();
        const sessionId = encodeURIComponent(getSession());
        await fetch(`/api/assistant/history?session_id=${sessionId}`, { method: "DELETE" });
        await loadHistory();
        document.getElementById("assistantStatus").textContent = "History cleared";
    }

    async function send() {
        persistSettings();
        const input = document.getElementById("assistantInput");
        const message = input.value.trim();
        if (!message) return;
        document.getElementById("assistantStatus").textContent = "Thinking...";
        try {
            const res = await fetch("/api/assistant/llm-chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    message,
                    api_key: document.getElementById("assistantApiKey").value.trim(),
                    provider: document.getElementById("assistantProvider").value.trim() || "gemini",
                    model: document.getElementById("assistantModel").value.trim() || "gemini-3-flash-preview",
                    session_id: getSession(),
                    scope: { limit: 120 }
                })
            });
            const data = await res.json();
            renderHistory(data.history || []);
            input.value = "";
            document.getElementById("assistantStatus").textContent = data.warning ? "Fallback used" : `Mode: ${data.mode}`;
        } catch (err) {
            document.getElementById("assistantStatus").textContent = `Error: ${err.message}`;
        }
    }

    function bind() {
        const panel = document.getElementById("assistantPanel");
        document.getElementById("assistantFab").addEventListener("click", async () => {
            panel.classList.toggle("open");
            if (panel.classList.contains("open")) await loadHistory();
        });
        document.getElementById("assistantClose").addEventListener("click", () => panel.classList.remove("open"));
        document.getElementById("assistantSend").addEventListener("click", send);
        document.getElementById("assistantInput").addEventListener("keydown", (e) => {
            if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                send();
            }
        });
        document.getElementById("assistantReload").addEventListener("click", loadHistory);
        document.getElementById("assistantClear").addEventListener("click", clearHistory);
        ["assistantApiKey", "assistantModel", "assistantProvider", "assistantSession"].forEach((id) => {
            document.getElementById(id).addEventListener("change", persistSettings);
            document.getElementById(id).addEventListener("blur", persistSettings);
        });
        document.getElementById("assistantProvider").addEventListener("change", () => {
            applyProviderDefaultModel(true);
            persistSettings();
        });
    }

    document.addEventListener("DOMContentLoaded", () => {
        ensureUi();
        restoreSettings();
        bind();
    });
})();
