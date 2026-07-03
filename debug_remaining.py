import re
from pathlib import Path

base = Path(r'E:\class  1 to 10 book\New folder\Nepal Textbooks Grade 1-10 - Markdown')

files = [
    ('Class 10/Class 10 Compulsory Mathematics (English).md', False),
    ('Class 10/Class 10 Optional Mathematics.md', True),
    ('Class 4/Class 4 Nepali.md', True),
    ('Class 5/Class 5 Mathematics (Nepali).md', True),
    ('Class 6/Class 6 Health Physical Creative Arts (English).md', False),
    ('Class 6/Class 6 Mathematics (English Transcribed).md', True),
    ('Class 6/Class 6 Science (Nepali).md', True),
    ('Class 7/Class 7 Maths (English).md', False),
    ('Class 7/Class 7 Maths (Nepali).md', True),
    ('Class 8/Class 8 English 2023.md', False),
    ('Class 8/Class 8 Health Physical Education.md', False),
    ('Class 8/Class 8 Maths (English Transcribed).md', False),
    ('Class 8/Class 8 Moral Education (Nepali).md', False),
    ('Class 8/Class 8 Nepali 2076.md', False),
    ('Class 8/Class 8 Social Studies Population.md', False),
    ('Class 8/Class 8 Vocational Technical Education.md', False),
    ('Class 9/Class 9 Naturopath 2082.md', True),
    ('Class 9/Class 9 Optional Mathematics 2074.md', True),
    ('Class 9/Class 9 Science Technology 2024.md', False),
]

for fp, is_nep in files:
    f = base / fp
    text = f.read_text(encoding='utf-8')
    lines = text.split('\n')
    
    # Detect if language detection is wrong
    dev_count = sum(1 for c in text if '\u0900' <= c <= '\u097F')
    dev_ratio = dev_count / len(text) if text else 0
    
    # Find TOC-like headers
    toc_headers = []
    if is_nep:
        hdrs = ['विषयसूची', 'सामग्री', 'अनुक्रमणिका', 'Contents', 'विषय']
    else:
        hdrs = ['table of contents', 'contents', 'index']
    
    # Find chapter-like patterns
    unit_lines = []
    chapter_lines = []
    lesson_lines = []
    
    for i, line in enumerate(lines):
        s = line.strip()
        if not s or s.startswith('#'):
            continue
        
        if is_nep:
            # Nepali patterns
            if re.match(r'^(पाठ|एकाइ|अध्याय)\s+\d+', s):
                unit_lines.append((i, s[:80]))
        else:
            # English patterns
            if re.match(r'^(Unit|Lesson|Chapter|Module)\s+\d+', s, re.IGNORECASE):
                unit_lines.append((i, s[:80]))
        
        # Check TOC-like headers
        for h in hdrs:
            if h in s and len(s) < 40:
                toc_headers.append((i, s[:80]))
                break
        
        # Check for "Unit N" or "Lesson N" patterns (English)
        if not is_nep:
            m = re.match(r'^(\d+)\.\s+(.+?)(?:\s+\d+)?$', s)
            if m:
                num = int(m.group(1))
                if 1 <= num <= 30:
                    lesson_lines.append((i, s[:80]))
    
    # For Nepali, also check "था N" and "N. Title" patterns
    if is_nep:
        for i, line in enumerate(lines):
            s = line.strip()
            if re.match(r'^\d+[\.\)]\s+\S', s):
                num = int(re.match(r'(\d+)', s).group(1))
                if 1 <= num <= 30:
                    lesson_lines.append((i, s[:80]))
    
    print(f'=== {fp} ===')
    print(f'  Size: {len(text):>6}, Dev: {dev_ratio:.2%} ({dev_count})')
    print(f'  Unit/Chapter lines: {len(unit_lines)}')
    if unit_lines:
        for li, ls in unit_lines[:8]:
            print(f'    L{li}: {ls}')
        if len(unit_lines) > 8:
            print(f'    ... ({len(unit_lines)-8} more)')
    print(f'  TOC-like headers: {len(toc_headers)}')
    if toc_headers:
        for li, ls in toc_headers[:3]:
            print(f'    L{li}: {ls}')
    print(f'  Numbered lesson lines: {len(lesson_lines)}')
    if lesson_lines:
        for li, ls in lesson_lines[:5]:
            print(f'    L{li}: {ls}')
        if len(lesson_lines) > 5:
            print(f'    ... ({len(lesson_lines)-5} more)')
    print()
