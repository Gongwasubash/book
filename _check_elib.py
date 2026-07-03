#!/usr/bin/env python3
"""Check CDC elibrary for PDF direct links."""
import requests, re, sys
sys.stdout.reconfigure(encoding='utf-8')

# Try elibrary PDF endpoint for resource 3886 (Nepali Class 6)
url = 'https://lib.moecdc.gov.np/elibrary/?r=3886'
r = requests.get(url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
print(f'Status: {r.status_code}, Length: {len(r.text)}')

# Find all PDF links
for m in re.finditer(r'href=["\']([^"\']*\.pdf[^"\']*)["\']', r.text, re.I):
    print('PDF:', m.group(1))

# Find download links
for m in re.finditer(r'(download|Download|DOWNLOAD).*?href=["\']([^"\']*)["\']', r.text):
    print('DOWNLOAD:', m.group(2))

# Look for links containing "download" or "pdf"
for i, line in enumerate(r.text.split('\n')):
    if 'pdf' in line.lower() and ('href' in line.lower() or 'src' in line.lower()):
        print(f'L{i}: {line.strip()[:200]}')
        if i > 10:
            break
