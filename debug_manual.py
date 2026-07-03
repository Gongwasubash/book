import sys; sys.path.insert(0, '.')
import format_books as fb
import re

# Directly test: enter TOC mode, then try to match a line
lines = ['वषियसूची', '्र पाठ १ ्र समाज र समुदाय ्र २ ्र']
is_nep = True

# Trace through the function
toc_headers_np = ['विषयसूची', 'विषयसूची', 'वषियसूची', 'वषयसूची', 'सामग्री', 'अनुक्रमणिका']
in_toc = False

for i in range(min(len(lines), int(len(lines)*0.2))):
    s_orig = lines[i].strip()
    s_flat = s_orig.lower().replace(' ', '').replace('्र', '')
    print(f'L{i}: s_orig={s_orig!r}')
    
    if not in_toc:
        for h in toc_headers_np:
            h_clean = h.replace(' ', '')
            if h_clean in s_flat:
                print(f'  -> MATCHED header {h!r}')
                in_toc = True
                break
        if in_toc:
            continue
        print('  -> no header match')
        continue
    
    print(f'  -> in_toc=True, processing...')
    
    # Line 313 check
    if not s_orig or re.match(r'^[\s्र\(\)]+$', s_orig):
        print('  -> SKIPPED (empty or noise)')
        continue
    
    # Try Nepali extraction
    s_clean = re.sub(r'^[\s्र\(\)]+', '', s_orig)
    print(f'  -> s_clean={s_clean!r}')
    
    m = re.match(r'^([०१२३४५६७८९\d]{1,2})[\.\)]\s+(.+)', s_clean)
    if m:
        print(f'  -> matched number+dot pattern')
    else:
        print(f'  -> trying split-on-्र...')
        parts = [p.strip() for p in s_orig.split('्र') if p.strip()]
        print(f'  -> parts={parts}')
        
        if len(parts) >= 2:
            first = parts[0]
            print(f'  -> first={first!r}')
            
            num_m = re.match(r'(?:पाठ\s*)?:?\s*(\S+?)\s*:?', first)
            if num_m:
                g1 = num_m.group(1)
                print(f'  -> num_m.group(1)={g1!r}')
                num = fb.parse_corrupted_num(g1)
                print(f'  -> parsed num={num}')
            else:
                num = None
                print(f'  -> num_m NO MATCH')
            
            if num is None:
                num_m2 = re.match(r'(\S+?)[\.\)]', first)
                if num_m2:
                    g1 = num_m2.group(1)
                    print(f'  -> num_m2.group(1)={g1!r}')
                    num = fb.parse_corrupted_num(g1)
                    print(f'  -> parsed num={num}')
            
            if num is not None and 1 <= num <= 60:
                print(f'  -> num valid: {num}')
                
                def is_page_num(s):
                    page_chars = set('ज्ञद्दद्धघद्धछटठडढण्')
                    s_clean = s.replace(' ', '').replace('-', '')
                    return all(c in page_chars for c in s_clean if c.isalpha()) and len(s_clean) <= 4
                
                title_candidate = None
                p = parts[1]
                print(f'  -> checking parts[1]={p!r}')
                print(f'     len>2: {len(p) > 2}')
                print(f'     is_noise: {fb.is_noise(p)}')
                print(f'     is_page_num: {is_page_num(p)}')
                
                if len(p) > 2 and not fb.is_noise(p) and not is_page_num(p):
                    title_candidate = p
                    print(f'  -> title_candidate={title_candidate!r}')
                    title = fb.clean_toc_title(title_candidate)
                    print(f'  -> cleaned title={title!r}')
                    if len(title) > 2:
                        print(f'  -> FINAL MATCH: [{num}] {title}')
            else:
                print(f'  -> num invalid: {num}')
        else:
            print(f'  -> parts < 2')
