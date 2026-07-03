import re, sys
from pathlib import Path

base = Path(__file__).parent.resolve()
out = open(base / '_debug_output.txt', 'w', encoding='utf-8')

def log(s):
    out.write(s + '\n')

p = base / 'Class 8' / 'Class 8 Nepali 2080.md'
text = p.read_text(encoding='utf-8')
lines = text.split('\n')

log('--- Looking for chapter-like lines ---')
for i, line in enumerate(lines):
    s = line.strip()
    if not s:
        continue
    if any(x in s for x in ['Wd', 'Id', 'Ud', 'TOA', 'षाठ', 'था', 'पाठ', 'एकाइ']) and len(s) < 30:
        log(f'  L{i}: {repr(s)}')

log('\n--- Looking for explicit chapter markers ---')
for i, line in enumerate(lines):
    s = line.strip()
    for marker in ['पाठ', 'एकाइ', 'भाग', 'पाट']:
        if s.startswith(marker) or s.startswith('  ' + marker):
            num = s[len(marker):].strip()
            log(f'  L{i}: marker={marker}, num={repr(num)}, full={repr(s)}')

log('\n--- Looking for Wd/Id/Ud patterns ---')
for i, line in enumerate(lines):
    s = line.strip()
    m = re.match(r'^[\s\(\)]*(Wd|Id|Ud|TOA|षाठ|था)\s*([०१२३४५६७८९\d]+)\s*$', s)
    if m:
        log(f'  L{i}: marker={m.group(1)}, num={m.group(2)}')

log('\n--- First 60 lines showing noise-filtered ---')
count = 0
for i, line in enumerate(lines[:150]):
    s = line.strip()
    if s and not re.match(r'^[\s\.\,\>\~\;\:\!\-\(\)\|\[\]\=\+\#\@\©\&\d<>=/\\\'\"\u0964\u0965\(\)]+$', s):
        log(f'  L{i}: {s[:80]}')
        count += 1
        if count >= 40:
            break

out.close()
print('Done. Check _debug_output.txt')
