#!/usr/bin/env python3
"""
Universal textbook formatter for Nepal School Textbooks (Grades 1-10).
"""

import re, sys
from pathlib import Path

BASE = Path(__file__).parent.resolve()
DRY_RUN = '--dry-run' in sys.argv
SINGLE_FILE = None
for i, a in enumerate(sys.argv):
    if a == '--single' and i + 1 < len(sys.argv):
        SINGLE_FILE = Path(sys.argv[i + 1])
        if not SINGLE_FILE.is_absolute():
            SINGLE_FILE = BASE / SINGLE_FILE
SAFE_MODE = '--safe' in sys.argv

DEV2ARAB = str.maketrans('०१२३४५६७८९', '0123456789')
ARAB2DEV = str.maketrans('0123456789', '०१२३४५६७८९')

def d2a(s):
    return s.translate(DEV2ARAB)
def a2d(s):
    return s.translate(ARAB2DEV)

# OCR-corrupted Devanagari digits (common TOC number corruptions)
CORRUPTED_DEV_DIGITS = {
    'ज्ञ': 1, 'द्द': 2, 'द्': 2, 'घ': 3, 'द्ध': 4,
    'छ': 5, 'ट': 6, 'ठ': 7, 'ड': 8, 'ढ': 9, 'ण्': 0,
}

def parse_corrupted_num(s):
    """Parse a potentially OCR-corrupted Devanagari number into an int."""
    s = s.strip().replace(' ', '').replace(':', '').replace('.', '').replace(')', '')
    if not s:
        return None
    # Try standard Devanagari digits first
    try:
        n = int(d2a(s))
        return n
    except ValueError:
        pass
    # Try ASCII digits
    try:
        n = int(s)
        if 1 <= n <= 99:
            return n
    except ValueError:
        pass
    # Try corrupted digit mapping (single or double digit)
    if s in CORRUPTED_DEV_DIGITS:
        return CORRUPTED_DEV_DIGITS[s]
    # Try two-character corrupted digits (e.g., ज्ञण् = 10, ज्ञज्ञ = 11)
    if len(s) >= 2:
        ch1 = s[0]
        ch2 = s[-1]  # last char
        d1 = CORRUPTED_DEV_DIGITS.get(ch1)
        d2 = CORRUPTED_DEV_DIGITS.get(ch2)
        if d1 is not None and d2 is not None:
            return d1 * 10 + d2
    return None

