#!/usr/bin/env python3
"""Fetch CDC textbook page and analyze structure."""
import requests, re, sys, html
sys.stdout.reconfigure(encoding='utf-8')

r = requests.get('https://moecdc.gov.np/category/textbook/', timeout=15,
                 headers={'User-Agent': 'Mozilla/5.0'})

# Find all links
all_links = re.findall(r'href=["\']([^"\']+)["\']', r.text)
print(f'Total links: {len(all_links)}')
for link in all_links[:50]:
    print(f'  {link}')
