/* ================================================
   AL-QURAN INTERACTIVE READER — SERVICE WORKER
   ================================================
   Strategy:
   - Pre-cache ONLY core app shell (HTML, CSS, JS, icons)
   - Chapter data files are cached ON FIRST USE (when user opens a chapter)
   - External fonts are cached during install (non-blocking)
   
   This keeps install fast — no downloading 114 chapter files upfront.
   Once a user opens a chapter, its data file is cached automatically
   by the fetch handler for offline use.
   
   CACHE VERSIONING:
   Increment CACHE_VERSION when you update ANY cached file.
================================================ */

const CACHE_VERSION = 'quran-reader-v1.1.1';

// ---- Core app shell — only the files needed for the homepage ----
// Chapter data files are NOT here — they cache on first use.
const CORE_ASSETS = [
  './',
  './index.html',
  './css/styles.css',
  './js/chapters-meta.js',
  './js/app.js',
  './icons/icon-192x192.png',
  './icons/icon-512x512.png',
  './manifest.json'
];

// ---- External fonts — cached during install (non-blocking) ----
const EXTERNAL_ASSETS = [
  'https://fonts.googleapis.com/css2?family=Amiri+Quran&family=Inter:wght@300;400;500;600;700;800&display=swap',
  'https://cdn.jsdelivr.net/gh/nickcisco/kfgqpc-hafs@1.0/font.css',
  'https://cdn.jsdelivr.net/gh/nickcisco/kfgqpc-hafs@1.0/UthmanicHafs_v2-1.woff2',
  'https://cdn.jsdelivr.net/gh/nickcisco/kfgqpc-hafs@1.0/UthmanicHafs_v2-1.woff'
];

/* ================================================
   INSTALL — cache core shell + fonts
================================================ */
self.addEventListener('install', (event) => {
  console.log('[SW] Installing v' + CACHE_VERSION);

  event.waitUntil(
    caches.open(CACHE_VERSION)
      .then((cache) => {
        console.log('[SW] Caching core app shell...');
        return cache.addAll(CORE_ASSETS);
      })
      .then(() => {
        // Cache fonts (non-blocking — failures don't stop install)
        return caches.open(CACHE_VERSION).then((cache) => {
          return Promise.allSettled(
            EXTERNAL_ASSETS.map((url) =>
              cache.add(url).catch((err) => {
                console.warn('[SW] Font cache skip:', url.substring(0, 50), err.message);
              })
            )
          );
        });
      })
      .then(() => {
        console.log('[SW] Install complete - forcing activation');
        return self.skipWaiting();
      })
      .catch((err) => {
        console.error('[SW] Install failed:', err);
      })
  );
});

/* ================================================
   ACTIVATE — clean old caches
================================================ */
self.addEventListener('activate', (event) => {
  console.log('[SW] Activating v' + CACHE_VERSION);
  
  event.waitUntil(
    caches.keys()
      .then((names) => {
        return Promise.all(
          names.map((name) => {
            if (name !== CACHE_VERSION) {
              console.log('[SW] Deleting old cache:', name);
              return caches.delete(name);
            }
          })
        );
      })
      .then(() => {
        console.log('[SW] Claiming clients');
        return self.clients.claim();
      })
  );
});

/* ================================================
   FETCH — serve cached, cache new requests
   ================================================
   Strategy improved:
   - HTML files: Network-first (ensures users get updates)
   - Local assets (CSS, JS, images): Cache-first
   - External (CDN fonts): Network-first with cache fallback
   - Chapter data files: Cache-first (auto-cache on first open)
================================================ */
self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;

  const url = new URL(event.request.url);
  const isExternal = url.origin !== self.location.origin;

  if (isExternal) {
    // External: network-first, cache fallback
    event.respondWith(
      fetch(event.request)
        .then((resp) => {
          if (resp && resp.status === 200) {
            const clone = resp.clone();
            caches.open(CACHE_VERSION).then((c) => c.put(event.request, clone));
          }
          return resp;
        })
        .catch(() => caches.match(event.request))
    );
  } else {
    // Determine if this is a navigation request (HTML)
    const isNavigationRequest = event.request.mode === 'navigate' || 
                                event.request.destination === 'document' ||
                                url.pathname.endsWith('.html') ||
                                url.pathname.endsWith('/');

    if (isNavigationRequest) {
      // HTML: Network-first (so users get updates immediately)
      event.respondWith(
        fetch(event.request)
          .then((resp) => {
            if (resp && resp.status === 200) {
              const clone = resp.clone();
              caches.open(CACHE_VERSION).then((c) => c.put(event.request, clone));
            }
            return resp;
          })
          .catch(() => {
            // If offline, try cache
            return caches.match(event.request).then((cached) => {
              if (cached) return cached;
              
              // If no cache, show offline page
              return new Response(
                `<!DOCTYPE html>
                <html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
                <title>Offline</title>
                <style>body{font-family:sans-serif;background:#0a0f1a;color:#f1f5f9;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0;text-align:center;padding:20px}
                h1{color:#5eead4;font-size:24px}p{color:#94a3b8;line-height:1.6}
                button{background:#0d9488;color:#fff;border:none;padding:12px 32px;border-radius:12px;font-size:16px;cursor:pointer;font-weight:600}</style>
                </head><body><div><div style="font-size:64px;margin-bottom:20px">📖</div>
                <h1>You're Offline</h1><p>Check your connection and try again.</p>
                <button onclick="location.reload()">Try Again</button></div></body></html>`,
                { headers: { 'Content-Type': 'text/html; charset=utf-8' } }
              );
            });
          })
      );
    } else {
      // Local assets (CSS, JS, images, chapter data): cache-first
      // This automatically caches chapter data files on first fetch
      event.respondWith(
        caches.match(event.request)
          .then((cached) => {
            if (cached) return cached;

            return fetch(event.request)
              .then((resp) => {
                if (resp && resp.status === 200) {
                  const clone = resp.clone();
                  caches.open(CACHE_VERSION).then((c) => c.put(event.request, clone));
                }
                return resp;
              })
              .catch((err) => {
                console.warn('[SW] Fetch failed for:', event.request.url, err);
                throw err;
              });
          })
      );
    }
  }
});
