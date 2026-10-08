import fs from 'fs';
import path from 'path';

const ROOT = process.cwd();
console.log('--- [BUILD LIGHT READER SPA] Starting generation ---');

const songsCsvPath = path.join(ROOT, 'data', 'songs.csv');
const songsCsvContent = fs.readFileSync(songsCsvPath, 'utf8');

// Read the canonical огненныйветер.html which is already the canonical audited light reader
const canonicalLightReader = fs.readFileSync(path.join(ROOT, 'огненныйветер.html'), 'utf8');

// Ensure dist/reader/index.html is identical to canonical огненныйветер.html
fs.mkdirSync(path.join(ROOT, 'dist', 'reader'), { recursive: true });
fs.writeFileSync(path.join(ROOT, 'dist', 'reader', 'index.html'), canonicalLightReader, 'utf8');

console.log('✓ Successfully synchronized огненныйветер.html and dist/reader/index.html!');
