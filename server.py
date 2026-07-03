import os
import sys
import json
import re
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory, Response
import requests

app = Flask(__name__, static_url_path='', static_folder='.')

BASE = Path(__file__).parent.resolve()

# --- AI Provider Configuration ---
# Supports: "groq" (free, recommended) or "deepseek" (paid)
# Set AI_PROVIDER env var to override (default: groq)
# Groq: get free API key at https://console.groq.com/keys
#   Set GROQ_API_KEY env var or paste below
# DeepSeek: requires paid credits
#   Set DEEPSEEK_API_KEY env var or paste below

AI_PROVIDER = os.environ.get("AI_PROVIDER", "groq")

# Groq config (free tier — set GROQ_API_KEY env var)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")  # or llama-3.1-8b-instant, qwen/qwen3-32b

# DeepSeek config (paid, fallback)
# Set DEEPSEEK_API_KEY env var to use DeepSeek
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"

# Mistral AI config (free tier fallback)
MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY", "u0YMFGONYPEqZHTEChuOUUr9Sw4QZUBI")
MISTRAL_URL = "https://api.mistral.ai/v1/chat/completions"
MISTRAL_MODEL = os.environ.get("MISTRAL_MODEL", "mistral-small-latest")

# Build file mapping from the directory structure
def build_file_map():
    fmap = {}
    for i in range(1, 11):
        cls_dir = BASE / f"Class {i}"
        if not cls_dir.is_dir():
            continue
        for fpath in sorted(cls_dir.iterdir()):
            if not fpath.name.endswith('.md') or 'DUPLICATE' in fpath.name:
                continue
            # Strip "Class N " prefix and ".md" suffix
            name = fpath.stem  # e.g. "Class 6 Mathematics (Nepali)"
            # Remove "Class N " prefix
            m = re.match(r'^Class\s+\d+\s+(.+)$', name)
            if m:
                display = m.group(1).strip()
                fmap[(f"Class {i}", display)] = str(fpath)
    return fmap

FILE_MAP = build_file_map()

# --- PDF URL Mapping ---
# Loads PDF URLs from book_pdf_map.json and builds a lookup table
PDF_CDN_BASE = 'https://giwmscdnone.gov.np/media/pdf_upload/'
_pdf_content_map_path = BASE / 'book_pdf_map.json'

# Nepali subject keywords for matching display subjects to PDF titles
# Each subject maps to one or more Nepali phrases that identify that subject in PDF titles
SUBJECT_NEPALI_KEYWORDS = {
    'nepali': ['नेपाली'],
    'english': ['अंग्रेजी'],
    'math': ['गणित'],
    'optional_math': ['ऐच्छिक गणित'],
    'science': ['विज्ञान तथा प्रविधि', 'विज्ञान'],
    'social_studies': ['सामाजिक अध्ययन', 'सामाजिक'],
    'history': ['इतिहास'],
    'economics': ['अर्थशास्त्र'],
    'accountancy': ['कार्यालय सञ्चालन र लेखा', 'लेखा'],
    'computer_science': ['कम्प्युटर विज्ञान', 'कम्प्युटर'],
    'health': ['स्वास्थ्य'],
    'optional_health': ['ऐच्छिक स्वास्थ्य'],
    'serofero': ['सेरोफेरो'],
    'population': ['जनसंख्या'],
    'education': ['शिक्षा'],
    'civics': ['नागरिक शास्त्र', 'नागरिक'],
    'environmental_science': ['वातावरण विज्ञान', 'वातावारण विज्ञान', 'वातावर'],
    'geography': ['भुगोल'],
    'yoga': ['योग शिक्षा', 'योग'],
    'ayurveda': ['आयुर्वेद शिक्षा', 'आयुर्वेद'],
    'sanskrit': ['संस्कृत'],
    'nitishasram': ['नीतिशास्र', 'नीतिशास्त्र'],
    'bhot_language': ['भोट भाषा'],
    'naturopath': ['प्राकृतिक'],
    'karmakand': ['कर्मकाण्ड'],
    'audit': ['लेखापरिक्षण']
}

DEVANAGARI_DIGITS = str.maketrans('०१२३४५६७८९', '0123456789')

def _to_arabic_digits(s):
    """Convert Devanagari digits to Arabic digits."""
    return s.translate(DEVANAGARI_DIGITS)