# ── OCR fixes (longest-first) ──────────────────────────────────────────────
OCR = [
    ('फाठ्यव्रम', 'पाठ्यक्रम'), ('पाठ्यव्रम', 'पाठ्यक्रम'),
    ('पाठ्ड्डम', 'पाठ्यक्रम'), ('पाठड्डम', 'पाठ्यक्रम'),
    ('फाठ्यक्रम', 'पाठ्यक्रम'), ('फाठ्यव्र', 'पाठ्यक्र'),
    ('पाठ्यपुस्', 'पाठ्यपुस्त'), ('पाठय्', 'पाठ्य'),
    ('सम्वन्ध', 'सम्बन्ध'), ('समवन्ध', 'सम्बन्ध'), ('सवन्ध', 'सम्बन्ध'),
    ('तŒव', 'तत्त्व'), ('तङ्खव', 'तत्त्व'),
    ('mव्रियाकलाप', 'क्रियाकलाप'), ('mव्रि', 'क्रि'), ('mव्र', 'क्र'),
    ('ड्डियाकलाप', 'क्रियाकलाप'), ('mव', 'क'),
    ('वै ज्ञानिक', 'वैज्ञानिक'), ('वज्ञै ानिक', 'वैज्ञानिक'),
    ('भौ तिक', 'भौतिक'), ('प्रया', 'प्रयो'),
    ('र ाष्ट्रिय', 'राष्ट्रिय'), ('रा ष्ट्रिय', 'राष्ट्रिय'),
    ('र ाष्ट्र', 'राष्ट्र'), ('दे ख', 'देख'),
    ('गन र्े', 'गर्ने'), ('गन र्', 'गर्न'),
    ('गरी ी', 'गरी'), ('गरी  गरी', 'गरी'),
    ('हन्ु छ', 'हुन्छ'), ('हुन े', 'हुने'),
    ('गर्न े', 'गर्ने'), ('गर्न े', 'गर्ने'),
    ('बस्', 'बस्तु'), ('वस्', 'वस्तु'),
    ('अनसु न्धान', 'अनुसन्धान'), ('अन्वष्े ाण', 'अन्वेषण'),
    ('पम्र ाण', 'प्रमाण'), ('प्राया', 'प्रयो'),
    ('प्रविधि', 'प्रविधि'), ('विद्युतीय', 'विद्युतीय'),
    ('का े', 'को'), ('का े', 'को'), ('काे', 'को'),
    ('भएका े', 'भएको'), ('भएकाे', 'भएको'),
    ('हाम्रा े', 'हाम्रो'), ('हाम्रा े', 'हाम्रो'),
    ('शार ीरि क', 'शारीरिक'), ('स्वास्', 'स्वास्थ्य'),
    ('स्वस् थ', 'स्वस्थ'), ('स्वस्', 'स्वास्थ्य'),
    ('स्वाभाविक', 'स्वाभाविक'), ('स्वावलम्बी', 'स्वावलम्बी'),
    ('पर्न े', 'पर्ने'), ('पर्न े', 'पर्ने'),
    ('गर्न े', 'गर्ने'), ('हुन े', 'हुने'),
    ('गर्नुहोस ्', 'गर्नुहोस्'), ('गनर्पु छ', 'गर्नुपर्छ'),
    ('गर्न े', 'गर्ने'), ('कन्े द्र', 'केन्द्र'),
    ('कन्े द्र', 'केन्द्र'), ('केन्द्र', 'केन्द्र'),
    ('के न्द्र', 'केन्द्र'), ('क ेन्द्र', 'केन्द्र'),
    ('फाठ्यव्रम', 'पाठ्यक्रम'),
    ('पष्ठृ', 'पृष्ठ'), ('पृष्ठ', 'पृष्ठ'),
    ('सङ्ख्', 'सङ्ख्या'),
    ('प्रथा', 'प्रथा'), ('प्रथम', 'प्रथम'),
    ('संस्क ार', 'संस्कार'), ('दै निक', 'दैनिक'),
    ('गर ाई', 'गराई'), ('सौ न्दर्य', 'सौन्दर्य'),
    ('सिर्जनात्मकता', 'सिर्जनात्मकता'),
    ('चारि त्रिक', 'चारित्रिक'),
    ('रो जगार', 'रोजगार'),
    ('लाके तान्त्रिक', 'लोकतान्त्रिक'),
    ('सिकी ी', 'सिकी'), ('हुने े', 'हुने'),
    ('रह ेक ो', 'रहेको'), ('रह ेको', 'रहेको'),
    ('भएक ो', 'भएको'), ('भएकाे', 'भएको'),
    ('अपे क्ष', 'अपेक्ष'), ('अपेि क्ष', 'अपेक्ष'),
    ('अपक्ष्े ाा', 'अपेक्षा'), ('अपे क्षा', 'अपेक्षा'),
    ('अनुर ोध', 'अनुरोध'), ('स्वीकृति', 'स्वीकृति'),
    ('प्रकाशक', 'प्रकाशक'), ('प्रकाशन', 'प्रकाशन'),
    ('प्रयो ग', 'प्रयोग'), ('प्रयोजन', 'प्रयोजन'),
    ('प्रयो े ग', 'प्रयोग'), ('प्रयागे', 'प्रयोग'),
    ('गर्नुपर्छ', 'गर्नुपर्छ'),
    ('आइे', 'ओइल'), ('आएको', 'आएको'),
    ('फ्रति', 'प्रति'), ('धे र', 'धेरै'),
    ('यसका े', 'यसको'), ('त्यसकाे', 'त्यसको'),
    ('त्यसका े', 'त्यसको'), ('यसकाे', 'यसको'),
    ('छन ्', 'छन्'), ('छन ै', 'छैन'),
    ('हुन ्', 'हुन्'), ('छन् ै', 'छैन'),
    ('अर ू', 'अरू'), ('भए े', 'भए'),
    ('भए े', 'भए'), ('नहनु', 'नहुने'),
    ('नहन ु', 'नहुने'), ('भएका े', 'भएको'),
    ('रह े', 'रहे'), ('रहने', 'रहने'),
    ('हुनेछ', 'हुनेछ'), ('हुन ेछ', 'हुनेछ'),
    ('हाँ ै', 'हौँ'), ('हा े', 'हो'),
    ('हा े', 'हो'), ('छौ  ँ', 'छौँ'),
    ('खा े', 'खो'), ('गछ र्', 'गर्छ'),
    ('गछ  र्', 'गर्छ'), ('गदा र्', 'गर्दा'),
    ('हुन े', 'हुने'), ('भन े', 'भने'),
    ('ले ख', 'लेख'), ('लेख्न', 'लेख्न'),
    ('ले ख्न', 'लेख्न'), ('दे ख्न', 'देख्न'),
    ('दे खे', 'देखे'), ('चाहन्छौ  ँ', 'चाहन्छौँ'),
    ('गन  र्े', 'गर्ने'), ('गन र्', 'गर्न'),
    ('गर ी', 'गरी'), ('गरी े', 'गरी'),
    ('गने र्', 'गर्ने'),
    ('र े', 'रे'), ('र्े', 'रे'),
    ('र्', 'र'), ('ल', 'ल'),
    ('पछि', 'पछि'), ('दे खाउन', 'देखाउन'),
    ('पुर ै', 'पूरै'), ('पुर ै', 'पूरै'),
    ('पर्छ', 'पर्छ'), ('हुन े', 'हुने'),
    ('सबै े', 'सबै'), ('सब ै', 'सबै'),
    ('सबैभन्दा', 'सबैभन्दा'),
    ('\u200b', ''), ('\u200c', ''), ('\u200d', ''), ('\u2060', ''),
    ('\u00a0', ' '),
]
OCR.sort(key=lambda x: -len(x[0]))

