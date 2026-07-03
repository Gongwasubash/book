#!/usr/bin/env python3
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'E:\class 1 to 10 book\New folder\Nepal Textbooks Grade 1-10 - Markdown')
from server import analyze_book

files = [
    'Class 10/Class 10 Compulsory Mathematics (English).md',
    'Class 6/Class 6 Mathematics (English Transcribed).md',
    'Class 8/Class 8 Nepali 2080.md',
    'Class 6/Class 6 Science (Nepali).md',
    'Class 8/Class 8 Health Physical Education.md',
    'Class 8/Class 8 Vocational Technical Education.md',
]
for fpath in files:
    try:
        result = analyze_book(fpath)
        chs = result['chapters']
        print(f'=== {fpath} ===')
        print(f'  Chapters: {len(chs)}')
        for c in chs[:5]:
            print(f'    {c["display_num"]}. {c["text"][:60]} (line {c["line"]})')
        if len(chs) > 5:
            print(f'    ... and {len(chs)-5} more')
    except Exception as e:
        print(f'=== {fpath} === ERROR: {e}')
    print()
