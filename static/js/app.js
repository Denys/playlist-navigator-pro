// Unified Playlist Manager JavaScript

let selectedColor = 'purple';
let allVideos = [];
let allPlaylists = [];

// ==================== Tab Navigation ====================

document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', function () {
        const tabName = this.dataset.tab;
        switchTab(tabName);
    });
});

function switchTab(tabName) {
    // Update buttons
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

    // Update content
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    document.getElementById(`${tabName}-tab`).classList.add('active');

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

function switchToSearch() {
    switchTab('search');
}

// ==================== Playlists Tab ====================

async function loadPlaylistsGrid() {
    try {
        const response = await fetch('/api/playlists');
        const data = await response.json();

        const grid = document.getElementById('playlistsGrid');
        const subtitle = document.getElementById('playlistsSubtitle');

        if (!data.playlists || data.playlists.length === 0) {
            grid.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">📚</div>
                    <p>No playlists indexed yet</p>
                    <p style="font-size: 14px; color: #999; margin-top: 10px;">
                        Go to "YouTube Indexer" tab to index your first playlist
                    </p>
                </div>
            `;
            return;
        }

        subtitle.textContent = `${data.total_playlists} playlists with ${data.total_videos} videos`;

        // Build grid
        let html = '';
        data.playlists.forEach(playlist => {
            const date = new Date(playlist.created_at).toLocaleDateString();
            const colorClass = playlist.color_scheme || 'purple';

            html += `
                <div class="playlist-card" onclick="openPlaylistDetails('${playlist.id}')">
                    <div class="playlist-card-header">
                        <h3>${playlist.name}</h3>
                        <span class="playlist-card-badge">${playlist.video_count}</span>
                    </div>
                    <div class="playlist-card-meta">
                        <span>🎨 ${colorClass.charAt(0).toUpperCase() + colorClass.slice(1)}</span>
                        <span>📅 ${date}</span>
                        <span>🔗 <a href="${playlist.youtube_url}" target="_blank" onclick="event.stopPropagation()">YouTube</a></span>
                    </div>
                </div>
            `;
        });

        grid.innerHTML = html;

    } catch (error) {
        console.error('Failed to load playlists:', error);
    }
}

async function openPlaylistDetails(playlistId) {
    try {
        // Store current playlist ID for sharing
        window.currentPlaylistId = playlistId;

        // Get playlist info
        const response = await fetch('/api/playlists');
        const data = await response.json();
        const playlist = data.playlists.find(p => p.id === playlistId);

        if (!playlist) {
            alert('Playlist not found');
            return;
        }

        // Load video data
        const videosResp = await fetch(`/api/search?playlist=${playlistId}&q=`);
        const videosData = await videosResp.json();

        // Update header
        document.getElementById('detailPlaylistName').textContent = playlist.name;
        document.getElementById('detailVideoCount').textContent = `${playlist.video_count} videos`;
        document.getElementById('detailCreatedAt').textContent = `Created: ${new Date(playlist.created_at).toLocaleString()}`;
        document.getElementById('detailYouTubeLink').href = playlist.youtube_url;

        // Build video list
        const videoList = document.getElementById('playlistVideoList');
        let videosHtml = '';

        videosData.results.forEach((video, index) => {
            const description = video.description || 'No description available';
            const truncatedDesc = description.substring(0, 200);

            videosHtml += `
                <div class="video-item">
                    <div class="video-item-title">
                        <span style="color: #999; margin-right: 10px;">${index + 1}.</span>
                        <a href="${video.url}" target="_blank">🎥 ${video.title}</a>
                    </div>
                    <div class="video-item-meta">
                        <span>👤 ${video.channel}</span>
                        ${video.category ? `<span>📂 ${video.category}</span>` : ''}
                    </div>
                    <div class="video-item-description">
                        ${truncatedDesc}${description.length > 200 ? '...' : ''}
                    </div>
                    ${video.tags && video.tags.length > 0 ? `
                        <div class="video-item-tags">
                            ${video.tags.slice(0, 5).map(tag => `<span class="tag">${tag}</span>`).join('')}
                        </div>
                    ` : ''}
                </div>
            `;
        });

        videoList.innerHTML = videosHtml;

        // Show detail view, hide grid
        document.getElementById('playlistsView').style.display = 'none';
        document.getElementById('playlistDetails').style.display = 'block';

    } catch (error) {
        console.error('Failed to load playlist details:', error);
        alert('Failed to load playlist details');
    }
}

function closePlaylistDetails() {
    document.getElementById('playlistsView').style.display = 'block';
    document.getElementById('playlistDetails').style.display = 'none';
}

function copyShareLink() {
    if (!window.currentPlaylistId) {
        alert('No playlist selected');
        return;
    }

    const shareUrl = `${window.location.origin}/share/${window.currentPlaylistId}`;

    navigator.clipboard.writeText(shareUrl).then(() => {
        // Show toast notification
        const btn = document.getElementById('shareBtn');
        const originalText = btn.textContent;
        btn.textContent = '✅ Copied!';
        btn.style.background = '#4caf50';

        setTimeout(() => {
            btn.textContent = originalText;
            btn.style.background = '';
        }, 2000);
    }).catch(err => {
        // Fallback for older browsers
        prompt('Copy this link:', shareUrl);
    });
}

function exportToExcel() {
    if (!window.currentPlaylistId) {
        alert('No playlist selected');
        return;
    }

    const btn = document.getElementById('exportBtn');
    const originalText = btn.textContent;
    btn.textContent = '⏳ Exporting...';
    btn.disabled = true;

    // Direct download - browser will use Content-Disposition header for filename
    const downloadUrl = `/api/export/excel?playlist=${encodeURIComponent(window.currentPlaylistId)}`;

    // Use anchor tag - the most standard HTML5 way
    // This allows us to set a client-side filename hint via the 'download' attribute
    const link = document.createElement('a');
    link.href = downloadUrl;
    // Set default filename hint (browser uses this if headers fail)
    link.download = `${window.currentPlaylistId || 'playlist'}_export.xlsx`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    // Success feedback
    setTimeout(() => {
        btn.textContent = '✅ Download Started';
        btn.style.background = '#4caf50';

        setTimeout(() => {
            btn.textContent = originalText;
            btn.style.background = '';
            btn.disabled = false;
        }, 2000);
    }, 1000);
}

// ==================== Indexer Tab ====================

// Color scheme selection
document.querySelectorAll('.color-option').forEach(btn => {
    btn.addEventListener('click', function () {
        document.querySelectorAll('.color-option').forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        selectedColor = this.dataset.color;
    });
});

// Form submission
document.getElementById('indexForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const playlistUrl = document.getElementById('playlistUrl').value;
    const playlistName = document.getElementById('playlistName').value;

    // Show status panel
    document.getElementById('statusPanel').style.display = 'block';
    document.getElementById('resultsPanel').style.display = 'none';
    document.getElementById('submitBtn').disabled = true;

    try {
        // Start indexing
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

        // Monitor progress
        monitorProgress(data.job_id);

    } catch (error) {
        showError(error.message);
    }
});

// Monitor job progress via SSE
function monitorProgress(jobId) {
    const eventSource = new EventSource(`/api/status/${jobId}`);

    eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);

        // Update UI
        document.getElementById('statusMessage').textContent = data.message;
        document.getElementById('progressFill').style.width = `${data.progress}%`;
        document.getElementById('progressText').textContent = `${data.progress}%`;

        // Update quota
        if (data.quota_used) {
            updateQuota(-data.quota_used);
        }

        // Handle completion
        if (data.status === 'complete') {
            eventSource.close();
            showResults(data.files);
            document.getElementById('submitBtn').disabled = false;
            updateStats();
        } else if (data.status === 'error') {
            eventSource.close();
            showError(data.message);
            document.getElementById('submitBtn').disabled = false;
        }
    };

    eventSource.onerror = () => {
        eventSource.close();
        showError('Connection lost');
        document.getElementById('submitBtn').disabled = false;
    };
}

// Show results
function showResults(files) {
    const resultsPanel = document.getElementById('resultsPanel');
    const filesList = document.getElementById('filesList');

    filesList.innerHTML = files.map(file => {
        const fileName = file.split('/').pop();
        return `
            <div class="file-item">
                <span>📄 ${fileName}</span>
                <a href="/${file}" target="_blank">Open</a>
            </div>
        `;
    }).join('');

    resultsPanel.style.display = 'block';
}

// Show error
function showError(message) {
    document.getElementById('statusMessage').textContent = `Error: ${message}`;
    document.getElementById('statusMessage').style.color = 'red';
}

// ==================== Search Tab ====================

async function loadSearchData() {
    try {
        // Load playlist info
        const response = await fetch('/api/playlists');
        const data = await response.json();

        allPlaylists = data.playlists || [];

        // Update subtitle
        document.getElementById('searchSubtitle').textContent =
            `Search across ${data.total_playlists || 0} playlists with ${data.total_videos || 0} videos`;

        // Populate playlist filter
        const playlistFilter = document.getElementById('playlistFilter');
        playlistFilter.innerHTML = '<option value="">All Playlists</option>';

        allPlaylists.forEach(playlist => {
            const option = document.createElement('option');
            option.value = playlist.id;
            option.textContent = `${playlist.name} (${playlist.video_count})`;
            playlistFilter.appendChild(option);
        });

    } catch (error) {
        console.error('Failed to load search data:', error);
    }
}

// Search functionality
document.getElementById('searchBtn').addEventListener('click', performSearch);
document.getElementById('searchInput').addEventListener('keyup', (e) => {
    if (e.key === 'Enter') performSearch();
});

// Auto-search on input
let searchTimeout;
document.getElementById('searchInput').addEventListener('input', () => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(performSearch, 400);
});

// Filter change
document.getElementById('playlistFilter').addEventListener('change', performSearch);
document.getElementById('categoryFilter').addEventListener('change', performSearch);

async function performSearch() {
    const query = document.getElementById('searchInput').value.trim();
    const playlistFilter = document.getElementById('playlistFilter').value;
    const categoryFilter = document.getElementById('categoryFilter').value;

    if (!query && !playlistFilter && !categoryFilter) {
        document.getElementById('searchResults').innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">🔍</div>
                <p>Type to search across all playlists</p>
            </div>
        `;
        return;
    }

    try {
        const params = new URLSearchParams({
            q: query,
            playlist: playlistFilter,
            category: categoryFilter
        });

        const response = await fetch(`/api/search?${params}`);
        const data = await response.json();

        displaySearchResults(data.results, data.total, query);

    } catch (error) {
        console.error('Search failed:', error);
    }
}

// Export Search Results
document.getElementById('searchExportBtn').addEventListener('click', exportSearchResults);

function exportSearchResults() {
    const query = document.getElementById('searchInput').value.trim();
    const playlistFilter = document.getElementById('playlistFilter').value;
    const categoryFilter = document.getElementById('categoryFilter').value;

    const btn = document.getElementById('searchExportBtn');
    const originalText = btn.textContent;
    btn.textContent = '⏳ Exporting...';
    btn.disabled = true;

    // Construct params
    const params = new URLSearchParams();
    if (query) params.append('q', query);
    if (playlistFilter) params.append('playlist', playlistFilter);
    if (categoryFilter) params.append('category', categoryFilter);

    // Direct download
    const downloadUrl = `/api/export/excel?${params.toString()}`;

    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = 'search_results.xlsx'; // Browser hint
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    // Success feedback
    setTimeout(() => {
        btn.textContent = '✅ Download Started';
        btn.style.background = '#4caf50';
        btn.style.color = 'white';

        setTimeout(() => {
            btn.textContent = originalText;
            btn.style.background = '';
            btn.style.color = '';
            btn.disabled = false;
        }, 2000);
    }, 1000);
}

function displaySearchResults(results, total, query) {
    const container = document.getElementById('searchResults');

    if (!results || results.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">😕</div>
                <p>No results found</p>
            </div>
        `;
        return;
    }

    const playlistCount = new Set(results.map(v => v.playlist_id)).size;

    let html = `<p class="results-count">Found ${total} results across ${playlistCount} playlists${results.length < total ? ` (showing first ${results.length})` : ''}</p>`;

    results.forEach(video => {
        const description = video.description || 'No description available';
        const truncatedDesc = description.substring(0, 200);

        html += `
            <div class="video-result">
                <div class="video-title">
                    <a href="${video.url}" target="_blank">📺 ${highlightText(video.title, query)}</a>
                </div>
                <div class="video-meta">
                    <span>📁 ${video.playlist_name}</span>
                    <span>👤 ${video.channel}</span>
                    ${video.category ? `<span>📂 ${video.category}</span>` : ''}
                </div>
                <div class="video-description">
                    ${highlightText(truncatedDesc, query)}${description.length > 200 ? '...' : ''}
                </div>
                ${video.tags && video.tags.length > 0 ? `
                    <div class="video-tags">
                        ${video.tags.slice(0, 5).map(tag => `<span class="tag">${tag}</span>`).join('')}
                    </div>
                ` : ''}
            </div>
        `;
    });

    container.innerHTML = html;
}

function highlightText(text, query) {
    if (!query) return text;
    const regex = new RegExp(`(${escapeRegex(query)})`, 'gi');
    return text.replace(regex, '<mark>$1</mark>');
}

function escapeRegex(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

// ==================== Quota & Stats ====================

async function fetchQuota() {
    try {
        const response = await fetch('/api/quota');
        const data = await response.json();

        const quotaEl = document.getElementById('quotaRemaining');
        quotaEl.textContent = `${data.remaining.toLocaleString()} / ${data.total.toLocaleString()}`;

        // Color code
        if (data.remaining < 1000) {
            quotaEl.style.color = '#e74c3c';
        } else if (data.remaining < 3000) {
            quotaEl.style.color = '#f39c12';
        } else {
            quotaEl.style.color = '#27ae60';
        }
    } catch (error) {
        console.error('Failed to fetch quota:', error);
    }
}

function updateQuota(delta) {
    // Update would happen here in real implementation
    fetchQuota();
}

async function updateStats() {
    try {
        const response = await fetch('/api/playlists');
        const data = await response.json();

        document.getElementById('statsInfo').textContent =
            `${data.total_playlists || 0} playlists | ${data.total_videos || 0} videos`;
    } catch (error) {
        console.error('Failed to update stats:', error);
    }
}

// Initialize
fetchQuota();
updateStats();
setInterval(fetchQuota, 30000); // Refresh quota every 30 seconds
setInterval(updateStats, 60000); // Refresh stats every minute

// ==================== Video Gallery Tab ====================

let galleryVideos = [];
let filteredGalleryVideos = [];

async function loadVideoGallery() {
    try {
        const response = await fetch('/api/videos/all');
        const data = await response.json();

        galleryVideos = data.videos;
        filteredGalleryVideos = [...galleryVideos];

        // Populate playlist filter
        const playlistFilter = document.getElementById('galleryPlaylistFilter');
        data.playlists.forEach(playlist => {
            const option = document.createElement('option');
            option.value = playlist;
            option.textContent = playlist.replace(/_/g, ' ').toUpperCase();
            playlistFilter.appendChild(option);
        });

        // Update subtitle
        document.getElementById('gallerySubtitle').textContent =
            `Browse ${data.total_count} videos from ${data.playlists.length} playlists`;

        renderGallery();
    } catch (error) {
        console.error('Failed to load gallery:', error);
        document.getElementById('videoGallery').innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">⚠️</div>
                <p>Failed to load videos. Please try again.</p>
            </div>
        `;
    }
}

function renderGallery() {
    const gallery = document.getElementById('videoGallery');

    if (filteredGalleryVideos.length === 0) {
        gallery.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">���</div>
                <p>No videos found</p>
            </div>
        `;
        return;
    }

    gallery.innerHTML = filteredGalleryVideos.map(video => renderVideoCard(video)).join('');
}

function renderVideoCard(video) {
    const thumbnail = video.thumbnail || `https://i.ytimg.com/vi/${video.video_id}/mqdefault.jpg`;
    const duration = formatDuration(video.duration || '');
    const publishDate = formatDate(video.published_at);
    const description = (video.description || '').substring(0, 150);
    const hasMore = (video.description || '').length > 150;

    return `
        <div class="video-card" onclick="window.open('${video.url}', '_blank')">
            <div class="video-thumbnail">
                <img src="${thumbnail}" alt="${video.title}" loading="lazy" 
                     onerror="this.src='data:image/svg+xml,%3Csvg xmlns=\\'http://www.w3.org/2000/svg\\' width=\\'320\\' height=\\'180\\'%3E%3Crect fill=\\'%23f0f0f0\\' width=\\'320\\' height=\\'180\\'/%3E%3Ctext fill=\\'%23999\\' x=\\'50%25\\' y=\\'50%25\\' dominant-baseline=\\'middle\\' text-anchor=\\'middle\\'%3ENo Thumbnail%3C/text%3E%3C/svg%3E'">
                ${duration ? `<div class="duration-badge">${duration}</div>` : ''}
            </div>
            <div class="video-info">
                <div class="video-card-title">${video.title}</div>
                <div class="video-channel">${video.channel}</div>
                <div class="video-gallery-meta">${publishDate}</div>
                ${description ? `
                    <div class="video-card-description collapsed" id="desc-${video.video_id}">
                        ${description}${hasMore ? '...' : ''}
                    </div>
                    ${hasMore ? `<div class="read-more-btn" onclick="event.stopPropagation(); toggleDescription('${video.video_id}')">Read more</div>` : ''}
                ` : ''}
            </div>
        </div>
    `;
}

function formatDuration(isoDuration) {
    if (!isoDuration) return '';
    const match = isoDuration.match(/PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?/);
    if (!match) return '';

    const hours = parseInt(match[1] || 0);
    const minutes = parseInt(match[2] || 0);
    const seconds = parseInt(match[3] || 0);

    if (hours > 0) {
        return `${hours}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
    }
    return `${minutes}:${String(seconds).padStart(2, '0')}`;
}

function formatDate(isoDate) {
    if (!isoDate) return '';
    const date = new Date(isoDate);
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
}

function toggleDescription(videoId) {
    const descElement = document.getElementById(`desc-${videoId}`);
    if (descElement) {
        descElement.classList.toggle('collapsed');
    }
}

function filterGallery() {
    const searchTerm = document.getElementById('gallerySearch').value.toLowerCase();
    const playlistFilter = document.getElementById('galleryPlaylistFilter').value;
    const sortBy = document.getElementById('gallerySortBy').value;

    // Filter
    filteredGalleryVideos = galleryVideos.filter(video => {
        const matchesSearch = !searchTerm ||
            video.title.toLowerCase().includes(searchTerm) ||
            (video.channel || '').toLowerCase().includes(searchTerm) ||
            (video.description || '').toLowerCase().includes(searchTerm);

        const matchesPlaylist = !playlistFilter || video.playlist_id === playlistFilter;

        return matchesSearch && matchesPlaylist;
    });

    // Sort
    filteredGalleryVideos.sort((a, b) => {
        switch (sortBy) {
            case 'newest':
                return new Date(b.published_at) - new Date(a.published_at);
            case 'oldest':
                return new Date(a.published_at) - new Date(b.published_at);
            case 'title':
                return a.title.localeCompare(b.title);
            case 'duration':
                return (b.duration || '').localeCompare(a.duration || '');
            default:
                return 0;
        }
    });

    renderGallery();
}

// Gallery tab event listeners
document.getElementById('gallerySearch')?.addEventListener('input', filterGallery);
document.getElementById('galleryPlaylistFilter')?.addEventListener('change', filterGallery);
document.getElementById('gallerySortBy')?.addEventListener('change', filterGallery);

