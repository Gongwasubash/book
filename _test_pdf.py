#!/usr/bin/env python3
"""Test CDC storage PDF URLs."""
import requests, sys
sys.stdout.reconfigure(encoding='utf-8')

test_urls = [
    ('Math 6 EN', 'https://moecdc.gov.np/storage/gallery/1708925838.pdf'),
    ('Math 7 EN', 'https://moecdc.gov.np/storage/gallery/1709112299.pdf'),
    ('Science Tech 8 EN', 'https://moecdc.gov.np/storage/gallery/1687157819.pdf'),
    ('English 8', 'https://moecdc.gov.np/storage/gallery/1689238602.pdf'),
    ('Math 6', 'https://moecdc.gov.np/storage/gallery/1708925838.pdf'),
]

for name, url in test_urls:
    try:
        r = requests.head(url, timeout=10, allow_redirects=True)
        size = r.headers.get('Content-Length', '?')
        ct = r.headers.get('Content-Type', '?')
        print(f'{name}: HTTP {r.status_code}, type={ct}, size={size}')
    except Exception as e:
        print(f'{name}: ERROR {type(e).__name__}')
