/**
 * Unit Tests for Song Parser, Chord Transposer, Search Engine, and CSV Round-trip
 * Run with: node tests/unit-tests.mjs
 */

import test from 'node:test';
import assert from 'node:assert/strict';

// ==========================================
// 1. CHORD PARSER & TRANSPOSER LOGIC
// ==========================================

const NOTES_SHARP = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
const NOTES_FLAT  = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B'];
const NOTES_GERMAN_SHARP = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'H'];
const NOTES_GERMAN_FLAT  = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'B', 'H'];

const CHORD_REGEX_STR = '^[A-H][b#♯♭]?(?:maj7?|min|m|dim|aug|sus[24]?|add[29]|7b5|m7b5|[0-9]|°|ø)?(?:\\/[A-H][b#♯♭]?)?$';
const CHORD_DETECTOR_REGEX = /^[A-H][b#♯♭]?(?:maj7?|min|m|dim|aug|sus[24]?|add[29]|7b5|m7b5|[0-9]|°|ø)?(?:\/[A-H][b#♯♭]?)?$/;

// Очистка и нормализация аккорда
function normalizeRootNote(note, useGerman = true) {
  let clean = note.replace('♯', '#').replace('♭', 'b');
  if (useGerman) {
    if (clean === 'B' || clean === 'Hb') return 'B'; // в немецкой нотации B = си-бемоль
    if (clean === 'H') return 'H';
  }
  return clean;
}

function parseChordTokens(chordStr, useGerman = true) {
  // Разбираем основной аккорд и бас: "F#m7b5/C#"
  const clean = chordStr.trim().replace('♯', '#').replace('♭', 'b');
  const slashIdx = clean.indexOf('/');
  let mainChord = slashIdx !== -1 ? clean.slice(0, slashIdx) : clean;
  let bass = slashIdx !== -1 ? clean.slice(slashIdx + 1) : null;

  // Извлекаем корень и суффикс
  const match = mainChord.match(/^([A-H][b#]?)(.*)$/);
  if (!match) return null;

  return {
    root: match[1],
    modifier: match[2],
    bass: bass
  };
}

function transposeNote(note, semitones, preferFlats = false, useGerman = true) {
  if (!note) return '';
  let clean = note.replace('♯', '#').replace('♭', 'b');

  // Определяем полутон (0-11)
  let idx = -1;
  if (useGerman) {
    if (clean === 'H') idx = 11;
    else if (clean === 'B') idx = 10;
  }
  
  if (idx === -1) {
    idx = NOTES_SHARP.indexOf(clean);
    if (idx === -1) idx = NOTES_FLAT.indexOf(clean);
  }

  if (idx === -1) return note; // Неизвестная нота

  let newIdx = (idx + semitones) % 12;
  if (newIdx < 0) newIdx += 12;

  if (useGerman) {
    return preferFlats ? NOTES_GERMAN_FLAT[newIdx] : NOTES_GERMAN_SHARP[newIdx];
  } else {
    return preferFlats ? NOTES_FLAT[newIdx] : NOTES_SHARP[newIdx];
  }
}

function transposeChord(chordStr, semitones, useGerman = true) {
  if (!semitones || semitones === 0) return chordStr;
  const parsed = parseChordTokens(chordStr, useGerman);
  if (!parsed) return chordStr;

  const isFlatChord = parsed.root.includes('b') || (useGerman && parsed.root === 'B');
  const preferFlats = isFlatChord;

  const newRoot = transposeNote(parsed.root, semitones, preferFlats, useGerman);
  let newBass = '';
  if (parsed.bass) {
    const isBassFlat = parsed.bass.includes('b') || (useGerman && parsed.bass === 'B');
    newBass = '/' + transposeNote(parsed.bass, semitones, isBassFlat, useGerman);
  }

  return `${newRoot}${parsed.modifier}${newBass}`;
}

// ==========================================
// 2. LINE CLASSIFIER & OPENSONG TO CHORDPRO
// ==========================================

function isChordToken(token) {
  const clean = token.replace(/[()[\]*]/g, '');
  return CHORD_DETECTOR_REGEX.test(clean) || ['N.C.', '%', '|', '||'].includes(clean);
}

function isChordLine(line) {
  const trimmed = line.trim();
  if (trimmed.startsWith('.')) return true;
  const tokens = trimmed.split(/\s+/).filter(Boolean);
  if (tokens.length === 0) return false;
  
  // Проверяем русские/английские слова, чтобы "Люблю Тебя, Господь" или "Do it again" не считались аккордами
  if (/[а-яА-ЯёЁ]/.test(trimmed)) {
    // В строке есть кириллица: может ли это быть слитное "AmБлагодать"?
    return false;
  }
  
  let chordCount = 0;
  for (const t of tokens) {
    if (isChordToken(t)) chordCount++;
  }
  return (chordCount / tokens.length) >= 0.6;
}

function parseFusedChordLine(line) {
  // Обработка:
  // 1) "AmБлагодать" -> "[Am]Благодать"
  // 2) "Am Благодать льется" -> "[Am] Благодать льется"
  const trimmed = line.trim();
  const match = trimmed.match(/^([A-H][b#]?(?:maj7?|min|m|dim|aug|sus[24]?|add[29]|7b5|m7b5|[0-9]|°|ø)?)(?:\s+)?([а-яА-ЯёЁ].*)$/);
  if (match) {
    const space = trimmed.startsWith(match[1] + ' ') ? ' ' : '';
    return `[${match[1]}]${space}${match[2]}`;
  }
  return line;
}

function convertOpenSongToChordPro(text) {
  const lines = text.split(/\r?\n/);
  const result = [];
  let pendingChords = null;

  for (let i = 0; i < lines.length; i++) {
    const rawLine = lines[i];
    const trimmed = rawLine.trim();

    if (trimmed.startsWith('.')) {
      // Строка аккордов OpenSong: убираем первый символ точки, но сохраняем остальные пробелы!
      const dotIndex = rawLine.indexOf('.');
      pendingChords = rawLine.slice(dotIndex + 1);
    } else if (pendingChords !== null) {
      // Спариваем аккорды с текстом
      let chordPositions = [];
      const chordRegex = /\S+/g;
      let m;
      while ((m = chordRegex.exec(pendingChords)) !== null) {
        chordPositions.push({ chord: m[0], pos: m.index });
      }

      // Собираем инлайн
      let merged = '';
      let textPos = 0;
      chordPositions.forEach(cp => {
        const targetPos = Math.min(cp.pos, rawLine.length);
        if (targetPos > textPos) {
          merged += rawLine.slice(textPos, targetPos);
          textPos = targetPos;
        }
        merged += `[${cp.chord}]`;
      });
      if (textPos < rawLine.length) {
        merged += rawLine.slice(textPos);
      }
      result.push(merged);
      pendingChords = null;
    } else {
      // Обычная строка
      result.push(parseFusedChordLine(rawLine));
    }
  }

  if (pendingChords !== null) {
    result.push(pendingChords.trim().split(/\s+/).map(c => `[${c}]`).join(' '));
  }

  return result.join('\n');
}

function extractPlainLyrics(chordProText) {
  return chordProText
    .replace(/\[[^\]]+\]/g, '') // удаляем [Am]
    .replace(/^[0-9]+\.\s*/gm, '') // убираем нумерацию куплетов
    .replace(/^(ПРИПЕВ|КУПЛЕТ|БРИДЖ|КОДА|ИНТРО|CHORUS|VERSE|BRIDGE):?\s*$/gmi, '')
    .split(/\r?\n/)
    .map(l => l.trim())
    .filter(Boolean)
    .join(' ');
}

// ==========================================
// 3. SEARCH ENGINE LOGIC
// ==========================================

function normalizeSearchText(text) {
  if (!text) return '';
  return text
    .normalize('NFKC')
    .toLowerCase()
    .replace(/ё/g, 'е')
    .replace(/[.,\/#!$%\^&\*;:{}=\-_`~()?"'«»—]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

function damerauLevenshtein(a, b) {
  const la = a.length;
  const lb = b.length;
  if (Math.abs(la - lb) > 2) return 99; // ранний выход
  const d = Array.from({ length: la + 1 }, () => new Array(lb + 1).fill(0));

  for (let i = 0; i <= la; i++) d[i][0] = i;
  for (let j = 0; j <= lb; j++) d[0][j] = j;

  for (let i = 1; i <= la; i++) {
    for (let j = 1; j <= lb; j++) {
      const cost = a[i - 1] === b[j - 1] ? 0 : 1;
      d[i][j] = Math.min(
        d[i - 1][j] + 1,      // deletion
        d[i][j - 1] + 1,      // insertion
        d[i - 1][j - 1] + cost // substitution
      );
      if (i > 1 && j > 1 && a[i - 1] === b[j - 2] && a[i - 2] === b[j - 1]) {
        d[i][j] = Math.min(d[i][j], d[i - 2][j - 2] + 1); // transposition
      }
    }
  }
  return d[la][lb];
}

class SongSearchIndex {
  constructor(songs) {
    this.songs = songs;
    this.buildIndex();
  }

  buildIndex() {
    this.docs = this.songs.map(song => {
      const normTitle = normalizeSearchText(song.title);
      const normAlt = normalizeSearchText(song.alt_title || '');
      const normAuthor = normalizeSearchText(song.author || '');
      const normBody = normalizeSearchText(song.body_plain || '');
      const normKey = (song.key || '').trim().toLowerCase();
      const tags = (song.tags || []).map(t => normalizeSearchText(t));

      return {
        id: song.id,
        song,
        normTitle,
        normAlt,
        normAuthor,
        normBody,
        normKey,
        tags,
        allText: `${normTitle} ${normAlt} ${normAuthor} ${tags.join(' ')} ${normBody}`
      };
    });
  }

  search(query) {
    if (!query || !query.trim()) {
      return this.songs;
    }

    // Выделяем фильтры (тэг:..., автор:..., key:...)
    const filterRegex = /(тэг|тег|tag|автор|author|key|тон):([^\s]+)/gi;
    const filters = {};
    let cleanQuery = query.replace(filterRegex, (_, key, val) => {
      const k = key.toLowerCase();
      if (k.startsWith('тэг') || k.startsWith('тег') || k === 'tag') filters.tag = normalizeSearchText(val);
      if (k === 'автор' || k === 'author') filters.author = normalizeSearchText(val);
      if (k === 'key' || k === 'тон') filters.key = val.trim().toLowerCase();
      return '';
    }).trim();

    const terms = normalizeSearchText(cleanQuery).split(/\s+/).filter(Boolean);

    let candidates = this.docs.filter(doc => {
      // Применяем фильтры
      if (filters.tag && !doc.tags.some(t => t.includes(filters.tag))) return false;
      if (filters.author && !doc.normAuthor.includes(filters.author)) return false;
      if (filters.key && doc.normKey !== filters.key) return false;
      return true;
    });

    if (terms.length === 0) {
      return candidates.map(c => c.song);
    }

    // Ранжирование по терминам с поддержкой опечаток (AND -> fallback OR)
    const scoredCandidates = [];

    candidates.forEach(doc => {
      let docScore = 0;
      let matchedTerms = 0;

      terms.forEach(term => {
        let termFound = false;
        let bestTermScore = 0;

        // Точное вхождение или префикс
        if (doc.normTitle.includes(term)) {
          bestTermScore = Math.max(bestTermScore, 50);
          termFound = true;
        } else if (doc.normAlt.includes(term)) {
          bestTermScore = Math.max(bestTermScore, 35);
          termFound = true;
        } else if (doc.normBody.includes(term)) {
          bestTermScore = Math.max(bestTermScore, 15);
          termFound = true;
        }

        // Проверка опечаток (Damerau-Levenshtein <= 2) для слов длиннее 3 букв
        if (!termFound && term.length >= 4) {
          const docWords = doc.allText.split(' ');
          for (const dw of docWords) {
            if (Math.abs(dw.length - term.length) <= 2) {
              const dist = damerauLevenshtein(term, dw);
              if (dist <= 1) {
                bestTermScore = Math.max(bestTermScore, 25);
                termFound = true;
                break;
              } else if (dist <= 2 && term.length >= 6) {
                bestTermScore = Math.max(bestTermScore, 10);
                termFound = true;
                break;
              }
            }
          }
        }

        if (termFound) {
          matchedTerms++;
          docScore += bestTermScore;
        }
      });

      if (matchedTerms === terms.length) {
        // Все слова найдены (AND)
        scoredCandidates.push({ song: doc.song, score: docScore + 100 });
      } else if (matchedTerms > 0) {
        // Частичное совпадение (OR)
        scoredCandidates.push({ song: doc.song, score: docScore });
      }
    });

    scoredCandidates.sort((a, b) => b.score - a.score);
    return scoredCandidates.map(c => c.song);
  }
}

// ==========================================
// 4. ТЕСТОВЫЕ КЕЙСЫ
// ==========================================

test('Chord Transposition: C -> D', () => {
  assert.equal(transposeChord('C', 2), 'D');
  assert.equal(transposeChord('Cmaj7', 2), 'Dmaj7');
});

test('Chord Transposition: C# and Db preservation', () => {
  assert.equal(transposeChord('C#', 2), 'D#');
  assert.equal(transposeChord('Db', 2), 'Eb');
});

test('Chord Transposition: Bb & German H/B notation', () => {
  // В немецкой нотации: Bb транспонированный на +1 = H
  assert.equal(transposeChord('Bb', 1, true), 'H');
  assert.equal(transposeChord('H', 1, true), 'C');
  assert.equal(transposeChord('Hm7', 2, true), 'C#m7');
});

test('Chord Transposition: Slash chords with bass note (A/C# +2)', () => {
  // A/C# + 2 -> H/D# (в системе с H)
  assert.equal(transposeChord('A/C#', 2, true), 'H/D#');
  assert.equal(transposeChord('G/H', 2, true), 'A/C#');
  assert.equal(transposeChord('Dm/F', 2, true), 'Em/G');
});

test('Chord Transposition: Complex jazz chords (F#m7b5, C°)', () => {
  assert.equal(transposeChord('F#m7b5', 2), 'G#m7b5');
  assert.equal(transposeChord('C°', 2), 'D°');
  assert.equal(transposeChord('Cadd9', 2), 'Dadd9');
});

test('Chord Parsing Line Classifier: Table §11 Requirements', () => {
  assert.equal(isChordLine('Am C G'), true, 'Am C G is chord line');
  assert.equal(isChordLine('A E F#m D'), true, 'A E F#m D is chord line');
  assert.equal(isChordLine('Люблю Тебя, Господь'), false, 'Cyrillic lyrics is not chord line');
  assert.equal(isChordLine('Do it again'), false, 'English lyrics words must not be treated as chords');
  
  // AmБлагодать fused parse
  const fusedResult = parseFusedChordLine('AmБлагодать');
  assert.equal(fusedResult, '[Am]Благодать', 'AmБлагодать splits into [Am]Благодать');

  const fusedWithSpace = parseFusedChordLine('Am Благодать льется');
  assert.equal(fusedWithSpace, '[Am] Благодать льется');
});

test('OpenSong to ChordPro roundtrip & extraction', () => {
  const openSongInput = `.G      G7           C
О, благодать, спасен тобой`;
  const chordPro = convertOpenSongToChordPro(openSongInput);
  assert.ok(chordPro.includes('[G]О, благ[G7]одать, спасен[C] тобой'));

  const plain = extractPlainLyrics(chordPro);
  assert.equal(plain, 'О, благодать, спасен тобой');
});

test('Search Engine §12 Mandatory Queries', () => {
  const demoSongs = [
    { id: '1', title: 'О, благодать', alt_title: 'Amazing Grace', author: 'Джон Ньютон', body_plain: 'О благодать спасен тобой небо любовь бог', key: 'G', tags: ['хвала'] },
    { id: '2', title: 'Ты искупил мир от греха', alt_title: 'Адонай, уповаем на Тебя', author: 'Иванов', body_plain: 'Адонай всей земле мир подай', key: 'Am', tags: ['хвала', 'молитва'] },
    { id: '3', title: 'Пой, курский соловей', alt_title: 'Соловей', author: 'Народная', body_plain: 'Пой курский соловей в тиши дубравы', key: 'Em', tags: ['фолк'] },
    { id: '4', title: 'В тишине молитвы', alt_title: '', author: 'Иванов', body_plain: 'Господь молюсь', key: 'Hm', tags: ['молитва'] }
  ];

  const index = new SongSearchIndex(demoSongs);

  // 1. "любовь бог небо"
  const r1 = index.search('любовь бог небо');
  assert.ok(r1.length >= 1 && r1[0].id === '1', 'Multi-word unordered match');

  // 2. "Аданай" (опечатка в Адонай)
  const r2 = index.search('Аданай');
  assert.ok(r2.length >= 1 && r2[0].id === '2', 'Typo tolerance: Аданай -> Адонай');

  // 3. "соловей курск"
  const r3 = index.search('соловей курск');
  assert.ok(r3.length >= 1 && r3[0].id === '3', 'Finds Пой, Курский соловей');

  // 4. "благодат" (стемминг/префикс)
  const r4 = index.search('благодат');
  assert.ok(r4.length >= 1 && r4[0].id === '1', 'Prefix search finds благодать');

  // 5. "тэг:хвала автор:Иванов"
  const r5 = index.search('тэг:хвала автор:Иванов');
  assert.ok(r5.length === 1 && r5[0].id === '2', 'Combined filter tag + author');

  // 6. "key:Am"
  const r6 = index.search('key:Am');
  assert.ok(r6.length === 1 && r6[0].id === '2', 'Exact key filter matches Am');

  // 7. пустой запрос
  const r7 = index.search('');
  assert.equal(r7.length, 4, 'Empty query returns all songs without crashing');
});
