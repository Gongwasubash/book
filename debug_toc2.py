import sys; sys.path.insert(0, '.')
import re
import format_books as fb
from pathlib import Path

base = fb.BASE
f = base / 'Class 5/Class 5 Mathematics (Nepali).md'
text = f.read_text(encoding='utf-8')
lines = text.split('\n')
is_nep = fb.detect_language(lines)

def is_page_num(s):
    page_chars = set('ज्ञद्दद्धघद्धछटठडढण्')
    s_clean = s.replace(' ', '').replace('-', '')
    return all(c in page_chars for c in s_clean if c.isalpha()) and len(s_clean) <= 4

# Manually test TOC parsing for lines 63-80
for i in range(60, 85):
    s_orig = lines[i].strip()
    if not s_orig:
        continue
    print(f'L{i}: [{s_orig[:80]}]')
    
    s_clean = re.sub(r'^[\s्र\(\)]+', '', s_orig)
    parts = [p.strip() for p in s_orig.split('्र') if p.strip()]
    if len(parts) >= 2:
        first = parts[0]
        num_m = re.match(r'(?:पाठ\s*)?:?\s*([०१२३४५६७८९\w]+)\s*:?', first)
        if num_m:
            num_raw = num_m.group(1)
            num = fb.parse_corrupted_num(num_raw)
            print(f'  first=[{first}], num_raw=[{num_raw}], num={num}')
            
            if num is not None and 1 <= num <= 60:
                title_candidate = None
                p = parts[1]
                print(f'  checking parts[1]=[{p}] (len={len(p)}, noise={fb.is_noise(p)}, page={is_page_num(p)})')
                if len(p) > 2 and not fb.is_noise(p) and not is_page_num(p):
                    title_candidate = p
                    print(f'  TITLE: [{title_candidate}]')
                else:
                    print(f'  parts[1] rejected')
        else:
            print(f'  first=[{first}], NO MATCH')
    print()