def _is_textbook(title):
    """Return True only for actual textbook PDFs."""
    if not title:
        return False
    # Non-textbook patterns to filter out
    non_textbook = [
        'शिक्षक निर्देशिका', 'शिक्षक निर्देशन',
        'विशिष्टीकरण तालिका', 'Specification Grid', 'Specification',
        'सूचना', 'Notice', 'मान्यता', 'समकक्षता',
    ]
    for pat in non_textbook:
        if pat in title:
            return False
    # Also filter TG- URLs
    return True

def _extract_nepali_subject(title):
    """Extract the Nepali subject name from a CDC PDF title."""
    # Remove curriculum center suffix
    clean = re.sub(r'\s*\|.*$', '', title).strip()
    # Remove parenthetical year/edition info
    clean = re.sub(r'\s*\([^)]*\)', '', clean)
    # The Nepali name is everything before कक्षा
    m = re.search(r'^([\u0900-\u097F\s/]+?)\s*(?:कक्षा|Grade|Class)', clean)
    if m:
        return m.group(1).strip()
    return ''

def _get_pdf_subject_slug(title):
    """Return the subject slug for a PDF title.
    Uses the extracted Nepali subject name (not parenthetical lang flags)."""
    ne = _extract_nepali_subject(title)
    if not ne:
        return None
    # Check subject keywords against the EXTRACTED Nepali name (e.g., "गणित")
    # Use longest-keyword-first matching
    all_kw = []
    for slug, keywords in SUBJECT_NEPALI_KEYWORDS.items():
        for kw in keywords:
            all_kw.append((kw, slug))
    all_kw.sort(key=lambda x: -len(x[0]))
    for kw, slug in all_kw:
        if kw in ne:
            return slug
    # Check against full title as fallback (for 'अंग्रेजी' as standalone subject)
    if 'अंग्रेजी' in title and 'अनुवाद' not in title:
        return 'english'
    return None

def _is_english_translation(title):
    """Check if a PDF title is an English translation."""
    return 'अंग्रेजी अनुवाद' in title or 'अङ्ग्रेजी अनुवाद' in title or 'english translation' in title.lower() or 'english version' in title.lower()

# Build (class, subject) -> pdf_url mapping from book_pdf_map.json titles
def _build_pdf_lookup():
    lookup = {}
    try:
        with open(_pdf_content_map_path, 'r', encoding='utf-8') as f:
            pmap = json.load(f)
    except Exception:
        return lookup

    for cid, info in pmap.items():
        pdf_url = info.get('pdf_url', '')
        title = info.get('title', '')
        if not pdf_url or not title:
            continue
        if not _is_textbook(title):
            continue
        # Detect class number (handles both Devanagari and Arabic digits)
        m = re.search(r'(?:कक्षा|Grade|class)\s*([\d०१२३४५६७८९]+)', title, re.I)
        if not m:
            continue
        cls_num_str = _to_arabic_digits(m.group(1))
        try:
            cls_num = int(cls_num_str)
        except ValueError:
            continue
        if cls_num < 1 or cls_num > 12:
            continue
        # Extract subject info
        nepali_name = _extract_nepali_subject(title)
        subject_slug = _get_pdf_subject_slug(title)
        is_eng_trans = _is_english_translation(title)
        cls_key = f"Class {cls_num}"
        entry = {
            'pdf_url': pdf_url, 'title': title,
            'nepali_name': nepali_name, 'subject_slug': subject_slug,
            'is_eng_trans': is_eng_trans
        }
        lookup.setdefault(cls_key, []).append(entry)

    return lookup

PDF_LOOKUP = _build_pdf_lookup()

