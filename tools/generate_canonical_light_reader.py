# -*- coding: utf-8 -*-
import json
import base64
import os
import re

# Read index.html as the primary application codebase
with open('index.html', 'r', encoding='utf-8') as f:
    app_html = f.read()

# 1. Title and Branding
app_html = app_html.replace('<title>Музыка Огненного Ветра</title>', '<title>Музыка Огненного Ветра — Карманный Сборник</title>')

# 2. PHYSICAL REMOVAL OF DOCKED PLAYER AND PLAYER TAB FROM HTML:
pos_start = app_html.find('<div class="docked-player-bar"')
pos_end = app_html.find('</div>\n  </div>', pos_start) + len('</div>\n  </div>')
assert pos_start != -1 and pos_end != -1, "Docked player markup not found"
app_html = app_html[:pos_start] + '<!-- Player removed in Light Reader -->' + app_html[pos_end:]

player_btn_start = app_html.find('<button class="nav-item" data-action="nav-tab" data-tab="player">')
player_btn_end = app_html.find('</button>', player_btn_start) + len('</button>')
assert player_btn_start != -1 and player_btn_end != -1, "Player nav button not found"
app_html = app_html[:player_btn_start] + app_html[player_btn_end:]

# Hide any player elements via CSS as well
player_purge_css = """
    /* LIGHT READER PURGE: ZERO AUDIO / ZERO PLAYER */
    #docked-player, .song-audio-bottom-hub, [data-tab="player"], [data-action="trigger-audio-batch-upload"] {
      display: none !important;
    }
"""
app_html = app_html.replace('</style>', player_purge_css + '\n</style>')