# ── Reversed English words (PDF extraction) ─────────────────────────────────
REV = {
    'egaP': 'Page', 'elbaT': 'Table', 'stnetnoC': 'Contents', 'fo': 'of',
    'krow': 'work', 'tcejorP': 'Project', 'noitseuQ': 'Question',
    'gnitirW': 'Writing', 'gnidaeR': 'Reading', 'gninetsiL': 'Listening',
    'gnikaepS': 'Speaking', 'yranoitciD': 'Dictionary',
    'senohpomoH': 'Homophones', 'noitautcnuP': 'Punctuation',
    'noitasilatipaC': 'Capitalisation', 'noitazilaicepS': 'Specialisation',
    'yrots': 'story', 'hpargaraP': 'Paragraph', 'egasseM': 'Message',
    'yassE': 'Essay', 'snoitseggus': 'suggestions',
    'eugolaid': 'dialogue', 'skram': 'marks',
    'noititepmoc': 'competition', 'dluow': 'would',
    'lliW': 'Will', 'nac': 'can', 'snwonk': 'knows',
    'evah': 'have', 'ekil': 'like', 'ot': 'to', 'erom': 'more',
    'esuaceb': 'because', 'lufituaeb': 'beautiful',
    'sdrawkcab': 'backwards', 'sepyt': 'types',
    'lavitsef': 'festival', 'tsil': 'list', 'morf': 'from',
    'seug': 'guess', 'ecitcarp': 'practice',
    'tib': 'bit', 'txE': 'Ext', 'noisiceD': 'Decision',
    'lanoitidnoc': 'conditional', 'sevitcennoC': 'Connective',
    'snoitanogidA': 'Addition', 'noitacilppA': 'Application',
    'evitageN': 'Negative', 'tnedets': 'student',
    'eliforp': 'profile', 'yalp': 'play', 'draob': 'board',
    'raey': 'year', 'erutcip': 'picture', 'drac': 'card',
    'pleh': 'help', 'kcehC': 'Check', 'laer': 'real',
    'yrtne': 'entry', 'tibah': 'habit', 'tsap': 'past',
    'tseuqeR': 'Request', 'sdeeN': 'Needs', 'gniteerG': 'Greeting',
    'stnaw': 'wants', 'retteL': 'Letter', 'eciton': 'notice',
    'selur': 'rules', 'moorssalC': 'Classroom',
    'snruter': 'returns', 'gnirahS': 'Sharing',
    'noitacifitnedi': 'identification',
    'noitangisnoc': 'consignation', 'noitalupinam': 'manipulation',
    'noitcaer': 'reaction', 'noitazinagrO': 'Organisation',
    'sgnihtyreve': 'everything', 'doolb': 'blood',
    'skoob': 'books', 'seviecer': 'receives',
    'yfilanoitanretni': 'internationality',
    'noitativnI': 'Invitation', 'noitangiseD': 'Designation',
    'noitaton': 'notation', 'ecnedifnoc': 'confidence',
    'noitadnemmoc': 'commendation', 'ecneuqesnoc': 'consequence',
    'ecnatsid': 'distance', 'ecnaraelc': 'clearance',
    'ecnalab': 'balance', 'senisub': 'business',
    'seinap': 'panies', 'seirtne': 'entries',
    'snoitome': 'emotions', 'snoitaulave': 'evaluation',
    'snoitseuq': 'questions', 'snoitidda': 'additions',
    'noitaropavnI': 'Innovation',
}

def fix_rev(text):
    # Use word boundaries for short patterns to avoid corrupting normal words
    for r, c in REV.items():
        if len(r) <= 4:
            text = re.sub(r'\b' + re.escape(r) + r'\b', c, text)
        else:
            text = text.replace(r, c)
    return text


