import sys; sys.path.insert(0, '.')
import format_books as fb
from pathlib import Path

base = fb.BASE

# Check Class 6 Social Studies - previously had 57 chapters
fp = 'Class 6/Class 6 Social Studies.md'
f = base / fp
text = f.read_text(encoding='utf-8')
lines = text.split('\n')
is_nep = fb.detect_language(lines)

print(f'is_nep={is_nep}, total_lines={len(lines)}')

# Run detect_chapters
chapters = fb.detect_chapters(lines, is_nep)
print(f'Chapters found: {len(chapters) if chapters else 0}')
if chapters:
    for i, (lnum, title, num) in enumerate(chapters[:10]):
        print(f'  {i}: L{lnum} [{num}] {title[:60]}')

# Now check the first strategy (numbered lines with Devanagari digits)
import re
nep_pats = [
    (re.compile(r'^[\s्र]*(?:पाठ|पाट)(?!्य)\s*([०१२३४५६७८९\d]+)\s*[:\.\)\-]?\s*(.*?)$'), 1, 2),
    (re.compile(r'^[\s्र]*(एकाइ|एकाई|इकाइ)\s*[—\-]?\s*([०१२३४५६७८९\d]{1,2})\s*[:\.\)\-]?\s*(.*?)$'), 2, 3),
    (re.compile(r'^[\s्र]*([०१२३४५६७८९]{1,2})[\.\)]\s+(\S.{0,60})$'), 1, 2),
]

all_matches = set()
for pat_idx, (pat, ng, tg) in enumerate(nep_pats):
    for i, line in enumerate(lines):
        s = line.strip()
        m = pat.match(s)
        if m:
            num_raw = m.group(ng)
            title = m.group(tg).strip() if m.lastindex >= tg else ''
            if num_raw:
                try:
                    num = int(fb.d2a(num_raw))
                    if 1 <= num <= 80 and i > 3:
                        all_matches.add((i, num_raw, num, title[:40], pat_idx))
                except ValueError:
                    pass

print(f'\nTotal pat matches: {len(all_matches)}')
for i, raw, num, title, pat_idx in sorted(all_matches)[:30]:
    print(f'  L{i} (pat{pat_idx}): num_raw={raw}, num={num}, title={title}')
