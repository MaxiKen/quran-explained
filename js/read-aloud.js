/* =========================================================
   READ ALOUD — commentary player (bottom dock + floating orb)
   ---------------------------------------------------------
   A media-player style companion for the commentary eBook:

   • mini bar pinned to the bottom while you keep reading
   • expand it for the karaoke / lyrics view — the spoken line
     is highlighted and the page itself scrolls as it is read
   • skip to previous / next verse, replay a line, jump to any
     verse, speed, voice, repeat and a sleep timer
   • the ✕ at the top-right cancels the panel and leaves a
     small logo orb on screen — tap it to bring the player back
   • when the surah finishes the orb stays, so you can replay

   Uses the browser's own speech engine: no sign-in, no
   download, no network round trip for the text.
   ========================================================= */

const READ_ALOUD_STORE = 'quran-reader-read-aloud';
const READ_ALOUD_BASE_RATE = 0.95;
const READ_ALOUD_RATES = [0.75, 0.9, 1, 1.15, 1.35, 1.6];
const SLEEP_OPTIONS = [0, 5, 10, 20, 30, 45, 60];
const READ_ALOUD_TTL = 1000 * 60 * 60 * 12; /* a saved place is good for 12h */

const ReadAloud = {
  /* ---------- state ---------- */
  activeSurah: null,
  ayah: null,              /* null while the surah introduction is read */
  kind: null,              /* 'intro' | 'verse' */
  lines: [],
  lineIndex: 0,
  isSpeaking: false,
  isPaused: false,
  hasSession: false,
  mode: 'off',             /* 'mini' | 'full' | 'off' */
  follow: true,
  focus: false,
  repeatVerse: false,
  rate: 1,
  voiceURI: null,
  sleepMinutes: 0,
  sleepEndsAt: 0,
  selectedSurah: null,
  selectedAyah: 1,
  session: 0,
  utterance: null,
  voices: [],
  orbY: null,

  /* ---------- internals ---------- */
  _unitCache: {},
  _lineEls: [],
  _lineTops: [],
  _rafId: null,
  _scrollAnim: null,
  _userScrollAt: 0,
  _lastBoundary: 0,
  _sleepTimer: null,
  _sleepTick: null,
  _watchdog: null,
  _lastProgressAt: 0,
  _wakeLock: null,

  /* =========================================================
     SETUP
     ========================================================= */
  init() {
    this._injectDock();
    this._injectOrb();
    this._loadPreferences();
    this._wireChrome();
    this.initVoices();
    this.wireMediaHandlers();

    this._syncViewClass();
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'visible' && this.isSpeaking) this._requestWakeLock();
      else if (document.visibilityState === 'hidden') this._releaseWakeLock();
    });
    window.addEventListener('pagehide', () => this.persist());
    window.addEventListener('beforeunload', () => this.persist());
    window.addEventListener('resize', () => { this._measureLines(); });
  },

  _syncViewClass() {
    const onCommentary = (typeof AppState !== 'undefined' && AppState.currentView === 'commentary');
    document.body.classList.toggle('view-commentary', onCommentary);
  },

  isSupported() {
    return typeof window !== 'undefined'
      && typeof window.speechSynthesis !== 'undefined'
      && typeof window.SpeechSynthesisUtterance === 'function';
  },

  initVoices() {
    if (!this.isSupported()) return;
    const refresh = () => {
      this.voices = window.speechSynthesis.getVoices() || [];
      this._renderVoiceOptions();
    };
    refresh();
    window.speechSynthesis.onvoiceschanged = refresh;
  },

  getNarrationVoice() {
    const voices = this.voices.length ? this.voices : (this.isSupported() ? window.speechSynthesis.getVoices() : []);
    if (this.voiceURI) {
      const picked = voices.find((voice) => voice.voiceURI === this.voiceURI);
      if (picked) return picked;
    }
    const english = voices.filter((voice) => /^en(?:[-_]|$)/i.test(voice.lang || ''));
    const local = english.filter((voice) => voice.localService);
    return local.find((voice) => voice.default) || local[0]
      || english.find((voice) => voice.default) || english[0]
      || voices.find((voice) => voice.default) || voices[0] || null;
  },

  /* =========================================================
     DOM CHROME
     ========================================================= */
  _injectDock() {
    if (document.getElementById('raDock')) return;
    const dock = document.createElement('section');
    dock.className = 'ra-dock';
    dock.id = 'raDock';
    dock.setAttribute('data-mode', 'off');
    dock.setAttribute('aria-label', 'Commentary read aloud player');
    dock.innerHTML = `
      <div class="ra-progress" aria-hidden="true"><span class="ra-progress-fill" id="raProgressFill"></span></div>

      <div class="ra-mini" id="raMini">
        <button class="ra-mini-verse" id="raMiniVerse" type="button" title="Open the read aloud player">1</button>
        <div class="ra-mini-copy">
          <strong id="raMiniTitle">Commentary read aloud</strong>
          <span id="raMiniLine">Ready when you are</span>
        </div>
        <div class="ra-mini-actions">
          <button class="ra-icon-btn" id="raMiniPrev" type="button" title="Previous verse" aria-label="Previous verse">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="19 20 9 12 19 4 19 20" fill="currentColor" stroke="none"/><line x1="5" y1="19" x2="5" y2="5"/></svg>
          </button>
          <button class="ra-icon-btn ra-play" id="raMiniPlay" type="button" title="Play or pause" aria-label="Play or pause"></button>
          <button class="ra-icon-btn" id="raMiniNext" type="button" title="Next verse" aria-label="Next verse">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" stroke="none"><polygon points="5 4 15 12 5 20 5 4"/><line x1="19" y1="5" x2="19" y2="19" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
          </button>
          <button class="ra-icon-btn" id="raMiniExpand" type="button" title="Expand player" aria-label="Expand player">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><polyline points="18 15 12 9 6 15"/></svg>
          </button>
          <button class="ra-icon-btn ra-close" id="raMiniClose" type="button" title="Cancel and collapse" aria-label="Cancel and collapse">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
        </div>
      </div>

      <div class="ra-full" id="raFull">
        <header class="ra-head">
          <span class="ra-head-icon" aria-hidden="true">
            <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" y1="19" x2="12" y2="22"></line><line x1="8" y1="22" x2="16" y2="22"></line></svg>
          </span>
          <div class="ra-head-copy">
            <p class="ra-eyebrow" aria-live="polite">Read aloud · <span id="raEyebrowState">ready</span></p>
            <h2 id="raTitle">Commentary</h2>
          </div>
          <output class="ra-chip" id="raVerseChip">Verse 1</output>
          <button class="ra-cancel" id="raCancel" type="button" title="Cancel read aloud" aria-label="Cancel read aloud">
            <span class="ra-cancel-x" aria-hidden="true">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
            </span>
            <span class="ra-cancel-label">Cancel</span>
          </button>
        </header>

        <div class="ra-scrub">
          <span class="ra-scrub-time" id="raElapsed">0:00</span>
          <div class="ra-scrub-bar" id="raScrubBar" role="progressbar" aria-label="Progress through this verse" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0">
            <span class="ra-scrub-fill" id="raScrubFill"></span>
          </div>
          <span class="ra-scrub-time" id="raRemaining">—</span>
        </div>

        <div class="ra-controls">
          <button class="ra-ctrl" id="raRepeat" type="button" title="Repeat this verse" aria-pressed="false">
            <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="17 1 21 5 17 9"/><path d="M3 11V9a4 4 0 0 1 4-4h14"/><polyline points="7 23 3 19 7 15"/><path d="M21 13v2a4 4 0 0 1-4 4H3"/></svg>
          </button>
          <button class="ra-ctrl" id="raPrevVerse" type="button" title="Previous verse" aria-label="Previous verse">
            <svg width="19" height="19" viewBox="0 0 24 24" fill="currentColor" stroke="none"><polygon points="19 20 9 12 19 4 19 20"/><line x1="5" y1="19" x2="5" y2="5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
          </button>
          <button class="ra-ctrl ra-ctrl-play" id="raPlay" type="button" title="Play or pause (Space)" aria-label="Play or pause"></button>
          <button class="ra-ctrl" id="raNextVerse" type="button" title="Next verse" aria-label="Next verse">
            <svg width="19" height="19" viewBox="0 0 24 24" fill="currentColor" stroke="none"><polygon points="5 4 15 12 5 20 5 4"/><line x1="19" y1="5" x2="19" y2="19" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
          </button>
          <button class="ra-ctrl" id="raSleep" type="button" title="Sleep timer" aria-label="Sleep timer">
            <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
          </button>
        </div>

        <div class="ra-seek">
          <label for="raVerseRange">Go to verse</label>
          <input id="raVerseRange" type="range" min="1" max="7" step="1" value="1" aria-label="Jump to verse">
          <output id="raVerseTotal">1 / 7</output>
        </div>

        <details class="ra-more">
          <summary>Player options <small>voice, speed, scrolling</small></summary>
          <div class="ra-options">
            <label class="ra-option">
              <span>Speed</span>
              <select id="raRate"></select>
            </label>
            <label class="ra-option ra-option-voice">
              <span>Voice</span>
              <select id="raVoice"></select>
            </label>
            <button class="ra-toggle" id="raFollow" type="button" aria-pressed="true">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="7 13 12 18 17 13"/><polyline points="7 6 12 11 17 6"/></svg>
              Follow page
            </button>
            <button class="ra-toggle" id="raFocus" type="button" aria-pressed="false">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="3.4"/></svg>
              Dim page
            </button>
            <button class="ra-toggle" id="raReplay" type="button">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"/></svg>
              Replay line
            </button>
          </div>
          <div class="ra-navigator" id="raNavigator" role="navigation" aria-label="Jump to verse commentary"></div>
        </details>

        <footer class="ra-foot">
          <button class="ra-foot-btn" id="raOpenView" type="button">Open commentary</button>
          <button class="ra-foot-btn ra-foot-muted" id="raReopenMini" type="button">Mini bar</button>
          <button class="ra-foot-btn ra-foot-danger" id="raEnd" type="button">End reading</button>
        </footer>
      </div>`;
    document.body.appendChild(dock);
  },

  _injectOrb() {
    /* floating orb disabled — read aloud is part of full commentary only */
  },

  _saveOrbPosition() {},

  _wireChrome() {
    const on = (id, handler) => {
      const el = document.getElementById(id);
      if (el) el.addEventListener('click', (event) => { event.preventDefault(); handler(event); });
    };
    on('raMiniExpand', () => this.setMode('full'));
    on('raMiniClose', () => this.cancel());
    on('raCancel', () => this.cancel());
    on('raMiniPlay', () => this.togglePlay());
    on('raPlay', () => this.togglePlay());
    on('raMiniPrev', () => this.prevVerse());
    on('raMiniNext', () => this.nextVerse());
    on('raPrevVerse', () => this.prevVerse());
    on('raNextVerse', () => this.nextVerse());
    on('raMiniVerse', () => this.setMode(this.mode === 'full' ? 'mini' : 'full'));
    on('raRepeat', () => this.toggleRepeat());
    on('raSleep', () => this.cycleSleep());
    on('raFollow', () => this.toggleFollow());
    on('raFocus', () => this.toggleFocus());
    on('raReplay', () => this.replayLine());
    on('raReopenMini', () => this.setMode('mini'));
    on('raOpenView', () => this.openCommentary());
    on('raEnd', () => this.endSession());

    const range = document.getElementById('raVerseRange');
    if (range) {
      range.addEventListener('input', () => this.previewVerse(this.activeSurah || AppState.currentSurah, parseInt(range.value, 10)));
      range.addEventListener('change', () => this.seekVerse(this.activeSurah || AppState.currentSurah, parseInt(range.value, 10)));
    }
    const rateSelect = document.getElementById('raRate');
    if (rateSelect) {
      rateSelect.innerHTML = READ_ALOUD_RATES.map((value) => `<option value="${value}">${value}×${value === 1 ? ' normal' : ''}</option>`).join('');
      rateSelect.addEventListener('change', () => this.setRate(parseFloat(rateSelect.value)));
    }
    /* a manual scroll means the reader wants control — stop fighting them */
    const mark = () => { this._userScrollAt = Date.now(); };
    window.addEventListener('wheel', mark, { passive: true });
    window.addEventListener('touchstart', mark, { passive: true });
    window.addEventListener('keydown', (event) => { if (['ArrowUp', 'ArrowDown', 'PageUp', 'PageDown', 'Home', 'End'].indexOf(event.key) !== -1) mark(); });
  },

  _renderVoiceOptions() {
    const select = document.getElementById('raVoice');
    if (!select) return;
    const voices = (this.voices || []).filter((voice) => /^en(?:[-_]|$)/i.test(voice.lang || ''));
    const pool = voices.length ? voices : (this.voices || []).slice(0, 24);
    const current = this.voiceURI;
    select.innerHTML = `<option value="">Browser default</option>` + pool.map((voice) =>
      `<option value="${escapeAttr(voice.voiceURI)}">${escapeHtml(voice.name)} (${escapeHtml(voice.lang)})</option>`).join('');
    select.value = current || '';
  },

  /* =========================================================
     PREFERENCES + SAVED PLACE
     ========================================================= */
  _readStore() {
    try { return JSON.parse(localStorage.getItem(READ_ALOUD_STORE) || '{}') || {}; } catch (err) { return {}; }
  },

  _loadPreferences() {
    const saved = this._readStore();
    if (saved.rate) this.rate = saved.rate;
    if (typeof saved.follow === 'boolean') this.follow = saved.follow;
    if (typeof saved.focus === 'boolean') this.focus = saved.focus;
    if (typeof saved.repeatVerse === 'boolean') this.repeatVerse = saved.repeatVerse;
    if (saved.voiceURI) this.voiceURI = saved.voiceURI;
    if (saved.orbY) { this.orbY = saved.orbY; PlayerOrb.applyPosition(saved.orbY); }
    if (Number.isFinite(saved.sleepMinutes)) this.sleepMinutes = saved.sleepMinutes;
    const select = document.getElementById('raRate');
    if (select) select.value = String(this.rate);
    this._applyOrbPosition();
  },

  _applyOrbPosition() { PlayerOrb.applyPosition(this.orbY); },

  persist() {
    const store = this._readStore();
    const next = Object.assign(store, {
      surah: this.hasSession ? this.activeSurah : null,
      ayah: this.hasSession ? this.ayah : null,
      lineIndex: this.hasSession ? this.lineIndex : 0,
      mode: this.mode === 'off' ? 'off' : this.mode,
      rate: this.rate,
      follow: this.follow,
      focus: this.focus,
      repeatVerse: this.repeatVerse,
      voiceURI: this.voiceURI,
      sleepMinutes: this.sleepMinutes,
      savedAt: Date.now(),
    });
    try { localStorage.setItem(READ_ALOUD_STORE, JSON.stringify(next)); } catch (err) { /* no-op */ }
  },

  /** Re-offer yesterday's place after a reload (never auto-plays). */
  restoreSavedPlace() {
    const saved = this._readStore();
    if (!saved || !saved.surah || !saved.savedAt) return null;
    if (Date.now() - saved.savedAt > READ_ALOUD_TTL) return null;
    this.selectedSurah = saved.surah;
    this.selectedAyah = Math.max(1, parseInt(saved.ayah, 10) || 1);
    this.resumePoint = { surah: saved.surah, ayah: this.selectedAyah, lineIndex: saved.lineIndex || 0 };
    const onCommentary = (typeof AppState !== 'undefined' && AppState.currentView === 'commentary');
    if (onCommentary) {
      this.hasSession = true;
      this.activeSurah = saved.surah;
      this.ayah = this.selectedAyah;
      this.kind = 'verse';
      this.lineIndex = saved.lineIndex || 0;
      this.mode = saved.mode === 'full' ? 'full' : 'mini';
      this.updateUI();
    } else {
      this.hasSession = false;
      this.mode = 'off';
    }
    return this.resumePoint;
  },

  clearSavedPlace() {
    this.resumePoint = null;
    const store = this._readStore();
    store.surah = null; store.ayah = null; store.lineIndex = 0;
    try { localStorage.setItem(READ_ALOUD_STORE, JSON.stringify(store)); } catch (err) { /* no-op */ }
  },

  /* =========================================================
     CONTENT — verses are built lazily so a 286-verse surah
     starts speaking immediately instead of building text.
     ========================================================= */
  verseCount(surahNum) {
    const ch = (window.chaptersData || []).find((chapter) => chapter.number === surahNum);
    return ch ? ch.verses : 1;
  },

  hasData(surahNum) {
    return !!(loadedChapters[surahNum] && loadedTafsir[surahNum]);
  },

  ensureData(surahNum) {
    if (this.hasData(surahNum)) return Promise.resolve();
    return Promise.all([loadChapterData(surahNum), loadTafsirData(surahNum)]).then(() => undefined);
  },

  translationFor(surahNum, ayah) {
    const verse = getVerseData(surahNum, ayah);
    return verse ? getVerseEnglish(verse) : '';
  },

  unitFor(surahNum, ayah) {
    const cacheKey = `${surahNum}:${ayah == null ? 'intro' : ayah}`;
    if (this._unitCache[cacheKey]) return this._unitCache[cacheKey];
    const tafsir = loadedTafsir[surahNum];
    if (!tafsir) return null;
    const lines = [];
    if (ayah == null) {
      const intro = getSurahIntro(tafsir);
      if (!intro) return null;
      const ch = (window.chaptersData || []).find((chapter) => chapter.number === surahNum);
      splitSpeechText(`Surah ${ch ? ch.name_en : surahNum}. Introduction. ${markdownToSpeechText(intro)}`)
        .forEach((text, index) => lines.push({
          ayah: null,
          speak: text,
          show: index === 0 ? text.replace(/^Surah [^.]*\. Introduction\.?/, 'Surah introduction').trim() : text,
          label: 'Introduction',
        }));
    } else {
      const commentary = getVerseCommentary(tafsir, ayah);
      if (!commentary) return null;
      const translation = this.translationFor(surahNum, ayah);
      lines.push({
        ayah,
        speak: `Verse ${ayah}. ${translation}`,
        show: translation,
        label: `Verse ${ayah}`,
        isTranslation: true,
      });
      splitSpeechText(`Commentary. ${markdownToSpeechText(commentary)}`).forEach((text, index) => lines.push({
        ayah,
        speak: text,
        show: text.replace(/^Commentary\.\s*/, ''),
        label: `Verse ${ayah}`,
        first: index === 0,
      }));
    }
    this._unitCache[cacheKey] = lines;
    return lines;
  },

  nextVerseWithCommentary(surahNum, fromVerse) {
    const tafsir = loadedTafsir[surahNum];
    if (!tafsir) return null;
    const total = this.verseCount(surahNum);
    for (let candidate = fromVerse + 1; candidate <= total; candidate += 1) {
      if (getVerseCommentary(tafsir, candidate)) return candidate;
    }
    return null;
  },

  prevVerseWithCommentary(surahNum, fromVerse) {
    const tafsir = loadedTafsir[surahNum];
    if (!tafsir) return null;
    for (let candidate = fromVerse - 1; candidate >= 1; candidate -= 1) {
      if (getVerseCommentary(tafsir, candidate)) return candidate;
    }
    return null;
  },

  /* =========================================================
     PLAYBACK
     ========================================================= */
  async start(surahNum, verse, options = {}) {
    if (!this.isSupported()) {
      if (typeof showToast === 'function') showToast('This browser has no built-in read aloud voice.', 'info');
      return false;
    }
    /* Read aloud lives only inside the full commentary page — steer there first */
    if (typeof AppState === 'undefined' || AppState.currentView !== 'commentary' || AppState.currentSurah !== surahNum) {
      if (typeof openCompleteCommentary === 'function') {
        openCompleteCommentary(surahNum);
        const target = Math.max(1, Math.min(this.verseCount(surahNum), parseInt(verse, 10) || 1));
        setTimeout(() => this.start(surahNum, target, options), 700);
        if (typeof showToast === 'function') showToast('Opening commentary — reading will start there', 'info');
        return true;
      }
    }
    const total = this.verseCount(surahNum);
    const targetVerse = Math.max(1, Math.min(total, parseInt(verse, 10) || 1));
    if (!options.skipDataCheck) {
      try { await this.ensureData(surahNum); } catch (err) { /* handled below */ }
    }
    if (!this.hasData(surahNum)) {
      if (typeof showToast === 'function') showToast('Commentary is still loading — try again in a moment.', 'info');
      return false;
    }
    if (window.AudioPlayer && AudioPlayer.isPlaying) AudioPlayer.stop();

    const keepIntro = targetVerse === 1 && !options.skipIntro;
    this.session += 1;
    if (this.isSupported()) window.speechSynthesis.cancel();
    this.activeSurah = surahNum;
    this.selectedSurah = surahNum;
    this.hasSession = true;
    this.isPaused = false;
    this.resumePoint = null;
    this._unitCache = {};
    this._setUnit(keepIntro ? null : targetVerse, options.lineIndex || 0);
    if (!this.lines.length) {
      this._setUnit(this.nextVerseWithCommentary(surahNum, 0) || targetVerse, 0);
    }
    this.isSpeaking = true;
    this.completed = false;
    if (this.mode === 'off') this.mode = 'mini';
    this._renderNavigator();
    this._speakCurrent();
    this._startWatchdog();
    this._requestWakeLock();
    this.updateUI();
    return true;
  },

  _setUnit(ayah, lineIndex) {
    this.kind = ayah == null ? 'intro' : 'verse';
    this.ayah = ayah;
    if (ayah != null) this.selectedAyah = ayah;
    this.lines = this.unitFor(this.activeSurah, ayah) || [];
    this.lineIndex = Math.max(0, Math.min(lineIndex || 0, Math.max(0, this.lines.length - 1)));
    this._cacheUnitEls();
  },

  toggle(surahNum) {
    if (this.activeSurah === surahNum && this.isSpeaking) { this.pause(); return; }
    if (this.activeSurah === surahNum && this.isPaused) { this.resume(); return; }
    if (this.activeSurah === surahNum && this.hasSession) {
      this.start(surahNum, this.ayah || this.getSelectedVerse(surahNum, this.verseCount(surahNum)), { skipIntro: (this.ayah || 1) > 1 });
      return;
    }
    const verse = this.getSelectedVerse(surahNum, this.verseCount(surahNum));
    this.start(surahNum, verse);
  },

  togglePlay() {
    if (!this.hasSession) { this.start(AppState.currentSurah || this.selectedSurah || 1, this.selectedAyah); return; }
    if (this.isSpeaking) this.pause();
    else if (this.isPaused) this.resume();
    else this.start(this.activeSurah, this.ayah == null ? 1 : this.ayah, { skipIntro: this.ayah != null });
  },

  pause() {
    if (!this.isSupported() || !this.isSpeaking) return;
    window.speechSynthesis.pause();
    this.isSpeaking = false;
    this.isPaused = true;
    this._mediaState('paused');
    this.updateUI();
  },

  resume() {
    if (!this.isSupported() || !this.isPaused) return;
    window.speechSynthesis.resume();
    this.isPaused = false;
    this.isSpeaking = true;
    this._mediaState('playing');
    this.updateUI();
  },

  _speakCurrent() {
    const line = this.lines[this.lineIndex];
    if (!line) { this._advance(); return; }
    const utterance = new SpeechSynthesisUtterance(line.speak);
    const voice = this.getNarrationVoice();
    if (voice) utterance.voice = voice;
    utterance.lang = voice && voice.lang ? voice.lang : 'en-US';
    utterance.rate = READ_ALOUD_BASE_RATE * this.rate;
    utterance.pitch = 1;
    this._utteranceSession = this.session;
    utterance.onboundary = (event) => this._onBoundary(event, line);
    utterance.onend = () => {
      if (this.session !== this._utteranceSession) return;
      this._lastProgressAt = Date.now();
      this._advance();
    };
    utterance.onerror = (event) => {
      const code = event && event.error;
      if (code === 'interrupted' || code === 'canceled') return;
      console.warn('[ReadAloud] speech error:', code);
      if (typeof showToast === 'function') showToast('Read aloud could not continue on this device.', 'info');
      this.finish();
    };
    this.utterance = utterance;
    try { window.speechSynthesis.speak(utterance); } catch (err) {
      if (typeof showToast === 'function') showToast('Read aloud is blocked by the browser right now.', 'info');
      this.finish();
      return;
    }
    this._lastProgressAt = Date.now();
    this._onLineStart(line);
    this.updateUI();
  },

  _onLineStart(line) {
    this._setActiveLine();
    this._followLine();
    this._mediaMetadata(line);
    this.persist();
  },

  _onBoundary(event, line) {
    if (!line) return;
    const now = Date.now();
    if (now - this._lastBoundary < 90) return;
    this._lastBoundary = now;
    const length = (line.speak || '').length || 1;
    const charIndex = Math.max(0, Math.min(length, event.charIndex || 0));
    const fraction = charIndex / length;
    this._paintLineProgress(fraction);
    this._followProgress(fraction);
  },

  _advance() {
    if (this.repeatVerse) {
      const last = this.lineIndex >= this.lines.length - 1;
      if (last && !(this._repeatGuardAt && Date.now() - this._repeatGuardAt < 900)) {
        this._repeatGuardAt = Date.now();
        this._setUnit(this.ayah, 0);
        this._onUnitChange();
        this._speakCurrent();
        return;
      }
    }
    if (this.lineIndex < this.lines.length - 1) {
      this.lineIndex += 1;
      this._onUnitChange();
      this._speakCurrent();
      return;
    }
    const nextVerse = this.ayah == null
      ? 1
      : this.nextVerseWithCommentary(this.activeSurah, this.ayah);
    if (!nextVerse) { this.finish(); return; }
    this._setUnit(nextVerse, 0);
    this._onUnitChange();
    this._speakCurrent();
  },

  _onUnitChange() {
    this._cacheUnitEls();
    this._setActiveLine();
    this.updateUI();
  },

  finish() {
    const wasActive = this.isSpeaking || this.isPaused;
    this.session += 1;
    if (this.isSupported()) window.speechSynthesis.cancel();
    this.isSpeaking = false;
    this.isPaused = false;
    this.utterance = null;
    this._stopWatchdog();
    this._clearSleep();
    this._releaseWakeLock();
    this._setActiveLine(true);
    this._mediaState('none');
    this.completed = wasActive;
    if (wasActive && typeof showToast === 'function') showToast('Commentary read aloud complete', 'success');
    this.setMode('off');
    this.updateOrb();
    this.persist();
    this.updateUI();
  },

  /** ✕ — stop talking, end session, close player dock. */
  cancel() {
    this.endSession();
  },

  endSession(options = {}) {
    this.session += 1;
    if (this.isSupported()) window.speechSynthesis.cancel();
    this.isSpeaking = false;
    this.isPaused = false;
    this.hasSession = false;
    this.completed = false;
    this.utterance = null;
    this.lines = [];
    this.lineIndex = 0;
    this.activeSurah = null;
    this.ayah = null;
    this.kind = null;
    this._stopWatchdog();
    this._clearSleep();
    this._releaseWakeLock();
    this._setActiveLine(true);
    this._mediaState('none');
    this.setMode('off');
    this.updateOrb();
    this.clearSavedPlace();
    this.updateUI();
    if (!options.silent && typeof showToast === 'function') showToast('Read aloud ended', 'info');
  },

  /** Kept for call sites that used the previous player. */
  stop(quiet) { this.endSession({ silent: quiet }); },

  /**
   * Moving to a different surah: stop talking and get out of the way,
   * but keep the place so the orb can hand it back later.
   */
  suspendForNavigation(nextSurah) {
    if (!this.hasSession) return;
    if (nextSurah != null && this.activeSurah === nextSurah) return;
    if (this.isSpeaking) this.pause();
    this.setMode('off');
    this.persist();
  },

  openFromOrb() {
    this.setMode(this.mode === 'off' ? 'mini' : this.mode);
    if (this.completed) { this.completed = false; this.start(this.activeSurah, 1); }
    this.updateUI();
  },

  setMode(mode) {
    this._syncViewClass();
    this.mode = mode;
    if (mode === 'full') this._renderNavigator();
    const onCommentary = typeof AppState !== 'undefined' && AppState.currentView === 'commentary';
    const dock = document.getElementById('raDock');
    const effective = onCommentary && this.hasSession ? mode : 'off';
    if (dock) dock.setAttribute('data-mode', effective);
    document.body.classList.toggle('ra-mini-open', onCommentary && this.hasSession && mode === 'mini');
    document.body.classList.toggle('ra-full-open', onCommentary && this.hasSession && mode === 'full');
    this.updateOrb();
    if (typeof updateScrollTopBtn === 'function') updateScrollTopBtn();
    if (typeof updateChromeSpacing === 'function') updateChromeSpacing();
  },

  openCommentary() {
    const surah = this.activeSurah;
    if (!surah) return;
    if (AppState.currentView !== 'commentary' || AppState.currentSurah !== surah) {
      Router.go({ view: 'commentary', surah }, { resume: true, force: true });
    }
    this.setMode('mini');
    const verse = this.ayah || this.selectedAyah;
    if (verse) setTimeout(() => this.scrollToVerse(verse, true), 240);
  },

  /* =========================================================
     NAVIGATION
     ========================================================= */
  getSelectedVerse(surahNum, maxVerse) {
    if (this.activeSurah === surahNum && this.ayah != null) this.selectedAyah = this.ayah;
    if (this.selectedSurah !== surahNum) {
      const saved = this._readStore();
      this.selectedSurah = surahNum;
      this.selectedAyah = saved.surah === surahNum ? (parseInt(saved.ayah, 10) || 1) : 1;
    }
    this.selectedAyah = Math.max(1, Math.min(maxVerse || 1, parseInt(this.selectedAyah, 10) || 1));
    return this.selectedAyah;
  },

  previewVerse(surahNum, verse) {
    this.selectedSurah = surahNum;
    this.selectedAyah = Math.max(1, Math.min(this.verseCount(surahNum), parseInt(verse, 10) || 1));
    const total = this.verseCount(surahNum);
    const chip = document.getElementById('raVerseChip');
    if (chip) chip.textContent = `Verse ${this.selectedAyah} of ${total}`;
    const out = document.getElementById('raVerseTotal');
    if (out) out.textContent = `${this.selectedAyah} / ${total}`;
  },

  /** Jump the play-head to a verse (also works while speaking). */
  seekVerse(surahNum, verse) {
    const total = this.verseCount(surahNum);
    const target = Math.max(1, Math.min(total, parseInt(verse, 10) || 1));
    this.selectedAyah = target;
    if (this.hasSession && this.activeSurah === surahNum) {
      const commentaryVerse = this._firstCommentedVerseAtOrAfter(surahNum, target) || target;
      this._setUnit(commentaryVerse, 0);
      if (this.isSpeaking || this.isPaused) {
        this.session += 1;
        if (this.isSupported()) window.speechSynthesis.cancel();
        this.isPaused = false;
        this.isSpeaking = true;
        this._speakCurrent();
      }
      this.scrollToVerse(commentaryVerse, true);
    } else {
      this.scrollToVerse(target, true);
    }
    this._renderNavigator();
    this.updateUI();
    this.persist();
  },

  selectVerse(surahNum, verse) {
    if (!this.hasSession || this.activeSurah !== surahNum) {
      this.selectedSurah = surahNum;
      this.selectedAyah = verse;
      this.scrollToVerse(verse, true);
      this.updateUI();
      return;
    }
    this.seekVerse(surahNum, verse);
  },

  _firstCommentedVerseAtOrAfter(surahNum, verse) {
    const tafsir = loadedTafsir[surahNum];
    if (!tafsir) return verse;
    const total = this.verseCount(surahNum);
    for (let candidate = verse; candidate <= total; candidate += 1) {
      if (getVerseCommentary(tafsir, candidate)) return candidate;
    }
    for (let candidate = verse - 1; candidate >= 1; candidate -= 1) {
      if (getVerseCommentary(tafsir, candidate)) return candidate;
    }
    return verse;
  },

  nextVerse() {
    if (!this.activeSurah) return;
    const base = this.ayah == null ? 0 : this.ayah;
    const next = this.nextVerseWithCommentary(this.activeSurah, base);
    if (!next) { if (typeof showToast === 'function') showToast('End of this commentary', 'info'); return; }
    this.seekVerse(this.activeSurah, next);
  },

  prevVerse() {
    if (!this.activeSurah) return;
    if (this.ayah == null) { this.seekVerse(this.activeSurah, 1); return; }
    const base = this.isPaused || this.isSpeaking ? this.ayah : this.ayah;
    const prev = this.prevVerseWithCommentary(this.activeSurah, base);
    if (!prev) { this.seekVerse(this.activeSurah, 1); return; }
    this.seekVerse(this.activeSurah, prev);
  },

  nextLine() {
    if (!this.lines.length) return;
    if (this.lineIndex < this.lines.length - 1) { this.lineIndex += 1; this._onUnitChange(); if (this.isSpeaking) { this.session += 1; window.speechSynthesis.cancel(); this._speakCurrent(); } }
    else this.nextVerse();
  },

  prevLine() {
    if (!this.lines.length) return;
    if (this.lineIndex > 0) {
      this.lineIndex -= 1;
      this._onUnitChange();
      if (this.isSpeaking) { this.session += 1; window.speechSynthesis.cancel(); this._speakCurrent(); }
    } else this.prevVerse();
  },

  replayLine() {
    if (!this.lines.length) return;
    this.session += 1;
    if (this.isSupported()) window.speechSynthesis.cancel();
    this.isPaused = false;
    this.isSpeaking = true;
    this._speakCurrent();
  },

  scrollToVerse(verse, smooth) {
    if (AppState.currentView !== 'commentary' || AppState.currentSurah !== this.activeSurah) return;
    const el = document.getElementById(`commentary-verse-${verse}`);
    if (!el) return;
    const headerH = ReadingMemory.headerHeight();
    const target = Math.max(0, el.getBoundingClientRect().top + window.scrollY - headerH - 16);
    this._scrollTo(target, smooth === false ? 0 : 520);
  },

  /* =========================================================
     OPTIONS
     ========================================================= */
  setRate(rate) {
    this.rate = READ_ALOUD_RATES.indexOf(rate) !== -1 ? rate : 1;
    const select = document.getElementById('raRate');
    if (select) select.value = String(this.rate);
    if (this.isSpeaking && this.lines[this.lineIndex]) this.replayLine();
    this.persist();
    if (typeof showToast === 'function') showToast(`Voice speed ${this.rate}×`, 'info');
  },

  setVoice(voiceURI) {
    this.voiceURI = voiceURI || null;
    if (this.isSpeaking) this.replayLine();
    this.persist();
  },

  toggleRepeat() {
    this.repeatVerse = !this.repeatVerse;
    const button = document.getElementById('raRepeat');
    if (button) { button.classList.toggle('active', this.repeatVerse); button.setAttribute('aria-pressed', String(this.repeatVerse)); }
    this.persist();
    if (typeof showToast === 'function') showToast(`Repeat verse ${this.repeatVerse ? 'on' : 'off'}`, 'info');
  },

  toggleFollow() {
    this.follow = !this.follow;
    const button = document.getElementById('raFollow');
    if (button) { button.classList.toggle('active', this.follow); button.setAttribute('aria-pressed', String(this.follow)); }
    this.persist();
    if (typeof showToast === 'function') showToast(this.follow ? 'The page will follow the reading' : 'Page following paused', 'info');
  },

  toggleFocus() {
    this.focus = !this.focus;
    const button = document.getElementById('raFocus');
    if (button) { button.classList.toggle('active', this.focus); button.setAttribute('aria-pressed', String(this.focus)); }
    document.body.classList.toggle('ra-focus', this.focus && this.isSpeaking);
    this.persist();
  },

  cycleSleep() {
    const index = SLEEP_OPTIONS.indexOf(this.sleepMinutes);
    const next = SLEEP_OPTIONS[(index + 1) % SLEEP_OPTIONS.length];
    this.setSleep(next);
  },

  setSleep(minutes) {
    this.sleepMinutes = SLEEP_OPTIONS.indexOf(minutes) !== -1 ? minutes : 0;
    this._clearSleep();
    const button = document.getElementById('raSleep');
    if (this.sleepMinutes > 0) {
      this.sleepEndsAt = Date.now() + this.sleepMinutes * 60000;
      this._sleepTimer = setTimeout(() => {
        this.pause();
        this.setMode('full');
        if (typeof showToast === 'function') showToast('Sleep timer — paused, rest well', 'success');
      }, this.sleepMinutes * 60000);
      this._sleepTick = setInterval(() => this._paintSleep(), 1000);
      this._paintSleep();
      if (button) button.classList.add('active');
      if (typeof showToast === 'function') showToast(`Sleep timer set to ${this.sleepMinutes} minutes`, 'info');
    } else {
      this.sleepEndsAt = 0;
      if (button) button.classList.remove('active');
      const label = document.getElementById('raEyebrowState');
      if (label) this.updateUI();
      if (typeof showToast === 'function') showToast('Sleep timer off', 'info');
    }
    if (button) button.title = this.sleepMinutes ? `Sleeps in ${this.sleepMinutes} min` : 'Sleep timer';
    this.persist();
  },

  _paintSleep() {
    const left = Math.max(0, this.sleepEndsAt - Date.now());
    const button = document.getElementById('raSleep');
    if (button) button.title = `Sleeps in ${Math.ceil(left / 60000)} min`;
    if (left <= 0 && this._sleepTick) { clearInterval(this._sleepTick); this._sleepTick = null; }
  },

  _clearSleep() {
    if (this._sleepTimer) { clearTimeout(this._sleepTimer); this._sleepTimer = null; }
    if (this._sleepTick) { clearInterval(this._sleepTick); this._sleepTick = null; }
  },

  /* =========================================================
     PAGE FOLLOW — the page scrolls with the reading
     ========================================================= */
  _cacheUnitEls() {
    this._lineEls = [];
    this._lineTops = [];
    if (AppState.currentView !== 'commentary') return;
    const verseEl = this.ayah == null ? null : document.getElementById(`commentary-verse-${this.ayah}`);
    const scope = verseEl || document.querySelector('.ebook-introduction');
    if (!scope) return;
    const nodes = scope.querySelectorAll('.ebook-commentary > *, .ebook-introduction-content > *, .ebook-translation');
    const list = Array.prototype.slice.call(nodes);
    this._lineEls = this.lines.map((line) => this._matchNode(line, list));
    this._measureLines();
  },

  _norm(text) {
    return String(text || '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
  },

  _matchNode(line, list) {
    const needle = this._norm(line.show).slice(0, 46);
    if (!needle) return null;
    for (const node of list) {
      if (this._norm(node.textContent).indexOf(needle) !== -1) return node;
    }
    const head = this._norm(line.show).slice(0, 18);
    if (head) for (const node of list) {
      if (this._norm(node.textContent).indexOf(head) !== -1) return node;
    }
    return null;
  },

  _measureLines() {
    if (!this._lineEls.length) { this._lineTops = []; return; }
    const scrollY = window.scrollY;
    this._lineTops = this._lineEls.map((node) => node ? node.getBoundingClientRect().top + scrollY : null);
  },

  _followLine() {
    if (!this.follow || !this.isSpeaking) return;
    const target = this._lineTops[this.lineIndex];
    if (target == null) return;
    if (Date.now() - this._userScrollAt < 2600) return;
    const headerH = ReadingMemory.headerHeight();
    this._scrollTo(Math.max(0, target - headerH - 22), 620);
  },

  _followProgress(fraction) {
    if (!this.follow || !this.isSpeaking) return;
    if (Date.now() - this._userScrollAt < 2600) return;
    const current = this._lineTops[this.lineIndex];
    const next = this._lineTops[this.lineIndex + 1];
    const headerH = ReadingMemory.headerHeight();
    if (current == null) return;
    const anchor = current - headerH - 22;
    if (next == null || next - current < 120) { this._paintScrub(fraction); return; }
    const target = Math.max(0, anchor + (next - current) * Math.min(1, fraction) * 0.92);
    this._paintScrub(fraction);
    const maxY = target;
    if (Math.abs(window.scrollY - maxY) < 6) return;
    this._scrollTo(maxY, 0, true);
  },

  _paintScrub(fraction) {
    const fill = document.getElementById('raScrubFill');
    if (fill) fill.style.width = `${Math.round(Math.max(0, Math.min(1, fraction)) * 100)}%`;
    const bar = document.getElementById('raScrubBar');
    if (bar) bar.setAttribute('aria-valuenow', String(Math.round(fraction * 100)));
  },

  /** rAF scroller — smooth, interruptible, dock-aware. */
  _scrollTo(targetY, duration = 520, immediate = false) {
    const reduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (immediate || duration <= 0 || reduced) {
      if (typeof window.scrollTo === 'function') window.scrollTo({ top: targetY, behavior: 'auto' });
      else document.documentElement.scrollTop = targetY;
      return;
    }
    if (this._scrollAnim) cancelAnimationFrame(this._scrollAnim);
    const startY = window.scrollY;
    const delta = targetY - startY;
    if (Math.abs(delta) < 3) return;
    const startTime = performance.now();
    const step = (now) => {
      const elapsed = now - startTime;
      const t = Math.min(1, elapsed / duration);
      const eased = t < 0.5 ? (4 * t * t * t) : (1 - Math.pow(-2 * t + 2, 3) / 2);
      if (typeof window.scrollTo === "function") window.scrollTo(0, startY + delta * eased);
      if (t < 1 && Date.now() - this._userScrollAt > 700) this._scrollAnim = requestAnimationFrame(step);
      else this._scrollAnim = null;
    };
    this._scrollAnim = requestAnimationFrame(step);
  },

  /* =========================================================
     COMMENTARY PAGE IS THE LYRICS — no duplicated panel
     ========================================================= */
  _renderLyrics() { /* intentionally no-op: page itself is the lyrics */ },

  _setActiveLine(cleared) {
    document.querySelectorAll('.ebook-verse .tts-line-active, .ebook-introduction .tts-line-active, .tts-line-active').forEach((node) => node.classList.remove('tts-line-active'));
    if (cleared) return;
    const lineEl = this._lineEls[this.lineIndex];
    if (lineEl) lineEl.classList.add('tts-line-active');
    const verseEl = this.ayah == null ? document.querySelector('.ebook-introduction') : document.getElementById(`commentary-verse-${this.ayah}`);
    if (verseEl) verseEl.classList.add('tts-active');
  },

  _paintLineProgress(fraction) {
    this._paintScrub(fraction);
  },

  _renderNavigator() {
    const wrap = document.getElementById('raNavigator');
    if (!wrap) return;
    const surah = this.activeSurah || AppState.currentSurah;
    if (!surah) { wrap.innerHTML = ''; return; }
    const total = this.verseCount(surah);
    const tafsir = loadedTafsir[surah];
    const current = this.ayah || this.selectedAyah;
    let html = '';
    for (let verse = 1; verse <= total; verse += 1) {
      const ready = !tafsir || getVerseCommentary(tafsir, verse);
      const state = verse === current ? ' selected' : ready ? '' : ' muted';
      html += `<button type="button" class="ra-nav-item${state}" data-nav-verse="${verse}" title="Verse ${verse}${ready ? '' : ' — commentary coming soon'}">${verse}</button>`;
    }
    wrap.innerHTML = html;
    wrap.querySelectorAll('[data-nav-verse]').forEach((node) => {
      node.addEventListener('click', () => this.seekVerse(surah, parseInt(node.getAttribute('data-nav-verse'), 10)));
    });
  },

  /* =========================================================
     UI SYNC — dock only lives on the commentary page
     ========================================================= */
  updateUI() {
    this._syncViewClass();
    const dock = document.getElementById('raDock');
    if (!dock) return;
    const onCommentary = typeof AppState !== 'undefined' && AppState.currentView === 'commentary';
    /* hide the dock entirely when not on the commentary page */
    const effectiveMode = onCommentary && this.hasSession ? this.mode : 'off';
    dock.setAttribute('data-mode', effectiveMode);
    document.body.classList.toggle('ra-mini-open', onCommentary && this.hasSession && this.mode === 'mini');
    document.body.classList.toggle('ra-full-open', onCommentary && this.hasSession && this.mode === 'full');
    document.body.classList.toggle('ra-focus', this.focus && this.isSpeaking && onCommentary);
    if (typeof updateScrollTopBtn === 'function') updateScrollTopBtn();
    if (typeof updateChromeSpacing === 'function') updateChromeSpacing();
    if (!onCommentary) { this.updateOrb(); return; }

    const playing = this.isSpeaking;
    const playIcon = (label) => playing
      ? '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4" width="4" height="16" rx="1.4"></rect><rect x="14" y="4" width="4" height="16" rx="1.4"></rect></svg>'
      : '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><polygon points="6 3 20 12 6 21 6 3"></polygon></svg>';
    const mini = document.getElementById('raMiniPlay');
    if (mini) { mini.innerHTML = playIcon(); mini.setAttribute('aria-label', playing ? 'Pause read aloud' : 'Resume read aloud'); }
    const full = document.getElementById('raPlay');
    if (full) { full.innerHTML = playIcon(); full.classList.toggle('is-playing', playing); }

    const state = document.getElementById('raEyebrowState');
    if (state) state.textContent = playing ? 'reading' : this.isPaused ? 'paused' : this.completed ? 'finished' : 'ready';

    const surah = this.activeSurah || this.selectedSurah;
    const ch = (window.chaptersData || []).find((chapter) => chapter.number === surah);
    const trigger = document.getElementById('raTrigger');
    const triggerLabel = document.getElementById('raTriggerLabel');
    if (trigger) trigger.classList.toggle('is-active', this.hasSession && (this.isSpeaking || this.isPaused));
    if (triggerLabel) {
      triggerLabel.textContent = !this.isSupported() ? 'Read aloud unavailable'
        : this.isSpeaking ? 'Reading aloud…'
        : this.isPaused ? 'Resume reading'
        : this.hasSession ? 'Show player'
        : 'Read aloud';
    }
    const title = document.getElementById('raTitle');
    if (title) title.textContent = ch ? `${ch.name_en} · commentary` : 'Commentary read aloud';
    const miniTitle = document.getElementById('raMiniTitle');
    if (miniTitle) miniTitle.textContent = ch ? `${ch.name_en} — commentary` : 'Commentary read aloud';

    const total = surah ? this.verseCount(surah) : 1;
    const verseNumber = this.ayah == null ? 1 : (this.ayah || this.selectedAyah || 1);
    const chip = document.getElementById('raVerseChip');
    if (chip) chip.textContent = this.ayah == null ? 'Introduction' : `Verse ${verseNumber} of ${total}`;
    const miniVerse = document.getElementById('raMiniVerse');
    if (miniVerse) miniVerse.textContent = this.ayah == null ? '✦' : String(verseNumber);

    const line = this.lines[this.lineIndex];
    const miniLine = document.getElementById('raMiniLine');
    if (miniLine) {
      miniLine.textContent = line ? line.show
        : this.completed ? 'Finished — tap the button to replay'
        : this.hasSession ? `Ready to resume at ${this.ayah == null ? 'the introduction' : `verse ${this.ayah}`}`
        : 'Ready when you are';
    }
    const fullHead = document.querySelector('.ra-head');
    if (fullHead) fullHead.classList.toggle('is-speaking', this.isSpeaking);

    const fill = document.getElementById('raProgressFill');
    if (fill) fill.style.width = `${Math.round((verseNumber / Math.max(1, total)) * 100)}%`;

    const range = document.getElementById('raVerseRange');
    if (range) {
      range.max = String(total);
      range.value = String(verseNumber);
    }
    const out = document.getElementById('raVerseTotal');
    if (out) out.textContent = `${verseNumber} / ${total}`;

    const rate = document.getElementById('raRate');
    if (rate) rate.value = String(this.rate);
    const followButton = document.getElementById('raFollow');
    if (followButton) { followButton.classList.toggle('active', this.follow); followButton.setAttribute('aria-pressed', String(this.follow)); }
    const focusButton = document.getElementById('raFocus');
    if (focusButton) { focusButton.classList.toggle('active', this.focus); focusButton.setAttribute('aria-pressed', String(this.focus)); }
    const repeatButton = document.getElementById('raRepeat');
    if (repeatButton) { repeatButton.classList.toggle('active', this.repeatVerse); repeatButton.setAttribute('aria-pressed', String(this.repeatVerse)); }
    const prevButton = document.getElementById('raPrevVerse');
    const nextButton = document.getElementById('raNextVerse');
    if (prevButton) prevButton.disabled = verseNumber <= 1 && this.ayah == null;
    if (nextButton) nextButton.disabled = verseNumber >= total;
    if (!this.sleepMinutes) this._paintSleep();

    const remaining = document.getElementById('raRemaining');
    if (remaining) remaining.textContent = this._estimateRemaining(verseNumber, total);
    const elapsed = document.getElementById('raElapsed');
    if (elapsed) elapsed.textContent = this.ayah == null ? 'Intro' : `Verse ${verseNumber}`;

    this.updateOrb();
    this._syncPageHighlight();
  },

  _estimateRemaining(verseNumber, total) {
    if (!this.hasSession) return '—';
    const surah = this.activeSurah;
    const tafsir = loadedTafsir[surah];
    if (!tafsir) return '—';
    if (!this._avgVerseChars) {
      const verses = tafsir.verses || {};
      const sizes = Object.keys(verses).map((key) => String(verses[key]).length);
      this._avgVerseChars = sizes.length ? sizes.reduce((sum, value) => sum + value, 0) / sizes.length : 900;
    }
    const remainingVerses = Math.max(0, total - verseNumber);
    const chars = remainingVerses * this._avgVerseChars;
    const minutes = chars / (1350 * Math.max(0.6, this.rate));
    if (remainingVerses === 0) return 'last verse';
    if (minutes < 1) return '<1 min left';
    return `${Math.round(minutes)} min left`;
  },

  updateOrb() {
    if (typeof PlayerOrb !== 'undefined' && PlayerOrb && PlayerOrb.hide) {
      PlayerOrb.hide('tts');
    }
  },

  _syncPageHighlight() {
    const verses = document.querySelectorAll('.ebook-verse.tts-active');
    verses.forEach((node) => node.classList.remove('tts-active'));
    if (this.ayah && AppState.currentView === 'commentary') {
      const el = document.getElementById(`commentary-verse-${this.ayah}`);
      if (el) el.classList.add('tts-active');
    }
  },

  /** Called after the commentary view (re)renders so the player re-attaches. */
  rebind() {
    this._syncViewClass();
    this._unitCache = {};
    if (!this.hasSession) { this.updateUI(); return; }
    this.lines = this.unitFor(this.activeSurah, this.ayah) || this.lines;
    this._cacheUnitEls();
    this._renderNavigator();
    this.updateUI();
    this._setActiveLine();
  },

  onRouteRendered() {
    this._syncViewClass();
    const onCommentary = (typeof AppState !== 'undefined' && AppState.currentView === 'commentary');
    if (onCommentary) {
      this.rebind();
    } else {
      if (this.isSpeaking || this.isPaused || this.hasSession) {
        this.endSession({ silent: true });
      }
      this._lineEls = [];
      this._lineTops = [];
      document.querySelectorAll('.ebook-verse.tts-active, .tts-line-active').forEach((n) => n.classList.remove('tts-active', 'tts-line-active'));
      this.updateUI();
    }
  },

  /* =========================================================
     SYSTEM INTEGRATIONS
     ========================================================= */
  _mediaState(state) {
    if (!('mediaSession' in navigator)) return;
    try { navigator.mediaSession.playbackState = state; } catch (err) { /* no-op */ }
  },

  _mediaMetadata(line) {
    if (!('mediaSession' in navigator) || typeof MediaMetadata !== 'function') return;
    const surah = this.activeSurah;
    const ch = (window.chaptersData || []).find((chapter) => chapter.number === surah);
    const name = ch ? ch.name_en : 'Surah';
    const subtitle = this.ayah == null ? 'Surah introduction' : `Verse ${this.ayah} of ${ch ? ch.verses : ''}`;
    try {
      navigator.mediaSession.metadata = new MediaMetadata({
        title: `${name} — ${subtitle}`,
        artist: 'Quran Explained · commentary read aloud',
        album: ch ? ch.meaning : 'Quran Explained',
        artwork: [
          { src: 'icons/icon-192x192.png', sizes: '192x192', type: 'image/png' },
          { src: 'icons/icon-512x512.png', sizes: '512x512', type: 'image/png' },
        ],
      });
    } catch (err) { /* older browsers */ }
    if (navigator.mediaSession.setPositionState && this.ayah != null) {
      const total = this.verseCount(surah);
      try {
        navigator.mediaSession.setPositionState({
          duration: Math.max(1, total),
          position: Math.max(0, this.ayah - 1 + (this.lineIndex / Math.max(1, this.lines.length))),
        });
      } catch (err) { /* no-op */ }
    }
  },

  wireMediaHandlers() {
    if (!('mediaSession' in navigator)) return;
    const set = (action, handler) => {
      try { navigator.mediaSession.setActionHandler(action, handler); } catch (err) { /* unsupported */ }
    };
    set('play', () => this.resume());
    set('pause', () => this.pause());
    set('previoustrack', () => this.prevVerse());
    set('nexttrack', () => this.nextVerse());
    set('stop', () => this.cancel());
  },

  _requestWakeLock() {
    if (!('wakeLock' in navigator)) return;
    try {
      const promise = navigator.wakeLock.request('screen');
      if (promise && promise.then) promise.then((lock) => { this._wakeLock = lock; }).catch(() => {});
    } catch (err) { /* no-op */ }
  },

  _releaseWakeLock() {
    if (this._wakeLock) { try { this._wakeLock.release(); } catch (err) { /* no-op */ } this._wakeLock = null; }
  },

  /** Chrome/Safari occasionally swallow onend; nudge the queue if it stalls. */
  _startWatchdog() {
    this._stopWatchdog();
    this._lastProgressAt = Date.now();
    this._watchdog = setInterval(() => {
      if (!this.isSpeaking) return;
      const speaking = window.speechSynthesis && window.speechSynthesis.speaking;
      if (speaking) { this._lastProgressAt = Date.now(); return; }
      if (Date.now() - this._lastProgressAt > 12000) {
        this._lastProgressAt = Date.now();
        this._advance();
      }
    }, 4000);
  },

  _stopWatchdog() { if (this._watchdog) { clearInterval(this._watchdog); this._watchdog = null; } },

  /* ---------- legacy helpers kept for existing call sites ---------- */
  previous(surahNum) { if (!this.activeSurah) { this.selectedAyah = Math.max(1, this.getSelectedVerse(surahNum, this.verseCount(surahNum)) - 1); this.updateUI(); return; } this.prevVerse(); },
  next(surahNum) { if (!this.activeSurah) { this.selectedAyah = Math.min(this.verseCount(surahNum), this.getSelectedVerse(surahNum, this.verseCount(surahNum)) + 1); this.updateUI(); return; } this.nextVerse(); },
};


/* =========================================================
   PLAYER ORB — one small floating button that remembers the
   player you cancelled (read aloud or recitation). Tap it and
   the player comes back exactly where it stopped.
   ========================================================= */
const PlayerOrb = {
  el: null,
  owner: null,
  onClick: null,
  _drag: null,

  init(config) {
    /* PlayerOrb disabled — read aloud is part of full commentary only */
    return;
  },

  _readPosition() { return null; },

  persistPosition() {},

  applyPosition(y) {},

  _bindDrag(orb) {},

  show(config) {
    /* PlayerOrb disabled */
    return;
  },

  hide(owner) {
    if (this.el) {
      this.el.classList.remove('visible', 'is-speaking', 'is-done', 'owner-tts', 'owner-recitation');
      this.el.setAttribute('aria-hidden', 'true');
    }
    document.body.classList.remove('has-orb');
    if (typeof updateScrollTopBtn === 'function') updateScrollTopBtn();
  },
};
