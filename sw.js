/* ================================================
   AL-QURAN INTERACTIVE READER — SERVICE WORKER
   ================================================
   Strategy:
   - Pre-cache core app shell (HTML, CSS, JS, icons) + locally bundled fonts
   - Chapter data files are cached ON FIRST USE (when user opens a chapter)
   - All fonts are bundled locally in /fonts — the app makes NO external
     font requests and renders fully offline

   FIXES:
   - Use relative paths so app works both at domain root and in subfolders
   - Avoid cache.addAll() hard-fail if one asset is missing
   - Provide cached index fallback for navigations
================================================ */

const CACHE_VERSION = 'quran-reader-v1.12.0-2026-10-17';

// ---- What an upgrade carries over from the previous cache ------------------
// Chapter data never changes shape, so it is always carried. The commentary
// payload was replaced wholesale: data/tafsir_NNN.json went from Tafsīr
// as-Saʿdī in Arabic to the eight English sources (v1.8.0), and on
// 2026-10-17 it became Tafsīr al-Ṭabarī in English with the Arabic original
// underneath (v1.11.0) — a different payload, not an addition. The
// data/guidance_NNN.json files (the plain-English commentary) were withdrawn
// on the same day and are no longer carried at all. A device must not keep
// showing a withdrawn copy, so each kind of payload is only carried from
// caches at least as new as the version that introduced its current form. Data
// files are fetched network-first anyway; this only matters for offline reading.
const CARRY_FROM = {
  'chapter_': 'quran-reader-v0',
  'tafsir_': 'quran-reader-v1.11.0'
};

function carriesPayload(cacheName, url) {
  const m = /\/data\/(chapter_|tafsir_)/.exec(url);
  if (!m) return false;
  return cacheName.startsWith('quran-reader-v') && cacheName >= CARRY_FROM[m[1]];
}

// ---- Core app shell — files needed for the homepage + offline fonts ----
const CORE_ASSETS = [
  './',
  './index.html',
  './css/styles.css',
  './js/chapters-meta.js',
  './js/reading-memory.js',
  './js/router.js',
  './js/read-aloud.js',
  './js/app.js',
  './icons/icon-192x192.png',
  './icons/icon-512x512.png',
  './manifest.json',
  './fonts/hafs.18.woff2',
  './fonts/hafs.18.ttf',
  './fonts/AmiriQuran-Regular.ttf',
  './fonts/NotoNaskhArabic-Regular.woff2',
  './fonts/NotoNaskhArabic-Bold.woff2',
  './fonts/Inter-Variable.ttf'
];

// ---- External assets — none: fonts and all static assets are local ----
const EXTERNAL_ASSETS = [];

/* ================================================
   INSTALL — cache core shell + fonts
================================================ */
self.addEventListener('install', (event) => {
  console.log('[SW] Installing v' + CACHE_VERSION);

  event.waitUntil(
    (async () => {
      const cache = await caches.open(CACHE_VERSION);

      // Cache core files one-by-one so one missing file doesn't kill install
      for (const asset of CORE_ASSETS) {
        try {
          await cache.add(asset);
          console.log('[SW] Cached core asset:', asset);
        } catch (err) {
          console.warn('[SW] Failed to cache core asset:', asset, err);
        }
      }

      // Cache any optional external assets (currently none) — non-blocking
      await Promise.allSettled(
        EXTERNAL_ASSETS.map(async (url) => {
          try {
            await cache.add(url);
          } catch (err) {
            console.warn('[SW] Optional asset cache skip:', String(url).substring(0, 80), err.message);
          }
        })
      );

      console.log('[SW] Install complete');
      await self.skipWaiting();
    })().catch((err) => {
      console.error('[SW] Install failed:', err);
    })
  );
});

/* ================================================
   ACTIVATE — clean old caches
================================================ */
self.addEventListener('activate', (event) => {
  event.waitUntil(
    (async () => {
      const names = await caches.keys();
      const currentCache = await caches.open(CACHE_VERSION);

      // Keep downloaded data when the app shell cache is upgraded. The old
      // implementation removed the whole cache on each release, forcing users
      // to download their saved chapters again. See CARRY_FROM for which
      // payloads are carried from which versions.
      for (const name of names) {
        if (name === CACHE_VERSION) continue;
        const oldCache = await caches.open(name);
        const requests = await oldCache.keys();
        for (const request of requests) {
          if (!carriesPayload(name, request.url || '')) continue;
          const response = await oldCache.match(request);
          if (response) await currentCache.put(request, response.clone());
        }
        await caches.delete(name);
      }

      await self.clients.claim();
    })()
  );
});

/* ================================================
   FETCH — serve cached, cache new requests

   Local files (including chapter data): Cache-First
   External (CDN fonts): Network-First with cache fallback
================================================ */
self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;

  const requestUrl = new URL(event.request.url);
  const isExternal = requestUrl.origin !== self.location.origin;

  if (isExternal) {
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
    return;
  }

  /* DATA IS NEVER STALE-BY-DESIGN: a cached copy of data/*.json is
     indistinguishable from a withdrawn or corrected payload, so the data files
     go to the network first and fall back to the cache only when the network is
     not there. Everything else same-origin keeps the cache-first path the
     offline shell needs. */
  if (/\/data\/.*\.json$/.test(requestUrl.pathname)) {
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
    return;
  }

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
          .catch(() => {
            if (event.request.mode === 'navigate') {
              return caches.match('./index.html').then((cachedPage) => {
                if (cachedPage) return cachedPage;

                return new Response(
                  `<!DOCTYPE html>
                  <html>
                  <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width,initial-scale=1.0">
                    <title>Offline</title>
                    <style>
                      body{font-family:sans-serif;background:#0a0f1a;color:#f1f5f9;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0;text-align:center;padding:20px}
                      h1{color:#5eead4;font-size:24px}
                      p{color:#94a3b8;line-height:1.6}
                      button{background:#0d9488;color:#fff;border:none;padding:12px 32px;border-radius:12px;font-size:16px;cursor:pointer;font-weight:600}
                    </style>
                  </head>
                  <body>
                    <div>
                      <div style="font-size:64px;margin-bottom:20px">📖</div>
                      <h1>You're Offline</h1>
                      <p>Check your connection and try again.</p>
                      <button onclick="location.reload()">Try Again</button>
                    </div>
                  </body>
                  </html>`,
                  { headers: { 'Content-Type': 'text/html; charset=utf-8' } }
                );
              });
            }
          });
      })
  );
});
