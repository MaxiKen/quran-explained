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

const CACHE_VERSION = 'quran-reader-v5.1.5-2-89';

// ---- Commentary payloads withdrawn from the server --------------------------
// A cleared or rewritten chapter must not be served to a device from an old
// cache, so these URLs are dropped from every cache when this version activates
// (the chapter downloads themselves are still carried across versions below).
//
// The commentary source itself was replaced: every data/tafsir_NNN.json went
// from Tafsīr as-Saʿdī in Arabic to Tafsīr Ibn Kathīr in English, and the
// payload gained a `ranges` array. That is all 114 files, so rather than listing
// them, RETIRE_ALL_TAFSIR drops every cached tafsir payload on activation.
// Chapter data is untouched and still carries across.
const RETIRE_ALL_TAFSIR = true;
// Chapters 1 and 2 have been rewritten twice since 2026-10-09 (cleared, then
// compiled, then recompiled against the lead rule), so a cached copy of either
// earlier state must not be carried forward by the copy loop in activate. Data
// files are fetched network-first now, so this list is only about copies that a
// previous version already left in a cache.
const RETIRED_PAYLOADS = [
  './data/guidance_001.json',
  './data/guidance_002.json'
];

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

      // Keep chapter downloads when the app shell cache is upgraded. The old
      // implementation removed the whole cache on each release, forcing users
      // to download their saved commentary again.
      for (const name of names) {
        if (name === CACHE_VERSION) continue;
        const oldCache = await caches.open(name);
        const requests = await oldCache.keys();
        for (const request of requests) {
          const url = request.url || '';
          if (!/\/data\/(?:tafsir_|chapter_|guidance_)/.test(url)) continue;
          const response = await oldCache.match(request);
          if (response) await currentCache.put(request, response.clone());
        }
        await caches.delete(name);
      }

      // withdrawn commentary: the copy loop above has already carried anything
      // an old cache held into the current cache, so dropping the URL here is
      // enough to stop a rewritten chapter being served from a stale payload.
      if (RETIRE_ALL_TAFSIR) {
        const carried = await currentCache.keys();
        for (const request of carried) {
          const url = request.url || '';
          if (!/\/data\/tafsir_/.test(url)) continue;
          await currentCache.delete(request);
        }
      }
      for (const url of RETIRED_PAYLOADS) {
        await currentCache.delete(new URL(url, self.location).toString());
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

  /* DATA IS NEVER STALE-BY-DESIGN: the guidance payloads grow verse by verse, and
     a cached copy of data/*.json is indistinguishable from an unpublished
     chapter, so the payload files go to the network first and fall back to the
     cache only when the network is not there. Everything else same-origin keeps
     the cache-first path the offline shell needs. */
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
