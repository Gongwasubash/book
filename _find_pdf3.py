#!/usr/bin/env python3
"""Search for PDF reference patterns in CDC book page HTML."""
import requests, re, sys
sys.stdout.reconfigure(encoding='utf-8')

url = 'https://moecdc.gov.np/content/458/history-purana-class-9--first-edition--/'
r = requests.get(url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})

# Search for dflip, pdf, source, data attributes
keywords = ['data-pdf', 'data-src', 'dflip', 'flipbook', 'source.*pdf', 'pdfUrl', 'pdf_url', 'pdf-source', 'data-file']
for kw in keywords:
    for i, line in enumerate(r.text.split('\n')):
        if kw.lower() in line.lower():
            print(f'{kw}: L{i}: {line.strip()[:300]}')
            break
    else:
        print(f'{kw}: not found')
