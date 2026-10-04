/**
 * build-pwa.mjs — Desktop & Web PWA Builder
 * Builds production-ready dist/pwa/ directory:
 * - index.html
 * - sw.js
 * - manifest.json
 * - data/ (songs.csv, audio.csv, playlists.csv, manifest.json)
 */

import fs from 'fs';
import path from 'path';

const ROOT = process.cwd();
const DIST_PWA = path.join(ROOT, 'dist', 'pwa');

console.log('--- [BUILD PWA] Generating dist/pwa artifact ---');

fs.mkdirSync(DIST_PWA, { recursive: true });
fs.mkdirSync(path.join(DIST_PWA, 'data'), { recursive: true });

// Copy core PWA assets
const filesToCopy = [
  'index.html',
  'sw.js',
  'manifest.json'
];

for (const file of filesToCopy) {
  if (fs.existsSync(path.join(ROOT, file))) {
    fs.copyFileSync(path.join(ROOT, file), path.join(DIST_PWA, file));
  }
}

// Copy data files
const dataFiles = ['songs.csv', 'audio.csv', 'playlists.csv', 'playlist_items.csv', 'user_notes.csv', 'manifest.json'];
for (const df of dataFiles) {
  const src = path.join(ROOT, 'data', df);
  if (fs.existsSync(src)) {
    fs.copyFileSync(src, path.join(DIST_PWA, 'data', df));
  }
}

console.log('✓ Successfully created dist/pwa package ready for static hosting or local PWA install.');
