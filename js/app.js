/* ================================================
   AL-QURAN INTERACTIVE READER — MAIN APP LOGIC v2.0
   ================================================ */

/* ================================================
   1. APP STATE
================================================ */
const AppState = {
  currentView: 'list',
  currentSurah: null,
  currentSurahData: null,
  searchTerm: '',
  detailSearchTerm: '',
  homeTab: 'chapters',
  _verseResultsLimit: 20,
};

/* ================================================
   2. THEME MANAGEMENT
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
  showToast(`Theme: ${THEME_LABELS[next]}`, 'info');
}

/* ================================================
   3. FONT SIZE MANAGEMENT
================================================ */
const FONT_SIZES_KEY = 'quran-reader-font-sizes';

function getFontSizes() {
  try {
    return JSON.parse(localStorage.getItem(FONT_SIZES_KEY)) || { arabic: 28, english: 17 };
  } catch { return { arabic: 28, english: 17 }; }
}

function saveFontSizes(sizes) {
  localStorage.setItem(FONT_SIZES_KEY, JSON.stringify(sizes));
  document.documentElement.style.setProperty('--arabic-font-size', sizes.arabic + 'px');
  document.documentElement.style.setProperty('--english-font-size', sizes.english + 'px');
}

function initFontSizes() {
  const sizes = getFontSizes();
  saveFontSizes(sizes);
}

function setFontSize(type, value) {
  const sizes = getFontSizes();
  sizes[type] = parseInt(value);
  saveFontSizes(sizes);
  const preview = document.getElementById(type === 'arabic' ? 'arabicPreview' : 'englishPreview');
  const valueEl = document.getElementById(type === 'arabic' ? 'arabicFontValue' : 'englishFontValue');
  if (preview) preview.style.fontSize = value + 'px';
  if (valueEl) valueEl.textContent = value + 'px';
}

function adjustFontSize(type, delta) {
  const sizes = getFontSizes();
  const min = type === 'arabic' ? 20 : 13;
  const max = type === 'arabic' ? 48 : 24;
  sizes[type] = Math.max(min, Math.min(max, sizes[type] + delta));
  saveFontSizes(sizes);
  const range = document.getElementById(type === 'arabic' ? 'arabicFontRange' : 'englishFontRange');
  const preview = document.getElementById(type === 'arabic' ? 'arabicPreview' : 'englishPreview');
  const valueEl = document.getElementById(type === 'arabic' ? 'arabicFontValue' : 'englishFontValue');
  if (range) range.value = sizes[type];
  if (preview) preview.style.fontSize = sizes[type] + 'px';
  if (valueEl) valueEl.textContent = sizes[type] + 'px';
}

function resetFontSizes() {
  saveFontSizes({ arabic: 28, english: 17 });
  const ar = document.getElementById('arabicFontRange');
  const en = document.getElementById('englishFontRange');
  if (ar) ar.value = 28;
  if (en) en.value = 17;
  const arP = document.getElementById('arabicPreview');
  const enP = document.getElementById('englishPreview');
  if (arP) arP.style.fontSize = '28px';
  if (enP) enP.style.fontSize = '17px';
  const arV = document.getElementById('arabicFontValue');
  const enV = document.getElementById('englishFontValue');
  if (arV) arV.textContent = '28px';
  if (enV) enV.textContent = '17px';
  showToast('Font sizes reset to default', 'info');
}

function openFontSizeModal() {
  const sizes = getFontSizes();
  const modal = document.getElementById('fontSizeModal');
  modal.classList.add('active');
  document.body.style.overflow = 'hidden';
  const ar = document.getElementById('arabicFontRange');
  const en = document.getElementById('englishFontRange');
  const arP = document.getElementById('arabicPreview');
  const enP = document.getElementById('englishPreview');
  const arV = document.getElementById('arabicFontValue');
  const enV = document.getElementById('englishFontValue');
  if (ar) ar.value = sizes.arabic;
  if (en) en.value = sizes.english;
  if (arP) arP.style.fontSize = sizes.arabic + 'px';
  if (enP) enP.style.fontSize = sizes.english + 'px';
  if (arV) arV.textContent = sizes.arabic + 'px';
  if (enV) enV.textContent = sizes.english + 'px';
}

function closeFontSizeModal() {
  document.getElementById('fontSizeModal').classList.remove('active');
  document.body.style.overflow = '';
}

/* ================================================
   4. TOAST NOTIFICATIONS
================================================ */
function showToast(message, type = 'info') {
  const container = document.getElementById('toastContainer');
  if (!container) return;
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  const iconSvg = type === 'success'
    ? '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>'
    : '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>';
  toast.innerHTML = `<span class="toast-icon">${iconSvg}</span>${escapeHtml(message)}`;
  container.appendChild(toast);
  setTimeout(() => { if (toast.parentNode) toast.parentNode.removeChild(toast); }, 3200);
}

/* ================================================
   5. LOCAL STORAGE HELPERS
================================================ */
const BOOKMARKS_KEY = 'quran-reader-bookmarks';
const HISTORY_KEY = 'quran-reader-history';

function getBookmarks() {
  try { return JSON.parse(localStorage.getItem(BOOKMARKS_KEY)) || []; } catch { return []; }
}
function saveBookmarks(bookmarks) { localStorage.setItem(BOOKMARKS_KEY, JSON.stringify(bookmarks)); }

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
    showToast('Bookmark removed', 'info');
  } else {
    const snippet = getEnglishSnippet(surahNum, ayahNum);
    bookmarks.unshift({ surah: surahNum, ayah: ayahNum, snippet, timestamp: new Date().toISOString() });
    showToast('Verse bookmarked', 'success');
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
  showToast('Bookmark removed', 'info');
  renderApp();
}

function getHistory() {
  try { return JSON.parse(localStorage.getItem(HISTORY_KEY)) || []; } catch { return []; }
}
function saveHistory(history) { localStorage.setItem(HISTORY_KEY, JSON.stringify(history)); }

function addToHistory(surahNum, ayahNum) {
  let history = getHistory();
  history = history.filter(h => !(h.surah === surahNum && h.ayah === ayahNum));
  const snippet = getEnglishSnippet(surahNum, ayahNum);
  history.unshift({ surah: surahNum, ayah: ayahNum, snippet, timestamp: new Date().toISOString() });
  if (history.length > 30) history = history.slice(0, 30);
  saveHistory(history);
}

