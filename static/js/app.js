// Playlist Navigator Pro - Stage A + Stage B

const KEYS = {
    theme: "pnp.theme.v1",
    playlistsView: "pnp.view.playlists.v1",
    galleryView: "pnp.view.gallery.v1",
    smartFilter: "pnp.search.smartFilter.v1",
    progressFilter: "pnp.search.progressFilter.v1",
    progressMap: "pnp.progress.map.v1",
    searchHistory: "pnp.search.history.v1",
    savedSearches: "pnp.search.saved.v1",
    activeFolder: "pnp.playlists.activeFolder.v1"
};

const SMART_FILTERS = [
    { id: "all", label: "All", fn: () => true },
    { id: "quick", label: "Quick Watch", fn: (v) => Number(v.duration_seconds || 0) < 300 },
    { id: "coffee", label: "Coffee Break", fn: (v) => {
        const d = Number(v.duration_seconds || 0);
        return d >= 300 && d <= 900;
    } },
    { id: "deep", label: "Deep Dive", fn: (v) => Number(v.duration_seconds || 0) >= 1800 },
    { id: "recent", label: "Recently Added", fn: (v) => {
        const dt = parseDate(v.indexed_at || v.created_at || v.updated_at);
        return !!dt && isWithinDays(dt, 7);
    } }
];

const PROGRESS_STATES = {
    not_started: { label: "Not Started", short: "NS", next: "in_progress" },
    in_progress: { label: "In Progress", short: "IP", next: "completed" },
    completed: { label: "Completed", short: "OK", next: "not_started" }
};

const PROGRESS_FILTERS = [
    { id: "all", label: "All", fn: () => true },
    { id: "not_started", label: "Not Started", fn: (v) => getProgressStatus(v.video_id) === "not_started" },
    { id: "in_progress", label: "In Progress", fn: (v) => getProgressStatus(v.video_id) === "in_progress" },
    { id: "completed", label: "Completed", fn: (v) => getProgressStatus(v.video_id) === "completed" }
];

let selectedColor = "green";
let allVideos = [];
let allPlaylists = [];
let allFolders = [];
let currentSearchResults = [];
let selectedSearchIndex = -1;
let activeSearchFilter = localStorage.getItem(KEYS.smartFilter) || "all";
let activeProgressFilter = localStorage.getItem(KEYS.progressFilter) || "all";
let activeFolderFilter = localStorage.getItem(KEYS.activeFolder) || "all";
let searchHistory = loadLocalArray(KEYS.searchHistory);
let savedSearches = loadLocalArray(KEYS.savedSearches);
let searchTimeout;

function parseDate(value) {
    if (!value) return null;
    const dt = new Date(value);
    return Number.isNaN(dt.getTime()) ? null : dt;
}

function isWithinDays(date, days) {
    const diff = Date.now() - date.getTime();
    return diff >= 0 && diff <= days * 24 * 60 * 60 * 1000;
}

function escapeHtml(str) {
    return String(str ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/\"/g, "&quot;")
        .replace(/'/g, "&#39;");
}

function loadLocalArray(key) {
    try {
        const parsed = JSON.parse(localStorage.getItem(key) || "[]");
        return Array.isArray(parsed) ? parsed : [];
    } catch (_) {
        return [];
    }
}

function saveLocalArray(key, value) {
    localStorage.setItem(key, JSON.stringify(value));
}

function loadProgressMap() {
    try {
        const parsed = JSON.parse(localStorage.getItem(KEYS.progressMap) || "{}");
        return parsed && typeof parsed === "object" ? parsed : {};
    } catch (_) {
        return {};
    }
}

function saveProgressMap(map) {
    localStorage.setItem(KEYS.progressMap, JSON.stringify(map));
}

function getProgressStatus(videoId) {
    const state = loadProgressMap()[String(videoId)] || "not_started";
    return PROGRESS_STATES[state] ? state : "not_started";
}

function cycleProgressStatus(videoId) {
    const map = loadProgressMap();
    const current = getProgressStatus(videoId);
    map[String(videoId)] = PROGRESS_STATES[current].next;
    saveProgressMap(map);
}

function getNotesKey(videoId) {
    return `pnp.notes.${videoId}`;
}

function getVideoNotes(video) {
    const local = localStorage.getItem(getNotesKey(video.video_id));
    if (local !== null) return local;
    return String(video.notes || "");
}

async function persistVideoNotes(videoId, notes) {
    const safe = String(notes || "");
    localStorage.setItem(getNotesKey(videoId), safe);
    try {
        await fetch(`/api/videos/${encodeURIComponent(videoId)}/notes`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ notes: safe })
        });
    } catch (error) {
        console.error("Failed to sync notes", error);
    }
}

