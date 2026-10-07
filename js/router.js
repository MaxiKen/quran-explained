/* =========================================================
   ROUTER — one screen, one tap
   ---------------------------------------------------------
   The reader keeps its own navigation stack and treats the
   browser history entry as a *trap*: exactly one app-owned
   history entry sits above the page the reader arrived from,
   so a hardware / gesture / mouse back press is delivered to
   the reader first (previous screen, same place) instead of
   silently dropping the reader out of the app.

   Everything the reader needs is also on screen: Back,
   Forward and Home in the header, edge swipes on touch
   devices, and Alt+←/→ on a keyboard.
   ========================================================= */

const Router = {
  stack: [],
  index: -1,
  maxDepth: 60,
  _busy: false,
  _allowExit: false,
  _exitPromptAt: 0,
  _armed: false,
  _lastLeftKey: null,

  /* ---------- boot ---------- */
  init(route) {
    if ('scrollRestoration' in history) {
      try { history.scrollRestoration = 'manual'; } catch (err) { /* older browsers */ }
    }
    window.addEventListener('popstate', () => this._onPop());
    window.addEventListener('hashchange', () => this._onHash());
    document.documentElement.classList.add('app-routed');
    this.stack = [route || { view: 'list' }];
    this.index = 0;
    this.arm();
  },

  /** Put (or refresh) the single app-owned history entry on top. */
  arm() {
    const route = this.current() || { view: 'list' };
    const state = this.stateOf(route);
    if (history.state && history.state.qx) history.replaceState(state, '', this.urlFor(route));
    else history.pushState(state, '', this.urlFor(route));
    this._armed = true;
    this._syncTitle(route);
  },

  stateOf(route) {
    return {
      qx: 1,
      view: route.view,
      surah: route.surah || undefined,
      verse: route.verse || undefined
    };
  },

  urlFor(route) {
    const base = `${window.location.pathname}${window.location.search}`;
    if (!route || route.view === 'list') {
      const tab = AppState.homeTab;
      return base + (tab === 'bookmarks' ? '#bookmarks' : tab === 'history' ? '#history' : '');
    }
    if (route.view === 'commentary') return `${base}#surah-${route.surah}-commentary`;
    return `${base}${getChapterHash(route.surah, route.verse || null)}`;
  },

  keyFor(route) {
    return ReadingMemory.key(route ? route.view : 'list', route ? route.surah : null);
  },

  current() { return this.index >= 0 ? this.stack[this.index] : null; },
  canGoBack() { return this.index > 0; },
  canGoForward() { return this.index >= 0 && this.index < this.stack.length - 1; },

  backLabel() {
    const prev = this.canGoBack() ? this.stack[this.index - 1] : null;
    if (prev && prev.view === 'commentary') return 'Commentary';
    if (prev && prev.view === 'detail') return prev.surah === (this.current() || {}).surah ? 'Chapter' : `Surah ${prev.surah}`;
    return 'Chapters';
  },

  /* ---------- navigation ---------- */
  async go(route, opts = {}) {
    const target = Object.assign({ view: 'list', surah: null, verse: null }, route);
    if (target.view !== 'list' && (!target.surah || target.surah < 1 || target.surah > 114)) return false;
    if (this._busy) { this._pending = { route: target, opts }; return false; }

    const current = this.current();
    const targetKey = this.keyFor(target);
    /* Coming back to (or forward into) the screen we just left, or being
       driven by the system back gesture → continue in place. A brand new
       screen always opens at the top. */
    const resume = opts.resume != null ? opts.resume : (targetKey === this._lastLeftKey || target.view === 'list');

    if (current) {
      this._lastLeftKey = this.keyFor(current);
      this.captureIfLive(current);
    }

    this.stack = this.stack.slice(0, this.index + 1);
    const top = this.stack[this.stack.length - 1];
    const sameAsTop = top && top.view === target.view && top.surah === target.surah && top.verse === target.verse;

    if (opts.replace && current) {
      this.stack[this.index] = target;
    } else if (sameAsTop && !opts.force) {
      this.index = this.stack.length - 1;
    } else {
      this.stack.push(target);
      if (this.stack.length > this.maxDepth) this.stack.shift();
      this.index = this.stack.length - 1;
    }
    return this._render(target, { resume });
  },

  /** Replace the live entry (used by deep links / error paths). */
  replace(route, opts = {}) {
    return this.go(route, Object.assign({ replace: true, force: true, resume: false }, opts));
  },

  /** Capture only when the live DOM really is showing that screen. */
  captureIfLive(route) {
    const key = this.keyFor(route);
    if (key !== ReadingMemory.key(AppState.currentView, AppState.currentSurah)) return null;
    const saved = ReadingMemory.capture(key);
    if (route && route.view !== 'list') {
      const verse = ReadingMemory.topVerseNum();
      if (verse && typeof addToHistory === 'function') addToHistory(route.surah, verse);
    }
    return saved;
  },

  async back() {
    if (!this.canGoBack()) return false;
    const current = this.current();
    if (current) {
      this._lastLeftKey = this.keyFor(current);
      this.captureIfLive(current);
    }
    this.index -= 1;
    await this._render(this.current(), { resume: true });
    return true;
  },

  async forward() {
    if (!this.canGoForward()) return false;
    const current = this.current();
    if (current) this.captureIfLive(current);
    this.index += 1;
    await this._render(this.current(), { resume: true });
    return true;
  },

  /** First paint of the app: adopt the URL (deep links keep working). */
  boot() {
    const route = routeFromHash(window.location.hash) || { view: 'list' };
    if (route.tab && typeof AppState !== 'undefined') AppState.homeTab = route.tab;
    this.init(route.view === 'list' ? { view: 'list' } : route);
    return this.go(route, { force: true, resume: !route.verse, replace: true });
  },

  goHome() {
    if ((this.current() || {}).view === 'list') { window.scrollTo({ top: 0, behavior: 'smooth' }); return Promise.resolve(false); }
    return this.go({ view: 'list' }, { resume: false });
  },

  async _render(route, opts) {
    this._busy = true;
    try {
      if (route.view === 'detail') await window.renderSurahView(route.surah, opts);
      else if (route.view === 'commentary') await window.renderCommentaryView(route.surah, opts);
      else await window.renderHomeRoute(opts);
    } catch (err) {
      console.error('[Router] failed to render', route, err);
    } finally {
      this._busy = false;
    }
    if (this._pending) {
      const pending = this._pending;
      this._pending = null;
      this.go(pending.route, pending.opts);
    }
    /* keep the address bar and the trap entry in step with the screen */
    const state = this.stateOf(route);
    if (history.state && history.state.qx) history.replaceState(state, '', this.urlFor(route));
    else history.pushState(state, '', this.urlFor(route));
    this._armed = true;
    this._syncTitle(route);
    if (window.renderHeaderNav) window.renderHeaderNav();
    if (window.afterRouteRender) window.afterRouteRender(route);
    return true;
  },

  _syncTitle(route) {
    const base = 'Quran Explained';
    if (!route || route.view === 'list') { document.title = `${base} — verse by verse`; return; }
    const ch = (window.chaptersData || []).find((chapter) => chapter.number === route.surah);
    const name = ch ? ch.name_en : `Surah ${route.surah}`;
    document.title = route.view === 'commentary'
      ? `${name} — commentary · ${base}`
      : `${name}${route.verse ? ` · verse ${route.verse}` : ''} · ${base}`;
  },

  /* ---------- browser back / forward ---------- */
  _onPop() {
    if (this._allowExit) { this._allowExit = false; return; }
    /* the pop removed our trap entry — put it straight back so the reader
       never leaves the app by accident */
    this.arm();
    if (this.canGoBack()) { this.back(); return; }

    const now = Date.now();
    if (now - this._exitPromptAt < 3200) {
      this._exitPromptAt = 0;
      this._allowExit = true;
      history.back();
      return;
    }
    this._exitPromptAt = now;
    if (typeof showToast === 'function') showToast('Press back again to leave the reader', 'info');
    setTimeout(() => { this._exitPromptAt = 0; }, 3400);
  },

  _onHash() {
    const route = routeFromHash(window.location.hash);
    if (!route) return;
    const current = this.current() || { view: 'list' };
    if (route.view === current.view && route.surah === current.surah) return;
    this.go(route, { resume: false });
  },

  /* ---------- shared deep links ---------- */
  openVerse(surahNum, ayahNum) {
    return this.go({ view: 'detail', surah: surahNum, verse: ayahNum }, { resume: false, force: true });
  },

  /** Comment back / "End of surah" style exits. */
  async backToChapter() {
    const current = this.current() || {};
    if (this.canGoBack() && this.stack[this.index - 1].view === 'detail' && this.stack[this.index - 1].surah === current.surah) {
      await this.back();
      return;
    }
    if (current.surah) await this.go({ view: 'detail', surah: current.surah }, { resume: true });
    else await this.goHome();
  },
};