function getTopVisibleVerseNum() {
  const headerHeight = (document.getElementById('appHeader') || {}).offsetHeight || 60;
  const verseEls = document.querySelectorAll('[id^="verse-"]');
  for (const el of verseEls) {
    const rect = el.getBoundingClientRect();
    if (rect.bottom > headerHeight + 10) return parseInt(el.id.replace('verse-', ''));
  }
  return null;
}

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
  showToast('History cleared', 'info');
  renderApp();
}

/* ================================================
   6. CHAPTER DATA — ON-DEMAND LOADING
================================================ */
const loadedChapters = {};
const loadedTafsir = {};

function injectScript(url) {
  return new Promise((resolve, reject) => {
    if (document.querySelector(`script[data-quran-src="${url}"]`)) { resolve(); return; }
    const script = document.createElement('script');
    script.src = url;
    script.setAttribute('data-quran-src', url);
    script.onload = () => resolve();
    script.onerror = () => reject(new Error(`Failed to load: ${url}`));
    document.head.appendChild(script);
  });
}

function loadTafsirData(num) {
  return new Promise((resolve, reject) => {
    if (loadedTafsir[num]) { resolve(loadedTafsir[num]); return; }
    const pad = String(num).padStart(3, '0');
    const url = `data/tafsir_${pad}.js`;
    const varName = `tafsirData_${num}`;
    injectScript(url)
      .then(() => {
        if (window[varName]) { loadedTafsir[num] = window[varName]; resolve(window[varName]); }
        else reject(new Error(`Tafsir ${num}: variable ${varName} not found`));
      })
      .catch(err => reject(err));
  });
}

function loadChapterData(num) {
  return new Promise((resolve, reject) => {
    if (loadedChapters[num]) { resolve(loadedChapters[num]); return; }
    const pad = String(num).padStart(3, '0');
    const url = `data/chapter_${pad}.js`;
    const varName = `chapterData_${num}`;
    injectScript(url)
      .then(() => {
        if (window[varName]) { loadedChapters[num] = window[varName]; resolve(window[varName]); }
        else reject(new Error(`Chapter ${num}: variable ${varName} not found`));
      })
      .catch(err => reject(err));
  });
}

