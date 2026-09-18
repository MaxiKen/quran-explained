# Reading Experience Updates — v2.2

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