function injectStyles() {
    if (document.getElementById("stage-ab-styles")) return;
    const style = document.createElement("style");
    style.id = "stage-ab-styles";
    style.textContent = `
        #playlistsGrid.view-list { grid-template-columns: 1fr !important; }
        #videoGallery.view-list { grid-template-columns: 1fr !important; }
        .filter-bar { display:flex; flex-wrap:wrap; gap:8px; margin-bottom:10px; }
        .filter-bar button { border:1px solid rgba(255,255,255,.2); border-radius:999px; padding:6px 12px; font-size:12px; background:rgba(255,255,255,.06); }
        .filter-bar button.active { background:rgba(5,150,105,.26); border-color:rgba(5,150,105,.72); }
        .search-result-item.selected { outline:2px solid rgba(5,150,105,.85); }
        .notes-panel.hidden { display:none; }
    `;
    document.head.appendChild(style);
}

function applyTheme(theme) {
    const safe = theme === "light" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", safe);
    localStorage.setItem(KEYS.theme, safe);
    const icon = document.getElementById("themeToggleIcon");
    if (icon) icon.textContent = safe === "dark" ? "Dark" : "Light";
}

function mountThemeToggle() {
    const row = document.querySelector("header .max-w-7xl .flex.items-center.justify-between");
    if (!row || document.getElementById("themeToggleBtn")) return;
    const btn = document.createElement("button");
    btn.id = "themeToggleBtn";
    btn.className = "nav-btn px-3 py-2 rounded-full text-sm font-medium text-white/80 hover:text-white";
    btn.innerHTML = '<span id="themeToggleIcon">Theme</span>';
    btn.addEventListener("click", () => {
        const current = localStorage.getItem(KEYS.theme) || "dark";
        applyTheme(current === "dark" ? "light" : "dark");
    });
    row.appendChild(btn);
    applyTheme(localStorage.getItem(KEYS.theme) || "dark");
}

function mountViewToggles() {
    const playlistsHeader = document.querySelector("#tab-playlists > .flex.justify-between.items-center");
    if (playlistsHeader && !document.getElementById("playlistsViewToggle")) {
        const el = document.createElement("div");
        el.id = "playlistsViewToggle";
        el.className = "flex gap-2";
        el.innerHTML = `
            <button type="button" data-view="grid" class="view-btn px-3 py-2 rounded-lg border border-white/20 bg-white/10 text-xs">Grid</button>
            <button type="button" data-view="list" class="view-btn px-3 py-2 rounded-lg border border-white/20 bg-white/5 text-xs">List</button>
        `;
        playlistsHeader.appendChild(el);
        el.querySelectorAll("button").forEach((btn) => btn.addEventListener("click", () => setPlaylistsView(btn.dataset.view)));
    }

    const galleryTitle = document.querySelector("#tab-gallery h2");
    if (galleryTitle && !document.getElementById("galleryViewToggle")) {
        const el = document.createElement("div");
        el.id = "galleryViewToggle";
        el.className = "flex gap-2 mb-4";
        el.innerHTML = `
            <button type="button" data-view="grid" class="view-btn px-3 py-2 rounded-lg border border-white/20 bg-white/10 text-xs">Grid</button>
            <button type="button" data-view="list" class="view-btn px-3 py-2 rounded-lg border border-white/20 bg-white/5 text-xs">List</button>
        `;
        galleryTitle.insertAdjacentElement("afterend", el);
        el.querySelectorAll("button").forEach((btn) => btn.addEventListener("click", () => setGalleryView(btn.dataset.view)));
    }

    setPlaylistsView(localStorage.getItem(KEYS.playlistsView) || "grid");
    setGalleryView(localStorage.getItem(KEYS.galleryView) || "grid");
}

