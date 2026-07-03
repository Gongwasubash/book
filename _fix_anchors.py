#!/usr/bin/env python3
"""
Add {#ch-N} anchors to markdown files missing them.
Matches chapter titles from TOC_TABLES/CHAPTERS against actual file content.
"""
import re, os, sys
sys.stdout.reconfigure(encoding='utf-8')

BASE = r'E:\class  1 to 10 book\New folder\Nepal Textbooks Grade 1-10 - Markdown'

# Files needing anchors (from audit)
NEED_ANCHORS = [
    # (class, subject, [(ch_num, ch_title), ...])
    # Class 10 Compulsory Maths English
    ("Class 10", "Compulsory Mathematics (English)", [
        (1, "Sets"), (2, "Compound Interest"), (3, "Growth and Depreciation"),
        (4, "Currency & Exchange Rate"), (5, "Area and Volume"),
        (6, "Sequence and Series"), (7, "Quadratic Equation"),
        (8, "Algebraic Fraction"), (9, "Indices"),
        (10, "Triangles & Quadrilaterals"), (11, "Construction"),
        (12, "Circle"), (13, "Statistics"), (14, "Probability")
    ]),
    # Class 6 Health Physical (Nepali)
    ("Class 6", "Health Physical (Nepali)", [
        (1, "मानव शरीर"), (2, "सामुदायिक स्वास्थ्य तथा मानसिक स्वास्थ्य"),
        (3, "पोषण र खाद्य सुरक्षा"), (4, "रोग, सुरक्षा र प्राथमिक उपचार"),
        (5, "यौनिक र प्रजनन स्वास्थ्य"), (6, "शारीरिक कसरत र कवाज"),
        (7, "एथलेटिक्स र साहसिक क्रियाकलाप"), (8, "खेलहरू"),
        (9, "योग"), (10, "कलाको परिचय, रेखाङ्कन र रङ"),
        (11, "छपाइ, माटाको काम, कोलाज"), (12, "गायन र वादन"),
        (13, "नृत्य र अभिनय")
    ]),
    # Class 6 Health Physical Creative Arts (English)
    ("Class 6", "Health Physical Creative Arts (English)", [
        (1, "Human Body"), (2, "Community & Mental Health"),
        (3, "Nutrition & Food Security"), (4, "Disease, Safety & First Aid"),
        (5, "Sexual & Reproductive Health"), (6, "Physical Exercise & Drill"),
        (7, "Athletics & Adventurous Activities"), (8, "Games"),
        (9, "Yoga"), (10, "Introduction to Arts, Line Art, Colour"),
        (11, "Print Making, Clay Work, Collage"), (12, "Singing & Playing Instrument"),
        (13, "Dance & Acting")
    ]),
    # Class 6 Mathematics (English Transcribed) - uses # Unit N: headings
    ("Class 6", "Mathematics (English Transcribed)", [
        (1, "Set"), (2, "Number System"), (3, "Mensuration"),
        (4, "Algebra"), (5, "Geometry"), (6, "Statistics")
    ]),
    # Class 6 Science (Nepali)
    ("Class 6", "Science (Nepali)", [
        (1, "वैज्ञानिक सिकाइ"), (2, "सूचना तथा सञ्चार प्रविधि"),
        (3, "जीवहरू र तिनीहरूको बनोट"), (4, "जैविक विविधता र वातावरण"),
        (5, "जीवन प्रक्रिया"), (6, "बल र चाल"),
        (7, "दैनिक जीवनमा शक्ति"), (8, "विद्युत् र चुम्बकत्व"),
        (9, "पदार्थ"), (10, "दैनिक प्रयोगका सामग्रीहरू"),
        (11, "पृथ्वी र अन्तरिक्ष")
    ]),
    # Class 7 Maths (English)
    ("Class 7", "Maths (English)", [
        (1, "Set"), (2, "Whole Number"), (3, "Integer"),
        (4, "Rational Number"), (5, "Fraction and Decimal"),
        (6, "Ratio and Proportion"), (7, "Profit and Loss"),
        (8, "Unitary Method"), (9, "Perimeter, Area, Volume"),
        (10, "Indices"), (11, "Algebraic Expression"),
        (12, "Equation, Inequality, Graph"), (13, "Lines and Angles"),
        (14, "Plane Figures"), (15, "Congruent Figures"),
        (16, "Solid Objects"), (17, "Coordinates"), (18, "Statistics"),
        (19, "Symmetry"), (20, "Bearing and Scale Drawing"),
        (21, "Presentation of Data")
    ]),
    # Class 8 English 2023
    ("Class 8", "English 2023", [
        (1, "A Tour to Central Zoo"), (2, "A Father's Letter"),
        (3, "Public Announcements"), (4, "A Memoir"),
        (5, "The Old Woman and the Lime Tree"),
        (6, "Traditional Wedding Customs"), (7, "Weather Forecast"),
        (8, "Having Fun"), (9, "The Leap"),
        (10, "Vacancy Announcement"), (11, "Sir Isaac Newton"),
        (12, "Nepal's Bird Man"), (13, "Nepal Doubles"),
        (14, "The Magic Mirror"), (15, "Conservation of Earth"),
        (16, "Why I Became a Vegan"), (17, "Naresh and the Stranger"),
        (18, "Road Accidents in Nepal"), (19, "A Tale of Two Birds")
    ]),
    # Class 8 Health Physical Education
    ("Class 8", "Health Physical Education", [
        (1, "Human Body"), (2, "Personal Health"), (3, "Nutrition"),
        (4, "Disease"), (5, "Adolescent Health"),
        (6, "Drugs, Alcohol, Tobacco"), (7, "Environmental Health"),
        (8, "Safety and First Aid"), (9, "Family & Community Health"),
        (10, "Physical Education"), (11, "Drill"),
        (12, "Physical Training"), (13, "Yoga"), (14, "Games"),
        (15, "Athletics")
    ]),
    # Class 8 Maths (English Transcribed)
    ("Class 8", "Maths (English Transcribed)", [
        (1, "Set"), (2, "Whole Numbers"), (3, "Rational and Irrational"),
        (4, "Ratio and Proportion"), (5, "Profit and Loss"),
        (6, "Unitary Method"), (7, "Simple Interest"),
        (8, "Area and Volume"), (9, "Indices"),
        (10, "Algebraic Expression"), (11, "Algebraic Fraction"),
        (12, "Equation and Graph"), (13, "Lines and Angles"),
        (14, "Plane Figures"), (15, "Congruency and Similarity"),
        (16, "Solid objects"), (17, "Coordinates"), (18, "Tessellation"),
        (19, "Transformation"), (20, "Bearing and Scale Drawing"),
        (21, "Statistics")
    ]),
    # Class 8 Social Studies Population
    ("Class 8", "Social Studies Population", [
        (1, "हामी, हाम्रो परिवार र राष्ट्र"),
        (2, "हाम्रो सामाजिक मूल्य र परम्परा"),
        (3, "सामाजिक समस्या र समाधान"),
        (4, "नागरिक चेतना"), (5, "हाम्रो पृथ्वी"),
        (6, "हाम्रो विगत"), (7, "हाम्रो आर्थिक क्रियाकलाप"),
        (8, "अन्तर्राष्ट्रिय सम्बन्ध"), (9, "जनसङ्ख्या परिचय"),
        (10, "जनसङ्ख्या वृद्धि र व्यवस्थापन")
    ]),
    # Class 8 Vocational Technical Education
    ("Class 8", "Vocational Technical Education", [
        (1, "व्यावसायिक शिक्षा"), (2, "शिक्षा, तालिम र रोजगारी"),
        (3, "रोजगारी सम्बन्धी सूचना"), (4, "जीवनोपयोगी सीपहरू"),
        (5, "व्यवसाय सञ्चालन"), (6, "व्यवसाय व्यवस्थापन"),
        (7, "तरकारी खेती"), (8, "कुखुरा खेती"),
        (9, "माछा खेती, घरेलु उद्योग"), (10, "बुनाइ र हस्तकला"),
        (11, "दुग्ध व्यवसाय र पशुपालन"), (12, "लेखनकला")
    ]),
    # Class 9 Naturopath 2082 - too corrupted
    # Class 9 Science Technology 2024
    ("Class 9", "Science Technology 2024", [
        (1, "Scientific Study"), (2, "Classification of Living Beings"),
        (3, "Mushroom"), (4, "Evolution"),
        (5, "Body Structure & Life Process"), (6, "Nature and Environment"),
        (7, "Force and Motion"), (8, "Simple Machine"), (9, "Energy"),
        (10, "Wave"), (11, "Electricity"), (12, "The Universe"),
        (13, "ICT"), (14, "Atomic Structure"), (15, "Chemical Reaction"),
        (16, "Gases"), (17, "Metals and Non-metals"),
        (18, "Carbon Compounds"), (19, "Agricultural Materials")
    ]),
]

