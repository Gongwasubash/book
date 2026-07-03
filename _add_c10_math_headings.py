#!/usr/bin/env python3
"""Add ## chapter headings to Class 10 Compulsory Mathematics (English).md"""
import os, sys, re
sys.stdout.reconfigure(encoding='utf-8')

BASE = r'E:\class  1 to 10 book\New folder\Nepal Textbooks Grade 1-10 - Markdown'
fpath = os.path.join(BASE, 'Class 10', 'Class 10 Compulsory Mathematics (English).md')

with open(fpath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Verify key positions
checks = {
    62: "Sets",
    854: "Compound Interest",
    1531: "Lesson",  # "Lesson Growth and Depreciation"  
    2099: "Lesson",  # "Lesson Currency and Exchange Rate"
    2542: "Lesson",  # "Lesson Area and Volume"
    3998: "Sequence and Series",
    4696: "Quadratic Equation",
    5313: "Algebraic Fraction",
    5615: "Indices",
    6016: "Triangle and Quadrilaterals",
    6538: "Construction",
    6843: "Circle",
    7387: "Statistics",
    8247: "Probability",
    9012: "Trigonometry",
}

all_ok = True
for ln, expected in checks.items():
    actual = lines[ln].strip()[:50]
    if expected not in actual:
        print(f'MISMATCH at L{ln}: expected "{expected}", got "{actual}"')
        all_ok = False
if all_ok:
    print('All key positions verified!')
else:
    print('Some positions wrong - aborting')
    sys.exit(1)

# Insert headings in reverse order (to preserve line numbers)
insertions = [
    (9012, "Trigonometry", 15),
    (8247, "Probability", 14),
    (7387, "Statistics", 13),
    (6843, "Circle", 12),
    (6538, "Construction", 11),
    (6016, "Triangles and Quadrilaterals", 10),
    (5615, "Indices", 9),
    (5313, "Algebraic Fraction", 8),
    (4696, "Quadratic Equation", 7),
    (3998, "Sequence and Series", 6),
    (2542, "Area and Volume", 5),
    (2099, "Currency and Exchange Rate", 4),
    (1531, "Growth and Depreciation", 3),
    (854, "Compound Interest", 2),
    (62, "Sets", 1),
]

for line_idx, title, ch_num in insertions:
    indent = re.match(r'^(\s*)', lines[line_idx]).group(1)
    new_line = f'{indent}## {title} {{#ch-{ch_num}}}\n'
    lines.insert(line_idx, new_line)
    print(f'  Inserted ## {title} {{#ch-{ch_num}}} at line {line_idx}')

with open(fpath, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print(f'\nDone! Inserted {len(insertions)} chapter headings.')
