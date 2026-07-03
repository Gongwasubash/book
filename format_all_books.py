#!/usr/bin/env python3
"""
Universal textbook formatter for Nepal School Textbooks (Grades 1-10).
Handles both Nepali and English books with language-appropriate formatting.
Edits all .md files in-place.

Approach:
1. Remove OCR garbage (shared across all books)
2. Add metadata block with book info
3. Detect chapter/unit markers and build TOC + heading hierarchy
4. Skip restructuring if structure is unclear or too fine-grained
"""

import re
from pathlib import Path

BASE = Path(__file__).parent.resolve()

# ── Shared OCR noise patterns ───────────────────────────────────────────────
NOISE_WORDS = [
    r'\bWa\b', r'\bAa\b', r'\bWw\b', r'\bBlei\b', r'\bTAG\b',
    r'\bata\b', r'\bTAHT\b', r'\bTAT\b', r'\bfast\b', r'\bfes\b',
    r'\bAAT\b', r'\balle\b', r'\bAT\b', r'\bam\b', r'\bAM\b',
    r'\bfan\b', r'\bfens\b', r'\bHae\b', r'\bGS\b', r'\bLl\b',
    r'\bOT\b', r'\bSGT\b', r'\bTT\b', r'\bTTA\b', r'\bGanga\b',
    r'\bMarse\b', r'\bST\b', r'\bTA\b', r'\bkaam\b',
    r'\bSse\b', r'\bko\b', r'\baja\b', r'\bTai\b',
    r'\bWSN\b', r'\bWS\b', r'\bWER\b', r'\bWSS\b',
    r'\bfem\b', r'\bTERT\b', r'\bW Ga\b', r'\bGa\b',
    r'\bdias\b', r'\bKG\b', r'\bae\b', r'\btr\)\b',
    r'\bHet\b', r'\bBSAA\b', r'\bSAA\b', r'\bSas\b', r'\bThess\b',
    r'\bin\b', r'\bx\b', r'\bSN\b',
    r'\bATS\b', r'\bBHA\b', r'\bSAS\b', r'\bRe\b', r'\bfest\b', r'\boy\)\b',
    r'\bTH\b', r'\bdt\b',
    r'\bbn\b', r'\bkm\b', r'\bCo\b', r'\bJO\b',
    r'\bcom\b', r'\bwww\b',
]
NOISE_PATTERN = re.compile('|'.join(NOISE_WORDS))


def detect_language(text):
    dev = sum(1 for c in text if '\u0900' <= c <= '\u097F')
    non_space = sum(1 for c in text if not c.isspace())
    if non_space == 0:
        return 'english'
    return 'nepali' if (dev / non_space) > 0.05 else 'english'


def is_noise(s):
    if not s or len(s) < 2:
        return True
    s = s.strip()
    if re.match(r'^[\.\s]*(?:नेपाली|ENGLISH|English)\s*,?\s*(?:कक्षा|Grade|Class)\s+\d+', s):
        return True
    if re.match(r'^[A-Za-z]{1,3}$', s) and s.lower() not in ['a', 'i']:
        return True
    if re.match(r'^[\s\.\,\>\~\;\:\!\-\(\)\|\[\]\=\+\#\@\©\&\d]+$', s):
        return True
    if re.match(r'^\d{1,4}$', s):
        return True
    if re.match(r'^https?://\S+$', s):
        return True
    return False


def clean_text(text):
    text = re.sub(r'\(cid:\d+\)', '', text)
    text = re.sub(r'https?://\S+', '', text)
    text = re.sub(r'[©®\u00a0]', '', text)
    text = text.replace('|', '।')
    text = re.sub(r'[\>\~\_\`\@\#\$\%\^\*\+\=\"]', '', text)
    text = re.sub(r'[\s\.\,\>\~\;\:\!\#\@\©\&]+', ' ', text)
    text = NOISE_PATTERN.sub('', text)
    text = re.sub(r'\s[ऀ-ऊऎ-ऐऒ-औक-ह]\s', ' ', text)
    text = re.sub(r' {2,}', ' ', text)
    return text.strip()


def count_devanagari(text):
    return sum(1 for c in text if '\u0900' <= c <= '\u097F')


def get_subject_name(filename):
    name = filename.replace('.md', '')
    name = re.sub(r'^Class\s+\d+\s*', '', name)
    name = re.sub(r'^\d+\.\s*', '', name)
    return name.strip() or 'Textbook'


