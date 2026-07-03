#!/usr/bin/env python3
"""Find chapter-like patterns in body text for files without headings."""
import re, sys
sys.stdout.reconfigure(encoding='utf-8')

files = [
    'Class 10/Class 10 Compulsory Mathematics (English).md',
    'Class 6/Class 6 Science (Nepali).md',
    'Class 8/Class 8 Social Studies Population.md',
    'Class 8/Class 8 Vocational Technical Education.md',
    'Class 8/Class 8 English 2023.md',
]

for fpath in files:
    with open(fpath, 'r', encoding='utf-8') as f:
        text = f.read()

    print(f'\n=== {fpath} ===')

    # Look for patterns like:
    # - "UNIT N:" or "Unit N:" at the start of a line
    # - "N." or "N)" as chapter numbers  
    # - "Chapter N"
    # - Lines that look like chapter titles (bold, all caps, etc.)
    
    lines = text.split('\n')

    # Pattern 1: "Unit X:", "UNIT X:", "Lesson X:" at start of non-heading lines
    pattern1 = re.finditer(r'^.*?(?:Unit|UNIT|Lesson|LESSON|Chapter|CHAPTER|एकाइ|पाठ)\s*\d+\s*[:.].*$', text, re.MULTILINE)
    p1_matches = [(m.start(), m.group().strip()[:100]) for m in pattern1]
    print(f'  "Unit/Chapter/Lesson N:" patterns: {len(p1_matches)}')
    for _, t in p1_matches[:5]:
        print(f'    -> {t}')

    # Pattern 2: Numbered items like "१. " or "1. " that could be chapter starts
    if any('\u0966' <= c <= '\u096F' for c in text):
        # Devanagari numerals
        pattern2 = re.finditer(r'^([०१२३४५६७८९]+)\s*[.、)\s]\s*(.{10,80})$', text, re.MULTILINE)
    else:
        pattern2 = re.finditer(r'^(\d+)\s*[.、)\s]\s*(.{10,80})$', text, re.MULTILINE)
    p2_matches = [(m.group(1), m.group(2)) for m in pattern2]
    print(f'  Numbered (N.) patterns: {len(p2_matches)}')
    for num, title in p2_matches[:8]:
        print(f'    {num}. {title}')

    # Pattern 3: Lines before/after horizontal rules (---)
    hr_matches = [i for i, l in enumerate(lines) if re.match(r'^[-*_]{3,}$', l.strip())]
    print(f'  Horizontal rules: {len(hr_matches)}')
    for i in hr_matches[:5]:
        ctx = []
        for j in range(max(0, i-2), min(len(lines), i+3)):
            l = lines[j].strip()
            if l and not re.match(r'^[-*_]{3,}$', l):
                ctx.append(l[:80])
        if ctx:
            print(f'    L{i}: {ctx}')

    # Pattern 4: First line of each non-frontmatter section
    body_start = 0
    for i, l in enumerate(lines):
        if l.strip().startswith('#') and i > 1:
            body_start = i
            break
    
    # Look at first 20 content lines after frontmatter
    content_after = [(i, l.strip()) for i, l in enumerate(lines[body_start:body_start+50], body_start) if l.strip() and not l.strip().startswith('#')]
    print(f'  First content lines after title:')
    for i, l in content_after[:8]:
        print(f'    L{i}: {l[:120]}')
