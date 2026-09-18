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
const THEMES = ['night', 'daylight', 'paper', 'forest', 'dusk'];
const THEME_LABELS = {
  night: 'Night',
  daylight: 'Daylight',
  paper: 'Paper',
  forest: 'Forest',
  dusk: 'Dusk'
};
const LEGACY_THEME_MAP = { dark: 'night', light: 'daylight', sepia: 'paper', midnight: 'dusk' };
const THEME_META_COLORS = { night: '#0b1216', daylight: '#f7faf8', paper: '#f7f1e4', forest: '#0d1d18', dusk: '#151425' };

function initTheme() {
  const saved = localStorage.getItem('quran-reader-theme') || 'night';
  applyTheme(LEGACY_THEME_MAP[saved] || (THEMES.includes(saved) ? saved : 'night'));
}

function applyTheme(theme) {
  const safeTheme = THEMES.includes(theme) ? theme : 'night';
  document.documentElement.setAttribute('data-theme', safeTheme);
  localStorage.setItem('quran-reader-theme', safeTheme);
  const label = document.getElementById('themeLabel');
  const meta = document.querySelector('meta[name="theme-color"]');
  if (label) label.textContent = THEME_LABELS[safeTheme];
  if (meta) meta.setAttribute('content', THEME_META_COLORS[safeTheme]);
  document.querySelectorAll('[data-theme-option]').forEach(option => {
    const isSelected = option.dataset.themeOption === safeTheme;
    option.classList.toggle('selected', isSelected);
    option.setAttribute('aria-checked', String(isSelected));
  });
}

function setTheme(theme) {
  applyTheme(theme);
  closeThemeMenu();
  showToast(`${THEME_LABELS[theme]} theme selected`, 'info');
}

function toggleThemeMenu() {
  const menu = document.getElementById('themeMenu');
  const trigger = document.getElementById('themeMenuButton');
  if (!menu || !trigger) return;
  const willOpen = !menu.classList.contains('active');
  menu.classList.toggle('active', willOpen);
  trigger.setAttribute('aria-expanded', String(willOpen));
}

function closeThemeMenu() {
  const menu = document.getElementById('themeMenu');
  const trigger = document.getElementById('themeMenuButton');
  if (menu) menu.classList.remove('active');
  if (trigger) trigger.setAttribute('aria-expanded', 'false');
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
        const text = typeof verse.ayah_en === 'string' ? verse.ayah_en : Object.keys(verse.ayah_en || {}).join(', ');
        if (!text) return '';
        return text.length > 80 ? text.substring(0, 80) + '…' : text;
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
    if (rect.bottom > headerHeight + 10) return parseInt(el.id.replace('verse-', ''), 10);
  }
  return null;
}

