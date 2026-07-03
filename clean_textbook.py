#!/usr/bin/env python3
"""
Comprehensive cleaner for Nepal Textbook Grade 8 Nepali (2080).
Strips OCR garbage, normalizes structure, generates clean TOC + sections.
Handles all 17 chapter heading corruptions (Wd, षाठ, Ud, Id, TOA, था, etc.)
"""

import re
from pathlib import Path

BASE = Path(__file__).parent.resolve()
INPUT_FILE = BASE / "Class 8" / "Class 8 Nepali 2080.md"
OUTPUT_FILE = BASE / "Class 8" / "Class 8 Nepali 2080_cleaned.md"

TOC_ENTRIES = [
    (1, "सहिदहरूको सम्झनामा", "कविता"),
    (2, "साकार सपना", "कथा"),
    (3, "स्वामी प्रपन्ताचार्य", "जीवनी"),
    (4, "व्यावसायिक चिठी", "चिठी"),
    (5, "मानव अधिकार", "निबन्ध"),
    (6, "अमर पुत्र", "कथा"),
    (7, "पदमार्ग", "संवाद"),
    (8, "फर्क आफ्नै देश", "कविता"),
    (9, "नेपालको वैदेशिक व्यापार", "प्रबन्ध"),
    (10, "हजुर आमाको जन्मोत्सव", "मनोवाद"),
    (11, "एकजोर जुत्ता", "कथा"),
    (12, "जुन्को ताबेई", "जीवनी"),
    (13, "प्यारो प्रकृति", "कविता"),
    (14, "शैक्षिक भ्रमण", "दैनिकी"),
    (15, "से गुम्बाको सुन्दरता", "यात्रा वर्णन"),
    (16, "सम्पादकलाई चिठी", "चिठी"),
    (17, "डल्ले खोला", "कथा"),
]

# Since OCR severely corrupted chapter markers, use exact line numbers.
# These were manually verified from the source file.
CHAPTER_LINES = {
    94: 1,    # Wd १
    453: 2,   # Wd २
    994: 3,   # Wd 3
    1453: 4,  # षाठ 8
    1859: 5,  # Wd ४
    2269: 6,  # षाठ & (amara putra)
    2782: 7,  # Wd © (padmarga)
    3349: 8,  # TOA (pharka aphnai desh)
    3690: 9,  # मुल पाठ (nepalko baideshik vyapar)
    4121: 10, # Ud १० (hajur amako janmotsav)
    4504: 11, # Id ११ (ekajor jutta)
    5076: 12, # Wd १२ (junko tabai)
    5624: 13, # था (pyaro prakriti) - must check context
    6019: 14, # पाठ 98 (shaikshik bhraman)
    6437: 15, # [1 (se gumbako sundarta)
    6936: 16, # Wd 9G (sampadaklai chithi)
    7246: 17, # पाठ १७ (dalle khola)
}

def get_chapter_markers(lines):
    """Build list of (line_index, chapter_number) from CHAPTER_LINES, verifying the line exists."""
    markers = []
    for line_idx, ch_num in CHAPTER_LINES.items():
        if line_idx < len(lines):
            markers.append((line_idx, ch_num))
    markers.sort()
    return markers

# Section header patterns (including OCR corruptions)
SECTION_NAMES = {
    "शब्दार्थ": "शब्दार्थ",
    "शब्दभण्डार": "शब्दभण्डार",
    "शब्ठभण्डार": "शब्दभण्डार",
    "बोध र अभिव्यक्ति": "बोध र अभिव्यक्ति",
    "सुनाइ र बोलाइ": "सुनाइ र बोलाइ",
    "भाषिक संरचना र वर्णविन्यास": "भाषिक संरचना र वर्णविन्यास",
    "सिर्जना र परियोजना कार्य": "सिर्जना र परियोजना कार्य",
}
SECTION_PATTERNS = [(re.compile(r'^(?:\d+[\s\.]*)*' + re.escape(k)), v) for k, v in SECTION_NAMES.items()]


def is_noise_line(s):
    stripped = s.strip()
    if not stripped:
        return False
    if re.match(r'^[\.\s]*नेपाली,\s*कक्षा\s+८', stripped):
        return True
    if 'कक्षा' in stripped and len(stripped) < 30:
        return True
    if re.match(r'^\d{1,4}$', stripped):
        return True
    if re.match(r'^[\s\.\,\>\~\;\:\!\-\(\)\|\[\]\=\+\#\@\©\&\d]+$', stripped):
        return True
    if re.match(r'^[A-Za-z]{1,3}$', stripped) and stripped not in ['Wa']:
        return True
    return False


def clean_line(text):
    text = re.sub(r'\(cid:\d+\)', '', text)
    text = text.replace('|', '।')
    # Remove leading/trailing ASCII punctuation artifacts only (not Devanagari)
    text = re.sub(r'^[\s\.\,\>\~\;\:\!\#\@\©\&]+', '', text)
    text = re.sub(r'[\s\.\,\>\~\;\:\!\#\@\©\&]+$', '', text)
    text = re.sub(r'\s{2,}', ' ', text)
    return text


