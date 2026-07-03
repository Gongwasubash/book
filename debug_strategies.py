import sys; sys.path.insert(0, '.')
import re
import format_books as fb
from pathlib import Path

base = fb.BASE

# Test Class 6 Social Studies
fp = 'Class 6/Class 6 Social Studies.md'
f = base / fp
text = f.read_text(encoding='utf-8')
lines = text.split('\n')
is_nep = fb.detect_language(lines)

print(f'TOTAL: {len(lines)} lines')

# Strategy 1: Clean explicit markers
pat0 = re.compile(r'^[\s्र]*(?:पाठ|पाट)(?!्य)\s*([०१२३४५६७८९\d]+)\s*[:\.\)\-]?\s*(.*?)$')
matches0 = []
for i, line in enumerate(lines):
    s = line.strip()
    m = pat0.match(s)
    if not m:
        continue
    num_raw = m.group(1)
    title = m.group(2).strip() if m.lastindex >= 2 else ''
    if not num_raw:
        continue
    try:
        num = int(fb.d2a(num_raw))
    except ValueError:
        continue
    if 1 <= num <= 80 and i > 3:
        if not title or len(title) < 4:
            title = fb._lookup_title(lines, i)
        if title and len(title) >= 4:
            matches0.append((i, num_raw, num, title[:50]))

print(f'\nStrategy 1 (पाठ N): {len(matches0)} raw matches')
min_line = max(int(len(lines) * 0.06), 30)
filtered0 = [m for m in matches0 if m[0] >= min_line]
print(f'  After min_line={min_line} filter: {len(filtered0)}')

# Strategy 3: Numbered Devanagari lines
pat2 = re.compile(r'^[\s्र]*([०१२३४५६७८९]{1,2})[\.\)]\s+(\S.{0,60})$')
matches2 = []
for i, line in enumerate(lines):
    s = line.strip()
    m = pat2.match(s)
    if not m:
        continue
    num_raw = m.group(1)
    title = m.group(2).strip()
    try:
        num = int(fb.d2a(num_raw))
    except ValueError:
        continue
    if 1 <= num <= 80 and i > 3 and len(title) >= 4:
        matches2.append((i, num_raw, num, title[:50]))

filtered2 = [m for m in matches2 if m[0] >= min_line]
print(f'\nStrategy 3 (N. Title): {len(matches2)} raw, {len(filtered2)} after filter')

# Strategy 4: Lone numbers
matches4 = []
for i in range(len(lines) - 1):
    s = lines[i].strip()
    if re.match(r'^\d{1,2}$', s) and i > 3:
        num = int(s)
        if 1 <= num <= 60:
            ns = lines[i + 1].strip()
            if ns and len(ns) > 5 and not fb.is_noise(ns) and ns[0].isupper():
                matches4.append((i, ns, num))
print(f'\nStrategy 4 (Lone numbers): {len(matches4)}')

# Strategy 5: TOC even-split
toc_entries, toc_end = fb.extract_toc_titles(lines, is_nep)
print(f'\nStrategy 5 (TOC even-split): {len(toc_entries)} TOC entries, end_line={toc_end}')
if toc_entries:
    for i, (num, title) in enumerate(toc_entries[:5]):
        print(f'  {i}: [{num}] {title[:50]}')

# Also check: does वषियसूची match?
s_flat = lines[48].strip().lower().replace(' ', '').replace('्र', '')
print(f'\nTOC header check: L48 = {lines[48].strip()!r}')
h = 'वषियसूची'
print(f'  \"{h}\" in \"{s_flat}\": {h in s_flat}')
