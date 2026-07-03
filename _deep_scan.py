#!/usr/bin/env python3
"""Deep scan CDC textbook page for PDF URL patterns."""
import requests, re, sys
sys.stdout.reconfigure(encoding='utf-8')

url = 'https://moecdc.gov.np/content/458/history-purana-class-9--first-edition--/'
r = requests.get(url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
text = r.text

# Search for ALL script tags containing PDF-related content
for i, line in enumerate(text.split('\n')):
    if 'pdf' in line.lower() or 'PDF' in line:
        print(f'L{i}: {line.strip()[:300]}')

# Search for _df_ or data-dflip
for i, line in enumerate(text.split('\n')):
    if '_df_' in line or 'data-dflip' in line or 'dflip' in line.lower():
        print(f'DFLIP L{i}: {line.strip()[:300]}')

# Search for source URL patterns
for i, line in enumerate(text.split('\n')):
    if 'source' in line.lower() and 'url' in line.lower():
        print(f'SOURCE L{i}: {line.strip()[:300]}')

# Search for any .pdf anywhere in the page (from JS strings)
for m in re.finditer(r'["\']([^"\']*\.pdf[^"\']*)["\']', text, re.I):
    print(f'PDF_IN_QUOTES: {m.group(1)}')
