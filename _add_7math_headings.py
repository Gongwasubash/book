#!/usr/bin/env python3
"""Insert chapter headings into Class 7 Maths English.

The file has a TOC (L44-L66) then continuous body text with "Lesson" markers.
No ## headings exist - we need to add them.
"""
import re, sys
sys.stdout.reconfigure(encoding='utf-8')

path = 'Class 7/Class 7 Maths (English).md'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Parse TOC entries from lines 46-66
toc_entries = []
for i in range(46, 67):
    l = lines[i].strip()
    if not l:
        continue
    # Format 1 (piped): | 1 Set | | 1 - 15 | |
    m = re.match(r'^\|?\s*(\d+)\s+(.+?)\s*\|\s*\|?\s*(?:\d+\s*-\s*\d+)?\s*\|?\s*\|?$', l)
    if m:
        toc_entries.append((int(m.group(1)), m.group(2).strip()))
        continue
    # Format 2 (plain): 2 Whole Number 16 - 44
    m = re.match(r'^\|?\s*(\d+)\s+(.+?)\s+(?:\d+\s*-\s*\d+)\s*\|?$', l)
    if m:
        toc_entries.append((int(m.group(1)), m.group(2).strip()))
        continue
    # Last resort
    m = re.match(r'^\|?\s*(\d+)\s+(.+?)\s*\|?$', l)
    if m:
        toc_entries.append((int(m.group(1)), m.group(2).strip()))

print(f"TOC entries: {len(toc_entries)}")
for n, t in toc_entries:
    print(f"  {n}. {t}")

# Find all "Lesson" lines in body
lesson_lines = [i for i, l in enumerate(lines) if l.strip() == 'Lesson' and i > 60]
print(f"\nLesson markers: {len(lesson_lines)} at {lesson_lines}")

# Map TOC entries to lesson markers by index
if len(toc_entries) != len(lesson_lines):
    print(f"WARNING: TOC ({len(toc_entries)}) vs Lessons ({len(lesson_lines)}) - using min")
    count = min(len(toc_entries), len(lesson_lines))
else:
    count = len(toc_entries)

# Insert headings before each "Lesson" marker, working backwards
insertions_made = 0
for i in range(count - 1, -1, -1):
    num, title = toc_entries[i]
    lesson_idx = lesson_lines[i]
    heading = f"## {num}. {title} {{#ch-{num}}}\n"
    lines.insert(lesson_idx, heading)
    insertions_made += 1
    print(f"  Inserted at L{lesson_idx}: {heading.rstrip()}")

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print(f"\nDone! Inserted {insertions_made} headings.")
