/* ================================================
   AL-QURAN INTERACTIVE READER — MAIN APP LOGIC
   ================================================
   This file handles:
   - View routing (list ↔ detail)
   - Chapter list rendering with search
   - Surah detail rendering (themes, verses, phrases)
   - Theme switching (dark, light, sepia, midnight)
   - Verse-level bookmarks (localStorage)
   - Verse-level reading history (localStorage)
   - Explanation modal
   - Verse-level search in detail view
   - Global search across loaded chapter content
   
   LOADING STRATEGY:
   Chapter data files are NOT loaded upfront. They are
   fetched on-demand when a user opens a chapter, then
   cached in memory. This keeps the homepage fast.
================================================ */

/* ================================================
   1. APP STATE
   Central state object for the entire application.
================================================ */
const AppState = {
  currentView: 'list',        // 'list' or 'detail'
  currentSurah: null,          // Chapter number when in detail view
  currentSurahData: null,      // Loaded chapter data array
  searchTerm: '',              // Home page search term
  detailSearchTerm: '',        // Detail page search term
  homeTab: 'chapters',        // Active home tab: 'chapters', 'bookmarks', 'history'
  _verseResultsLimit: 20,     // Progressive pagination for verse search results
};

/* ================================================
   2. THEME MANAGEMENT
   Supports 4 themes: dark, light, sepia, midnight.
   Theme preference is saved to localStorage.
================================================ */
const THEMES = ['dark', 'light', 'sepia', 'midnight'];
const THEME_LABELS = { dark: 'Dark', light: 'Light', sepia: 'Sepia', midnight: 'Midnight' };

function initTheme() {
  const saved = localStorage.getItem('quran-reader-theme') || 'dark';
  applyTheme(saved);
}

function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('quran-reader-theme', theme);
  const label = document.getElementById('themeLabel');
  if (label) label.textContent = THEME_LABELS[theme];
}

function cycleTheme() {
  const current = document.documentElement.getAttribute('data-theme') || 'dark';
  const idx = THEMES.indexOf(current);
  const next = THEMES[(idx + 1) % THEMES.length];
  applyTheme(next);
}

/* ================================================
   3. LOCAL STORAGE HELPERS
   Manage VERSE-LEVEL bookmarks and history.
================================================ */
const BOOKMARKS_KEY = 'quran-reader-bookmarks';
const HISTORY_KEY = 'quran-reader-history';

/* ---------- BOOKMARKS ---------- */
function getBookmarks() {
  try { return JSON.parse(localStorage.getItem(BOOKMARKS_KEY)) || []; }
  catch { return []; }
}

function saveBookmarks(bookmarks) {
  localStorage.setItem(BOOKMARKS_KEY, JSON.stringify(bookmarks));
}

/**
 * Extract a short English snippet for a verse from the in-memory chapter cache.
 * Joins the phrase keys of the verse and trims to 80 chars.
 * Returns empty string if chapter data isn't loaded yet.
 */
function getEnglishSnippet(surahNum, ayahNum) {
  const data = loadedChapters[surahNum] || AppState.currentSurahData;
  if (!data) return '';
  for (const theme of data) {
    for (const verse of theme.verses) {
      if (verse.ayah_no_surah === ayahNum) {
        const phrases = Object.keys(verse.ayah_en);
        if (phrases.length === 0) return '';
        const joined = phrases.join(', ');
        return joined.length > 80 ? joined.substring(0, 80) + '…' : joined;
      }
    }
  }
  return '';
}

function toggleBookmark(surahNum, ayahNum) {
  let bookmarks = getBookmarks();
  const idx = bookmarks.findIndex(b => b.surah === surahNum && b.ayah === ayahNum);
  if (idx >= 0) {
    bookmarks.splice(idx, 1);
  } else {
    const snippet = getEnglishSnippet(surahNum, ayahNum);
    bookmarks.unshift({ surah: surahNum, ayah: ayahNum, snippet, timestamp: new Date().toISOString() });
  }
  saveBookmarks(bookmarks);
  renderApp();
}

function isVerseBookmarked(surahNum, ayahNum) {
  return getBookmarks().some(b => b.surah === surahNum && b.ayah === ayahNum);
}

function removeBookmark(surahNum, ayahNum) {
  let bookmarks = getBookmarks();
  bookmarks = bookmarks.filter(b => !(b.surah === surahNum && b.ayah === ayahNum));
  saveBookmarks(bookmarks);
  renderApp();
}

/* ---------- HISTORY ---------- */
function getHistory() {
  try { return JSON.parse(localStorage.getItem(HISTORY_KEY)) || []; }
  catch { return []; }
}

function saveHistory(history) {
  localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
}

function addToHistory(surahNum, ayahNum) {
  let history = getHistory();
  // Remove previous entry for same verse so it moves to top
  history = history.filter(h => !(h.surah === surahNum && h.ayah === ayahNum));
  const snippet = getEnglishSnippet(surahNum, ayahNum);
  history.unshift({ surah: surahNum, ayah: ayahNum, snippet, timestamp: new Date().toISOString() });
  if (history.length > 30) history = history.slice(0, 30);
  saveHistory(history);
}

/**
 * Find the verse number of the topmost verse currently visible in the viewport.
 * Used to capture reading position when the user leaves a chapter.
 */
