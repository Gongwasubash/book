#!/usr/bin/env python3
"""Check heading structure in files that are missing {#ch-N} anchors."""
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

targets = [
    'Class 10/Class 10 Compulsory Mathematics (English).md',
    'Class 6/Class 6 Health Physical (Nepali).md',
    'Class 6/Class 6 Health Physical Creative Arts (English).md',
    'Class 6/Class 6 Mathematics (English Transcribed).md',
    'Class 6/Class 6 Science (Nepali).md',
    'Class 7/Class 7 Maths (English).md',
    'Class 8/Class 8 English 2023.md',
    'Class 8/Class 8 Health Physical Education.md',
    'Class 8/Class 8 Maths (English Transcribed).md',
    'Class 8/Class 8 Maths (Nepali)_unicode.md',
    'Class 8/Class 8 Moral Education (Nepali).md',
    'Class 8/Class 8 Nepali 2076.md',
    'Class 8/Class 8 Social Studies Population.md',
    'Class 8/Class 8 Vocational Technical Education.md',
    'Class 9/Class 9 Naturopath 2082.md',
    'Class 9/Class 9 Science Technology 2024.md',
]

for fpath in targets:
    with open(fpath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    headings = []
    for i, line in enumerate(lines):
        m = re.match(r'^(#{1,6})\s+(.+)$', line)
        if m:
            level = len(m.group(1))
            text = m.group(2).strip()[:100]
            headings.append((i, level, text))
    
    print(f'=== {fpath} === ({len(headings)} headings)')
    for i, lvl, text in headings[:8]:
        prefix = '#' * lvl
        print(f'  L{i}: {prefix} {text}')
    if len(headings) > 8:
        print(f'  ... and {len(headings)-8} more headings')
    
    # Find first non-frontmatter content
    body_start = 0
    for i, line in enumerate(lines):
        if i > 0 and line.startswith('#'):
            body_start = i
            break
    print(f'  First heading at line {body_start}')
    
    # Check if headings have numbered prefixes
    num_headings = 0
    nd = '\\u0966\\u0967\\u0968\\u0969\\u096a\\u096b\\u096c\\u096d\\u096e\\u096f'
    for i, lvl, text in headings:
        if re.match(rf'^[{nd}\\d]+\\s*[:.\\s]', text):
            num_headings += 1
    if num_headings > 0:
        print(f'  Numbered: {num_headings}/{len(headings)}')
    else:
        spaces = []
        for i, lvl, text in headings[:5]:
            spaces.append(repr(text[:60]))
        print(f'  First 5 headings: {spaces}')
    print()
