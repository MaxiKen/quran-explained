# quran-explained

Quran explained verse by verse.

This repository contains a static Quran reader. Arabic text, English translation, themes, and audio references are stored in `data/chapter_NNN.js`; the reader interface is in `index.html`, `css/`, and `js/`.

Commentary is not currently included. Chapters without a commentary payload show the app's “coming soon” note. The source tafsir collections remain in the `tafsir-*/` directories and `tafsir_initial/`.

## Run locally

Serve the repository with a static HTTP server (for example, `python3 -m http.server`) and open the served address. The app uses fetches and a service worker, so it should be served over HTTP rather than opened with `file://`.
