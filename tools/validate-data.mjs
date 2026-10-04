/**
 * Валидатор целостности реляционной базы песен
 * Запуск: node tools/validate-data.mjs [каталог_с_данными]
 */

import fs from 'node:fs';
import path from 'node:path';

const dataDir = process.argv[2] || path.join(process.cwd(), 'data');

console.log(`\x1b[36m▶ Запуск валидации базы данных в каталоге: ${dataDir}\x1b[0m`);

/**
 * Парсер CSV формата RFC 4180 с поддержкой точки с запятой
 */
function parseCsv(content) {
  // Удаляем BOM, если есть
  if (content.charCodeAt(0) === 0xFEFF) {
    content = content.slice(1);
  }
  const rows = [];
  let currentRow = [];
  let currentField = '';
  let insideQuotes = false;

  for (let i = 0; i < content.length; i++) {
    const char = content[i];
    const nextChar = content[i + 1];

    if (char === '"') {
      if (insideQuotes && nextChar === '"') {
        currentField += '"';
        i++;
      } else {
        insideQuotes = !insideQuotes;
      }
    } else if (char === ';' && !insideQuotes) {
      currentRow.push(currentField);
      currentField = '';
    } else if ((char === '\r' || char === '\n') && !insideQuotes) {
      if (char === '\r' && nextChar === '\n') {
        i++;
      }
      currentRow.push(currentField);
      currentField = '';
      if (currentRow.length > 0 && !(currentRow.length === 1 && currentRow[0] === '')) {
        rows.push(currentRow);
      }
      currentRow = [];
    } else {
      currentField += char;
    }
  }

  if (currentField !== '' || currentRow.length > 0) {
    currentRow.push(currentField);
    rows.push(currentRow);
  }

  if (rows.length === 0) return [];
  const headers = rows[0].map(h => h.trim());
  const data = [];

  for (let r = 1; r < rows.length; r++) {
    const row = rows[r];
    const item = {};
    headers.forEach((header, idx) => {
      item[header] = row[idx] !== undefined ? row[idx] : '';
    });
    data.push(item);
  }
  return data;
}

const errors = [];
const warnings = [];

function checkFile(fileName) {
  const filePath = path.join(dataDir, fileName);
  if (!fs.existsSync(filePath)) {
    errors.push(`Критический файл отсутствует: ${fileName}`);
    return null;
  }
  return fs.readFileSync(filePath, 'utf-8');
}

// 1. Проверка manifest.json
const manifestRaw = checkFile('manifest.json');
let manifest = null;
if (manifestRaw) {
  try {
    manifest = JSON.parse(manifestRaw);
    if (!manifest.version || !manifest.schemaVersion) {
      warnings.push('manifest.json: отсутствуют поля version или schemaVersion');
    }
  } catch (e) {
    errors.push(`manifest.json поврежден: ${e.message}`);
  }
}

// 2. Чтение основных таблиц
const songsRaw = checkFile('songs.csv');
const tagsRaw = checkFile('tags.csv');
const songTagsRaw = checkFile('song_tags.csv');
const audioRaw = checkFile('audio.csv');
const resourcesRaw = checkFile('resources.csv');
const playlistsRaw = checkFile('playlists.csv');
const playlistItemsRaw = checkFile('playlist_items.csv');

const songs = songsRaw ? parseCsv(songsRaw) : [];
const tags = tagsRaw ? parseCsv(tagsRaw) : [];
const songTags = songTagsRaw ? parseCsv(songTagsRaw) : [];
const audio = audioRaw ? parseCsv(audioRaw) : [];
const resources = resourcesRaw ? parseCsv(resourcesRaw) : [];
const playlists = playlistsRaw ? parseCsv(playlistsRaw) : [];
const playlistItems = playlistItemsRaw ? parseCsv(playlistItemsRaw) : [];

console.log(`Загружено записей:
- Песен: ${songs.length}
- Тегов: ${tags.length}
- Связей песня-тег: ${songTags.length}
- Аудиозаписей: ${audio.length}
- Ресурсов: ${resources.length}
- Плейлистов: ${playlists.length}
- Элементов плейлистов: ${playlistItems.length}`);