def is_noise(s):
    s = s.strip()
    if not s or len(s) < 2:
        return True
    if re.match(r'^[\s\.\,\>\~\;\:\!\-\(\)\|\[\]\=\+\#\@\©\&\d<>=/\\\'\"\u0964\u0965\(\)]+$', s):
        return True
    if re.match(r'^[A-Za-z]{1,3}$', s) and s.lower() not in {'a','i','an','is','it','in','on','at','to',
        'be','by','my','we','he','she','no','go','ok','or','as','up','us','am','do','so','if','me','of'}:
        return True
    if re.match(r'^\d{1,4}$', s):
        return True
    if re.match(r'^https?://\S+$', s):
        return True
    if re.match(r'^[\s\(\)\[\]]*[्रढघडठञ]+[\s\(\)\[\]]*$', s):
        return True
    if re.match(r'^[\s\(\)]*\({2,}[\s\(\)]*$', s):
        return True
    if re.match(r'^[द्धद्दद्धज्ञञढघठटड]+.*(?:कक्षा|Grade|Class)\s+\d+', s):
        return True
    # Line is just table border chars or book title repeats
    if re.match(r'^[\s\|]*-{3,}[\s\|]*$', s):
        return True
    # "My English Book: Grade X" headers
    if re.match(r'^[A-Z][a-z]+ (?:English|Nepali|Maths?) (?:Book|Textbook)[:\s]*Grade', s):
        return True
    # Nepali book header "मेरो नेपाली, कक्षा १ घ" etc with OCR corruption page markers
    if re.match(r'^[^\s]{1,4}\s*(?:कक्षा|Grade)', s) and 'कक्षा' in s:
        return True
    return False


def apply_ocr(s):
    for w, c in OCR:
        s = s.replace(w, c)
    return s


def has_dev(text, thresh=0.03):
    d = sum(1 for c in text if '\u0900' <= c <= '\u097F')
    n = sum(1 for c in text if not c.isspace())
    return n > 0 and d / n >= thresh


def detect_language(lines):
    txt = '\n'.join(lines)
    return has_dev(txt)


def get_subject(fname):
    n = fname.replace('.md', '')
    n = re.sub(r'^Class\s+\d+\s*', '', n)
    n = re.sub(r'\s+\d{4}$', '', n)
    n = re.sub(r'\s*\(.*?\)\s*$', '', n)
    return n.strip() or 'Textbook'


def get_class(dirname):
    m = re.search(r'\d+', dirname)
    return int(m.group()) if m else 0


# ── OCR-corrupted chapter marker mapping ─────────────────────────────────────
# Many Nepali books have OCRs that replace पाठ with various garbage
OCR_CHAPTER_MARKERS = {
    'Wd': 'पाठ', 'Id': 'पाठ', 'Ud': 'पाठ',
    'TOA': 'पाठ', 'षाठ': 'पाठ', 'था': 'पाठ',
    'Td': 'पाठ', 'Td': 'पाठ',
}
# Lines that indicate chapter structure in TOC for Nepali books
DEV_UNIT_WORDS = ['एकाइ', 'एकाई', 'इकाइ']
DEV_LESSON_WORDS = ['पाठ', 'पाट']


def clean_toc_title(title):
    title = title.replace('्र', '').strip()
    # Remove trailing known page-marker tokens
    title = re.sub(r'\s+[०१२३४५६७८९\d]{1,6}\s*$', '', title).strip()
    for old, new in OCR:
        title = title.replace(old, new)
    title = re.sub(r'\s+', ' ', title).strip()
    return title


