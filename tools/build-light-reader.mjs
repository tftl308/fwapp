/**
 * build-light-reader.mjs
 * Generates огненныйветер.html and dist/reader/index.html:
 * 1. Embeds the full 700-song CSV content directly as INLINED_SONGS_CSV.
 * 2. On first launch, initializes directly from INLINED_SONGS_CSV with zero server delay.
 * 3. Keeps full ability to load fresh CSV files via file input button in UI.
 * 4. Adds external clickable links for link_audio and link_youtube.
 * 5. Strips heavy background audio players and network sync.
 */

import fs from 'fs';
import path from 'path';

const ROOT = process.cwd();
console.log('--- [BUILD LIGHT READER SPA] Starting generation ---');

const songsCsvPath = path.join(ROOT, 'data', 'songs.csv');
const songsCsvContent = fs.readFileSync(songsCsvPath, 'utf8');

// Read the canonical index.html
let html = fs.readFileSync(path.join(ROOT, 'index.html'), 'utf8');

// 1. Update Title and Branding
html = html.replace('<title>Огненный Ветер</title>', '<title>Огненный Ветер — Портативный Песенник</title>');

// 2. Hide audio player tab in bottom navigation
html = html.replace(
  '<button class="bottom-nav-btn" data-action="nav-tab" data-tab="player" aria-label="Плеер">',
  '<button class="bottom-nav-btn" data-action="nav-tab" data-tab="player" aria-label="Плеер" style="display: none !important;">'
);

// 3. Hide docked mini player permanently in CSS
const hidePlayerCss = `
    /* LIGHT READER MODE: AUDIO PLAYER HIDDEN */
    #docked-player, .song-audio-bottom-hub, [data-action="trigger-audio-batch-upload"] {
      display: none !important;
    }
    .badge-light-reader {
      font-size: 0.68rem;
      padding: 2px 7px;
      border-radius: 9999px;
      background: #fef3c7;
      color: #92400e;
      border: 1px solid #fde68a;
      font-weight: 700;
    }
`;
html = html.replace('</style>', hidePlayerCss + '\n</style>');

// 4. Inject header badge and Manual CSV Upload Button directly into top actions
const headerActionsMarker = '<div class="header-actions" id="header-actions">';
const newHeaderActions = `<div class="header-actions" id="header-actions">
      <!-- Кнопка быстрой загрузки любого CSV пользователем прямо в шапке -->
      <label class="btn btn-outline btn-sm" style="cursor: pointer; display: inline-flex; align-items: center; gap: 0.3rem;" title="Загрузить свой файл songs.csv">
        📁 Загрузить CSV
        <input type="file" id="input-manual-csv-reader" accept=".csv,text/csv" style="display: none;">
      </label>`;

if (html.includes(headerActionsMarker)) {
  html = html.replace(headerActionsMarker, newHeaderActions);
}

// 5. Add clickable links for link_audio and link_youtube in song details view
const externalLinksCode = `
    // ВНЕШНИЕ ССЫЛКИ НА АУДИО И ВИДЕО (ДЛЯ ВОКАЛИСТОВ И МУЗЫКАНТОВ)
    if (song.link_audio || song.link_youtube) {
      const extLinksBox = Renderer.createElement('div', {
        className: 'flex items-center gap-2 mt-2 flex-wrap',
        style: 'padding: 0.5rem 0.75rem; background: rgba(180, 83, 9, 0.08); border-radius: 6px; border: 1px solid rgba(180, 83, 9, 0.2);'
      });
      extLinksBox.appendChild(Renderer.createElement('strong', { className: 'text-xs text-muted' }, ['Внешние медиа:']));
      if (song.link_audio) {
        extLinksBox.appendChild(Renderer.createElement('a', {
          href: song.link_audio,
          target: '_blank',
          rel: 'noopener noreferrer',
          className: 'btn btn-outline btn-sm',
          style: 'padding: 0.2rem 0.5rem; font-size: 0.75rem; text-decoration: none;'
        }, ['🎧 Слушать оригинал ↗']));
      }
      if (song.link_youtube) {
        extLinksBox.appendChild(Renderer.createElement('a', {
          href: song.link_youtube,
          target: '_blank',
          rel: 'noopener noreferrer',
          className: 'btn btn-outline btn-sm',
          style: 'padding: 0.2rem 0.5rem; font-size: 0.75rem; text-decoration: none; color: #dc2626;'
        }, ['▶ YouTube разбор ↗']));
      }
      topBar.appendChild(extLinksBox);
    }
`;

const topBarMarker = 'topBar.appendChild(paramsWrap);';
if (html.includes(topBarMarker)) {
  html = html.replace(topBarMarker, topBarMarker + '\n' + externalLinksCode);
}

