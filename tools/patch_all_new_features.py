# -*- coding: utf-8 -*-
with open('data/admin.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update Dropzone and Toolbar HTML:
# Add OpenSong import button and folder picker
old_drop_grid = """      <!-- Источники ввода: DOCX или Копипаст текста -->
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem;">
        <div class="dropzone" id="docx-dropzone" style="padding: 1.2rem; min-height: 120px;">
          <input type="file" id="input-docx-chords" accept=".docx" multiple style="display: none;">
          <div style="font-size: 1.8rem; margin-bottom: 0.3rem;">📄</div>
          <strong>Загрузить .docx файл(ы) сборника</strong>
          <p style="color: var(--muted); font-size: 0.78rem; margin-top: 0.2rem;">Распаковка через JSZip, извлечение стилей w:b и геометрических отступов</p>
          <span id="docx-file-name" style="color: var(--info); font-size: 0.82rem; font-weight: bold; margin-top: 0.3rem; display: block;">Файл не выбран</span>
        </div>

        <div style="border: 1px dashed var(--border); border-radius: 6px; padding: 0.8rem; background: #fafafa; display: flex; flex-direction: column;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem;">
            <strong style="font-size: 0.85rem;">📝 Или вставьте текст песни:</strong>
            <button class="btn btn-sm btn-outline" id="btn-parse-pasted-text">Распознать вставку</button>
          </div>
          <textarea id="paste-text-input" placeholder="Вставьте сюда песню (текст с аккордами сверху, формат ChordPro [Am] или OpenSong с точкой .Am)..." style="flex: 1; min-height: 65px; font-family: monospace; font-size: 0.78rem; padding: 0.4rem; border: 1px solid var(--border); border-radius: 4px; resize: none;"></textarea>
        </div>
      </div>"""

new_drop_grid = """      <!-- Источники ввода: DOCX, OpenSong файлы и Копипаст -->
      <div style="display: grid; grid-template-columns: 1.2fr 1.2fr 1fr; gap: 0.8rem; margin-bottom: 1rem;">
        <div class="dropzone" id="docx-dropzone" style="padding: 1rem; min-height: 110px;">
          <input type="file" id="input-docx-chords" accept=".docx" multiple style="display: none;">
          <div style="font-size: 1.6rem; margin-bottom: 0.2rem;">📄</div>
          <strong style="font-size: 0.88rem;">1. Загрузить DOCX файл(ы)</strong>
          <p style="color: var(--muted); font-size: 0.75rem; margin-top: 0.2rem;">Автораспознавание сеток аккордов и оглавления</p>
          <span id="docx-file-name" style="color: var(--info); font-size: 0.8rem; font-weight: bold; margin-top: 0.2rem; display: block;">Файл не выбран</span>
        </div>

        <div class="dropzone" id="opensong-dropzone" style="padding: 1rem; min-height: 110px; border-color: #0284c7; background: #f0f9ff;">
          <input type="file" id="input-opensong-files" accept=".xml,.opensong,text/xml" multiple style="display: none;">
          <input type="file" id="input-opensong-folder" webkitdirectory directory multiple style="display: none;">
          <div style="font-size: 1.6rem; margin-bottom: 0.2rem;">🎼</div>
          <strong style="font-size: 0.88rem; color: #0369a1;">2. Импорт OpenSong XML</strong>
          <p style="color: var(--muted); font-size: 0.75rem; margin-top: 0.2rem;">Загрузить файл(ы) или указать локальную папку</p>
          <div style="display: flex; gap: 0.4rem; justify-content: center; margin-top: 0.4rem;">
            <button type="button" class="btn btn-sm btn-outline" id="btn-pick-opensong-files" style="padding: 0.2rem 0.5rem; font-size: 0.75rem;">Файлы .xml</button>
            <button type="button" class="btn btn-sm btn-outline" id="btn-pick-opensong-folder" style="padding: 0.2rem 0.5rem; font-size: 0.75rem;">📁 Папка opensong</button>
          </div>
          <span id="opensong-status-badge" style="color: #0369a1; font-size: 0.78rem; font-weight: bold; margin-top: 0.2rem; display: block;">Загружено файлов: 0</span>
        </div>

        <div style="border: 1px dashed var(--border); border-radius: 6px; padding: 0.75rem; background: #fafafa; display: flex; flex-direction: column;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.3rem;">
            <strong style="font-size: 0.82rem;">3. Текст / Буфер:</strong>
            <button type="button" class="btn btn-sm btn-outline" id="btn-parse-pasted-text" style="padding: 0.2rem 0.5rem; font-size: 0.75rem;">Распознать</button>
          </div>
          <textarea id="paste-text-input" placeholder="Вставьте песню (аккорды над текстом или [Am])..." style="flex: 1; min-height: 55px; font-family: monospace; font-size: 0.75rem; padding: 0.3rem; border: 1px solid var(--border); border-radius: 4px; resize: none;"></textarea>
        </div>
      </div>"""

assert old_drop_grid in text, "old_drop_grid not matched"
text = text.replace(old_drop_grid, new_drop_grid)

# 2. Add Undo / Redo buttons to converter-toolbar
old_toolbar = """      <!-- Панель управления и экспорта -->
      <div class="converter-toolbar">
        <button class="btn" id="btn-parse-docx-chords" disabled>⚡ 1. Запустить точный DP-парсинг</button>
        <button class="btn btn-outline" id="btn-realign-current-song" title="Автоматически пересчитать привязку аккордов для текущей песни">⟲ Автовыравнивание</button>
        <div style="height: 24px; width: 1px; background: #cbd5e1; margin: 0 0.3rem;"></div>"""

new_toolbar = """      <!-- Панель управления и экспорта -->
      <div class="converter-toolbar">
        <button type="button" class="btn" id="btn-parse-docx-chords" disabled>⚡ 1. Запустить точный DP-парсинг</button>
        <button type="button" class="btn btn-outline" id="btn-realign-current-song" title="Автоматически пересчитать привязку аккордов для текущей песни">⟲ Автовыравнивание</button>
        
        <!-- Undo / Redo controls (до 50 операций) -->
        <div style="height: 24px; width: 1px; background: #cbd5e1; margin: 0 0.3rem;"></div>
        <button type="button" class="btn btn-outline" id="btn-editor-undo" title="Отменить последнее действие (Ctrl+Z)" disabled>↶ Отмена (Undo)</button>
        <button type="button" class="btn btn-outline" id="btn-editor-redo" title="Повторить отменённое действие (Ctrl+Y)" disabled>↷ Повтор (Redo)</button>
        <span id="history-steps-badge" style="font-size:0.75rem; color:var(--muted); font-weight:600;">0/50</span>

        <div style="height: 24px; width: 1px; background: #cbd5e1; margin: 0 0.3rem;"></div>"""

assert old_toolbar in text, "old_toolbar not matched"
text = text.replace(old_toolbar, new_toolbar)

# 3. Add CSS for processed green song badge and fast tabs
css_ext = """
    /* Processed OpenSong file badge indicator */
    .song-list-item.has-saved-xml {
      background: #f0fdf4 !important;
      border-left: 4px solid #16a34a !important;
    }
    .song-list-item.has-saved-xml:hover {
      background: #dcfce7 !important;
    }
    .badge-xml-exists {
      display: inline-flex;
      align-items: center;
      gap: 0.2rem;
      font-size: 0.7rem;
      font-weight: 700;
      color: #15803d;
      background: #bbf7d0;
      padding: 0.1rem 0.45rem;
      border-radius: 4px;
      margin-left: 0.4rem;
    }
"""

if '/* Processed OpenSong file badge indicator */' not in text:
    text = text.replace('</style>', css_ext + '\n</style>', 1)

# 4. Inject Undo/Redo Engine, Fast Tabs, and OpenSong Importer in JS
js_injection = r"""
    // =========================================================================
    // DEEP HISTORY (UNDO / REDO UP TO 50 STATES)
    // =========================================================================
    const MAX_HISTORY_STATES = 50;
    let undoStack = [];
    let redoStack = [];
    let isExecutingHistoryAction = false;

    function saveEditorState(description = '') {
      if (!activeSongModel || isExecutingHistoryAction) return;
      const snapshot = JSON.stringify(activeSongModel);
      // Avoid duplicate consecutive snapshots
      if (undoStack.length > 0 && undoStack[undoStack.length - 1].data === snapshot) return;
      
      undoStack.push({ data: snapshot, desc: description, time: Date.now() });
      if (undoStack.length > MAX_HISTORY_STATES) undoStack.shift();
      redoStack = []; // Clear forward history on new edit
      updateHistoryButtonsUI();
    }

    function performUndo() {
      if (undoStack.length <= 1) return;
      const currentState = undoStack.pop();
      redoStack.push(currentState);

      const prevState = undoStack[undoStack.length - 1];
      isExecutingHistoryAction = true;
      try {
        activeSongModel = JSON.parse(prevState.data);
        if (parsedDocxSongs && parsedDocxSongs[currentSongIndex]) {
          parsedDocxSongs[currentSongIndex].rawModel = activeSongModel;
        }
        renderInteractiveEditor(activeSongModel);
        updateAllLivePreviews();
      } finally {
        isExecutingHistoryAction = false;
      }
      updateHistoryButtonsUI();
    }

    function performRedo() {
      if (redoStack.length === 0) return;
      const nextState = redoStack.pop();
      undoStack.push(nextState);

      isExecutingHistoryAction = true;
      try {
        activeSongModel = JSON.parse(nextState.data);
        if (parsedDocxSongs && parsedDocxSongs[currentSongIndex]) {
          parsedDocxSongs[currentSongIndex].rawModel = activeSongModel;
        }
        renderInteractiveEditor(activeSongModel);
        updateAllLivePreviews();
      } finally {
        isExecutingHistoryAction = false;
      }
      updateHistoryButtonsUI();
    }

    function updateHistoryButtonsUI() {
      const btnUndo = document.getElementById('btn-editor-undo');
      const btnRedo = document.getElementById('btn-editor-redo');
      const badge = document.getElementById('history-steps-badge');
      if (btnUndo) btnUndo.disabled = (undoStack.length <= 1);
      if (btnRedo) btnRedo.disabled = (redoStack.length === 0);
      if (badge) badge.textContent = `${Math.max(0, undoStack.length - 1)}/50`;
    }

    // Keyboard Shortcuts: Ctrl+Z (Undo) and Ctrl+Y / Ctrl+Shift+Z (Redo)
    window.addEventListener('keydown', (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'z') {
        if (e.shiftKey) {
          e.preventDefault();
          performRedo();
        } else {
          e.preventDefault();
          performUndo();
        }
      } else if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'y') {
        e.preventDefault();
        performRedo();
      }
    });

    document.getElementById('btn-editor-undo')?.addEventListener('click', performUndo);
    document.getElementById('btn-editor-redo')?.addEventListener('click', performRedo);

    // =========================================================================
    // REGISTRY OF PROCESSED OPENSONG XML FILES
    // (Local storage & folder scanning: songs with matching normalized 4-digit ID glow GREEN)
    // =========================================================================
    let processedOpenSongMap = new Map(); // normalizedId -> filename/title

    function loadKnownOpenSongFiles() {
      try {
        const stored = localStorage.getItem('ov_processed_opensong_ids');
        if (stored) {
          const arr = JSON.parse(stored);
          arr.forEach(item => processedOpenSongMap.set(String(item.id).padStart(4, '0'), item.name));
        }
      } catch (e) {
        console.warn('Error loading known opensong registry:', e);
      }
    }

    function recordProcessedOpenSong(idStr, nameStr) {
      const norm = String(idStr).padStart(4, '0');
      processedOpenSongMap.set(norm, nameStr);
      try {
        const arr = [];
        processedOpenSongMap.forEach((name, id) => arr.push({ id, name }));
        localStorage.setItem('ov_processed_opensong_ids', JSON.stringify(arr));
      } catch (e) {}
      renderParsedSongsList();
    }

    // Preload known registry on startup
    loadKnownOpenSongFiles();

    // =========================================================================
    // OPENGSONG XML IMPORT ENGINE (Single or Multiple files / Folder)
    // =========================================================================
    const btnPickFiles = document.getElementById('btn-pick-opensong-files');
    const btnPickFolder = document.getElementById('btn-pick-opensong-folder');
    const inputOpenSongFiles = document.getElementById('input-opensong-files');
    const inputOpenSongFolder = document.getElementById('input-opensong-folder');
    const opensongDropzone = document.getElementById('opensong-dropzone');

    btnPickFiles?.addEventListener('click', (e) => { e.stopPropagation(); inputOpenSongFiles.click(); });
    btnPickFolder?.addEventListener('click', (e) => { e.stopPropagation(); inputOpenSongFolder.click(); });
    opensongDropzone?.addEventListener('click', () => inputOpenSongFiles.click());

    opensongDropzone?.addEventListener('dragover', (e) => { e.preventDefault(); opensongDropzone.classList.add('dragover'); });
    opensongDropzone?.addEventListener('dragleave', () => opensongDropzone.classList.remove('dragover'));
    opensongDropzone?.addEventListener('drop', async (e) => {
      e.preventDefault();
      opensongDropzone.classList.remove('dragover');
      if (e.dataTransfer.files.length) handleOpenSongFilesBatch(Array.from(e.dataTransfer.files));
    });

    inputOpenSongFiles?.addEventListener('change', (e) => {
      if (e.target.files.length) handleOpenSongFilesBatch(Array.from(e.target.files));
    });
    inputOpenSongFolder?.addEventListener('change', (e) => {
      if (e.target.files.length) handleOpenSongFilesBatch(Array.from(e.target.files));
    });

    /**
     * Batch import OpenSong XML files
     */
    async function handleOpenSongFilesBatch(files) {
      const xmlFiles = files.filter(f => f.name.endsWith('.xml') || f.name.endsWith('.opensong') || f.type.includes('xml'));
      if (xmlFiles.length === 0) {
        alert('В выбранных файлах не найдено документов OpenSong (.xml).');
        return;
      }

      appendLog(`[OpenSong Импорт] Обработка ${xmlFiles.length} файлов...`);
      let loadedCount = 0;

      for (const file of xmlFiles) {
        try {
          const text = await file.text();
          // Extract normalized ID from filename: "0482_Белый снег.xml" or tag
          let idMatch = file.name.match(/^(\d{1,4})/);
          let idStr = idMatch ? String(idMatch[1]).padStart(4, '0') : '';

          const parser = new DOMParser();
          const xmlDoc = parser.parseFromString(text, 'text/xml');
          const title = (xmlDoc.querySelector('title')?.textContent || file.name.replace(/\.[^.]+$/, '')).trim();
          const author = (xmlDoc.querySelector('author')?.textContent || 'Огненный ветер').trim();
          const key_line = (xmlDoc.querySelector('key')?.textContent || '').trim();
          const capo = (xmlDoc.querySelector('capo')?.textContent || '').trim();
          const tempo = (xmlDoc.querySelector('tempo')?.textContent || '').trim();
          const lyricsBody = xmlDoc.querySelector('lyrics')?.textContent || '';

          if (!idStr) {
            // Check if title or db has number
            const normTitle = normalizeSongTitle(title);
            const foundInDb = dbSongs.find(s => normalizeSongTitle(s.title) === normTitle);
            if (foundInDb) idStr = foundInDb.id;
            else idStr = String(parsedDocxSongs.length + 1).padStart(4, '0');
          }

          // Register in processed map
          recordProcessedOpenSong(idStr, file.name);

          // Build song model from OpenSong lyrics
          const songModel = {
            id: idStr,
            number: parseInt(idStr, 10) || (parsedDocxSongs.length + 1),
            title: title,
            key_default: key_line,
            capo: capo,
            tempo: tempo,
            author: author,
            album: 'OpenSong XML',
            lines: []
          };

          // Parse lyrics into canonical lines
          const rawLines = lyricsBody.split(/\r?\n/);
          let lIdx = 0;
          while (lIdx < rawLines.length) {
            const curL = rawLines[lIdx];
            if (curL.startsWith('.')) {
              const chordLine = curL.substring(1);
              const nextL = rawLines[lIdx + 1];
              let lyricStr = '';
              if (nextL !== undefined && !nextL.startsWith('.') && !nextL.startsWith('[')) {
                lyricStr = nextL.startsWith(' ') ? nextL.substring(1) : nextL;
                lIdx += 2;
              } else {
                lIdx += 1;
              }

              const chords = [];
              const regex = /\S+/g;
              let m;
              while ((m = regex.exec(chordLine)) !== null) {
                chords.push({
                  name: m[0],
                  charIndex: Math.max(0, m.index),
                  confidence: 1.0,
                  manual: true
                });
              }

              songModel.lines.push({ kind: 'verse', lyric: lyricStr, chords });
            } else if (curL.startsWith('[')) {
              const sec = curL.toLowerCase();
              const kind = sec.includes('c') ? 'chorus' : (sec.includes('b') ? 'bridge' : 'verse');
              songModel.lines.push({ kind, lyric: curL, chords: [] });
              lIdx++;
            } else if (!curL.trim()) {
              songModel.lines.push({ kind: 'blank', lyric: '', chords: [] });
              lIdx++;
            } else {
              const lyricStr = curL.startsWith(' ') ? curL.substring(1) : curL;
              songModel.lines.push({ kind: 'verse', lyric: lyricStr, chords: [] });
              lIdx++;
            }
          }

          parsedDocxSongs.push({
            id: idStr,
            number: songModel.number,
            title: songModel.title,
            key_default: songModel.key_default,
            capo: songModel.capo,
            tempo: songModel.tempo,
            alt_title: file.name,
            body_chordpro: serializeSongToChordPro(songModel),
            body_plain: serializeSongToPlainText(songModel),
            rawModel: songModel
          });

          loadedCount++;
        } catch (err) {
          console.warn('Error parsing opensong file:', file.name, err);
        }
      }

      const statusBadge = document.getElementById('opensong-status-badge');
      if (statusBadge) statusBadge.textContent = `Загружено файлов: ${processedOpenSongMap.size}`;

      if (parsedDocxSongs.length > 0) {
        currentSongIndex = parsedDocxSongs.length - loadedCount;
        activeSongModel = parsedDocxSongs[currentSongIndex].rawModel;
        undoStack = [{ data: JSON.stringify(activeSongModel), desc: 'Initial OpenSong Load', time: Date.now() }];
        redoStack = [];
        updateHistoryButtonsUI();
        renderParsedSongsList();
        renderInteractiveEditor(activeSongModel);
        document.getElementById('btn-apply-docx-songs').disabled = false;
      }

      appendLog(`[Успех] Загружено ${loadedCount} песен OpenSong! Песни с существующим XML подсвечены зелёным цветом.`);
      alert(`Успешно загружено ${loadedCount} файлов OpenSong!`);
    }
"""

if 'DEEP HISTORY (UNDO / REDO' not in text:
    # Inject before // 1. DOCX CHORDS IMPORT EVENT HANDLERS
    m_inj = text.find('// 1. DOCX CHORDS IMPORT EVENT HANDLERS')
    assert m_inj != -1, "Target insertion point not found"
    text = text[:m_inj] + js_injection + '\n\n    ' + text[m_inj:]

# 5. Update renderParsedSongsList to display green badge if processed OpenSong exists
old_render_list = """    function renderParsedSongsList() {
      const container = document.getElementById('docx-parsed-songs-container');
      const list = document.getElementById('parsed-songs-list');
      const countEl = document.getElementById('parsed-songs-count');
      if (!container || !list) return;

      container.style.display = 'block';
      countEl.textContent = parsedDocxSongs.length;
      list.innerHTML = '';

      parsedDocxSongs.forEach((song, idx) => {
        const item = document.createElement('div');
        item.className = 'song-list-item' + (idx === currentSongIndex ? ' active' : '');
        item.innerHTML = `
          <div>
            <strong>${song.id}. ${song.title}</strong>
            <span style="font-size:0.75rem; color:var(--muted); margin-left:0.5rem;">${song.key_default ? 'Тон: ' + song.key_default : ''} ${song.capo ? 'Капо: ' + song.capo : ''}</span>
          </div>
          <span style="font-size:0.72rem; color:var(--info);">Править ➔</span>
        `;

        item.addEventListener('click', () => {
          currentSongIndex = idx;
          document.querySelectorAll('.song-list-item').forEach(el => el.classList.remove('active'));
          item.classList.add('active');

          if (song.rawModel) {
            activeSongModel = song.rawModel;
          } else {
            activeSongModel = parseRawBlockToSongModel(song.body_chordpro, song.id);
            song.rawModel = activeSongModel;
          }
          renderInteractiveEditor(activeSongModel);
        });

        list.appendChild(item);
      });
    }"""

new_render_list = """    function renderParsedSongsList() {
      const container = document.getElementById('docx-parsed-songs-container');
      const list = document.getElementById('parsed-songs-list');
      const countEl = document.getElementById('parsed-songs-count');
      if (!container || !list) return;

      container.style.display = 'block';
      countEl.textContent = parsedDocxSongs.length;
      list.innerHTML = '';

      parsedDocxSongs.forEach((song, idx) => {
        const normId = String(song.id || idx + 1).padStart(4, '0');
        const hasSavedXml = processedOpenSongMap.has(normId);

        const item = document.createElement('div');
        item.className = 'song-list-item' + (idx === currentSongIndex ? ' active' : '') + (hasSavedXml ? ' has-saved-xml' : '');
        item.innerHTML = `
          <div style="display: flex; align-items: center; gap: 0.3rem;">
            <strong>${normId}. ${song.title}</strong>
            <span style="font-size:0.75rem; color:var(--muted); margin-left:0.3rem;">${song.key_default ? 'Тон: ' + song.key_default : ''} ${song.capo ? 'Капо: ' + song.capo : ''}</span>
            ${hasSavedXml ? '<span class="badge-xml-exists" title="Песня уже оцифрована и сохранена в OpenSong XML">✓ OpenSong</span>' : ''}
          </div>
          <span style="font-size:0.72rem; color:var(--info);">Править ➔</span>
        `;

        item.addEventListener('click', () => {
          currentSongIndex = idx;
          document.querySelectorAll('.song-list-item').forEach(el => el.classList.remove('active'));
          item.classList.add('active');

          if (song.rawModel) {
            activeSongModel = song.rawModel;
          } else {
            activeSongModel = parseRawBlockToSongModel(song.body_chordpro, song.id);
            song.rawModel = activeSongModel;
          }

          // Reset history for selected song
          undoStack = [{ data: JSON.stringify(activeSongModel), desc: 'Open Song', time: Date.now() }];
          redoStack = [];
          updateHistoryButtonsUI();

          renderInteractiveEditor(activeSongModel);
        });

        list.appendChild(item);
      });
    }"""

assert old_render_list in text, "old_render_list not matched"
text = text.replace(old_render_list, new_render_list)

# 6. Mark song as processed when exported to OpenSong XML
old_export_xml_handler = "downloadTextFile(xml, filename, 'application/xml;charset=utf-8;');"
new_export_xml_handler = "downloadTextFile(xml, filename, 'application/xml;charset=utf-8;');\n      recordProcessedOpenSong(normId, filename);"
assert old_export_xml_handler in text, "old_export_xml_handler not matched"
text = text.replace(old_export_xml_handler, new_export_xml_handler)

# 7. In setupChordDrag and interactive editor, record history state on changes
old_chip_drag_finish = """          // Re-render editor and live preview
          renderInteractiveEditor(song);
          updateAllLivePreviews();"""

new_chip_drag_finish = """          saveEditorState('Move Chord');
          renderInteractiveEditor(song);
          updateAllLivePreviews();"""

assert old_chip_drag_finish in text, "old_chip_drag_finish not matched"
text = text.replace(old_chip_drag_finish, new_chip_drag_finish)

with open('data/admin.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("All requested features successfully patched in data/admin.html!")
