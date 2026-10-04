# -*- coding: utf-8 -*-
import json
import base64
import os

with open('index.html', 'r', encoding='utf-8') as f:
    app_html = f.read()

# 1. Update title
app_html = app_html.replace('<title>Огненный Ветер</title>', '<title>Огненный Ветер — Карманный Сборник</title>')

# 2. Hide docked audio player and player tab completely
hide_audio_css = """
    /* LIGHT READER MODE: AUDIO PLAYER HIDDEN */
    #docked-player, .song-audio-bottom-hub, [data-action="trigger-audio-batch-upload"], [data-action="nav-tab"][data-tab="player"] {
      display: none !important;
    }
"""
app_html = app_html.replace('</style>', hide_audio_css + '\n</style>')

# 3. STRICT SETTINGS VIEW FOR LIGHT READER SPA
strict_light_settings_view = """  renderSettingsView(container) {
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

app_html = app_html[:pos_set] + strict_light_settings_view[2:] + app_html[pos_set_end + len('container.appendChild(wrap);\n  }'):]

# 4. External audio/video clickable links in song details view
ext_links_marker = 'topBar.appendChild(paramsWrap);'
ext_links_code = """
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
"""
app_html = app_html.replace(ext_links_marker, ext_links_marker + '\n' + ext_links_code)

# 5. Embed parser and inlined declaration
script_pos = app_html.find('<script>')
assert script_pos != -1

html_before_script = app_html[:script_pos]

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

script_content = app_html[script_pos + len('<script>'):]

old_load = """  async loadInitialData() {
    let songs = await storage.getAll('songs');
    let tags = await storage.getAll('tags');
    let songTags = await storage.getAll('songTags');
    let audio = await storage.getAll('audio');
    let playlists = await storage.getAll('playlists');
    let playlistItems = await storage.getAll('playlistItems');"""

# ROBUST RESEED: If storage has 0 songs or less songs than the inlined catalog, ALWAYS seed from INLINED_SONGS_CSV_DATA!
new_load = """  async loadInitialData() {
    let songs = await storage.getAll('songs');
    let tags = await storage.getAll('tags');
    let songTags = await storage.getAll('songTags');
    let audio = await storage.getAll('audio');
    let playlists = await storage.getAll('playlists');
    let playlistItems = await storage.getAll('playlistItems');

    const inlinedSongs = parseInlinedSongsCsv(INLINED_SONGS_CSV_DATA);

    // Если база пуста или содержит устаревшее число песен — обновляем из вшитой базы
    if (!songs || songs.length < inlinedSongs.length) {
      songs = inlinedSongs;
      AppLogger.info('BOOT', 'Инициализация карманного песенника: ' + songs.length + ' песен.');
      for (const s of songs) {
        await storage.putOne('songs', s);
      }
    }"""

assert old_load in script_content, "old_load not found in script_content"
script_content = script_content.replace(old_load, new_load)

full_reader_template = html_before_script + "<script>\n" + inlined_header + script_content

# Encode clean template into Base64
b64_template = base64.b64encode(full_reader_template.encode('utf-8')).decode('ascii')

with open('tools/b64_reader_template.txt', 'w', encoding='ascii') as f:
    f.write(b64_template)

os.makedirs('dist/reader', exist_ok=True)

with open('data/songs.csv', 'r', encoding='utf-8') as f:
    songs_csv = f.read()

fresh_light_reader = full_reader_template.replace('__CSV_DATA_JSON__', json.dumps(songs_csv))

with open('огненныйветер.html', 'w', encoding='utf-8') as f:
    f.write(fresh_light_reader)

with open('dist/reader/index.html', 'w', encoding='utf-8') as f:
    f.write(fresh_light_reader)

print("Light reader generated with strict settings order and matching action icons!")