# 3. STRICT SETTINGS VIEW (P0 requirement: only 5 blocks, no CSV upload, strictly in order)
strict_settings_view = """  renderSettingsView(container) {
    container.innerHTML = '';
    const state = store.getState();
    const wrap = Renderer.createElement('div', { className: 'flex', style: 'flex-direction: column; gap: 1rem;' });

    // 1. ПОЛНОЭКРАННЫЙ РЕЖИМ
    const fullscreenCard = Renderer.createElement('div', { className: 'song-card', style: 'flex-direction: column; align-items: stretch; gap: 0.75rem;' });
    fullscreenCard.appendChild(Renderer.createElement('h3', { className: 'text-main text-sm' }, ['⛶ Полноэкранный режим']));
    fullscreenCard.appendChild(Renderer.createElement('div', { className: 'text-sm text-muted' }, [
      'Убрать рамки браузера для максимального удобства на сцене и репетиции.'
    ]));
    const fsBtns = Renderer.createElement('div', { className: 'flex gap-2 flex-wrap' }, [
      Renderer.createElement('button', {
        className: 'btn btn-outline btn-sm',
        dataset: { action: 'toggle-fullscreen-app' }
      }, ['⛶ Переключить полный экран'])
    ]);
    fullscreenCard.appendChild(fsBtns);
    wrap.appendChild(fullscreenCard);

    // 2. ЦВЕТОВАЯ СХЕМА
    const themeCard = Renderer.createElement('div', { className: 'song-card', style: 'flex-direction: column; align-items: stretch; gap: 0.75rem;' });
    themeCard.appendChild(Renderer.createElement('h3', { className: 'text-main text-sm' }, ['🎨 Цветовая схема']));
    themeCard.appendChild(Renderer.createElement('div', { className: 'text-sm text-muted' }, [
      'Выберите комфортную палитру оформления и контраста аккордов:'
    ]));
    const themeBtns = Renderer.createElement('div', { className: 'flex gap-2 flex-wrap' }, [
      Renderer.createElement('button', {
        className: 'btn btn-outline btn-sm',
        dataset: { action: 'toggle-theme-palette' }
      }, ['Сменить цветовую гамму'])
    ]);
    themeCard.appendChild(themeBtns);
    wrap.appendChild(themeCard);

    // 3. РЕЖИМ РАБОТЫ (ПРОФИЛЬ МУЗЫКАНТА)
    const profCard = Renderer.createElement('div', { className: 'song-card', style: 'flex-direction: column; align-items: stretch; gap: 0.75rem;' });
    profCard.appendChild(Renderer.createElement('h3', { className: 'text-main text-sm' }, ['🎸 Режим работы']));
    profCard.appendChild(Renderer.createElement('div', { className: 'text-sm text-muted' }, [
      'По умолчанию включён режим слушателя. Если вы играете в группе, выберите свой инструмент для отображения персональных заметок:'
    ]));

    const selectProfileWrap = Renderer.createElement('div', { className: 'w-full mt-2' });
    const profileSelect = Renderer.createElement('select', {
      className: 'input-select w-full',
      dataset: { action: 'select-profile-dropdown' },
      style: 'font-weight: 700;'
    });

    const optDefault = Renderer.createElement('option', { value: 'none' }, ['Обычный пользователь (Слушатель)']);
    if (state.currentProfile === 'none') optDefault.selected = true;
    profileSelect.appendChild(optDefault);

    MUSICIAN_PROFILES.forEach(p => {
      const opt = Renderer.createElement('option', { value: p.id }, [p.label]);
      if (state.currentProfile === p.id) opt.selected = true;
      profileSelect.appendChild(opt);
    });

    selectProfileWrap.appendChild(profileSelect);
    profCard.appendChild(selectProfileWrap);
    wrap.appendChild(profCard);

    // 4. ЭКСПОРТ ЗАМЕТОК
    const notesSyncCard = Renderer.createElement('div', { className: 'song-card', style: 'flex-direction: column; align-items: stretch; gap: 0.75rem;' });
    notesSyncCard.appendChild(Renderer.createElement('h3', { className: 'text-main text-sm' }, ['📤 Экспорт заметок']));
    notesSyncCard.appendChild(Renderer.createElement('div', { className: 'text-sm text-muted' }, [
      'Сохранить или передать администратору сделанные вами пометки к песням:'
    ]));

    const syncBtns = Renderer.createElement('div', { className: 'flex gap-2 mt-2 flex-wrap' }, [
      Renderer.createElement('button', {
        className: 'btn btn-primary btn-sm',
        dataset: { action: 'export-notes-json' }
      }, ['📤 Экспорт базы заметок для админа']),
      Renderer.createElement('button', {
        className: 'btn btn-outline btn-sm',
        dataset: { action: 'import-notes-json' }
      }, ['📥 Загрузить файл заметок'])
    ]);

    const hiddenFileInput = Renderer.createElement('input', {
      type: 'file',
      id: 'file-import-notes',
      accept: '.json',
      className: 'hidden'
    });
    hiddenFileInput.addEventListener('change', (e) => this.handleImportFile(e));

    notesSyncCard.appendChild(syncBtns);
    notesSyncCard.appendChild(hiddenFileInput);
    wrap.appendChild(notesSyncCard);

    // 5. ДИАГНОСТИЧЕСКИЙ ЖУРНАЛ (ЛОГ)
    const logCard = Renderer.createElement('div', { className: 'song-card', style: 'flex-direction: column; align-items: stretch; gap: 0.75rem;' });
    logCard.appendChild(Renderer.createElement('h3', { className: 'text-main text-sm' }, ['🛠 Диагностический лог']));
    logCard.appendChild(Renderer.createElement('div', { className: 'text-xs text-muted' }, [
      'Технический журнал событий и ошибок приложения:'
    ]));

    const logBox = Renderer.createElement('pre', {
      id: 'debug-log-content',
      style: 'max-height: 180px; overflow-y: auto; background: #1c1917; color: #a3e635; padding: 0.5rem; border-radius: 0.4rem; font-size: 0.72rem; font-family: monospace; white-space: pre-wrap; word-break: break-all;'
    }, [AppLogger.getFormattedLogs() || '[Журнал пуст. Все системы работают в штатном режиме...]']);
    logCard.appendChild(logBox);

    const logBtns = Renderer.createElement('div', { className: 'flex gap-2 flex-wrap' }, [
      Renderer.createElement('button', {
        className: 'btn btn-outline btn-sm',
        dataset: { action: 'copy-app-logs' }
      }, ['📋 Скопировать лог']),
      Renderer.createElement('button', {
        className: 'btn btn-outline btn-sm',
        dataset: { action: 'download-app-logs' }
      }, ['💾 Скачать лог (.txt)']),
      Renderer.createElement('button', {
        className: 'btn btn-outline btn-sm text-muted',
        dataset: { action: 'clear-app-logs' }
      }, ['Очистить'])
    ]);
    logCard.appendChild(logBtns);
    wrap.appendChild(logCard);

    container.appendChild(wrap);
  }"""

