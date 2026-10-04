import fs from 'fs';
import vm from 'vm';

console.log('Testing full simulation of index.html and reader...');

// 1. Read files
const indexHtml = fs.readFileSync('index.html', 'utf8');
const readerHtml = fs.readFileSync('огненныйветер.html', 'utf8');

// Check bottom-nav in readerHtml
if (!readerHtml.includes('class="bottom-nav"')) {
  console.error('FAIL: readerHtml missing bottom-nav!');
  process.exit(1);
} else {
  console.log('OK: readerHtml has bottom-nav.');
}

// Check player removed from readerHtml
if (readerHtml.includes('id="docked-player"')) {
  console.error('FAIL: readerHtml contains docked-player!');
  process.exit(1);
} else {
  console.log('OK: readerHtml does NOT contain docked-player.');
}

// Check 700 songs inlined in readerHtml
if (!readerHtml.includes('INLINED_SONGS_CSV_DATA')) {
  console.error('FAIL: readerHtml missing INLINED_SONGS_CSV_DATA!');
  process.exit(1);
} else {
  console.log('OK: readerHtml contains inlined songs data.');
}
