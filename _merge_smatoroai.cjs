const fs = require('fs');

// Read original HTML
let html = fs.readFileSync('toc_webpage.html', 'utf8');

// Read imported smatoroai entries
const smatText = fs.readFileSync('imported_toc_entries.txt', 'utf8');

// Parse smatoroai entries into key->content map
const smatEntries = {};
const smatRegex = /(addTOC\("([^"]+)",\[[\s\S]*?\n\]\);\n?)/gm;
let m;
while ((m = smatRegex.exec(smatText)) !== null) {
  smatEntries[m[2]] = m[1];
}

// Read our existing keys
const ourKeys = fs.readFileSync('our_books_clean.txt', 'utf8')
  .split('\n').map(s => s.trim()).filter(Boolean);

let replaceCount = 0;
let addCount = 0;
let skipCount = 0;

// Build a mapping: our key -> smatoroai key (handle name differences)
// smatoroai often uses "Mathematics" where we use "Maths", and drops "Compulsory"
const ourToSmat = {};
for (const ourKey of ourKeys) {
  // Direct match
  if (smatEntries[ourKey]) {
    ourToSmat[ourKey] = ourKey;
    continue;
  }
  // Try variations
  let candidate = ourKey
    .replace('Maths (English Transcribed)', 'Mathematics (English)')
    .replace('Maths (English)', 'Mathematics (English)')
    .replace('Maths (Nepali)', 'Mathematics (Nepali)')
    .replace('Compulsory English', 'English')
    .replace('Compulsory Mathematics (English)', 'Mathematics (English)')
    .replace('Compulsory Mathematics (Nepali)', 'Mathematics (Nepali)')
    .replace('Compulsory Nepali', 'Nepali')
    .replace('Science Health Physical (English)', 'Health Physical (English)')
    .replace('Science Health Physical (Nepali)', 'Health Physical (Nepali)')
    .replace('Health Physical Creative Arts (English)', 'Health Physical Creative Arts (English)')
    .replace('Science and Technology (English)', 'Science and Technology (Nepali)') // smat only has Nepali version
    .replace('Science and Technology', '');
  if (candidate && smatEntries[candidate]) {
    ourToSmat[ourKey] = candidate;
  }
}

// Process each of our addTOC() entries
for (const ourKey of ourKeys) {
  const smatKey = ourToSmat[ourKey];
  
  if (smatKey && smatEntries[smatKey]) {
    // Replace our entry with smatoroai's
    const ourRegex = new RegExp(
      `addTOC\\("${escapeRegex(ourKey)}",\\[[\\s\\S]*?\\]\\);`,
      'm'
    );
    const smatEntry = smatEntries[smatKey];
    // If keys differ, update key in the replacement
    const replacement = ourKey === smatKey ? smatEntry : smatEntry.replace(`addTOC("${smatKey}"`, `addTOC("${ourKey}"`);
    
    if (ourRegex.test(html)) {
      html = html.replace(ourRegex, replacement);
      replaceCount++;
    } else {
      skipCount++;
    }
  } else {
    // No smatoroai match — keep our version
    skipCount++;
  }
}

// Now add smatoroai entries that DON'T exist in our list
for (const [smatKey, smatEntry] of Object.entries(smatEntries)) {
  if (!ourKeys.some(k => ourToSmat[k] === smatKey)) {
    // This smatoroai entry has no corresponding book in our system
    // Don't add — would need addChapters entry too
    // Just note it
    addCount++;
  }
}

fs.writeFileSync('toc_webpage.html', html);
console.log(`Replaced: ${replaceCount}, Skipped (kept ours): ${skipCount}, Smat-only (not added): ${addCount}`);

function escapeRegex(s) {
  return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}
