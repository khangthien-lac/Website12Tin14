// Lightweight CI script to detect hard-coded hex colors outside theme palette
// Usage: node ci_color_check.js
const fs = require('fs');
const path = require('path');

const root = process.cwd();
const exts = ['.css', '.html'];

const whitelist = new Set([
  '#c92077','/c92077', // theme heading
  '#f4cccc','/f4cccc', // theme bg
  '#1e88e5','/1e88e5', // primary
  '#26c6da','/26c6da', // gradient end
  '#e91e63','/e91e63', // accent
  '#f06292','/f06292', // hover gradient
  '#ba68c8','/ba68c8',
  '#2e86de','/2e86de',
  '#ffffff','/ffffff',
  '#000000','/000000',
  '#212121','/212121',
  '#616161','/616161',
  '#eef6ff','/eef6ff',
  '#f5f9ff','/f5f9ff',
  '#e3f2fd','/e3f2fd',
  '#0b5e93','/0b5e93',
  '#0d47a1','/0d47a1',
  '#4a148c','/4a148c',
  '#7b1fa2','/7b1fa2',
  '#dbeafe','/dbeafe',
  '#d1fae5','/d1fae5',
  '#fde2e2','/fde2e2'
]);

let violations = [];

function walk(dir) {
  let entries;
  try { entries = fs.readdirSync(dir); } catch (e) { return; }
  for (const name of entries) {
    const full = path.join(dir, name);
    const stat = fs.statSync(full);
    if (stat.isDirectory()) {
      walk(full);
    } else {
      const ext = path.extname(name).toLowerCase();
      if (!exts.includes(ext)) continue;
      const content = fs.readFileSync(full, 'utf8');
      const lines = content.split(/\r?\n/);
      lines.forEach((line, idx) => {
        const matches = line.match(/#[0-9a-fA-F]{3,6}/g);
        if (matches) {
          for (const c of matches) {
            // Normalize 3-digit hex to 6-digit if needed (e.g. #abc -> #aabbcc)
            let hex = c;
            if (hex.length === 4) {
              hex = '#' + hex[1] + hex[1] + hex[2] + hex[2] + hex[3] + hex[3];
            }
            // skip explicit theme usage like var(--hex)
            if (line.includes(`var(${c})`)) continue;
            // skip if already using a CSS var for the color
            if (line.includes('var(--') && line.includes(hex)) continue;
            // if color is in whitelist, ignore (even in 3-digit form)
            if (whitelist.has(hex.toLowerCase()) || Array.from(whitelist).some(w => w.toLowerCase() === hex.toLowerCase())) {
              continue;
            }
            // report violation using the normalized hex
            violations.push({ file: full, line: idx + 1, color: hex, snippet: line.trim() });
          }
        }
      });
    }
  }
}

walk(root);
if (violations.length > 0) {
  console.log('Color usage violations detected:');
  for (const v of violations) {
    console.log(`${v.file}:${v.line} -> ${v.color}  // ${v.snippet}`);
  }
  process.exit(1);
} else {
  console.log('No hard-coded color violations found.');
  process.exit(0);
}