/** Parse a location hash into a route object (deep links + shared verses). */
function routeFromHash(hash) {
  const value = String(hash || '');
  if (value === '#bookmarks') return { view: 'list', tab: 'bookmarks' };
  if (value === '#history') return { view: 'list', tab: 'history' };
  const commentary = value.match(/^#surah-(\d+)-commentary$/);
  if (commentary) {
    const num = parseInt(commentary[1], 10);
    return num >= 1 && num <= 114 ? { view: 'commentary', surah: num } : null;
  }
  const surah = value.match(/^#surah-(\d+)(?:-verse-(\d+))?$/);
  if (surah) {
    const num = parseInt(surah[1], 10);
    if (num < 1 || num > 114) return null;
    return { view: 'detail', surah: num, verse: surah[2] ? parseInt(surah[2], 10) : null };
  }
  return null;
}

/* =========================================================
   SCREEN GESTURES — swipe from either edge to move through
   the reader's own stack (right edge → forward).
   ========================================================= */
const ScreenGestures = {
  edge: 34,
  minDistance: 78,
  _start: null,
  _hint: null,

  init() {
    if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    this._hint = document.createElement('div');
    this._hint.className = 'swipe-hint';
    this._hint.setAttribute('aria-hidden', 'true');
    document.body.appendChild(this._hint);

    document.addEventListener('touchstart', (event) => this._onStart(event), { passive: true });
    document.addEventListener('touchmove', (event) => this._onMove(event), { passive: true });
    document.addEventListener('touchend', () => this._onEnd(), { passive: true });
    document.addEventListener('pointercancel', () => this._reset(), { passive: true });
  },

  _blocked(target) {
    if (!target) return true;
    const tag = (target.tagName || '').toUpperCase();
    if (['INPUT', 'TEXTAREA', 'SELECT', 'BUTTON', 'A', 'SUMMARY', 'LABEL'].indexOf(tag) !== -1) return true;
    if (target.closest && target.closest('.modal-overlay, .ra-dock, .ra-orb, .audio-player-bar, .downloads-modal-content')) return true;
    return false;
  },

  _onStart(event) {
    if (event.touches.length !== 1) { this._start = null; return; }
    const touch = event.touches[0];
    if (this._blocked(event.target)) { this._start = null; return; }
    const fromLeft = touch.clientX <= this.edge;
    const fromRight = touch.clientX >= window.innerWidth - this.edge;
    if (!fromLeft && !fromRight) { this._start = null; return; }
    this._start = { x: touch.clientX, y: touch.clientY, dir: fromLeft ? 1 : -1, fired: false };
  },

  _onMove(event) {
    if (!this._start || this._start.fired) return;
    const touch = event.touches[0];
    if (!touch) return;
    const dx = touch.clientX - this._start.x;
    const dy = touch.clientY - this._start.y;
    if (Math.abs(dy) > 46 && Math.abs(dy) > Math.abs(dx)) { this._start = null; this._hideHint(); return; }
    if (Math.abs(dx) > this.minDistance && Math.abs(dx) > Math.abs(dy) * 1.35) {
      this._start.fired = true;
      this._hideHint();
      const dir = this._start.dir;
      this._start = null;
      if (dir > 0) { if (!Router.back()) this._bounce(); }
      else if (!Router.forward()) this._bounce();
    } else if (Math.abs(dx) > 18) {
      this._showHint(this._start.dir, Math.min(1, Math.abs(dx) / this.minDistance));
    }
  },

  _onEnd() { this._reset(); },

  _reset() { this._start = null; this._hideHint(); },

  _showHint(dir, strength) {
    if (!this._hint) return;
    this._hint.className = `swipe-hint visible ${dir > 0 ? 'from-left' : 'from-right'}`;
    this._hint.style.setProperty('--swipe-strength', strength.toFixed(2));
  },

  _hideHint() { if (this._hint) this._hint.className = 'swipe-hint'; },

  _bounce() {
    if (!this._hint) return;
    this._hint.className = 'swipe-hint nope from-left visible';
    this._hint.style.setProperty('--swipe-strength', '0.55');
    setTimeout(() => this._hideHint(), 260);
  },
};