def _get_display_subject_slug(subj):
    """Map a display subject name to a normalized slug for PDF matching."""
    s = subj.lower().strip()
    # Remove Compulsory/Optional prefix
    is_optional = s.startswith('optional')
    s = re.sub(r'^(compulsory|optional)\s+', '', s)
    # Remove parenthetical
    s_clean = re.sub(r'\s*\([^)]*\)', '', s).strip()
    has_english = 'english' in s or s_clean.endswith('(english)')

    # Direct slug mappings — ORDER MATTERS: more specific keys must come FIRST
    slug_map = [
        ('computer science', 'computer_science'),
        ('environmental science', 'environmental_science'),
        ('optional mathematics', 'optional_math'),
        ('social studies', 'social_studies'),
        ('yoga education', 'yoga'),
        ('nepali', 'nepali'),
        ('english', 'english'),
        ('mathematics', 'optional_math' if is_optional else 'math'),
        ('math', 'optional_math' if is_optional else 'math'),
        ('science', 'science'),
        ('accountancy', 'accountancy'),
        ('account', 'accountancy'),
        ('economics', 'economics'),
        ('history', 'history'),
        ('computer', 'computer_science'),
        ('health', 'health'),
        ('population', 'population'),
        ('education', 'education'),
        ('serofero', 'serofero'),
        ('civics', 'civics'),
        ('yoga', 'yoga'),
        ('ayurveda', 'ayurveda'),
        ('sanskrit', 'sanskrit'),
        ('naturopath', 'naturopath'),
    ]
    for key, slug in slug_map:
        if key in s_clean:
            return slug
    # Check for Nepali words in subject
    for slug, keywords in SUBJECT_NEPALI_KEYWORDS.items():
        for kw in keywords:
            if kw in subj:
                return slug
    return None

def get_pdf_url(cls, subj):
    """Look up PDF URL for a given class and subject using the built lookup."""
    entries = PDF_LOOKUP.get(cls, [])
    if not entries:
        return None

    subj_slug = _get_display_subject_slug(subj)
    if not subj_slug:
        return None

    subj_lower = subj.lower()
    has_eng_in_name = 'english' in subj_lower or '(english)' in subj_lower
    has_nep_in_name = 'nepali' in subj_lower or '(nepali)' in subj_lower or '(nep' in subj_lower

    # Find best matching entry
    best_score = -999
    best_url = None

    for entry in entries:
        slug = entry['subject_slug']
        if not slug:
            continue
        score = 0

        # Primary: subject slug matches
        if slug == subj_slug:
            score += 200
        # Partial: e.g. 'science' slug matching 'science' subject
        elif slug in subj_slug or subj_slug in slug:
            score += 100

        if score == 0:
            continue

        # Language version matching (tiebreaker)
        wants_eng = has_eng_in_name
        wants_nep = not has_eng_in_name
        if wants_eng and entry['is_eng_trans']:
            score += 50
        elif wants_eng and not entry['is_eng_trans']:
            score -= 30
        elif wants_nep and not entry['is_eng_trans']:
            score += 20
        elif wants_nep and entry['is_eng_trans']:
            score -= 30

        if score > best_score:
            best_score = score
            best_url = entry['pdf_url']

    return best_url

def parse_frontmatter(text):
    """Extract YAML frontmatter fields from markdown content."""
    # Normalize line endings
    text = text.replace('\r\n', '\n')
    m = re.match(r'^---\s*\n(.+?)\n---', text, re.DOTALL)
    if not m:
        return {}
    data = {}
    for line in m.group(1).split('\n'):
        line = line.strip()
        if ':' in line:
            sep = line.index(':')
            key = line[:sep].strip()
            val = line[sep+1:].strip().strip('"\'')
            data[key] = val
    return data