function getTopVisibleCommentaryVerseNum() {
  const headerHeight = (document.getElementById('appHeader') || {}).offsetHeight || 60;
  const sections = document.querySelectorAll('[id^="commentary-verse-"]');
  for (const section of sections) {
    const rect = section.getBoundingClientRect();
    if (rect.bottom > headerHeight + 10) return parseInt(section.id.replace('commentary-verse-', ''), 10);
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

const tafsirLoadPromises = {};

function loadTafsirData(num) {
  if (loadedTafsir[num]) return Promise.resolve(loadedTafsir[num]);
  if (tafsirLoadPromises[num]) return tafsirLoadPromises[num];

  const pad = String(num).padStart(3, '0');
  const url = `data/tafsir_${pad}.json`;

  tafsirLoadPromises[num] = fetch(url)
    .then(res => {
      if (!res.ok) throw new Error(`HTTP ${res.status} loading ${url}`);
      return res.json();
    })
    .then(data => {
      loadedTafsir[num] = data;
      delete tafsirLoadPromises[num];
      return data;
    })
    .catch(err => {
      delete tafsirLoadPromises[num];
      console.error(`Failed to load tafsir for Surah ${num}:`, err);
      throw err;
    });

  return tafsirLoadPromises[num];
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
function updateHeaderDownloadVisibility() {
  const downloadButton = document.getElementById('offlineHeaderButton');
  if (downloadButton) downloadButton.hidden = AppState.currentView !== 'list';
}

function getChapterHash(num, ayahNum) {
  return `#surah-${num}${ayahNum ? `-verse-${ayahNum}` : ''}`;
}

async function openSurah(num, options = {}) {
  try {
    const { fromHistory = false } = options;
    if (num < 1 || num > 114) return;
    // A reader should never have an old chapter recitation or eBook voice
    // continue after navigating to a chapter view.
    AudioPlayer.stop();
    DeviceSpeech.stop(true);
    AppState.currentView = 'detail';
    updateHeaderDownloadVisibility();
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

    const detailHash = getChapterHash(num);
    if (fromHistory) history.replaceState({ view: 'detail', surah: num }, '', detailHash);
    else history.pushState({ view: 'detail', surah: num }, '', detailHash);
    renderApp();

    setTimeout(() => { loadTafsirData(num).catch(() => {}); }, 300);
    setTimeout(() => {
      if (num < 114) prefetchChapter(num + 1);
      if (num > 1) prefetchChapter(num - 1);
    }, 1500);
  } catch (err) {
    console.error(`Failed to open Surah ${num}:`, err);
    AppState.currentView = 'list';
    AppState.currentSurah = null;
    AppState.currentSurahData = null;
    updateHeaderDownloadVisibility();
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

async function openCompleteCommentary(num, options = {}) {
  const ch = chaptersData.find(chapter => chapter.number === num);
  if (!ch) return;

  const { fromHistory = false } = options;
  AudioPlayer.stop();
  DeviceSpeech.stop(true);
  AppState.currentView = 'commentary';
  AppState.currentSurah = num;
  AppState.detailSearchTerm = '';
  updateHeaderDownloadVisibility();

  const app = document.getElementById('app');
  app.innerHTML = `<div class="ebook-loading" role="status" aria-live="polite">
    <div class="ebook-loading-book">📚</div>
    <h2>Preparing ${escapeHtml(ch.name_en)} commentary</h2>
    <p>Loading the complete chapter into a distraction-free reading view…</p>
    <div class="ebook-loading-lines" aria-hidden="true"><span></span><span></span><span></span></div>
  </div>`;
  document.getElementById('headerAction').innerHTML = `<button class="back-btn" onclick="backToSurah()">
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"/></svg>
    Chapter
  </button>`;

  try {
    const [data] = await Promise.all([loadChapterData(num), loadTafsirData(num)]);
    if (AppState.currentView !== 'commentary' || AppState.currentSurah !== num) return;
    AppState.currentSurahData = data;
    AppState._scrollToTopOnRender = true;
    const commentaryHash = `#surah-${num}-commentary`;
    if (fromHistory) history.replaceState({ view: 'commentary', surah: num }, '', commentaryHash);
    else history.pushState({ view: 'commentary', surah: num }, '', commentaryHash);
    renderApp();
  } catch (err) {
    console.error(`Failed to load commentary for Surah ${num}:`, err);
    app.innerHTML = `<div class="ebook-loading ebook-load-error" role="alert">
      <div class="ebook-loading-book">📖</div>
      <h2>Commentary is unavailable right now</h2>
      <p>Check your connection or save this chapter for offline reading before trying again.</p>
      <button class="back-btn" onclick="backToSurah()">Return to chapter</button>
    </div>`;
  }
}

function backToSurah() {
  const num = AppState.currentSurah;
  if (!num) { goBack(); return; }
  if (!AppState.currentSurahData) {
    openSurah(num, { fromHistory: true });
    return;
  }
  const ayah = getTopVisibleCommentaryVerseNum();
  if (ayah) addToHistory(num, ayah);
  DeviceSpeech.stop(true);
  AppState.currentView = 'detail';
  AppState._scrollToTopOnRender = false;
  history.replaceState({ view: 'detail', surah: num }, '', getChapterHash(num));
  renderApp();
  if (ayah) setTimeout(() => scrollToVerse(ayah), 80);
}

function goBack() {
  AudioPlayer.stop();
  DeviceSpeech.stop(true);
  AppState.currentView = 'list';
  AppState.currentSurah = null;
  AppState.currentSurahData = null;
  AppState.detailSearchTerm = '';
  history.replaceState({ view: 'list' }, '', `${window.location.pathname}${window.location.search}`);
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

/* Get the full English translation of a verse as a single string
   (supports both the new string format and the legacy phrase-object format) */
function getVerseEnglish(verse) {
  if (typeof verse.ayah_en === 'string') return verse.ayah_en;
  if (verse.ayah_en && typeof verse.ayah_en === 'object') return Object.keys(verse.ayah_en).join(', ');
  return '';
}

function getVerseData(surahNum, ayahNum) {
  const data = loadedChapters[surahNum] || AppState.currentSurahData;
  if (!data) return null;
  for (const theme of data) {
    const verse = theme.verses.find(item => item.ayah_no_surah === ayahNum);
    if (verse) return verse;
  }
  return null;
}

async function copyText(text) {
  if (navigator.clipboard?.writeText) {
    await navigator.clipboard.writeText(text);
    return;
  }
  const area = document.createElement('textarea');
  area.value = text;
  area.setAttribute('readonly', '');
  area.style.position = 'fixed';
  area.style.opacity = '0';
  document.body.appendChild(area);
  area.select();
  document.execCommand('copy');
  area.remove();
}

async function shareVerse(surahNum, ayahNum) {
  const ch = chaptersData.find(chapter => chapter.number === surahNum);
  const verse = getVerseData(surahNum, ayahNum);
  if (!ch || !verse) {
    showToast('Verse details are still loading. Please try again.', 'info');
    return;
  }
  const url = `${window.location.origin}${window.location.pathname}${getChapterHash(surahNum, ayahNum)}`;
  const text = `Surah ${ch.name_en} (${ch.name_ar}), Verse ${ayahNum}\n\n${verse.ayah_ar}\n\n${getVerseEnglish(verse)}\n\nRead with commentary: ${url}`;
  try {
    if (navigator.share) {
      await navigator.share({ title: `Surah ${ch.name_en} — Verse ${ayahNum}`, text, url });
      return;
    }
    await copyText(text);
    showToast('Verse and link copied to your clipboard', 'success');
  } catch (err) {
    if (err && err.name === 'AbortError') return;
    try {
      await copyText(text);
      showToast('Verse and link copied to your clipboard', 'success');
    } catch {
      showToast('Could not share this verse on this device.', 'info');
    }
  }
}

async function shareSurahCommentary(surahNum) {
  const ch = chaptersData.find(chapter => chapter.number === surahNum);
  if (!ch) return;
  const url = `${window.location.origin}${window.location.pathname}#surah-${surahNum}-commentary`;
  const text = `Read the complete commentary for Surah ${ch.name_en} (${ch.name_ar}) in Quran Explained: ${url}`;
  try {
    if (navigator.share) {
      await navigator.share({ title: `Surah ${ch.name_en} Commentary`, text, url });
      return;
    }
    await copyText(text);
    showToast('Commentary link copied to your clipboard', 'success');
  } catch (err) {
    if (err && err.name === 'AbortError') return;
    try { await copyText(text); showToast('Commentary link copied to your clipboard', 'success'); }
    catch { showToast('Could not share this commentary on this device.', 'info'); }
  }
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
        const enText = getVerseEnglish(verse);
        if (enText && matchesWordStart(enText.toLowerCase(), s)) {
          const snippet = enText.length > 60 ? enText.substring(0, 60) + '…' : enText;
          results.push({ surah: parseInt(chNum), ayah: verse.ayah_no_surah, matchText: snippet, chapterName: ch.name_en });
          matched = true;
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
  updateHeaderDownloadVisibility();

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
  } else if (AppState.currentView === 'commentary') {
    headerAction.innerHTML = `<button class="back-btn" onclick="backToSurah()">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"/></svg>
      Chapter
    </button>`;
    renderCompleteCommentary(app);
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

function renderContinueReadingCard() {
  const latest = getHistory()[0];
  if (!latest) return '';
  const ch = chaptersData.find(chapter => chapter.number === latest.surah);
  if (!ch) return '';
  return `<button class="continue-reading-card" onclick="openSurahAtVerse(${ch.number}, ${latest.ayah})">
    <span class="continue-reading-icon" aria-hidden="true">↺</span>
    <span class="continue-reading-copy"><strong>Continue reading</strong><small>${escapeHtml(ch.name_en)} · Verse ${latest.ayah}${latest.snippet ? ` · ${escapeHtml(latest.snippet)}` : ''}</small></span>
    <svg class="continue-reading-arrow" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><polyline points="9 18 15 12 9 6"/></svg>
  </button>`;
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
    ${!AppState.searchTerm ? renderContinueReadingCard() : ''}
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
        if (matchesWordStart(getVerseEnglish(v).toLowerCase(), s)) return true;
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
          <div class="surah-title-interactive" onclick="showSurahNotes(${ch.number})" title="Click to view Sūrah Overview &amp; Notes" role="button" tabindex="0" onkeydown="if(event.key==='Enter'||event.key===' ')showSurahNotes(${ch.number})">
            <h2 class="arabic-text surah-title-ar">${ch.name_ar}</h2>
            <h3 class="surah-title-en">${ch.name_en}</h3>
            <p class="surah-meaning">${ch.meaning}</p>
          </div>
          <div class="surah-stats">
            <span class="surah-stat">${ch.verses} Verses</span>
            <span style="color:var(--text-separator);">•</span>
            <span class="surah-stat">${themeCount} Themes</span>
            <span style="color:var(--text-separator);">•</span>
            <span class="surah-stat" style="color:${typeLower === 'makkan' ? 'var(--makkan-color)' : 'var(--medinan-color)'};">${ch.type}</span>
          </div>
          <div class="surah-action-buttons-wrap">
            <button class="surah-intro-badge-btn" onclick="showSurahNotes(${ch.number})" title="Read Sūrah Introduction &amp; Notes">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path>
                <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path>
              </svg>
              <span>Read Sūrah Notes</span>
            </button>
            <button class="surah-commentary-btn" onclick="openCompleteCommentary(${ch.number})" title="Read the complete chapter commentary in a focused eBook view">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
                <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
              </svg>
              <span>Complete Commentary</span>
            </button>
            <button class="surah-offline-btn ${OfflineManager.isChapterCached(ch.number) ? 'cached' : ''}" id="surahOfflineBtn" onclick="OfflineManager.toggleChapterFromDetail(${ch.number})" title="${OfflineManager.isChapterCached(ch.number) ? 'Chapter saved offline (click to remove)' : 'Save chapter for offline reading'}">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                ${OfflineManager.isChapterCached(ch.number)
                  ? '<polyline points="20 6 9 17 4 12"/>'
                  : '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>'}
              </svg>
              <span>${OfflineManager.isChapterCached(ch.number) ? 'Saved Offline' : 'Save Offline'}</span>
            </button>
          </div>

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
              title="${verseBookmarked ? 'Remove bookmark' : 'Bookmark verse ' + verse.ayah_no_surah}" aria-label="${verseBookmarked ? 'Remove bookmark for verse ' : 'Bookmark verse '}${verse.ayah_no_surah}">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="${verseBookmarked ? 'currentColor' : 'none'}" stroke="currentColor" stroke-width="2"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/></svg>
            </button>
            <button class="verse-action-btn share-btn" onclick="shareVerse(${AppState.currentSurah}, ${verse.ayah_no_surah})" title="Share verse ${verse.ayah_no_surah}" aria-label="Share verse ${verse.ayah_no_surah}">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"></circle><circle cx="6" cy="12" r="3"></circle><circle cx="18" cy="19" r="3"></circle><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"></line><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"></line></svg>
            </button>
          </div>
          <p class="arabic-text verse-arabic-text">${verse.ayah_ar}</p>
        </div>`;

      const enText = getVerseEnglish(verse);
      html += `<div style="padding:8px 0 16px;">
        <span class="verse-translation phrase-chip" data-surah="${AppState.currentSurah}" data-ayah="${verse.ayah_no_surah}" title="Tap to read the commentary for verse ${verse.ayah_no_surah}">${escapeHtml(enText)}</span>
      </div>`;

      if (vIdx < theme.verses.length - 1) {
        html += `<div class="verse-separator"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div>`;
      }
    });
    html += `</div>`;
  }

  const previousChapter = ch.number > 1 ? chaptersData.find(chapter => chapter.number === ch.number - 1) : null;
  const nextChapter = ch.number < 114 ? chaptersData.find(chapter => chapter.number === ch.number + 1) : null;
  html += `<nav class="chapter-navigation" aria-label="Chapter navigation">
    ${previousChapter ? `<button class="chapter-nav-btn previous" onclick="openSurah(${previousChapter.number})"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"/></svg><span><small>Previous</small><strong>${escapeHtml(previousChapter.name_en)}</strong></span></button>` : '<span></span>'}
    ${nextChapter ? `<button class="chapter-nav-btn next" onclick="openSurah(${nextChapter.number})"><span><small>Next</small><strong>${escapeHtml(nextChapter.name_en)}</strong></span><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg></button>` : '<span></span>'}
  </nav>`;
  html += `<div class="surah-end"><p class="surah-end-text">End of Surah ${ch.name_en}</p><div class="bismillah-decor" style="margin-top:8px;"><span class="line"></span><span class="star">✦</span><span class="line"></span></div></div></div>`;

  container.innerHTML = html;

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
   12. COMPLETE COMMENTARY EBOOK
================================================ */
function getChapterVerses(data) {
  if (!Array.isArray(data)) return [];
  return data.flatMap(theme => theme.verses || []).sort((a, b) => a.ayah_no_surah - b.ayah_no_surah);
}

function getCommentaryReadingMinutes(data, tafsir) {
  const text = [getSurahIntro(tafsir), ...getChapterVerses(data).map(verse => getVerseCommentary(tafsir, verse.ayah_no_surah))]
    .filter(Boolean)
    .join(' ');
  const words = text.trim() ? text.trim().split(/\s+/).length : 0;
  return Math.max(1, Math.ceil(words / 220));
}

function scrollToCommentaryVerse(ayahNum) {
  const verse = document.getElementById(`commentary-verse-${ayahNum}`);
  if (!verse) return;
  const headerHeight = document.getElementById('appHeader')?.offsetHeight || 60;
  const top = verse.getBoundingClientRect().top + window.pageYOffset;
  window.scrollTo({ top: top - headerHeight - 18, behavior: 'smooth' });
  verse.classList.add('ebook-verse-highlight');
  setTimeout(() => verse.classList.remove('ebook-verse-highlight'), 1600);
}

function jumpToCommentaryVerse() {
  const input = document.getElementById('commentaryJumpInput');
  const ch = chaptersData.find(chapter => chapter.number === AppState.currentSurah);
  if (!input || !ch) return;
  const ayah = parseInt(input.value, 10);
  if (!Number.isInteger(ayah) || ayah < 1 || ayah > ch.verses) {
    input.classList.add('input-error');
    setTimeout(() => input.classList.remove('input-error'), 900);
    return;
  }
  DeviceSpeech.selectVerse(AppState.currentSurah, ayah);
}

function renderCompleteCommentary(container) {
  const ch = chaptersData.find(chapter => chapter.number === AppState.currentSurah);
  const data = AppState.currentSurahData;
  const tafsir = loadedTafsir[AppState.currentSurah];
  if (!ch || !data || !tafsir) {
    container.innerHTML = `<div class="ebook-loading" role="status"><div class="ebook-loading-book">📚</div><h2>Preparing commentary…</h2><div class="ebook-loading-lines" aria-hidden="true"><span></span><span></span><span></span></div></div>`;
    return;
  }

  const readingMinutes = getCommentaryReadingMinutes(data, tafsir);
  const intro = getSurahIntro(tafsir);
  const speechSupported = DeviceSpeech.isSupported();
  const selectedVerse = DeviceSpeech.getSelectedVerse(ch.number, ch.verses);
  const chapterVerses = getChapterVerses(data);

  let html = `
    <article class="ebook-view">
      <header class="ebook-hero">
        <p class="ebook-eyebrow">Complete commentary · Reading edition</p>
        <div class="ebook-hero-title-row">
          <div>
            <h1>${escapeHtml(ch.name_en)}</h1>
            <p class="arabic-text ebook-arabic-title">${escapeHtml(ch.name_ar)}</p>
          </div>
          <span class="ebook-number" aria-label="Surah ${ch.number}">${ch.number}</span>
        </div>
        <p class="ebook-subtitle">${escapeHtml(ch.meaning)} · A focused commentary for the complete chapter.</p>
        <div class="ebook-meta" aria-label="Reading details"><span>${ch.verses} verses</span><span aria-hidden="true">·</span><span>About ${readingMinutes} min read</span><span aria-hidden="true">·</span><span>${escapeHtml(ch.type)}</span></div>
      </header>

      <section class="ebook-toolbar" aria-label="Commentary reading tools">
        <div class="ebook-tool-group ebook-jump-group">
          <label for="commentaryJumpInput">Jump to verse</label>
          <div class="ebook-jump-controls">
            <input id="commentaryJumpInput" type="number" min="1" max="${ch.verses}" inputmode="numeric" placeholder="#" aria-label="Verse number" onkeydown="if(event.key==='Enter'){jumpToCommentaryVerse();}">
            <button class="ebook-secondary-btn" onclick="jumpToCommentaryVerse()">Go</button>
          </div>
        </div>
        <div class="ebook-toolbar-actions">
          <button class="ebook-secondary-btn" onclick="openFontSizeModal()" title="Adjust text size">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 7V4h16v3"/><path d="M9 20h6"/><path d="M12 4v16"/></svg> Text size
          </button>
          <button class="ebook-secondary-btn" onclick="shareSurahCommentary(${ch.number})" title="Share commentary link">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"></circle><circle cx="6" cy="12" r="3"></circle><circle cx="18" cy="19" r="3"></circle><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"></line><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"></line></svg> Share
          </button>
          <button class="ebook-secondary-btn" onclick="window.print()" title="Print or save as PDF">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 6 2 18 2 18 9"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect x="6" y="14" width="12" height="8"></rect></svg> Save PDF
          </button>
        </div>
      </section>

      <section class="commentary-player" aria-labelledby="deviceSpeechTitle">
        <div class="commentary-player-heading">
          <div class="device-speech-icon" aria-hidden="true">
            <svg width="21" height="21" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" y1="19" x2="12" y2="22"></line><line x1="8" y1="22" x2="16" y2="22"></line></svg>
          </div>
          <div class="device-speech-copy">
            <h2 id="deviceSpeechTitle">Commentary read aloud</h2>
            <p id="deviceSpeechStatus">${speechSupported ? 'Ready to read aloud with your browser’s built-in voice. No sign-in, download, or setup is needed.' : 'Read aloud is unavailable because this browser has not exposed its built-in speech feature.'}</p>
          </div>
          <output class="commentary-player-verse" id="commentaryPlayerVerse">Verse ${selectedVerse} of ${ch.verses}</output>
        </div>
        <div class="commentary-player-controls" aria-label="Commentary player controls">
          <button class="commentary-skip-btn" id="commentaryPlayerPrevious" onclick="DeviceSpeech.previous(${ch.number})" ${selectedVerse <= 1 ? 'disabled' : ''} aria-label="Previous verse commentary" title="Previous verse commentary">
            <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3"><polyline points="11 17 6 12 11 7"></polyline><polyline points="18 17 13 12 18 7"></polyline></svg>
          </button>
          <button class="device-speech-btn" id="deviceTtsBtn" onclick="DeviceSpeech.toggle(${ch.number})" ${speechSupported ? '' : 'disabled'}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" stroke="none"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
            ${speechSupported ? 'Read aloud' : 'Read aloud unavailable'}
          </button>
          <button class="commentary-skip-btn" id="commentaryPlayerNext" onclick="DeviceSpeech.next(${ch.number})" ${selectedVerse >= ch.verses ? 'disabled' : ''} aria-label="Next verse commentary" title="Next verse commentary">
            <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3"><polyline points="6 17 11 12 6 7"></polyline><polyline points="13 17 18 12 13 7"></polyline></svg>
          </button>
          <button class="device-speech-stop" id="deviceTtsStop" onclick="DeviceSpeech.stop()" hidden aria-label="Stop read aloud" title="Stop read aloud">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><rect x="6" y="6" width="12" height="12" rx="1"></rect></svg>
          </button>
        </div>
        <label class="commentary-player-range-label" for="commentaryPlayerRange"><span>Choose a starting verse</span><span>Move the slider, then release to navigate</span></label>
        <input class="commentary-player-range" id="commentaryPlayerRange" type="range" min="1" max="${ch.verses}" value="${selectedVerse}" oninput="DeviceSpeech.previewVerse(${ch.number}, this.value)" onchange="DeviceSpeech.seek(${ch.number}, this.value)" aria-label="Choose commentary verse">
      </section>
      <details class="commentary-navigator">
        <summary><span><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg> Verse navigator</span><small>Choose any commentary verse</small></summary>
        <p>Tap a verse to move there. If Read aloud is playing, it immediately continues from your choice.</p>
        <div class="commentary-navigator-grid" role="navigation" aria-label="Select verse commentary">
          ${chapterVerses.map(verse => `<button class="commentary-navigator-item ${verse.ayah_no_surah === selectedVerse ? 'selected' : ''}" data-commentary-verse="${verse.ayah_no_surah}" onclick="DeviceSpeech.selectVerse(${ch.number}, ${verse.ayah_no_surah})" aria-current="${verse.ayah_no_surah === selectedVerse ? 'true' : 'false'}" aria-label="Go to verse ${verse.ayah_no_surah} commentary">${verse.ayah_no_surah}</button>`).join('')}
        </div>
      </details>

      ${intro ? `<section class="ebook-introduction"><p class="ebook-section-label">Surah introduction</p><div class="ebook-introduction-content">${renderMarkdown(intro)}</div></section>` : ''}
      <div class="ebook-content">`;

  for (const theme of data) {
    html += `<section class="ebook-theme-group"><p class="ebook-theme-label">Theme ${theme.theme_no} · ${escapeHtml(theme.theme_description)}</p>`;
    for (const verse of theme.verses || []) {
      const commentary = getVerseCommentary(tafsir, verse.ayah_no_surah);
      html += `<article class="ebook-verse" id="commentary-verse-${verse.ayah_no_surah}">
        <header class="ebook-verse-header"><span>Verse ${verse.ayah_no_surah}</span><button class="ebook-verse-share" onclick="shareVerse(${ch.number}, ${verse.ayah_no_surah})" title="Share verse ${verse.ayah_no_surah}" aria-label="Share verse ${verse.ayah_no_surah}"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"></circle><circle cx="6" cy="12" r="3"></circle><circle cx="18" cy="19" r="3"></circle><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"></line><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"></line></svg></button></header>
        <p class="ebook-translation">${escapeHtml(getVerseEnglish(verse))}</p>
        <div class="ebook-commentary">${commentary ? renderMarkdown(commentary) : '<p class="modal-p">Detailed commentary is coming soon, in sha Allah.</p>'}</div>
      </article>`;
    }
    html += `</section>`;
  }

  html += `<footer class="ebook-footer"><span>End of the commentary for Surah ${escapeHtml(ch.name_en)}</span><button class="ebook-secondary-btn" onclick="window.scrollTo({top:0,behavior:'smooth'})">Back to top</button></footer></div></article>`;
  container.innerHTML = html;
  DeviceSpeech.updateUI();

  if (AppState._scrollToTopOnRender) {
    window.scrollTo({ top: 0, behavior: 'smooth' });
    AppState._scrollToTopOnRender = false;
  }
}

/* ================================================
   13. MODALS & MARKDOWN COMMENTARY
================================================ */
/* Get the merged commentary for a verse */
function getVerseCommentary(tafsir, ayahNum) {
  if (!tafsir) return '';
  const verses = tafsir.verses || tafsir;
  const key = String(ayahNum);
  const entry = verses[key] !== undefined ? verses[key] : verses[ayahNum];
  if (typeof entry === 'string') return entry;
  if (typeof entry === 'object' && entry !== null) return Object.values(entry).join('\n\n');
  return '';
}

/* Get the Sūrah introduction / overview notes */
function getSurahIntro(tafsir) {
  if (!tafsir) return '';
  return tafsir.intro || '';
}

function showExplanation(surahNum, ayahNum) {
  const ch = chaptersData.find(c => c.number === surahNum);
  const title = `${ch ? ch.name_en : 'Surah ' + surahNum} — Verse ${ayahNum}`;
  document.getElementById('modalTitle').textContent = title;
  document.getElementById('modal').classList.add('active');
  document.body.style.overflow = 'hidden';

  const explanation = getVerseCommentary(loadedTafsir[surahNum], ayahNum);
  if (explanation) {
    document.getElementById('modalBody').innerHTML = renderMarkdown(explanation);
  } else {
    document.getElementById('modalBody').innerHTML = `
      <div class="modal-loading-state">
        <div class="skeleton" style="height:22px;width:60%;margin-bottom:16px;border-radius:6px;"></div>
        <div class="skeleton" style="height:16px;width:100%;margin-bottom:10px;border-radius:4px;"></div>
        <div class="skeleton" style="height:16px;width:95%;margin-bottom:10px;border-radius:4px;"></div>
        <div class="skeleton" style="height:16px;width:88%;margin-bottom:10px;border-radius:4px;"></div>
      </div>`;
    loadTafsirData(surahNum)
      .then(tafsir => {
        const text = getVerseCommentary(tafsir, ayahNum);
        document.getElementById('modalBody').innerHTML = text
          ? renderMarkdown(text)
          : '<p class="modal-p">Detailed commentary coming soon, in sha Allah.</p>';
      })
      .catch(() => {
        document.getElementById('modalBody').innerHTML = '<p class="modal-p" style="color:var(--text-dim);">Commentary not available. Please check your connection.</p>';
      });
  }
}

function showSurahNotes(surahNum) {
  const ch = chaptersData.find(c => c.number === surahNum);
  const title = `${ch ? ch.name_en : 'Surah ' + surahNum} (${ch ? ch.name_ar : ''}) — Sūrah Overview & Notes`;
  document.getElementById('modalTitle').textContent = title;
  document.getElementById('modal').classList.add('active');
  document.body.style.overflow = 'hidden';

  const intro = getSurahIntro(loadedTafsir[surahNum]);
  if (intro) {
    document.getElementById('modalBody').innerHTML = renderMarkdown(intro);
  } else {
    document.getElementById('modalBody').innerHTML = `
      <div class="modal-loading-state">
        <div class="skeleton" style="height:22px;width:60%;margin-bottom:16px;border-radius:6px;"></div>
        <div class="skeleton" style="height:16px;width:100%;margin-bottom:10px;border-radius:4px;"></div>
        <div class="skeleton" style="height:16px;width:95%;margin-bottom:10px;border-radius:4px;"></div>
        <div class="skeleton" style="height:16px;width:88%;margin-bottom:10px;border-radius:4px;"></div>
      </div>`;
    loadTafsirData(surahNum)
      .then(tafsir => {
        const text = getSurahIntro(tafsir);
        document.getElementById('modalBody').innerHTML = text
          ? renderMarkdown(text)
          : '<p class="modal-p">Detailed overview and notes for this chapter are coming soon.</p>';
      })
      .catch(() => {
        document.getElementById('modalBody').innerHTML = '<p class="modal-p" style="color:var(--text-dim);">Sūrah notes not available. Please check your connection.</p>';
      });
  }
}

/* ================================================
   MARKDOWN PARSER & RENDERER (Zero-Dependency)
================================================ */
function renderMarkdown(md) {
  if (!md) return '';
  let text = md.trim().replace(/\r\n/g, '\n');
  const blocks = text.split(/\n\s*\n/);
  const htmlBlocks = [];

  for (let block of blocks) {
    block = block.trim();
    if (!block) continue;

    if (/^(\-{3,}|\*{3,}|_{3,})$/.test(block)) {
      htmlBlocks.push('<hr class="modal-hr">');
      continue;
    }

    const headingMatch = block.match(/^(#{1,6})\s+(.+)$/);
    if (headingMatch) {
      const level = headingMatch[1].length;
      const content = parseInline(headingMatch[2]);
      htmlBlocks.push(`<h${Math.min(level + 1, 6)} class="modal-h${level + 1}">${content}</h${Math.min(level + 1, 6)}>`);
      continue;
    }

    const boldHeadingMatch = block.match(/^\*\*([^*]+)\*\*$/);
    if (boldHeadingMatch) {
      htmlBlocks.push(`<h4 class="modal-section-title">${parseInline(boldHeadingMatch[1])}</h4>`);
      continue;
    }

    if (block.startsWith('>')) {
      const quoteText = block.split('\n')
        .map(line => line.replace(/^>\s?/, ''))
        .join(' ');
      htmlBlocks.push(`<blockquote class="modal-blockquote"><p>${parseInline(quoteText)}</p></blockquote>`);
      continue;
    }

    if (/^[\*\-]\s+/.test(block)) {
      const items = block.split('\n')
        .filter(line => /^[\*\-]\s+/.test(line))
        .map(line => line.replace(/^[\*\-]\s+/, '').trim());
      const listHtml = items.map(item => `<li>${parseInline(item)}</li>`).join('');
      htmlBlocks.push(`<ul class="modal-list">${listHtml}</ul>`);
      continue;
    }

    if (/^\d+\.\s+/.test(block)) {
      const items = block.split('\n')
        .filter(line => /^\d+\.\s+/.test(line))
        .map(line => line.replace(/^\d+\.\s+/, '').trim());
      const listHtml = items.map(item => `<li>${parseInline(item)}</li>`).join('');
      htmlBlocks.push(`<ol class="modal-ordered-list">${listHtml}</ol>`);
      continue;
    }

    const pContent = parseInline(block.replace(/\n/g, ' '));
    htmlBlocks.push(`<p class="modal-p">${pContent}</p>`);
  }

  return htmlBlocks.join('\n');
}

function parseInline(str) {
  if (!str) return '';
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\*\*\*([^*]+)\*\*\*/g, '<strong><em>$1</em></strong>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/\*([^*]+)\*/g, '<em>$1</em>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');
}

function closeModal() { document.getElementById('modal').classList.remove('active'); document.body.style.overflow = ''; }
function openAboutModal() { document.getElementById('aboutModal').classList.add('active'); document.body.style.overflow = 'hidden'; }
function closeAboutModal() { document.getElementById('aboutModal').classList.remove('active'); document.body.style.overflow = ''; }

function openDownloadsModal() {
  document.getElementById('downloadsModal').classList.add('active');
  document.body.style.overflow = 'hidden';
  OfflineManager.scanCachedChapters().then(() => {
    OfflineManager.renderDownloadsList();
  });
}
function closeDownloadsModal() {
  document.getElementById('downloadsModal').classList.remove('active');
  document.body.style.overflow = '';
}

/* ================================================
   13. UTILITY FUNCTIONS
================================================ */
function escapeHtml(str) { const d = document.createElement('div'); d.textContent = str; return d.innerHTML; }
function escapeAttr(str) { return String(str).replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/'/g, '&#39;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }

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

  _prefetchNext() {
    const next = this._getAdjacentVerse(1);
    if (next && !this._prefetchedAudios[next.url]) {
      const prefetchAudio = new Audio();
      prefetchAudio.preload = 'auto';
      prefetchAudio.src = next.url;
      this._prefetchedAudios[next.url] = prefetchAudio;
    }
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

    this.audio.src = audioUrl;
    this.audio.load();
    this.audio.playbackRate = this.speed;
    this.audio.play().catch(() => {
      this.isPlaying = false;
      this._updateUI();
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
   16. DEVICE SPEECH (OFFLINE PHONE TTS)
================================================ */
const DeviceSpeech = {
  queue: [],
  index: 0,
  utterance: null,
  isSpeaking: false,
  isPaused: false,
  activeSurah: null,
  activeAyah: null,
  selectedSurah: null,
  selectedAyah: 1,
  session: 0,
  voices: [],

  init() {
    if (!this.isSupported()) return;
    const refreshVoices = () => { this.voices = window.speechSynthesis.getVoices(); };
    refreshVoices();
    window.speechSynthesis.onvoiceschanged = refreshVoices;
  },

  isSupported() {
    return typeof window !== 'undefined'
      && typeof window.speechSynthesis !== 'undefined'
      && typeof window.SpeechSynthesisUtterance === 'function';
  },

  getNarrationVoice() {
    const voices = this.voices.length ? this.voices : (this.isSupported() ? window.speechSynthesis.getVoices() : []);
    const english = voices.filter(voice => /^en(?:[-_]|$)/i.test(voice.lang));
    const localEnglish = english.filter(voice => voice.localService);
    // Prefer an installed English voice for offline use, but immediately fall
    // back to the browser's default voice. Readers never have to configure one.
    return localEnglish.find(voice => voice.default) || localEnglish[0]
      || english.find(voice => voice.default) || english[0]
      || voices.find(voice => voice.default) || voices[0] || null;
  },

  getSelectedVerse(surahNum, maxVerse) {
    if (this.selectedSurah !== surahNum) {
      this.selectedSurah = surahNum;
      this.selectedAyah = 1;
    }
    this.selectedAyah = Math.max(1, Math.min(maxVerse, parseInt(this.selectedAyah, 10) || 1));
    return this.selectedAyah;
  },

  getSpeechUnits(surahNum, startVerse = 1) {
    const data = loadedChapters[surahNum] || AppState.currentSurahData;
    const tafsir = loadedTafsir[surahNum];
    const ch = chaptersData.find(chapter => chapter.number === surahNum);
    if (!data || !tafsir || !ch) return [];
    const units = [];
    const intro = getSurahIntro(tafsir);
    if (startVerse === 1 && intro) {
      units.push({ ayah: null, text: `Surah ${ch.name_en}. Introduction. ${markdownToSpeechText(intro)}` });
    }
    getChapterVerses(data).forEach(verse => {
      if (verse.ayah_no_surah < startVerse) return;
      const commentary = getVerseCommentary(tafsir, verse.ayah_no_surah);
      if (!commentary) return;
      const translation = getVerseEnglish(verse);
      units.push({
        ayah: verse.ayah_no_surah,
        text: `Verse ${verse.ayah_no_surah}. ${translation}. Commentary. ${markdownToSpeechText(commentary)}`
      });
    });
    return units;
  },

  makeQueue(surahNum, startVerse) {
    return this.getSpeechUnits(surahNum, startVerse)
      .flatMap(unit => splitSpeechText(unit.text).map(text => ({ ...unit, text })));
  },

  toggle(surahNum) {
    if (!this.isSupported()) {
      showToast('Read aloud is not available in this browser.', 'info');
      return;
    }
    if (this.activeSurah === surahNum && this.isSpeaking) {
      this.pause();
      return;
    }
    if (this.activeSurah === surahNum && this.isPaused) {
      this.resume();
      return;
    }
    this.start(surahNum, this.getSelectedVerse(surahNum, this.getVerseCount(surahNum)));
  },

  getVerseCount(surahNum) {
    return chaptersData.find(chapter => chapter.number === surahNum)?.verses || 1;
  },

  start(surahNum, startVerse = 1) {
    if (!this.isSupported()) return;
    const maxVerse = this.getVerseCount(surahNum);
    const verse = Math.max(1, Math.min(maxVerse, parseInt(startVerse, 10) || 1));
    const queue = this.makeQueue(surahNum, verse);
    if (!queue.length) {
      showToast('Commentary is still loading. Please try again in a moment.', 'info');
      return;
    }
    this.stop(true);
    this.selectedSurah = surahNum;
    this.selectedAyah = verse;
    this.queue = queue;
    this.index = 0;
    this.activeSurah = surahNum;
    this.isSpeaking = true;
    this.isPaused = false;
    this.session += 1;
    this._speakCurrent(this.session);
    this.updateUI();
  },

  selectVerse(surahNum, ayahNum) {
    const maxVerse = this.getVerseCount(surahNum);
    const verse = Math.max(1, Math.min(maxVerse, parseInt(ayahNum, 10) || 1));
    const wasActive = this.activeSurah === surahNum && (this.isSpeaking || this.isPaused);
    this.selectedSurah = surahNum;
    this.selectedAyah = verse;
    scrollToCommentaryVerse(verse);
    if (wasActive) this.start(surahNum, verse);
    else this.updateUI();
  },

  previewVerse(surahNum, ayahNum) {
    this.selectedSurah = surahNum;
    this.selectedAyah = Math.max(1, Math.min(this.getVerseCount(surahNum), parseInt(ayahNum, 10) || 1));
    this.updateUI();
  },

  seek(surahNum, ayahNum) {
    this.selectVerse(surahNum, ayahNum);
  },

  previous(surahNum) {
    this.selectVerse(surahNum, this.getSelectedVerse(surahNum, this.getVerseCount(surahNum)) - 1);
  },

  next(surahNum) {
    this.selectVerse(surahNum, this.getSelectedVerse(surahNum, this.getVerseCount(surahNum)) + 1);
  },

  pause() {
    if (!this.isSupported() || !this.isSpeaking) return;
    window.speechSynthesis.pause();
    this.isSpeaking = false;
    this.isPaused = true;
    this.updateUI();
  },

  resume() {
    if (!this.isSupported() || !this.isPaused) return;
    window.speechSynthesis.resume();
    this.isPaused = false;
    this.isSpeaking = true;
    this.updateUI();
  },

  stop(quiet = false) {
    const wasActive = this.isSpeaking || this.isPaused;
    this.session += 1;
    if (this.isSupported()) window.speechSynthesis.cancel();
    this.queue = [];
    this.index = 0;
    this.utterance = null;
    this.isSpeaking = false;
    this.isPaused = false;
    this.activeSurah = null;
    this.setActiveVerse(null);
    this.updateUI();
    if (wasActive && !quiet) showToast('Read aloud stopped', 'info');
  },

  _speakCurrent(session) {
    if (session !== this.session || !this.queue[this.index]) {
      this.finish();
      return;
    }
    const unit = this.queue[this.index];
    if (unit.ayah) {
      this.selectedSurah = this.activeSurah;
      this.selectedAyah = unit.ayah;
    }
    this.setActiveVerse(unit.ayah);
    const utterance = new SpeechSynthesisUtterance(unit.text);
    const voice = this.getNarrationVoice();
    if (voice) utterance.voice = voice;
    utterance.lang = voice?.lang || 'en-US';
    utterance.rate = 0.92;
    utterance.pitch = 1;
    utterance.onend = () => {
      if (session !== this.session || this.isPaused) return;
      this.index += 1;
      this._speakCurrent(session);
    };
    utterance.onerror = (event) => {
      if (session !== this.session || event.error === 'interrupted' || event.error === 'canceled') return;
      console.warn('Speech synthesis error:', event.error);
      showToast('Read aloud could not continue on this device.', 'info');
      this.finish();
    };
    this.utterance = utterance;
    window.speechSynthesis.speak(utterance);
    this.updateUI();
  },

  finish() {
    const completed = this.queue.length > 0 && this.index >= this.queue.length;
    this.queue = [];
    this.index = 0;
    this.utterance = null;
    this.isSpeaking = false;
    this.isPaused = false;
    this.activeSurah = null;
    this.setActiveVerse(null);
    this.updateUI();
    if (completed) showToast('Commentary read aloud complete', 'success');
  },

  setActiveVerse(ayah) {
    this.activeAyah = ayah;
    document.querySelectorAll('.ebook-verse.tts-active').forEach(element => element.classList.remove('tts-active'));
    if (ayah) document.getElementById(`commentary-verse-${ayah}`)?.classList.add('tts-active');
  },

  updateUI() {
    const button = document.getElementById('deviceTtsBtn');
    const stopButton = document.getElementById('deviceTtsStop');
    const previousButton = document.getElementById('commentaryPlayerPrevious');
    const nextButton = document.getElementById('commentaryPlayerNext');
    const status = document.getElementById('deviceSpeechStatus');
    const verseLabel = document.getElementById('commentaryPlayerVerse');
    const range = document.getElementById('commentaryPlayerRange');
    const supported = this.isSupported();
    const maxVerse = this.getVerseCount(AppState.currentSurah);
    const selectedVerse = this.getSelectedVerse(AppState.currentSurah, maxVerse);

    if (button) {
      button.classList.toggle('is-active', this.isSpeaking || this.isPaused);
      button.disabled = !supported;
      button.innerHTML = !supported
        ? '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12.01" y2="8"></line><line x1="12" y1="12" x2="12" y2="16"></line></svg> Read aloud unavailable'
        : this.isSpeaking
          ? '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4" width="4" height="16" rx="1"></rect><rect x="14" y="4" width="4" height="16" rx="1"></rect></svg> Pause'
          : this.isPaused
            ? '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg> Resume'
            : '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg> Read aloud';
    }
    if (stopButton) stopButton.hidden = !(this.isSpeaking || this.isPaused);
    if (previousButton) previousButton.disabled = selectedVerse <= 1;
    if (nextButton) nextButton.disabled = selectedVerse >= maxVerse;
    if (range) range.value = selectedVerse;
    if (verseLabel) verseLabel.textContent = `Verse ${selectedVerse} of ${maxVerse}`;
    document.querySelectorAll('[data-commentary-verse]').forEach(item => {
      const isSelected = parseInt(item.dataset.commentaryVerse, 10) === selectedVerse;
      item.classList.toggle('selected', isSelected);
      item.setAttribute('aria-current', isSelected ? 'true' : 'false');
    });
    if (status) {
      if (this.isSpeaking || this.isPaused) {
        status.textContent = this.activeAyah
          ? `${this.isPaused ? 'Paused at' : 'Reading'} verse ${this.activeAyah}. Use Previous, Next, the slider, or the verse navigator to move.`
          : `${this.isPaused ? 'Paused during' : 'Reading'} the surah introduction.`;
      } else if (!supported) {
        status.textContent = 'Read aloud is unavailable because this browser has not exposed its built-in speech feature.';
      } else {
        status.textContent = 'Ready to read aloud with your browser’s built-in voice. No sign-in, download, or setup is needed.';
      }
    }
  }
};

function markdownToSpeechText(markdown) {
  return String(markdown || '')
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
    .replace(/[`*_#>]/g, '')
    .replace(/\n+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

function splitSpeechText(text, maxLength = 220) {
  const sentences = String(text || '').match(/[^.!?]+[.!?]+|[^.!?]+$/g) || [];
  const chunks = [];
  let current = '';
  const pushCurrent = () => { if (current.trim()) chunks.push(current.trim()); current = ''; };
  sentences.forEach(sentence => {
    const trimmed = sentence.trim();
    if (!trimmed) return;
    if ((current + ' ' + trimmed).trim().length <= maxLength) {
      current = `${current} ${trimmed}`.trim();
      return;
    }
    pushCurrent();
    if (trimmed.length <= maxLength) {
      current = trimmed;
      return;
    }
    const words = trimmed.split(/\s+/);
    words.forEach(word => {
      if ((current + ' ' + word).trim().length > maxLength) pushCurrent();
      current = `${current} ${word}`.trim();
    });
  });
  pushCurrent();
  return chunks;
}

/* ================================================
   17. OFFLINE STORAGE & DOWNLOAD MANAGER
================================================ */
const CHAPTER_SIZES_KB = {"1":53,"2":2376,"3":1367,"4":1324,"5":924,"6":1088,"7":1750,"8":566,"9":870,"10":691,"11":798,"12":823,"13":290,"14":325,"15":616,"16":919,"17":804,"18":715,"19":644,"20":1086,"21":804,"22":678,"23":746,"24":485,"25":518,"26":1435,"27":602,"28":568,"29":550,"30":458,"31":224,"32":196,"33":476,"34":365,"35":298,"36":556,"37":1744,"38":569,"39":545,"40":616,"41":377,"42":359,"43":575,"44":421,"45":236,"46":232,"47":252,"48":193,"49":119,"50":286,"51":382,"52":319,"53":420,"54":314,"55":478,"56":613,"57":206,"58":180,"59":196,"60":99,"61":95,"62":72,"63":81,"64":117,"65":84,"66":82,"67":199,"68":328,"69":392,"70":328,"71":190,"72":189,"73":138,"74":377,"75":240,"76":192,"77":317,"78":272,"79":329,"80":261,"81":175,"82":122,"83":236,"84":160,"85":131,"86":98,"87":110,"88":149,"89":169,"90":144,"91":111,"92":181,"93":86,"94":64,"95":51,"96":124,"97":35,"98":57,"99":54,"100":83,"101":73,"102":54,"103":24,"104":57,"105":32,"106":27,"107":42,"108":21,"109":39,"110":30,"111":44,"112":38,"113":43,"114":50};

const OfflineManager = {
  CACHE_NAME: 'quran-reader-v2.2.0',
  cachedChapters: new Set(),
  isDownloadingAll: false,
  shouldCancelDownloadAll: false,
  activeFilter: 'all',
  searchQuery: '',

  async init() {
    await this.scanCachedChapters();
    this.updateHeaderBadge();
  },

  async getCache() {
    if (!('caches' in window)) return null;
    try {
      return await caches.open(this.CACHE_NAME);
    } catch (e) {
      console.warn('[OfflineManager] Cache API error:', e);
      return null;
    }
  },

  async scanCachedChapters() {
    const cache = await this.getCache();
    if (!cache) return;
    this.cachedChapters.clear();
    try {
      const keys = await cache.keys();
      for (const req of keys) {
        const url = req.url || '';
        const match = url.match(/data\/tafsir_(\d{3})\.json/);
        if (match) {
          this.cachedChapters.add(parseInt(match[1], 10));
        }
      }
    } catch (e) {
      console.warn('[OfflineManager] scan keys error:', e);
    }
    this.updateHeaderBadge();
    this.updateSummaryStats();
  },

  isChapterCached(num) {
    return this.cachedChapters.has(num);
  },

  updateHeaderBadge() {
    const badge = document.getElementById('offlineHeaderBadge');
    if (!badge) return;
    const count = this.cachedChapters.size;
    badge.textContent = count > 0 ? `${count}` : '0';
    badge.title = `${count} of 114 chapters downloaded for offline reading`;
    if (count > 0) {
      badge.style.background = 'var(--accent)';
      badge.style.color = '#fff';
    } else {
      badge.style.background = 'var(--accent-bg)';
      badge.style.color = 'var(--accent)';
    }
  },

  updateSummaryStats() {
    const countEl = document.getElementById('dlCountText');
    const sizeEl = document.getElementById('dlSizeText');
    const savedCountEl = document.getElementById('dlTabSavedCount');
    const count = this.cachedChapters.size;
    if (countEl) countEl.textContent = `${count} / 114`;
    if (savedCountEl) savedCountEl.textContent = `${count}`;

    let totalKb = 0;
    this.cachedChapters.forEach(num => {
      totalKb += CHAPTER_SIZES_KB[num] || 150;
    });

    if (sizeEl) {
      if (totalKb >= 1024) {
        sizeEl.textContent = `${(totalKb / 1024).toFixed(1)} MB`;
      } else {
        sizeEl.textContent = `${totalKb} KB`;
      }
    }
  },

  async downloadChapter(num) {
    const cache = await this.getCache();
    if (!cache) {
      showToast('Offline cache is not supported in this browser.', 'info');
      return false;
    }
    const pad = String(num).padStart(3, '0');
    const tafsirUrl = `data/tafsir_${pad}.json`;
    const chapterUrl = `data/chapter_${pad}.js`;

    const rowBtn = document.getElementById(`dlBtn_${num}`);
    if (rowBtn) {
      rowBtn.disabled = true;
      rowBtn.innerHTML = '<span class="skeleton" style="display:inline-block;width:60px;height:16px;"></span>';
    }

    try {
      const [tRes, cRes] = await Promise.all([
        fetch(tafsirUrl),
        fetch(chapterUrl)
      ]);
      if (!tRes.ok || !cRes.ok) throw new Error('Fetch failed');

      await Promise.all([
        cache.put(tafsirUrl, tRes),
        cache.put(chapterUrl, cRes)
      ]);

      this.cachedChapters.add(num);
      this.updateHeaderBadge();
      this.updateSummaryStats();
      this.renderDownloadsList();
      this.updateSurahDetailButton(num);

      const ch = chaptersData.find(c => c.number === num);
      showToast(`Surah ${ch ? ch.name_en : num} saved offline!`, 'success');
      return true;
    } catch (err) {
      console.error(`Download failed for Surah ${num}:`, err);
      showToast(`Download failed for Surah ${num}. Check connection.`, 'info');
      if (rowBtn) {
        rowBtn.disabled = false;
        rowBtn.innerHTML = '📥 Download';
      }
      return false;
    }
  },

  async deleteChapter(num) {
    const cache = await this.getCache();
    if (!cache) return;
    const pad = String(num).padStart(3, '0');
    try {
      await Promise.all([
        cache.delete(`data/tafsir_${pad}.json`),
        cache.delete(`data/chapter_${pad}.js`)
      ]);
      this.cachedChapters.delete(num);
      this.updateHeaderBadge();
      this.updateSummaryStats();
      this.renderDownloadsList();
      this.updateSurahDetailButton(num);

      const ch = chaptersData.find(c => c.number === num);
      showToast(`Removed Surah ${ch ? ch.name_en : num} from offline storage.`, 'info');
    } catch (err) {
      console.error(`Delete failed for Surah ${num}:`, err);
    }
  },

  async toggleChapterFromDetail(num) {
    if (this.isChapterCached(num)) {
      if (confirm(`Remove Surah ${num} from offline storage?`)) {
        await this.deleteChapter(num);
      }
    } else {
      await this.downloadChapter(num);
    }
  },

  updateSurahDetailButton(num) {
    if (AppState.currentSurah !== num) return;
    const btn = document.getElementById('surahOfflineBtn');
    if (!btn) return;
    const isCached = this.isChapterCached(num);
    btn.className = `surah-offline-btn ${isCached ? 'cached' : ''}`;
    btn.title = isCached ? 'Chapter saved offline (click to remove)' : 'Save chapter for offline reading';
    btn.innerHTML = `
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        ${isCached
          ? '<polyline points="20 6 9 17 4 12"/>'
          : '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>'}
      </svg>
      <span>${isCached ? 'Saved Offline' : 'Save Offline'}</span>
    `;
  },

  async toggleDownloadAll() {
    if (this.isDownloadingAll) {
      this.shouldCancelDownloadAll = true;
      const btnText = document.getElementById('dlAllBtnText');
      if (btnText) btnText.textContent = 'Cancelling...';
      return;
    }

    const unCached = [];
    for (let i = 1; i <= 114; i++) {
      if (!this.cachedChapters.has(i)) unCached.push(i);
    }

    if (unCached.length === 0) {
      showToast('All 114 chapters are already saved offline!', 'success');
      return;
    }

    if (!confirm(`Download ${unCached.length} remaining chapters (~${(unCached.length * 0.35).toFixed(1)} MB)? This will make the entire Quran available offline.`)) {
      return;
    }

    this.isDownloadingAll = true;
    this.shouldCancelDownloadAll = false;

    const progressWrap = document.getElementById('dlProgressWrap');
    const progressFill = document.getElementById('dlProgressFill');
    const progressLabel = document.getElementById('dlProgressLabel');
    const progressPercent = document.getElementById('dlProgressPercent');
    const dlAllBtn = document.getElementById('dlAllBtn');
    const dlAllBtnText = document.getElementById('dlAllBtnText');

    if (progressWrap) progressWrap.style.display = 'block';
    if (dlAllBtnText) dlAllBtnText.textContent = 'Cancel Download';
    if (dlAllBtn) dlAllBtn.classList.add('danger');

    let completed = 0;
    const total = unCached.length;

    for (const num of unCached) {
      if (this.shouldCancelDownloadAll) {
        showToast('Download cancelled.', 'info');
        break;
      }

      const ch = chaptersData.find(c => c.number === num);
      if (progressLabel) progressLabel.textContent = `Downloading ${num}/114: ${ch ? ch.name_en : ''}...`;

      await this.downloadChapter(num);
      completed++;

      const pct = Math.round((completed / total) * 100);
      if (progressFill) progressFill.style.width = `${pct}%`;
      if (progressPercent) progressPercent.textContent = `${pct}%`;
    }

    this.isDownloadingAll = false;
    this.shouldCancelDownloadAll = false;

    if (progressWrap) setTimeout(() => { progressWrap.style.display = 'none'; }, 1500);
    if (dlAllBtn) dlAllBtn.classList.remove('danger');
    if (dlAllBtnText) dlAllBtnText.textContent = this.cachedChapters.size === 114 ? '✓ All Chapters Saved' : 'Download All Chapters (~40 MB)';

    if (this.cachedChapters.size === 114) {
      showToast('All 114 chapters downloaded for offline reading!', 'success');
    }
  },

  async confirmClearAll() {
    if (this.cachedChapters.size === 0) {
      showToast('No offline chapters to clear.', 'info');
      return;
    }
    if (!confirm(`Remove all ${this.cachedChapters.size} downloaded chapters from offline storage? You will need an internet connection to read them again.`)) {
      return;
    }
    const cache = await this.getCache();
    if (!cache) return;
    try {
      const keys = await cache.keys();
      for (const req of keys) {
        if (req.url.includes('/data/tafsir_') || req.url.includes('/data/chapter_')) {
          await cache.delete(req);
        }
      }
      this.cachedChapters.clear();
      this.updateHeaderBadge();
      this.updateSummaryStats();
      this.renderDownloadsList();
      if (AppState.currentSurah) this.updateSurahDetailButton(AppState.currentSurah);
      showToast('All offline downloads cleared.', 'info');
    } catch (e) {
      console.error('Clear failed:', e);
    }
  },

  handleSearch(query) {
    this.searchQuery = (query || '').trim().toLowerCase();
    this.renderDownloadsList();
  },

  setFilter(filter) {
    this.activeFilter = filter;
    document.querySelectorAll('.dl-tab-btn').forEach(btn => btn.classList.remove('active'));
    if (filter === 'all') document.getElementById('dlTabAll')?.classList.add('active');
    if (filter === 'saved') document.getElementById('dlTabSaved')?.classList.add('active');
    if (filter === 'pending') document.getElementById('dlTabPending')?.classList.add('active');
    this.renderDownloadsList();
  },

  renderDownloadsList() {
    const listEl = document.getElementById('downloadsList');
    if (!listEl) return;

    let chapters = chaptersData || [];

    if (this.activeFilter === 'saved') {
      chapters = chapters.filter(c => this.cachedChapters.has(c.number));
    } else if (this.activeFilter === 'pending') {
      chapters = chapters.filter(c => !this.cachedChapters.has(c.number));
    }

    if (this.searchQuery) {
      const q = this.searchQuery;
      chapters = chapters.filter(c =>
        c.number.toString().includes(q) ||
        (c.name_en && c.name_en.toLowerCase().includes(q)) ||
        (c.meaning && c.meaning.toLowerCase().includes(q)) ||
        (c.name_ar && c.name_ar.includes(q))
      );
    }

    if (chapters.length === 0) {
      listEl.innerHTML = `<div style="text-align:center;padding:32px 16px;color:var(--text-dim);font-size:14px;">No chapters found.</div>`;
      return;
    }

    let html = '';
    for (const ch of chapters) {
      const isCached = this.cachedChapters.has(ch.number);
      const sizeKb = CHAPTER_SIZES_KB[ch.number] || 100;
      const sizeStr = sizeKb >= 1000 ? `${(sizeKb / 1024).toFixed(1)} MB` : `${sizeKb} KB`;

      html += `
        <div class="dl-chapter-row" id="dlRow_${ch.number}">
          <div class="dl-chapter-left">
            <div class="dl-chapter-num">${ch.number}</div>
            <div class="dl-chapter-info">
              <div class="dl-chapter-name">
                ${escapeHtml(ch.name_en)} <span class="arabic-text dl-chapter-ar">${escapeHtml(ch.name_ar)}</span>
              </div>
              <div class="dl-chapter-meta">${ch.verses} verses • ${sizeStr} • ${ch.type}</div>
            </div>
          </div>
          <div class="dl-chapter-actions">
            ${isCached
              ? `<span class="dl-btn saved">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
                  Downloaded
                </span>
                <button class="dl-btn delete" onclick="OfflineManager.deleteChapter(${ch.number})" title="Remove from offline storage" aria-label="Delete download">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
                </button>`
              : `<button class="dl-btn download" id="dlBtn_${ch.number}" onclick="OfflineManager.downloadChapter(${ch.number})">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
                  Download
                </button>`}
          </div>
        </div>
      `;
    }

    listEl.innerHTML = html;
  }
};

/* ================================================
   17. EVENT LISTENERS
================================================ */
document.getElementById('modal').addEventListener('click', function(e) { if (e.target === this) closeModal(); });
document.getElementById('aboutModal').addEventListener('click', function(e) { if (e.target === this) closeAboutModal(); });
document.getElementById('fontSizeModal').addEventListener('click', function(e) { if (e.target === this) closeFontSizeModal(); });
document.getElementById('downloadsModal').addEventListener('click', function(e) { if (e.target === this) closeDownloadsModal(); });

document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') { closeModal(); closeAboutModal(); closeFontSizeModal(); closeDownloadsModal(); closeThemeMenu(); }
});

document.addEventListener('click', function(e) {
  const switcher = document.getElementById('themeSwitcher');
  if (switcher && !switcher.contains(e.target)) closeThemeMenu();
  if (e.target && e.target.classList.contains('phrase-chip')) {
    const dataset = e.target.dataset;
    showExplanation(parseInt(dataset.surah), parseInt(dataset.ayah));
  }
});

window.addEventListener('popstate', function(e) {
  if (e.state && e.state.view === 'commentary' && e.state.surah) {
    openCompleteCommentary(e.state.surah, { fromHistory: true });
  } else if (e.state && e.state.view === 'detail' && e.state.surah) {
    openSurah(e.state.surah, { fromHistory: true });
  } else {
    if (AppState.currentView === 'detail' && AppState.currentSurah) {
      const ayah = getTopVisibleVerseNum();
      if (ayah) addToHistory(AppState.currentSurah, ayah);
    } else if (AppState.currentView === 'commentary' && AppState.currentSurah) {
      const ayah = getTopVisibleCommentaryVerseNum();
      if (ayah) addToHistory(AppState.currentSurah, ayah);
    }
    DeviceSpeech.stop(true);
    AudioPlayer.stop();
    AppState.currentView = 'list';
    AppState.currentSurah = null;
    AppState.currentSurahData = null;
    renderApp();
  }
});

window.addEventListener('scroll', function() {
  updateReadingProgress();
  updateScrollTopBtn();
}, { passive: true });

function handleInitialHash() {
  const hash = window.location.hash;

  if (hash === '#bookmarks') {
    AppState.homeTab = 'bookmarks';
    renderApp();
    return;
  }

  if (hash === '#history') {
    AppState.homeTab = 'history';
    renderApp();
    return;
  }

  const commentaryMatch = hash.match(/^#surah-(\d+)-commentary$/);
  if (commentaryMatch) {
    const num = parseInt(commentaryMatch[1], 10);
    if (num >= 1 && num <= 114) {
      openCompleteCommentary(num, { fromHistory: true });
      return;
    }
  }

  const surahMatch = hash.match(/^#surah-(\d+)(?:-verse-(\d+))?$/);
  if (surahMatch) {
    const num = parseInt(surahMatch[1], 10);
    const ayah = surahMatch[2] ? parseInt(surahMatch[2], 10) : null;
    if (num >= 1 && num <= 114) {
      openSurah(num, { fromHistory: true }).then(() => {
        if (ayah) setTimeout(() => scrollToVerse(ayah), 120);
      });
      return;
    }
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
DeviceSpeech.init();
initTheme();
initFontSizes();
OfflineManager.init();
handleInitialHash();

if ('requestIdleCallback' in window) requestIdleCallback(prefetchPopularChapters);
else setTimeout(prefetchPopularChapters, 5000);
