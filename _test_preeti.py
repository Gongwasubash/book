import sys
sys.path.append(r'C:\Users\acer\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages')
from nepali_converter import convert

# Test basic conversion
tests = [
    'Pp6f lahn Lsf',  # Example
    'g]kfn',           # Nepal
    'k|sf]',           # etc
]

for t in tests:
    r = convert(t, 'preeti')
    dev = sum(1 for c in r if '\u0900' <= c <= '\u097F')
    print(f'Input: {t!r} -> Output hex: {r.encode("unicode_escape")!r} (Devanagari: {dev})')

# Test on actual file content
with open('Class 8/Class 8 Maths (Nepali).md', 'r', encoding='utf-8') as f:
    text = f.read()

# Separate frontmatter
import re
m = re.match(r'^(---.*?\n---)\n?(.*)', text, re.DOTALL)
if m:
    fm = m.group(1)
    body = m.group(2)
else:
    fm = ''
    body = text

# Convert body
converted = convert(body, 'preeti')
dev_before = sum(1 for c in text if '\u0900' <= c <= '\u097F')
dev_after = sum(1 for c in converted if '\u0900' <= c <= '\u097F')

print(f'\nFile: Class 8 Maths (Nepali).md')
print(f'Before: {len(text)} chars, {dev_before} Devanagari')
print(f'After:  {len(converted)} chars, {dev_after} Devanagari')
print(f'Output preview (hex): {converted[:200].encode("unicode_escape")!r}')

# Save result
with open('Class 8/Class 8 Maths (Nepali)_unicode.md', 'w', encoding='utf-8') as f:
    f.write(fm + '\n\n' + converted)
print('Saved to _unicode.md')