function getTopVisibleVerseNum() {
  const headerHeight = (document.getElementById('appHeader') || {}).offsetHeight || 60;
  const verseEls = document.querySelectorAll('[id^="verse-"]');
  for (const el of verseEls) {
    const rect = el.getBoundingClientRect();
    if (rect.bottom > headerHeight + 10) {
      return parseInt(el.id.replace('verse-', ''));
    }
  }
  return null;
}

/**
 * Save current reading position to history, then go back to the chapter list.
 * This is the back-button handler when inside a surah.
 */
function savePositionAndGoBack() {
  if (AppState.currentView === 'detail' && AppState.currentSurah) {
    const ayah = getTopVisibleVerseNum();
    if (ayah) addToHistory(AppState.currentSurah, ayah);
  }
  goBack();
}

function removeHistoryByIndex(index) {
  let history = getHistory();
  if (index >= 0 && index < history.length) { history.splice(index, 1); saveHistory(history); }
  renderApp();
}

function clearAllHistory() {
  localStorage.removeItem(HISTORY_KEY);
  renderApp();
}

/* ================================================
   4. CHAPTER DATA — ON-DEMAND LOADING
   ================================================
   Chapter data files (data/chapter_XXX.js) are NOT
   loaded via <script> tags. Instead, they are fetched
   on-demand when a user opens a chapter.
   
   This means the homepage loads with just 2 JS files
   (chapters-meta.js + app.js) — no 114-file download.
   
   Once fetched, chapter data is cached in the
   loadedChapters object for instant re-access.
   The service worker also caches the file for offline use.
================================================ */

// In-memory cache for loaded chapter data
const loadedChapters = {};

// In-memory cache for loaded tafsir/commentary data (split format)
const loadedTafsir = {};

/**
 * Load a script file by injecting a <script> tag into the document.
 * This is the most reliable cross-browser method to load and execute
 * a JS file that declares a global variable. The browser's own JS
 * engine parses it — handles comments, single quotes, numeric object
 * keys, and every other valid JS syntax perfectly.
 *
 * @param {string} url  - The URL of the script file to load
 * @returns {Promise}   - Resolves when script has loaded and executed
 */
function injectScript(url) {
  return new Promise((resolve, reject) => {
    // Check if this script tag already exists (avoid double-loading)
    if (document.querySelector(`script[data-quran-src="${url}"]`)) {
      resolve();
      return;
    }
    const script = document.createElement('script');
    script.src = url;
    script.setAttribute('data-quran-src', url); // marker so we can detect duplicates
    script.onload = () => resolve();
    script.onerror = () => reject(new Error(`Failed to load: ${url}`));
    document.head.appendChild(script);
  });
}

/**
 * Load a chapter's tafsir (commentary) data on demand.
 * Injects data/tafsir_XXX.js as a <script> tag, which sets the
 * global variable tafsirData_X. Then caches in memory.
 * The service worker automatically caches the file for offline use.
 *
 * This is called:
 * 1. In background after a chapter renders (prefetch — 300ms delay)
 * 2. On demand when user clicks a phrase and tafsir isn't loaded yet
 *
 * @param {number} num - Chapter number (1-114)
 * @returns {Promise<Object>} - Resolves with tafsir data object
 */
function loadTafsirData(num) {
  return new Promise((resolve, reject) => {
    // Return from memory cache if already loaded
    if (loadedTafsir[num]) {
      resolve(loadedTafsir[num]);
      return;
    }

    const pad = String(num).padStart(3, '0');
    const url = `data/tafsir_${pad}.js`;
    const varName = `tafsirData_${num}`;

    // Inject the script — browser parses and executes it natively
    // This sets window[varName] (e.g. window.tafsirData_1 = {...})
    injectScript(url)
      .then(() => {
        if (window[varName]) {
          loadedTafsir[num] = window[varName];
          resolve(window[varName]);
        } else {
          reject(new Error(`Tafsir ${num}: script loaded but variable ${varName} not found`));
        }
      })
      .catch(err => reject(new Error(`Failed to load tafsir ${num}: ${err.message}`)));
  });
}

/**
 * Load a chapter's structure data on demand.
 * Injects data/chapter_XXX.js as a <script> tag, which sets the
 * global variable chapterData_X. Then caches in memory.
 * Caches in memory so subsequent calls are instant.
 *
 * @param {number} num - Chapter number (1-114)
 * @returns {Promise<Array>} - Resolves with the chapter data array
 */
function loadChapterData(num) {
  return new Promise((resolve, reject) => {
    // Return from memory cache if already loaded
    if (loadedChapters[num]) {
      resolve(loadedChapters[num]);
      return;
    }

    const pad = String(num).padStart(3, '0');
    const url = `data/chapter_${pad}.js`;
    const varName = `chapterData_${num}`;

    // Inject the script — browser parses and executes it natively
    // This sets window[varName] (e.g. window.chapterData_1 = [...])
    injectScript(url)
      .then(() => {
        if (window[varName]) {
          loadedChapters[num] = window[varName];
          resolve(window[varName]);
        } else {
          reject(new Error(`Chapter ${num}: script loaded but variable ${varName} not found`));
        }
      })
      .catch(err => {
        reject(new Error(`Failed to load chapter ${num}: ${err.message}`));
      });
  });
}

/* ================================================
   5. NAVIGATION & VIEW MANAGEMENT
================================================ */

/**
 * Open a surah detail view.
 * Fetches chapter data on-demand, then renders.
 */
