#!/usr/bin/env python3
"""Check chapter patterns in Class 7 Maths English."""
import re, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('Class 7/Class 7 Maths (English).md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Look for patterns indicating chapter structure
# Check for "Topics Page Number" area
print('=== Lines 20-100 ===')
for i in range(20, min(100, len(lines))):
    if lines[i].strip():
        print(f'  L{i}: {lines[i].rstrip()[:120]}')

# Search for "Lesson", "Unit", "Chapter", numbered headings in body
print('\n=== "Lesson" markers ===')
for i, l in enumerate(lines):
    if 'Lesson' in l and len(l.strip()) < 60:
        print(f'  L{i}: {l.rstrip()[:100]}')

print('\n=== "Unit" markers ===')
for i, l in enumerate(lines):
    if re.search(r'\bUnit\s+\d+', l, re.I) and len(l.strip()) < 80:
        print(f'  L{i}: {l.rstrip()[:100]}')

# Look for numbered TOC-like entries
print('\n=== TOC-like content (lines 40-60) ===')
for i in range(40, 60):
    if lines[i].strip():
        print(f'  L{i}: {lines[i].rstrip()[:100]}')