def extract_toc_titles(lines, is_nepali):
    toc_entries = []
    toc_end_line = 0
    in_toc = False
    toc_headers_np = ['विषयसूची', 'विषयसूची', 'वषियसूची', 'वषयसूची', 'सामग्री', 'अनुक्रमणिका']
    toc_headers_en = ['table of contents', 'contents', 'index']
    non_match_count = 0
    last_match_line = 0

    for i in range(min(len(lines), int(len(lines)*0.2))):
        s_orig = lines[i].strip()
        s_flat = s_orig.lower().replace(' ', '').replace('्र', '')
        if not in_toc:
            if is_nepali:
                if any(h.replace(' ', '') in s_flat for h in toc_headers_np):
                    in_toc = True
            else:
                if any(h in s_flat for h in toc_headers_en):
                    in_toc = True
            continue

        if not s_orig or re.match(r'^[\s्र\(\)]+$', s_orig):
            continue

        matched = False
        if is_nepali:
            # Strip leading ्र-like characters
            s_clean = re.sub(r'^[\s्र\(\)]+', '', s_orig)
            # Try number + dot format first: "१. Title" (no ्र delimiters)
            m = re.match(r'^([०१२३४५६७८९\d]{1,2})[\.\)]\s+(.+)', s_clean)
            if not m:
                # Try split on ्र delimiter: "्र N ्र Title ्र" or "्र पाठ N ्र Title ्र"
                parts = [p.strip() for p in s_orig.split('्र') if p.strip()]
                if len(parts) >= 2:
                    first = parts[0]
                    # Try to find a number in the first part (may be corrupted)
                    num = None
                    # Try matching "पाठ : N" or "पाठ N :" or just "N"
                    # Use \S+ to capture any non-whitespace after optional पाठ prefix
                    # (since \w inside [...] is ASCII-only in Python)
                    num_m = re.match(r'(?:पाठ\s*)?:?\s*(\S+?)\s*:?', first)
                    if num_m:
                        num = parse_corrupted_num(num_m.group(1))
                    if num is None:
                        # Try matching "N. Title" format in first part
                        num_m2 = re.match(r'(\S+?)[\.\)]', first)
                        if num_m2:
                            num = parse_corrupted_num(num_m2.group(1))
                    if num is not None and 1 <= num <= 60:
                        # Helper: check if a string looks like a page number (corrupted Devanagari digits)
                        def is_page_num(s):
                            # Pure Devanagari corrupted digit characters
                            page_chars = set('ज्ञद्दद्धघद्धछटठडढण्')
                            s_clean = s.replace(' ', '').replace('-', '')
                            return all(c in page_chars for c in s_clean if c.isalpha()) and len(s_clean) <= 4
                        # Title is typically parts[1] (second column in table)
                        title_candidate = None
                        if len(parts) >= 2:
                            p = parts[1]
                            if len(p) > 2 and not is_noise(p) and not is_page_num(p):
                                title_candidate = p
                        # If no title, look backward then forward
                        if not title_candidate:
                            for direction in [-1, 1]:
                                for step in range(1, 4):
                                    ni = i + step * direction
                                    if ni < 0 or ni >= len(lines):
                                        break
                                    ns = lines[ni].strip()
                                    if not ns or re.match(r'^[\s्र\(\)]+$', ns):
                                        continue
                                    nparts = [q.strip() for q in ns.split('्र') if q.strip()]
                                    if len(nparts) >= 2:
                                        np = nparts[1]
                                        if len(np) > 2 and not is_noise(np) and not is_page_num(np):
                                            title_candidate = np
                                            break
                                    if title_candidate:
                                        break
                                if title_candidate:
                                    break
                        if title_candidate:
                            title = clean_toc_title(title_candidate)
                            if len(title) > 2:
                                toc_entries.append((num, title))
                                matched = True
            else:
                num = int(d2a(m.group(1)))
                title = clean_toc_title(m.group(2))
                if 1 <= num <= 60 and len(title) > 2:
                    toc_entries.append((num, title))
                    matched = True
        else:
            m = re.match(r'^[\s\W]*(\d{1,2})[\.\)]\s*(.{0,80}?)(?:\s+\d+\s*)?$', s_orig)
            if m:
                title = fix_rev(m.group(2).strip().rstrip('.'))
                if len(title) > 2:
                    num = int(m.group(1))
                    toc_entries.append((num, title))
                    matched = True

        if matched:
            non_match_count = 0
            last_match_line = i
        elif toc_entries:
            non_match_count += 1
            if non_match_count > 5:
                toc_end_line = last_match_line
                break
    if not toc_end_line and toc_entries:
        toc_end_line = last_match_line
    return toc_entries, toc_end_line


def _lookup_title(lines, i, max_look=3):
    """Look for a chapter title before or after line i (non-exercise, non-noise)."""
    # Try previous non-empty lines first
    for j in range(1, max_look + 1):
        if i - j < 0:
            break
        ps = lines[i - j].strip()
        if ps and len(ps) > 3 and not is_noise(ps):
            if not re.match(r'^[\s\d]*[\.\)]', ps) and 'सुनाइ' not in ps and 'पूर्व' not in ps:
                return ps[:80]
    # Then try next lines
    for j in range(1, max_look + 1):
        if i + j >= len(lines):
            break
        ns = lines[i + j].strip()
        if ns and len(ns) > 3 and not is_noise(ns):
            if not re.match(r'^[\s\d]*[\.\)]', ns) and 'सुनाइ' not in ns and 'पूर्व' not in ns:
                return ns[:80]
    return ''


