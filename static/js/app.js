// Playlist Navigator Pro - Modern Liquid Glass UI JavaScript

let selectedColor = 'purple';
let allVideos = [];
let allPlaylists = [];

// ==================== Tab Navigation ====================

// Handle nav button clicks
document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', function () {
        const tabName = this.dataset.tab;
        switchTab(tabName);
    });
});

function switchTab(tabName) {
    // Update buttons
    document.querySelectorAll('.nav-btn').forEach(b => {
        b.classList.remove('active');
        if (b.dataset.tab === tabName) {
            b.classList.add('active');
        }
    });

    // Update content visibility
    document.querySelectorAll('.tab-content').forEach(c => {
        c.classList.remove('active');
    });
    const tabContent = document.getElementById(`tab-${tabName}`);
    if (tabContent) {
        tabContent.classList.add('active');
    }

    // Load data based on tab
    if (tabName === 'search') {
        loadSearchData();
    } else if (tabName === 'playlists') {
        loadPlaylistsGrid();
    } else if (tabName === 'gallery') {
        loadVideoGallery();
    } else if (tabName === 'mindmap') {
        loadMindMap();
    }
}

// ==================== Color Scheme Selection ====================

document.querySelectorAll('.color-orb').forEach(btn => {
    btn.addEventListener('click', function () {
        // Remove selected state from all
        document.querySelectorAll('.color-orb').forEach(b => {
            b.classList.remove('ring-2', 'ring-white', 'ring-offset-2', 'ring-offset-transparent', 'opacity-100');
            b.classList.add('opacity-60');
        });

        // Add selected state to clicked
        this.classList.remove('opacity-60');
        this.classList.add('ring-2', 'ring-white', 'ring-offset-2', 'ring-offset-transparent', 'opacity-100');

        selectedColor = this.dataset.color;
    });
});

// ==================== Indexer Form ====================

document.getElementById('indexForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();

    const playlistUrl = document.getElementById('playlistUrl').value;
    const playlistName = document.getElementById('playlistName').value;

    // Show progress panel
    const statusPanel = document.getElementById('statusPanel');
    if (statusPanel) {
        statusPanel.classList.remove('hidden');
    }

    try {
        const response = await fetch('/api/index', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                playlist_url: playlistUrl,
                name: playlistName,
                color_scheme: selectedColor
            })
        });

        const data = await response.json();

        if (data.error) {
            showError(data.error);
            return;
        }

        monitorProgress(data.job_id);

    } catch (error) {
        showError(error.message);
    }
});

function monitorProgress(jobId) {
    const eventSource = new EventSource(`/api/status/${jobId}`);
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    const statusMessage = document.getElementById('statusMessage');

    eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (progressBar) progressBar.style.width = `${data.progress}%`;
        if (progressText) progressText.textContent = `${data.progress}%`;
        if (statusMessage) statusMessage.textContent = data.message;

        if (data.status === 'complete') {
            eventSource.close();
            showResults(data.files);
            updateStats();
        } else if (data.status === 'error') {
            eventSource.close();
            showError(data.message);
        }
    };

    eventSource.onerror = () => {
        eventSource.close();
        showError('Connection lost');
    };
}

function showResults(files) {
    const statusMessage = document.getElementById('statusMessage');
    if (statusMessage) {
        statusMessage.innerHTML = '✅ <span class="text-green-400">Indexing Complete!</span>';
    }
}

function showError(message) {
    const statusMessage = document.getElementById('statusMessage');
    if (statusMessage) {
        statusMessage.innerHTML = `❌ <span class="text-red-400">Error: ${message}</span>`;
    }
}

// ==================== Playlists ====================

async function loadPlaylistsGrid() {
    try {
        const response = await fetch('/api/playlists');
        const data = await response.json();

        const grid = document.getElementById('playlistsGrid');
        if (!grid) return;

        if (!data.playlists || data.playlists.length === 0) {
            grid.innerHTML = `
                <div class="col-span-full text-center py-20">
                    <div class="w-24 h-24 mx-auto mb-4 rounded-full bg-purple-500/10 flex items-center justify-center text-5xl">📚</div>
                    <h3 class="text-xl font-semibold text-white mb-2">No playlists yet</h3>
                    <p class="text-white/60">Start by indexing your first YouTube playlist</p>
                </div>
            `;
            return;
        }

        let html = '';
        data.playlists.forEach(playlist => {
            const colorGradient = {
                'purple': 'from-purple-600 to-indigo-800',
                'teal': 'from-teal-500 to-emerald-700',
                'blue': 'from-blue-500 to-sky-700',
                'green': 'from-green-500 to-lime-700'
            }[playlist.color_scheme] || 'from-purple-600 to-indigo-800';

            html += `
                <div class="video-card glass-card overflow-hidden cursor-pointer group" onclick="openPlaylist('${playlist.id}')">
                    <div class="h-32 bg-gradient-to-br ${colorGradient} relative">
                        <div class="absolute inset-0 flex items-center justify-center">
                            <span class="text-6xl opacity-20">📚</span>
                        </div>
                    </div>
                    <div class="p-5">
                        <h3 class="text-lg font-semibold text-white mb-1">${playlist.name}</h3>
                        <div class="flex justify-between text-sm text-white/60">
                            <span>${playlist.video_count} videos</span>
                            <span>${new Date(playlist.created_at).toLocaleDateString()}</span>
                        </div>
                    </div>
                </div>
            `;
        });

        grid.innerHTML = html;

    } catch (error) {
        console.error('Failed to load playlists:', error);
    }
}