function setPlaylistsView(mode) {
    const safe = mode === "list" ? "list" : "grid";
    localStorage.setItem(KEYS.playlistsView, safe);
    document.getElementById("playlistsGrid")?.classList.toggle("view-list", safe === "list");
}

function setGalleryView(mode) {
    const safe = mode === "list" ? "list" : "grid";
    localStorage.setItem(KEYS.galleryView, safe);
    document.getElementById("videoGallery")?.classList.toggle("view-list", safe === "list");
}

function switchTab(tabName) {
    document.querySelectorAll(".nav-btn").forEach((b) => b.classList.toggle("active", b.dataset.tab === tabName));
    document.querySelectorAll(".tab-content").forEach((c) => c.classList.remove("active"));
    document.getElementById(`tab-${tabName}`)?.classList.add("active");

    if (tabName === "search") {
        ensureSearchUi();
    } else if (tabName === "playlists") {
        loadPlaylistsGrid();
    } else if (tabName === "gallery") {
        loadVideoGallery();
    } else if (tabName === "mindmap") {
        loadMindMap();
    }
}

function bindNavigation() {
    document.querySelectorAll(".nav-btn").forEach((btn) => btn.addEventListener("click", () => switchTab(btn.dataset.tab)));
}

function bindColorSelection() {
    document.querySelectorAll(".color-orb").forEach((btn) => {
        btn.addEventListener("click", () => {
            document.querySelectorAll(".color-orb").forEach((b) => {
                b.classList.remove("ring-2", "ring-white", "ring-offset-2", "ring-offset-transparent", "opacity-100");
                b.classList.add("opacity-60");
            });
            btn.classList.remove("opacity-60");
            btn.classList.add("ring-2", "ring-white", "ring-offset-2", "ring-offset-transparent", "opacity-100");
            selectedColor = btn.dataset.color;
        });
    });
}

function bindIndexerForm() {
    document.getElementById("indexForm")?.addEventListener("submit", async (e) => {
        e.preventDefault();
        document.getElementById("statusPanel")?.classList.remove("hidden");
        const playlistUrl = document.getElementById("playlistUrl").value;
        const playlistName = document.getElementById("playlistName").value;
        try {
            const response = await fetch("/api/index", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ playlist_url: playlistUrl, name: playlistName, color_scheme: selectedColor })
            });
            const data = await response.json();
            if (data.error) return showError(data.error);
            monitorProgress(data.job_id);
        } catch (error) {
            showError(error.message);
        }
    });
}

function monitorProgress(jobId) {
    const eventSource = new EventSource(`/api/status/${jobId}`);
    const progressBar = document.getElementById("progressBar");
    const progressText = document.getElementById("progressText");
    const statusMessage = document.getElementById("statusMessage");
    eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (progressBar) progressBar.style.width = `${data.progress}%`;
        if (progressText) progressText.textContent = `${data.progress}%`;
        if (statusMessage) statusMessage.textContent = data.message;
        if (data.status === "complete") {
            eventSource.close();
            if (statusMessage) statusMessage.innerHTML = '<span class="text-green-400">Indexing complete.</span>';
            updateStats();
        } else if (data.status === "error") {
            eventSource.close();
            showError(data.message);
        }
    };
    eventSource.onerror = () => { eventSource.close(); showError("Connection lost"); };
}

function showError(message) {
    const el = document.getElementById("statusMessage");
    if (el) el.innerHTML = `<span class="text-red-400">Error: ${escapeHtml(message)}</span>`;
}

async function loadPlaylistsGrid() {
    try {
        const [playlistsRes, foldersRes] = await Promise.all([fetch("/api/playlists"), fetch("/api/folders")]);
        const playlistsData = await playlistsRes.json();
        const foldersData = await foldersRes.json();
        allPlaylists = Array.isArray(playlistsData.playlists) ? playlistsData.playlists : [];
        allFolders = Array.isArray(foldersData.folders) ? foldersData.folders : [];
        renderFoldersBar();
        renderPlaylists();
    } catch (error) {
        console.error("Failed to load playlists", error);
    }
}