def add_anchors_to_file(filepath, chapters):
    """Add {#ch-N} anchors to headings in a markdown file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    lines = content.split('\n')
    changes = 0
    unmatched = []
    
    # First: check if file already has some anchors
    existing = set(re.findall(r'\{#ch-(\d+)\}', content))
    if existing:
        print(f"  Already has anchors: {sorted(existing, key=int)}")
        return False
    
    # Strategy 1: Find ## headings or # headings that match chapter titles
    for ch_num, ch_title in chapters:
        anchor_tag = '{#ch-' + str(ch_num) + '}'
        found = False
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            # Look for heading lines: ## ... or # ...
            m = re.match(r'^#{1,4}\s+(.+)$', stripped)
            if not m:
                continue
            heading_text = m.group(1)
            
            # Check if heading text contains the chapter title (fuzzy match)
            # For partial match: chapter title should be a significant substring
            def fuzzy_match(haystack, needle):
                h = haystack.lower().strip()
                n = needle.lower().strip()
                # Exact match
                if h == n or h.startswith(n + ' ') or h.startswith(n + ':') or h.startswith(n + '.') or h.startswith(n + '—'):
                    return True
                # Contains match (for longer titles)
                if len(n) > 5 and n in h:
                    return True
                # Check if heading contains unit/chapter number plus part of title
                if re.match(r'^#\s+(?:unit|chapter|lesson|पाठ|एकाइ)\s*\d+', stripped, re.I) and len(n) > 8:
                    # Get the part after the number
                    parts = re.split(r'[:.、]\s*', h, maxsplit=1)
                    if len(parts) > 1:
                        after_num = parts[1].strip()
                        # Check if the title starts with this
                        short_n = n.split('(')[0].split('—')[0].strip()
                        if len(short_n) > 4 and (short_n.startswith(after_num[:20]) or after_num.startswith(short_n[:20])):
                            return True
                return False
            
            if fuzzy_match(heading_text, ch_title):
                # Add anchor - but first check it doesn't already have one
                if '{#ch-' not in line:
                    new_line = line.replace(stripped, stripped + ' ' + anchor_tag)
                    lines[i] = new_line
                    changes += 1
                    found = True
                    break
        
        if not found:
            unmatched.append((ch_num, ch_title))
    
    if changes > 0:
        new_content = '\n'.join(lines)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"  Added {changes} anchors")
    else:
        print(f"  No changes")
    
    if unmatched:
        print(f"  UNMATCHED ({len(unmatched)}): {[t for _, t in unmatched]}")
    
    return changes > 0

def main():
    # First check which files exist and their current anchor state
    for cls, subj, chapters in NEED_ANCHORS:
        fname = f"{cls} {subj}.md"
        fpath = os.path.join(BASE, cls, fname)
        
        if not os.path.exists(fpath):
            print(f"NOT FOUND: {fpath}")
            continue
        
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        anchors = sorted(set(re.findall(r'\{#ch-(\d+)\}', content)))
        print(f"\n{cls}/{subj}: {len(anchors)} existing anchors -> ", end='')
        
        if len(anchors) > 0:
            print(f"Already has {anchors}")
            continue
        
        print(f"NEEDS ANCHORS ({len(chapters)} chapters)")
        add_anchors_to_file(fpath, chapters)
    
    # Now check Class 8 Preeti-corrupted files and Class 8 Maths (Nepali)_unicode
    special_files = [
        ("Class 8", "Maths (Nepali)", [
            (1, "रेखा र कोण"), (2, "त्रिभुज, चतुर्भुज र बहुभुज"),
            (3, "त्रिभुजको सर्वांगसमता र समरूपता"), (4, "वृत्त"),
            (5, "ठोस आकृतिहरू"), (6, "निर्देशांक"), (7, "क्षेत्रफल र आयतन"),
            (8, "स्थानान्तरण"), (9, "बीजगणितीय अभिव्यक्ति"), (10, "संख्या"),
            (11, "अभाज्य संख्याहरू"), (12, "अभाज्य गुणनखण्ड"),
            (13, "पूर्ण संख्याहरू"), (14, "प्राकृतिक संख्याहरू"),
            (15, "अनुपात, समानुपात र प्रतिशत"), (16, "नाफा र नोक्सान"),
            (17, "पाइथागोरस नियम"), (18, "साधारण ब्याज"),
            (19, "तथ्याङ्क शास्त्र"), (20, "बीजगणितीय अभिव्यक्तिहरू"),
            (21, "ग्राफ"), (22, "समीकरण, असमानता र रेखाचित्र")
        ]),
        ("Class 8", "Maths (Nepali)_unicode", [
            (1, "रेखा र कोण"), (2, "त्रिभुज, चतुर्भुज र बहुभुज"),
            (3, "त्रिभुजको सर्वांगसमता र समरूपता"), (4, "वृत्त"),
            (5, "ठोस आकृतिहरू"), (6, "निर्देशांक"), (7, "क्षेत्रफल र आयतन"),
            (8, "स्थानान्तरण"), (9, "बीजगणितीय अभिव्यक्ति"), (10, "संख्या"),
            (11, "अभाज्य संख्याहरू"), (12, "अभाज्य गुणनखण्ड"),
            (13, "पूर्ण संख्याहरू"), (14, "प्राकृतिक संख्याहरू"),
            (15, "अनुपात, समानुपात र प्रतिशत"), (16, "नाफा र नोक्सान"),
            (17, "पाइथागोरस नियम"), (18, "साधारण ब्याज"),
            (19, "तथ्याङ्क शास्त्र"), (20, "बीजगणितीय अभिव्यक्तिहरू"),
            (21, "ग्राफ"), (22, "समीकरण, असमानता र रेखाचित्र")
        ]),
        ("Class 8", "Moral Education (Nepali)", [
            (1, "Character Development"), (2, "Human Values"),
            (3, "Civil Rights and Duties"), (4, "Community Life Style"),
            (5, "Discipline and Positive Thinking")
        ]),
        ("Class 8", "Nepali 2076", [
            (1, "नेपाल"), (2, "मिठो"), (3, "बिदेशीले यात्रा"),
            (4, "हिमालपारि"), (5, "लघुबान्धव"), (6, "प्रीति"),
            (7, "जीवन र प्रेम"), (8, "एउटा निर्लज्जको संसार"),
            (9, "सिर्जना र वातावरण"), (10, "एउटा घटना"),
            (11, "बुबालाई चिठी"), (12, "मेरो घर"),
            (13, "विज्ञान विनासको जरिवाना"),
            (14, "स्वस्थताको लागि योगाभ्यास"), (15, "सात सुन्दरी"),
            (16, "स्काउट र गाइडिङ"), (17, "हामी एउटै हौँ"),
            (18, "चेपाङ"), (19, "जात्रा र पर्वको कथा"),
            (20, "नेपाली संस्कृति"), (21, "डा. कोफी अन्नान"),
            (22, "मधुकरी")
        ]),
        ("Class 8", "Science Environment (Nepali)", [
            (1, "भौतिक"), (2, "भौतिक"), (3, "भौतिक"),
            (4, "रसायन"), (5, "रसायन"), (6, "जीव"), (7, "भूगर्भ"), (8, "वातावरण")
        ]),
    ]
    
    print("\n\n=== Special files (may be Preeti-corrupted) ===")
    for cls, subj, chapters in special_files:
        fname = f"{cls} {subj}.md"
        fpath = os.path.join(BASE, cls, fname)
        
        if not os.path.exists(fpath):
            print(f"NOT FOUND: {fpath}")
            continue
        
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        anchors = sorted(set(re.findall(r'\{#ch-(\d+)\}', content)))
        print(f"\n{cls}/{subj}: {len(anchors)} existing anchors -> ", end='')
        
        if len(anchors) >= len(chapters):
            print(f"Already has {len(anchors)} anchors")
            continue
        
        print(f"NEEDS ANCHORS")
        add_anchors_to_file(fpath, chapters)

if __name__ == '__main__':
    main()
