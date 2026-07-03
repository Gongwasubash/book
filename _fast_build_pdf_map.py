#!/usr/bin/env python3
"""Fast PDF map builder - scans content IDs 1-2000 for textbook PDFs."""
import re, json, sys, time
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request

BASE = 'https://moecdc.gov.np'
results = {}
try:
    with open('book_pdf_map.json', 'r', encoding='utf-8') as f:
        results = json.load(f)
except:
    pass

print(f'Loaded {len(results)} existing entries')
skipped = 0
found = 0

for cid in range(1, 2001):
    cid_str = str(cid)
    if cid_str in results:
        skipped += 1
        continue
    url = f'{BASE}/content/{cid}/'
    if cid % 20 == 0:
        out = f'  [{cid}] total={len(results)} skipped={skipped} found={found}'
        print(out, end='\r')

    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read()
            text = raw.decode('utf-8', errors='replace')
        m = re.search(r"var\s+pdf\s*=\s*['\"]([^'\"]+\.pdf[^'\"]*)['\"]", text)
        if m:
            pdf_url = m.group(1)
            tm = re.search(r'<title>([^<]+)', text)
            title = tm.group(1).strip() if tm else ''
            results[cid_str] = {'content_url': url, 'pdf_url': pdf_url, 'title': title}
            found += 1
            print(f'\n[{cid}] FOUND: {title[:60]} -> {pdf_url.split("/")[-1][:60]}')
    except urllib.error.HTTPError:
        pass
    except Exception:
        pass
    time.sleep(0.3)

with open('book_pdf_map.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f'\nDone. Total: {len(results)}, New: {found}, Skipped: {skipped}')