async function openSurah(num) {
  try {
    const app = document.getElementById('app');
    // Show skeleton loading screen (mimics the real layout for perceived speed)
    app.innerHTML = `<div class="detail-view">
      <div class="surah-header-card">
        <div class="surah-header-inner" style="display:flex;flex-direction:column;align-items:center;gap:16px;">
          <div class="skeleton" style="width:56px;height:56px;border-radius:16px;transform:rotate(45deg);"></div>
          <div class="skeleton" style="width:140px;height:36px;border-radius:8px;"></div>
          <div class="skeleton" style="width:200px;height:24px;border-radius:8px;"></div>
          <div class="skeleton" style="width:120px;height:16px;border-radius:8px;"></div>
          <div class="skeleton" style="width:220px;height:14px;border-radius:8px;"></div>
        </div>
      </div>
      <div style="margin-top:32px;">
        <div class="skeleton" style="width:120px;height:30px;border-radius:100px;margin-bottom:12px;"></div>
        <div class="skeleton" style="width:60%;height:22px;border-radius:8px;margin-bottom:24px;"></div>
        <div class="verse-arabic" style="margin:20px 0;padding:28px 24px;">
          <div class="skeleton" style="width:80%;height:28px;border-radius:8px;margin:0 auto 10px;"></div>
          <div class="skeleton" style="width:55%;height:28px;border-radius:8px;margin:0 auto;"></div>
        </div>
        <div style="display:flex;gap:8px;flex-wrap:wrap;padding:8px 0;">
          <div class="skeleton" style="width:110px;height:34px;border-radius:6px;"></div>
          <div class="skeleton" style="width:150px;height:34px;border-radius:6px;"></div>
          <div class="skeleton" style="width:90px;height:34px;border-radius:6px;"></div>
        </div>
        <div class="verse-arabic" style="margin:20px 0;padding:28px 24px;">
          <div class="skeleton" style="width:70%;height:28px;border-radius:8px;margin:0 auto 10px;"></div>
          <div class="skeleton" style="width:50%;height:28px;border-radius:8px;margin:0 auto;"></div>
        </div>
        <div style="display:flex;gap:8px;flex-wrap:wrap;padding:8px 0;">
          <div class="skeleton" style="width:130px;height:34px;border-radius:6px;"></div>
          <div class="skeleton" style="width:100px;height:34px;border-radius:6px;"></div>
          <div class="skeleton" style="width:160px;height:34px;border-radius:6px;"></div>
        </div>
      </div>
    </div>`;

    // Show back button immediately so user can cancel
    document.getElementById('headerAction').innerHTML = `<button class="back-btn" onclick="savePositionAndGoBack()">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"/></svg>
      All Chapters
    </button>`;

    // Fetch chapter data (from memory cache or network)
    const data = await loadChapterData(num);
    AppState.currentSurah = num;
    AppState.currentSurahData = data;
    AppState.currentView = 'detail';
    AppState.detailSearchTerm = '';
    AppState._scrollToTopOnRender = true;

    history.pushState({ view: 'detail', surah: num }, '', `#surah-${num}`);
    renderApp();

    // Prefetch tafsir for this chapter in background (300ms delay so rendering isn't blocked)
    // By the time user reads the Arabic and clicks a phrase, tafsir is already loaded
    setTimeout(() => { loadTafsirData(num).catch(() => {}); }, 300);

    // Background prefetch: download adjacent chapters while user reads
    setTimeout(() => {
      if (num < 114) prefetchChapter(num + 1);
      if (num > 1) prefetchChapter(num - 1);
    }, 1500);
  } catch (err) {
    const app = document.getElementById('app');
    app.innerHTML = `<div style="text-align:center; padding:80px 20px;">
      <div style="font-size:48px; margin-bottom:16px; opacity:0.3;">📖</div>
      <div style="color:var(--text-muted); font-size:16px; font-weight:600;">Chapter data not available yet</div>
      <p style="color:var(--text-dim); margin-top:8px; font-size:14px;">This chapter's interactive content is coming soon.</p>
      <button class="back-btn" onclick="goBack()" style="margin-top:24px;">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"/></svg>
        Back to Chapters
      </button>
    </div>`;
  }
}

/**
 * Open a surah and scroll to a specific verse.
 * Used by bookmarks and history entries.
 */
async function openSurahAtVerse(surahNum, ayahNum) {
  if (AppState.currentView === 'detail' && AppState.currentSurah === surahNum) {
    scrollToVerse(ayahNum);
    return;
  }
  await openSurah(surahNum);
  setTimeout(() => { scrollToVerse(ayahNum); }, 150);
}

/**
 * Scroll smoothly to a specific verse with highlight effect.
 */
function scrollToVerse(ayahNum) {
  const el = document.getElementById('verse-' + ayahNum);
  if (el) {
    const headerHeight = document.getElementById('appHeader').offsetHeight;
    const elTop = el.getBoundingClientRect().top + window.pageYOffset;
    window.scrollTo({ top: elTop - headerHeight - 20, behavior: 'smooth' });
    // Highlight effect
    el.style.transition = 'box-shadow 0.3s, border-color 0.3s';
    el.style.boxShadow = '0 0 20px rgba(var(--accent-rgb), 0.3)';
    el.style.borderColor = 'var(--accent-border-hover)';
    setTimeout(() => { el.style.boxShadow = ''; el.style.borderColor = ''; }, 2000);
  }
}

