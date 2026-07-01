"""Scan all .md files, extract exercise sections, save to exercises.json"""
import os, re, json
from pathlib import Path

BASE = Path(__file__).parent.resolve()
EXERCISES_FILE = BASE / 'exercises.json'

# OCR corruption mapping: OCR'd text → standard Devanagari numeral
# Ordered by match length (longest first) to handle overlaps
OCR_TO_DEV = [
    ('\u091c\u094d\u091e', '\u0967'),  # ज्ञ → १ (1)
    ('\u0926\u094d\u0926', '\u0968'),  # द्द → २ (2)
    ('\u0926\u094d\u0927', '\u096a'),  # द्ध → ४ (4)
    ('\u0923\u094d', '\u0966'),        # ण् → ० (0)
    ('\u0918', '\u0969'),              # घ → ३ (3)
    ('\u091b', '\u096b'),              # छ → ५ (5)
    ('\u091f', '\u096c'),              # ट → ६ (6)
    ('\u0920', '\u096d'),              # ठ → ७ (7)
    ('\u0921', '\u096e'),              # ड → ८ (8)
    ('\u0922', '\u096f'),              # ढ → ९ (9)
]
OCR_TO_DEV.sort(key=lambda x: -len(x[0]))

DEV_NUM = set('\u0966\u0967\u0968\u0969\u096a\u096b\u096c\u096d\u096e\u096f')  # ०-९
DEV_MAP = {'\u0966':'0','\u0967':'1','\u0968':'2','\u0969':'3','\u096a':'4',
           '\u096b':'5','\u096c':'6','\u096d':'7','\u096e':'8','\u096f':'9'}

def normalize_devanagari(text):
    """Normalize OCR-corrupted Devanagari numerals to standard Devanagari."""
    for ocr, dev in OCR_TO_DEV:
        text = text.replace(ocr, dev)
    return text

def has_ocr_corruption(text):
    """Check if text contains OCR-corrupted Devanagari numerals."""
    for ocr, _ in OCR_TO_DEV:
        if ocr in text:
            return True
    return False

def dev_to_arabic(s):
    """Convert standard Devanagari numerals (०-९) to Arabic (0-9)."""
    for d, a in DEV_MAP.items():
        s = s.replace(d, a)
    return s

def extract_exercise_number(line):
    """Extract and convert exercise number from a line to Arabic digits string."""
    line = line.strip()
    # First handle any known patterns:
    # "Mixed Exercise" "Review Exercise" "Practice" headings have no number
    if line.lower().startswith(('mixed exercise', 'review exercise', 'practice')):
        return ''

    # Detect OCR corruption and normalize
    if has_ocr_corruption(line):
        line = normalize_devanagari(line)

    # Try Arabic numbers directly
    m = re.search(r'(\d+(?:\.\d+)?)', line)
    if m:
        return m.group(1)

    # Try Devanagari numbers (with । as decimal separator)
    m = re.search(r'([\u0966-\u096f]+(?:\u0964[\u0966-\u096f]+)?)', line)
    if m:
        raw = m.group(1).replace('\u0964', '.')
        return dev_to_arabic(raw)

    return ''

def normalize_exercise_line(line):
    """Normalize a line (heading or number line) to standard Devanagari/Arabic."""
    line = line.strip()
    if has_ocr_corruption(line):
        line = normalize_devanagari(line)
    return line

def parse_chapter_index(num_str):
    """Convert '1.1' or '1' to 0-based chapter index."""
    if not num_str:
        return None
    parts = num_str.split('.')
    try:
        return int(parts[0]) - 1
    except ValueError:
        return None

# Match English exercise headings
EX_HEADING_EN = re.compile(
    r'^(Exercise|Mixed Exercise|Review Exercise|Practice)\s*([\d.]+)?\s*$',
    re.IGNORECASE
)

