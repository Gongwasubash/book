import sys; sys.path.insert(0, '.')
import re
import format_books as fb

lines = ['वषियसूची', '्र पाठ १ ्र समाज र समुदाय ्र २ ्र']
is_nep = True

# Copy of extract_toc_titles WITH debug
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
    print(f'L{i}: s_flat={s_flat!r}')
    if not in_toc:
        if is_nep:
            found = False
            for h in toc_headers_np:
                h_clean = h.replace(' ', '')
                if h_clean in s_flat:
                    print(f'  MATCH header: {h!r}')
                    in_toc = True
                    found = True
                    break
            if not found:
                print(f'  NO header match; headers={[h.replace(" ","") for h in toc_headers_np]}')
        else:
            if any(h in s_flat for h in toc_headers_en):
                in_toc = True
        continue

    if not s_orig or re.match(r'^[\s्र\(\)]+$', s_orig):
        print(f'  SKIP (empty/noise)')
        continue

    matched = False
    print(f'  PROCESSING...')
    
    if is_nep:
        s_clean = re.sub(r'^[\s्र\(\)]+', '', s_orig)
        print(f'  s_clean={s_clean!r}')
        
        m = re.match(r'^([०१२३४५६७८९\d]{1,2})[\.\)]\s+(.+)', s_clean)
        if not m:
            print(f'  number+dot: NO')
            parts = [p.strip() for p in s_orig.split('्र') if p.strip()]
            print(f'  parts={parts}')
            
            if len(parts) >= 2:
                first = parts[0]
                print(f'  first={first!r}')
                
                num = None
                num_m = re.match(r'(?:पाठ\s*)?:?\s*(\S+?)\s*:?', first)
                if num_m:
                    g1 = num_m.group(1)
                    print(f'  num_m g1={g1!r}')
                    num = fb.parse_corrupted_num(g1)
                    print(f'  num={num}')
                else:
                    print(f'  num_m NO MATCH')
                
                if num is None:
                    num_m2 = re.match(r'(\S+?)[\.\)]', first)
                    if num_m2:
                        g1 = num_m2.group(1)
                        print(f'  num_m2 g1={g1!r}')
                        num = fb.parse_corrupted_num(g1)
                        print(f'  num2={num}')
                
                if num is not None and 1 <= num <= 60:
                    print(f'  num IN RANGE: {num}')
                    
                    def is_page_num(s):
                        page_chars = set('ज्ञद्दद्धघद्धछटठडढण्')
                        s_clean = s.replace(' ', '').replace('-', '')
                        return all(c in page_chars for c in s_clean if c.isalpha()) and len(s_clean) <= 4
                    
                    title_candidate = None
                    if len(parts) >= 2:
                        p = parts[1]
                        print(f'  parts[1]={p!r}')
                        print(f'    len>2: {len(p)>2}')
                        print(f'    is_noise: {fb.is_noise(p)}')
                        print(f'    is_page_num: {is_page_num(p)}')
                        if len(p) > 2 and not fb.is_noise(p) and not is_page_num(p):
                            title_candidate = p
                            print(f'  title_candidate={p!r}')
                    
                    if title_candidate:
                        title = fb.clean_toc_title(title_candidate)
                        print(f'  cleaned={title!r} len={len(title)}')
                        if len(title) > 2:
                            print(f'  APPENDING: [{num}] {title}')
                            toc_entries.append((num, title))
                            matched = True
        else:
            print(f'  number+dot: YES g1={m.group(1)!r} g2={m.group(2)!r}')
            num = int(fb.d2a(m.group(1)))
            title = fb.clean_toc_title(m.group(2))
            if 1 <= num <= 60 and len(title) > 2:
                toc_entries.append((num, title))
                matched = True
    else:
        m = re.match(r'^[\s\W]*(\d{1,2})[\.\)]\s*(.{0,80}?)(?:\s+\d+\s*)?$', s_orig)
        if m:
            title = fb.fix_rev(m.group(2).strip().rstrip('.'))
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

print(f'\nFINAL: {len(toc_entries)} entries')
for num, title in toc_entries:
    print(f'  [{num}] {title}')
