You are auditing a plain-English commentary entry for Qur'an {ref} against the material it was written from. The standard is: every substantive point in the material about this verse appears in the entry (merged where texts overlap), and the entry says nothing the material does not support.

# The verse

{verses_block}

# The material

{material_block}

# The entry under audit

<<<ENTRY>>>
{entry}
<<<END>>>

# Your task

1. List every distinct substantive point the material makes about {ref}: meanings of words, alternative readings, grammar that changes the sense, occasion of revelation, stories, each hadith or report, rulings with conditions, cross-references to other verses, virtues, warnings, lessons, inner readings. Merge points that several texts share. Ignore material that is about a different verse or about the surah as a whole. Ignore a text that merely restates the translation.
2. For each point say whether the entry covers it: "yes", "partial" (mentioned but a meaningful part is missing), or "no".
3. List every statement in the entry that the material does not support, including any reference to a verse the material does not cite, any name, number, date, or grading the material does not give, and any hedge the entry has dropped or added.
4. List every rule violation: Arabic script, a named tafsīr work or author (Ibn Kathīr, Maʿārif, Mufti Shafīʿ, Wāḥiduddīn Khān, Tazkīrul, Tanwīr al-Miqbās, al-Jalālayn, al-Mukhtaṣar, al-Qushayrī, al-Wāḥidī, "the sources", "the commentators"), em dash, semicolon, missing opening quotation of the translation, missing "Phrase by phrase" or "In short" section, a generic heading.

Answer with JSON only, in this exact shape:

{{"points": [{{"text_ids": ["Text 1"], "point": "short paraphrase of the point", "covered": "yes|partial|no"}}],
 "unsupported": ["quoted or closely paraphrased statement from the entry", "..."],
 "violations": ["..."],
 "verdict": "pass|repair"}}

"verdict" is "pass" only when no point is "no", at most one is "partial", and the unsupported and violations lists are empty.
