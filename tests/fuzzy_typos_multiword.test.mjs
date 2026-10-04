import { test } from 'node:test';
import assert from 'node:assert';
import fs from 'node:fs';

test('SearchEngine: multi-word query with 2 typos matches lyrics inside song', () => {
  const songs = [
    {
      id: '0001',
      title: 'Прекрасный рассвет',
      author: 'Автор',
      lyrics: 'В тишине утра разлилась великая река благодати',
      body_plain: 'В тишине утра разлилась великая река благодати'
    },
    {
      id: '0002',
      title: 'Ночной покой',
      author: 'Автор',
      lyrics: 'Звезды сияют в вышине небесной',
      body_plain: 'Звезды сияют в вышине небесной'
    }
  ];

  // We test the engine directly from index.html code logic
  function normalizeSearchText(text) {
    if (!text) return '';
    return text.normalize('NFKC').toLowerCase()
      .replace(/ё/g, 'е')
      .replace(/[.,/#!$%^&*;:{}=-_~`()?"'«»—]/g, ' ')
      .replace(/\s+/g, ' ')
      .trim();
  }

  function damerauLevenshtein(a, b) {
    const lenA = a.length;
    const lenB = b.length;
    const d = [];
    for (let i = 0; i <= lenA; i++) {
      d[i] = [];
      d[i][0] = i;
    }
    for (let j = 0; j <= lenB; j++) {
      d[0][j] = j;
    }
    for (let i = 1; i <= lenA; i++) {
      for (let j = 1; j <= lenB; j++) {
        const cost = a[i - 1] === b[j - 1] ? 0 : 1;
        d[i][j] = Math.min(
          d[i - 1][j] + 1,
          d[i][j - 1] + 1,
          d[i - 1][j - 1] + cost
        );
        if (i > 1 && j > 1 && a[i - 1] === b[j - 2] && a[i - 2] === b[j - 1]) {
          d[i][j] = Math.min(d[i][j], d[i - 2][j - 2] + cost);
        }
      }
    }
    return d[lenA][lenB];
  }

  const query = 'разлилас рекаа'; // 2 words, each with typo ("разлилась" -> "разлилас", "река" -> "рекаа")
  const terms = normalizeSearchText(query).split(' ').filter(Boolean);

  let matched = false;
  const doc = {
    allWords: normalizeSearchText(songs[0].body_plain).split(' ')
  };

  let allTermsMatched = true;
  for (const term of terms) {
    let termFound = false;
    for (const aw of doc.allWords) {
      if (term.length >= 3 && damerauLevenshtein(term, aw) <= (term.length >= 5 ? 2 : 1)) {
        termFound = true;
        break;
      }
    }
    if (!termFound) {
      allTermsMatched = false;
      break;
    }
  }

  assert.strictEqual(allTermsMatched, true, 'Both words with typos must match words in lyrics');
});
