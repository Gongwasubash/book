#!/usr/bin/env python3
"""Check Class 6 Maths English Transcribed for units 1-2."""
import re, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('Class 6/Class 6 Mathematics (English Transcribed).md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Show everything between frontmatter and Unit 3 heading (L1189)
print('=== Lines 0-1200 ===')
for i in range(0, 1200):
    t = lines[i].rstrip()
    if t:
        print(f'  L{i}: {t[:120]}')

# Search for "Set", "Whole Number", "Number System" etc.
print('\n=== Searching for unit/chapter keywords ===')
keywords = ['Set', 'Whole Number', 'Number System', 'Integer', 'Fraction', 'Decimal', 'Percentage']
for kw in keywords:
    for i, l in enumerate(lines):
        if kw.lower() in l.lower() and len(l.strip()) < 80:
            print(f'  L{i}: [{kw}] {l.strip()[:100]}')