/* ================================================
   7. NAVIGATION
================================================ */
async function openSurah(num) {
  try {
    const app = document.getElementById('app');
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
      </div>
    </div>`;

    document.getElementById('headerAction').innerHTML = `<button class="back-btn" onclick="savePositionAndGoBack()">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"/></svg>
      Back
    </button>`;

    const data = await loadChapterData(num);
    AppState.currentSurah = num;
    AppState.currentSurahData = data;
    AppState.currentView = 'detail';
    AppState.detailSearchTerm = '';
    AppState._scrollToTopOnRender = true;

    history.pushState({ view: 'detail', surah: num }, '', `#surah-${num}`);
    renderApp();

    setTimeout(() => { loadTafsirData(num).catch(() => {}); }, 300);
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

async function openSurahAtVerse(surahNum, ayahNum) {
  if (AppState.currentView === 'detail' && AppState.currentSurah === surahNum) {
    scrollToVerse(ayahNum);
    return;
  }
  await openSurah(surahNum);
  setTimeout(() => { scrollToVerse(ayahNum); }, 150);
}

function scrollToVerse(ayahNum) {
  const el = document.getElementById('verse-' + ayahNum);
  if (el) {
    const headerHeight = document.getElementById('appHeader').offsetHeight;
    const elTop = el.getBoundingClientRect().top + window.pageYOffset;
    window.scrollTo({ top: elTop - headerHeight - 20, behavior: 'smooth' });
    el.style.transition = 'box-shadow 0.3s, border-color 0.3s';
    el.style.boxShadow = '0 0 20px rgba(var(--accent-rgb), 0.3)';
    el.style.borderColor = 'var(--accent-border-hover)';
    setTimeout(() => { el.style.boxShadow = ''; el.style.borderColor = ''; }, 2000);
  }
}

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
  AudioPlayer.stop();
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
   8. SEARCH HELPERS
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
  if (val.length > 0 && val.length < 3) return;
  AppState.detailSearchTerm = val;
  renderSurahDetail(document.getElementById('app'));
  const inp = document.querySelector('.detail-search-input');
  if (inp) { inp.focus(); inp.setSelectionRange(val.length, val.length); }
}

function matchesWordStart(text, term) {
  const words = text.split(/[\s,\-—–;:'"()[\]{}./\\!?]+/);
  return words.some(word => word.startsWith(term));
}

function matchesArabicWordStart(text, term) {
  const words = text.split(/\s+/);
  return words.some(word => word.startsWith(term));
}

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
        for (const phrase of Object.keys(verse.ayah_en)) {
          if (matchesWordStart(phrase.toLowerCase(), s)) {
            results.push({ surah: parseInt(chNum), ayah: verse.ayah_no_surah, matchText: phrase, chapterName: ch.name_en });
            matched = true; break;
          }
        }
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
   9. MAIN RENDER FUNCTION
================================================ */
function renderApp() {
  const app = document.getElementById('app');
  const headerAction = document.getElementById('headerAction');

  if (AppState.currentView === 'list') {
    headerAction.innerHTML = '';
    renderHomeView(app);
    removeReadingProgress();
  } else if (AppState.currentView === 'detail') {
    headerAction.innerHTML = `<button class="back-btn" onclick="savePositionAndGoBack()">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"/></svg>
      Back
    </button>`;
    renderSurahDetail(app);
    initReadingProgress();
  }
}

/* ================================================
   10. HOME VIEW RENDERING
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
        Bookmarks${bookmarks.length > 0 ? ` <span class="tab-count">${bookmarks.length}</span>` : ''}
      </button>
      <button class="home-tab ${AppState.homeTab === 'history' ? 'active' : ''}" onclick="switchTab('history')">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
        History${historyItems.length > 0 ? ` <span class="tab-count">${historyItems.length}</span>` : ''}
      </button>
    </div>`;

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
  if (AppState.searchTerm && AppState.searchTerm.length >= 3) verseResults = searchLoadedVerses(AppState.searchTerm);

  const _isInstalled = window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone === true;

  let html = `
    ${!_isInstalled ? `<div class="home-install-banner" onclick="window.triggerPWAInstall && window.triggerPWAInstall()">
      <div class="home-install-banner-icon">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
      </div>
      <div class="home-install-banner-body">
        <div class="home-install-banner-title">Install for offline reading</div>
        <div class="home-install-banner-sub">Add to your home screen — read anytime without internet</div>
      </div>
      <div class="home-install-banner-cta">Install <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"/></svg></div>
    </div>` : ''}
    <div class="search-container">
      <svg class="search-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
      <input type="text" class="search-input" placeholder="Search chapters by name, number, meaning, or verse content..." value="${escapeAttr(AppState.searchTerm)}" oninput="handleSearch(this.value)">
    </div>`;

  if (verseResults.length > 0) {
    const pageSize = 20;
    const currentLimit = AppState._verseResultsLimit || pageSize;
    const visibleResults = verseResults.slice(0, currentLimit);
    const hasMore = verseResults.length > currentLimit;
    const remaining = verseResults.length - currentLimit;
    html += `<div style="margin-bottom:24px;"><h3 style="font-size:14px;font-weight:600;color:var(--accent);margin-bottom:12px;text-transform:uppercase;letter-spacing:0.05em;">Verse Results (${verseResults.length} found${hasMore ? ', showing ' + currentLimit : ''})</h3><div class="bh-list">`;
    for (const r of visibleResults) {
      html += `<div class="bh-card" onclick="openSurahAtVerse(${r.surah}, ${r.ayah})"><div class="bh-icon history">📖</div><div class="bh-info"><div class="bh-title">${r.chapterName} — Verse ${r.ayah}</div><div class="bh-sub">"${escapeHtml(r.matchText)}"</div></div></div>`;
    }
    html += `</div>`;
    if (hasMore) {
      const nextBatch = Math.min(remaining, pageSize);
      html += `<div style="text-align:center;margin-top:12px;"><button onclick="showMoreVerseResults(${pageSize})" class="show-more-btn">Show ${nextBatch} More</button>${remaining > pageSize ? `<button onclick="showMoreVerseResults(${remaining})" class="show-more-btn show-all-btn">Show All ${remaining}</button>` : ''}</div>`;
    }
    html += `</div>`;
  }

  html += `<div class="chapters-grid">`;
  if (filtered.length === 0) {
    html += `<div class="no-results">No chapters found matching "${escapeHtml(AppState.searchTerm)}"</div>`;
  } else {
    for (const ch of filtered) {
      const typeLower = ch.type.toLowerCase();
      html += `<div class="chapter-card" onclick="openSurah(${ch.number})">
        <div class="chapter-card-inner">
          <div class="chapter-number"><span>${ch.number}</span></div>
          <div style="flex:1;min-width:0;">
            <div class="chapter-name-row"><h3 class="chapter-name">${ch.name_en}</h3><span class="arabic-text chapter-arabic">${ch.name_ar}</span></div>
            <div class="chapter-meta"><span class="chapter-meaning">${ch.meaning}</span><span class="meta-dot">•</span><span class="chapter-verses-count">${ch.verses} verses</span><span class="meta-dot">•</span><span class="type-badge ${typeLower}">${ch.type}</span></div>
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
  if (bookmarks.length === 0) return `<div class="empty-state"><div class="empty-state-icon">🔖</div><div class="empty-state-text">No bookmarks yet</div><div class="empty-state-sub">Bookmark specific verses while reading for quick access later</div></div>`;
  let html = `<div class="bh-list">`;
  for (const bm of bookmarks) {
    const ch = chaptersData.find(c => c.number === bm.surah);
    if (!ch) continue;
    html += `<div class="bh-card"><div class="bh-icon bookmark" onclick="openSurahAtVerse(${ch.number},${bm.ayah})">🔖</div><div class="bh-info" onclick="openSurahAtVerse(${ch.number},${bm.ayah})"><div class="bh-title">${ch.name_en} — Verse ${bm.ayah}</div><div class="bh-sub">${bm.snippet ? escapeHtml(bm.snippet) + ' • ' : ''}Bookmarked ${getTimeAgo(bm.timestamp)}</div></div><button class="bh-remove" onclick="event.stopPropagation();removeBookmark(${ch.number},${bm.ayah})" title="Remove"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></button></div>`;
  }
  return html + `</div>`;
}

function renderHistoryTab(historyItems) {
  if (historyItems.length === 0) return `<div class="empty-state"><div class="empty-state-icon">🕐</div><div class="empty-state-text">No reading history</div><div class="empty-state-sub">Your last-read verse will be saved here when you leave a chapter</div></div>`;
  let html = `<div style="display:flex;justify-content:flex-end;margin-bottom:12px;"><button onclick="clearAllHistory()" style="font-size:12px;color:var(--text-dim);background:none;border:1px solid var(--accent-border-light);border-radius:8px;padding:6px 14px;cursor:pointer;font-family:'Inter',sans-serif;transition:all 0.2s;" onmouseover="this.style.color='#ef4444'" onmouseout="this.style.color='var(--text-dim)'">Clear All</button></div><div class="bh-list">`;
  historyItems.forEach((hi, index) => {
    const ch = chaptersData.find(c => c.number === hi.surah);
    if (!ch) return;
    html += `<div class="bh-card"><div class="bh-icon history" onclick="openSurahAtVerse(${ch.number},${hi.ayah})">🕐</div><div class="bh-info" onclick="openSurahAtVerse(${ch.number},${hi.ayah})"><div class="bh-title">${ch.name_en} — Verse ${hi.ayah}</div><div class="bh-sub">${hi.snippet ? escapeHtml(hi.snippet) + ' • ' : ''}Read ${getTimeAgo(hi.timestamp)}</div></div><button class="bh-remove" onclick="event.stopPropagation();removeHistoryByIndex(${index})" title="Remove"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></button></div>`;
  });
  return html + `</div>`;
}

/* ================================================
   11. SURAH DETAIL VIEW RENDERING
================================================ */
function renderSurahDetail(container) {
  const ch = chaptersData.find(c => c.number === AppState.currentSurah);
  const data = AppState.currentSurahData;
  if (!ch || !data) return;

  const typeLower = ch.type.toLowerCase();

  let filteredData = data;
  if (AppState.detailSearchTerm) {
    const s = AppState.detailSearchTerm.toLowerCase();
    filteredData = [];
    for (const theme of data) {
      const mv = theme.verses.filter(v => {
        if (v.ayah_no_surah.toString() === AppState.detailSearchTerm.trim()) return true;
        if (matchesArabicWordStart(v.ayah_ar, AppState.detailSearchTerm)) return true;
        for (const phrase of Object.keys(v.ayah_en)) { if (matchesWordStart(phrase.toLowerCase(), s)) return true; }
        return false;
      });
      if (mv.length > 0) filteredData.push({ ...theme, verses: mv });
    }
  }

  const themeCount = data.length;
  const isChapterPlaying = AudioPlayer.isChapterMode && AudioPlayer.currentSurah === AppState.currentSurah && AudioPlayer.isPlaying;

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

          <!-- CHAPTER AUDIO PLAYER -->
          <div class="chapter-player-card">
            <div class="chapter-player-header">
              <div class="chapter-player-title">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="5 3 19 12 5 21 5 3"/></svg>
                Chapter Recitation
              </div>
              <button class="about-btn" onclick="openFontSizeModal()" title="Adjust text size" style="width:30px;height:30px;">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 7V4h16v3"/><path d="M9 20h6"/><path d="M12 4v16"/></svg>
              </button>
            </div>
            <div class="chapter-player-start-row">
              <div class="cp-start-group">
                <span class="cp-start-label">Start from verse</span>
                <div class="cp-start-input-wrap">
                  <input type="number" id="chapterStartVerse" class="cp-start-input" min="1" max="${ch.verses}" value="1">
                  <span class="cp-start-total">/ ${ch.verses}</span>
                </div>
              </div>
              <button class="cp-play-btn ${isChapterPlaying ? 'playing' : ''}" id="chapterPlayBtn" onclick="AudioPlayer.toggleChapterPlay(${ch.number})">
                ${isChapterPlaying
                  ? '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg> Pause'
                  : '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" stroke="none"><polygon points="5 3 19 12 5 21 5 3"/></svg> Play Chapter'}
              </button>
            </div>
            <div class="cp-options-row">
              <button class="cp-option-toggle ${AudioPlayer.autoPlay ? 'active' : ''}" id="cpAutoplayToggle" onclick="AudioPlayer.toggleAutoPlay()">
                <span class="toggle-dot"></span> Auto-play
              </button>
              <button class="cp-option-toggle ${AudioPlayer.repeatVerse ? 'active' : ''}" id="cpRepeatToggle" onclick="AudioPlayer.toggleRepeatVerse()">
                <span class="toggle-dot"></span> Repeat verse
              </button>
              <select class="cp-speed-select" id="cpSpeedSelect" onchange="AudioPlayer.setSpeed(parseFloat(this.value))">
                <option value="0.5" ${AudioPlayer.speed === 0.5 ? 'selected' : ''}>0.5×</option>
                <option value="0.75" ${AudioPlayer.speed === 0.75 ? 'selected' : ''}>0.75×</option>
                <option value="1" ${AudioPlayer.speed === 1 ? 'selected' : ''}>1× Speed</option>
                <option value="1.25" ${AudioPlayer.speed === 1.25 ? 'selected' : ''}>1.25×</option>
                <option value="1.5" ${AudioPlayer.speed === 1.5 ? 'selected' : ''}>1.5×</option>
              </select>
            </div>
          </div>

          <!-- VERSE JUMP -->
          <div class="verse-jump-widget">
            <label class="verse-jump-label">Jump to Verse</label>
            <div class="verse-jump-controls">
              <button class="verse-jump-arrow" onclick="jumpVerseBy(-1)" title="Previous verse"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="15 18 9 12 15 6"/></svg></button>
              <div class="verse-jump-input-wrap">
                <input type="number" id="verseJumpInput" class="verse-jump-input" min="1" max="${ch.verses}" value="1" onkeydown="if(event.key==='Enter'){jumpToVerseFromInput();}">
                <span class="verse-jump-total">/ ${ch.verses}</span>
              </div>
              <button class="verse-jump-arrow" onclick="jumpVerseBy(1)" title="Next verse"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"/></svg></button>
              <button class="verse-jump-go" onclick="jumpToVerseFromInput()">Go</button>
            </div>
          </div>
        </div>
      </div>

      <div class="search-container detail-search">
        <svg class="search-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        <input type="text" class="search-input detail-search-input" placeholder="Search verses by number or content..." value="${escapeAttr(AppState.detailSearchTerm)}" oninput="handleDetailSearch(this.value)">
      </div>

      <div class="bismillah-decor"><span class="line"></span><span class="star">✦</span><span class="line"></span></div>`;

  if (AppState.detailSearchTerm && filteredData.length === 0) {
    html += `<div class="no-results">No verses found matching "${escapeHtml(AppState.detailSearchTerm)}"</div>`;
  }

  for (const theme of filteredData) {
    html += `<div class="theme-section">
      <div class="theme-badge"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z"/></svg> Theme ${theme.theme_no}</div>
      <h3 class="theme-title">${theme.theme_description}</h3>`;

    theme.verses.forEach((verse, vIdx) => {
      const verseBookmarked = isVerseBookmarked(AppState.currentSurah, verse.ayah_no_surah);
      const hasAudio = !!verse.audio;
      const isThisPlaying = AudioPlayer.currentSurah === AppState.currentSurah && AudioPlayer.currentAyah === verse.ayah_no_surah && AudioPlayer.isPlaying;
      const isThisLoading = AudioPlayer.currentSurah === AppState.currentSurah && AudioPlayer.currentAyah === verse.ayah_no_surah && AudioPlayer.isLoading;
      const audioActiveClass = (isThisPlaying || isThisLoading) ? ' audio-active' : '';

      html += `
        <div class="verse-arabic${audioActiveClass}" id="verse-${verse.ayah_no_surah}">
          <div class="ayah-number">${verse.ayah_no_surah}</div>
          <div class="verse-actions">
            ${hasAudio ? `<button class="verse-action-btn play-btn ${isThisPlaying || isThisLoading ? 'playing' : ''}" 
              data-ayah="${verse.ayah_no_surah}" data-audio="${encodeURIComponent(verse.audio)}"
              onclick="AudioPlayer.playVerse(${AppState.currentSurah}, ${verse.ayah_no_surah}, decodeURIComponent(this.dataset.audio))" 
              title="${isThisPlaying ? 'Pause' : 'Play verse ' + verse.ayah_no_surah}">
              ${isThisLoading ? '<div class="audio-spinner"></div>'
                : isThisPlaying ? '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4" width="4" height="16" rx="1"/><rect x="14" y="4" width="4" height="16" rx="1"/></svg>'
                : '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg>'}
            </button>` : ''}
            <button class="verse-action-btn bookmark-btn ${verseBookmarked ? 'bookmarked' : ''}" 
              onclick="toggleBookmark(${AppState.currentSurah}, ${verse.ayah_no_surah})" 
              title="${verseBookmarked ? 'Remove bookmark' : 'Bookmark verse ' + verse.ayah_no_surah}">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="${verseBookmarked ? 'currentColor' : 'none'}" stroke="currentColor" stroke-width="2"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/></svg>
            </button>
          </div>
          <p class="arabic-text verse-arabic-text">${verse.ayah_ar}</p>
        </div>`;

      const phrases = Object.keys(verse.ayah_en);
      html += `<div style="padding:8px 0 16px;line-height:2.2;">`;
      phrases.forEach((phrase, pIdx) => {
        html += `<span class="phrase-chip" data-surah="${AppState.currentSurah}" data-ayah="${verse.ayah_no_surah}" data-phrase="${encodeURIComponent(phrase)}">${phrase}</span>`;
        if (pIdx < phrases.length - 1) html += `<span class="phrase-separator">, </span>`;
        else html += `<span style="color:var(--text-dim);">.</span>`;
      });
      html += `</div>`;

      if (vIdx < theme.verses.length - 1) {
        html += `<div class="verse-separator"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div>`;
      }
    });
    html += `</div>`;
  }

  html += `<div class="surah-end"><p class="surah-end-text">End of Surah ${ch.name_en}</p><div class="bismillah-decor" style="margin-top:8px;"><span class="line"></span><span class="star">✦</span><span class="line"></span></div></div></div>`;

  container.innerHTML = html;

  // Build audio list and restore state
  AudioPlayer.buildVerseAudioList(AppState.currentSurah);
  if (AudioPlayer.currentSurah === AppState.currentSurah && AudioPlayer.isPlaying) {
    AudioPlayer._setVerseActive(true);
    document.querySelector('.app-container')?.classList.add('audio-playing');
  }

  if (AppState._scrollToTopOnRender) {
    window.scrollTo({ top: 0, behavior: 'smooth' });
    AppState._scrollToTopOnRender = false;
  }
}

/* ================================================
   12. MODALS
================================================ */
function showExplanation(phrase, surahNum, ayahNum) {
  let explanation = '';
  const tafsir = loadedTafsir[surahNum];
  if (tafsir && tafsir[ayahNum] && tafsir[ayahNum][phrase]) explanation = tafsir[ayahNum][phrase];
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
  document.getElementById('modalTitle').textContent = phrase;
  document.getElementById('modalBody').textContent = explanation || 'Loading explanation...';
  document.getElementById('modal').classList.add('active');
  document.body.style.overflow = 'hidden';
  if (!explanation) {
    loadTafsirData(surahNum).then(() => {
      const t = loadedTafsir[surahNum];
      document.getElementById('modalBody').textContent = (t && t[ayahNum] && t[ayahNum][phrase]) ? t[ayahNum][phrase] : 'Detailed explanation coming soon, in sha Allah.';
    }).catch(() => { document.getElementById('modalBody').textContent = 'Explanation not available. Please check your connection.'; });
  }
}

function closeModal() { document.getElementById('modal').classList.remove('active'); document.body.style.overflow = ''; }
function openAboutModal() { document.getElementById('aboutModal').classList.add('active'); document.body.style.overflow = 'hidden'; }
function closeAboutModal() { document.getElementById('aboutModal').classList.remove('active'); document.body.style.overflow = ''; }

/* ================================================
   13. UTILITY FUNCTIONS
================================================ */
function escapeHtml(str) { const d = document.createElement('div'); d.textContent = str; return d.innerHTML; }
function escapeAttr(str) { return str.replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/'/g, '&#39;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }

function getTimeAgo(timestamp) {
  const now = new Date(); const then = new Date(timestamp); const diffMs = now - then;
  const diffSec = Math.floor(diffMs / 1000); const diffMin = Math.floor(diffSec / 60);
  const diffHr = Math.floor(diffMin / 60); const diffDay = Math.floor(diffHr / 24);
  if (diffSec < 60) return 'just now'; if (diffMin < 60) return `${diffMin}m ago`;
  if (diffHr < 24) return `${diffHr}h ago`; if (diffDay < 7) return `${diffDay}d ago`;
  if (diffDay < 30) return `${Math.floor(diffDay / 7)}w ago`; return then.toLocaleDateString();
}

/* ================================================
   14. READING PROGRESS BAR
================================================ */
function initReadingProgress() {
  if (!document.getElementById('readingProgressBar')) {
    const bar = document.createElement('div');
    bar.className = 'reading-progress-bar';
    bar.id = 'readingProgressBar';
    bar.innerHTML = '<div class="reading-progress-fill" id="readingProgressFill"></div>';
    document.body.appendChild(bar);
  }
}

function removeReadingProgress() {
  const bar = document.getElementById('readingProgressBar');
  if (bar) bar.remove();
}

function updateReadingProgress() {
  const fill = document.getElementById('readingProgressFill');
  if (!fill) return;
  const scrollTop = window.pageYOffset;
  const docHeight = document.documentElement.scrollHeight - window.innerHeight;
  const pct = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
  fill.style.width = Math.min(100, pct) + '%';
}

/* ================================================
   15. SCROLL TO TOP BUTTON
================================================ */
function updateScrollTopBtn() {
  const btn = document.getElementById('scrollTopBtn');
  if (!btn) return;
  const hasPlayer = document.querySelector('.audio-player-bar.visible');
  if (window.pageYOffset > 400) {
    btn.classList.add('visible');
    btn.style.bottom = hasPlayer ? '90px' : '24px';
  } else {
    btn.classList.remove('visible');
  }
}

/* ================================================
   16. AUDIO PLAYER MODULE
================================================ */
const AudioPlayer = {
  audio: null,
  currentSurah: null,
  currentAyah: null,
  currentAudioUrl: null,
  isPlaying: false,
  isLoading: false,
  duration: 0,
  currentTime: 0,
  autoPlay: false,
  repeatVerse: false,
  speed: 1,
  isChapterMode: false,
  _rafId: null,
  _verseAudioList: [],
  _prefetchedAudios: {},

  init() {
    this.audio = new Audio();
    this.audio.preload = 'auto';
    this.autoPlay = localStorage.getItem('quran-audio-autoplay') === 'true';
    this.repeatVerse = localStorage.getItem('quran-audio-repeat') === 'true';
    this.speed = parseFloat(localStorage.getItem('quran-audio-speed')) || 1;

    this.audio.addEventListener('loadstart', () => { this.isLoading = true; this._updateUI(); });
    this.audio.addEventListener('canplay', () => { this.isLoading = false; this._updateUI(); });
    this.audio.addEventListener('playing', () => {
      this.isPlaying = true; this.isLoading = false;
      this._updateUI(); this._startProgressLoop(); this._setVerseActive(true);
      document.querySelector('.app-container')?.classList.add('audio-playing');
    });
    this.audio.addEventListener('pause', () => { this.isPlaying = false; this._updateUI(); this._stopProgressLoop(); });
    this.audio.addEventListener('ended', () => {
      this.isPlaying = false; this._stopProgressLoop();
      if (this.repeatVerse) {
        this.audio.currentTime = 0;
        this.audio.play().catch(() => {});
        return;
      }
      this._setVerseActive(false);
      if (this.autoPlay || this.isChapterMode) {
        this._playNextVerse();
      } else {
        this._updateUI();
      }
    });
    this.audio.addEventListener('timeupdate', () => {
      this.currentTime = this.audio.currentTime;
      this.duration = this.audio.duration || 0;
    });
    this.audio.addEventListener('error', () => {
      this.isLoading = false; this.isPlaying = false; this._updateUI();
      showToast('Audio failed to load. Check your connection.', 'info');
    });

    this._injectPlayerBar();

    document.addEventListener('keydown', (e) => {
      if (this._isTyping(e)) return;
      if (e.code === 'Space' && this.currentAudioUrl) { e.preventDefault(); this.togglePlayPause(); }
      if (e.shiftKey && e.key === 'ArrowLeft') { e.preventDefault(); this.playPrev(); }
      if (e.shiftKey && e.key === 'ArrowRight') { e.preventDefault(); this.playNext(); }
    });
  },

  _isTyping(e) { const t = (e.target || {}).tagName; return t === 'INPUT' || t === 'TEXTAREA' || t === 'SELECT'; },

  _injectPlayerBar() {
    const bar = document.createElement('div');
    bar.className = 'audio-player-bar';
    bar.id = 'audioPlayerBar';
    bar.innerHTML = `
      <div class="audio-progress-container" id="audioProgressContainer">
        <div class="audio-progress-fill" id="audioProgressFill"></div>
      </div>
      <div class="audio-player-inner">
        <div class="audio-player-info" id="audioPlayerInfo" onclick="AudioPlayer.scrollToCurrentVerse()">
          <div class="audio-player-ayah-badge" id="audioAyahBadge">-</div>
          <div class="audio-player-text">
            <div class="audio-player-title" id="audioPlayerTitle">No verse selected</div>
            <div class="audio-player-sub"><span class="audio-time" id="audioTimeDisplay">0:00 / 0:00</span></div>
          </div>
        </div>
        <div class="audio-player-controls">
          <button class="audio-ctrl-btn prev-next-btn" onclick="AudioPlayer.playPrev()" title="Previous verse (Shift+←)">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="19 20 9 12 19 4 19 20"/><line x1="5" y1="19" x2="5" y2="5"/></svg>
          </button>
          <button class="audio-ctrl-btn primary" id="audioPlayPauseBtn" onclick="AudioPlayer.togglePlayPause()" title="Play / Pause (Space)">
            <svg id="audioPlayIcon" width="18" height="18" viewBox="0 0 24 24" fill="currentColor" stroke="none"><polygon points="5 3 19 12 5 21 5 3"/></svg>
          </button>
          <button class="audio-ctrl-btn prev-next-btn" onclick="AudioPlayer.playNext()" title="Next verse (Shift+→)">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 4 15 12 5 20 5 4"/><line x1="19" y1="5" x2="19" y2="19"/></svg>
          </button>
          <button class="audio-autoplay-toggle ${this.autoPlay ? 'active' : ''}" id="audioAutoplayBtn" onclick="AudioPlayer.toggleAutoPlay()" title="Auto-play next verse">
            <span class="autoplay-dot"></span><span class="autoplay-label">Auto</span>
          </button>
        </div>
        <button class="audio-close-btn" onclick="AudioPlayer.stop()" title="Close player">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
      </div>`;
    document.body.appendChild(bar);

    // Progress seeking
    const pc = document.getElementById('audioProgressContainer');
    let dragging = false;
    pc.addEventListener('click', (e) => this._seekFromEvent(e, pc));
    pc.addEventListener('mousedown', (e) => { dragging = true; this._seekFromEvent(e, pc); });
    document.addEventListener('mousemove', (e) => { if (dragging) this._seekFromEvent(e, pc); });
    document.addEventListener('mouseup', () => { dragging = false; });
    pc.addEventListener('touchstart', (e) => this._seekFromEvent(e.touches[0], pc), { passive: true });
    pc.addEventListener('touchmove', (e) => this._seekFromEvent(e.touches[0], pc), { passive: true });
  },

  _seekFromEvent(e, container) {
    if (!this.audio || !this.duration) return;
    const rect = container.getBoundingClientRect();
    let ratio = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
    this.audio.currentTime = ratio * this.duration;
    this._updateProgress();
  },

  /* -- Audio list -- */
  buildVerseAudioList(surahNum) {
    this._verseAudioList = [];
    const data = loadedChapters[surahNum] || AppState.currentSurahData;
    if (!data) return;
    for (const theme of data) {
      for (const verse of theme.verses) {
        if (verse.audio) this._verseAudioList.push({ ayah: verse.ayah_no_surah, url: verse.audio });
      }
    }
    this._verseAudioList.sort((a, b) => a.ayah - b.ayah);
  },

  /* -- Prefetching next audio for gapless playback -- */
  _prefetchNext() {
    const next = this._getAdjacentVerse(1);
    if (next && !this._prefetchedAudios[next.url]) {
      const prefetchAudio = new Audio();
      prefetchAudio.preload = 'auto';
      prefetchAudio.src = next.url;
      this._prefetchedAudios[next.url] = prefetchAudio;
    }
    // Also prefetch +2
    const next2 = this._getAdjacentVerseByOffset(2);
    if (next2 && !this._prefetchedAudios[next2.url]) {
      const pf2 = new Audio();
      pf2.preload = 'auto';
      pf2.src = next2.url;
      this._prefetchedAudios[next2.url] = pf2;
    }
  },

  _getAdjacentVerseByOffset(offset) {
    if (!this.currentAyah || this._verseAudioList.length === 0) return null;
    const idx = this._verseAudioList.findIndex(v => v.ayah === this.currentAyah);
    if (idx === -1) return null;
    const newIdx = idx + offset;
    if (newIdx < 0 || newIdx >= this._verseAudioList.length) return null;
    return this._verseAudioList[newIdx];
  },

  /* -- Core playback -- */
  playVerse(surahNum, ayahNum, audioUrl) {
    if (!audioUrl) return;
    if (this.currentSurah === surahNum && this.currentAyah === ayahNum && this.currentAudioUrl === audioUrl) {
      this.togglePlayPause();
      return;
    }
    this._setVerseActive(false);
    this.currentSurah = surahNum;
    this.currentAyah = ayahNum;
    this.currentAudioUrl = audioUrl;
    this.currentTime = 0;
    this.duration = 0;

    if (this._verseAudioList.length === 0) this.buildVerseAudioList(surahNum);

    // Use prefetched audio if available
    if (this._prefetchedAudios[audioUrl]) {
      this.audio.src = audioUrl;
    } else {
      this.audio.src = audioUrl;
    }
    this.audio.load();
    this.audio.playbackRate = this.speed;
    this.audio.play().catch(err => {
      this.isPlaying = false; this._updateUI();
    });

    this._showPlayerBar();
    this._updateUI();
    this._prefetchNext();
  },

  toggleChapterPlay(surahNum) {
    if (this.isChapterMode && this.currentSurah === surahNum && this.isPlaying) {
      this.audio.pause();
      this.isChapterMode = false;
      this._updateChapterBtn();
      return;
    }

    this.isChapterMode = true;
    const startInput = document.getElementById('chapterStartVerse');
    let startFrom = startInput ? parseInt(startInput.value) || 1 : 1;
    const ch = chaptersData.find(c => c.number === surahNum);
    if (ch && (startFrom < 1 || startFrom > ch.verses)) startFrom = 1;

    this.buildVerseAudioList(surahNum);
    const verse = this._verseAudioList.find(v => v.ayah >= startFrom);
    if (verse) {
      this.playVerse(surahNum, verse.ayah, verse.url);
      setTimeout(() => this._scrollVerseIntoViewIfNeeded(verse.ayah), 200);
    } else {
      showToast('No audio available for this chapter', 'info');
      this.isChapterMode = false;
    }
    this._updateChapterBtn();
  },

  _updateChapterBtn() {
    const btn = document.getElementById('chapterPlayBtn');
    if (!btn) return;
    const playing = this.isChapterMode && this.isPlaying;
    btn.className = `cp-play-btn ${playing ? 'playing' : ''}`;
    btn.innerHTML = playing
      ? '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg> Pause'
      : '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" stroke="none"><polygon points="5 3 19 12 5 21 5 3"/></svg> Play Chapter';
  },

  togglePlayPause() {
    if (!this.audio || !this.currentAudioUrl) return;
    if (this.isPlaying) { this.audio.pause(); }
    else { this.audio.play().catch(() => {}); }
  },

  stop() {
    if (this.audio) { this.audio.pause(); this.audio.src = ''; }
    this._setVerseActive(false);
    this.isPlaying = false; this.isLoading = false; this.isChapterMode = false;
    this.currentSurah = null; this.currentAyah = null; this.currentAudioUrl = null;
    this._stopProgressLoop(); this._hidePlayerBar(); this._updateAllPlayButtons();
    this._updateChapterBtn();
    document.querySelector('.app-container')?.classList.remove('audio-playing');
    this._prefetchedAudios = {};
  },

  playNext() {
    const next = this._getAdjacentVerse(1);
    if (next) {
      this.playVerse(this.currentSurah, next.ayah, next.url);
      setTimeout(() => this._scrollVerseIntoViewIfNeeded(next.ayah), 200);
    } else {
      showToast('End of chapter reached', 'info');
      this.isChapterMode = false;
      this._updateChapterBtn();
    }
  },

  playPrev() {
    if (this.currentTime > 3) { this.audio.currentTime = 0; return; }
    const prev = this._getAdjacentVerse(-1);
    if (prev) {
      this.playVerse(this.currentSurah, prev.ayah, prev.url);
      setTimeout(() => this._scrollVerseIntoViewIfNeeded(prev.ayah), 200);
    }
  },

  _playNextVerse() {
    const next = this._getAdjacentVerse(1);
    if (next) {
      this.playVerse(this.currentSurah, next.ayah, next.url);
      setTimeout(() => this._scrollVerseIntoViewIfNeeded(next.ayah), 200);
    } else {
      this.isChapterMode = false;
      this._updateUI();
      this._updateChapterBtn();
      showToast('Chapter recitation complete', 'success');
    }
  },

  _getAdjacentVerse(direction) {
    if (!this.currentAyah || this._verseAudioList.length === 0) return null;
    const idx = this._verseAudioList.findIndex(v => v.ayah === this.currentAyah);
    if (idx === -1) return null;
    const newIdx = idx + direction;
    if (newIdx < 0 || newIdx >= this._verseAudioList.length) return null;
    return this._verseAudioList[newIdx];
  },

  toggleAutoPlay() {
    this.autoPlay = !this.autoPlay;
    localStorage.setItem('quran-audio-autoplay', this.autoPlay ? 'true' : 'false');
    document.querySelectorAll('#audioAutoplayBtn, #cpAutoplayToggle').forEach(btn => {
      btn.classList.toggle('active', this.autoPlay);
    });
    showToast(`Auto-play ${this.autoPlay ? 'enabled' : 'disabled'}`, 'info');
  },

  toggleRepeatVerse() {
    this.repeatVerse = !this.repeatVerse;
    localStorage.setItem('quran-audio-repeat', this.repeatVerse ? 'true' : 'false');
    const btn = document.getElementById('cpRepeatToggle');
    if (btn) btn.classList.toggle('active', this.repeatVerse);
    showToast(`Repeat verse ${this.repeatVerse ? 'enabled' : 'disabled'}`, 'info');
  },

  setSpeed(speed) {
    this.speed = speed;
    localStorage.setItem('quran-audio-speed', speed.toString());
    if (this.audio) this.audio.playbackRate = speed;
    showToast(`Playback speed: ${speed}×`, 'info');
  },

  scrollToCurrentVerse() { if (this.currentAyah) scrollToVerse(this.currentAyah); },

  /* -- UI updates -- */
  _showPlayerBar() { const b = document.getElementById('audioPlayerBar'); if (b) b.classList.add('visible'); updateScrollTopBtn(); },
  _hidePlayerBar() {
    const b = document.getElementById('audioPlayerBar'); if (b) b.classList.remove('visible');
    document.querySelector('.app-container')?.classList.remove('audio-playing');
    updateScrollTopBtn();
  },

  _updateUI() {
    this._updatePlayerBar();
    this._updatePlayButtonState();
    this._updateChapterBtn();
  },

  _updatePlayerBar() {
    const badge = document.getElementById('audioAyahBadge');
    const title = document.getElementById('audioPlayerTitle');
    const timeDisplay = document.getElementById('audioTimeDisplay');

    if (badge && this.currentAyah) badge.textContent = this.currentAyah;
    if (title && this.currentSurah && this.currentAyah) {
      const ch = chaptersData.find(c => c.number === this.currentSurah);
      title.textContent = ch ? `${ch.name_en} — Verse ${this.currentAyah}` : `Verse ${this.currentAyah}`;
    }
    if (timeDisplay) timeDisplay.textContent = `${this._formatTime(this.currentTime)} / ${this._formatTime(this.duration)}`;

    // Update play/pause icon in player bar
    const existing = document.getElementById('audioPlayIcon');
    if (existing) {
      if (this.isLoading) {
        existing.outerHTML = `<div class="audio-spinner" id="audioPlayIcon"></div>`;
      } else if (this.isPlaying) {
        existing.outerHTML = `<svg id="audioPlayIcon" width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4" width="4" height="16" rx="1"/><rect x="14" y="4" width="4" height="16" rx="1"/></svg>`;
      } else {
        existing.outerHTML = `<svg id="audioPlayIcon" width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg>`;
      }
    }
  },

  _updatePlayButtonState() {
    document.querySelectorAll('.verse-action-btn.play-btn').forEach(btn => {
      const ayah = parseInt(btn.dataset.ayah);
      const isThis = this.currentAyah === ayah && this.currentSurah === AppState.currentSurah;
      btn.classList.toggle('playing', isThis && (this.isPlaying || this.isLoading));
      if (isThis && this.isLoading) {
        btn.innerHTML = '<div class="audio-spinner"></div>';
      } else if (isThis && this.isPlaying) {
        btn.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4" width="4" height="16" rx="1"/><rect x="14" y="4" width="4" height="16" rx="1"/></svg>';
      } else {
        btn.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg>';
      }
    });
  },

  _updateAllPlayButtons() {
    document.querySelectorAll('.verse-action-btn.play-btn').forEach(btn => {
      btn.classList.remove('playing');
      btn.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg>';
    });
  },

  _setVerseActive(active) {
    document.querySelectorAll('.verse-arabic.audio-active').forEach(el => el.classList.remove('audio-active'));
    if (active && this.currentAyah) {
      const el = document.getElementById('verse-' + this.currentAyah);
      if (el) el.classList.add('audio-active');
    }
  },

  _scrollVerseIntoViewIfNeeded(ayahNum) {
    const el = document.getElementById('verse-' + ayahNum);
    if (!el) return;
    const rect = el.getBoundingClientRect();
    const headerH = document.getElementById('appHeader')?.offsetHeight || 60;
    const playerH = document.getElementById('audioPlayerBar')?.offsetHeight || 70;
    if (rect.top < headerH + 10 || rect.bottom > window.innerHeight - playerH - 10) {
      const elTop = el.getBoundingClientRect().top + window.pageYOffset;
      window.scrollTo({ top: elTop - headerH - 20, behavior: 'smooth' });
    }
  },

  _startProgressLoop() {
    this._stopProgressLoop();
    const update = () => { this._updateProgress(); this._rafId = requestAnimationFrame(update); };
    this._rafId = requestAnimationFrame(update);
  },

  _stopProgressLoop() { if (this._rafId) { cancelAnimationFrame(this._rafId); this._rafId = null; } },

  _updateProgress() {
    const fill = document.getElementById('audioProgressFill');
    const timeDisplay = document.getElementById('audioTimeDisplay');
    if (!fill) return;
    const ct = this.audio?.currentTime || 0;
    const dur = this.audio?.duration || 0;
    fill.style.width = (dur > 0 ? (ct / dur) * 100 : 0) + '%';
    if (timeDisplay) timeDisplay.textContent = `${this._formatTime(ct)} / ${this._formatTime(dur)}`;
  },

  _formatTime(seconds) {
    if (!seconds || isNaN(seconds)) return '0:00';
    const m = Math.floor(seconds / 60); const s = Math.floor(seconds % 60);
    return `${m}:${s < 10 ? '0' : ''}${s}`;
  }
};