function ensureFoldersBar() {
    let bar = document.getElementById("playlistsFolderSidebar");
    const grid = document.getElementById("playlistsGrid");
    if (!grid) return null;
    if (!bar) {
        bar = document.createElement("div");
        bar.id = "playlistsFolderSidebar";
        bar.className = "glass-card p-4 mb-6";
        grid.parentNode.insertBefore(bar, grid);
    }
    return bar;
}

function renderFoldersBar() {
    const bar = ensureFoldersBar();
    if (!bar) return;
    const folderNames = Array.from(new Set([
        ...allFolders.map((f) => f.name),
        ...allPlaylists.map((p) => (p.folder || "").trim()).filter(Boolean)
    ])).sort((a, b) => a.localeCompare(b));

    const counts = {};
    allPlaylists.forEach((p) => {
        const key = (p.folder || "").trim() || "__none";
        counts[key] = (counts[key] || 0) + 1;
    });

    let html = '<div class="filter-bar">';
    html += `<button type="button" data-folder="all" class="${activeFolderFilter === "all" ? "active" : ""}">All (${allPlaylists.length})</button>`;
    html += `<button type="button" data-folder="__none" class="${activeFolderFilter === "__none" ? "active" : ""}">Unsorted (${counts.__none || 0})</button>`;
    folderNames.forEach((name) => {
        html += `<button type="button" data-folder="${escapeHtml(name)}" class="${activeFolderFilter === name ? "active" : ""}">${escapeHtml(name)} (${counts[name] || 0})</button>`;
    });
    html += "</div>";
    bar.innerHTML = html;

    bar.querySelectorAll("button[data-folder]").forEach((btn) => {
        btn.addEventListener("click", () => {
            activeFolderFilter = btn.dataset.folder || "all";
            localStorage.setItem(KEYS.activeFolder, activeFolderFilter);
            renderFoldersBar();
            renderPlaylists();
        });
    });
}

function renderPlaylists() {
    const grid = document.getElementById("playlistsGrid");
    if (!grid) return;

    let playlists = allPlaylists;
    if (activeFolderFilter !== "all") {
        if (activeFolderFilter === "__none") {
            playlists = allPlaylists.filter((p) => !(p.folder || "").trim());
        } else {
            playlists = allPlaylists.filter((p) => (p.folder || "").trim() === activeFolderFilter);
        }
    }

    if (!playlists.length) {
        grid.innerHTML = '<div class="col-span-full text-center py-20"><h3 class="text-xl font-semibold text-white mb-2">No playlists in this folder</h3></div>';
        return;
    }

    const folderOptions = Array.from(new Set([
        ...allFolders.map((f) => f.name),
        ...allPlaylists.map((p) => (p.folder || "").trim()).filter(Boolean)
    ])).sort((a, b) => a.localeCompare(b));

    const optionsHtml = ['<option value="">Unsorted</option>']
        .concat(folderOptions.map((name) => `<option value="${escapeHtml(name)}">${escapeHtml(name)}</option>`))
        .join("");

    let html = "";
    playlists.forEach((playlist) => {
        const gradient = {
            purple: "from-purple-600 to-indigo-800",
            teal: "from-teal-500 to-emerald-700",
            blue: "from-blue-500 to-sky-700",
            green: "from-green-500 to-lime-700"
        }[playlist.color_scheme] || "from-emerald-600 to-sky-800";

        html += `
            <div class="video-card glass-card overflow-hidden group">
                <div class="h-32 bg-gradient-to-br ${gradient} cursor-pointer" data-open-playlist="${escapeHtml(playlist.id)}"></div>
                <div class="p-5">
                    <h3 class="text-lg font-semibold text-white mb-1">${escapeHtml(playlist.name)}</h3>
                    <div class="flex justify-between text-sm text-white/60 mb-3">
                        <span>${Number(playlist.video_count || 0)} videos</span>
                        <span>${(playlist.last_updated || playlist.created_at) ? new Date(playlist.last_updated || playlist.created_at).toLocaleDateString() : "-"}</span>
                    </div>
                    <select class="playlist-folder-select w-full px-2 py-2 rounded-lg border border-white/15 bg-black/20 text-sm" data-playlist-id="${escapeHtml(playlist.id)}">
                        ${optionsHtml}
                    </select>
                </div>
            </div>
        `;
    });

    grid.innerHTML = html;
    setPlaylistsView(localStorage.getItem(KEYS.playlistsView) || "grid");

    grid.querySelectorAll("[data-open-playlist]").forEach((el) => {
        el.addEventListener("click", () => window.open(`/playlist/${el.dataset.openPlaylist}`, "_blank"));
    });

    grid.querySelectorAll(".playlist-folder-select").forEach((select) => {
        const playlist = playlists.find((p) => p.id === select.dataset.playlistId);
        if (playlist) select.value = (playlist.folder || "").trim();
        select.addEventListener("change", async () => {
            try {
                await fetch(`/api/playlists/${encodeURIComponent(select.dataset.playlistId)}/folder`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ folder: select.value || null })
                });
                await loadPlaylistsGrid();
            } catch (error) {
                console.error("Failed to set folder", error);
            }
        });
    });
}

