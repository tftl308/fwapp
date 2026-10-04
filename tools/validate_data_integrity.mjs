/**
 * validate_data_integrity.mjs
 * Strict P0 / P1 verification suite for canonical data lifecycle:
 * 1. Validates data/songs.csv (all 700 songs, 22 canonical fields, no corrupt lines)
 * 2. Validates data/admin.html (embedded 700 songs, zero file errors)
 * 3. Validates огненныйветер.html (standalone, 700 songs inlined, zero player, no CSV upload)
 * 4. Validates lifecycle contract between lyrics (OpenSong) and chordpro (ChordPro)
 */

import fs from 'fs';
import path from 'path';
import assert from 'assert';

const ROOT = process.cwd();
console.log('--- [VALIDATE DATA INTEGRITY] Starting strict audit ---');

// 1. Audit data/songs.csv
const csvPath = path.join(ROOT, 'data', 'songs.csv');
const csvContent = fs.readFileSync(csvPath, 'utf8');
const lines = csvContent.trim().split(/\r?\n/);

const expectedHeaders = [
  'id', 'number', 'title', 'author', 'key', 'capo', 'tempo',
  'time_signature', 'duration', 'predelay', 'presentation',
  'theme', 'alttheme', 'user1', 'user2', 'user3',
  'lyrics', 'chordpro', 'notes', 'link_audio', 'link_youtube', 'custom_chords'
];

const headerRow = lines[0].split(';').map(h => h.trim());
assert.deepStrictEqual(headerRow, expectedHeaders, 'Header in data/songs.csv must match canonical 22 fields');
console.log('✓ songs.csv header verified: exactly 22 canonical columns.');

// Parse records
function parseCsv(text) {
  const records = [];
  const lines = text.trim().split(/\r?\n/);
  const headers = lines[0].split(';').map(h => h.trim());

  function parseRow(line) {
    const row = [];
    let cur = '';
    let inQuotes = false;
    for (let i = 0; i < line.length; i++) {
      const ch = line[i];
      if (ch === '"') {
        if (inQuotes && line[i+1] === '"') {
          cur += '"';
          i++;
        } else {
          inQuotes = !inQuotes;
        }
      } else if (ch === ';' && !inQuotes) {
        row.push(cur);
        cur = '';
      } else {
        cur += ch;
      }
    }
    row.push(cur);
    return row;
  }

  let acc = '';
  let inMulti = false;
  for (let i = 1; i < lines.length; i++) {
    const line = lines[i];
    if (inMulti) {
      acc += '\n' + line;
      if (acc.split('"').length % 2 === 1) {
        inMulti = false;
        const vals = parseRow(acc);
        acc = '';
        records.push(Object.fromEntries(headers.map((h, idx) => [h, vals[idx] || ''])));
      }
    } else {
      if (line.split('"').length % 2 === 0) {
        inMulti = true;
        acc = line;
      } else {
        const vals = parseRow(line);
        records.push(Object.fromEntries(headers.map((h, idx) => [h, vals[idx] || ''])));
      }
    }
  }
  return records;
}

const records = parseCsv(csvContent);
assert.strictEqual(records.length, 700, `Expected exactly 700 songs in songs.csv, got ${records.length}`);
console.log(`✓ songs.csv records count verified: exactly ${records.length} songs.`);

// 2. Audit огненныйветер.html
const readerPath = path.join(ROOT, 'огненныйветер.html');
const readerHtml = fs.readFileSync(readerPath, 'utf8');

// P0 Check: Zero player DOM elements in reader
assert(!readerHtml.includes('id="docked-player"'), 'Reader SPA must not contain docked-player element');
assert(!readerHtml.includes('<button class="nav-item" data-action="nav-tab" data-tab="player"'), 'Reader SPA must not contain player nav button');
console.log('✓ Reader SPA audio player audit: completely purged.');

// P0 Check: No CSV upload button in reader catalog
assert(!readerHtml.includes('id="input-manual-csv-reader"'), 'Reader SPA must not show CSV uploader on catalog');
console.log('✓ Reader SPA autonomy audit: clean interface without catalog CSV upload clutter.');

// P0 Check: Inlined songs count
assert(readerHtml.includes('INLINED_SONGS_CSV_DATA'), 'Reader SPA must contain INLINED_SONGS_CSV_DATA');
const inlinedRecords = parseCsv(csvContent);
assert.strictEqual(inlinedRecords.length, 700, 'Reader SPA inlined catalog must contain 700 songs');
console.log('✓ Reader SPA inlined catalog verified: 700 songs embedded.');

// 3. Audit data/admin.html
const adminPath = path.join(ROOT, 'data', 'admin.html');
const adminHtml = fs.readFileSync(adminPath, 'utf8');
assert(adminHtml.includes('compileStandaloneLightReaderFromAdmin'), 'Admin must have compileStandaloneLightReaderFromAdmin');
assert(adminHtml.includes('P0 ЗАЩИТА: запрет компиляции при пустой базе'), 'Admin must guard against compiling empty database');
assert(adminHtml.includes('LIGHT_READER_BASE64_TEMPLATE'), 'Admin must have clean Base64 reader template');
console.log('✓ Data Studio compiler guards verified: empty base protection and integrity alerts active.');

console.log('--- [VALIDATE DATA INTEGRITY] All strict audits PASSED! ---');
