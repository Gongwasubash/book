#!/usr/bin/env python3
"""Test updated analyze_book on all problem files."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'E:\class 1 to 10 book\New folder\Nepal Textbooks Grade 1-10 - Markdown')
from server import analyze_book

files = [
    'Class 10/Class 10 Compulsory Mathematics (English).md',
    'Class 6/Class 6 Health Physical (Nepali).md',
    'Class 6/Class 6 Health Physical Creative Arts (English).md',
    'Class 6/Class 6 Mathematics (English Transcribed).md',
    'Class 6/Class 6 Science (Nepali).md',
    'Class 7/Class 7 Maths (English).md',
    'Class 8/Class 8 English 2023.md',
    'Class 8/Class 8 Health Physical Education.md',
    'Class 8/Class 8 Maths (English Transcribed).md',
    'Class 8/Class 8 Social Studies Population.md',
    'Class 8/Class 8 Vocational Technical Education.md',
    'Class 9/Class 9 Naturopath 2082.md',
    'Class 9/Class 9 Science Technology 2024.md',
]
for fpath in files:
    try:
        result = analyze_book(fpath)
        chs = result['chapters']
        print(f'{fpath}: {len(chs)} chapters')
        for c in chs[:4]:
            anchor_mark = ' ✓' if c.get('anchor') else ''
            from_body = ' [body]' if c.get('_from_body') else ''
            print(f'  {c["display_num"]}. {c["text"][:50]} (L{c["line"]}){anchor_mark}{from_body}')
        if len(chs) > 4:
            print(f'  ... and {len(chs)-4} more')
    except Exception as e:
        print(f'{fpath}: ERROR: {e}')
    print()
