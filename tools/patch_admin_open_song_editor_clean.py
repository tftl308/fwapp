# -*- coding: utf-8 -*-
with open('data/admin.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Fix serializeSongToChordPro to use (c.name || c.chord || '')
old_serialize_chordpro = """        // Sort chords descending by charIndex so insertion does not disrupt prior indices
        const sortedChords = [...line.chords].sort((a, b) => b.charIndex - a.charIndex);
        let result = line.lyric;
        for (const c of sortedChords) {
          const idx = Math.min(Math.max(0, c.charIndex), result.length);
          result = result.slice(0, idx) + `[${c.name}]` + result.slice(idx);
        }
        lines.push(result);"""

new_serialize_chordpro = """        // Sort chords descending by charIndex so insertion does not disrupt prior indices
        const sortedChords = [...line.chords].sort((a, b) => b.charIndex - a.charIndex);
        let result = line.lyric;
        for (const c of sortedChords) {
          const chordText = c.name || c.chord || '';
          if (!chordText) continue;
          const idx = Math.min(Math.max(0, c.charIndex), result.length);
          result = result.slice(0, idx) + `[${chordText}]` + result.slice(idx);
        }
        lines.push(result);"""

assert old_serialize_chordpro in text, "old_serialize_chordpro not found"
text = text.replace(old_serialize_chordpro, new_serialize_chordpro)

# 2. Fix serializeSongToOpenSongLyrics to use (c.name || c.chord || '')
old_serialize_os = """            while (chordLineStr.length < targetCol) chordLineStr += ' ';
            chordLineStr += c.name;"""

new_serialize_os = """            while (chordLineStr.length < targetCol) chordLineStr += ' ';
            chordLineStr += (c.name || c.chord || '');"""

assert old_serialize_os in text, "old_serialize_os not found"
text = text.replace(old_serialize_os, new_serialize_os)

# 3. Fix chip rendering in renderInteractiveEditor to use (chord.name || chord.chord || '')
old_chip = """chip.innerHTML = `<span>${chord.name}</span><span class="btn-chip-del" title="Удалить аккорд">×</span>`;"""
new_chip = """const chordDisplayName = chord.name || chord.chord || '';
            chip.innerHTML = `<span>${chordDisplayName}</span><span class="btn-chip-del" title="Удалить аккорд">×</span>`;"""

assert old_chip in text, "old_chip not found"
text = text.replace(old_chip, new_chip)

# 4. Replace parseChordProTextToModel in openSongInVisualEditor helper
# It should robustly handle:
# - Skipping {title}, {key}, {capo}, etc. without dropping actual lyric lines
# - OpenSong dot lines (.Am)
# - Inline [Am] chords
# - Retaining line.name = chordToken
old_parse_helper = """    function parseChordProTextToModel(chordProText, songMeta) {
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
    }"""

new_parse_helper = """    function parseChordProTextToModel(chordProText, songMeta) {
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

      for (let lineIndex = 0; lineIndex < lines.length; lineIndex++) {
        const rawLine = lines[lineIndex];
        const trimmed = rawLine.trim();
        if (!trimmed) {
          model.lines.push({ kind: 'blank', lyric: '', chords: [] });
          continue;
        }

        // Meta tags: {title: ...}, {key: ...}, {capo: ...}, {tempo: ...} - extract metadata and skip without eating song text
        const mMeta = trimmed.match(/^{(title|key|capo|tempo|artist|composer):\\s*(.*?)}/i);
        if (mMeta) {
          const field = mMeta[1].toLowerCase();
          const val = mMeta[2].trim();
          if (field === 'title' && !model.title) model.title = val;
          if (field === 'key' && !model.key_default) model.key_default = val;
          if (field === 'capo' && !model.capo) model.capo = val;
          if (field === 'tempo' && !model.tempo) model.tempo = val;
          continue;
        }

        // OpenSong dot chord line: .Am  G  F
        if (rawLine.startsWith('.')) {
          const chordLine = rawLine.substring(1);
          let lyricStr = '';
          const nextLine = lines[lineIndex + 1];
          if (nextLine !== undefined && !nextLine.startsWith('.') && !nextLine.startsWith('[') && !nextLine.startsWith('{')) {
            lyricStr = nextLine.startsWith(' ') ? nextLine.substring(1) : nextLine;
            lineIndex++;
          }

          const chords = [];
          const regex = /\\S+/g;
          let m;
          while ((m = regex.exec(chordLine)) !== null) {
            chords.push({
              name: m[0],
              chord: m[0],
              charIndex: Math.max(0, m.index),
              confidence: 1.0,
              manual: true
            });
          }

          model.lines.push({
            kind: 'verse',
            lyric: lyricStr,
            chords: chords
          });
          continue;
        }

        // Section header in OpenSong format: [V1], [C], [B] or russian section
        if (/^\\[(v\\d*|c\\d*|b\\d*|t|e|intro|outro|куплет|припев|бридж|вступление|проигрыш)/i.test(trimmed)) {
          const kind = /припев|c/i.test(trimmed) ? 'chorus-header' : 'section-header';
          model.lines.push({ kind: kind, lyric: trimmed, chords: [] });
          continue;
        }

        // Parse line with inline [Chord] tokens
        let lyric = '';
        const chords = [];
        const regex = /\\[([^\\]]+)\\]/g;
        let match;
        let lastEnd = 0;

        while ((match = regex.exec(rawLine)) !== null) {
          lyric += rawLine.slice(lastEnd, match.index);
          const chordToken = match[1].trim();
          chords.push({
            name: chordToken,
            chord: chordToken,
            charIndex: lyric.length,
            confidence: 1.0,
            manual: true
          });
          lastEnd = regex.lastIndex;
        }
        lyric += rawLine.slice(lastEnd);

        // Check if this was a standalone chord line without brackets
        if (chords.length === 0 && isChordLine(trimmed)) {
          const tokens = trimmed.split(/\\s+/);
          tokens.forEach((tok, i) => {
            chords.push({
              name: tok,
              chord: tok,
              charIndex: i * 8,
              confidence: 0.9,
              manual: true
            });
          });
          lyric = '';
        }

        model.lines.push({
          kind: 'verse',
          lyric: lyric,
          chords: chords
        });
      }

      return model;
    }"""

assert old_parse_helper in text, "old_parse_helper not found"
text = text.replace(old_parse_helper, new_parse_helper)

# 5. In Tab 1, add a dedicated modal button for Tag editing (tags & 22 canonical metadata)
old_toolbar = """        <!-- Undo / Redo controls (до 50 операций) -->
        <div style="height: 24px; width: 1px; background: #cbd5e1; margin: 0 0.3rem;"></div>
        <button type="button" class="btn btn-outline" id="btn-editor-undo" title="Отменить последнее действие (Ctrl+Z)" disabled>↶ Отмена (Undo)</button>
        <button type="button" class="btn btn-outline" id="btn-editor-redo" title="Повторить отменённое действие (Ctrl+Y)" disabled>↷ Повтор (Redo)</button>
        <span id="history-steps-badge" style="font-size:0.75rem; color:var(--muted); font-weight:600;">0/50</span>

        <div style="height: 24px; width: 1px; background: #cbd5e1; margin: 0 0.3rem;"></div>
        
        <button class="btn btn-success" id="btn-apply-docx-songs" disabled>📥 Сохранить в базу (songs.csv)</button>"""

new_toolbar = """        <!-- Undo / Redo controls (до 50 операций) -->
        <div style="height: 24px; width: 1px; background: #cbd5e1; margin: 0 0.3rem;"></div>
        <button type="button" class="btn btn-outline" id="btn-editor-undo" title="Отменить последнее действие (Ctrl+Z)" disabled>↶ Отмена (Undo)</button>
        <button type="button" class="btn btn-outline" id="btn-editor-redo" title="Повторить отменённое действие (Ctrl+Y)" disabled>↷ Повтор (Redo)</button>
        <span id="history-steps-badge" style="font-size:0.75rem; color:var(--muted); font-weight:600;">0/50</span>

        <div style="height: 24px; width: 1px; background: #cbd5e1; margin: 0 0.3rem;"></div>
        
        <!-- Отдельная кнопка для редактирования всех тэгов и 22 полей текущей песни -->
        <button type="button" class="btn btn-outline" id="btn-editor-edit-tags" style="border-color: #0284c7; color: #0369a1; font-weight: 700;" title="Открыть окно редактирования тэгов, темы, размера и заметок">🏷️ Тэги и поля (22 поля)</button>

        <button class="btn btn-success" id="btn-apply-docx-songs" disabled>📥 Сохранить в базу (songs.csv)</button>"""

assert old_toolbar in text, "old_toolbar not found"
text = text.replace(old_toolbar, new_toolbar)

# Wire btn-editor-edit-tags to openEditModal with activeSongModel.id
wire_tag_button = """
    document.getElementById('btn-editor-edit-tags')?.addEventListener('click', () => {
      if (!activeSongModel || !activeSongModel.id) {
        alert('Выберите песню в списке слева для редактирования тэгов.');
        return;
      }
      openEditModal(activeSongModel.id);
    });
"""

pos_wire = text.find("document.getElementById('btn-apply-docx-songs').addEventListener('click'")
assert pos_wire != -1
text = text[:pos_wire] + wire_tag_button + "\n    " + text[pos_wire:]

with open('data/admin.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("data/admin.html successfully patched: chords [Am] fixed, first lines preserved, tags modal button added!")
