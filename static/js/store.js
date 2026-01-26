
// Video Store Logic

let storeState = {
    categories: [],
    filters: {},
    currentSearch: {
        query: '',
        thematic: '',
        genre: '',
        length: '',
        author_type: '',
        sort: 'newest',
        page: 1
    },
    isLoading: false
};

// Initialize Store
async function initStore() {
    await Promise.all([
        loadStoreCategories(),
        loadStoreFilters()
    ]);
    performStoreSearch(); // Load initial results
}

async function loadStoreCategories() {
    try {
        const response = await fetch('/api/store/categories');
        const data = await response.json();
        storeState.categories = data.categories;
        renderCategories();
    } catch (error) {
        console.error('Failed to load categories:', error);
    }
}

async function loadStoreFilters() {
    try {
        const response = await fetch('/api/store/filters');
        const data = await response.json();
        storeState.filters = data;
        renderFilterOptions();
    } catch (error) {
        console.error('Failed to load filters:', error);
    }
}

function renderCategories() {
    const container = document.getElementById('storeCategories');
    if (!container) return;

    container.innerHTML = storeState.categories.map(cat => `
        <div class="category-card ${storeState.currentSearch.thematic === cat.id ? 'active' : ''}" 
             onclick="selectCategory('${cat.id}')">
            <div class="category-icon">${cat.icon}</div>
            <div class="category-name">${cat.name}</div>
            <div class="category-count">${cat.count} videos</div>
        </div>
    `).join('');
}

function renderFilterOptions() {
    const genreSelect = document.getElementById('storeGenre');
    const lengthSelect = document.getElementById('storeLength');
    const authorSelect = document.getElementById('storeAuthor');

    if (storeState.filters.genres) {
        storeState.filters.genres.forEach(g => genreSelect.add(new Option(g, g)));
    }
    if (storeState.filters.lengths) {
        storeState.filters.lengths.forEach(l => lengthSelect.add(new Option(l, l)));
    }
    if (storeState.filters.author_types) {
        storeState.filters.author_types.forEach(a => authorSelect.add(new Option(a, a)));
    }
}

function selectCategory(id) {
    // Toggle
    if (storeState.currentSearch.thematic === id) {
        storeState.currentSearch.thematic = '';
    } else {
        storeState.currentSearch.thematic = id;
    }
    renderCategories(); // Re-render to show active state
    storeState.currentSearch.page = 1;
    performStoreSearch();
}

async function performStoreSearch() {
    if (storeState.isLoading) return;
    storeState.isLoading = true;

    updateStoreUIState();

    try {
        const params = new URLSearchParams({
            q: storeState.currentSearch.query,
            thematic: storeState.currentSearch.thematic,
            genre: storeState.currentSearch.genre,
            length: storeState.currentSearch.length,
            author_type: storeState.currentSearch.author_type,
            sort: storeState.currentSearch.sort,
            page: storeState.currentSearch.page
        });

        const response = await fetch(`/api/store/search?${params}`);
        const data = await response.json();

        renderStoreResults(data);
    } catch (error) {
        console.error('Store search failed:', error);
    } finally {
        storeState.isLoading = false;
        updateStoreUIState();
    }
}

function renderStoreResults(data) {
    const grid = document.getElementById('storeGrid');
    document.getElementById('storeTotalCount').textContent = `${data.total} results`;

    if (!data.videos || data.videos.length === 0) {
        grid.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">🏪</div>
                <p>No videos found matching your filters.</p>
            </div>
        `;
        return;
    }

    grid.innerHTML = data.videos.map(video => renderStoreVideoCard(video)).join('');
}

function renderStoreVideoCard(video) {
    const meta = video.metadata || {};
    const thumb = video.thumbnail || `https://i.ytimg.com/vi/${video.video_id}/mqdefault.jpg`;

    // Safety checks
    const thematic = (meta.thematic && meta.thematic.primary) ? meta.thematic.primary : "";
    const genre = (meta.genre && meta.genre.primary) ? meta.genre.primary : "";

    return `
        <div class="video-card" onclick="window.open('${video.url}', '_blank')">
            <div class="video-thumbnail">
                <img src="${thumb}" loading="lazy" alt="${video.title}">
                <div class="duration-badge">${formatDuration(video.duration)}</div>
            </div>
            <div class="video-info">
                <div class="video-card-title">${video.title}</div>
                <div class="video-channel">${video.channel}</div>
                <div class="video-meta-tags">
                    ${thematic ? `<span class="meta-tag theme">${thematic}</span>` : ''}
                    ${genre ? `<span class="meta-tag genre">${genre}</span>` : ''}
                </div>
            </div>
        </div>
    `;
}

function updateStoreUIState() {
    const loader = document.getElementById('storeLoader');
    if (storeState.isLoading) {
        loader.style.display = 'block';
    } else {
        loader.style.display = 'none';
    }
}

// Event Listeners
document.getElementById('storeSearchInput')?.addEventListener('input', (e) => {
    storeState.currentSearch.query = e.target.value;
    // Debounce?
    clearTimeout(window.searchDebounce);
    window.searchDebounce = setTimeout(() => {
        storeState.currentSearch.page = 1;
        performStoreSearch();
    }, 500);
});

['storeGenre', 'storeLength', 'storeAuthor', 'storeSort'].forEach(id => {
    document.getElementById(id)?.addEventListener('change', (e) => {
        const key = id.replace('store', '').toLowerCase();
        // handling special key mapping if needed, e.g. storeAuthor -> author_type
        let paramKey = key;
        if (key === 'author') paramKey = 'author_type';

        storeState.currentSearch[paramKey] = e.target.value;
        storeState.currentSearch.page = 1;
        performStoreSearch();
    });
});

// Init on load if tab active, or when tab switched
// We can hook into existing tab switch logic in app.js if needed
