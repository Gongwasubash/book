#!/usr/bin/env python3
"""
Convert Preeti-encoded Nepali textbook files to Unicode.
Handles 4 files: Maths (Nepali), Moral Education (Nepali), 
Nepali 2076, Science Environment (Nepali).
"""
import os, re, sys

sys.path.insert(0, os.path.dirname(__file__))

# Try importing the converter
try:
    from nepali_converter import convert, detect_font
    CONVERTER_OK = True
except ImportError:
    try:
        from nepali_converter.nepali_converter import convert, detect_font
        CONVERTER_OK = True
    except ImportError:
        print("WARNING: nepali-converter not installed. Trying npttf2utf...")
        CONVERTER_OK = False

FILES_TO_CONVERT = [
    ('Class 8', 'Class 8 Maths (Nepali).md', 'गणित कक्षा ८'),
    ('Class 8', 'Class 8 Moral Education (Nepali).md', 'नैतिक शिक्षा कक्षा ८'),
    ('Class 8', 'Class 8 Nepali 2076.md', 'नेपाली कक्षा ८'),
    ('Class 8', 'Class 8 Science Environment (Nepali).md', 'विज्ञान तथा वातावरण कक्षा ८'),
]

def has_valid_nepali(text, min_ratio=0.1):
    """Check if text has meaningful Nepali Unicode content."""
    dev = sum(1 for c in text if '\u0900' <= c <= '\u097F')
    total = len(text.strip())
    if total == 0:
        return False
    return dev / total >= min_ratio

def separate_frontmatter(text):
    """Separate YAML frontmatter from body."""
    m = re.match(r'^(---\s*\n.*?\n---)\n?(.*)$', text, re.DOTALL)
    if m:
        return m.group(1), m.group(2)
    return '', text

def extract_chapter_headings(text):
    """Find all ## headings with {#ch-N} anchors."""
    return re.findall(r'^##\s+(.+?)\s*\{#ch-(\d+)\}', text, re.MULTILINE)

def convert_file(dirname, fname, display_title):
    fpath = os.path.join(dirname, fname)
    if not os.path.exists(fpath):
        print(f"  NOT FOUND: {fpath}")
        return False
    
    with open(fpath, 'r', encoding='utf-8') as f:
        raw = f.read()
    
    # Separate frontmatter
    fm, body = separate_frontmatter(raw)
    
    # Check if already Unicode
    if has_valid_nepali(raw):
        print(f"  ALREADY UNICODE: {fname}")
        return False
    
    print(f"  Converting: {fname} ({len(raw)} chars)")
    
    if CONVERTER_OK:
        # Use nepali-converter
        try:
            converted_body = convert(body, 'preeti')
            # Verify conversion produced Nepali text
            if has_valid_nepali(converted_body):
                new_content = fm + '\n\n' + converted_body
                # Fix common OCR artifacts
                new_content = new_content.replace('\uf0b7', '।')  # Danda
                new_content = new_content.replace('\u00b0', '')  # Degree symbol artifacts
                
                with open(fpath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"    CONVERTED SUCCESSFULLY ({len(new_content)} chars)")
                return True
            else:
                print(f"    Conversion produced little Nepali text, trying alternative...")
        except Exception as e:
            print(f"    Error: {e}")
    
    # Alternative: use npttf2utf if available
    try:
        import subprocess
        # Try using the CLI
        temp_in = fpath + '.preeti'
        temp_out = fpath + '.unicode'
        
        with open(temp_in, 'w', encoding='utf-8') as f:
            f.write(body)
        
        result = subprocess.run(
            ['npttf2utf', '-m', 'plain', '-if', 'Preeti', '-of', 'unicode', 
             '-i', temp_in, '-o', temp_out],
            capture_output=True, text=True
        )
        
        if os.path.exists(temp_out):
            with open(temp_out, 'r', encoding='utf-8') as f:
                converted_body = f.read()
            if has_valid_nepali(converted_body):
                new_content = fm + '\n\n' + converted_body
                with open(fpath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"    CONVERTED via npttf2utf")
                os.remove(temp_in)
                os.remove(temp_out)
                return True
        
        # Cleanup
        for p in [temp_in, temp_out]:
            if os.path.exists(p):
                os.remove(p)
    except Exception as e:
        print(f"    npttf2utf failed: {e}")
    
    return False

def main():
    print("=" * 60)
    print("PREETI -> UNICODE CONVERSION")
    print("=" * 60)
    
    base = os.path.dirname(os.path.abspath(__file__)) or '.'
    converted = 0
    
    for dirname, fname, display_title in FILES_TO_CONVERT:
        full_dir = os.path.join(base, dirname)
        if convert_file(full_dir, fname, display_title):
            converted += 1
    
    print(f"\nConverted {converted}/{len(FILES_TO_CONVERT)} files")

if __name__ == '__main__':
    main()