def read_file_frontmatter(path):
    """Read just the frontmatter from a markdown file."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            head = f.read(4096)
        return parse_frontmatter(head)
    except Exception:
        return {}

def analyze_book(path):
    """Extract frontmatter, all headings, and chapter info from a markdown file."""
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    content = content.replace('\r\n', '\n')

    fm = parse_frontmatter(content)
    lines = content.split('\n')
    headings = []
    pos = 0

    for i, line in enumerate(lines):
        m = re.match(r'^(#{1,6})\s+(.+)$', line)
        if m:
            level = len(m.group(1))
            raw = m.group(2).strip()
            anchor = None
            clean = raw
            am = re.search(r'\{#ch-(\d+)\}', raw)
            if am:
                anchor = f'ch-{am.group(1)}'
                clean = re.sub(r'\s*\{#ch-\d+\}\s*', '', raw)
            headings.append({
                'level': level, 'text': clean, 'anchor': anchor,
                'line': i, 'pos': pos
            })
        pos += len(line) + 1

    # Chapter detection: find ALL chapter-like headings
    skip_list = ['table of contents', 'contents', 'content', 'index', 'introduction',
                 'preface', 'acknowledgements', 'foreword', 'glossary',
                 'bibliography', 'references', 'appendix',
                 'topic', 'summary', 'exercise', 'review',
                 'विषयवस्तु', 'विषय सूची', 'अनुक्रमणिका','प्रस्तावना','भूमिका']
    nepali_digits = set('०१२३४५६७८९')
    en_digit_start = re.compile(r'^\d+\s*[:.)\s]')
    nepali_digit_start = re.compile(r'^[०१२३४५६७८९]+\s*[:.)\s]')
    unit_prefix = re.compile(r'^(?:Unit|Lesson|Chapter|Module|Section|एकाइ|पाठ|भाग)\s*\d+', re.I)

    chapters = []
    seen_ch_num = set()
    first_h1 = True

    for h in headings:
        text = h['text'].strip()
        text_lower = text.lower().rstrip('.').strip()

        # Skip document title (first h1)
        if h['level'] == 1:
            if first_h1:
                first_h1 = False
                continue

        # Skip non-chapter headings
        if h['level'] > 2:
            continue
        if text_lower in skip_list:
            continue
        if len(text) < 4 and not h['anchor']:
            continue

        is_chapter = False
        if h['anchor']:
            is_chapter = True
        elif en_digit_start.match(text) or nepali_digit_start.match(text):
            is_chapter = True
        elif unit_prefix.match(text):
            is_chapter = True
        # Also accept any `##` or `#` heading that's not a skip word
        elif h['level'] == 2 and len(text) > 5:
            is_chapter = True

        if is_chapter:
            # Deduplicate by anchor
            if h['anchor'] and h['anchor'] in seen_ch_num:
                continue
            if h['anchor']:
                seen_ch_num.add(h['anchor'])
            chapters.append(h)

    # If no chapters with anchors and the file has clear Lesson/Unit markers,
    # scan body text for them as a last resort
    if len([c for c in chapters if c.get('anchor')]) == 0 and len(chapters) <= 1:
        # Check first 800 non-heading lines for "Lesson" or "Unit" patterns
        body_lines = []
        for i, line in enumerate(lines):
            if i > 0 and not re.match(r'^#{1,4}\s+', line):
                body_lines.append((i, line))
        check_text = '\n'.join(l for _, l in body_lines[:300])
        
        has_lesson = bool(re.search(r'^Lesson\s', check_text, re.MULTILINE))
        has_unit = bool(re.search(r'\bUnit\s+\d+\s*:', check_text[:2000]))
        
        if has_lesson or has_unit:
            for line_idx, line in body_lines[:500]:
                stripped = line.strip()
                # Match "Lesson Title" pattern
                lm = re.match(r'^Lesson\s+(.+)$', stripped, re.I)
                if lm:
                    title = lm.group(1).strip()
                    if title and len(title) > 3 and title.lower() != 'topic page':
                        chapters.append({
                            'level': 0, 'text': title, 'anchor': None,
                            'line': line_idx, 'pos': 0, '_from_body': True
                        })
                        if len(chapters) >= 20:
                            break

    # Assign display numbers
    prev_num = 0
    for idx, ch in enumerate(chapters):
        ch['display_num'] = idx + 1
        if ch['anchor']:
            try:
                ch['ch_num'] = int(ch['anchor'].split('-')[1])
            except (ValueError, IndexError):
                ch['ch_num'] = idx + 1
        else:
            ch['ch_num'] = idx + 1

    return {'frontmatter': fm, 'headings': headings, 'chapters': chapters}

@app.route('/api/scan', methods=['GET'])
def scan_books():
    """Scan ALL books and return structured index with real chapters from each file."""
    result = {}
    for (cls, subj), path in sorted(FILE_MAP.items()):
        if cls not in result:
            result[cls] = []
        try:
            analysis = analyze_book(path)
            fm = analysis['frontmatter']
            result[cls].append({
                'name': fm.get('subject', subj) if fm.get('subject') else subj,
                'file': os.path.relpath(path, str(BASE)),
                'frontmatter': fm,
                'chapters': analysis['chapters'],
                'heading_count': len(analysis['headings'])
            })
        except Exception as e:
            result[cls].append({
                'name': subj, 'file': os.path.relpath(path, str(BASE)),
                'error': str(e), 'chapters': [], 'heading_count': 0
            })
    return jsonify(result)

@app.route('/')
def index():
    return send_from_directory(BASE, 'toc_webpage.html')

@app.route('/api/files', methods=['GET'])
def list_files():
    """Return the file mapping for debugging."""
    items = {}
    for (cls, subj), path in sorted(FILE_MAP.items()):
        items.setdefault(cls, {})[subj] = path
    return jsonify(items)

@app.route('/api/resolve', methods=['GET'])
def resolve_file():
    """Resolve a class+subject to its file path and return parsed frontmatter."""
    cls = request.args.get('class', '')
    subj = request.args.get('subject', '')
    path = FILE_MAP.get((cls, subj))
    matched_subj = None
    if not path:
        for (c, s), p in FILE_MAP.items():
            if c == cls and (s.lower() == subj.lower() or subj.lower() in s.lower() or s.lower() in subj.lower()):
                path = p
                matched_subj = s
                break
    if not path:
        return jsonify({"path": None, "exists": False}), 404
    rel = os.path.relpath(path, str(BASE))
    fm = read_file_frontmatter(path)
    result = {"path": rel, "exists": True}
    if matched_subj:
        result["matched_subject"] = matched_subj
    if fm:
        result["frontmatter"] = fm
    return jsonify(result)

@app.route('/api/pdf-url', methods=['GET'])
def pdf_url():
    """Return the PDF URL for a given class/subject if known."""
    cls = request.args.get('class', '')
    subj = request.args.get('subject', '')
    url = get_pdf_url(cls, subj)
    if url:
        return jsonify({"pdf_url": url, "available": True})
    return jsonify({"pdf_url": None, "available": False})

@app.route('/api/read-file', methods=['GET'])
def read_file():
    """Read and return the full content of a textbook markdown file."""
    cls = request.args.get('class', '')
    subj = request.args.get('subject', '')
    path = FILE_MAP.get((cls, subj))
    if not path:
        # fuzzy fallback
        for (c, s), p in FILE_MAP.items():
            if c == cls and (subj.lower() in s.lower() or s.lower() in subj.lower()):
                path = p
                break
    if not path:
        return jsonify({"error": f"File not found for {cls}/{subj}"}), 404
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        rel = os.path.relpath(path, str(BASE))
        return jsonify({"path": rel, "content": content, "size": len(content)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/chapter-content', methods=['GET'])
def chapter_content():
    """Extract and return content for a specific chapter from a markdown file."""
    cls = request.args.get('class', '')
    subj = request.args.get('subject', '')
    ch_idx = request.args.get('index')
    if ch_idx is None:
        return jsonify({"error": "Missing 'index' parameter"}), 400
    try:
        ch_idx = int(ch_idx)
    except ValueError:
        return jsonify({"error": "Invalid chapter index"}), 400

    path = FILE_MAP.get((cls, subj))
    if not path:
        for (c, s), p in FILE_MAP.items():
            if c == cls and (subj.lower() in s.lower() or s.lower() in subj.lower()):
                path = p
                break
    if not path:
        return jsonify({"error": f"File not found for {cls}/{subj}"}), 404

    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        content = content.replace('\r\n', '\n')

        analysis = analyze_book(path)
        chapters = analysis['chapters']
        if not chapters or ch_idx >= len(chapters):
            return jsonify({"error": f"Chapter index {ch_idx} out of range ({len(chapters)} chapters)"}), 404

        ch = chapters[ch_idx]
        lines = content.split('\n')

        # Find start line: the chapter's heading line
        start_line = ch['line']
        # Find end line: next chapter heading, or end of file
        end_line = len(lines)
        for other in chapters:
            if other['line'] > start_line:
                end_line = other['line']
                break

        # Extract content
        ch_lines = lines[start_line:end_line]
        ch_content = '\n'.join(ch_lines)

        # Also try to include content before the heading if it's a body-detected chapter
        if ch.get('_from_body'):
            # Include a few lines before for context
            pre = max(0, start_line - 2)
            ch_content = '\n'.join(lines[pre:end_line])

        lines_before = start_line
        lines_after = len(lines) - end_line

        return jsonify({
            "content": ch_content,
            "chapter": ch,
            "start_line": start_line,
            "end_line": end_line,
            "total_lines": len(lines),
            "lines_before": lines_before,
            "lines_after": lines_after
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Send textbook content + user query to DeepSeek API.
    Body: { class, subject, chapterIndex, query, mode }
    """
    data = request.get_json() or {}
    cls = data.get('class', '')
    subj = data.get('subject', '')
    chapter_index = data.get('chapterIndex')
    query = data.get('query', '')
    mode = data.get('mode', 'ask')  # mcq, mindmap, exercise, ask

    # Accept fileContent from request, or read from filesystem
    content = data.get('fileContent', '')
    if not content:
        # Fallback: read from filesystem (for local dev with old frontend)
        path = FILE_MAP.get((cls, subj))
        if not path:
            for (c, s), p in FILE_MAP.items():
                if c == cls and (subj.lower() in s.lower() or s.lower() in subj.lower()):
                    path = p
                    break
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                return jsonify({"error": f"Failed to read file: {e}"}), 500
        else:
            return jsonify({"error": f"No content provided and file not found for {cls}/{subj}"}), 400

    # Build system prompt based on mode
    subject_header = f"{cls} - {subj}"
    is_nepali = bool(re.search(r'[\u0900-\u097F]', (subj + content[:500])))
    lang = 'Nepali' if is_nepali else 'English'
    lang_instr = 'IMPORTANT: Respond in Nepali language only. Use textbook terminology and explanations.' if is_nepali else 'Respond in English.'
    source_instr = 'Base your answer strictly on the textbook content provided below. Do not use external knowledge or make up information not present in the text.'

    system_prompts = {
        "mcq": f"""You are an AI tutor for {subject_header}. {lang_instr} {source_instr} Generate 10 multiple-choice questions with 4 options each and an answer key. Focus on the most important concepts from the chapter covered in the textbook content. Format as:

## Multiple Choice Questions

1. **Question text?**
   - A) Option A
   - B) Option B  
   - C) Option C
   - D) Option D
   **Answer:** A) Option A

(Continue for all 10 questions)""",

        "mindmap": f"""You are an AI tutor for {subject_header}. {lang_instr} {source_instr} Create a detailed mind map / concept map of the chapter based on the textbook content. Use indentation to show hierarchy. Format as:

## Mind Map: [Chapter Title]

- Main Concept 1
  - Sub-concept 1.1
    - Detail 1.1.1
    - Detail 1.1.2
  - Sub-concept 1.2
- Main Concept 2
  - Sub-concept 2.1
...""",

        "exercise": f"""You are an AI tutor for {subject_header}. {lang_instr} {source_instr} Create a practice exercise set based on the textbook content with:
1. 5 short-answer questions
2. 3 numerical/long-answer problems
3. A brief answer key

Format clearly with sections.""",

        "chapter_exercise": f"""You are an AI tutor for {subject_header}. {lang_instr} {source_instr} This is the most important instruction: Carefully read the provided textbook content for this specific chapter and generate a complete chapter exercise that includes:
1. 5 MCQs (multiple choice questions with 4 options each and answer key)
2. 5 short-answer conceptual questions
3. 3 numerical/long-answer problems with step-by-step solutions
4. A summary of key formulas/concepts from this chapter

Every question must be directly based on the content present in the textbook excerpt below. Do not include any topic not covered in the provided text. Use the exact terminology and examples from the textbook. Format clearly with sections.""",

        "ask": f"""You are an AI tutor for {subject_header}. {lang_instr} {source_instr} Answer the student's question based on the textbook content below. Be thorough, educational, and use examples from the text. If the question is off-topic, politely redirect to the subject matter."""
    }

    # Build mode-specific prompt
    if mode == "extract_chapter":
        chapter_num = (chapter_index or 0) + 1
        system_prompt = f"""You are a textbook content extractor for {subject_header}. {lang_instr} Given the full textbook markdown content below, find the chapter that contains the anchor `{{#ch-{chapter_num}}}` and extract it in clean, readable markdown format. The chapter starts at the heading line containing `{{#ch-{chapter_num}}}`. Include ALL content from that chapter: headings, subheadings, body text, exercises, questions, activities, examples, tables, diagrams, and any other material. Clean up OCR artifacts or garbled text where the original meaning is clear. CRITICAL: Output the chapter content directly — start with the heading and nothing else. No preamble like \"Here is the extracted chapter\", no explanations, no code fences. Just the raw markdown starting from the chapter heading."""
    else:
        system_prompt = system_prompts.get(mode, system_prompts["ask"])

    content_limit = 80000 if mode == "extract_chapter" else 20000

    # If chapter specified, try to extract that section
    chapter_context = ""
    if chapter_index is not None:
        chapter_context = f"\n(The student is asking about Chapter {chapter_index + 1})"

    if mode == "extract_chapter":
        user_prompt = f"""Here is the full textbook content:

=== BEGIN TEXTBOOK CONTENT ===
{content[:content_limit]}
=== END TEXTBOOK CONTENT ===

Extract Chapter {chapter_index + 1} from the content above. Return it cleanly formatted in markdown."""
    else:
        user_prompt = f"""Here is the full textbook content for {subject_header}:

=== BEGIN TEXTBOOK CONTENT ===
{content[:content_limit]}
=== END TEXTBOOK CONTENT ===

{chapter_context}
Student's request: {query}"""

    # Call AI API — try Groq first, fallback to Mistral
    def call_api(api_key, api_url, model):
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 4096,
            "stream": False
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        resp = requests.post(api_url, json=payload, headers=headers, timeout=120)
        resp.raise_for_status()
        return resp.json()

    answer = None
    model_used = None
    last_error = None

    # Try Groq first
    if GROQ_API_KEY:
        try:
            result = call_api(GROQ_API_KEY, GROQ_URL, GROQ_MODEL)
            answer = result['choices'][0]['message']['content']
            model_used = GROQ_MODEL
        except Exception as e:
            last_error = f"Groq failed: {str(e)}"

    # Fallback to Mistral
    if not answer and MISTRAL_API_KEY:
        try:
            result = call_api(MISTRAL_API_KEY, MISTRAL_URL, MISTRAL_MODEL)
            answer = result['choices'][0]['message']['content']
            model_used = MISTRAL_MODEL
        except Exception as e:
            last_error = f"Groq and Mistral both failed. Mistral error: {str(e)}"

    if not answer:
        err_msg = last_error or "No AI provider available. Set GROQ_API_KEY or MISTRAL_API_KEY."
        return jsonify({"error": err_msg}), 502

    return jsonify({
        "answer": answer,
        "model": model_used
    })