function ensureSearchUi() {
    const results = document.getElementById("searchResults");
    if (!results) return;

    if (!document.getElementById("searchControls")) {
        const controls = document.createElement("div");
        controls.id = "searchControls";
        controls.className = "glass-card p-4 text-left mb-4";
        results.parentNode.insertBefore(controls, results);
    }

    if (!document.getElementById("assistantPanel")) {
        const panel = document.createElement("div");
        panel.id = "assistantPanel";
        panel.className = "glass-card p-4 text-left mb-4";
        results.parentNode.insertBefore(panel, results);
    }

    renderSearchControls();
    renderAssistantPanel();
}

function renderSearchControls() {
    const host = document.getElementById("searchControls");
    if (!host) return;

    const smartButtons = SMART_FILTERS.map((f) => `<button type="button" data-smart="${f.id}" class="${activeSearchFilter === f.id ? "active" : ""}">${escapeHtml(f.label)}</button>`).join("");
    const progressButtons = PROGRESS_FILTERS.map((f) => `<button type="button" data-progress="${f.id}" class="${activeProgressFilter === f.id ? "active" : ""}">${escapeHtml(f.label)}</button>`).join("");

    host.innerHTML = `
        <div class="flex flex-wrap items-center gap-3 mb-2">
            <label class="text-xs text-white/70">Logic</label>
            <select id="searchLogic" class="px-2 py-1 rounded-lg border border-white/20 bg-black/20 text-sm">
                <option value="or">OR</option>
                <option value="and">AND</option>
            </select>
            <label class="inline-flex items-center gap-2 text-xs text-white/80">
                <input id="searchInDescription" type="checkbox" checked>
                Search in descriptions
            </label>
            <button id="saveSearchBtn" type="button" class="px-3 py-1.5 rounded-lg border border-white/20 bg-white/10 text-xs">Save Search</button>
        </div>
        <div class="filter-bar">${smartButtons}</div>
        <div class="filter-bar">${progressButtons}</div>
        <div id="savedSearchesBox" class="text-xs text-white/70"></div>
    `;

    host.querySelectorAll("button[data-smart]").forEach((btn) => {
        btn.addEventListener("click", () => {
            activeSearchFilter = btn.dataset.smart || "all";
            localStorage.setItem(KEYS.smartFilter, activeSearchFilter);
            renderSearchControls();
            displaySearchResults(currentSearchResults);
        });
    });

    host.querySelectorAll("button[data-progress]").forEach((btn) => {
        btn.addEventListener("click", () => {
            activeProgressFilter = btn.dataset.progress || "all";
            localStorage.setItem(KEYS.progressFilter, activeProgressFilter);
            renderSearchControls();
            displaySearchResults(currentSearchResults);
        });
    });

    document.getElementById("saveSearchBtn")?.addEventListener("click", () => {
        const q = (document.getElementById("searchInput")?.value || "").trim();
        if (!q) return;
        const name = window.prompt("Saved search name", q);
        if (!name) return;
        const entry = {
            name: name.trim() || q,
            query: q,
            logic: document.getElementById("searchLogic")?.value || "or",
            in_description: !!document.getElementById("searchInDescription")?.checked
        };
        savedSearches = [entry].concat(savedSearches).slice(0, 20);
        saveLocalArray(KEYS.savedSearches, savedSearches);
        renderSavedSearchesBox();
    });

    renderSavedSearchesBox();
}

