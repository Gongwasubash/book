const fs = require('fs');

const ts = fs.readFileSync('E:\\smatoroai\\src\\chapterMap.ts', 'utf8');

// Strip TS types — the data objects are valid JS already
let js = ts
  .replace(/^export interface .*$/gm, '')
  .replace('const chapterMap: Record<string, ChapterEntry[]> =', 'var chapterMap =')
  .replace('export default chapterMap;', '')
  .replace(/import .*/g, '');

eval(js);

function arToDev(s) {
  return String(s).split('').map(d => '०१२३४५६७८९'[parseInt(d)] || d).join('');
}

const keys = Object.keys(chapterMap).sort();
let output = '// Imported from smatoroai chapterMap.ts\n';
output += `// Total: ${keys.length} books\n\n`;

for (const key of keys) {
  const chapters = chapterMap[key];
  const entries = chapters.map((ch, i) => {
    const num = i + 1;
    const title = ch.title.replace(/"/g, '\\"');
    const pageDev = arToDev(ch.page);
    return `  {num:${num},title:"${title}",page:"${pageDev}"}`;
  }).join(',\n');
  output += `addTOC("${key}",[\n${entries}\n]);\n\n`;
}

fs.writeFileSync('imported_toc_entries.txt', output, 'utf8');
console.log('Wrote imported_toc_entries.txt with', keys.length, 'books');