/** Jump to verse from the input widget */
function jumpToVerseFromInput() {
  const input = document.getElementById('verseJumpInput');
  if (!input) return;
  const num = parseInt(input.value);
  const ch = chaptersData.find(c => c.number === AppState.currentSurah);
  if (!ch) return;
  if (isNaN(num) || num < 1 || num > ch.verses) {
    input.style.borderColor = '#ef4444';
    setTimeout(() => { input.style.borderColor = ''; }, 800);
    return;
  }
  scrollToVerse(num);
}

/** Step verse input up or down by delta */
function jumpVerseBy(delta) {
  const input = document.getElementById('verseJumpInput');
  if (!input) return;
  const ch = chaptersData.find(c => c.number === AppState.currentSurah);
  if (!ch) return;
  let num = parseInt(input.value) || 1;
  num += delta;
  if (num < 1) num = 1;
  if (num > ch.verses) num = ch.verses;
  input.value = num;
  scrollToVerse(num);
}

function goBack() {
  AppState.currentView = 'list';
  AppState.currentSurah = null;
  AppState.currentSurahData = null;
  AppState.detailSearchTerm = '';
  renderApp();
}

function switchTab(tab) {
  AppState.homeTab = tab;
  AppState.searchTerm = '';
  AppState._verseResultsLimit = 20;
  renderApp();
}

/* ================================================
   6. SEARCH HELPERS
================================================ */

function handleSearch(val) {
  AppState._verseResultsLimit = 20;
  AppState.searchTerm = val;
  renderApp();
  const inp = document.querySelector('.search-input');
  if (inp) { inp.focus(); inp.setSelectionRange(val.length, val.length); }
}

function showMoreVerseResults(additionalCount) {
  const scrollPos = window.pageYOffset;
  AppState._verseResultsLimit = (AppState._verseResultsLimit || 20) + additionalCount;
  renderApp();
  window.scrollTo(0, scrollPos);
  const inp = document.querySelector('.search-input');
  if (inp) { inp.focus(); inp.setSelectionRange(AppState.searchTerm.length, AppState.searchTerm.length); }
}

function handleDetailSearch(val) {
  // Only trigger filtering after 3 characters (performance); clear immediately when empty
  if (val.length > 0 && val.length < 3) return;
  AppState.detailSearchTerm = val;
  renderSurahDetail(document.getElementById('app'));
  const inp = document.querySelector('.detail-search-input');
  if (inp) { inp.focus(); inp.setSelectionRange(val.length, val.length); }
}

/**
 * Word-start matching for English text.
 * Splits text into words and checks if any word STARTS with the term.
 * "mercy" matches "mercy" but "ercy" does NOT.
 */