@app.route('/api/chat/stream', methods=['POST'])
def chat_stream():
    """Streaming version of /api/chat."""
    data = request.get_json() or {}
    cls = data.get('class', '')
    subj = data.get('subject', '')
    chapter_index = data.get('chapterIndex')
    query = data.get('query', '')
    mode = data.get('mode', 'ask')

    # Accept fileContent from request, or read from filesystem
    content = data.get('fileContent', '')
    if not content:
        path = FILE_MAP.get((cls, subj))
        if not path:
            for (c, s), p in FILE_MAP.items():
                if c == cls and (subj.lower() in s.lower() or s.lower() in subj.lower()):
                    path = p
                    break
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                return jsonify({"error": f"Failed to read file: {e}"}), 500
        else:
            return jsonify({"error": f"No content provided and file not found for {cls}/{subj}"}), 400

    subject_header = f"{cls} - {subj}"
    is_nepali = bool(re.search(r'[\u0900-\u097F]', subj + content[:500]))
    lang_instr = 'IMPORTANT: Respond in Nepali language only. Use textbook terminology and explanations.' if is_nepali else 'Respond in English.'
    source_instr = 'Base your answer strictly on the textbook content provided below. Do not use external knowledge.'
    system_prompts = {
        "mcq": f"You are an AI tutor for {subject_header}. {lang_instr} {source_instr} Generate 10 multiple-choice questions with 4 options each and an answer key. Focus on the most important concepts from the chapter covered in the textbook content.",
        "mindmap": f"You are an AI tutor for {subject_header}. {lang_instr} {source_instr} Create a detailed mind map / concept map of the chapter based on the textbook content. Use indentation to show hierarchy.",
        "exercise": f"You are an AI tutor for {subject_header}. {lang_instr} {source_instr} Create a practice exercise set based on the textbook content with 5 short-answer questions, 3 numerical/long-answer problems, and a brief answer key.",
        "chapter_exercise": f"You are an AI tutor for {subject_header}. {lang_instr} {source_instr} Carefully read the provided textbook content for this specific chapter and generate a complete chapter exercise that includes: 5 MCQs with answer key, 5 short-answer conceptual questions, 3 numerical/long-answer problems with step-by-step solutions, and a summary of key concepts. Every question must be directly based on the content present in the textbook excerpt below.",
        "ask": f"You are an AI tutor for {subject_header}. {lang_instr} {source_instr} Answer the student's question based on the textbook content below. Be thorough, educational, and use examples from the text."
    }

    if mode == "extract_chapter":
        chapter_num = (chapter_index or 0) + 1
        chapter_name = data.get('chapterName', f'Chapter {chapter_num}')
        system_prompt = f"You are a textbook content extractor for {subject_header}. {lang_instr} Given the full textbook markdown content below, find the chapter that contains the anchor `{{#ch-{chapter_num}}}` and extract it in clean, readable markdown format. The chapter starts at the heading line containing `{{#ch-{chapter_num}}}`. Include ALL content from that chapter: headings, subheadings, body text, exercises, questions, activities, examples, tables, diagrams, and any other material. Clean up OCR artifacts or garbled text where the original meaning is clear. CRITICAL: Output the chapter content directly — start with the heading and nothing else. No preamble like \"Here is the extracted chapter\", no explanations, no code fences. Just the raw markdown starting from the chapter heading."
    else:
        system_prompt = system_prompts.get(mode, system_prompts["ask"])

    content_limit = 80000 if mode == "extract_chapter" else 20000

    chapter_context = ""
    if chapter_index is not None:
        chapter_context = f"\n(The student is asking about Chapter {chapter_index + 1})"

    if mode == "extract_chapter":
        user_prompt = f"Here is the full textbook content:\n\n=== BEGIN TEXTBOOK CONTENT ===\n{content[:content_limit]}\n=== END TEXTBOOK CONTENT ===\n\nExtract Chapter {chapter_index + 1} from the content above. Return it cleanly formatted in markdown."
    else:
        user_prompt = f"Here is the full textbook content for {subject_header}:\n\n=== BEGIN TEXTBOOK CONTENT ===\n{content[:content_limit]}\n=== END TEXTBOOK CONTENT ===\n{chapter_context}\nStudent's request: {query}"

    def generate():
        def stream_provider(api_key, api_url, model):
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 4096,
                "stream": True
            }
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            with requests.post(api_url, json=payload, headers=headers, stream=True, timeout=120) as resp:
                resp.raise_for_status()
                for line in resp.iter_lines(decode_unicode=True):
                    if line:
                        if line.startswith("data: "):
                            data_str = line[6:]
                            if data_str.strip() == "[DONE]":
                                break
                            try:
                                chunk = json.loads(data_str)
                                delta = chunk['choices'][0].get('delta', {})
                                if 'content' in delta:
                                    yield delta['content']
                            except json.JSONDecodeError:
                                continue

        yielded = False
        # Try Groq first
        if GROQ_API_KEY:
            try:
                for chunk in stream_provider(GROQ_API_KEY, GROQ_URL, GROQ_MODEL):
                    yielded = True
                    yield chunk
                if yielded:
                    return
            except Exception as e:
                yield f"\n[Groq failed, trying Mistral...]\n"

        # Fallback to Mistral
        if MISTRAL_API_KEY:
            try:
                for chunk in stream_provider(MISTRAL_API_KEY, MISTRAL_URL, MISTRAL_MODEL):
                    yielded = True
                    yield chunk
                if yielded:
                    return
            except Exception as e:
                yield f"\n\n[Error: Groq and Mistral both failed. Mistral error: {str(e)}]"
                return

        if not yielded:
            yield "\n\n[Error: No AI provider available. Set GROQ_API_KEY or MISTRAL_API_KEY.]"

    return Response(generate(), mimetype='text/plain')

if __name__ == '__main__':
    print(f"Server starting...")
    print(f"AI provider: {AI_PROVIDER}")
    key_status = "set" if (GROQ_API_KEY if AI_PROVIDER=='groq' else DEEPSEEK_API_KEY) else "MISSING"
    print(f"API key: {key_status}")
    if AI_PROVIDER == 'groq':
        print(f"Groq model: {GROQ_MODEL}")
    print(f"Files indexed: {len(FILE_MAP)}")
    # Print stats
    by_class = {}
    for (cls, subj) in FILE_MAP:
        by_class.setdefault(cls, 0)
        by_class[cls] += 1
    for cls in sorted(by_class):
        print(f"  {cls}: {by_class[cls]} files")
    app.run(host='127.0.0.1', port=5000, debug=True)
