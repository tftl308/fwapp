import test from 'node:test';
import assert from 'node:assert/strict';

function normalizeSearchText(text) {
  if (!text) return '';
  return text.normalize('NFKC').toLowerCase()
    .replace(/ё/g, 'е')
    .replace(/[.,\/#!$%\^&\*;:{}=\-_~`()?"'«»—]/g, ' ')
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
        d[i][j] = Math.min(d[i][j], d[i - 2][j - 2] + 1);
      }
    }
  }
  return d[lenA][lenB];
}

function isSubsequence(sub, str) {
  let subIdx = 0;
  for (let i = 0; i < str.length; i++) {
    if (subIdx < sub.length && str[i] === sub[subIdx]) {
      subIdx++;
    }
  }
  return subIdx === sub.length;
}

test('Fuzzy Search: Consonant abbreviation "блй снг" matches "Белый снег"', () => {
  const songs = [
    { id: '0482', title: 'Белый снег', body_plain: 'Белый снег как вуаль' },
    { id: '0103', title: 'Утонули в обидах', body_plain: 'Утонули' },
    { id: '0589', title: 'Словно белые снега', body_plain: 'Снега' }
  ];

  const query = 'блй снг';
  const terms = normalizeSearchText(query).split(' ').filter(Boolean);

  const matched = songs.filter(s => {
    const tWords = normalizeSearchText(s.title).split(' ');
    return terms.every(term => {
      return tWords.some(tw => isSubsequence(term, tw) || damerauLevenshtein(term, tw) <= 1);
    });
  });

  assert.ok(matched.length >= 1, 'Must find at least one match');
  assert.equal(matched[0].id, '0482', 'Top match must be Белый снег');
});

test('Fuzzy Search: Subsequence matcher precision', () => {
  assert.equal(isSubsequence('блй', 'белый'), true);
  assert.equal(isSubsequence('снг', 'снег'), true);
  assert.equal(isSubsequence('xyz', 'белый'), false);
});
