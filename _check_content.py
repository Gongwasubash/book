#!/usr/bin/env python3
"""Check content quality of key files and extract sample text."""
import os, re

# Check the Preeti-encoded files
print("=" * 60)
print("CLASS 8 MATHS (NEPALI) - checking for Preeti encoding")
print("=" * 60)
with open('Class 8/Class 8 Maths (Nepali).md', 'rb') as f:
    raw = f.read()

# Show a sample of raw bytes around the first content
idx = raw.find(b'##')
if idx > 0:
    sample = raw[idx:idx+500]
    print(f"Raw bytes at first heading:", sample.hex(' '))
    print()
    # Try to decode as cp1252 for Preeti
    try:
        as_cp1252 = sample.decode('cp1252')
        print(f"As cp1252:", repr(as_cp1252[:200]))
    except:
        pass
    # Try as latin-1
    as_latin1 = sample.decode('latin-1')
    print(f"As latin-1:", repr(as_latin1[:200]))

print()
print("=" * 60)
print("CLASS 8 MATHS (ENGLISH TRANSCRIBED) - checking content")
print("=" * 60)
with open('Class 8/Class 8 Maths (English Transcribed).md', 'r', encoding='utf-8') as f:
    content = f.read()
dev = sum(1 for c in content if '\u0900' <= c <= '\u097F')
ascii = sum(1 for c in content if 32 <= ord(c) <= 126)
print(f"Devanagari: {dev}, ASCII: {ascii}")
# Show chapters
for m in re.finditer(r'^##\s+(.+?)\s*\{#ch-(\d+)\}', content, re.MULTILINE):
    print(f"  Ch {m.group(2)}: {m.group(1)[:80]}")

print()
print("=" * 60)
print("CLASS 10 COMPULSORY NEPALI - sample chapter content")
print("=" * 60)
with open('Class 10/Class 10 Compulsory Nepali.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find chapter 1 content
in_ch1 = False
ch1_lines = []
for i, line in enumerate(lines):
    if '{#ch-1}' in line:
        in_ch1 = True
        continue
    if in_ch1:
        if '{#ch-2}' in line:
            break
        ch1_lines.append(line.rstrip('\n'))

# Show first 30 lines of chapter 1 content
for line in ch1_lines[:30]:
    if line.strip():
        print(f"  {line.encode('utf-8')[:120]}")

print()
print("=" * 60)
print("FILES NEEDING PREETI->UNICODE CONVERSION:")
print("=" * 60)
base = os.path.dirname(os.path.abspath(__file__)) or '.'
for cls in range(1, 11):
    cls_dir = os.path.join(base, f'Class {cls}')
    if not os.path.isdir(cls_dir):
        continue
    for fname in sorted(os.listdir(cls_dir)):
        if not fname.endswith('.md'):
            continue
        fpath = os.path.join(cls_dir, fname)
        with open(fpath, 'r', encoding='utf-8') as f:
            text = f.read()
        dev = sum(1 for c in text if '\u0900' <= c <= '\u097F')
        total = len(text)
        # Has Nepali subject but very little Devanagari content?
        is_nepali_subj = 'nepali' in fname.lower() or 'nepali' in text[:200].lower()
        if is_nepali_subj and dev < total * 0.1:
            print(f"  NEEDS FIX: {fname} ({dev}/{total} Devanagari chars)")
        else:
            print(f"  OK: {fname}")
