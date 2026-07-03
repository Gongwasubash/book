#!/usr/bin/env python3
"""Find Lesson/Unit headings in Class 10 Math English."""
import re, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('Class 10/Class 10 Compulsory Mathematics (English).md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the ## Content section
for i, l in enumerate(lines):
    if '## Content' in l:
        toc_start = i
        break

print(f'TOC starts at line {toc_start}')
# Show lines from TOC to next structure
for i in range(toc_start, min(len(lines), toc_start + 100)):
    l = lines[i].rstrip()
    if l:
        print(f'  L{i}: {l[:120]}')

# Search for "Lesson" or chapter structure markers throughout the file
print('\n\nSearching for "Lesson" patterns...')
for i, l in enumerate(lines):
    t = l.strip()
    if 'Lesson' in t and len(t) < 80:
        print(f'  L{i}: {t[:120]}')

# Search for "Chapter" patterns
print('\nSearching for "Chapter" patterns...')
for i, l in enumerate(lines):
    t = l.strip()
    if re.search(r'\bChapter\s+\d+', t, re.I):
        print(f'  L{i}: {t[:120]}')

# Search for "Unit" patterns
print('\nSearching for "Unit" patterns...')
for i, l in enumerate(lines):
    t = l.strip()
    if re.search(r'\bUnit\s+\d+', t, re.I):
        print(f'  L{i}: {t[:120]}')

# Check for exercise headers
print('\nSearching for "Exercise" or "Review" patterns...')
for i, l in enumerate(lines):
    t = l.strip()
    if re.match(r'^(?:Exercise|Review|Lesson)\s', t, re.I) and len(t) < 60:
        print(f'  L{i}: {t[:120]}')

# Show total size and check for any ## headings
print(f'\nTotal lines: {len(lines)}')
for i, l in enumerate(lines):
    t = l.strip()
    if t.startswith('##') and len(t) < 60:
        print(f'  ## {t}: L{i}')
