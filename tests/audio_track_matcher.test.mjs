import { test } from 'node:test';
import assert from 'node:assert';
import fs from 'fs';

function parseFullCsv(text) {
  const rows = [];
  let currentRow = [];
  let currentVal = '';
  let insideQuotes = false;
  for (let i = 0; i < text.length; i++) {
    const ch = text[i];
    if (ch === '"') {
      if (insideQuotes && text[i+1] === '"') { currentVal += '"'; i++; }
      else { insideQuotes = !insideQuotes; }
    } else if (ch === ';' && !insideQuotes) {
      currentRow.push(currentVal.trim());
      currentVal = '';
    } else if ((ch === '\r' || ch === '\n') && !insideQuotes) {
      if (ch === '\r' && text[i+1] === '\n') i++;
      currentRow.push(currentVal.trim());
      currentVal = '';
      if (currentRow.length > 1 || currentRow[0] !== '') rows.push(currentRow);
      currentRow = [];
    } else { currentVal += ch; }
  }
  if (currentRow.length > 0 || currentVal !== '') { currentRow.push(currentVal.trim()); rows.push(currentRow); }
  const headers = rows[0];
  const records = [];
  for (let r = 1; r < rows.length; r++) {
    const rec = {};
    headers.forEach((h, idx) => rec[h] = rows[r][idx] || '');
    records.push(rec);
  }
  return records;
}

const csv = fs.readFileSync('data/songs.csv', 'utf-8');
const songs = parseFullCsv(csv);

// Extract matchTrackToSong from index.html
const indexHtml = fs.readFileSync('index.html', 'utf-8');
const pMatchStart = indexHtml.indexOf('function matchTrackToSong(filename, songs) {');
const pMatchEnd = indexHtml.indexOf('window.matchAudioTrackToSong = matchTrackToSong;', pMatchStart);
const matchCode = indexHtml.slice(pMatchStart, pMatchEnd);

const pNormStart = indexHtml.indexOf('function normalizeSearchText(str) {');
const pNormEnd = indexHtml.indexOf('function matchTrackToSong', pNormStart);
const normCode = indexHtml.slice(pNormStart, pNormEnd);

const fullModule = new Function(normCode + '\n' + matchCode + '\nreturn { matchTrackToSong, cleanFilenameToTitleVariants };')();

test('Audio File Recognition: Legacy mask ID_type_title matches correctly', () => {
  const res = fullModule.matchTrackToSong('0482_studio_Белый_снег.mp3', songs);
  assert.ok(res, 'Legacy track should be matched');
  assert.strictEqual(res.song.id, '0482');
  assert.strictEqual(res.type, 'альбом');
});

test('Audio File Recognition: Samples from arbitrary folders match catalog >99%', () => {
  if (!fs.existsSync('uploads/примеры названий песен.txt')) return;
  const lines = fs.readFileSync('uploads/примеры названий песен.txt', 'utf-8').split(/\r?\n/).filter(Boolean);
  let matched = 0;
  for (const line of lines) {
    const res = fullModule.matchTrackToSong(line, songs);
    if (res) matched++;
  }
  const matchRate = (matched / lines.length) * 100;
  assert.ok(matchRate >= 99, `Match rate should be >= 99%, was ${matchRate}% (${matched}/${lines.length})`);
});
