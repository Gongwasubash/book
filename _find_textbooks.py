#!/usr/bin/env python3
"""Find actual textbook pages on CDC site."""
import re, sys
sys.stdout.reconfigure(encoding='utf-8')

try:
    import requests
except ImportError:
    import urllib.request
    get = lambda url: urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}))
else:
    def get(url):
        return requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})

# Check the textbook category page for links to specific classes
r = get('https://moecdc.gov.np/category/textbook/')
text = r.text

# Find all links
links = re.findall(r'href=["\']([^"\']+)["\']', text)

# Look for class-specific pages
class_pages = set()
for link in links:
    if any(x in link.lower() for x in ['class', 'kaksha', 'कक्षा', 'grade', 'textbook', 'text-book']):
        class_pages.add(link)

print("Class/grade related links:")
for link in sorted(class_pages)[:30]:
    print(f'  {link}')
