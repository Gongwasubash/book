import sys; sys.path.insert(0, '.')
import format_books as fb
from pathlib import Path

base = fb.BASE
fp = 'Class 6/Class 6 Social Studies.md'
f = base / fp
text = f.read_text(encoding='utf-8')
lines = text.split('\n')
is_nep = fb.detect_language(lines)

toc_entries, toc_end = fb.extract_toc_titles(lines, is_nep)
print(f'TOC entries: {len(toc_entries)}, end_line: {toc_end}')
for i, (num, title) in enumerate(toc_entries):
    print(f'  {i}: [{num}] {title[:60]}')

# Also show what TOC zone looks like
print(f'\nTOC zone (lines 50-95):')
for i in range(50, 95):
    s = lines[i].strip()
    if s:
        print(f'  L{i}: {s[:100]}')