# Match Nepali exercise heading "अभ्यास" optionally followed by a number
EX_HEADING_NP = re.compile(
    r'^(अभ्यास)\s*([\u0966-\u096f.]+)?\s*$'
)

def is_exercise_heading(line, next_line=None):
    """Check if a line is any exercise heading."""
    s = line.strip()
    if EX_HEADING_EN.match(s):
        return True, 'en'
    if EX_HEADING_NP.match(s):
        return True, 'np'
    return False, None

def extract_exercises_from_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    exercises = []
    i = 0
    while i < len(lines):
        line = lines[i]
        s = line.strip()
        m_en = EX_HEADING_EN.match(s)
        m_np = EX_HEADING_NP.match(s)

        if m_en:
            name = s
            num_str = m_en.group(2) or ''
            chapter_idx = parse_chapter_index(num_str)

            i += 1
            ex_lines = []
            while i < len(lines):
                ns = lines[i].strip()
                if EX_HEADING_EN.match(ns) or EX_HEADING_NP.match(ns):
                    break
                ex_lines.append(lines[i])
                i += 1
            text = ''.join(ex_lines).strip()
            if text:
                exercises.append({
                    'name': name,
                    'number': num_str or '',
                    'chapterIndex': chapter_idx,
                    'text': text
                })

        elif m_np:
            name = s
            num_str = m_np.group(2) or ''
            chapter_idx = parse_chapter_index(num_str)

            # Check next line for exercise number (Dev or OCR-corrupted)
            if not num_str and i + 1 < len(lines):
                next_line = lines[i + 1]
                next_s = next_line.strip()
                next_num = extract_exercise_number(next_s)
                if next_num:
                    num_str = next_num
                    chapter_idx = parse_chapter_index(num_str)
                    name = name + ' ' + next_s
                    i += 2  # skip heading + number line
                else:
                    i += 1
            else:
                i += 1

            ex_lines = []
            while i < len(lines):
                ns = lines[i].strip()
                if EX_HEADING_EN.match(ns) or EX_HEADING_NP.match(ns):
                    break
                ex_lines.append(lines[i])
                i += 1
            text = ''.join(ex_lines).strip()
            if text:
                exercises.append({
                    'name': name,
                    'number': num_str or '',
                    'chapterIndex': chapter_idx,
                    'text': text
                })
        else:
            i += 1

    return exercises

def build_exercise_map():
    result = {}
    for i in range(1, 11):
        cls_dir = BASE / f"Class {i}"
        if not cls_dir.is_dir():
            continue
        for fpath in sorted(cls_dir.iterdir()):
            if not fpath.name.endswith('.md') or 'DUPLICATE' in fpath.name:
                continue
            stem = fpath.stem
            m = re.match(r'^Class\s+\d+\s+(.+)$', stem)
            if not m:
                continue
            subject = m.group(1).strip()
            class_name = f"Class {i}"
            exercises = extract_exercises_from_file(fpath)
            if exercises:
                key = f"{class_name}|{subject}"
                result[key] = {
                    'class': class_name,
                    'subject': subject,
                    'file': str(fpath.relative_to(BASE)),
                    'exercises': exercises
                }
    return result

if __name__ == '__main__':
    print("Scanning markdown files for exercises...")
    data = build_exercise_map()
    total_ex = sum(len(v['exercises']) for v in data.values())
    print(f"Found exercises in {len(data)} files, total {total_ex} exercise sections.")
    with open(EXERCISES_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved to {EXERCISES_FILE}")
    for key, val in sorted(data.items()):
        mapped = sum(1 for e in val['exercises'] if e['chapterIndex'] is not None)
        print(f"  {key}: {len(val['exercises'])} exercises ({mapped} mapped)")
    total_mapped = sum(1 for v in data.values() for e in v['exercises'] if e['chapterIndex'] is not None)
    print(f"  Total: {total_mapped}/{total_ex} exercises have chapterIndex mapped.")
