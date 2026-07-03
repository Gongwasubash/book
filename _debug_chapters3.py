#!/usr/bin/env python3
"""Debug chapter detection for zero-chapter books."""
import re, sys
from pathlib import Path

base = Path(r'E:\class  1 to 10 book\New folder\Nepal Textbooks Grade 1-10 - Markdown')

# For books with nepali markers, check the actual body content after the TOC
targets = [
    ('Class 6/Class 6 Nepali.md', True),
    ('Class 7/Class 7 Nepali.md', True),
    ('Class 4/Class 4 Nepali.md', True),
    ('Class 6/Class 6 Social Studies.md', True),
    ('Class 8/Class 8 Social Studies Population.md', True),
    ('Class 6/Class 6 English.md', False),
    ('Class 10/Class 10 Compulsory Mathematics (English).md', False),
    ('Class 7/Class 7 Maths (English).md', False),
    ('Class 10/Class 10 Compulsory Mathematics (Nepali).md', True),
    ('Class 6/Class 6 Science (Nepali).md', True),
    ('Class 5/Class 5 Nepali.md', True),
    ('Class 5/Class 5 Mathematics (Nepali).md', True),
]

for fp, is_nep in targets:
    f = base / fp
    text = f.read_text(encoding='utf-8')
    lines = text.split('\n')

    print(f'=== {fp} ({len(lines)} lines) ===')

    # Find content start (skip first 10% to get past preface/TOC)
    start = int(len(lines) * 0.10)

    # For Nepali: find पाठ N that looks like a real chapter marker
    if is_nep:
        markers = []
        for i in range(start, len(lines)):
            s = lines[i].strip()
            m = re.match(r'^[\s्र]*(?:पाठ)\s+([०१२३४५६७८९\d]+)\s*$', s)
            if m:
                num_raw = m.group(1)
                num = 0
                try:
                    num = int(''.join(str('०१२३४५६७८९'.index(c)) if c in '०१२३४५६७८९' else c for c in num_raw))
                except:
                    try: num = int(num_raw)
                    except: pass
                if num < 1 or num > 60:
                    continue
                # Get next line title
                title = ''
                for j in range(1, 4):
                    if i + j < len(lines):
                        ns = lines[i+j].strip()
                        if ns and len(ns) > 3 and not re.match(r'^[\s्र\(\)]+$', ns):
                            title = ns[:80]
                            break
                markers.append((i, num, title))
                if len(markers) >= 20:
                    break

        if markers:
            print(f'  Found {len(markers)} markers:')
            for i, n, t in markers[:5]:
                print(f'    L{i}: पाठ {n} -> "{t}"')
        else:
            # Try broader search
            print('  No clean पाठ N markers found.')
            # Show first 20 content lines for context
            count = 0
            for i in range(start, len(lines)):
                s = lines[i].strip()
                if s and len(s) > 5:
                    print(f'  L{i}: {s[:80]}')
                    count += 1
                    if count >= 10:
                        break
    else:
        # For English: look for Unit/Lesson/Chapter patterns
        markers = []
        for pat_name, pat in [
            ('Unit', re.compile(r'^Unit\s+(\d+)', re.I)),
            ('Lesson', re.compile(r'^Lesson\s+(\d+)', re.I)),
            ('Chapter', re.compile(r'^Chapter\s+(\d+)', re.I)),
        ]:
            for i in range(start, len(lines)):
                s = lines[i].strip()
                m = pat.search(s)
                if m:
                    num = int(m.group(1))
                    if 1 <= num <= 60:
                        markers.append((i, pat_name, num, s[:80]))
                        if len(markers) >= 5:
                            break
            if markers:
                break

        if markers:
            print(f'  Found {len(markers)} markers:')
            for i, p, n, s in markers[:3]:
                print(f'    L{i}: {p} {n}: "{s}"')
        else:
            print('  No Unit/Lesson/Chapter markers found.')
            # Try numbered patterns like "1. Title"
            count = 0
            for i in range(start, len(lines)):
                s = lines[i].strip()
                m = re.match(r'^(\d+)\.\s+([A-Z][a-zA-Z\s]+)$', s)
                if m:
                    num = int(m.group(1))
                    if 1 <= num <= 40:
                        print(f'  L{i}: {m.group(0)[:80]}')
                        count += 1
                        if count >= 5:
                            break
            if count == 0:
                # Show first 10 content lines
                count = 0
                for i in range(start, len(lines)):
                    s = lines[i].strip()
                    if s and len(s) > 5:
                        print(f'  L{i}: {s[:80]}')
                        count += 1
                        if count >= 10:
                            break
    print()
