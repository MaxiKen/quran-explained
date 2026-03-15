import os
import re
import json

# Configuration
DATA_DIR = 'data'
BASE_URL = "https://everyayah.com/data/Alafasy_64kbps/{:03d}{:03d}.mp3"

def update_audio_urls():
    # Check if directory exists
    if not os.path.exists(DATA_DIR):
        print(f"Error: Directory '{DATA_DIR}' not found.")
        return

    # Loop through files from chapter_001.js to chapter_114.js
    for i in range(1, 115):
        filename = f"chapter_{i:03d}.js"
        filepath = os.path.join(DATA_DIR, filename)

        if not os.path.exists(filepath):
            print(f"Skipping: {filename} (File not found)")
            continue

        print(f"Processing: {filename}...")

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Regex to extract the variable name and the JSON array content
        # Matches: var name = [ ... ];
        match = re.search(r'(var\s+\w+\s*=\s*)([\s\S]*?)(?=\s*;\s*$|$)', content.strip())
        
        if match:
            prefix = match.group(1)
            json_str = match.group(2)

            try:
                data = json.loads(json_str)
                
                # Update the audio values
                # surah_no is derived from the current file index 'i'
                for theme in data:
                    for verse in theme.get('verses', []):
                        ayah_no = verse.get('ayah_no_surah')
                        # Format: SSSAAA.mp3 (e.g., 001001.mp3)
                        new_audio = BASE_URL.format(i, ayah_no)
                        verse['audio'] = new_audio

                # Convert back to JSON string with nice formatting
                updated_json = json.dumps(data, indent=2, ensure_ascii=False)
                
                # Reconstruct the JS file content
                new_content = f"{prefix}{updated_json};"

                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON in {filename}: {e}")
        else:
            print(f"Could not find valid data structure in {filename}")

    print("\nUpdate complete!")

if __name__ == "__main__":
    update_audio_urls()