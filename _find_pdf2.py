#!/usr/bin/env python3
"""Find all links and patterns on CDC book page."""
import requests, re, sys
sys.stdout.reconfigure(encoding='utf-8')

url = 'https://moecdc.gov.np/content/458/history-purana-class-9--first-edition--/'
r = requests.get(url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})

# Search for "gallery" in the HTML text
for i, line in enumerate(r.text.split('\n')):
    if 'gallery' in line.lower() and '.pdf' in line.lower():
        print(f'L{i}: {line.strip()[:200]}')
    if 'download' in line.lower() and '.pdf' in line.lower():
        print(f'L{i}: {line.strip()[:200]}')
    if 'storage' in line.lower() and '.pdf' in line.lower():
        print(f'L{i}: {line.strip()[:200]}')

# If nothing found, search for gallery/ or storage/ more broadly
for i, line in enumerate(r.text.split('\n')):
    if ('/storage/' in line or '/gallery/' in line) and 'pdf' in line.lower():
        print(f'L{i} (storage): {line.strip()[:200]}')