/* ================================================
   17. EVENT LISTENERS
================================================ */
document.getElementById('modal').addEventListener('click', function(e) { if (e.target === this) closeModal(); });
document.getElementById('aboutModal').addEventListener('click', function(e) { if (e.target === this) closeAboutModal(); });
document.getElementById('fontSizeModal').addEventListener('click', function(e) { if (e.target === this) closeFontSizeModal(); });

document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') { closeModal(); closeAboutModal(); closeFontSizeModal(); }
});

document.addEventListener('click', function(e) {
  if (e.target && e.target.classList.contains('phrase-chip')) {
    const dataset = e.target.dataset;
    showExplanation(decodeURIComponent(dataset.phrase), parseInt(dataset.surah), parseInt(dataset.ayah));
  }
});

window.addEventListener('popstate', function(e) {
  if (e.state && e.state.view === 'detail' && e.state.surah) {
    openSurah(e.state.surah);
  } else {
    if (AppState.currentView === 'detail' && AppState.currentSurah) {
      const ayah = getTopVisibleVerseNum();
      if (ayah) addToHistory(AppState.currentSurah, ayah);
    }
    AppState.currentView = 'list'; AppState.currentSurah = null; AppState.currentSurahData = null;
    renderApp();
  }
});

// Scroll events: progress bar + scroll-to-top
window.addEventListener('scroll', function() {
  updateReadingProgress();
  updateScrollTopBtn();
}, { passive: true });

function handleInitialHash() {
  const hash = window.location.hash;
  if (hash && hash.startsWith('#surah-')) {
    const num = parseInt(hash.replace('#surah-', ''));
    if (num >= 1 && num <= 114) { openSurah(num); return; }
  }
  renderApp();
}

/* ================================================
   18. PREFETCHING
================================================ */
function prefetchChapter(num) {
  if (!loadedChapters[num] && num >= 1 && num <= 114) loadChapterData(num).catch(() => {});
}

function prefetchPopularChapters() {
  const popular = [1, 36, 67, 55, 56, 18, 112, 2];
  let delay = 0;
  for (const num of popular) {
    if (!loadedChapters[num]) { setTimeout(() => prefetchChapter(num), delay); delay += 2000; }
  }
}

/* ================================================
   19. INITIALIZATION
================================================ */
AudioPlayer.init();
initTheme();
initFontSizes();
handleInitialHash();

if ('requestIdleCallback' in window) requestIdleCallback(prefetchPopularChapters);
else setTimeout(prefetchPopularChapters, 5000);