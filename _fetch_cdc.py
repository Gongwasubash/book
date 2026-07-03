#!/usr/bin/env python3
"""Fetch CDC textbook page and extract PDF links."""
import requests, re, sys
sys.stdout.reconfigure(encoding='utf-8')

r = requests.get('https://moecdc.gov.np/category/textbook/', timeout=15, 
                 headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
print(f'Status: {r.status_code}')
print(f'Length: {len(r.text)}')

pdfs = re.findall(r"href=['\"](.*?\.pdf)['\"]", r.text)
print(f'Found {len(pdfs)} PDF links:')
for p in pdfs[:20]:
    print(f'  {p}')
