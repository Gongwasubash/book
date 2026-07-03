import re
from pathlib import Path

base = Path(__file__).parent.resolve()
out = open(base / '_debug_output2.txt', 'w', encoding='utf-8')

def log(s):
    out.write(s + '\n')

# Test Class 10 Science
p = base / 'Class 10' / 'Class 10 Science.md'
text = p.read_text(encoding='utf-8')
lines = text.split('\n')

log('=== Class 10 Science ===')
log('--- First 150 lines (non-noise) ---')
count = 0
for i, line in enumerate(lines[:150]):
    s = line.strip()
    if s and not re.match(r'^[\s\.\,\>\~\;\:\!\-\(\)\|\[\]\=\+\#\@\©\&\d<>=/\\\'\"\u0964\u0965\(\)]+$', s) and len(s) > 2:
        log(f'  L{i}: {s[:100]}')
        count += 1
        if count >= 50:
            break

log('\n--- Looking for chapter-like lines ---')
for i, line in enumerate(lines[:2000]):
    s = line.strip()
    if not s:
        continue
    if any(x in s for x in ['Wd', 'Id', 'Ud', 'पाठ', 'एकाइ', 'विषयसूची']):
        log(f'  L{i}: {repr(s[:80])}')
    # Devanagari numbered lines
    m = re.match(r'^[०१२३४५६७८९]+[\.\)]\s', s)
    if m:
        log(f'  L{i}: [devnum] {s[:80]}')

# Also check Class 6 English
p2 = base / 'Class 6' / 'Class 6 English.md'
text2 = p2.read_text(encoding='utf-8')
lines2 = text2.split('\n')

log('\n\n=== Class 6 English ===')
log('--- Lines 50-200 ---')
for i in range(50, min(200, len(lines2))):
    s = lines2[i].strip()
    if s and len(s) > 2:
        log(f'  L{i}: {s[:100]}')

# Check Class 9 Social Studies
p3 = base / 'Class 9' / 'Class 9 Social Studies 2079.md'
text3 = p3.read_text(encoding='utf-8')
lines3 = text3.split('\n')

log('\n\n=== Class 9 Social Studies ===')
log('--- Lines 50-150 (non-noise) ---')
count = 0
for i in range(50, min(200, len(lines3))):
    s = lines3[i].strip()
    if s and len(s) > 3:
        log(f'  L{i}: {s[:100]}')
        count += 1
        if count >= 60:
            break

out.close()
print('Done')
