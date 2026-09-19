/* =========================================================
   READING MEMORY — "continue where you left off"
   ---------------------------------------------------------
   Every screen (home list, a surah, a commentary eBook) owns
   a remembered place. Returning to the *same* screen resumes
   exactly there; opening a *different* screen has no memory
   of its own yet, so it starts at the top.

   Positions are stored as an anchor element + the distance the
   reader had scrolled it past the header, which survives line
   reflow, font-size changes and reloads far better than a raw
   pixel offset.
   ========================================================= */

const SCROLL_MEMORY_KEY = 'quran-reader-scroll-memory';
const SCROLL_MEMORY_TTL = 1000 * 60 * 60 * 24 * 60; /* 60 days */
const SCROLL_MEMORY_MAX = 200;

const ReadingMemory = {
  entries: {},
  ready: false,
  _persistTimer: null,
  _captureTimer: null,

  /* ---------- keys ---------- */
  key(view, surah) {
    if (view === 'commentary' && surah) return `surah-${surah}-commentary`;
    if (view === 'detail' && surah) return `surah-${surah}`;
    return 'home';
  },

  /* ---------- storage ---------- */
  load() {
    if (this.ready) return;
    try {
      const raw = JSON.parse(localStorage.getItem(SCROLL_MEMORY_KEY) || '{}');
      const now = Date.now();
      const fresh = {};
      let changed = false;
      Object.keys(raw || {}).forEach((key) => {
        const entry = raw[key];
        if (!entry || typeof entry !== 'object') { changed = true; return; }
        if (entry.savedAt && now - entry.savedAt > SCROLL_MEMORY_TTL) { changed = true; return; }
        fresh[key] = entry;
      });
      this.entries = fresh;
      if (changed) this.persist(true);
    } catch (err) {
      this.entries = {};
    }
    this.ready = true;
  },

  persist(now = false) {
    const write = () => {
      this._persistTimer = null;
      try {
        const keys = Object.keys(this.entries);
        if (keys.length > SCROLL_MEMORY_MAX) {
          keys.sort((a, b) => (this.entries[b].savedAt || 0) - (this.entries[a].savedAt || 0))
            .slice(SCROLL_MEMORY_MAX)
            .forEach((key) => { delete this.entries[key]; });
        }
        localStorage.setItem(SCROLL_MEMORY_KEY, JSON.stringify(this.entries));
      } catch (err) { /* private mode / quota — memory stays in-session only */ }
    };
    if (now) { if (this._persistTimer) clearTimeout(this._persistTimer); this._persistTimer = null; write(); return; }
    if (this._persistTimer) return;
    this._persistTimer = setTimeout(write, 400);
  },

  get(key) {
    this.load();
    return this.entries[key] || null;
  },

  /** Every remembered place, for progress hints on the chapter list. */
  all() {
    this.load();
    return this.entries;
  },

  set(key, payload) {
    this.load();
    if (!payload) { this.remove(key); return; }
    this.entries[key] = Object.assign({ savedAt: Date.now() }, payload);
    this.persist();
  },

  remove(key) {
    if (!this.entries[key]) return;
    delete this.entries[key];
    this.persist();
  },

  /* ---------- capture ---------- */
  headerHeight() {
    return (document.getElementById('appHeader') || {}).offsetHeight || 60;
  },

  escape(value) {
    return (window.CSS && CSS.escape) ? CSS.escape(value) : String(value).replace(/[^a-zA-Z0-9_-]/g, '\\$&');
  },

  topAnchor(headerH) {
    const anchors = document.querySelectorAll('[data-scroll-anchor]');
    const line = headerH + 8;
    for (const el of anchors) {
      const rect = el.getBoundingClientRect();
      if (rect.bottom > line) {
        return { anchor: el.getAttribute('data-scroll-anchor'), top: Math.round(rect.top - headerH) };
      }
    }
    return null;
  },

  /**
   * Freeze the current scroll place for a screen.
   * @param {string} [key] route key to write (defaults to the live view)
   * @returns {object|null} the stored payload (null when nothing worth remembering)
   */
  capture(key) {
    this.load();
    const routeKey = key || this.key(AppState.currentView, AppState.currentSurah);
    const headerH = this.headerHeight();
    const anchor = this.topAnchor(headerH);
    const y = Math.round(window.scrollY || window.pageYOffset || 0);
    const meta = routeKey === 'home' ? { tab: AppState.homeTab, search: AppState.searchTerm } : null;
    const verse = this.topVerseNum();

    if (y <= 6 && !verse && !meta) {
      this.remove(routeKey);
      return null;
    }
    const payload = {
      anchor: anchor ? anchor.anchor : null,
      top: anchor ? anchor.top : 0,
      y,
      verse,
      docH: document.documentElement.scrollHeight,
      meta,
    };
    this.set(routeKey, payload);
    return payload;
  },

  /** Verse number currently under the header line (surah view or commentary view). */
  topVerseNum() {
    if (AppState.currentView === 'detail' && typeof getTopVisibleVerseNum === 'function') return getTopVisibleVerseNum();
    if (AppState.currentView === 'commentary' && typeof getTopVisibleCommentaryVerseNum === 'function') return getTopVisibleCommentaryVerseNum();
    return null;
  },

  /** Keep the memory fresh while the reader scrolls (used by the window scroll hook). */
  scheduleCapture() {
    if (this._captureTimer) clearTimeout(this._captureTimer);
    this._captureTimer = setTimeout(() => {
      this._captureTimer = null;
      this.capture();
    }, 650);
  },

  /* ---------- restore ---------- */
  /**
   * Jump the freshly rendered screen back to its remembered place.
   * @returns {object|null} the entry that was applied
   */
  restore(key) {
    this.load();
    const entry = this.entries[key];
    if (!entry) return null;
    const headerH = this.headerHeight();
    let target = null;

    if (entry.anchor) {
      const el = document.querySelector(`[data-scroll-anchor="${this.escape(entry.anchor)}"]`);
      if (el) target = Math.round(el.getBoundingClientRect().top + window.scrollY - headerH - (entry.top || 0));
    }
    if (target == null && entry.y) {
      const docH = document.documentElement.scrollHeight;
      const drift = Math.abs((entry.docH || docH) - docH);
      if (drift <= Math.max(600, docH * 0.08)) target = entry.y;
    }
    if (target == null || target <= 4) return null;

    const max = Math.max(0, document.documentElement.scrollHeight - window.innerHeight);
    target = Math.min(Math.max(0, target), max);
    if (typeof window.scrollTo === 'function') window.scrollTo({ top: target, behavior: 'auto' });
    return Object.assign({}, entry, { applied: target });
  },

  /** Human label for a remembered place, e.g. "verse 12 of Al-Imran". */
  labelFor(surahNum, verse) {
    if (!verse) return '';
    const ch = (window.chaptersData || []).find((chapter) => chapter.number === surahNum);
    return `${ch ? ch.name_en : 'Surah ' + surahNum} · verse ${verse}`;
  },
};
