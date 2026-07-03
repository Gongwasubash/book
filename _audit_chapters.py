#!/usr/bin/env python3
"""Check chapter anchor coverage across all files."""
import os, re

print("Chapter Anchor Audit")
print("=" * 70)

anchors_found = {}
files_no_anchors = []
files_preeti = []

for cls in range(1, 11):
    cls_dir = f'Class {cls}'
    if not os.path.isdir(cls_dir):
        continue
    for fname in sorted(os.listdir(cls_dir)):
        if not fname.endswith('.md'):
            continue
        fpath = os.path.join(cls_dir, fname)
        with open(fpath, 'r', encoding='utf-8') as f:
            text = f.read()
        
        anchors = sorted(set(int(m.group(1)) for m in re.finditer(r'{#ch-(\d+)\}', text)))
        
        # Check for Preeti encoding
        lang_match = re.search(r'language:\s*(\w+)', text)
        lang = lang_match.group(1) if lang_match else '?'
        dev = sum(1 for c in text if '\u0900' <= c <= '\u097F')
        
        if lang == 'nepali' and dev < 100:
            files_preeti.append((fname, len(text), dev, len(anchors)))
        elif len(anchors) == 0:
            files_no_anchors.append((fname, lang))
        
        anchors_found[fname] = (len(anchors), anchors[:5])

print(f"\nFiles with NO chapter anchors ({len(files_no_anchors)}):")
for fname, lang in sorted(files_no_anchors):
    print(f"  {fname} (lang={lang})")

print(f"\nPreeti-corrupted Nepali files ({len(files_preeti)}):")
for fname, size, dev, anchors in sorted(files_preeti):
    print(f"  {fname}: {size} chars, {dev} Devanagari, {anchors} anchors")

print(f"\nAll files anchor counts:")
for fname, (count, first5) in sorted(anchors_found.items()):
    status = "OK" if count > 0 else "MISSING"
    print(f"  {status}: {fname} -> {count} anchors")
