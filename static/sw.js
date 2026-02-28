// Playlist Navigator Pro — Service Worker
// Cache version: bump this to invalidate all caches
const CACHE_VERSION = 'pnav-v1';
const STATIC_CACHE = `${CACHE_VERSION}-static`;
const API_CACHE = `${CACHE_VERSION}-api`;

// Static assets to precache on install
const PRECACHE_URLS = [
    '/',
    '/static/css/style.css',
    '/static/css/liquid-theme.css',
    '/static/css/liquid-components.css',
    '/static/css/liquid-responsive.css',
    '/static/js/app.js',
    '/static/js/liquid-integration.js',
    '/static/js/mindmap.js',
    '/static/js/store.js',
    '/static/icons/icon-192.png',
    '/static/icons/icon-512.png',
    '/static/manifest.json',
    '/offline'
];

// ==================== Install ====================
self.addEventListener('install', event => {
    console.log('[SW] Installing...');
    event.waitUntil(
        caches.open(STATIC_CACHE)
            .then(cache => cache.addAll(PRECACHE_URLS))
            .then(() => self.skipWaiting())
    );
});

// ==================== Activate ====================
self.addEventListener('activate', event => {
    console.log('[SW] Activating...');
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames
                    .filter(name => name !== STATIC_CACHE && name !== API_CACHE)
                    .map(name => {
                        console.log('[SW] Deleting old cache:', name);
                        return caches.delete(name);
                    })
            );
        }).then(() => self.clients.claim())
    );
});

// ==================== Fetch ====================
self.addEventListener('fetch', event => {
    const { request } = event;
    const url = new URL(request.url);

    // Skip non-GET requests
    if (request.method !== 'GET') return;

    // Skip Chrome extension requests and other non-http
    if (!url.protocol.startsWith('http')) return;

    // API requests: network-first, cache fallback
    if (url.pathname.startsWith('/api/')) {
        event.respondWith(networkFirstWithCache(request, API_CACHE));
        return;
    }

    // Static assets and app shell: cache-first, network fallback
    if (url.pathname.startsWith('/static/') || url.pathname === '/') {
        event.respondWith(cacheFirstWithNetwork(request, STATIC_CACHE));
        return;
    }

    // External CDNs (Tailwind, D3, Google Fonts): cache-first
    if (url.hostname !== location.hostname) {
        event.respondWith(cacheFirstWithNetwork(request, STATIC_CACHE));
        return;
    }

    // Everything else: network-first with offline fallback
    event.respondWith(networkFirstWithOffline(request));
});

// ==================== Strategies ====================

async function cacheFirstWithNetwork(request, cacheName) {
    const cached = await caches.match(request);
    if (cached) return cached;

    try {
        const response = await fetch(request);
        if (response.ok) {
            const cache = await caches.open(cacheName);
            cache.put(request, response.clone());
        }
        return response;
    } catch {
        return new Response('Offline', { status: 503 });
    }
}

async function networkFirstWithCache(request, cacheName) {
    try {
        const response = await fetch(request);
        if (response.ok) {
            const cache = await caches.open(cacheName);
            cache.put(request, response.clone());
        }
        return response;
    } catch {
        const cached = await caches.match(request);
        if (cached) return cached;
        return new Response(
            JSON.stringify({ error: 'You are offline and this data is not cached.' }),
            { status: 503, headers: { 'Content-Type': 'application/json' } }
        );
    }
}

async function networkFirstWithOffline(request) {
    try {
        return await fetch(request);
    } catch {
        const cached = await caches.match(request);
        if (cached) return cached;
        // Return offline page for navigation requests
        if (request.mode === 'navigate') {
            const offlinePage = await caches.match('/offline');
            if (offlinePage) return offlinePage;
        }
        return new Response('Offline', { status: 503 });
    }
}
