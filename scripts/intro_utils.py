import re
import os

def insert_surah_intro(ch_num, intro_markdown):
    filepath = f"markdown commentry/{ch_num:03d}.md"
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Find verse 1 heading pattern
    # Matches ## Sūrah ... {ch_num}:1 or ## {ch_num}:1
    v1_match = re.search(rf"(?m)^##\s+.*?{ch_num}:1\b", content)
    if not v1_match:
        raise ValueError(f"Verse 1 heading not found for chapter {ch_num} in {filepath}")

    # Extract H1 title line
    h1_match = re.search(r"(?m)^#\s+.*$", content[:v1_match.start()])
    if not h1_match:
        # Fallback H1 if not found
        title_line = f"# Sūrah Chapter {ch_num} — Expanded Verse-by-Verse Commentary"
    else:
        title_line = h1_match.group(0).strip()

    # Prepare intro block
    intro_clean = intro_markdown.strip()
    # Ensure it starts with subheadings, not with ## Introduction or **Expanded Commentary**
    # if it doesn't already have them, we add them
    header_block = f"{title_line}\n\n## Introduction to the Sūrah\n\n**Expanded Commentary**\n\n{intro_clean}\n\n---\n\n"

    # The rest of the content starting from verse 1
    rest_of_file = content[v1_match.start():]

    new_content = header_block + rest_of_file

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"Successfully updated Chapter {ch_num:03d} (Intro length: {len(intro_clean)} chars)")

if __name__ == "__main__":
    print("Intro utils ready")
