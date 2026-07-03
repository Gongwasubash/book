import re
from pathlib import Path
p = Path(__file__).parent.resolve() / 'Class 10' / 'Class 10 Compulsory English.md'
text = p.read_text(encoding='utf-8')
dev = sum(1 for c in text if '\u0900' <= c <= '\u097F')
total = sum(1 for c in text if not c.isspace())
print(f'Devanagari chars: {dev} / {total} non-space = {dev/total*100:.2f}%')

# Show some Devanagari chars and context
for m in re.finditer(r'[\u0900-\u097F]{2,}', text[:10000]):
    print(f'  Found: {repr(m.group())} at pos {m.start()} context: {repr(text[max(0,m.start()-30):m.end()+30])}')
    if m.end() > 5000:
        break