def clean_garbage_words(text):
    noise_patterns = [
        r'\bWa\b', r'\bAa\b', r'\bWw\b', r'\bBlei\b', r'\bTAG\b',
        r'\bata\b', r'\bTAHT\b', r'\bTAT\b', r'\bfast\b', r'\bfes\b',
        r'\bAAT\b', r'\balle\b', r'\bAT\b', r'\bam\b', r'\bAM\b',
        r'\bfan\b', r'\bfens\b', r'\bHae\b', r'\bGS\b', r'\bLl\b',
        r'\bOT\b', r'\bSGT\b', r'\bTT\b', r'\bTTA\b', r'\bGanga\b',
        r'\bMarse\b', r'\bST\b', r'\bTA\b', r'\bkaam\b',
        r'\bSse\b', r'\bko\b', r'\bn\b', r'\baja\b', r'\bTai\b',
        r'\bWSN\b', r'\bfens\b', r'\bfast\b', r'\bfes\b',
        r'\bPR\b', r'\bol\b', r'\bWS\b', r'\bWER\b', r'\bWSS\b',
        r'\bfem\b', r'\bTERT\b', r'\bTAG\b', r'\bW Ga\b', r'\bGa\b',
        r'\bdias\b', r'\bKG\b', r'\bae\b', r'\btr\)\b',
        r'\bHet\b', r'\bBSAA\b', r'\bSAA\b', r'\bSas\b', r'\bThess\b',
        r'\bis\b', r'\bin\b', r'\bx\b', r'\bSN\b',
        r'\bATS\b', r'\bBHA\b', r'\bSAS\b', r'\bRe\b', r'\bfest\b', r'\boy\)\b',
        r'\bTH\b', r'\bdt\b',
    ]
    for p in noise_patterns:
        text = re.sub(p, '', text)
    # Clean inline OCR garbage characters (not hyphen, parens, quotes used in Nepali)
    text = re.sub(r'[\>\~\_\`\@\#\$\%\^\*\+\=\"]', '', text)
    # Clean leading/trailing punctuation artifacts within words (not parens, not hyphens)
    text = re.sub(r'^[\s\.\,\;\:\>\~]+', '', text)
    text = re.sub(r'[\s\.\,\;\:\>\~]+$', '', text)
    # Remove isolated single Devanagari chars (likely OCR fragments)
    text = re.sub(r'\s[ऀ-ऊऎ-ऐऒ-औक-ह]\s', ' ', text)
    text = re.sub(r' {2,}', ' ', text)
    return text


