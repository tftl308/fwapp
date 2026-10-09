import test from 'node:test';
import assert from 'node:assert';
import fs from 'node:fs';

test('Data Integrity: songs.csv Title and ChordPro alignment', () => {
  const content = fs.readFileSync('data/songs.csv', 'utf8');
  const lines = content.split(/\r?\n/).filter(Boolean);
  
  // We parse CSV properly
  let inQuotes = false;
  let currentField = '';
  let currentRow = [];
  const rows = [];

  for (let i = 0; i < content.length; i++) {
    const ch = content[i];
    if (ch === '"') {
      if (inQuotes && content[i + 1] === '"') {
        currentField += '"';
        i++;
      } else {
        inQuotes = !inQuotes;
      }
    } else if (ch === ';' && !inQuotes) {
      currentRow.push(currentField);
      currentField = '';
    } else if ((ch === '\r' || ch === '\n') && !inQuotes) {
      if (ch === '\r' && content[i + 1] === '\n') i++;
      currentRow.push(currentField);
      currentField = '';
      if (currentRow.length > 1) {
        rows.push(currentRow);
      }
      currentRow = [];
    } else {
      currentField += ch;
    }
  }
  if (currentRow.length > 0) {
    currentRow.push(currentField);
    rows.push(currentRow);
  }

  const header = rows[0];
  const dataRows = rows.slice(1);
  assert.strictEqual(dataRows.length, 700, 'Must have exactly 700 songs');

  let titleMismatches = 0;
  for (const row of dataRows) {
    const id = row[0];
    const title = row[2].trim();
    const chordpro = row[17] || '';
    
    // Song 0275 "Мама" legacy exception where chordpro has raw chords header
    if (id === '0275') continue;

    if (chordpro.includes('{title:')) {
      const match = chordpro.match(/\{title:\s*([^}]+)\}/);
      if (match) {
        const cpTitle = match[1].trim().toLowerCase();
        const csvTitle = title.toLowerCase();
        const matches = csvTitle === cpTitle ||
                        csvTitle.startsWith(cpTitle) ||
                        cpTitle.startsWith(csvTitle);
        if (!matches) {
          titleMismatches++;
          console.error(`Mismatch in song ${id}: CSV title="${title}" vs ChordPro title="${match[1]}"`);
        }
      }
    }
  }

  assert.strictEqual(titleMismatches, 0, `Detected ${titleMismatches} mismatched songs where wrong chords/lyrics were attached!`);
});