function renderSavedSearchesBox() {
    const box = document.getElementById("savedSearchesBox");
    if (!box) return;
    if (!savedSearches.length) {
        box.textContent = "No saved searches yet.";
        return;
    }

    box.innerHTML = savedSearches.map((s, i) => `
        <button type="button" class="saved-search-item mr-2 mb-2 px-2 py-1 rounded border border-white/20" data-index="${i}">
            ${escapeHtml(s.name)}
        </button>
    `).join("");

    box.querySelectorAll(".saved-search-item").forEach((btn) => {
        btn.addEventListener("click", () => {
            const item = savedSearches[Number(btn.dataset.index)];
            if (!item) return;
            const input = document.getElementById("searchInput");
            const logic = document.getElementById("searchLogic");
            const inDesc = document.getElementById("searchInDescription");
            if (input) input.value = item.query;
            if (logic) logic.value = item.logic === "and" ? "and" : "or";
            if (inDesc) inDesc.checked = !!item.in_description;
            performSearch();
        });
    });
}

function renderAssistantPanel() {
    const panel = document.getElementById("assistantPanel");
    if (!panel || panel.dataset.ready === "1") return;
    panel.dataset.ready = "1";
    panel.innerHTML = `
        <h3 class="text-sm font-semibold text-white mb-2">Assistant</h3>
        <div class="flex gap-2 mb-2">
            <input id="assistantInput" type="text" class="flex-1 px-3 py-2 rounded-lg border border-white/15 bg-black/20 text-sm" placeholder="Summarize this result set">
            <button id="assistantSend" type="button" class="px-3 py-2 rounded-lg border border-white/20 bg-white/10 text-sm">Ask</button>
        </div>
        <div id="assistantOutput" class="text-sm text-white/80 whitespace-pre-wrap"></div>
    `;
    document.getElementById("assistantSend")?.addEventListener("click", askAssistant);
}

async function askAssistant() {
    const message = (document.getElementById("assistantInput")?.value || "").trim();
    const output = document.getElementById("assistantOutput");
    if (!message || !output) return;

    output.textContent = "Thinking...";
    const query = (document.getElementById("searchInput")?.value || "").trim();

    try {
        const response = await fetch("/api/assistant/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message, scope: { query, limit: 50 } })
        });
        const data = await response.json();
        output.textContent = data.answer || data.error || "No response";
    } catch (_) {
        output.textContent = "Assistant unavailable.";
    }
}

async function performSearch() {
    const query = (document.getElementById("searchInput")?.value || "").trim();
    if (!query) return;

    const logic = document.getElementById("searchLogic")?.value || "or";
    const inDescription = !!document.getElementById("searchInDescription")?.checked;
    const params = new URLSearchParams({ q: query, logic, in_description: String(inDescription) });

    try {
        const response = await fetch(`/api/search?${params.toString()}`);
        const data = await response.json();
        currentSearchResults = Array.isArray(data.results) ? data.results : [];
        searchHistory = [query].concat(searchHistory.filter((q) => q !== query)).slice(0, 20);
        saveLocalArray(KEYS.searchHistory, searchHistory);
        displaySearchResults(currentSearchResults);
    } catch (error) {
        console.error("Search failed", error);
    }
}

function applySearchFilters(results) {
    const smart = SMART_FILTERS.find((f) => f.id === activeSearchFilter) || SMART_FILTERS[0];
    const progress = PROGRESS_FILTERS.find((f) => f.id === activeProgressFilter) || PROGRESS_FILTERS[0];
    return (results || []).filter((v) => smart.fn(v)).filter((v) => progress.fn(v));
}