def process_textbook():
    raw_text = INPUT_FILE.read_text(encoding='utf-8')
    raw_len = len(raw_text)
    lines = raw_text.split('\n')

    # Get chapter markers from verified line numbers
    found_chapters = get_chapter_markers(lines)
    print(f"Found {len(found_chapters)} chapter markers: {[ch for _, ch in found_chapters]}")

    # ---- Build output ----
    output_parts = []
    output_parts.append("# नेपाली")
    output_parts.append("")
    output_parts.append("| विवरण | मान |")
    output_parts.append("|--------|-----|")
    output_parts.append("| **विषय** | नेपाली |")
    output_parts.append("| **कक्षा** | ८ |")
    output_parts.append("| **प्रकाशक** | नेपाल सरकार, शिक्षा, विज्ञान तथा प्रविधि मन्त्रालय, पाठ्यक्रम विकास केन्द्र |")
    output_parts.append("| **स्थान** | सानोठिमी, भक्तपुर |")
    output_parts.append("| **संस्करण** | प्रथम संस्करण |")
    output_parts.append("| **वर्ष** | वि.सं. २०८० |")
    output_parts.append("")

    # TOC
    output_parts.append("## विषयसूची")
    output_parts.append("")
    output_parts.append("| क्र.स. | शीर्षक | विधा |")
    output_parts.append("|--------|--------|------|")
    for num, title, genre in TOC_ENTRIES:
        output_parts.append(f"| {num} | [{title}](#पाठ-{num}) | {genre} |")
    output_parts.append("")

    # ---- Detect appendix start for trimming last chapter ----
    appendix_start = None
    for idx, line in enumerate(lines):
        if 'परिशिष्ठ' in line or 'परिशिष्ट' in line:
            appendix_start = idx
            break

    # ---- Process each chapter ----
    for ci, (start_idx, ch_num) in enumerate(found_chapters):
        if ci + 1 < len(found_chapters):
            end_idx = found_chapters[ci + 1][0]
        else:
            # Trim appendix from last chapter if found
            if appendix_start and appendix_start > start_idx:
                end_idx = appendix_start
            else:
                end_idx = len(lines)

        if ch_num <= len(TOC_ENTRIES):
            _, ch_title, ch_genre = TOC_ENTRIES[ch_num - 1]
        else:
            ch_title, ch_genre = f"पाठ {ch_num}", ""

        output_parts.append(f"## पाठ {ch_num}: {ch_title}  {{#पाठ-{ch_num}}}")
        output_parts.append("")
        if ch_genre:
            output_parts.append(f"*विधा: {ch_genre}*")
            output_parts.append("")

        # Extract and clean chapter lines
        chapter_lines = lines[start_idx + 1:end_idx]
        cleaned_lines = []
        for line in chapter_lines:
            if is_noise_line(line):
                continue
            cleaned = clean_line(line)
            cleaned = clean_garbage_words(cleaned)
            s = cleaned.strip()
            if not s:
                continue
            # Skip the garbled chapter marker text that might remain
            if re.match(r'^[\(\[]?\d+[\)\]]?\s*[A-Za-z]*$', s) and len(s) < 10:
                continue
            # Post-clean check for short ASCII junk or pure noise
            if re.match(r'^[A-Za-z]{1,3}$', s) and s not in ['Wa']:
                continue
            if re.match(r'^[A-Za-z]{1,3}[\)\]]$', s):
                continue
            cleaned_lines.append(s)

        # Detect sections
        section_map = {}
        current_sec = None
        pre_body = []
        main_body = []
        found_any_section = False
        
        # Determine which lines are pre-discussion vs main text
        # The first few lines are typically discussion prompts (with "१." numbering)
        # Then comes the actual literary text
        literary_markers = [t for _, t, _ in TOC_ENTRIES]
        
        in_literary = False
        for s in cleaned_lines:
            matched_sec = None
            for pattern, norm_name in SECTION_PATTERNS:
                if pattern.match(s):
                    matched_sec = norm_name
                    break

            if matched_sec:
                current_sec = matched_sec
                section_map.setdefault(current_sec, [])
                found_any_section = True
            else:
                # Check if this line starts the literary text
                if not in_literary:
                    for marker in literary_markers:
                        if marker in s:
                            in_literary = True
                            break
                
                if current_sec:
                    section_map.setdefault(current_sec, []).append(s)
                elif in_literary:
                    main_body.append(s)
                else:
                    pre_body.append(s)

        # Write pre-discussion
        if pre_body:
            output_parts.append("### पूर्वछलफल")
            output_parts.append("")
            output_parts.append('\n\n'.join(pre_body))
            output_parts.append("")

        # Write main body
        if main_body:
            output_parts.append("### मूल पाठ")
            output_parts.append("")
            output_parts.append('\n\n'.join(main_body))
            output_parts.append("")
        
        if not pre_body and not main_body and not found_any_section:
            # All content is main body
            output_parts.append("### मूल पाठ")
            output_parts.append("")
            output_parts.append('\n\n'.join(cleaned_lines))
            output_parts.append("")

        # Write sections in canonical order
        canonical_order = ["शब्दार्थ", "शब्दभण्डार", "बोध र अभिव्यक्ति",
                          "सुनाइ र बोलाइ", "भाषिक संरचना र वर्णविन्यास",
                          "सिर्जना र परियोजना कार्य"]
        for sec_name in canonical_order:
            if sec_name in section_map and section_map[sec_name]:
                output_parts.append(f"### {sec_name}")
                output_parts.append("")
                output_parts.append('\n\n'.join(section_map[sec_name]))
                output_parts.append("")

        for sec_name, sec_lines in section_map.items():
            if sec_name not in canonical_order:
                output_parts.append(f"### {sec_name}")
                output_parts.append("")
                output_parts.append('\n\n'.join(sec_lines))
                output_parts.append("")

    # ---- Add appendix (सुनाइ पाठ) ----
    if appendix_start and appendix_start > found_chapters[-1][0]:
        output_parts.append("## परिशिष्ठ: सुनाइ पाठहरू")
        output_parts.append("")
        output_parts.append("*विधा: सुनाइ पाठ (Listening Lessons)*")
        output_parts.append("")
        
        # Only process lines after appendix marker
        appendix_lines = lines[appendix_start + 1:]
        current_listening = None
        listening_sections = {}
        
        for line in appendix_lines:
            if is_noise_line(line):
                continue
            cleaned = clean_line(line)
            cleaned = clean_garbage_words(cleaned)
            s = cleaned.strip()
            if not s:
                continue
            
            # Detect new listening lesson
            m = re.match(r'^(?:सुनाइ|सुवाइ)\s+पाठ\s+([\d०१२३४५६७८९&]+)', s)
            if m:
                current_listening = s
                listening_sections[current_listening] = []
                continue
            
            if current_listening:
                listening_sections.setdefault(current_listening, []).append(s)
            else:
                listening_sections.setdefault("सुनाइ पाठ", []).append(s)
        
        for title, content in listening_sections.items():
            output_parts.append(f"### {title}")
            output_parts.append("")
            output_parts.append('\n\n'.join(content))
            output_parts.append("")

    return '\n'.join(output_parts), raw_len


result, raw_len = process_textbook()
result = re.sub(r'\n{4,}', '\n\n\n', result)
result = result.strip() + '\n'

OUTPUT_FILE.write_text(result, encoding='utf-8')
print(f"Cleaned file written to: {OUTPUT_FILE}")
print(f"Original size: {raw_len} chars")
print(f"Cleaned size: {len(result)} chars ({result.count(chr(10))+1} lines)")
chapters_found = result.count('## पाठ ')
print(f"Chapters processed: {chapters_found}")
