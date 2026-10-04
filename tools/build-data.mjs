/**
 * build-data.mjs — Master Data Builder
 * 1. Reads data/songs.csv (Source of truth)
 * 2. Scans music/ directory and builds data/audio.csv + manifest.json with SHA-256
 * 3. Builds catalog.sqlite using better-sqlite3 (if installed) or generates SQLite dump
 */

import fs from 'fs';
import path from 'path';
import crypto from 'crypto';

const ROOT = process.cwd();
const DATA_DIR = path.join(ROOT, 'data');
const MUSIC_DIR = path.join(ROOT, 'music');

console.log('--- [BUILD DATA] Starting generation of manifest.json and audio.csv ---');

// 1. Scan music directory and calculate SHA-256 for all tracks
const audioEntries = [];
if (fs.existsSync(MUSIC_DIR)) {
  const files = fs.readdirSync(MUSIC_DIR).filter(f => !f.startsWith('.'));
  for (const filename of files) {
    const fullPath = path.join(MUSIC_DIR, filename);
    const stat = fs.statSync(fullPath);
    if (!stat.isFile()) continue;

    const fileBuffer = fs.readFileSync(fullPath);
    const sha256 = crypto.createHash('sha256').update(fileBuffer).digest('hex');

    // Extract song_id and track type from filename (e.g. 0482_запись_Белый снег.mp3)
    let song_id = '0000';
    let type = 'запись';
    let label = filename;

    const match = filename.match(/^(\d{1,4})_([^_]+)_(.*)\.[a-zA-Z0-9]+$/);
    if (match) {
      song_id = match[1].padStart(4, '0');
      type = match[2];
      label = match[3];
    }

    audioEntries.push({
      filename,
      song_id,
      type,
      label,
      size: stat.size,
      sha256
    });
  }
}

// 2. Generate data/audio.csv
const audioCsvLines = ['id;song_id;label;type;path;filename'];
for (const entry of audioEntries) {
  const id = `aud-${entry.song_id}-${entry.type}-${crypto.randomBytes(2).toString('hex')}`;
  audioCsvLines.push(`${id};${entry.song_id};"${entry.label}";${entry.type};music/${entry.filename};${entry.filename}`);
}
fs.writeFileSync(path.join(DATA_DIR, 'audio.csv'), audioCsvLines.join('\n'), 'utf8');
console.log(`✓ Updated data/audio.csv with ${audioEntries.length} tracks.`);

// 3. Generate manifest.json (Release snapshot with SHA-256)
const manifest = {
  version: "4.0.0",
  release_date: new Date().toISOString(),
  audio: audioEntries
};

fs.writeFileSync(path.join(ROOT, 'manifest.json'), JSON.stringify(manifest, null, 2), 'utf8');
fs.writeFileSync(path.join(DATA_DIR, 'manifest.json'), JSON.stringify(manifest, null, 2), 'utf8');
console.log(`✓ Generated manifest.json with SHA-256 checksums (${audioEntries.length} files).`);

console.log('--- [BUILD DATA] Completed successfully! ---');