function displaySearchResults(results) {
    const container = document.getElementById("searchResults");
    if (!container) return;

    selectedSearchIndex = -1;
    const filtered = applySearchFilters(results);

    if (!filtered.length) {
        container.innerHTML = '<div class="text-center py-12 text-white/40"><p>No results found</p></div>';
        return;
    }

    let html = `<p class="text-white/60 mb-4">Found ${filtered.length} results</p>`;

    filtered.forEach((video, idx) => {
        const status = getProgressStatus(video.video_id);
        html += `
            <div class="search-result-item glass-card p-4 mb-3" data-index="${idx}" data-url="${escapeHtml(video.url || "#")}">
                <div class="flex items-start justify-between gap-3">
                    <div class="flex-1">
                        <h4 class="font-medium text-white mb-1">${escapeHtml(video.title || "")}</h4>
                        <p class="text-sm text-white/60">${escapeHtml(video.channel || "")} | ${escapeHtml(video.playlist_name || "")}</p>
                    </div>
                    <div class="flex flex-col gap-2">
                        <button type="button" class="open-btn px-3 py-1 rounded border border-white/20 bg-white/10 text-xs" data-url="${escapeHtml(video.url || "#")}">Open</button>
                        <button type="button" class="progress-btn px-3 py-1 rounded border border-white/20 bg-white/10 text-xs" data-video-id="${escapeHtml(video.video_id)}">${PROGRESS_STATES[status].label}</button>
                        <button type="button" class="notes-toggle px-3 py-1 rounded border border-white/20 bg-white/5 text-xs" data-video-id="${escapeHtml(video.video_id)}">Notes</button>
                    </div>
                </div>
                <div id="notes-${escapeHtml(video.video_id)}" class="notes-panel hidden mt-3">
                    <textarea class="notes-input w-full min-h-[80px] p-2 rounded-lg border border-white/20 bg-black/20 text-sm" data-video-id="${escapeHtml(video.video_id)}">${escapeHtml(getVideoNotes(video))}</textarea>
                    <div class="mt-2 text-right">
                        <button type="button" class="notes-save px-3 py-1 rounded border border-white/20 bg-white/10 text-xs" data-video-id="${escapeHtml(video.video_id)}">Save</button>
                    </div>
                </div>
            </div>
        `;
    });

    container.innerHTML = html;

    container.querySelectorAll(".open-btn").forEach((btn) => btn.addEventListener("click", () => window.open(btn.dataset.url, "_blank")));

    container.querySelectorAll(".progress-btn").forEach((btn) => {
        btn.addEventListener("click", () => {
            cycleProgressStatus(btn.dataset.videoId);
            displaySearchResults(currentSearchResults);
        });
    });

    container.querySelectorAll(".notes-toggle").forEach((btn) => {
        btn.addEventListener("click", () => document.getElementById(`notes-${btn.dataset.videoId}`)?.classList.toggle("hidden"));
    });

    container.querySelectorAll(".notes-save").forEach((btn) => {
        btn.addEventListener("click", async () => {
            const videoId = btn.dataset.videoId;
            const value = container.querySelector(`.notes-input[data-video-id="${videoId}"]`)?.value || "";
            await persistVideoNotes(videoId, value);
        });
    });
}

function bindSearchInput() {
    const input = document.getElementById("searchInput");
    if (!input) return;

    input.addEventListener("keyup", (e) => {
        if (e.key === "Enter") performSearch();
    });

    input.addEventListener("input", () => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(performSearch, 300);
    });
}