def detect_chapters(lines, is_nepali):
    """Multi-strategy chapter detection."""

    # Strategy 1: Clean explicit markers
    if is_nepali:
        nep_pats = [
            (re.compile(r'^[\s्र]*(?:पाठ|पाट)(?!्य)\s*([०१२३४५६७८९\d]+)\s*[:\.\)\-]?\s*(.*?)$'), 1, 2),
            (re.compile(r'^[\s्र]*(एकाइ|एकाई|इकाइ)\s*[—\-]?\s*([०१२३४५६७८९\d]{1,2})\s*[:\.\)\-]?\s*(.*?)$'), 2, 3),
            (re.compile(r'^[\s्र]*([०१२३४५६७८९]{1,2})[\.\)]\s+(\S.{0,60})$'), 1, 2),
        ]
        for pat, ng, tg in nep_pats:
            matches = []
            for i, line in enumerate(lines):
                s = line.strip()
                m = pat.match(s)
                if not m:
                    continue
                num_raw = m.group(ng)
                title = m.group(tg).strip() if m.lastindex >= tg else ''
                if not num_raw:
                    continue
                num = int(d2a(num_raw))
                if not (1 <= num <= 80 and i > 3):
                    continue
                # Filter false positives
                if 'सुनाइ' in s or 'पूर्व' in s:
                    continue
                # Title lookup (same-line or previous/next)
                if not title or len(title) < 4:
                    title = _lookup_title(lines, i)
                if not title or len(title) < 4:
                    continue
                # Also filter if title looks like an exercise
                if re.match(r'^[०१२३४५६७८९\d]+[\.\)]', title):
                    continue
                matches.append((i, title, num))
            if 2 <= len(matches) <= 100:
                min_line = max(int(len(lines) * 0.06), 30)
                content = [m for m in matches if m[0] >= min_line]
                if len(content) >= 2:
                    # Deduplicate by chapter number
                    seen = {}
                    for m in content:
                        if m[2] not in seen:
                            seen[m[2]] = m
                    deduped = sorted(seen.values(), key=lambda x: x[0])
                    if len(deduped) >= 2:
                        return deduped
    else:
        eng_pats = [
            (re.compile(r'^(?:Unit|UNIT|unit)\s+(\d+)\s*[:\-\.\)]?\s*(.{0,80})$'), 1, 2),
            (re.compile(r'^(?:Lesson|LESSON|lesson)\s+(\d+)\s*[:\-\.\)]?\s*(.{0,80})$'), 1, 2),
            (re.compile(r'^(?:Chapter|CHAPTER|chapter)\s+(\d+)\s*[:\-\.\)]?\s*(.{0,80})$'), 1, 2),
            (re.compile(r'^(\d+)[\.\)]\s+([A-Z].{0,80})$'), 1, 2),
        ]
        for pat, ng, tg in eng_pats:
            matches = []
            for i, line in enumerate(lines):
                s = line.strip()
                m = pat.match(s)
                if not m:
                    continue
                num_raw = m.group(ng)
                title = m.group(tg).strip() if m.lastindex >= tg else ''
                if not num_raw:
                    continue
                num = int(num_raw)
                if not (1 <= num <= 80 and i > 3):
                    continue
                # Title lookup (same-line or next)
                if not title or len(title) < 4:
                    for j in range(1, 4):
                        if i + j >= len(lines):
                            break
                        ns = lines[i + j].strip()
                        if ns and not is_noise(ns) and len(ns) > 3:
                            title = ns
                            break
                if not title or len(title) < 4:
                    continue
                # Filter out exercise/dialogue items
                if re.match(r'^[A-E]\)', title) or title.startswith('A:'):
                    continue
                if '…' in title:
                    continue
                matches.append((i, title, num))
            if 2 <= len(matches) <= 100:
                min_line = max(int(len(lines) * 0.06), 30)
                content = [m for m in matches if m[0] >= min_line]
                if len(content) >= 2:
                    seen = {}
                    for m in content:
                        if m[2] not in seen:
                            seen[m[2]] = m
                    deduped = sorted(seen.values(), key=lambda x: x[0])
                    if len(deduped) >= 2:
                        return deduped

    # Strategy 2: OCR-corrupted Nepali markers (Wd १, Id ११, etc.)
    if is_nepali:
        all_markers = []
        for i, line in enumerate(lines):
            s = line.strip()
            if i < 5:
                continue
            if not s or is_noise(s):
                continue
            for ocr_m, correct in OCR_CHAPTER_MARKERS.items():
                m = re.match(
                    r'^[\s\(\)]*' + re.escape(ocr_m) +
                    r'\s*([०१२३४५६७८९\d\w©&]+)\s*$', s
                )
                if m:
                    all_markers.append((i, f'{correct}', 0))
                    break
        for i, line in enumerate(lines):
            s = line.strip()
            if i < 5:
                continue
            if re.match(r'^[\s\(\)]*TOA\s*$', s):
                all_markers.append((i, 'पाठ', 0))
            elif re.match(r'^[\s\(\)]*मुल\s+पाठ\s*$', s):
                all_markers.append((i, 'मुल पाठ', 0))

        if 2 <= len(all_markers) <= 100:
            all_markers.sort(key=lambda x: x[0])
            deduped = [all_markers[0]]
            for m in all_markers[1:]:
                if m[0] - deduped[-1][0] > 3:
                    deduped.append(m)
            deduped = [(i, t, idx+1) for idx, (i, t, _) in enumerate(deduped)]
            return deduped

    # Strategy 3: "था Title" pattern
    if is_nepali:
        special_matches = []
        for i, line in enumerate(lines):
            s = line.strip()
            m = re.match(r'^[\s्र]*था\s+(\S.+)', s)
            if m and i > 3:
                special_matches.append((i, m.group(1).strip(), None))
        if len(special_matches) >= 2:
            return special_matches

    # Strategy 4: Lone number + next line title (Arabic numerals)
    matches = []
    for i in range(len(lines) - 1):
        s = lines[i].strip()
        if re.match(r'^\d{1,2}$', s) and i > 3:
            num = int(s)
            if 1 <= num <= 60:
                ns = lines[i + 1].strip()
                if ns and len(ns) > 5 and not is_noise(ns) and ns[0].isupper():
                    matches.append((i, ns, num))
    if 2 <= len(matches) <= 50:
        return matches

    # LAST RESORT: Use TOC to determine chapter count, even-split content
    toc_entries, toc_end = extract_toc_titles(lines, is_nepali)
    if len(toc_entries) >= 2:
        total = len(toc_entries)
        start = max(toc_end + 1, 1)
        for j in range(start, len(lines)):
            l = lines[j].strip()
            if l and len(l) > 10 and not is_noise(l):
                start = j
                break
        if start < len(lines):
            content_len = len(lines) - start
            section = content_len // total
            if section > 20:
                return [(start + n * section, toc_entries[n][1] if n < len(toc_entries) else '', n + 1) for n in range(total)]


    return []


