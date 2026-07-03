#!/usr/bin/env python3
"""Add {#ch-N} headings to files that have body content but no chapter headings."""
import re, os, sys
sys.stdout.reconfigure(encoding='utf-8')

BASE = r'E:\class 1 to 10 book\New folder\Nepal Textbooks Grade 1-10 - Markdown'

def add_heading_to_file(relpath, chapter_markers):
    """
    Insert ## Chapter Title {#ch-N} headings at specific line offsets.
    chapter_markers: list of (line_index, title, ch_num)
    """
    fpath = os.path.join(BASE, relpath)
    with open(fpath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Check for existing anchors
    existing = set(re.findall(r'\{#ch-(\d+)\}', ''.join(lines)))
    if existing:
        print(f'  Already has anchors: {sorted(existing, key=int)}')
        # Only add missing ones
        needed = [(idx, title, n) for idx, title, n in chapter_markers if str(n) not in existing]
        if not needed:
            print(f'  All anchors present')
            return False
        chapter_markers = needed
    
    # Process in reverse order to preserve line numbers
    chapter_markers.sort(key=lambda x: -x[0])
    changes = 0
    for line_idx, title, ch_num in chapter_markers:
        indent = re.match(r'^(\s*)', lines[line_idx]).group(1)
        new_heading = f'{indent}## {title} {{#ch-{ch_num}}}\n'
        lines.insert(line_idx, new_heading)
        changes += 1
    
    if changes:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print(f'  Added {changes} headings')
        return True
    return False

# ========== Class 10 Compulsory Mathematics (English) ==========
# Structure: "Lesson" marker at certain lines, with title either on same line or next
# TOC chapters: Sets(1), Compound Interest(2), Growth and Depreciation(3), Currency(4),
# Area and Volume(5), Sequence and Series(6), Quadratic Equation(7), Algebraic Fraction(8),
# Indices(9), Triangles and Quadrilaterals(10), Construction(11), Circle(12), Statistics(13), Probability(14)
with open(os.path.join(BASE, 'Class 10', 'Class 10 Compulsory Mathematics (English).md'), 'r', encoding='utf-8') as f:
    lines = f.readlines()

c10_math_markers = []
# Find "Lesson" lines
lesson_lines = [(i, l.rstrip()) for i, l in enumerate(lines) if l.strip() == 'Lesson' or l.strip().startswith('Lesson ')]
# Lesson lines: 63(Lesson), 853(Lesson), 1531(Lesson Growth), 2099(Lesson Currency), 2542(Lesson Area),
# 3999(Lesson), 4724(Lesson), 5314(Lesson), 5616(Lesson), 6017(Lesson), 6539(Lesson),
# 6844(Lesson), 7388(Lesson), 8246(Lesson), 9011(Lesson)
# But first chapter "Sets" is at line 62, before Lesson on line 63

toc_chapters = [
    (62, "Sets", 1),
    (853, "Compound Interest", 2),
    (1531, "Growth and Depreciation", 3),
    (2099, "Currency and Exchange Rate", 4),
    (2542, "Area and Volume", 5),
    (3999, "Sequence and Series", 6),
    (4724, "Quadratic Equation", 7),
    (5314, "Algebraic Fraction", 8),
    (5616, "Indices", 9),
    (6017, "Triangles and Quadrilaterals", 10),
    (6539, "Construction", 11),
    (6844, "Circle", 12),
    (7388, "Statistics", 13),
    (8246, "Probability", 14),
]
# Actually, check what's at line 9011
print(f"Last lesson line: {lesson_lines[-1]} -> {lines[lesson_lines[-1][0]+1][:60] if lesson_lines[-1][0]+1 < len(lines) else 'N/A'}")

# The remaining content at line 9012+ might be "Exercise 15" or "Answer" section
# Let's check
print(f"Lines 9000-9020:")
for i in range(9000, min(len(lines), 9020)):
    if lines[i].strip():
        print(f"  L{i}: {lines[i].rstrip()[:100]}")

print(f"\nLines 9270-9320:")
for i in range(9270, min(len(lines), 9320)):
    if lines[i].strip():
        print(f"  L{i}: {lines[i].rstrip()[:100]}")

print(f"\nLines 9400-end:")
for i in range(9400, len(lines)):
    if lines[i].strip():
        print(f"  L{i}: {lines[i].rstrip()[:100]}")
