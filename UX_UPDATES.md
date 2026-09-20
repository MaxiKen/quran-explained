# Reading Experience Updates — v2.3

This release gives the reader continuity: where you left off is where you come back to, navigation is driven by the screen instead of the browser's back button, and read-aloud becomes a proper music-player dock that follows the text like lyrics.

## 1. Reading continuity (resume exactly where you stopped)

- Every place you stop in is remembered per screen: the **home list** (including the open tab and search text), each **chapter page**, and each chapter's **complete commentary**.
- Returning to the *same* place — via the on-screen back pill, a browser back gesture, or opening the chapter again — restores the exact verse or commentary block you were reading, not a pixel guess. Positions are stored as verse anchors (`ch-N`, `v-N`, `c-N`) so they survive text-size changes, theme changes and re-renders.
- Returning to a *different* chapter or page always starts fresh at the top — remembering is deliberately scoped to the place you actually left.
- When a remembered place exists but you land at the top (e.g. after a bookmark jump), a **Continue at Surah · verse N** chip offers the way back, with a *Start over* action that clears the saved place.
- Leaving a screen at the very top clears its saved place, so "continue reading" never nags you with a page you already finished.
- A **position read-out** in the header shows `verse N / total` while you read, and a small dot tells you when read-aloud or recitation is running.
- Places are also flushed on `pagehide`/tab-hide, so closing the app mid-read does not lose the position.

## 2. Read-aloud belongs strictly to the complete commentary page

- Read-aloud is exclusively part of the complete commentary eBook view. Standalone read-aloud buttons outside of commentary (home continue card, chapter detail header, tafsir sheet modal) have been removed.
- The player opens as a **fixed bottom dock**, pinned flush to the viewport bottom across all screen sizes (mobile, tablet, desktop) without any floating gap, margin offset, or horizontal translation shifts.
- Full dock: play/pause, previous/next verse, **go-to-verse scrubber**, verse-range jump list (navigator), a seek bar, speed, voice picker, follow toggle, and a **sleep timer** (5–60 min).
- **Line following**: the commentary page itself serves as the reading display, scrolling smoothly and highlighting the active verse and sentence as it is spoken.
- **Cancel / End** stops speech synthesis immediately and closes the dock.
- Leaving the commentary page terminates the read-aloud session immediately. Floating orbs outside commentary are disabled.
- Lock-screen / headset controls are wired through the Media Session API, and a wake lock is held while speaking.
- The recitation audio bar and the read-aloud dock never play over each other — starting one suspends the other.

## 3. Tafsir popup: explicit way out

- The popup is now a proper **tafsir sheet**: sticky header with the verse chip and a **Close (Esc)** button, its own scroll region, and a sticky footer with **Prev / Next verse**, **Bookmark**, **Open commentary** and **Done**.
- Clicking outside still closes it; you can also **drag the sheet down** to dismiss, or swipe sideways on the handle strip to step verses. A progress rail at the top shows how far through the chapter's tafsir you are.
- Opening the sheet always starts at the top of its own scroll area, and the reading position behind it is untouched.

## 4. Back/forward is driven by the screen, not the browser

- The header now carries a navigation cluster: **‹ Back** (labelled with the screen you'll land on, e.g. *‹ Al-Baqarah*), a forward pill when a forward step exists, and **Home**. The logo is also a tappable home button.
- A lightweight in-app router owns the history: it pushes a single guard entry so a browser/OS back press is intercepted and turned into an *in-app* step (close the sheet → leave the commentary → leave the chapter). Only a second, deliberate press at the very top level leaves the reader, and it shows a "press back again to exit" toast instead of vanishing.
- Overscroll and swipe gestures are handled in-app: **edge-swipe** from the left goes back one screen with a live rubber-band hint, and the same gesture is mirrored on the sheet header.
- `history.scrollRestoration` is set to manual so the browser cannot jump the page mid-render; the app decides where a screen opens.
- Keyboard shortcuts stay available for desktop: **H / C / L**, `Alt + ←/→`, `Esc` (closes the sheet first, then leaves the screen).

## Other improvements in this release

- Page content now reserves space for whatever is docked at the bottom (`--bottom-chrome`), so the player never covers the last verse, and the scroll-top button lifts itself above the player bar.
- **Chapter progress** is shown on home: a per-chapter rail, and the last verse reached, on the continue card and chapter list.
- The eBook toolbar's read-aloud button reflects live state (*Reading · verse N*, *Paused at verse N*).
- Per-verse **play** affordances in the eBook start the dock at that verse; verse anchors in the chapter view accept the same deep links as before.
- Unavailable screens (a chapter with no data, a missing commentary) get a real "screen unavailable" state with a way back instead of an empty page.
- Toasts can carry an action button (*Start over*, *Undo*).
- Service worker cache bumped to `v2.3.0` and now precaches the three new modules (`reading-memory`, `router`, `read-aloud`); previously downloaded chapters are carried over untouched.

---

# Previous release — v2.2

This release prioritizes a calmer chapter-reading experience, better mobile support, and clearer offline behavior.

## Requested improvements

### 1. Cleaner chapter navigation
- The **Offline Downloads** icon is shown on the home/chapter-list screen only.
- It is deliberately hidden while reading an individual surah and in the commentary eBook, where the contextual **Save Offline** button remains available in the surah header.

### 2. Complete Commentary eBook
- Every individual surah now has a **Complete Commentary** button next to **Read Surah Notes** and **Save Offline**.
- It opens a dedicated, distraction-free continuous reading view with the chapter introduction, each verse’s English context, and the complete commentary.
- The eBook includes jump-to-verse, text-size, share-link, and **Save PDF** tools.

### 3. Built-in commentary read aloud
- The eBook now has a full **Read aloud** player that starts immediately with the browser’s built-in voice—no sign-in, app installation, audio download, or voice selection is required.
- The player includes play/pause/resume, stop, previous/next verse controls, and a verse slider. It starts at the selected verse and continues through the remaining commentary.
- The **Verse navigator** lists every verse in the surah. Selecting a verse scrolls to its commentary and, during playback, immediately continues narration from that verse.
- Commentary text is not sent by this app to an audio service. Where a browser uses an installed local system voice, it also works offline after the chapter is loaded.

### 4. Five directly selectable reading themes
The old cycling control was replaced by a direct theme picker, so readers do not have to tap repeatedly to reach a preferred appearance.

1. **Night** — calm teal-on-deep-slate contrast for low-light sessions.
2. **Daylight** — crisp, high-legibility light surface.
3. **Paper** — warm, book-like cream page for long commentary reading.
4. **Forest** — low-glare deep green with a restful accent.
5. **Dusk** — soft indigo and lavender for an alternative dark mode.

Existing saved theme choices are automatically mapped to their closest new equivalent (Dark → Night, Light → Daylight, Sepia → Paper, Midnight → Dusk).

## Additional usability improvements added

- **Continue reading** appears above the chapter search when a reader has history, returning directly to the last recorded verse.
- **Previous / next chapter** controls at the end of every surah make sequential reading easier.
- **Share** controls on verses and eBook pages use the device share sheet when available and copy a deep link otherwise.
- Shared verse links open the relevant surah and scroll to the referenced verse.
- **Print / Save PDF** styling keeps the eBook content clean when readers save a commentary copy.
- Keyboard focus outlines and reduced-motion support improve accessibility without changing the reading content.
- Service-worker cache upgrades now preserve downloaded chapter data instead of discarding a reader’s saved chapters with an app update.