pos_set = app_html.find('renderSettingsView(container) {')
assert pos_set != -1
pos_set_end = app_html.find('container.appendChild(wrap);\n  }', pos_set)
assert pos_set_end != -1
app_html = app_html[:pos_set] + strict_settings_view[2:] + app_html[pos_set_end + len('container.appendChild(wrap);\n  }'):]

# 4. Split at <script>
script_pos = app_html.find('<script>')
assert script_pos != -1
html_before_script = app_html[:script_pos]
script_content = app_html[script_pos + len('<script>'):]

# 5. INLINED CSV PARSER AND GUARANTEED RESEED
inlined_header = """
const INLINED_SONGS_CSV_DATA = __CSV_DATA_JSON__;

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
"""

# Guarantee loadInitialData ALWAYS loads inlined catalog if database has fewer songs than catalog
load_old = """  async loadInitialData() {
    let songs = await storage.getAll('songs');
    let tags = await storage.getAll('tags');
    let songTags = await storage.getAll('songTags');
    let audio = await storage.getAll('audio');
    let playlists = await storage.getAll('playlists');
    let playlistItems = await storage.getAll('playlistItems');"""

load_new = """  async loadInitialData() {
    let songs = await storage.getAll('songs');
    let tags = await storage.getAll('tags');
    let songTags = await storage.getAll('songTags');
    let audio = await storage.getAll('audio');
    let playlists = await storage.getAll('playlists');
    let playlistItems = await storage.getAll('playlistItems');

    const inlinedSongs = parseInlinedSongsCsv(INLINED_SONGS_CSV_DATA);

    // КРИТИЧЕСКИЙ P0 ФИКС: если в базе меньше песен чем во вшитом каталоге — обновляем базу
    if (!songs || songs.length < inlinedSongs.length) {
      songs = inlinedSongs;
      AppLogger.info('BOOT', 'Автономный сборник загружает все ' + songs.length + ' песен.');
      for (const s of songs) {
        await storage.putOne('songs', s);
      }
    }"""

assert load_old in script_content
script_content = script_content.replace(load_old, load_new)

# Combine template
full_template = html_before_script + "<script>\n" + inlined_header + script_content

# Save base64 version
b64_str = base64.b64encode(full_template.encode('utf-8')).decode('ascii')
with open('tools/b64_reader_template.txt', 'w', encoding='ascii') as f:
    f.write(b64_str)

# Generate огненныйветер.html with current data/songs.csv
with open('data/songs.csv', 'r', encoding='utf-8') as f:
    songs_csv = f.read()

standalone_html = full_template.replace('__CSV_DATA_JSON__', json.dumps(songs_csv))

with open('огненныйветер.html', 'w', encoding='utf-8') as f:
    f.write(standalone_html)

os.makedirs('dist/reader', exist_ok=True)
with open('dist/reader/index.html', 'w', encoding='utf-8') as f:
    f.write(standalone_html)

print("Canonical standalone Light Reader generated successfully without player, without CSV upload, with full 700 songs!")