async function loadVideoGallery() {
    try {
        const response = await fetch("/api/videos/all");
        const data = await response.json();
        const gallery = document.getElementById("videoGallery");
        if (!gallery) return;

        if (!Array.isArray(data.videos) || !data.videos.length) {
            gallery.innerHTML = '<div class="col-span-full text-center py-20"><h3 class="text-xl font-semibold text-white mb-2">No videos yet</h3></div>';
            return;
        }

        allVideos = data.videos;
        gallery.innerHTML = data.videos.slice(0, 60).map((video) => {
            const thumb = `https://i.ytimg.com/vi/${encodeURIComponent(video.video_id || "")}/mqdefault.jpg`;
            const status = PROGRESS_STATES[getProgressStatus(video.video_id)];
            return `
                <div class="video-card glass-card overflow-hidden group">
                    <div class="relative aspect-video cursor-pointer" data-url="${escapeHtml(video.url || "#")}">
                        <img src="${thumb}" alt="${escapeHtml(video.title || "")}" class="w-full h-full object-cover opacity-80">
                    </div>
                    <div class="p-4">
                        <h4 class="font-medium text-white text-sm line-clamp-2 mb-1">${escapeHtml(video.title || "")}</h4>
                        <p class="text-xs text-white/60 mb-2">${escapeHtml(video.channel || "")}</p>
                        <button type="button" class="gallery-progress-btn px-3 py-1 rounded border border-white/20 bg-white/10 text-xs" data-video-id="${escapeHtml(video.video_id)}">${status.short}</button>
                    </div>
                </div>
            `;
        }).join("");

        gallery.querySelectorAll("[data-url]").forEach((el) => el.addEventListener("click", () => window.open(el.dataset.url, "_blank")));
        gallery.querySelectorAll(".gallery-progress-btn").forEach((btn) => {
            btn.addEventListener("click", () => {
                cycleProgressStatus(btn.dataset.videoId);
                const state = PROGRESS_STATES[getProgressStatus(btn.dataset.videoId)];
                btn.textContent = state.short;
            });
        });

        setGalleryView(localStorage.getItem(KEYS.galleryView) || "grid");
    } catch (error) {
        console.error("Failed to load gallery", error);
    }
}

function loadMindMap() {
    const container = document.getElementById("mindmap");
    if (!container) return;
    container.innerHTML = '<div class="text-center"><p class="text-white/60">Mind map will appear here when you have indexed playlists</p></div>';
}

async function fetchQuota() {
    try { await fetch("/api/quota"); } catch (_) {}
}

async function updateStats() {
    try {
        const response = await fetch("/api/playlists");
        const data = await response.json();
        const stats = document.getElementById("statsInfo");
        if (stats) stats.textContent = `${data.total_playlists || 0} playlists | ${data.total_videos || 0} videos`;
    } catch (_) {}
}

function bindKeyboardShortcuts() {
    document.addEventListener("keydown", (e) => {
        const target = e.target;
        const isInput = target instanceof HTMLElement && (target.tagName === "INPUT" || target.tagName === "TEXTAREA" || target.isContentEditable);

        if (e.key === "/" && !isInput) {
            e.preventDefault();
            switchTab("search");
            document.getElementById("searchInput")?.focus();
            return;
        }

        if (!document.getElementById("tab-search")?.classList.contains("active")) return;

        const items = Array.from(document.querySelectorAll(".search-result-item"));

        if ((e.key === "j" || e.key === "k") && !isInput && items.length) {
            e.preventDefault();
            if (selectedSearchIndex < 0) selectedSearchIndex = 0;
            selectedSearchIndex += (e.key === "j" ? 1 : -1);
            selectedSearchIndex = Math.max(0, Math.min(items.length - 1, selectedSearchIndex));
            items.forEach((el, idx) => el.classList.toggle("selected", idx === selectedSearchIndex));
            items[selectedSearchIndex]?.scrollIntoView({ block: "nearest" });
        }

        if (e.key === "Enter" && !isInput && selectedSearchIndex >= 0) {
            const url = items[selectedSearchIndex]?.dataset.url || "";
            if (url) window.open(url, "_blank");
        }
    });
}

document.addEventListener("DOMContentLoaded", () => {
    injectStyles();
    mountThemeToggle();
    mountViewToggles();
    bindNavigation();
    bindColorSelection();
    bindIndexerForm();
    bindSearchInput();
    bindKeyboardShortcuts();
    ensureSearchUi();
    updateStats();
    fetchQuota();
});
