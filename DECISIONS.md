# Decisions, as given by the owner (2026-10-01, revised 2026-10-02, amended 2026-10-02)

These choices govern every chapter this project writes, and stand until the
owner changes them. The pipeline itself is described in
`scripts/tafsir/README.md`.

| Question | Decision |
|---|---|
| Depth per verse | **Full-depth for every verse** (owner revision, 2026-10-02). The verse no longer determines the size of its commentary. Every verse section works in the evidences the corpora actually carry — reports, named authorities, linguistic points, legal and creedal readings, cross-references — targeting roughly 2–3× the earlier evidence-led length (≈800–1,200 words per verse, 3–5 headings). No verse is kept deliberately lean; material must be exhausted, not rationed. |
| Citation style | **Independent voice, works named where they carry the point.** The prose is the book's own. A work may be named for a contested or striking point it uniquely carries ("al-Qurṭubī notes…", "Ibn Kathīr adds…"); reports are still quoted with their collection, and early authorities (Companions, Successors, the first imams) are named where they carry the reading. No source parades: naming a work is a reason to cite it, not decoration. |
| Order | **The owner names the chapters.** Nothing is started until a chapter (or chapter:verse) is named. |
| Cadence | **Continuous.** Once a chapter is named, I work through it without stopping for approval — evidence pack, draft, check, payload, `sw.js` bump, commit and push per chapter — and the owner reads the pushed result and redirects whenever needed. |
| Composition | **Never compose programmatically** (owner amendment, 2026-10-02). Commentary prose is written by hand, verse by verse — no builder scripts, template loops, or string-assembly of sections, which only add predictable structure to the work. Scripts gather evidence, verify format, and build payloads; they never write commentary. Programmatic drafts of Sūrah 2 vv.101–130 were removed on this ruling. Full craft instructions: `COMMENTARY_PROMPT.md`. |

The standard is the owner-approved voice of Sūrah 2 vv.1–100 (`tafsir/002.md`):
flowing commentary written by hand, reports woven as evidence inside the prose,
structure varied verse by verse, the chapter's argument carried throughout.
