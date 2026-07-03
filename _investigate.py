#!/usr/bin/env python3
"""Deep investigation of chapter patterns in body text."""
import re, sys
sys.stdout.reconfigure(encoding='utf-8')

files = [
    'Class 10/Class 10 Compulsory Mathematics (English).md',
    'Class 6/Class 6 Science (Nepali).md',
    'Class 8/Class 8 Health Physical Education.md',
]

for fpath in files:
    with open(fpath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f'\n=== {fpath} === ({len(lines)} lines)')
    
    # Find the body start (after frontmatter and first heading)
    body_start = 0
    content_started = False
    for i, l in enumerate(lines):
        if l.strip().startswith('#'):
            content_started = True
        if content_started and not l.strip().startswith('#'):
            body_start = i
            break
    
    # Show lines around body start
    print(f'  Body starts near line {body_start}:')
    for i in range(max(0, body_start-3), min(len(lines), body_start+15)):
        l = lines[i].rstrip()
        if l:
            print(f'    L{i}: {l[:120]}')
    
    # Look for ALL lines that start with a number pattern
    num_starts = []
    for i, l in enumerate(lines[body_start:], body_start):
        t = l.strip()
        if re.match(r'^\d+\s*[.)]\s+', t):
            num_starts.append((i, t[:100]))
        elif re.match(r'^[०१२३४५६७८९]+\s*[.)]\s+', t):
            num_starts.append((i, t[:100]))
        elif re.match(r'^(?:Unit|Lesson|Chapter|Module|Section|एकाइ|पाठ)\s+\d+', t, re.I):
            num_starts.append((i, t[:100]))
    
    print(f'  Numbered/unit line starts: {len(num_starts)}')
    for i, t in num_starts[:15]:
        print(f'    L{i}: {t}')
    if len(num_starts) > 15:
        print(f'    ... and {len(num_starts)-15} more')