// 3. Валидация уникальности ID песен
const songIds = new Set();
songs.forEach((song, idx) => {
  if (!song.id || !song.id.trim()) {
    errors.push(`songs.csv: строка ${idx + 2} не содержит обязательного поля id`);
  } else if (songIds.has(song.id)) {
    errors.push(`songs.csv: дубликат id песни "${song.id}" (строка ${idx + 2})`);
  } else {
    songIds.add(song.id);
  }

  if (!song.title || !song.title.trim()) {
    warnings.push(`songs.csv: песня ${song.id} не имеет названия (title)`);
  }

  // Проверка опасных формул
  ['title', 'body_chordpro', 'notes'].forEach(field => {
    const val = song[field] || '';
    if (/^[=+\-@]/.test(val)) {
      warnings.push(`songs.csv: поле ${field} песни ${song.id} начинается со спецсимвола формулы: "${val[0]}"`);
    }
  });
});

// 4. Валидация тегов
const tagIds = new Set();
tags.forEach((tag, idx) => {
  if (!tag.id || !tag.id.trim()) {
    errors.push(`tags.csv: строка ${idx + 2} не содержит id тега`);
  } else if (tagIds.has(tag.id)) {
    errors.push(`tags.csv: дубликат id тега "${tag.id}"`);
  } else {
    tagIds.add(tag.id);
  }
});

// 5. Валидация связей song_tags
songTags.forEach((rel, idx) => {
  if (!songIds.has(rel.song_id)) {
    errors.push(`song_tags.csv: ссылка на несуществующую песню song_id="${rel.song_id}" (строка ${idx + 2})`);
  }
  if (!tagIds.has(rel.tag_id)) {
    errors.push(`song_tags.csv: ссылка на несуществующий тег tag_id="${rel.tag_id}" (строка ${idx + 2})`);
  }
});

// 6. Валидация audio и resources
audio.forEach((aud, idx) => {
  if (aud.song_id && !songIds.has(aud.song_id)) {
    errors.push(`audio.csv: ссылка на несуществующую песню song_id="${aud.song_id}" (строка ${idx + 2})`);
  }
});

resources.forEach((res, idx) => {
  if (res.song_id && !songIds.has(res.song_id)) {
    errors.push(`resources.csv: ссылка на несуществующую песню song_id="${res.song_id}" (строка ${idx + 2})`);
  }
});

// 7. Валидация плейлистов
const playlistIds = new Set();
playlists.forEach((pl, idx) => {
  if (!pl.id || !pl.id.trim()) {
    errors.push(`playlists.csv: строка ${idx + 2} не имеет id`);
  } else if (playlistIds.has(pl.id)) {
    errors.push(`playlists.csv: дубликат id плейлиста "${pl.id}"`);
  } else {
    playlistIds.add(pl.id);
  }
});

playlistItems.forEach((item, idx) => {
  if (!playlistIds.has(item.playlist_id)) {
    errors.push(`playlist_items.csv: ссылка на несуществующий плейлист playlist_id="${item.playlist_id}" (строка ${idx + 2})`);
  }
  if (!songIds.has(item.song_id)) {
    errors.push(`playlist_items.csv: «висячая ссылка» на несуществующую песню song_id="${item.song_id}" (строка ${idx + 2})`);
  }
});

// Итоги
console.log('\n--- РЕЗУЛЬТАТЫ ВАЛИДАЦИИ ---');
if (errors.length > 0) {
  console.log(`\x1b[31m❌ НАЙДЕНО КРИТИЧЕСКИХ ОШИБОК: ${errors.length}\x1b[0m`);
  errors.forEach(e => console.log(`  - ${e}`));
} else {
  console.log(`\x1b[32m✔ Критических ошибок целостности не обнаружено!\x1b[0m`);
}

if (warnings.length > 0) {
  console.log(`\x1b[33m⚠ Предупреждений: ${warnings.length}\x1b[0m`);
  warnings.forEach(w => console.log(`  - ${w}`));
}

if (errors.length > 0) {
  process.exit(1);
} else {
  console.log(`\x1b[32m✔ Все связи реляционных данных валидны.\x1b[0m\n`);
  process.exit(0);
}
