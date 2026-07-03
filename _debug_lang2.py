import sys
sys.path.insert(0, r'E:\class  1 to 10 book\New folder\Nepal Textbooks Grade 1-10 - Markdown')
from format_books import reverse_reversed_text, detect_language

p = r'E:\class  1 to 10 book\New folder\Nepal Textbooks Grade 1-10 - Markdown\Class 10\Class 10 Compulsory English.md'
text = open(p, encoding='utf-8').read()
raw_lines = text.split('\n')
fixed_lines = [reverse_reversed_text(l) for l in raw_lines]

lang = detect_language(fixed_lines)
print(f'Detected language: {lang}')

# Debug: check the Devanagari ratio
full_text = '\n'.join(fixed_lines)
dev = sum(1 for c in full_text if '\u0900' <= c <= '\u097F')
non_space = sum(1 for c in full_text if not c.isspace())
print(f'Dev chars: {dev}, non-space: {non_space}, ratio: {dev/non_space:.6f}')