def extract_metadata(lines, is_nepali, class_num, subject):
    meta = {
        'subject': subject, 'grade': class_num,
        'language': 'nepali' if is_nepali else 'english',
        'publisher': '', 'location': '', 'edition': '', 'isbn': '',
    }
    first = '\n'.join(lines[:60])
    if is_nepali:
        if 'नेपाल सरकार' in first:
            meta['publisher'] = 'नेपाल सरकार, शिक्षा, विज्ञान तथा प्रविधि मन्त्रालय, पाठ्यक्रम विकास केन्द्र'
        if 'सानोठिमी' in first:
            meta['location'] = 'सानोठिमी, भक्तपुर'
        m = re.search(r'(?:पहिलो|प्रथम)\s*(?:संस्करण|संकरण)\s*:.*?(\d{4})', first)
        if m:
            meta['edition'] = m.group(1)
    else:
        if 'Government of Nepal' in first:
            meta['publisher'] = 'Government of Nepal, Ministry of Education, Science and Technology, Curriculum Development Centre'
        if 'Sanothimi' in first:
            meta['location'] = 'Sanothimi, Bhaktapur'
        m = re.search(r'ISBN[\s:]*([\d\-X]+)', first)
        if m:
            meta['isbn'] = m.group(1)
        m = re.search(r'(?:Edition|edition)[:\s]*(\d+\s*(?:AD|BS)?)', first)
        if m:
            meta['edition'] = m.group(1)
    return meta


def extract_content(lines, start, end):
    content = []
    for li in range(start, end):
        s = lines[li].strip()
        if not s or is_noise(s):
            continue
        c = apply_ocr(s)
        c = re.sub(r' {3,}', ' ', c)
        # Clean up remaining table artifacts
        c = re.sub(r'^[\s्र\(\)\[\]]+', '', c)
        c = re.sub(r'[\s्र\(\)\[\]]+$', '', c)
        if c:
            content.append(c)
    return content