function matchesWordStart(text, term) {
  const words = text.split(/[\s,\-—–;:'"()[\]{}./\\!?]+/);
  return words.some(word => word.startsWith(term));
}

/**
 * Word-start matching for Arabic text.
 * Splits by spaces, checks if any Arabic word starts with the term.
 */
function matchesArabicWordStart(text, term) {
  const words = text.split(/\s+/);
  return words.some(word => word.startsWith(term));
}

/**
 * Search loaded chapters' verse content (phrase keys + Arabic text).
 * Does NOT search commentary/explanations.
 * Only searches chapters already in memory (previously opened by user).
 */
function searchLoadedVerses(term) {
  const results = [];
  if (!term || term.length < 2) return results;
  const s = term.toLowerCase();

  for (const [chNum, data] of Object.entries(loadedChapters)) {
    const ch = chaptersData.find(c => c.number === parseInt(chNum));
    if (!ch || !data) continue;

    for (const theme of data) {
      for (const verse of theme.verses) {
        let matched = false;

        // Search English phrase keys only (not explanations)
        for (const phrase of Object.keys(verse.ayah_en)) {
          if (matchesWordStart(phrase.toLowerCase(), s)) {
            results.push({ surah: parseInt(chNum), ayah: verse.ayah_no_surah, matchText: phrase, chapterName: ch.name_en });
            matched = true;
            break;
          }
        }

        // Search Arabic text (word-start)
        if (!matched && matchesArabicWordStart(verse.ayah_ar, term)) {
          results.push({
            surah: parseInt(chNum), ayah: verse.ayah_no_surah,
            matchText: verse.ayah_ar.substring(0, 50) + (verse.ayah_ar.length > 50 ? '...' : ''),
            chapterName: ch.name_en
          });
        }
      }
    }
  }
  return results;
}

/* ================================================
   7. MAIN RENDER FUNCTION
================================================ */
function renderApp() {
  const app = document.getElementById('app');
  const headerAction = document.getElementById('headerAction');

  if (AppState.currentView === 'list') {
    headerAction.innerHTML = '';
    renderHomeView(app);
  } else if (AppState.currentView === 'detail') {
    headerAction.innerHTML = `<button class="back-btn" onclick="savePositionAndGoBack()">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"/></svg>
      All Chapters
    </button>`;
    renderSurahDetail(app);
  }
}

/* ================================================
   8. HOME VIEW RENDERING
================================================ */
function renderHomeView(container) {
  const bookmarks = getBookmarks();
  const historyItems = getHistory();

  let html = `
    <div style="text-align: center; margin-bottom: 16px; padding-top: 8px;">
      <h2 style="font-size: 32px; font-weight: 800; color: var(--text-primary); margin-bottom: 8px; letter-spacing: -0.03em;">Quran Explained</h2>
      <p style="color: var(--text-dim); font-size: 15px;">Explore all 114 chapters with interactive verse explanations</p>
      <p style="color: var(--text-dim); font-size: 15px;"><i>@maxikennexus</i></p>
    </div>

    <div class="home-tabs">
      <button class="home-tab ${AppState.homeTab === 'chapters' ? 'active' : ''}" onclick="switchTab('chapters')">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>
        Chapters
      </button>
      <button class="home-tab ${AppState.homeTab === 'bookmarks' ? 'active' : ''}" onclick="switchTab('bookmarks')">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/></svg>
        Bookmarks
        ${bookmarks.length > 0 ? `<span class="tab-count">${bookmarks.length}</span>` : ''}
      </button>
      <button class="home-tab ${AppState.homeTab === 'history' ? 'active' : ''}" onclick="switchTab('history')">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
        History
        ${historyItems.length > 0 ? `<span class="tab-count">${historyItems.length}</span>` : ''}
      </button>
    </div>
  `;

  if (AppState.homeTab === 'chapters') html += renderChaptersTab();
  else if (AppState.homeTab === 'bookmarks') html += renderBookmarksTab(bookmarks);
  else if (AppState.homeTab === 'history') html += renderHistoryTab(historyItems);

  container.innerHTML = html;
}

function renderChaptersTab() {
  const filtered = chaptersData.filter(ch => {
    if (!AppState.searchTerm) return true;
    const s = AppState.searchTerm.toLowerCase();
    if (ch.number.toString().startsWith(AppState.searchTerm)) return true;
    if (matchesWordStart(ch.name_en.toLowerCase(), s)) return true;
    if (matchesWordStart(ch.meaning.toLowerCase(), s)) return true;
    if (matchesArabicWordStart(ch.name_ar, AppState.searchTerm)) return true;
    return false;
  });

  let verseResults = [];
  if (AppState.searchTerm && AppState.searchTerm.length >= 3) {
    verseResults = searchLoadedVerses(AppState.searchTerm);
  }

  // Show install banner only when not already running as installed PWA
  const _isInstalled = window.matchMedia('(display-mode: standalone)').matches
                     || window.navigator.standalone === true;

  let html = `
    ${!_isInstalled ? `
    <div class="home-install-banner" onclick="window.triggerPWAInstall && window.triggerPWAInstall()">
      <div class="home-install-banner-icon">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
          <polyline points="7 10 12 15 17 10"/>
          <line x1="12" y1="15" x2="12" y2="3"/>
        </svg>
      </div>
      <div class="home-install-banner-body">
        <div class="home-install-banner-title">Install for offline reading</div>
        <div class="home-install-banner-sub">Add to your home screen — read Quran Explained without internet, anytime</div>
      </div>
      <div class="home-install-banner-cta">
        Install
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"/></svg>
      </div>
    </div>` : ''}
    <div class="search-container">
      <svg class="search-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
      </svg>
      <input type="text" class="search-input" placeholder="Search chapters by name, number, meaning, or verse content..." value="${escapeAttr(AppState.searchTerm)}" oninput="handleSearch(this.value)">
    </div>
  `;

  // Verse search results with progressive "Show More"
  if (verseResults.length > 0) {
    const pageSize = 20;
    const currentLimit = AppState._verseResultsLimit || pageSize;
    const visibleResults = verseResults.slice(0, currentLimit);
    const hasMore = verseResults.length > currentLimit;
    const remaining = verseResults.length - currentLimit;

    html += `<div style="margin-bottom:24px;">
      <h3 style="font-size:14px; font-weight:600; color:var(--accent); margin-bottom:12px; text-transform:uppercase; letter-spacing:0.05em;">
        Verse Results (${verseResults.length} found${hasMore ? ', showing ' + currentLimit : ''})
      </h3>
      <div class="bh-list">`;
    for (const r of visibleResults) {
      html += `<div class="bh-card" onclick="openSurahAtVerse(${r.surah}, ${r.ayah})">
          <div class="bh-icon history">📖</div>
          <div class="bh-info">
            <div class="bh-title">${r.chapterName} — Verse ${r.ayah}</div>
            <div class="bh-sub">"${escapeHtml(r.matchText)}"</div>
          </div>
        </div>`;
    }
    html += `</div>`;
    if (hasMore) {
      const nextBatch = Math.min(remaining, pageSize);
      html += `<div style="text-align:center; margin-top:12px;">
          <button onclick="showMoreVerseResults(${pageSize})" class="show-more-btn">
            Show ${nextBatch} More${remaining > nextBatch ? ' of ' + remaining + ' remaining' : ''}
          </button>
          ${remaining > pageSize ? `<button onclick="showMoreVerseResults(${remaining})" class="show-more-btn show-all-btn">
            Show All ${remaining} Remaining
          </button>` : ''}
        </div>`;
    }
    html += `</div>`;
  }

  // Chapter grid
  html += `<div class="chapters-grid">`;
  if (filtered.length === 0) {
    html += `<div class="no-results">No chapters found matching "${escapeHtml(AppState.searchTerm)}"</div>`;
  } else {
    for (const ch of filtered) {
      const typeLower = ch.type.toLowerCase();
      html += `
        <div class="chapter-card" onclick="openSurah(${ch.number})">
          <div class="chapter-card-inner">
            <div class="chapter-number"><span>${ch.number}</span></div>
            <div style="flex: 1; min-width: 0;">
              <div class="chapter-name-row">
                <h3 class="chapter-name">${ch.name_en}</h3>
                <span class="arabic-text chapter-arabic">${ch.name_ar}</span>
              </div>
              <div class="chapter-meta">
                <span class="chapter-meaning">${ch.meaning}</span>
                <span class="meta-dot">•</span>
                <span class="chapter-verses-count">${ch.verses} verses</span>
                <span class="meta-dot">•</span>
                <span class="type-badge ${typeLower}">${ch.type}</span>
              </div>
            </div>
          </div>
          <span class="status-badge interactive">✦ Interactive</span>
        </div>`;
    }
  }
  html += `</div>`;
  return html;
}

function renderBookmarksTab(bookmarks) {
  if (bookmarks.length === 0) {
    return `<div class="empty-state">
        <div class="empty-state-icon">🔖</div>
        <div class="empty-state-text">No bookmarks yet</div>
        <div class="empty-state-sub">Bookmark specific verses while reading for quick access later</div>
      </div>`;
  }

  let html = `<div class="bh-list">`;
  for (const bm of bookmarks) {
    const ch = chaptersData.find(c => c.number === bm.surah);
    if (!ch) continue;
    const timeAgo = getTimeAgo(bm.timestamp);

    const englishSnippet = bm.snippet || '';

    html += `<div class="bh-card">
        <div class="bh-icon bookmark" onclick="openSurahAtVerse(${ch.number}, ${bm.ayah})">🔖</div>
        <div class="bh-info" onclick="openSurahAtVerse(${ch.number}, ${bm.ayah})">
          <div class="bh-title">${ch.name_en} — Verse ${bm.ayah}</div>
          <div class="bh-sub">${englishSnippet ? escapeHtml(englishSnippet) + ' • ' : ''}Bookmarked ${timeAgo}</div>
        </div>
        <button class="bh-remove" onclick="event.stopPropagation(); removeBookmark(${ch.number}, ${bm.ayah})" title="Remove bookmark">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
      </div>`;
  }
  html += `</div>`;
  return html;
}

function renderHistoryTab(historyItems) {
  if (historyItems.length === 0) {
    return `<div class="empty-state">
        <div class="empty-state-icon">🕐</div>
        <div class="empty-state-text">No reading history</div>
        <div class="empty-state-sub">Your last-read verse in each chapter will be saved here when you leave</div>
      </div>`;
  }

  let html = `
    <div style="display:flex; justify-content:flex-end; margin-bottom:12px;">
      <button onclick="clearAllHistory()" style="font-size:12px; color:var(--text-dim); background:none; border:1px solid var(--accent-border-light); border-radius:8px; padding:6px 14px; cursor:pointer; font-family:'Inter',sans-serif; transition: all 0.2s;"
        onmouseover="this.style.color='#ef4444'; this.style.borderColor='rgba(239,68,68,0.3)'"
        onmouseout="this.style.color='var(--text-dim)'; this.style.borderColor='var(--accent-border-light)'">
        Clear All
      </button>
    </div>
    <div class="bh-list">`;

  historyItems.forEach((hi, index) => {
    const ch = chaptersData.find(c => c.number === hi.surah);
    if (!ch) return;
    const timeAgo = getTimeAgo(hi.timestamp);

    const englishSnippet = hi.snippet || '';

    html += `<div class="bh-card">
        <div class="bh-icon history" onclick="openSurahAtVerse(${ch.number}, ${hi.ayah})">🕐</div>
        <div class="bh-info" onclick="openSurahAtVerse(${ch.number}, ${hi.ayah})">
          <div class="bh-title">${ch.name_en} — Verse ${hi.ayah}</div>
          <div class="bh-sub">${englishSnippet ? escapeHtml(englishSnippet) + ' • ' : ''}Read ${timeAgo}</div>
        </div>
        <button class="bh-remove" onclick="event.stopPropagation(); removeHistoryByIndex(${index})" title="Remove from history">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
      </div>`;
  });
  html += `</div>`;
  return html;
}

/* ================================================
   9. SURAH DETAIL VIEW RENDERING
================================================ */
function renderSurahDetail(container) {
  const ch = chaptersData.find(c => c.number === AppState.currentSurah);
  const data = AppState.currentSurahData;
  if (!ch || !data) return;

  const typeLower = ch.type.toLowerCase();

  // Filter by detail search (word-start matching, no commentary)
  let filteredData = data;
  if (AppState.detailSearchTerm) {
    const s = AppState.detailSearchTerm.toLowerCase();
    filteredData = [];
    for (const theme of data) {
      const matchingVerses = theme.verses.filter(v => {
        if (v.ayah_no_surah.toString() === AppState.detailSearchTerm.trim()) return true;
        if (matchesArabicWordStart(v.ayah_ar, AppState.detailSearchTerm)) return true;
        for (const phrase of Object.keys(v.ayah_en)) {
          if (matchesWordStart(phrase.toLowerCase(), s)) return true;
        }
        return false;
      });
      if (matchingVerses.length > 0) filteredData.push({ ...theme, verses: matchingVerses });
    }
  }

  const themeCount = data.length;

  const verseNavHtml = `
    <div class="verse-jump-widget">
      <label class="verse-jump-label">Jump to Verse</label>
      <div class="verse-jump-controls">
        <button class="verse-jump-arrow" onclick="jumpVerseBy(-1)" title="Previous verse">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="15 18 9 12 15 6"/></svg>
        </button>
        <div class="verse-jump-input-wrap">
          <input type="number" id="verseJumpInput" class="verse-jump-input" min="1" max="${ch.verses}" value="1" onkeydown="if(event.key==='Enter'){jumpToVerseFromInput();}">
          <span class="verse-jump-total">/ ${ch.verses}</span>
        </div>
        <button class="verse-jump-arrow" onclick="jumpVerseBy(1)" title="Next verse">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"/></svg>
        </button>
        <button class="verse-jump-go" onclick="jumpToVerseFromInput()">Go</button>
      </div>
    </div>`;

  let html = `
    <div class="detail-view">
      <div class="surah-header-card">
        <div class="surah-header-inner">
          <div class="surah-number-badge"><span>${ch.number}</span></div>
          <h2 class="arabic-text surah-title-ar">${ch.name_ar}</h2>
          <h3 class="surah-title-en">${ch.name_en}</h3>
          <p class="surah-meaning">${ch.meaning}</p>
          <div class="surah-stats">
            <span class="surah-stat">${ch.verses} Verses</span>
            <span style="color:var(--text-separator);">•</span>
            <span class="surah-stat">${themeCount} Themes</span>
            <span style="color:var(--text-separator);">•</span>
            <span class="surah-stat" style="color:${typeLower === 'makkan' ? 'var(--makkan-color)' : 'var(--medinan-color)'};">${ch.type}</span>
          </div>
          ${verseNavHtml}
        </div>
      </div>

      <div class="search-container detail-search">
        <svg class="search-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
        </svg>
        <input type="text" class="search-input detail-search-input" placeholder="Search verses by number or content..." value="${escapeAttr(AppState.detailSearchTerm)}" oninput="handleDetailSearch(this.value)">
      </div>

      <div class="bismillah-decor">
        <span class="line"></span><span class="star">✦</span><span class="line"></span>
      </div>
  `;

  if (AppState.detailSearchTerm && filteredData.length === 0) {
    html += `<div class="no-results">No verses found matching "${escapeHtml(AppState.detailSearchTerm)}"</div>`;
  }

  // NOTE: Pagination logic removed. All verses render at once.
  
  for (const theme of filteredData) {
    html += `<div class="theme-section">
        <div class="theme-badge">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z"/></svg>
          Theme ${theme.theme_no}
        </div>
        <h3 class="theme-title">${theme.theme_description}</h3>`;

    theme.verses.forEach((verse, vIdx) => {
      const verseBookmarked = isVerseBookmarked(AppState.currentSurah, verse.ayah_no_surah);

      html += `
        <div class="verse-arabic" id="verse-${verse.ayah_no_surah}">
          <div class="ayah-number">${verse.ayah_no_surah}</div>
          <button class="verse-bookmark-btn ${verseBookmarked ? 'bookmarked' : ''}" 
            onclick="toggleBookmark(${AppState.currentSurah}, ${verse.ayah_no_surah})" 
            title="${verseBookmarked ? 'Remove bookmark' : 'Bookmark this verse'}">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="${verseBookmarked ? 'currentColor' : 'none'}" stroke="currentColor" stroke-width="2"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/></svg>
          </button>
          <p class="arabic-text verse-arabic-text">${verse.ayah_ar}</p>
        </div>`;

      const phrases = Object.keys(verse.ayah_en);
      html += `<div style="padding: 8px 0 16px; line-height: 2.2; font-size: 17px;">`;
      phrases.forEach((phrase, pIdx) => {
        // UPDATED: Using data-attributes instead of inline onclick to handle quotes safely
        html += `<span class="phrase-chip" data-surah="${AppState.currentSurah}" data-ayah="${verse.ayah_no_surah}" data-phrase="${encodeURIComponent(phrase)}">${phrase}</span>`;
        if (pIdx < phrases.length - 1) html += `<span class="phrase-separator">, </span>`;
        else html += `<span style="color: var(--text-dim);">.</span>`;
      });
      html += `</div>`;

      if (vIdx < theme.verses.length - 1) {
        html += `<div class="verse-separator"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div>`;
      }
    });

    html += `</div>`;
  }

  html += `
      <div class="surah-end">
        <p class="surah-end-text">End of Surah ${ch.name_en}</p>
        <div class="bismillah-decor" style="margin-top: 8px;">
          <span class="line"></span><span class="star">✦</span><span class="line"></span>
        </div>
      </div>
    </div>`;

  container.innerHTML = html;
  if (AppState._scrollToTopOnRender) {
    window.scrollTo({ top: 0, behavior: 'smooth' });
    AppState._scrollToTopOnRender = false;
  }
}

/* ================================================
   10. MODALS
================================================ */

/**
 * Show explanation for a clicked phrase.
 * 
 * LOOKUP ORDER (fast → fallback):
 * 1. Check tafsir cache (split format — separate commentary file)
 * 2. Check inline explanation in chapter data (old format — explanation inside chapter file)
 * 3. If neither found, fetch tafsir file on demand and show loading state
 * 
 * This supports BOTH formats seamlessly:
 * - Old format: chapter file has explanations inline → works without tafsir file
 * - Split format: chapter file has empty strings → loads tafsir on demand
 * - Mixed: some chapters old, some split → both work
 */
function showExplanation(phrase, surahNum, ayahNum) {
  let explanation = '';

  // 1. Try tafsir cache first (split format — fastest if preloaded)
  const tafsir = loadedTafsir[surahNum];
  if (tafsir && tafsir[ayahNum] && tafsir[ayahNum][phrase]) {
    explanation = tafsir[ayahNum][phrase];
  }

  // 2. Try inline explanation from chapter data (old format / fallback)
  if (!explanation) {
    const data = loadedChapters[surahNum] || AppState.currentSurahData;
    if (data) {
      for (const theme of data) {
        for (const verse of theme.verses) {
          const val = verse.ayah_en[phrase];
          if (val) { explanation = val; break; }
        }
        if (explanation) break;
      }
    }
  }

  // Open the modal — either with the explanation or a loading state
  document.getElementById('modalTitle').textContent = phrase;
  document.getElementById('modalBody').textContent = explanation || 'Loading explanation...';
  document.getElementById('modal').classList.add('active');
  document.body.style.overflow = 'hidden';

  // 3. If no explanation found yet, fetch tafsir file on demand
  if (!explanation) {
    loadTafsirData(surahNum)
      .then(() => {
        const t = loadedTafsir[surahNum];
        const text = (t && t[ayahNum] && t[ayahNum][phrase])
          ? t[ayahNum][phrase]
          : 'Detailed explanation coming soon, in sha Allah.';
        document.getElementById('modalBody').textContent = text;
      })
      .catch(() => {
        document.getElementById('modalBody').textContent =
          'Explanation not available. Please check your connection and try again.';
      });
  }
}

function closeModal() {
  document.getElementById('modal').classList.remove('active');
  document.body.style.overflow = '';
}

function openAboutModal() {
  document.getElementById('aboutModal').classList.add('active');
  document.body.style.overflow = 'hidden';
}

function closeAboutModal() {
  document.getElementById('aboutModal').classList.remove('active');
  document.body.style.overflow = '';
}

/* ================================================
   11. UTILITY FUNCTIONS
================================================ */

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

function escapeAttr(str) {
  return str.replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/'/g, '&#39;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function escapeJs(str) {
  return str.replace(/\\/g, '\\\\').replace(/'/g, "\\'").replace(/"/g, '\\"');
}

function getTimeAgo(timestamp) {
  const now = new Date();
  const then = new Date(timestamp);
  const diffMs = now - then;
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHr = Math.floor(diffMin / 60);
  const diffDay = Math.floor(diffHr / 24);

  if (diffSec < 60) return 'just now';
  if (diffMin < 60) return `${diffMin}m ago`;
  if (diffHr < 24) return `${diffHr}h ago`;
  if (diffDay < 7) return `${diffDay}d ago`;
  if (diffDay < 30) return `${Math.floor(diffDay / 7)}w ago`;
  return then.toLocaleDateString();
}

/* ================================================
   12. EVENT LISTENERS
================================================ */

document.getElementById('modal').addEventListener('click', function(e) {
  if (e.target === this) closeModal();
});

document.getElementById('aboutModal').addEventListener('click', function(e) {
  if (e.target === this) closeAboutModal();
});

document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') { closeModal(); closeAboutModal(); }
});

