import sys; sys.path.insert(0, '.')
import format_books
from pathlib import Path

base = format_books.BASE

# Test Class 4 Nepali
fp = 'Class 4/Class 4 Nepali.md'
f = base / fp
text = f.read_text(encoding='utf-8')
lines = text.split('\n')
is_nep = format_books.detect_language(lines)

print(f'TOC headers in Class 4 Nepali:')
print(f'  is_nep={is_nep}')
toc_entries, toc_end = format_books.extract_toc_titles(lines, is_nep)
print(f'  TOC entries: {len(toc_entries)}')
if toc_entries:
    for i, (num, title) in enumerate(toc_entries):
        print(f'    {i}. [{num}] {title[:50]}')
print(f'  TOC end line: {toc_end}')

# Also check Class 5 Math Nepali
fp2 = 'Class 5/Class 5 Mathematics (Nepali).md'
f2 = base / fp2
text2 = f2.read_text(encoding='utf-8')
lines2 = text2.split('\n')
is_nep2 = format_books.detect_language(lines2)

print(f'\nTOC headers in Class 5 Math Nepali:')
toc_entries2, toc_end2 = format_books.extract_toc_titles(lines2, is_nep2)
print(f'  TOC entries: {len(toc_entries2)}')
if toc_entries2:
    for i, (num, title) in enumerate(toc_entries2):
        print(f'    {i}. [{num}] {title[:50]}')
print(f'  TOC end line: {toc_end2}')
