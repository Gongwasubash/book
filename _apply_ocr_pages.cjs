const fs = require('fs');
const html = fs.readFileSync('toc_webpage.html', 'utf8');

// === CURATED OCR RESULTS ===
// Manually verified/best-guess page numbers from OCR output
// Format: key -> { chapterNum: "DevanagariPageNumber" }

const PAGE_DATA = {};

// Class 1 Mathematics (English) — carefully verified
// OCR showed: Ch 1(Shape,1), 2(Lines,13), 5(Zero,43), 6(Ten,48), 7(Add10,54), 8(Sub10,73)
// 9(11-20,91), 10(Add20,102), 11(Sub20,113), 13(Name20,126), 14(Ordinal,128), 15(21-100,134)
// 16(Add100,148), 17(Sub2digit,155), 18(Deva,161), 19(Time,174), 20(Coins,178), 21(Length,183), 22(Pictograph,188)
PAGE_DATA['Class 1|Mathematics (English)'] = {
  1: "१", 2: "१३", 5: "४३", 6: "४८",
  7: "५४", 8: "७३", 9: "९१", 10: "१०२", 11: "११३",
  13: "१२६", 14: "१३१", 15: "१३७", 16: "१५०",
  17: "१५५", 18: "१६१", 19: "१७४", 20: "१७८", 21: "१८३", 22: "१८८"
};
// Note: Ch 3(Geometric Shapes,21) and Ch 4(Numbers9,31) and Ch 12(OddEven,123) OCR missed — adjust manually later

// Class 2 Mathematics (English)
PAGE_DATA['Class 2|Mathematics (English)'] = {
  1: "१०", 2: "२२", 3: "७६", 4: "९४", 5: "१४६",
  6: "१८०", 7: "१९४", 8: "२१०", 9: "२४८"
};

// Class 4 Mathematics (English)
PAGE_DATA['Class 4|Mathematics (English)'] = {
  1: "१", 2: "८", 3: "१५", 4: "२६", 5: "४१",
  6: "६३", 7: "९८", 8: "११४", 9: "१२१", 10: "१३३",
  11: "१४१", 12: "१५३", 13: "१६४", 14: "१९०", 15: "२०५"
};

// Class 4 Science and Technology (English)
PAGE_DATA['Class 4|Science and Technology (English)'] = {
  1: "१", 2: "१७", 3: "४४", 4: "५८", 5: "८२",
  6: "९३", 7: "१२०", 8: "१४२"
};

// Wait - these English OCR results are in Arabic numerals. I need to convert to Devanagari.
// Actually, the system accepts both Devanagari and Arabic numerals in page: field,
// and the offset system handles both. Let me convert to Devanagari for consistency.

function arToDev(s) {
  return String(s).split('').map(d => '०१२३४५६७८९'[parseInt(d)]).join('');
}

// Convert all to Devanagari
for (const [key, pages] of Object.entries(PAGE_DATA)) {
  for (const [ch, page] of Object.entries(pages)) {
    if (/^\d+$/.test(page)) {
      pages[ch] = arToDev(page);
    }
  }
}

// Now add Class 7 Maths (English & Nepali) - these share the same PDF, same TOC pages
PAGE_DATA['Class 7|Maths (English)'] = {
  1: "१५", 2: "४४", 3: "६६", 4: "७६", 5: "८६", 6: "९७",
  7: "१०३", 8: "१११", 9: "१३७", 10: "१४३", 11: "१६७",
  12: "१८५", 13: "२०३", 14: "२२०", 15: "२२६", 16: "२३५",
  17: "२४१", 18: "२४९", 19: "२५८", 20: "२६८", 21: "२८२"
};

PAGE_DATA['Class 7|Maths (Nepali)'] = {
  1: "१५", 2: "४४", 3: "६६", 4: "७६", 5: "८६", 6: "९७",
  7: "१०३", 8: "१११", 9: "१३७", 10: "१४३", 11: "१६७",
  12: "१८५", 13: "२०३", 14: "२२०", 15: "२२६", 16: "२३५",
  17: "२४१", 18: "२४९", 19: "२५८", 20: "२६८", 21: "२८२"
};

