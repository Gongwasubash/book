#!/usr/bin/env python3
"""Check headings in Class 7 Maths English."""
import re, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('Class 7/Class 7 Maths (English).md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print('All headings:')
for i, l in enumerate(lines):
    m = re.match(r'^(#{1,6})\s+(.+)$', l.strip())
    if m:
        level = len(m.group(1))
        text = m.group(2).strip()[:80]
        print(f'  L{i}: {"#"*level} {text}')
