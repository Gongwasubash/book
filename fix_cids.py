import re, os

CID_MAP = {
    '354': '\u0915\u094d\u0930',  # क्र
    '366': '\u092a\u094d\u0930',  # प्र
    '389': '\u0915\u094d\u0924',  # क्त
    '407': '\u0915\u094d\u0937',  # क्ष
    '421': '\u0916\u094d\u092f',  # ख्य
    '466': '\u091c\u094d\u091e',  # ज्ञ
    '492': '\u0920\u094d\u092f',  # ठ्य
    '559': '\u0927\u094d\u092f',  # ध्य
    '568': '\u0928\u094d\u0924\u094d\u0930',  # न्त्र
    '574': '\u0928\u094d\u0926\u094d\u0930',  # न्द्र
    '681': '\u0935\u094d\u092f',  # व्य
    '738': '\u0938\u094d\u0935',  # स्व
    '726': '\u0938\u094d\u0925\u094d\u092f',  # स्थ्य
}

# Title page reconstructions: file_basename -> list of 7 lines
TITLE_FIXES = {
    'Class 8 Health Physical Education.md': [
        '\u0938\u094d\u0935\u093e\u0938\u094d\u0925\u094d\u092f \u0924\u0925\u093e \u0936\u093e\u0930\u0940\u0930\u093f\u0915 \u0936\u093f\u0915\u094d\u0937\u093e',
        '\u0915\u0915\u094d\u0937\u093e \u096e',
        '\u0928\u0947\u092a\u093e\u0932 \u0938\u0930\u0915\u093e\u0930',
        '\u0936\u093f\u0915\u094d\u0937\u093e, \u0935\u093f\u091c\u094d\u091e\u093e\u0928 \u0924\u0925\u093e \u092a\u094d\u0930\u0935\u093f\u0927\u093f \u092e\u0928\u094d\u0924\u094d\u0930\u093e\u0932\u092f',
        '\u092a\u093e\u0920\u094d\u092f\u0915\u094d\u0930\u092e \u0935\u093f\u0915\u093e\u0938 \u0915\u0947\u0928\u094d\u0926\u094d\u0930',
        '\u0938\u093e\u0928\u094b\u0920\u093f\u092e\u093f, \u092d\u0915\u094d\u0924\u092a\u0941\u0930',
        '',
    ],
    'Class 8 Maths (Nepali).md': [
        '\u0917\u0923\u093f\u0924',
        '\u0915\u0915\u094d\u0937\u093e \u096e',
        '\u0928\u0947\u092a\u093e\u0932 \u0938\u0930\u0915\u093e\u0930',
        '\u0936\u093f\u0915\u094d\u0937\u093e, \u0935\u093f\u091c\u094d\u091e\u093e\u0928 \u0924\u0925\u093e \u092a\u094d\u0930\u0935\u093f\u0927\u093f \u092e\u0928\u094d\u0924\u094d\u0930\u093e\u0932\u092f',
        '\u092a\u093e\u0920\u094d\u092f\u0915\u094d\u0930\u092e \u0935\u093f\u0915\u093e\u0938 \u0915\u0947\u0928\u094d\u0926\u094d\u0930',
        '\u0938\u093e\u0928\u094b\u0920\u093f\u092e\u093f, \u092d\u0915\u094d\u0924\u092a\u0941\u0930',
        '',
    ],
    'Class 8 Moral Education (Nepali).md': [
        '\u0928\u0948\u0924\u093f\u0915 \u0936\u093f\u0915\u094d\u0937\u093e',
        '\u0915\u0915\u094d\u0937\u093e \u096e',
        '\u0928\u0947\u092a\u093e\u0932 \u0938\u0930\u0915\u093e\u0930',
        '\u0936\u093f\u0915\u094d\u0937\u093e, \u0935\u093f\u091c\u094d\u091e\u093e\u0928 \u0924\u0925\u093e \u092a\u094d\u0930\u0935\u093f\u0927\u093f \u092e\u0928\u094d\u0924\u094d\u0930\u093e\u0932\u092f',
        '\u092a\u093e\u0920\u094d\u092f\u0915\u094d\u0930\u092e \u0935\u093f\u0915\u093e\u0938 \u0915\u0947\u0928\u094d\u0926\u094d\u0930',
        '\u0938\u093e\u0928\u094b\u0920\u093f\u092e\u093f, \u092d\u0915\u094d\u0924\u092a\u0941\u0930',
        '',
    ],
    'Class 8 Nepali 2076.md': [
        '\u0928\u0947\u092a\u093e\u0932\u0940',
        '\u0915\u0915\u094d\u0937\u093e \u096e',
        '\u0928\u0947\u092a\u093e\u0932 \u0938\u0930\u0915\u093e\u0930',
        '\u0936\u093f\u0915\u094d\u0937\u093e, \u0935\u093f\u091c\u094d\u091e\u093e\u0928 \u0924\u0925\u093e \u092a\u094d\u0930\u0935\u093f\u0927\u093f \u092e\u0928\u094d\u0924\u094d\u0930\u093e\u0932\u092f',
        '\u092a\u093e\u0920\u094d\u092f\u0915\u094d\u0930\u092e \u0935\u093f\u0915\u093e\u0938 \u0915\u0947\u0928\u094d\u0926\u094d\u0930',
        '\u0938\u093e\u0928\u094b\u0920\u093f\u092e\u093f, \u092d\u0915\u094d\u0924\u092a\u0941\u0930',
        '',
    ],
    'Class 8 Science Environment (Nepali).md': [
        '\u0935\u093f\u091c\u094d\u091e\u093e\u0928 \u0924\u0925\u093e \u0935\u093e\u0924\u093e\u0935\u0930\u0923',
        '\u0915\u0915\u094d\u0937\u093e \u096e',
        '\u0928\u0947\u092a\u093e\u0932 \u0938\u0930\u0915\u093e\u0930',
        '\u0936\u093f\u0915\u094d\u0937\u093e, \u0935\u093f\u091c\u094d\u091e\u093e\u0928 \u0924\u0925\u093e \u092a\u094d\u0930\u0935\u093f\u0927\u093f \u092e\u0928\u094d\u0924\u094d\u0930\u093e\u0932\u092f',
        '\u092a\u093e\u0920\u094d\u092f\u0915\u094d\u0930\u092e \u0935\u093f\u0915\u093e\u0938 \u0915\u0947\u0928\u094d\u0926\u094d\u0930',
        '\u0938\u093e\u0928\u094b\u0920\u093f\u092e\u093f, \u092d\u0915\u094d\u0924\u092a\u0941\u0930',
        '',
    ],
    'Class 8 Social Studies Population.md': [
        '\u0938\u093e\u092e\u093e\u091c\u093f\u0915 \u0905\u0927\u094d\u092f\u092f\u0928 \u0924\u0925\u093e \u091c\u0928\u0938\u0919\u094d\u0916\u094d\u092f\u093e',
        '\u0936\u093f\u0915\u094d\u0937\u093e',
        '\u0915\u0915\u094d\u0937\u093e \u096e',
        '\u0928\u0947\u092a\u093e\u0932 \u0938\u0930\u0915\u093e\u0930',
        '\u0936\u093f\u0915\u094d\u0937\u093e, \u0935\u093f\u091c\u094d\u091e\u093e\u0928 \u0924\u0925\u093e \u092a\u094d\u0930\u0935\u093f\u0927\u093f \u092e\u0928\u094d\u0924\u094d\u0930\u093e\u0932\u092f',
        '\u092a\u093e\u0920\u094d\u092f\u0915\u094d\u0930\u092e \u0935\u093f\u0915\u093e\u0938 \u0915\u0947\u0928\u094d\u0926\u094d\u0930',
        '\u0938\u093e\u0928\u094b\u0920\u093f\u092e\u093f, \u092d\u0915\u094d\u0924\u092a\u0941\u0930',
        '',
    ],
    'Class 8 Vocational Technical Education.md': [
        '\u092a\u0947\u0938\u093e \u0935\u094d\u092f\u0935\u0938\u093e\u092f \u0930 \u092a\u094d\u0930\u0935\u093f\u0927\u093f \u0936\u093f\u0915\u094d\u0937\u093e',
        '\u0915\u0915\u094d\u0937\u093e \u096e',
        '\u0928\u0947\u092a\u093e\u0932 \u0938\u0930\u0915\u093e\u0930',
        '\u0936\u093f\u0915\u094d\u0937\u093e, \u0935\u093f\u091c\u094d\u091e\u093e\u0928 \u0924\u0925\u093e \u092a\u094d\u0930\u0935\u093f\u0927\u093f \u092e\u0928\u094d\u0924\u094d\u0930\u093e\u0932\u092f',
        '\u092a\u093e\u0920\u094d\u092f\u0915\u094d\u0930\u092e \u0935\u093f\u0915\u093e\u0938 \u0915\u0947\u0928\u094d\u0926\u094d\u0930',
        '\u0938\u093e\u0928\u094b\u0920\u093f\u092e\u093f, \u092d\u0915\u094d\u0924\u092a\u0941\u0930',
        '',
    ],
}

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    old_content = content

    # Step 1: Apply global CID replacements
    for cid, repl in CID_MAP.items():
        content = content.replace(f'(cid:{cid})', repl)

    # Step 2: Replace title page for known files
    basename = os.path.basename(filepath)
    if basename in TITLE_FIXES:
        lines = content.split('\n')
        new_lines = list(TITLE_FIXES[basename])
        # Preserve the rest of the file after line 7
        if len(lines) > 7:
            rest = lines[7:]
            # Skip empty leading lines from the original rest
            while rest and rest[0].strip() == '':
                rest = rest[1:]
            content = '\n'.join(new_lines + [''] + rest)
        else:
            content = '\n'.join(new_lines)

    # Step 3: Remove leftover CIDs for small values (likely artifacts)
    content = re.sub(r'\(cid:\d+\)', '', content)

    if content != old_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False


if __name__ == '__main__':
    target_dirs = ['Class 8', 'Class 9']
    fixed = []
    for d in target_dirs:
        if not os.path.isdir(d):
            continue
        for fname in os.listdir(d):
            if fname.endswith('.md'):
                fpath = os.path.join(d, fname)
                if fix_file(fpath):
                    fixed.append(fpath)
    print(f'Fixed {len(fixed)} files:')
    for f in fixed:
        print(f'  {f}')
