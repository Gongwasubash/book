#!/usr/bin/env python3
"""
Scrape CDC Nepal textbook pages to build a PDF URL mapping.

1. Get textbook listing from /category/textbook/
2. For each textbook, visit its page and extract the PDF URL
3. Save the mapping to a JSON file
"""
import re, json, sys, time
sys.stdout.reconfigure(encoding='utf-8')

try:
    import requests
except ImportError:
    print("requests not available, using urllib")
    import urllib.request, urllib.error
    def get(url, **kw):
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=kw.get('timeout', 15)) as resp:
            return type('R', (), {'text': resp.read().decode('utf-8'), 'status_code': resp.status})()
else:
    def get(url, **kw):
        return requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, **kw)

BASE = 'https://moecdc.gov.np'

# Step 1: Get textbook listing
print("Fetching textbook listing...")
r = get(BASE + '/category/textbook/', timeout=20)
print(f'  Status: {r.status_code}, Size: {len(r.text)}')

# Find all textbook links
links = re.findall(r'href=["\'](/content/(\d+)/[^"\']*?)["\']', r.text)
print(f'  Found {len(links)} content links')

# Deduplicate by content ID
seen_ids = set()
textbooks = []
for href, cid in links:
    if cid not in seen_ids:
        seen_ids.add(cid)
        textbooks.append((cid, href))

print(f'  Unique textbooks: {len(textbooks)}')

# Step 2: Visit each textbook page to extract PDF URL
results = {}
for i, (cid, href) in enumerate(textbooks[:50]):  # limit for testing
    url = BASE + href
    print(f'  [{i+1}/{len(textbooks)}] Fetching {url}', end='')
    try:
        r2 = get(url, timeout=20)
        # Extract PDF URL from JavaScript
        m = re.search(r"var\s+pdf\s*=\s*['\"]([^'\"]+\.pdf[^'\"]*)['\"]", r2.text)
        if m:
            pdf_url = m.group(1)
            results[href] = pdf_url
            print(f' -> OK: {pdf_url.split("/")[-1][:60]}')
        else:
            print(' -> NO PDF found')
    except Exception as e:
        print(f' -> ERROR: {e}')
    time.sleep(0.5)  # be polite

# Save results
with open('cdc_pdf_map.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f'\nDone! Found {len(results)} PDF URLs out of {len(textbooks)} textbooks.')
print('Results saved to cdc_pdf_map.json')
