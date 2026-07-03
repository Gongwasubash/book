import sys; sys.path.insert(0, '.')
import re
import format_books as fb
from pathlib import Path

base = fb.BASE

# Test Class 6 Social Studies line by line
fp = 'Class 6/Class 6 Social Studies.md'
f = base / fp
text = f.read_text(encoding='utf-8')
lines = text.split('\n')
is_nep = fb.detect_language(lines)

# Simulate the beginning of extract_toc_titles with debug
toc_headers_np = ['विषयसूची', 'विषयसूची', 'वषियसूची', 'वषयसूची', 'सामग्री', 'अनुक्रमणिका']
in_toc = False
non_match_count = 0
last_match_line = 0
toc_entries = []

for i in range(min(len(lines), int(len(lines)*0.2))):
    s_orig = lines[i].strip()
    s_flat = s_orig.lower().replace(' ', '').replace('्र', '')
    if not in_toc:
        if is_nep:
            if any(h.replace(' ', '') in s_flat for h in toc_headers_np):
                print(f'L{i}: ENTERED TOC mode via [{s_orig[:60]}]')
                in_toc = True
        continue
    
    if i > 150 and i < 200:
        continue  # Skip body text
    
    if not s_orig or re.match(r'^[\s्र\(\)]+$', s_orig):
        continue
    
    matched = False
    
    # Try split on ्र
    parts = [p.strip() for p in s_orig.split('्र') if p.strip()]
    if len(parts) >= 2:
        first = parts[0]
        if 'पाठ' in first or 'एकाइ' in first or 'इकाइ' in first:
            num_m = re.match(r'(?:पाठ\s*)?:?\s*(\S+?)\s*:?', first)
            num = None
            if num_m:
                num = fb.parse_corrupted_num(num_m.group(1))
            if num is None:
                num_m2 = re.match(r'(\S+?)[\.\)]', first)
                if num_m2:
                    num = fb.parse_corrupted_num(num_m2.group(1))
            
            if num is not None and 1 <= num <= 60:
                title_candidate = None
                if len(parts) >= 2:
                    p = parts[1]
                    def is_page_num(s):
                        page_chars = set('ज्ञद्दद्धघद्धछटठडढण्')
                        s_clean = s.replace(' ', '').replace('-', '')
                        return all(c in page_chars for c in s_clean if c.isalpha()) and len(s_clean) <= 4
                    
                    if len(p) > 2 and not fb.is_noise(p) and not is_page_num(p):
                        title_candidate = p
                
                if title_candidate:
                    toc_entries.append((num, title_candidate[:50]))
                    matched = True
                    print(f'  L{i}: MATCH [{num}] {title_candidate[:50]}')
    
    if matched:
        non_match_count = 0
        last_match_line = i
    elif toc_entries:
        non_match_count += 1
        if non_match_count > 5:
            print(f'  L{i}: BREAK at non_match_count=5 (last_match={last_match_line})')
            break

print(f'\nTotal entries found: {len(toc_entries)}')