def extract_class_num(class_dir_name):
    m = re.search(r'\d+', class_dir_name)
    return int(m.group()) if m else 0


def detect_chapters(lines, is_nepali):
    """
    Detect chapter/unit boundaries.
    Returns list of (line_index, title_text) or empty list.
    """
    patterns = []
    if is_nepali:
        patterns.append((
            re.compile(r'^(?:पाठ|पाट|पाठ्य)\s*[०१२३४५६७८९\d]+(?:\s*[:\.\)\-]|\s*$)', re.IGNORECASE),
            'nepali_lesson'
        ))
        patterns.append((
            re.compile(r'^एकाइ\s*[०१२३४५६७८९\d]+(?:\s*[:\.\)\-]|\s*$)'),
            'nepali_unit'
        ))
    else:
        patterns.append((
            re.compile(r'^(?:Unit|UNIT)\s+\d+(?:\s*[:\.\)\-]|\s*$)'),
            'english_unit'
        ))
        patterns.append((
            re.compile(r'^(?:Lesson|LESSON)\s+\d+(?:\s*[:\.\)\-]|\s*$)'),
            'english_lesson'
        ))
        patterns.append((
            re.compile(r'^(?:Chapter|CHAPTER)\s+\d+(?:\s*[:\.\)\-]|\s*$)'),
            'english_chapter'
        ))

    for pat, strategy in patterns:
        matches = [(i, lines[i].strip()) for i in range(len(lines))
                   if pat.match(lines[i].strip())]
        if 2 <= len(matches) <= 100:
            print(f"      Using {strategy}: {len(matches)} matches")
            return matches

    # Strategy: lone number + title on next line
    # Filter for sequential numbers and proper titles
    candidates = []
    for i in range(len(lines) - 1):
        s = lines[i].strip()
        if re.match(r'^\d{1,2}$', s) and not is_noise(s):
            next_s = lines[i + 1].strip()
            if next_s and len(next_s) > 4 and len(next_s) < 80 and not is_noise(lines[i+1]):
                # Check it looks like a proper title (first char uppercase or Devanagari)
                first_char = next_s[0]
                is_upper = first_char.isupper() or ('\u0900' <= first_char <= '\u097F')
                if is_upper and not next_s.startswith('|') and not re.search(r'https?://', next_s):
                    candidates.append((i, next_s))
    
    # Check for sequential numbering
    if candidates:
        nums = [int(lines[i].strip()) for i, _ in candidates]
        # Accept if mostly sequential (at least 70% of numbers follow a pattern)
        if len(candidates) >= 3:
            # Only keep those where numbers are in ascending order
            sorted_candidates = sorted(candidates, key=lambda x: int(lines[x[0]].strip()))
            found = []
            expected = int(lines[sorted_candidates[0][0]].strip())
            for i, title in sorted_candidates:
                num = int(lines[i].strip())
                if num == expected:
                    found.append((i, title))
                    expected += 1
                elif num > expected:
                    # Skip missing numbers but don't break
                    expected = num + 1
                    found.append((i, title))
            if 2 <= len(found) <= 100:
                print(f"      Using number+title pairs: {len(found)} matches")
                return found

    # Strategy: subsection numbering (1.1, 2.1...)
    seen = set()
    found = []
    for i, line in enumerate(lines):
        m = re.match(r'^\s*(\d+)\.\d+\s', line)
        if m:
            top = int(m.group(1))
            if top not in seen and 1 <= top <= 60:
                seen.add(top)
                found.append((i, line.strip()))
    if 2 <= len(found) <= 50:
        print(f"      Using subsection numbers: {len(found)} matches")
        return found

    return []


def get_title_from_line(s, is_nepali):
    s = s.strip()
    if is_nepali:
        s = re.sub(r'^(?:पाठ|पाट|पाठ्य|एकाइ|अध्याय)\s*[०१२३४५६७८९\d]+[\s:\.\)\-]*', '', s).strip()
    else:
        s = re.sub(r'^(?:Unit|UNIT|Lesson|LESSON|Chapter|CHAPTER)\s+\d+[\s:\.\)\-]*', '', s, flags=re.IGNORECASE).strip()
        s = re.sub(r'^\d+[\s\.\)\-]+', '', s).strip()
    if not s:
        return "Unit"
    return s


