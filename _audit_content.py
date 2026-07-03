#!/usr/bin/env python3
"""Audit textbook content quality."""
import os, re

files_to_check = [
    'Class 1/Class 1 Nepali.md',
    'Class 1/Class 1 English.md',
    'Class 10/Class 10 Compulsory Nepali.md',
    'Class 10/Class 10 Compulsory English.md',
    'Class 8/Class 8 Nepali 2080.md',
    'Class 8/Class 8 Maths (Nepali).md',
    'Class 9/Class 9 Social Studies 2079.md',
    'Class 9/Class 9 Computer Science 2081.md',
    'Class 10/Class 10 Science.md',
    'Class 4/Class 4 Nepali.md',
]

for fpath in files_to_check:
    fname = os.path.basename(fpath)
    if not os.path.exists(fpath):
        print(f'{fname}: NOT FOUND')
        continue
    
    with open(fpath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Basic stats
    total = len(text)
    devanagari = sum(1 for c in text if '\u0900' <= c <= '\u097F')
    ascii_print = sum(1 for c in text if 32 <= ord(c) <= 126)
    unknowns = [c for c in text if ord(c) > 127 and not ('\u0900' <= c <= '\u097F') and c not in '\n\r\t']
    
    # Check for issues
    has_cid = '(cid:' in text
    has_fffd = '\ufffd' in text
    has_preeti = bool(re.search(r'[A-Za-z]{3,}\]\(#ch-\d+\)', text))  # Preeti-looking chapter refs
    
    # Count chapters
    chapters = re.findall(r'\{#ch-(\d+)\}', text)
    h1_count = len(re.findall(r'^# ', text, re.MULTILINE))
    h2_count = len(re.findall(r'^## ', text, re.MULTILINE))
    
    # Frontmatter
    fm_match = re.search(r'language:\s*(\w+)', text)
    lang = fm_match.group(1) if fm_match else '?'
    
    print(f'{fname}:')
    print(f'  Language: {lang}, Size: {total:,} chars')
    print(f'  Devanagari: {devanagari:,} ({100*devanagari/total:.0f}%) ASCII: {ascii_print:,} ({100*ascii_print/total:.0f}%)')
    print(f'  Unknown chars: {len(unknowns)} unique={len(set(unknowns))}')
    print(f'  Chapters: {len(chapters)} (H1={h1_count}, H2={h2_count})')
    if has_cid: print('  WARNING: Contains (cid:NNN) artifacts')
    if has_fffd: print('  WARNING: Contains U+FFFD replacement chars')
    if has_preeti: print('  WARNING: May contain Preeti-encoded text')
    
    # Show unique unknown chars
    unique_u = sorted(set(unknowns), key=ord)
    if unique_u:
        u_str = ', '.join(f'U+{ord(c):04X}' for c in unique_u[:10])
        print(f'  Unknown chars: {u_str}')
    
    # Sample a chapter heading line with content
    ch_heads = re.findall(r'^##\s+(.+?)\s*\{#ch-\d+\}', text, re.MULTILINE)
    if ch_heads:
        print(f'  Sample chapter: (escaped) {ch_heads[0][:80].encode("unicode_escape").decode()[:80]}')
    
    # Check for garbled section
    # Find a section with many consecutive non-Devanagari, non-ASCII characters
    print()
