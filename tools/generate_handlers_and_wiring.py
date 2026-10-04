# -*- coding: utf-8 -*-
with open('data/admin.html', 'r', encoding='utf-8') as f:
    text = f.read()

m1 = text.find('// 1. DOCX CHORDS IMPORT EVENT HANDLERS')
m2 = text.find('// 2. DOCX / TXT ID ORDER PARSER')
assert m1 != -1 and m2 != -1

new_handlers = r'''// 1. DOCX CHORDS IMPORT EVENT HANDLERS (ENHANCED GEOMETRIC DP ENGINE)
    // =========================================================================
    const docxDropzone = document.getElementById('docx-dropzone');
    const inputDocxChords = document.getElementById('input-docx-chords');
    let chordsDocxFile = null;

    docxDropzone.addEventListener('click', () => inputDocxChords.click());
    docxDropzone.addEventListener('dragover', (e) => { e.preventDefault(); docxDropzone.classList.add('dragover'); });
    docxDropzone.addEventListener('dragleave', () => docxDropzone.classList.remove('dragover'));
    docxDropzone.addEventListener('drop', (e) => {
      e.preventDefault();
      docxDropzone.classList.remove('dragover');
      if (e.dataTransfer.files.length) handleDocxChordsSelected(e.dataTransfer.files[0]);
    });
    inputDocxChords.addEventListener('change', (e) => {
      if (e.target.files.length) handleDocxChordsSelected(e.target.files[0]);
    });

    function handleDocxChordsSelected(file) {
      chordsDocxFile = file;
      document.getElementById('docx-file-name').textContent = file.name + ' (' + Math.round(file.size / 1024) + ' KB)';
      document.getElementById('btn-parse-docx-chords').disabled = false;
      appendLog(`[Файл выбран] ${file.name}. Нажмите «Запустить точный DP-парсинг».`);
    }

    function appendLog(msg) {
      const log = document.getElementById('docx-log');
      if (log) log.textContent += `\n[${new Date().toLocaleTimeString()}] ${msg}`;
    }

    // Direct Parsing of Pasted Song Text
    document.getElementById('btn-parse-pasted-text')?.addEventListener('click', () => {
      const rawText = document.getElementById('paste-text-input').value;
      if (!rawText.trim()) {
        alert('Пожалуйста, вставьте текст песни в поле ввода.');
        return;
      }
      
      const songModel = parseRawBlockToSongModel(rawText, '0001');
      activeSongModel = songModel;
      parsedDocxSongs = [{
        id: songModel.id,
        number: 1,
        title: songModel.title,
        key_default: songModel.key_default,
        capo: songModel.capo,
        tempo: songModel.tempo,
        body_chordpro: serializeSongToChordPro(songModel),
        body_plain: serializeSongToPlainText(songModel),
        rawModel: songModel
      }];

      renderParsedSongsList();
      renderInteractiveEditor(activeSongModel);
      document.getElementById('btn-apply-docx-songs').disabled = false;
      appendLog(`Успешно распознана вставленная песня: «${songModel.title}» (${songModel.lines.length} строк).`);
    });

    // Realign current song button
    document.getElementById('btn-realign-current-song')?.addEventListener('click', () => {
      if (!activeSongModel) {
        alert('Нет выбранной песни для выравнивания.');
        return;
      }
      // Re-run dynamic programming on all verse lines
      activeSongModel.lines.forEach(line => {
        if (line.lyric && line.chords && line.chords.length > 0) {
          const xs = computeCharXPositions(line.lyric);
          const snaps = buildLyricSnapPoints(line.lyric, xs);
          const chordTokens = line.chords.map(c => ({
            text: c.name,
            x: xs[c.charIndex] || measureTextWidth(line.lyric.substring(0, c.charIndex)),
            rawCol: c.charIndex
          }));
          const newIndices = alignChordsDP(chordTokens, snaps);
          line.chords.forEach((c, idx) => {
            if (newIndices[idx] !== undefined) {
              c.charIndex = newIndices[idx];
              const targetX = xs[c.charIndex] || c.charIndex * 8;
              c.confidence = computeChordConfidence(chordTokens[idx].x, targetX);
            }
          });
        }
      });

      renderInteractiveEditor(activeSongModel);
      alert('Автоматическое перевыравнивание выполнено!');
    });

    // Main Parse Button (DOCX)
    document.getElementById('btn-parse-docx-chords').addEventListener('click', async () => {
      if (!chordsDocxFile) return;
      const log = document.getElementById('docx-log');
      log.textContent = `[${new Date().toLocaleTimeString()}] Распаковка архива DOCX через JSZip...\n`;
      
      try {
        const { songBlocks, allParagraphs } = await extractParagraphsFromDocx(chordsDocxFile);
        log.textContent += `[${new Date().toLocaleTimeString()}] Извлечено ${allParagraphs.length} абзацев. Найдено ${songBlocks.length} секций песен.\n`;
        
        // TOC parsing
        const tocMap = new Map();
        const firstSongIdx = allParagraphs.findIndex(p => /^#\s/.test(p) || /^[0-9]+\.\s+[A-ZА-ЯЁ]/.test(p));
        if (firstSongIdx > 0) {
          const tocLines = allParagraphs.slice(0, firstSongIdx);
          for (const line of tocLines) {
            const m = line.match(/^(\d+)\.\s+(.*?)(?:\s*\[|\s*\^|\s*\(|$)/);
            if (m) {
              const num = parseInt(m[1], 10);
              const title = m[2].trim();
              tocMap.set(normalizeSongTitle(title), num);
            }
          }
          log.textContent += `[${new Date().toLocaleTimeString()}] Оглавление распознано: найдено ${tocMap.size} названий с номерами.\n`;
        }

        parsedDocxSongs = [];

        songBlocks.forEach((block, idx) => {
          if (!block.trim()) return;

          let number = null;
          const numMatch = block.match(/^#?\s*(\d+)\./);
          if (numMatch) {
            number = parseInt(numMatch[1], 10);
          }

          const idStr = number !== null ? String(number).padStart(4, '0') : String(idx + 1).padStart(4, '0');
          const songModel = parseRawBlockToSongModel(block, idStr);
          if (!songModel) return;

          if (number === null) {
            const norm = normalizeSongTitle(songModel.title);
            if (tocMap.has(norm)) {
              number = tocMap.get(norm);
              songModel.id = String(number).padStart(4, '0');
              songModel.number = number;
            }
          }

          const songObj = {
            id: songModel.id,
            number: songModel.number || (idx + 1),
            title: songModel.title,
            key_default: songModel.key_default,
            capo: songModel.capo || '',
            tempo: songModel.tempo || '',
            alt_title: chordsDocxFile.name.replace('.docx', ''),
            body_chordpro: serializeSongToChordPro(songModel),
            body_plain: serializeSongToPlainText(songModel),
            author: 'Огненный ветер',
            album: 'Сборник DOCX',
            rawModel: songModel
          };

          parsedDocxSongs.push(songObj);
        });

        if (parsedDocxSongs.length > 0) {
          activeSongModel = parsedDocxSongs[0].rawModel;
          renderParsedSongsList();
          renderInteractiveEditor(activeSongModel);
          document.getElementById('btn-apply-docx-songs').disabled = false;
          log.textContent += `[Успех] Извлечено и оцифровано ${parsedDocxSongs.length} песен!\nПервая песня загружена в визуальный редактор.`;
        }
      } catch (err) {
        log.textContent += `[ОШИБКА ПАРСИНГА] ${err.message}\n${err.stack}`;
      }
    });

    /**
     * Render the list of parsed songs for 1-click switching
     */
    function renderParsedSongsList() {
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
    }

    // Apply converted songs to general dbSongs catalog
    document.getElementById('btn-apply-docx-songs').addEventListener('click', () => {
      if (parsedDocxSongs.length === 0) return;
      let added = 0;
      let updated = 0;

      // Sync active song edits back
      if (activeSongModel && parsedDocxSongs[currentSongIndex]) {
        parsedDocxSongs[currentSongIndex].title = activeSongModel.title;
        parsedDocxSongs[currentSongIndex].key_default = activeSongModel.key_default;
        parsedDocxSongs[currentSongIndex].capo = activeSongModel.capo;
        parsedDocxSongs[currentSongIndex].tempo = activeSongModel.tempo;
        parsedDocxSongs[currentSongIndex].body_chordpro = serializeSongToChordPro(activeSongModel);
        parsedDocxSongs[currentSongIndex].body_plain = serializeSongToPlainText(activeSongModel);
      }

      parsedDocxSongs.forEach(newSong => {
        const normNew = normalizeSongTitle(newSong.title);
        const existingIdx = dbSongs.findIndex(s => 
          (s.id === newSong.id && s.id !== '0000') || normalizeSongTitle(s.title) === normNew
        );

        if (existingIdx >= 0) {
          dbSongs[existingIdx].body_chordpro = newSong.body_chordpro || dbSongs[existingIdx].body_chordpro;
          dbSongs[existingIdx].body_plain = newSong.body_plain || dbSongs[existingIdx].body_plain;
          if (newSong.key_default) dbSongs[existingIdx].key_default = newSong.key_default;
          if (newSong.capo) dbSongs[existingIdx].capo = newSong.capo;
          if (newSong.tempo) dbSongs[existingIdx].tempo = newSong.tempo;
          updated++;
        } else {
          dbSongs.push(newSong);
          added++;
        }
      });

      saveDb();
      renderCatalog();
      alert(`Слияние успешно завершено!\nОбновлено песен: ${updated}\nДобавлено новых песен: ${added}\nВсего в реестре: ${dbSongs.length}`);
    });

    '''

new_content = text[:m1] + new_handlers + text[m2:]
with open('data/admin.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Handlers successfully updated in admin.html!")