// GLOBAL DELEGATE LISTENER FOR PHRASE CHIPS
// Handles clicks on phrases, safely decoding special characters (quotes, etc.)
document.addEventListener('click', function(e) {
  if (e.target && e.target.classList.contains('phrase-chip')) {
    const dataset = e.target.dataset;
    const phrase = decodeURIComponent(dataset.phrase);
    const surah = parseInt(dataset.surah);
    const ayah = parseInt(dataset.ayah);
    showExplanation(phrase, surah, ayah);
  }
});

window.addEventListener('popstate', function(e) {
  if (e.state && e.state.view === 'detail' && e.state.surah) {
    openSurah(e.state.surah);
  } else {
    // Save position before leaving if we were in a detail view
    if (AppState.currentView === 'detail' && AppState.currentSurah) {
      const ayah = getTopVisibleVerseNum();
      if (ayah) addToHistory(AppState.currentSurah, ayah);
    }
    AppState.currentView = 'list';
    AppState.currentSurah = null;
    AppState.currentSurahData = null;
    renderApp();
  }
});

function handleInitialHash() {
  const hash = window.location.hash;
  if (hash && hash.startsWith('#surah-')) {
    const num = parseInt(hash.replace('#surah-', ''));
    if (num >= 1 && num <= 114) { openSurah(num); return; }
  }
  renderApp();
}

