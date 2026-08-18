import os
import re
import json

md_path = r"d:\聯合大學\專題\本傳續寫\騎蹟到府_正傳連載.md"
html_path = r"d:\聯合大學\專題\本傳續寫\index.html"

with open(md_path, 'r', encoding='utf-8') as f:
    raw_md = f.read()

# Let's parse into chapters and sections
lines = raw_md.split('\n')

html_content = []
current_chapter = None
current_section = None
toc = []

# Regex patterns
h1_pattern = re.compile(r"^#\s+(.*?)$")
h2_pattern = re.compile(r"^##\s+(.*?)$")
order_pattern = re.compile(r"^【(.*?)】$")

# Process lines
def format_line(line):
    # Bold
    line = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", line)
    # Highlight / code
    line = re.sub(r"`(.*?)`", r"<code>\1</code>", line)
    return line

# Let's inspect how the markdown is structured
parsed_chapters = []
curr_ch = None
curr_sec = None

for line in lines:
    line_stripped = line.strip()
    if not line_stripped or line_stripped == '---':
        continue
        
    if line_stripped.startswith('# '):
        title = line_stripped[2:].strip()
        if '騎蹟到府' in title and '作者' in title:
            continue # Main book title
        
        curr_ch = {
            'type': 'chapter',
            'title': title,
            'id': f"ch-{len(parsed_chapters)+1}",
            'sections': []
        }
        parsed_chapters.append(curr_ch)
        curr_sec = None
    elif line_stripped.startswith('## '):
        sec_title = line_stripped[3:].strip()
        sec_id = f"sec-{len(parsed_chapters)}-{len(curr_ch['sections'])+1 if curr_ch else 1}"
        curr_sec = {
            'type': 'section',
            'title': sec_title,
            'id': sec_id,
            'content': []
        }
        if curr_ch:
            curr_ch['sections'].append(curr_sec)
    else:
        if curr_sec:
            curr_sec['content'].append(line)
        elif curr_ch:
            if not curr_ch['sections']:
                # fallback section
                curr_sec = {
                    'type': 'section',
                    'title': curr_ch['title'],
                    'id': f"sec-{len(parsed_chapters)}-1",
                    'content': []
                }
                curr_ch['sections'].append(curr_sec)
            curr_sec['content'].append(line)

print(f"Parsed {len(parsed_chapters)} chapters.")
for c in parsed_chapters:
    print(f" - {c['title']} ({len(c['sections'])} sections)")

with open(r"d:\聯合大學\專題\本傳續寫\parsed_data.json", "w", encoding="utf-8") as f:
    json.dump(parsed_chapters, f, ensure_ascii=False, indent=2)
