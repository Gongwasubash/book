#!/usr/bin/env python3
"""
Discover CDC PDF URLs by scanning content IDs 1-500.
Skips non-textbook pages (notices, admin, etc.) by checking for Grade/class patterns.
"""
import re, json, sys, time
sys.stdout.reconfigure(encoding='utf-8')

try:
    import requests
except ImportError:
    import urllib.request
    def get(url):
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return type('R', (), {'text': resp.read().decode('utf-8'), 'status_code': resp.status})()
else:
    def get(url):
        return requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15, verify=False)

BASE = 'https://moecdc.gov.np'

# Load existing results
try:
    with open('book_pdf_map.json', 'r', encoding='utf-8') as f:
        results = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    results = {}

textbook_pattern = re.compile(
    r'(?:कक्षा|Grade|class)\s*\d+|'  # class indicators
    r'(?:पाठ्यपुस्तक|textbook|Textbook)|'
    r'(?:शिक्षा|Education|education)',
    re.I
)

skip_pattern = re.compile(
    r'(?:notice|सूचना|tender|बोलपत्र|bid|निवेदन|application|result|admit|card|syllabus|'
    r'curriculum|पाठ्यक्रम|specification|grid|model.question|guideline|निर्देशिका|'
    r'price.list|मूल्यसूची|accreditation|equivalence|list.of|selected|expert|'
    r'decision|निर्णय|minutes|कार्यविवरण|feedback|सुझाव|revision|पुनरावलोकन|'
    r'officer|अधिकृत|tender.notice|bid.notice|expression.of.interest|eoi)',
    re.I
)

def is_textbook(title, url):
    """Check if this content page is likely a textbook."""
    if skip_pattern.search(title) or skip_pattern.search(url):
        return False
    if not textbook_pattern.search(title):
        return False
    return True

# Scan content IDs 1-500
print('Scanning content IDs 1-500...')
for cid in range(1, 501):
    cid_str = str(cid)
    if cid_str in results:
        continue  # already found
    
    url = f'{BASE}/content/{cid}/'
    if cid % 10 == 0:
        print(f'  [{cid}] checking...', end='\r')
    
    try:
        r = get(url)
        tm = re.search(r'<title>([^<]+)', r.text)
        title = tm.group(1).strip() if tm else ''
        
        # Skip obvious non-textbook pages
        if not title or not is_textbook(title, url):
            continue
        
        # Extract PDF URL
        pm = re.search(r"var\s+pdf\s*=\s*['\"]([^'\"]+\.pdf[^'\"]*)['\"]", r.text)
        if pm:
            pdf_url = pm.group(1)
            pdf_name = pdf_url.split('/')[-1][:60]
            results[cid_str] = {"content_url": url, "pdf_url": pdf_url, "title": title}
            print(f'[{cid}] FOUND: {title[:50]} → {pdf_name}')
    except Exception:
        pass
    time.sleep(0.3)

# Save
with open('book_pdf_map.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f'\nDone. Total entries: {len(results)}')
