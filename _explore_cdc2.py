#!/usr/bin/env python3
"""Explore CDC subcategory textbook pages."""
import re, sys
sys.stdout.reconfigure(encoding='utf-8')

try:
    import requests
except ImportError:
    import urllib.request
    def get(url):
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as resp:
            return type('R', (), {'text': resp.read().decode('utf-8')})()
else:
    def get(url):
        return requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})

BASE = 'https://moecdc.gov.np'

# Check subcategory pages
cat_pages = [
    '/category/textbook--b-/',
    '/category/textbook--e-/',
    '/category/textbook--g-/',
    '/category/textbook--m-/',
    '/category/textbook--s-/',
    '/category/textbook--t-/',
]

for p in cat_pages:
    url = BASE + p
    print(f'\n=== {p} ===')
    try:
        r = get(url)
        links = re.findall(r'/content/(\d+)/[^"\']*?textbook[^"\']*?["\']', r.text, re.I)
        if links:
            seen = set()
            for cid in links:
                if cid not in seen:
                    seen.add(cid)
                    print(f'  content/{cid}/')
        else:
            print('  No textbook links found')
    except Exception as e:
        print(f'  ERROR: {e}')
