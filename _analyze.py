"""Analyze all textbook .md files for structure patterns, language, noise levels"""
import os, re, json
from pathlib import Path

BASE = Path(__file__).parent.resolve()


def detect_language(text):
    dev = sum(1 for c in text if '\u0900' <= c <= '\u097F')
    non_space = sum(1 for c in text if not c.isspace())
    if non_space == 0:
        return 'english'
    return 'nepali' if (dev / non_space) > 0.05 else 'english'


def count_devanagari(text):
    return sum(1 for c in text if '\u0900' <= c <= '\u097F')


def is_noise_line(s):
    s = s.strip()
    if not s or len(s) < 2:
        return True
    if re.match(r'^[\.\s]*\u0928\u0947\u092a\u093e\u0932\u0940', s):
        return True
    if re.match(r'^[\.\s]*ENGLISH', s, re.I):
        return True
    if re.match(r'^[A-Za-z]{1,3}$', s):
        return True
    if re.match(r'^[\s\.\,\>\~\;\:\!\-\(\)\|\[\]\=\+\#\@\©\&\d]+$', s):
        return True
    if re.match(r'^\d{1,4}$', s):
        return True
    if re.match(r'^https?://\S+$', s):
        return True
    return False


def detect_chapters(lines, is_nepali):
    patterns = []
    if is_nepali:
        patterns += [
            (re.compile(r'^(?:पाठ|पाट|पाठ्य)\s*[०१२३४५६७८९\d]+(?:\s*[:\.\)\-]|\s*$)', re.I), 'nepali_lesson'),
            (re.compile(r'^एकाइ\s*[०१२३४५६७८९\d]+(?:\s*[:\.\)\-]|\s*$)'), 'nepali_unit'),
        ]
    else:
        patterns += [
            (re.compile(r'^(?:Unit|UNIT)\s+\d+(?:\s*[:\.\)\-]|\s*$)'), 'english_unit'),
            (re.compile(r'^(?:Lesson|LESSON)\s+\d+(?:\s*[:\.\)\-]|\s*$)'), 'english_lesson'),
            (re.compile(r'^(?:Chapter|CHAPTER)\s+\d+(?:\s*[:\.\)\-]|\s*$)'), 'english_chapter'),
        ]

    for pat, strategy in patterns:
        matches = [(i, lines[i].strip()) for i in range(len(lines)) if pat.match(lines[i].strip())]
        if 2 <= len(matches) <= 100:
            return (strategy, len(matches), matches)
    return (None, 0, [])


def count_cid(text):
    return len(re.findall(r'\(cid:\d+\)', text))


stats = []
for i in range(1, 11):
    cls_dir = BASE / f'Class {i}'
    if not cls_dir.is_dir():
        continue
    for fpath in sorted(cls_dir.glob('*.md')):
        raw = fpath.read_text(encoding='utf-8')
        lines = raw.split('\n')
        lang = detect_language(raw)
        dev_count = count_devanagari(raw)
        cid_count = count_cid(raw)
        noise_count = sum(1 for l in lines if is_noise_line(l))
        total_lines = len(lines)
        strategy, ch_count, ch_matches = detect_chapters(lines, lang == 'nepali')
        stats.append({
            'file': fpath.relative_to(BASE).as_posix(),
            'class': i,
            'subject': fpath.stem,
            'lang': lang,
            'total_lines': total_lines,
            'chars': len(raw),
            'dev_chars': dev_count,
            'cid_codes': cid_count,
            'noise_lines': noise_count,
            'noise_pct': round(noise_count / total_lines * 100, 1),
            'chapter_pat': strategy,
            'chapter_count': ch_count,
        })

# Summary
nepali_count = sum(1 for s in stats if s['lang'] == 'nepali')
english_count = sum(1 for s in stats if s['lang'] == 'english')
with_chapters = sum(1 for s in stats if s['chapter_count'] > 0)
without_chapters = sum(1 for s in stats if s['chapter_count'] == 0)
total_cid = sum(s['cid_codes'] for s in stats)

print(f"Total files: {len(stats)}")
print(f"  Nepali books: {nepali_count}")
print(f"  English books: {english_count}")
print(f"  With detectable chapters: {with_chapters}")
print(f"  Without chapters: {without_chapters}")
print(f"  Total CID codes remaining: {total_cid}")
print(f"\n{'='*100}")
print(f"{'File':60s} {'Lang':6s} {'Ch':4s} {'Pattern':18s} {'CID':4s} {'Noise%':7s}")
print(f"{'='*100}")

for s in sorted(stats, key=lambda x: (x['class'], x['file'])):
    pat = s['chapter_pat'] or 'none'
    ch = str(s['chapter_count']) if s['chapter_count'] else '-'
    print(f"  C{s['class']:>2} | {s['lang']:>6} | {ch:>2} | {pat:>18} | {s['cid_codes']:>3} | {s['noise_pct']:>5}% | {s['file']}")

# Identify books that need special handling
print(f"\n\n=== Books needing special attention (no chapters detected) ===")
for s in sorted(stats, key=lambda x: (x['class'], x['file'])):
    if s['chapter_count'] == 0:
        print(f"  {s['file']} ({s['lang']}, {s['chars']} chars)")

print(f"\n=== Books with high noise (>30% lines are noise) ===")
for s in sorted(stats, key=lambda x: -x['noise_pct']):
    if s['noise_pct'] > 30:
        print(f"  {s['noise_pct']:>5}% | {s['file']}")

print(f"\n=== Books with remaining CID codes ===")
for s in sorted(stats, key=lambda x: -x['cid_codes']):
    if s['cid_codes'] > 0:
        print(f"  {s['cid_codes']:>3} CID | {s['file']}")
