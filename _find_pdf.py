#!/usr/bin/env python3
"""Fetch a CDC book page and find PDF download links."""
import requests, re, sys
sys.stdout.reconfigure(encoding='utf-8')

url = 'https://moecdc.gov.np/content/458/history-purana-class-9--first-edition--/'
r = requests.get(url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})

# Find PDF download links
for m in re.finditer(r'href=["\']([^"\']*\.pdf[^"\']*)["\']', r.text, re.I):
    print('PDF:', m.group(1))

# Find all storage/gallery links
for m in re.finditer(r'(https?://[^"\']*storage/gallery/[^"\']*\.pdf[^"\']*)', r.text, re.I):
    print('STORAGE:', m.group(1))

# Find iframe or embed with PDF
for m in re.finditer(r'src=["\']([^"\']*\.pdf[^"\']*)["\']', r.text, re.I):
    print('SRC:', m.group(1))
