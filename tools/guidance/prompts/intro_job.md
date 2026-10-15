# Job

Write the introduction to Surah {surah}, {name_en} ({meaning}), {type}, {n_verses} verses.

The introduction is what a reader sees before verse 1. It is written from the material below, which is the opening of the commentaries on this surah, and from the outline of the surah's themes that the app already carries. Use only what concerns the surah as a whole: its name or names and what they mean, when and where it was revealed and what the material says about the circumstances, its virtues and how the Prophet ﷺ and his Companions used it, how many verses it has, where it sits in the Qur'an and how it connects with the surah before it, what it covers from beginning to end, and its central message. Leave the verse-by-verse explanation to the verse entries: do not explain verse 1 here.

Shape, in Markdown:

1. Opening paragraph or two, no heading: what this surah is and why it matters.
2. `###` sections as the material needs, with specific headings in sentence case, such as: What the name means · When it was revealed · What the surah covers · Its virtues · How it connects to the previous surah. A section exists only if the material has something to put in it.
3. `### In short`: two to five bullet points.

Everything in the material that concerns the surah as a whole goes in, once. Nothing from outside the material and the outline goes in. Same voice and rules as for verse entries: plain modern English, no Arabic script, no naming of the texts or their authors, no em dashes, no semicolons, no tables, links, HTML or horizontal rules.

# The surah's own outline (from the app)

{themes_block}

# The first verse

{verses_block}

# The material

{material_block}

# Output format

<<<INTRO {surah}>>>
(the introduction)
<<<END>>>

<<<NOTES>>>
(one line per point left out and why, or none)
<<<END>>>


# Chapter-session scope

Write only the requested chapter/job. Chapters can be generated in any order
in different sessions; earlier chapters need not already be generated. Within
the selected chapter, keep verse order and source-grounded self-contained
entries. Do not invent connections to previously generated content. The
orchestrating agent must follow CHAPTER_RUN.md: work-output checks throughout,
one full published-chapter verification only after the introduction and every
verse are complete, then a chapter-local completion receipt and exact file
change manifest. These operational notes are not part of the commentary output
or its verse/intro/NOTES markers.