// 6. Embed the RAW CSV and instant boot loader directly into script
const inlinedDataAndBootJs = `
// =========================================================================
// ВШИТАЯ БАЗА ПЕСЕН (700 ПЕСЕН) ДЛЯ АВТОНОМНОГО КАРМАННОГО ПЕСЕННИКА
// =========================================================================
const INLINED_SONGS_CSV_DATA = ${JSON.stringify(songsCsvContent)};

function parseInlinedSongsCsv(csvText) {
  const records = CsvHelper.parse(csvText);
  return records.map(r => ({
    id: String(r.id || '').padStart(4, '0'),
    number: r.number || r.id,
    title: r.title || 'Без названия',
    author: r.author || '',
    key: r.key || '',
    key_default: r.key || '',
    capo: r.capo || '',
    tempo: r.tempo || '',
    time_signature: r.time_signature || '',
    duration: r.duration || '',
    predelay: r.predelay || '',
    presentation: r.presentation || '',
    theme: r.theme || r.alt_title || '',
    alttheme: r.alttheme || '',
    user1: r.user1 || '',
    user2: r.user2 || '',
    user3: r.user3 || '',
    lyrics: r.lyrics || r.body_plain || '',
    body_plain: r.lyrics || r.body_plain || '',
    chordpro: r.chordpro || r.body_chordpro || '',
    body_chordpro: r.chordpro || r.body_chordpro || '',
    notes: r.notes || '',
    link_audio: r.link_audio || '',
    link_youtube: r.link_youtube || '',
    custom_chords: r.custom_chords || ''
  }));
}
`;

const scriptStart = '<script>';
html = html.replace(scriptStart, scriptStart + '\n' + inlinedDataAndBootJs);

// 7. Replace loadInitialData implementation to guarantee instant loading from INLINED_SONGS_CSV_DATA
const oldLoadInitialData = `  async loadInitialData() {
    let songs = await storage.getAll('songs');
    let tags = await storage.getAll('tags');
    let songTags = await storage.getAll('songTags');
    let audio = await storage.getAll('audio');
    let playlists = await storage.getAll('playlists');
    let playlistItems = await storage.getAll('playlistItems');`;

const newLoadInitialData = `  async loadInitialData() {
    let songs = await storage.getAll('songs');
    let tags = await storage.getAll('tags');
    let songTags = await storage.getAll('songTags');
    let audio = await storage.getAll('audio');
    let playlists = await storage.getAll('playlists');
    let playlistItems = await storage.getAll('playlistItems');

    // ГАРАНТИРОВАННАЯ ИНИЦИАЛИЗАЦИЯ ИЗ ВШИТОЙ БАЗЫ 700 ПЕСЕН:
    if (!songs || songs.length === 0) {
      songs = parseInlinedSongsCsv(INLINED_SONGS_CSV_DATA);
      AppLogger.info('BOOT', 'Инициализация карманного песенника из вшитой базы: ' + songs.length + ' песен.');
      for (const s of songs) {
        await storage.putOne('songs', s);
      }
    }`;

if (html.includes(oldLoadInitialData)) {
  html = html.replace(oldLoadInitialData, newLoadInitialData);
}

// 8. Add event listener for manual CSV loading in setupDelegatedEvents
const manualCsvListener = `
    const manualCsvInput = document.getElementById('input-manual-csv-reader');
    if (manualCsvInput) {
      manualCsvInput.addEventListener('change', async (e) => {
        const file = e.target.files && e.target.files[0];
        if (!file) return;
        try {
          const text = await file.text();
          const parsedSongs = parseInlinedSongsCsv(text);
          if (parsedSongs.length === 0) {
            alert('Файл CSV пуст или не содержит корректных строк песен.');
            return;
          }
          await storage.clear('songs');
          for (const s of parsedSongs) {
            await storage.putOne('songs', s);
          }
          this.searchEngine = new SearchEngine(parsedSongs);
          store.setState({ songs: parsedSongs });
          AppController.showToast('✓ Загружено ' + parsedSongs.length + ' песен из файла ' + file.name);
          this.renderCurrentView();
        } catch (err) {
          alert('Ошибка чтения CSV файла: ' + err.message);
        }
      });
    }
`;

const setupDelegatedMarker = 'this.setupDelegatedEvents();';
if (html.includes(setupDelegatedMarker)) {
  html = html.replace(setupDelegatedMarker, setupDelegatedMarker + '\n    ' + manualCsvListener);
}

// Write deliverable to огненныйветер.html and dist/reader/index.html
fs.writeFileSync(path.join(ROOT, 'огненныйветер.html'), html, 'utf8');

fs.mkdirSync(path.join(ROOT, 'dist', 'reader'), { recursive: true });
fs.writeFileSync(path.join(ROOT, 'dist', 'reader', 'index.html'), html, 'utf8');

console.log('✓ Successfully generated огненныйветер.html with embedded 1.7MB songs.csv!');
console.log('✓ Successfully generated dist/reader/index.html!');