// Class 5 Science Health Physical (English & Nepali) - share PDF
PAGE_DATA['Class 5|Science Health Physical (English)'] = {
  1: "३", 2: "३०", 3: "६१", 4: "७८", 5: "१०७",
  6: "१२१", 7: "१४२", 8: "१६८"
};

PAGE_DATA['Class 5|Science Health Physical (Nepali)'] = {
  1: "३", 2: "३०", 3: "६१", 4: "७८", 5: "१०७",
  6: "१२१", 7: "१४२", 8: "१६८"
};

// Class 6 Mathematics (Nepali) - partial OCR, need cleanup
PAGE_DATA['Class 6|Mathematics (Nepali)'] = {
  1: "१", 2: "१०", 3: "४०", 4: "४३", 5: "७६",
  6: "८७", 7: "९३", 8: "९९", 9: "१०६", 10: "१११",
  11: "१२८", 12: "१३१", 13: "१४९", 14: "१५९", 15: "१८६",
  16: "१९८", 17: "२०९", 18: "२०८", 19: "२१४", 20: "२२८"
};

// Class 9 Mathematics Open Ended 2079
PAGE_DATA['Class 9|Mathematics Open Ended 2079'] = {
  1: "२४", 2: "४९", 3: "७५", 4: "९८", 5: "११२",
  6: "१४६", 7: "१६९", 8: "१८४", 9: "१९६", 10: "२१४",
  11: "२३६", 12: "२५१", 13: "२७३", 14: "२८३", 15: "२९६",
  16: "३०५", 17: "३२५", 18: "३४६", 19: "३६३", 20: "३८०"
};

// Class 9 Naturopath 2082
PAGE_DATA['Class 9|Naturopath 2082'] = {
  1: "१", 2: "१९", 3: "२७", 4: "३७", 5: "५१",
  6: "६१", 7: "७१", 8: "८१", 9: "९१", 10: "१००",
  11: "११०", 12: "१२२", 13: "१४०", 14: "१५२", 15: "१७३", 16: "१८१"
};

// Class 8 Social Studies Population - OCR was messy, different chapter structure
// Skip for now, needs manual review

// Apply pages to existing addTOC calls
const tocRegex = /addTOC\("([^"]+)",\[([\s\S]*?)\]\);/g;
let result = html;
const replacements = [];

let match;
while ((match = tocRegex.exec(html)) !== null) {
  const key = match[1];
  const body = match[2];
  const fullMatch = match[0];
  
  const pages = PAGE_DATA[key];
  if (!pages) continue;
  
  // Parse existing chapters
  try {
    const chapters = eval('[' + body + ']');
    let updated = false;
    
    const newChapters = chapters.map((ch, i) => {
      const chNum = ch.num || (i + 1);
      const page = pages[chNum];
      if (page && !ch.page) {
        updated = true;
        const genreStr = ch.genre ? `,genre:${JSON.stringify(ch.genre)}` : '';
        return `  {num:${chNum},title:${JSON.stringify(ch.title)}${genreStr},page:"${page}"}`;
      }
      // Keep as-is
      const genreStr = ch.genre ? `,genre:${JSON.stringify(ch.genre)}` : '';
      const pageStr = ch.page ? `,page:"${ch.page}"` : '';
      return `  {num:${chNum},title:${JSON.stringify(ch.title)}${genreStr}${pageStr}}`;
    }).join(',\n');
    
    if (updated) {
      const newEntry = `addTOC("${key}",[\n${newChapters}\n]);`;
      replacements.push({ from: fullMatch, to: newEntry });
      console.log(`✓ ${key} - updated with ${Object.keys(pages).length} page numbers`);
    }
  } catch(e) {
    console.log(`✗ ${key} - parse error: ${e.message}`);
  }
}

// Apply all replacements
for (const { from, to } of replacements) {
  result = result.replace(from, to);
}

fs.writeFileSync('toc_webpage.html', result);
console.log(`\nApplied ${replacements.length} updates. Saved to toc_webpage.html`);
