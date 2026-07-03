#!/usr/bin/env python3
"""Examine actual content structure of problem files."""
import re, sys
sys.stdout.reconfigure(encoding='utf-8')

files = [
    'Class 10/Class 10 Compulsory Mathematics (English).md',
    'Class 6/Class 6 Science (Nepali).md',
    'Class 6/Class 6 Mathematics (English Transcribed).md',
    'Class 8/Class 8 Social Studies Population.md',
    'Class 8/Class 8 Vocational Technical Education.md',
    'Class 8/Class 8 English 2023.md',
]

for fpath in files:
    with open(fpath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    print(f'=== {fpath} === ({len(lines)} lines)')

    # Show all headings
    headings = []
    for i, l in enumerate(lines):
        m = re.match(r'^(#{1,6})\s+(.+)$', l.strip())
        if m:
            level = len(m.group(1))
            text = m.group(2).strip()[:100]
            headings.append((i, level, text))

    print(f'  Headings ({len(headings)}):')
    for i, level, text in headings[:15]:
        print(f'    L{i}: {"#"*level} {text}')
    if len(headings) > 15:
        print(f'    ... and {len(headings)-15} more')

    # Check for content after line 100
    content_lines = [l for l in lines[100:] if l.strip() and not l.strip().startswith('#')]
    print(f'  Non-heading content lines after line 100: {len(content_lines)}')
    if content_lines:
        print(f'    First: {content_lines[0].strip()[:120]}')
        print(f'    Sample: {content_lines[min(5, len(content_lines)-1)].strip()[:120]}')

    # Check for patterns like "Unit N:", "Chapter N:", numbered items
    unit_patterns = re.findall(r'(?:^|\n)(?:##|#)\s*(?:Unit|Chapter|Lesson|एकाइ|पाठ)\s*\d+', ''.join(lines[:500]), re.I | re.M)
    print(f'  Unit/Chapter headings: {unit_patterns[:5]}')

    print()