def format_book(filepath):
    print(f'  {filepath.relative_to(BASE)}')
    raw = filepath.read_text(encoding='utf-8')
    raw_len = len(raw)
    raw_lines = raw.split('\n')

    # Fix reversed text in English books
    fixed_lines = [fix_rev(l) for l in raw_lines]

    is_nepali = detect_language(fixed_lines)
    fn = filepath.name
    subject = get_subject(fn)
    class_num = get_class(filepath.parent.name)

    meta = extract_metadata(fixed_lines, is_nepali, class_num, subject)

    chapters = detect_chapters(fixed_lines, is_nepali)
    if chapters and chapters[0][2] is None:
        # Special markers with unknown numbers - assign sequentially
        chapters = [(i, t, idx+1) for idx, (i, t, _) in enumerate(chapters)]

    out = []

    # Frontmatter
    out.append('---')
    out.append(f'title: "{meta["subject"]}"')
    out.append(f'grade: {meta["grade"]}')
    out.append(f'language: {meta["language"]}')
    out.append(f'subject: "{meta["subject"]}"')
    if meta['publisher']:
        out.append(f'publisher: "{meta["publisher"]}"')
    if meta.get('location'):
        out.append(f'location: "{meta["location"]}"')
    if meta.get('edition'):
        out.append(f'edition: "{meta["edition"]}"')
    if meta.get('isbn'):
        out.append(f'isbn: "{meta["isbn"]}"')
    out.append('---')
    out.append('')

    # H1
    if is_nepali:
        out.append(f'# {subject} — कक्षा {a2d(str(class_num))}')
    else:
        out.append(f'# {subject} — Grade {class_num}')
    out.append('')

    # Publisher
    if meta['publisher']:
        if is_nepali:
            out.append(f'> **प्रकाशक:** {meta["publisher"]}')
            if meta.get('location'):
                out.append(f'> **स्थान:** {meta["location"]}')
        else:
            out.append(f'> **Publisher:** {meta["publisher"]}')
            if meta.get('location'):
                out.append(f'> **Location:** {meta["location"]}')
        out.append('')

    if chapters:
        # Remove duplicates (keep first occurrence of each chapter number)
        seen_nums = set()
        unique_chapters = []
        for idx, (line_i, title, num) in enumerate(chapters):
            if num not in seen_nums:
                seen_nums.add(num)
                unique_chapters.append((line_i, title, num))
        chapters = unique_chapters

        # Sort by line position
        chapters.sort(key=lambda x: x[0])

        # TOC
        if is_nepali:
            out.append('## विषयसूची\n')
            out.append('| क्र.स. | शीर्षक |')
            out.append('|--------|--------|')
        else:
            out.append('## Table of Contents\n')
            out.append('| S.No. | Title |')
            out.append('|-------|-------|')

        for line_i, title, num in chapters:
            anchor = f'ch-{num}'
            if is_nepali:
                dn = a2d(str(num))
                dt = title if title else f'पाठ {dn}'
                out.append(f'| {dn} | [{dt}](#{anchor}) |')
            else:
                dt = title if title else f'Unit {num}'
                out.append(f'| {num} | [{dt}](#{anchor}) |')
        out.append('')
        out.append('---\n')

        # Chapter content
        for ci, (line_i, title, num) in enumerate(chapters):
            end_i = chapters[ci + 1][0] if ci + 1 < len(chapters) else len(fixed_lines)
            anchor = f'ch-{num}'

            if is_nepali:
                dn = a2d(str(num))
                dt = title if title else f'पाठ {dn}'
                out.append(f'## {dn}: {dt}  {{#{anchor}}}')
            else:
                dt = title if title else f'Unit {num}'
                out.append(f'## {num}: {dt}  {{#{anchor}}}')
            out.append('')

            content = extract_content(fixed_lines, line_i + 1, end_i)
            if content:
                out.extend(content)
            out.append('')

        ch_count = len(chapters)
    else:
        ch_count = 0
        if is_nepali:
            out.append('## विषयवस्तु\n')
        else:
            out.append('## Content\n')

        # Clean all lines, skip preface
        cleaned = []
        for line in fixed_lines:
            s = line.strip()
            if not s or is_noise(s):
                continue
            s = apply_ocr(s)
            s = re.sub(r' {3,}', ' ', s)
            s = re.sub(r'^[\s्र\(\)\[\]]+', '', s)
            s = re.sub(r'[\s्र\(\)\[\]]+$', '', s)
            if s:
                cleaned.append(s)

        # Find content start (skip preface/TOC)
        skip = 0
        for idx, line in enumerate(cleaned):
            lower = line.lower()
            if is_nepali and ('हाम्रो भनाइ' in line or 'हाम्रा े भनाइ' in line):
                skip = idx + 3
            elif not is_nepali and ('preface' in lower):
                skip = idx + 3

        remaining = cleaned[skip:] if skip and skip < len(cleaned) else cleaned[len(cleaned)//3:]
        if remaining:
            out.extend(remaining)

    result = '\n'.join(out)
    result = re.sub(r'\n{4,}', '\n\n\n', result)
    result = result.strip() + '\n'

    reduction = raw_len - len(result)
    print(f'    {raw_len} -> {len(result)} chars, {ch_count} ch, -{reduction} chars ({100*ch_count//max(1,(ch_count or 1)) if ch_count else 0}%)')

    if not DRY_RUN:
        filepath.write_text(result, encoding='utf-8')

    return ch_count


def main():
    if SINGLE_FILE:
        if not SINGLE_FILE.exists():
            print(f'Error: {SINGLE_FILE} not found')
            sys.exit(1)
        format_book(SINGLE_FILE)
        return

    total_files = 0
    total_ch = 0
    ch_books = 0
    no_ch_books = 0

    for cls_dir in sorted(BASE.glob('Class *')):
        if not cls_dir.is_dir() or not re.match(r'^Class \d+$', cls_dir.name):
            continue
        mds = sorted(cls_dir.glob('*.md'))
        if not mds:
            continue

        print(f'\n{"="*60}')
        print(f'{cls_dir.name} ({len(mds)} files)')
        print(f'{"="*60}')

        for md in mds:
            try:
                nc = format_book(md)
                total_files += 1
                total_ch += nc
                if nc > 0:
                    ch_books += 1
                else:
                    no_ch_books += 1
            except Exception as e:
                print(f'    ERROR: {e}')
                import traceback
                traceback.print_exc()

    print(f'\n{"="*60}')
    print(f'Books with chapters: {ch_books}, without: {no_ch_books}')
    print(f'Total: {total_files} files, {total_ch} chapters')
    print(f'DRY RUN' if DRY_RUN else 'DONE')
    print(f'{"="*60}')


if __name__ == '__main__':
    main()
