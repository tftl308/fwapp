# -*- coding: utf-8 -*-
import sys

editor_and_ui_code = r'''
    // =========================================================================
    // PARSED SONGS STORE & ACTIVE SONG STATE
    // =========================================================================
    let activeSongModel = null;
    let currentSongIndex = 0;

    /**
     * Convert raw text blocks into the rich canonical Song Model
     */
    function parseRawBlockToSongModel(textBlock, defaultId = '0001') {
      const rawLines = textBlock.split(/\r?\n/);
      if (!rawLines.length) return null;

      let title = 'Без названия';
      let key = '';
      let capo = '';
      let tempo = '';
      let headerLinesCount = 0;

      // Extract title and metadata from leading lines
      for (let i = 0; i < rawLines.length; i++) {
        const l = rawLines[i].trim();
        if (!l) continue;
        if (/^#?\s*\d*\.?\s*[A-ZА-ЯЁ]/.test(l) && title === 'Без названия') {
          title = cleanSongTitle(l);
          capo = extractCapo(l) || '';
          headerLinesCount = i + 1;
          break;
        }
      }

      const song = {
        id: defaultId,
        number: parseInt(defaultId, 10) || 1,
        title: title,
        key_default: key,
        capo: capo,
        tempo: tempo,
        author: 'Огненный ветер',
        album: 'Сборник DOCX',
        lines: []
      };

      const bodyLines = rawLines.slice(headerLinesCount);
      let i = 0;

      while (i < bodyLines.length) {
        const currentLine = bodyLines[i];
        const trimmed = currentLine.trim();

        if (!trimmed) {
          song.lines.push({ kind: 'blank', lyric: '', chords: [] });
          i++;
          continue;
        }

        // Section markers check
        if (/^(куплет|припев|бридж|вступление|проигрыш|кода|verse|chorus|bridge|intro|outro)/i.test(trimmed)) {
          const kind = /припев|chorus/i.test(trimmed) ? 'chorus' : (/бридж|bridge/i.test(trimmed) ? 'bridge' : 'verse');
          song.lines.push({ kind: kind, lyric: trimmed, chords: [] });
          i++;
          continue;
        }

        // Check if line contains chords
        if (isChordLine(trimmed)) {
          // Tokenize chords and their character offsets
          const chordTokens = [];
          const regex = /\S+/g;
          let match;
          while ((match = regex.exec(currentLine)) !== null) {
            const chordName = match[0].replace(/[\*\*\(\)\[\]]/g, '');
            // Calculate proportional X position in Times New Roman
            const leadingSubstr = currentLine.substring(0, match.index);
            const xPos = measureTextWidth(leadingSubstr);
            chordTokens.push({ text: chordName, x: xPos, rawCol: match.index });
          }

          // Check next line: is it the corresponding lyric line?
          const nextLine = bodyLines[i + 1];
          if (nextLine !== undefined && !isChordLine(nextLine.trim())) {
            const lyricText = nextLine;
            const xs = computeCharXPositions(lyricText);
            const snaps = buildLyricSnapPoints(lyricText, xs);
            const assignedCharIndices = alignChordsDP(chordTokens, snaps);

            const chordsList = chordTokens.map((t, idx) => {
              const charIdx = assignedCharIndices[idx] !== undefined ? assignedCharIndices[idx] : t.rawCol;
              const targetX = xs[charIdx] || t.x;
              const conf = computeChordConfidence(t.x, targetX);
              return {
                name: t.text,
                charIndex: charIdx,
                confidence: conf,
                manual: false
              };
            });

            song.lines.push({
              kind: 'verse',
              lyric: lyricText,
              chords: chordsList
            });

            i += 2; // Handled chord + lyric pair
            continue;
          } else {
            // Chord-only line (e.g. Intro or Solo)
            const chordsList = chordTokens.map(t => ({
              name: t.text,
              charIndex: t.rawCol,
              confidence: 0.9,
              manual: false
            }));

            song.lines.push({
              kind: 'instrumental',
              lyric: '',
              chords: chordsList
            });
            i++;
            continue;
          }
        } else if (trimmed.includes('[') && trimmed.includes(']')) {
          // Line already in ChordPro format: [Am]Белый снег
          const chordsList = [];
          let cleanLyric = '';
          let cIndex = 0;
          const cpRegex = /\[(.*?)\]|([^\[]+)/g;
          let cpMatch;

          while ((cpMatch = cpRegex.exec(currentLine)) !== null) {
            if (cpMatch[1]) {
              chordsList.push({
                name: cpMatch[1],
                charIndex: cleanLyric.length,
                confidence: 1.0,
                manual: true
              });
            } else if (cpMatch[2]) {
              cleanLyric += cpMatch[2];
            }
          }

          song.lines.push({
            kind: 'verse',
            lyric: cleanLyric,
            chords: chordsList
          });
          i++;
          continue;
        } else {
          // Regular text line without chords
          song.lines.push({
            kind: 'verse',
            lyric: currentLine,
            chords: []
          });
          i++;
        }
      }

      // Infer default key from the very first chord found
      if (!song.key_default) {
        for (const l of song.lines) {
          if (l.chords && l.chords.length > 0) {
            const firstC = l.chords[0].name;
            song.key_default = (firstC === 'Dm' || firstC.startsWith('Dm/')) ? 'Am' : firstC;
            break;
          }
        }
      }

      return song;
    }

    // =========================================================================
    // VISUAL DOM DRAG-AND-DROP EDITOR IMPLEMENTATION
    // =========================================================================

    function renderInteractiveEditor(song) {
      const container = document.getElementById('interactive-editor');
      if (!container) return;
      if (!song) {
        container.innerHTML = '<div style="text-align: center; color: var(--muted); padding: 3rem 1rem;">Нет выбранной песни для редактирования.</div>';
        return;
      }

      container.innerHTML = '';

      // Meta header form
      const metaDiv = document.createElement('div');
      metaDiv.className = 'editor-song-meta';
      metaDiv.innerHTML = `
        <div>
          <label style="font-size: 0.72rem; color: var(--muted); display: block;">Название песни</label>
          <input type="text" id="edit-song-title" value="${song.title || ''}" style="width: 100%; font-size: 0.85rem; font-weight: bold; padding: 0.2rem 0.4rem; border: 1px solid var(--border); border-radius: 4px;">
        </div>
        <div>
          <label style="font-size: 0.72rem; color: var(--muted); display: block;">Тональность</label>
          <input type="text" id="edit-song-key" value="${song.key_default || ''}" style="width: 100%; font-size: 0.85rem; padding: 0.2rem 0.4rem; border: 1px solid var(--border); border-radius: 4px;">
        </div>
        <div>
          <label style="font-size: 0.72rem; color: var(--muted); display: block;">Каподастр</label>
          <input type="text" id="edit-song-capo" value="${song.capo || ''}" style="width: 100%; font-size: 0.85rem; padding: 0.2rem 0.4rem; border: 1px solid var(--border); border-radius: 4px;">
        </div>
        <div>
          <label style="font-size: 0.72rem; color: var(--muted); display: block;">Темп (BPM)</label>
          <input type="text" id="edit-song-tempo" value="${song.tempo || ''}" style="width: 100%; font-size: 0.85rem; padding: 0.2rem 0.4rem; border: 1px solid var(--border); border-radius: 4px;">
        </div>
      `;
      container.appendChild(metaDiv);

      // Bind meta inputs
      document.getElementById('edit-song-title').addEventListener('input', (e) => { song.title = e.target.value; updateAllLivePreviews(); });
      document.getElementById('edit-song-key').addEventListener('input', (e) => { song.key_default = e.target.value; updateAllLivePreviews(); });
      document.getElementById('edit-song-capo').addEventListener('input', (e) => { song.capo = e.target.value; updateAllLivePreviews(); });
      document.getElementById('edit-song-tempo').addEventListener('input', (e) => { song.tempo = e.target.value; updateAllLivePreviews(); });

      // Render song lines
      song.lines.forEach((line, lineIndex) => {
        if (!line.lyric && (!line.chords || line.chords.length === 0)) return;

        const lineBlock = document.createElement('div');
        lineBlock.className = 'editor-line-block';

        const lineHeader = document.createElement('div');
        lineHeader.className = 'editor-line-header';
        lineHeader.innerHTML = `<span>Строка ${lineIndex + 1} (${line.kind})</span> <span style="font-size: 0.7rem; color: #94a3b8;">${line.chords ? line.chords.length : 0} аккордов</span>`;
        lineBlock.appendChild(lineHeader);

        const trackDiv = document.createElement('div');
        trackDiv.className = 'editor-line-track';
        trackDiv.dataset.lineIndex = lineIndex;

        const textRow = document.createElement('div');
        textRow.className = 'editor-text-row';

        const chars = Array.from(line.lyric || ' ');
        chars.forEach((char, charIdx) => {
          const span = document.createElement('span');
          span.className = 'char-cell';
          span.dataset.charIndex = charIdx;
          span.dataset.lineIndex = lineIndex;
          span.textContent = char;

          // Click on letter to quickly add chord
          span.addEventListener('dblclick', () => {
            const chordName = prompt('Введите имя аккорда над этим слогом (например, Am, G7, F#m):', 'Am');
            if (chordName && chordName.trim()) {
              if (!line.chords) line.chords = [];
              line.chords.push({
                name: chordName.trim(),
                charIndex: charIdx,
                confidence: 1.0,
                manual: true
              });
              renderInteractiveEditor(song);
              updateAllLivePreviews();
            }
          });

          textRow.appendChild(span);
        });

        trackDiv.appendChild(textRow);

        // Position Chords above text row
        if (line.chords && line.chords.length > 0) {
          line.chords.forEach((chord, chordIdx) => {
            const chip = document.createElement('div');
            chip.className = 'chord-chip';
            chip.dataset.chordIndex = chordIdx;
            chip.dataset.lineIndex = lineIndex;

            // Confidence coloring
            if (chord.confidence >= 0.8) chip.classList.add('conf-high');
            else if (chord.confidence >= 0.5) chip.classList.add('conf-med');
            else chip.classList.add('conf-low');

            chip.innerHTML = `<span>${chord.name}</span><span class="btn-chip-del" title="Удалить аккорд">×</span>`;

            // Delete chord handler
            chip.querySelector('.btn-chip-del').addEventListener('click', (e) => {
              e.stopPropagation();
              line.chords.splice(chordIdx, 1);
              renderInteractiveEditor(song);
              updateAllLivePreviews();
            });

            // Edit chord name on click
            chip.querySelector('span').addEventListener('click', (e) => {
              e.stopPropagation();
              const newName = prompt('Изменить аккорд:', chord.name);
              if (newName && newName.trim()) {
                chord.name = newName.trim();
                chord.manual = true;
                renderInteractiveEditor(song);
                updateAllLivePreviews();
              }
            });

            // Make Draggable
            setupChordDrag(chip, chord, line, trackDiv, textRow, song);

            trackDiv.appendChild(chip);
          });
        }

        lineBlock.appendChild(trackDiv);
        container.appendChild(lineBlock);
      });

      // Align chip positions after DOM layout render
      requestAnimationFrame(() => positionAllChipsInEditor());
      updateQualityConfidenceBadges();
      updateAllLivePreviews();
    }

    /**
     * Compute horizontal pixel coordinates for each chord chip based on target char cell rect
     */
    function positionAllChipsInEditor() {
      const tracks = document.querySelectorAll('.editor-line-track');
      tracks.forEach(track => {
        const lineIdx = parseInt(track.dataset.lineIndex, 10);
        const textRow = track.querySelector('.editor-text-row');
        if (!textRow) return;

        const charCells = textRow.querySelectorAll('.char-cell');
        const chips = track.querySelectorAll('.chord-chip');

        chips.forEach(chip => {
          const chordIdx = parseInt(chip.dataset.chordIndex, 10);
          const line = activeSongModel.lines[lineIdx];
          if (!line || !line.chords || !line.chords[chordIdx]) return;
          const chord = line.chords[chordIdx];

          const targetChar = charCells[chord.charIndex];
          if (targetChar) {
            const charRect = targetChar.getBoundingClientRect();
            const trackRect = track.getBoundingClientRect();
            const leftOffset = (charRect.left - trackRect.left) + (charRect.width / 2);
            chip.style.left = `${Math.max(12, leftOffset)}px`;
          } else {
            // Position at end of line
            chip.style.left = `${textRow.offsetWidth + 10}px`;
          }
        });
      });
    }

    /**
     * Setup drag-and-drop interaction with magnetic syllable snapping
     */
    function setupChordDrag(chip, chord, line, trackDiv, textRow, song) {
      let isDragging = false;
      let startX = 0;
      let initialLeft = 0;

      chip.addEventListener('mousedown', (e) => {
        if (e.target.classList.contains('btn-chip-del')) return;
        isDragging = true;
        startX = e.clientX;
        initialLeft = parseFloat(chip.style.left) || 20;
        chip.classList.add('selected');
        e.preventDefault();

        const charCells = Array.from(textRow.querySelectorAll('.char-cell'));

        function onMouseMove(ev) {
          if (!isDragging) return;
          const dx = ev.clientX - startX;
          const newLeft = Math.max(10, initialLeft + dx);
          chip.style.left = `${newLeft}px`;

          // Find closest char cell (magnetic snap)
          const trackRect = trackDiv.getBoundingClientRect();
          let closestChar = null;
          let minDistance = Infinity;

          charCells.forEach(cell => {
            const cellRect = cell.getBoundingClientRect();
            const cellCenter = (cellRect.left - trackRect.left) + (cellRect.width / 2);
            const dist = Math.abs(cellCenter - newLeft);
            if (dist < minDistance) {
              minDistance = dist;
              closestChar = cell;
            }
          });

          charCells.forEach(c => c.classList.remove('snap-target'));
          if (closestChar && minDistance < 35) {
            closestChar.classList.add('snap-target');
          }
        }

        function onMouseUp(ev) {
          if (!isDragging) return;
          isDragging = false;
          chip.classList.remove('selected');
          window.removeEventListener('mousemove', onMouseMove);
          window.removeEventListener('mouseup', onMouseUp);

          // Find snapped target
          const activeSnap = textRow.querySelector('.char-cell.snap-target');
          if (activeSnap) {
            chord.charIndex = parseInt(activeSnap.dataset.charIndex, 10);
            chord.confidence = 1.0;
            chord.manual = true;
            activeSnap.classList.remove('snap-target');
          }

          // Re-render editor and live preview
          renderInteractiveEditor(song);
          updateAllLivePreviews();
        }

        window.addEventListener('mousemove', onMouseMove);
        window.addEventListener('mouseup', onMouseUp);
      });
    }

    /**
     * Update quality control stats badges (green / yellow / red)
     */
    function updateQualityConfidenceBadges() {
      let high = 0, med = 0, low = 0;
      if (activeSongModel && activeSongModel.lines) {
        activeSongModel.lines.forEach(l => {
          if (l.chords) {
            l.chords.forEach(c => {
              if (c.confidence >= 0.8) high++;
              else if (c.confidence >= 0.5) med++;
              else low++;
            });
          }
        });
      }
      const elHigh = document.getElementById('stat-high-conf');
      const elMed = document.getElementById('stat-med-conf');
      const elLow = document.getElementById('stat-low-conf');
      if (elHigh) elHigh.textContent = `🟢 ${high}`;
      if (elMed) elMed.textContent = `🟡 ${med}`;
      if (elLow) elLow.textContent = `🔴 ${low}`;
    }

    /**
     * Refresh all live preview tabs (OpenSong, ChordPro, Plain Text)
     */
    function updateAllLivePreviews() {
      if (!activeSongModel) return;
      const osView = document.getElementById('live-opensong-view');
      const cpView = document.getElementById('live-chordpro-view');
      const plainView = document.getElementById('live-plain-view');

      if (osView) osView.textContent = serializeSongToOpenSongXml(activeSongModel);
      if (cpView) cpView.textContent = serializeSongToChordPro(activeSongModel);
      if (plainView) plainView.textContent = serializeSongToPlainText(activeSongModel);
    }

    // Bind Live Preview Tab Switching
    document.querySelectorAll('.preview-tab-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.preview-tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.ptab-content').forEach(c => c.style.display = 'none');
        btn.classList.add('active');
        const targetId = btn.dataset.ptab;
        const targetEl = document.getElementById(targetId);
        if (targetEl) targetEl.style.display = 'block';
      });
    });

    // =========================================================================
    // EXPORT & PRINT ENGINES (OpenSong XML, ChordPro .cho, PDF Print, DOCX)
    // =========================================================================

    // 1. Export OpenSong XML file
    document.getElementById('btn-export-opensong-xml')?.addEventListener('click', () => {
      if (!activeSongModel) { alert('Сначала загрузите или выберите песню.'); return; }
      const xml = serializeSongToOpenSongXml(activeSongModel);
      const filename = `${activeSongModel.title || 'song'}.xml`;
      downloadTextFile(xml, filename, 'application/xml;charset=utf-8;');
    });

    // 2. Export ChordPro .cho file
    document.getElementById('btn-export-chordpro-txt')?.addEventListener('click', () => {
      if (!activeSongModel) { alert('Сначала загрузите или выберите песню.'); return; }
      const cho = serializeSongToChordPro(activeSongModel);
      const filename = `${activeSongModel.title || 'song'}.cho`;
      downloadTextFile(cho, filename, 'text/plain;charset=utf-8;');
    });

    // 3. Print / Generate PDF (via browser print preview)
    document.getElementById('btn-print-html-pdf')?.addEventListener('click', () => {
      if (!activeSongModel) { alert('Сначала загрузите или выберите песню.'); return; }
      const osLyrics = serializeSongToOpenSongLyrics(activeSongModel);

      const printWin = window.open('', '_blank');
      printWin.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="utf-8">
          <title>${activeSongModel.title} — Огненный ветер</title>
          <style>
            @page { size: A4; margin: 15mm; }
            body { font-family: "Times New Roman", Times, serif; font-size: 14pt; line-height: 1.4; color: #000; margin: 0; padding: 15mm; }
            h1 { text-align: center; font-size: 20pt; margin-bottom: 4px; text-transform: uppercase; }
            .meta { text-align: center; font-size: 11pt; color: #555; margin-bottom: 20px; }
            pre { font-family: "Times New Roman", Times, serif; font-size: 13pt; line-height: 1.35; white-space: pre-wrap; word-wrap: break-word; }
            .chord-line { font-weight: bold; color: #111; }
          </style>
        </head>
        <body>
          <h1>${activeSongModel.title}</h1>
          <div class="meta">
            ${activeSongModel.key_default ? 'Тональность: <b>' + activeSongModel.key_default + '</b>' : ''}
            ${activeSongModel.capo ? ' | Капо: <b>' + activeSongModel.capo + '</b>' : ''}
            ${activeSongModel.tempo ? ' | Темп: <b>' + activeSongModel.tempo + '</b>' : ''}
          </div>
          <pre>${osLyrics.split('\n').map(l => l.startsWith('.') ? `<span class="chord-line">${l.substring(1)}</span>` : l).join('\n')}</pre>
          <script>
            window.onload = function() { window.print(); };
          </script>
        </body>
        </html>
      `);
      printWin.document.close();
    });

    // 4. Export Clean DOCX for Print
    document.getElementById('btn-export-song-docx')?.addEventListener('click', async () => {
      if (!activeSongModel) { alert('Сначала загрузите или выберите песню.'); return; }
      
      const zip = new JSZip();
      const osLyrics = serializeSongToOpenSongLyrics(activeSongModel);
      const lines = osLyrics.split('\n');

      let paragraphsXml = '';
      paragraphsXml += `<w:p><w:pPr><w:jc w:val="center"/></w:pPr><w:r><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/><w:b/><w:sz w:val="36"/></w:rPr><w:t>${activeSongModel.title}</w:t></w:r></w:p>`;
      
      const metaStr = `Тональность: ${activeSongModel.key_default || '—'}  Капо: ${activeSongModel.capo || '—'}  Темп: ${activeSongModel.tempo || '—'}`;
      paragraphsXml += `<w:p><w:pPr><w:jc w:val="center"/></w:pPr><w:r><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/><w:i/><w:sz w:val="22"/><w:color w:val="666666"/></w:rPr><w:t>${metaStr}</w:t></w:r></w:p>`;
      paragraphsXml += `<w:p><w:r><w:t></w:t></w:r></w:p>`;

      for (const l of lines) {
        if (!l.trim()) {
          paragraphsXml += `<w:p><w:r><w:t></w:t></w:r></w:p>`;
          continue;
        }
        if (l.startsWith('.')) {
          // Chord line: Bold
          paragraphsXml += `<w:p><w:r><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/><w:b/><w:sz w:val="24"/></w:rPr><w:t xml:space="preserve">${l.substring(1)}</w:t></w:r></w:p>`;
        } else {
          // Lyric line: Regular
          paragraphsXml += `<w:p><w:r><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/><w:sz w:val="24"/></w:rPr><w:t xml:space="preserve">${l}</w:t></w:r></w:p>`;
        }
      }

      // Minimal valid DOCX document structure
      zip.file('[Content_Types].xml', `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>`);

      zip.file('_rels/.rels', `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>`);

      zip.file('word/document.xml', `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    ${paragraphsXml}
  </w:body>
</w:document>`);

      const blob = await zip.generateAsync({ type: 'blob' });
      const filename = `${activeSongModel.title || 'song'}.docx`;
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    });

    // 5. Batch Export all parsed songs to a single ZIP
    document.getElementById('btn-export-all-zip')?.addEventListener('click', async () => {
      if (!parsedDocxSongs || parsedDocxSongs.length === 0) {
        alert('Нет распознанных песен для скачивания.');
        return;
      }

      const zip = new JSZip();
      let count = 0;

      parsedDocxSongs.forEach((song, idx) => {
        const baseName = `${song.id || String(idx+1).padStart(4,'0')}_${(song.title || 'song').replace(/[\\/:*?"<>|]/g, '_')}`;
        // Add OpenSong XML
        if (song.rawModel) {
          zip.file(`opensong/${baseName}.xml`, serializeSongToOpenSongXml(song.rawModel));
          zip.file(`chordpro/${baseName}.cho`, serializeSongToChordPro(song.rawModel));
        } else {
          zip.file(`chordpro/${baseName}.cho`, song.body_chordpro || '');
        }
        count++;
      });

      const blob = await zip.generateAsync({ type: 'blob' });
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = `songs_archive_opensong_chordpro_${formatBackupTimestamp()}.zip`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      alert(`Сформирован ZIP архив с ${count} песнями в форматах OpenSong XML и ChordPro!`);
    });

    function downloadTextFile(content, filename, mimeType) {
      const blob = new Blob([content], { type: mimeType });
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    }
'''

with open('data/admin.html', 'r', encoding='utf-8') as f:
    text = f.read()

m = text.find('// 1. DOCX CHORDS IMPORT EVENT HANDLERS')
assert m != -1, "Target section not found"

new_text = text[:m] + editor_and_ui_code + '\n\n    ' + text[m:]

with open('data/admin.html', 'w', encoding='utf-8') as f:
    f.write(new_text)

print("Editor and Export engine successfully injected!")