/* ================================================
   PERFORMANCE: Progressive Rendering & Prefetching
================================================ */

/**
 * Prefetch a chapter in the background (silent, non-blocking).
 * The service worker will cache the downloaded file for offline use.
 */
function prefetchChapter(num) {
  if (!loadedChapters[num] && num >= 1 && num <= 114) {
    loadChapterData(num).catch(() => {}); // Silent fail — it's just a prefetch
  }
}

/**
 * Prefetch popular/commonly-read chapters during browser idle time.
 * Staggered with 2s delays to avoid flooding the network.
 */
function prefetchPopularChapters() {
  const popular = [1, 36, 67, 55, 56, 18, 112, 2];
  let delay = 0;
  for (const num of popular) {
    if (!loadedChapters[num]) {
      setTimeout(() => prefetchChapter(num), delay);
      delay += 2000;
    }
  }
}

/* ================================================
   13. INITIALIZATION
================================================ */
initTheme();
handleInitialHash();

/* Prefetch popular chapters during browser idle time.
   Uses requestIdleCallback if available (runs when browser is free),
   otherwise falls back to a 5-second setTimeout. */
if ('requestIdleCallback' in window) {
  requestIdleCallback(prefetchPopularChapters);
} else {
  setTimeout(prefetchPopularChapters, 5000);
}
