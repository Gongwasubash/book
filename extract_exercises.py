"""Scan all .md files, extract exercise sections, save to exercises.json"""
import os, re, json
from pathlib import Path

BASE = Path(__file__).parent.resolve()
EXERCISES_FILE = BASE / 'exercises.json'

# OCR corruption mapping: OCR'd text -> standard Devanagari numeral
OCR_TO_DEV = [
    ('\u091c\u094d\u091e', '\u0967'),  # ज्ञ -> १ (1)
    ('\u0926\u094d\u0926', '\u0968'),  # द्द -> २ (2)
    ('\u0926\u094d\u0927', '\u096a'),  # द्ध -> ४ (4)
    ('\u0923\u094d', '\u0966'),        # ण् -> ० (0)
    ('\u0918', '\u0969'),              # घ -> ३ (3)
    ('\u091b', '\u096b'),              # छ -> ५ (5)
    ('\u091f', '\u096c'),              # ट -> ६ (6)
    ('\u0920', '\u096d'),              # ठ -> ७ (7)
    ('\u0921', '\u096e'),              # ड -> ८ (8)
    ('\u0922', '\u096f'),              # ढ -> ९ (9)
]
OCR_TO_DEV.sort(key=lambda x: -len(x[0]))

DEV_NUM = set('\u0966\u0967\u0968\u0969\u096a\u096b\u096c\u096d\u096e\u096f')
DEV_MAP = {'\u0966':'0','\u0967':'1','\u0968':'2','\u0969':'3','\u096a':'4',
           '\u096b':'5','\u096c':'6','\u096d':'7','\u096e':'8','\u096f':'9'}

def normalize_devanagari(text):
    for ocr, dev in OCR_TO_DEV:
        text = text.replace(ocr, dev)
    return text

def has_ocr_corruption(text):
    for ocr, _ in OCR_TO_DEV:
        if ocr in text:
            return True
    return False

def dev_to_arabic(s):
    for d, a in DEV_MAP.items():
        s = s.replace(d, a)
    return s

def extract_exercise_number(line):
    line = line.strip()
    if line.lower().startswith(('mixed exercise', 'review exercise', 'practice')):
        return ''
    if has_ocr_corruption(line):
        line = normalize_devanagari(line)
    m = re.search(r'(\d+(?:\.\d+)?)', line)
    if m:
        return m.group(1)
    m = re.search(r'([\u0966-\u096f]+(?:\u0964[\u0966-\u096f]+)?)', line)
    if m:
        raw = m.group(1).replace('\u0964', '.')
        return dev_to_arabic(raw)
    return ''

def parse_chapter_index(num_str):
    if not num_str:
        return None
    parts = num_str.split('.')
    try:
        return int(parts[0]) - 1
    except ValueError:
        return None

EX_HEADING_EN = re.compile(
    r'^(Exercise|Mixed Exercise|Review Exercise|Practice)\s*([\d.]+)?\s*$',
    re.IGNORECASE
)
EX_HEADING_NP = re.compile(
    r'^(अभ्यास)\s*([\u0966-\u096f.]+)?\s*$'
)

# Pattern to detect chapter headings in the markdown
# Matches: "Chapter 1", "Chapter 1:", "Chapter : 1", "१.", "एकाइ १", "पाठ १", "Unit 1", "Topic 1"
CHAPTER_HEADING = re.compile(
    r'^(?:Chapter\s+(\d+)|chapter\s+(\d+)|Unit\s+(\d+)|'
    r'([\u0966-\u096f]+)[\.\u0964]|'
    r'(?:एकाइ|पाठ|भाग|Lesson)\s+([\u0966-\u096f\d]+))',
    re.IGNORECASE
)

def find_chapter_positions(lines):
    """Scan lines for chapter markers, return list of (line_index, chapterIndex)."""
    positions = []
    for i, line in enumerate(lines):
        s = line.strip()
        if not s:
            continue
        # Try English chapter patterns
        m = re.match(r'^(?:Chapter|chapter|Unit|unit|Lesson|lesson)\s+(\d+)', s)
        if m:
            ch = int(m.group(1)) - 1
            positions.append((i, ch))
            continue
        # Try Devanagari numeral prefix like "१." or "१।" at start of line
        m = re.match(r'^([\u0966-\u096f]+)[\.\u0964]\s', s)
        if m:
            ch = int(dev_to_arabic(m.group(1))) - 1
            if ch >= 0:
                positions.append((i, ch))
                continue
        # Try "एकाइ १" or "पाठ १" or "भाग १"
        m = re.match(r'^(?:एकाइ|पाठ|भाग)\s+([\u0966-\u096f\d]+)', s)
        if m:
            raw = m.group(1)
            if raw.isdigit():
                ch = int(raw) - 1
            else:
                ch = int(dev_to_arabic(raw)) - 1
            positions.append((i, ch))
    return positions

def assign_chapter_by_position(exercises, lines):
    """For exercises without chapterIndex, assign based on position in file."""
    chapter_positions = find_chapter_positions(lines)
    if not chapter_positions:
        return exercises
    # Build a list of chapter boundary positions
    chapter_positions.sort()
    for ex in exercises:
        if ex['chapterIndex'] is not None:
            continue
        # Find the exercise's estimated position (use the exercise name text)
        # We approximate by looking for the exercise name in lines
        ex_line = None
        name_stripped = ex['name'].strip()
        for i, line in enumerate(lines):
            if name_stripped in line:
                ex_line = i
                break
        if ex_line is None:
            continue
        # Find which chapter this line falls in
        assigned_ch = None
        for j, (pos, ch) in enumerate(chapter_positions):
            if pos > ex_line:
                break
            assigned_ch = ch
        if assigned_ch is not None:
            # Verify: don't override if the exercise number says differently
            if ex['chapterIndex'] is None:
                ex['chapterIndex'] = assigned_ch
    return exercises

def extract_exercises_from_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    exercises = []
    i = 0
    while i < len(lines):
        s = lines[i].strip()
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

            if not num_str and i + 1 < len(lines):
                next_line = lines[i + 1]
                next_s = next_line.strip()
                next_num = extract_exercise_number(next_s)
                if next_num:
                    num_str = next_num
                    chapter_idx = parse_chapter_index(num_str)
                    name = name + ' ' + next_s
                    i += 2
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

    # Assign chapter by position for unnumbered exercises
    exercises = assign_chapter_by_position(exercises, lines)
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
