# -*- coding: utf-8 -*-
with open('data/admin.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update renderCatalog table row to have both ✏️ Ред. (22 поля) AND 🎨 Аккорды (интерактивный редактор)
old_catalog_actions = """          <td>
            <button class="btn btn-outline" style="padding: 0.25rem 0.6rem; font-size: 0.8rem;" onclick="openEditModal('${song.id}')">✏️ Ред.</button>
            <button class="btn btn-outline" style="padding: 0.25rem 0.6rem; font-size: 0.8rem; color: #b91c1c;" onclick="deleteSong('${song.id}')">✕</button>
          </td>"""

new_catalog_actions = """          <td style="white-space: nowrap;">
            <button class="btn btn-sm btn-outline" style="padding: 0.25rem 0.5rem; font-size: 0.78rem; background: #fef3c7; border-color: #f59e0b; color: #92400e;" onclick="openSongInVisualEditor('${song.id}')" title="Открыть в интерактивном визуальном редакторе аккордов над текстом">🎨 Аккорды</button>
            <button class="btn btn-sm btn-outline" style="padding: 0.25rem 0.5rem; font-size: 0.78rem;" onclick="openEditModal('${song.id}')" title="Редактировать все 22 поля песни">✏️ Поля</button>
            <button class="btn btn-sm btn-outline" style="padding: 0.25rem 0.45rem; font-size: 0.78rem; color: #b91c1c;" onclick="deleteSong('${song.id}')" title="Удалить песню">✕</button>
          </td>"""

assert old_catalog_actions in text, "old_catalog_actions not found"
text = text.replace(old_catalog_actions, new_catalog_actions)

# 2. Add openSongInVisualEditor function and populate parsedDocxSongs on CSV upload
open_editor_helpers = """
    // =========================================================================
    // ПЕРЕХОД ПЕСНИ ИЗ КАТАЛОГА В ИНТЕРАКТИВНЫЙ РЕДАКТОР АККОРДОВ
    // =========================================================================
    function parseChordProTextToModel(chordProText, songMeta) {
      const lines = (chordProText || '').split(/\\r?\\n/);
      const model = {
        id: songMeta.id || '0001',
        number: songMeta.number || parseInt(songMeta.id, 10) || 1,
        title: songMeta.title || 'Песня',
        key_default: songMeta.key || songMeta.key_default || '',
        capo: songMeta.capo || '',
        tempo: songMeta.tempo || '',
        author: songMeta.author || 'Огненный ветер',
        lines: []
      };

      for (let rawLine of lines) {
        const trimmed = rawLine.trim();
        if (!trimmed) {
          model.lines.push({ kind: 'blank', lyric: '', chords: [] });
          continue;
        }

        if (/^(куплет|припев|бридж|вступление|проигрыш|кода|verse|chorus|bridge|intro|outro)/i.test(trimmed)) {
          const kind = /припев|chorus/i.test(trimmed) ? 'chorus-header' : 'section-header';
          model.lines.push({ kind: kind, lyric: trimmed, chords: [] });
          continue;
        }

        // Parse line with inline [Chord] tokens
        let lyric = '';
        let chords = [];
        let curIdx = 0;
        const regex = /\\[([^\\]]+)\\]/g;
        let match;
        let lastEnd = 0;

        while ((match = regex.exec(rawLine)) !== null) {
          lyric += rawLine.slice(lastEnd, match.index);
          const chordToken = match[1].trim();
          chords.push({
            chord: chordToken,
            charIndex: lyric.length,
            ratio: lyric.length / Math.max(1, rawLine.length),
            confidence: 1.0
          });
          lastEnd = regex.lastIndex;
        }
        lyric += rawLine.slice(lastEnd);

        if (chords.length === 0 && isChordLine(trimmed)) {
          // Pure chord line above
          const tokens = trimmed.split(/\\s+/);
          tokens.forEach((tok, i) => {
            chords.push({
              chord: tok,
              charIndex: i * 8,
              ratio: (i * 8) / Math.max(1, trimmed.length),
              confidence: 0.9
            });
          });
          lyric = '';
        }

        model.lines.push({
          kind: 'lyric',
          lyric: lyric,
          chords: chords
        });
      }

      return model;
    }

    window.openSongInVisualEditor = function(songId) {
      const song = dbSongs.find(s => s.id === songId);
      if (!song) return;

      // 1. Build or retrieve model
      let model = song.rawModel;
      if (!model) {
        const textToParse = song.chordpro || song.body_chordpro || song.lyrics || song.body_plain || '';
        if (textToParse.includes('[')) {
          model = parseChordProTextToModel(textToParse, song);
        } else {
          model = parseRawBlockToSongModel(textToParse, song.id);
          if (model) {
            model.title = song.title;
            model.key_default = song.key || song.key_default || '';
            model.capo = song.capo || '';
            model.tempo = song.tempo || '';
          }
        }
        song.rawModel = model;
      }

      // 2. Ensure song is in parsedDocxSongs list for the sidebar
      if (!parsedDocxSongs.some(s => s.id === song.id)) {
        parsedDocxSongs.unshift(song);
      }
      currentSongIndex = parsedDocxSongs.findIndex(s => s.id === song.id);

      // 3. Switch to Tab 1 (DOCX & OpenSong/ChordPro Студия)
      const tabBtn = document.querySelector('.tab-btn[data-tab="docx-songs"]');
      if (tabBtn) tabBtn.click();

      // 4. Update parsed songs UI list
      renderParsedSongsList();

      // 5. Render song into interactive drag-and-drop editor
      activeSongModel = model;
      undoStack = [{ data: JSON.stringify(activeSongModel), desc: 'Open Song ' + song.title, time: Date.now() }];
      redoStack = [];
      updateHistoryButtonsUI();

      renderInteractiveEditor(activeSongModel);

      // Scroll to editor smoothly
      document.getElementById('interactive-editor')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    };
"""

pos_edit_modal = text.find('window.openEditModal = function')
assert pos_edit_modal != -1, "window.openEditModal not found"
text = text[:pos_edit_modal] + open_editor_helpers + "\n    " + text[pos_edit_modal:]

# 3. Update handleAdminSongsCsvUpload to automatically fill parsedDocxSongs and switch to list
old_upload_end = """        dbSongs = normalizedSongs;
        dbTables.songs = normalizedSongs;
        localStorage.setItem('ov_admin_songs', JSON.stringify(dbSongs));
        localStorage.setItem('ov_admin_songs_table', JSON.stringify(dbSongs));

        saveDb();
        renderCatalog();
        updateTableStatCounts();

        const statusEl = document.getElementById('csv-import-status');
        if (statusEl) {
          statusEl.textContent = `✓ Загружено ${normalizedSongs.length} песен!`;
        }

        alert(`УСПЕШНО!\\n\\nБаза songs.csv успешно импортирована в Data Studio.\\nВсего загружено песен: ${normalizedSongs.length}.\\nРеестр и все 22 поля обновлены.`);"""

new_upload_end = """        dbSongs = normalizedSongs;
        dbTables.songs = normalizedSongs;
        localStorage.setItem('ov_admin_songs', JSON.stringify(dbSongs));
        localStorage.setItem('ov_admin_songs_table', JSON.stringify(dbSongs));

        // Сразу загружаем песни в список визуального редактора Таба 1
        parsedDocxSongs = [...normalizedSongs];
        renderParsedSongsList();

        saveDb();
        renderCatalog();
        updateTableStatCounts();

        const statusEl = document.getElementById('csv-import-status');
        if (statusEl) {
          statusEl.textContent = `✓ Загружено ${normalizedSongs.length} песен!`;
        }

        // Если в списке есть песни — сразу открываем первую в визуальном редакторе!
        if (parsedDocxSongs.length > 0) {
          currentSongIndex = 0;
          openSongInVisualEditor(parsedDocxSongs[0].id);
        }

        alert(`УСПЕШНО!\\n\\nБаза songs.csv (${normalizedSongs.length} песен) загружена!\\nСписок песен открыт прямо перед вами в визуальном редакторе аккордов.`);"""

assert old_upload_end in text, "old_upload_end not found"
text = text.replace(old_upload_end, new_upload_end)

with open('data/admin.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("data/admin.html patched: CSV songs immediately openable in Visual Editor and Catalog!")
