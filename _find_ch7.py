#!/usr/bin/env python3
"""Insert ## chapter headings into Class 10 Compulsory Mathematics (English).md"""
import os, sys, re
sys.stdout.reconfigure(encoding='utf-8')

BASE = r'E:\class  1 to 10 book\New folder\Nepal Textbooks Grade 1-10 - Markdown'
fpath = os.path.join(BASE, 'Class 10', 'Class 10 Compulsory Mathematics (English).md')

with open(fpath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Check existing anchors
existing = set(re.findall(r'\{#ch-\d+\}', ''.join(lines)))
print(f'Existing anchors: {existing}')

# Define insertions: (line_number, title, ch_num)
# The structure found:
insertions = [
    # Ch 1: "Sets" at L62, "Lesson" at L63 -> insert heading before "Sets"
    (62, "Sets", 1),
    # Ch 2: "Lesson" at L853, "Compound Interest" at L854 -> insert at L854  
    (854, "Compound Interest", 2),
    # Ch 3: "Lesson Growth and Depreciation" at L1531
    (1531, "Growth and Depreciation", 3),
    # Ch 4: "Lesson Currency and Exchange Rate" at L2099
    (2099, "Currency and Exchange Rate", 4),
    # Ch 5: "Lesson Area and Volume" at L2542
    (2542, "Area and Volume", 5),
    # Ch 6: "Sequence and Series" at L3998, "Lesson" at L3999
    (3998, "Sequence and Series", 6),
    # Ch 7: Find "Quadratic Equation" 
    # Search for it
]

# Find "Quadratic Equation" in the file
found_qe = None
for i, l in enumerate(lines):
    if 'Quadratic Equation' in l and l.strip().startswith('7'):
        found_qe = i
        print(f'Found "Quadratic Equation" at L{i}: {l.rstrip()[:100]}')
        break

# Also search around L4680-L4750 for chapter 7 content
print('\nSearching for Ch 7 boundaries...')
for i in range(4680, 4760):
    if lines[i].strip():
        print(f'  L{i}: {lines[i].rstrip()[:100]}')

# Find the pattern: before "Lesson" marker, there's often "Mathematics, grade -10" 
# and a chapter title line. Search more broadly.
print('\nLooking for "7." in file...')
for i, l in enumerate(lines):
    t = l.strip()
    if t.startswith('7. '):
        print(f'  L{i}: {t[:100]}')
