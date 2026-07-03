#!/usr/bin/env python3
"""Explore CDC textbook category pages for PDF links."""
import re, json, sys, time
sys.stdout.reconfigure(encoding='utf-8')

try:
    import requests
except ImportError:
    import urllib.request
    def get(url, **kw):
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=kw.get('timeout', 20)) as resp:
            return type('R', (), {'text': resp.read().decode('utf-8'), 'status_code': resp.status})()
else:
    def get(url, **kw):
        return requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, **kw)

BASE = 'https://moecdc.gov.np'

# Check content/189 - textbook date page
paths = [
    '/content/189/information-of-the-date-on-the-textbooks/',
    '/content/99/factical-information-in-compulsory-nepali-textbooks-of/',
    '/content/41/social-studies-class-10/',
    '/content/63/mathematics-class-9/',
    '/content/37/population-education-class-10/',
    '/content/8/my-nepali-classroom-1/',
]

for p in paths:
    url = BASE + p
    print(f'\n=== {p} ===')
    try:
        r = get(url, timeout=20)
        # Find PDF links
        for m in re.finditer(r'var\s+pdf\s*=\s*["\']([^"\']+\.pdf[^"\']*)["\']', r.text):
            pdf = m.group(1)
            pdf_name = pdf.split('/')[-1][:80]
            print(f'  PDF: {pdf_name}')

        # Find content links to other textbooks
        for m in re.finditer(r'href=["\'](/content/(\d+)/[^"\']*?)["\']', r.text):
            cid = m.group(2)
            slug = m.group(1)[:80]
            print(f'  Link -> /content/{cid}/')
    except Exception as e:
        print(f'  ERROR: {e}')