def format_book(filepath):
    print(f"  Processing: {filepath.name}")

    raw = filepath.read_text(encoding='utf-8')
    original_len = len(raw)
    raw_lines = raw.split('\n')

    is_nepali = detect_language(raw)
    fn = filepath.name
    subject = get_subject_name(fn)
    class_num = extract_class_num(filepath.parent.name)

    # Detect chapters
    chapters = detect_chapters(raw_lines, is_nepali)

    # Clean all lines
    cleaned_lines = []
    for line in raw_lines:
        if is_noise(line):
            continue
        c = clean_text(line)
        if not c:
            continue
        cleaned_lines.append(c)

    # Build output
    out = []

    # Metadata
    if is_nepali:
        out.append(f"# {subject}")
        out.append("")
        out.append("| विवरण | मान |")
        out.append("|--------|-----|")
        out.append(f"| **विषय** | {subject} |")
        out.append(f"| **कक्षा** | {class_num} |")
        out.append("| **प्रकाशक** | नेपाल सरकार, शिक्षा, विज्ञान तथा प्रविधि मन्त्रालय, पाठ्यक्रम विकास केन्द्र |")
        out.append("| **स्थान** | सानोठिमी, भक्तपुर |")
        out.append("")
    else:
        out.append(f"# {subject}")
        out.append("")
        out.append("| Field | Value |")
        out.append("|-------|-------|")
        out.append(f"| **Subject** | {subject} |")
        out.append(f"| **Grade** | {class_num} |")
        out.append("| **Publisher** | Government of Nepal, Ministry of Education, Science and Technology, Curriculum Development Centre |")
        out.append("| **Location** | Sanothimi, Bhaktapur |")
        out.append("")

    # TOC
    if chapters:
        if is_nepali:
            out.append("## विषयसूची")
            out.append("")
            out.append("| क्र.स. | शीर्षक |")
            out.append("|--------|--------|")
            for idx, (_, line_text) in enumerate(chapters, 1):
                title = get_title_from_line(line_text, is_nepali)
                anchor = f"पाठ-{idx}"
                out.append(f"| {idx} | [{title}](#{anchor}) |")
        else:
            out.append("## Table of Contents")
            out.append("")
            out.append("| S.No. | Title |")
            out.append("|------|-------|")
            for idx, (_, line_text) in enumerate(chapters, 1):
                title = get_title_from_line(line_text, is_nepali)
                anchor = f"unit-{idx}"
                out.append(f"| {idx} | [{title}](#{anchor}) |")
        out.append("")

        # Content with chapter headings
        for ci, (start_line, _) in enumerate(chapters):
            end_line = chapters[ci + 1][0] if ci + 1 < len(chapters) else len(raw_lines)
            title = get_title_from_line(raw_lines[start_line].strip(), is_nepali)

            if is_nepali:
                heading = f"## पाठ {ci+1}: {title}  {{#पाठ-{ci+1}}}"
            else:
                heading = f"## Unit {ci+1}: {title}  {{#unit-{ci+1}}}"
            out.append(heading)
            out.append("")

            for li in range(start_line + 1, end_line):
                if is_noise(raw_lines[li]):
                    continue
                c = clean_text(raw_lines[li])
                if c:
                    out.append(c)
            out.append("")
    else:
        print(f"      No chapters detected, applying basic cleanup")
        # Just add cleaned content
        out.append("## Content")
        out.append("")
        out.extend(cleaned_lines)

    result = '\n'.join(out)
    result = re.sub(r'\n{4,}', '\n\n\n', result)
    result = result.strip() + '\n'

    filepath.write_text(result, encoding='utf-8')

    ch_count = len(chapters) if chapters else 0
    print(f"      {original_len} -> {len(result)} chars ({result.count(chr(10))+1} lines, {ch_count} chapters)")
    return ch_count


def main():
    class_dirs = sorted(BASE.glob('Class *'))
    total_files = 0
    total_chapters = 0

    for class_dir in class_dirs:
        if not class_dir.is_dir() or not re.match(r'^Class \d+$', class_dir.name):
            continue

        md_files = sorted(class_dir.glob('*.md'))
        if not md_files:
            continue

        print(f"\n{'='*60}")
        print(f"{class_dir.name} ({len(md_files)} files)")
        print(f"{'='*60}")

        for md_file in md_files:
            if '_cleaned' in md_file.stem or 'test' in md_file.stem.lower():
                continue
            try:
                nc = format_book(md_file)
                total_files += 1
                total_chapters += nc
            except Exception as e:
                print(f"    ERROR: {e}")

    print(f"\n{'='*60}")
    print(f"Done: {total_files} files, {total_chapters} total chapters")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