function openPlaylist(playlistId) {
    window.open(`/playlist/${playlistId}`, '_blank');
}

// ==================== Search ====================

async function loadSearchData() {
    try {
        const response = await fetch('/api/playlists');
        const data = await response.json();
        allPlaylists = data.playlists || [];
    } catch (error) {
        console.error('Failed to load search data:', error);
    }
}

document.getElementById('searchInput')?.addEventListener('keyup', (e) => {
    if (e.key === 'Enter') performSearch();
});

let searchTimeout;
document.getElementById('searchInput')?.addEventListener('input', () => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(performSearch, 400);
});

async function performSearch() {
    const query = document.getElementById('searchInput').value.trim();
    if (!query) return;

    try {
        const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
        const data = await response.json();
        displaySearchResults(data.results);
    } catch (error) {
        console.error('Search failed:', error);
    }
}

function displaySearchResults(results) {
    const container = document.getElementById('searchResults');
    if (!container) return;

    if (!results || results.length === 0) {
        container.innerHTML = `
            <div class="text-center py-12 text-white/40">
                <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-white/5 flex items-center justify-center text-3xl">😕</div>
                <p>No results found</p>
            </div>
        `;
        return;
    }

    let html = `<p class="text-white/60 mb-4">Found ${results.length} results</p>`;

    results.forEach(video => {
        html += `
            <div class="glass-card p-4 mb-3 hover:bg-white/10 transition-colors cursor-pointer" onclick="window.open('${video.url}', '_blank')">
                <h4 class="font-medium text-white mb-1">${video.title}</h4>
                <p class="text-sm text-white/60">👤 ${video.channel} • 📁 ${video.playlist_name}</p>
            </div>
        `;
    });

    container.innerHTML = html;
}

// ==================== Gallery ====================

async function loadVideoGallery() {
    try {
        const response = await fetch('/api/videos/all');
        const data = await response.json();

        const gallery = document.getElementById('videoGallery');
        if (!gallery) return;

        if (!data.videos || data.videos.length === 0) {
            gallery.innerHTML = `
                <div class="col-span-full text-center py-20">
                    <div class="w-24 h-24 mx-auto mb-4 rounded-full bg-purple-500/10 flex items-center justify-center text-5xl">🎬</div>
                    <h3 class="text-xl font-semibold text-white mb-2">No videos yet</h3>
                    <p class="text-white/60">Index a playlist to see your videos here</p>
                </div>
            `;
            return;
        }

        let html = '';
        data.videos.slice(0, 12).forEach(video => {
            const thumbnail = `https://i.ytimg.com/vi/${video.video_id}/mqdefault.jpg`;
            html += `
                <div class="video-card glass-card overflow-hidden cursor-pointer group" onclick="window.open('${video.url}', '_blank')">
                    <div class="relative aspect-video">
                        <img src="${thumbnail}" alt="${video.title}" class="w-full h-full object-cover opacity-80 group-hover:opacity-100 transition-opacity">
                        <div class="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity bg-black/40">
                            <div class="bg-white/20 p-3 rounded-full backdrop-blur-md border border-white/30">
                                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg>
                            </div>
                        </div>
                    </div>
                    <div class="p-4">
                        <h4 class="font-medium text-white text-sm line-clamp-2 mb-1">${video.title}</h4>
                        <p class="text-xs text-white/60">${video.channel}</p>
                    </div>
                </div>
            `;
        });

        gallery.innerHTML = html;

    } catch (error) {
        console.error('Failed to load gallery:', error);
    }
}

// ==================== Mind Map ====================

function loadMindMap() {
    const container = document.getElementById('mindmap');
    if (!container) return;

    // Placeholder for mind map visualization
    container.innerHTML = `
        <div class="text-center">
            <div class="w-20 h-20 mx-auto mb-4 rounded-full bg-purple-500/10 flex items-center justify-center text-4xl">🧠</div>
            <p class="text-white/60">Mind map will appear here when you have indexed playlists</p>
        </div>
    `;
}

// ==================== Stats & Quota ====================

async function fetchQuota() {
    try {
        const response = await fetch('/api/quota');
        const data = await response.json();
        // Update quota display if element exists
    } catch (error) {
        console.error('Failed to fetch quota:', error);
    }
}

async function updateStats() {
    try {
        const response = await fetch('/api/playlists');
        const data = await response.json();

        const statsEl = document.getElementById('statsInfo');
        if (statsEl) {
            statsEl.textContent = `${data.total_playlists || 0} playlists | ${data.total_videos || 0} videos`;
        }
    } catch (error) {
        console.error('Failed to update stats:', error);
    }
}

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    updateStats();
    fetchQuota();
});
