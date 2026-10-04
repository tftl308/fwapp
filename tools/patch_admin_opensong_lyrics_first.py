# -*- coding: utf-8 -*-
with open('data/admin.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update serializeSongToOpenSongLyrics:
# NEVER output synthesized section headers like [VERSE] or [BLANK]!
# If the line has kind with a specific name like [Куплет 1] or [Припев], keep it,
# but DO NOT invent [VERSE] on ordinary lyrics lines.
old_os_serialize = """      for (const line of song.lines) {
        if (line.kind && line.kind !== 'verse' && line.kind !== 'blank') {
          const secHeader = `[${line.kind.toUpperCase()}]`;
          if (secHeader !== currentSection) {
            outputLines.push(secHeader);
            currentSection = secHeader;
          }
        }"""

new_os_serialize = """      for (const line of song.lines) {
        // Section headers: only output if line is explicitly a section header
        if (line.kind === 'section-header' || line.kind === 'chorus-header' || (line.kind && line.kind.startsWith('['))) {
          const secText = line.lyric && line.lyric.startsWith('[') ? line.lyric : `[${line.lyric || line.kind}]`;
          if (secText !== currentSection) {
            outputLines.push(secText);
            currentSection = secText;
          }
          continue;
        }"""

assert old_os_serialize in text, "old_os_serialize not found"
text = text.replace(old_os_serialize, new_os_serialize)

# 2. Add buildModelFromOpenSongLyrics(lyricsText, songMeta) helper function:
# Perfectly parses OpenSong format into song model without dropping lines or confusing chords
opensong_builder_fn = """
    // =========================================================================
    // ТОЧНЫЙ ПАРСЕР ТЕКСТА OPENSONG В МОДЕЛЬ РЕДАКТОРА
    // =========================================================================
    function buildModelFromOpenSongLyrics(lyricsText, songMeta = {}) {
      const model = {
        id: songMeta.id || '0001',
        number: songMeta.number || parseInt(songMeta.id, 10) || 1,
        title: songMeta.title || 'Без названия',
        key_default: songMeta.key || songMeta.key_default || '',
        capo: songMeta.capo || '',
        tempo: songMeta.tempo || '',
        author: songMeta.author || 'Огненный ветер',
        lines: []
      };

      if (!lyricsText) return model;

      // Check if it is XML wrapped
      let text = lyricsText;
      const mXml = lyricsText.match(/<lyrics>([\\s\\S]*?)<\\/lyrics>/i);
      if (mXml) text = mXml[1].trim();

      const rawLines = text.split(/\\r?\\n/);
      let i = 0;

      while (i < rawLines.length) {
        const line = rawLines[i];
        const trimmed = line.trim();

        if (!trimmed) {
          model.lines.push({ kind: 'blank', lyric: '', chords: [] });
          i++;
          continue;
        }

        // 1. OpenSong Dot Chord line (.Am   G   C)
        if (line.startsWith('.')) {
          const chordLine = line.substring(1);
          let lyricStr = '';
          const nextLine = rawLines[i + 1];

          // Next line is the text matching this chord line
          if (nextLine !== undefined && !nextLine.startsWith('.') && !nextLine.startsWith('[')) {
            lyricStr = nextLine.startsWith(' ') ? nextLine.substring(1) : nextLine;
            i += 2;
          } else {
            i += 1;
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

        // 2. OpenSong Section marker ([V1], [C], [Куплет 1], etc.)
        if (line.startsWith('[') && line.endsWith(']')) {
          const isChorus = /припев|chorus|\\[c/i.test(line);
          model.lines.push({
            kind: isChorus ? 'chorus-header' : 'section-header',
            lyric: line,
            chords: []
          });
          i++;
          continue;
        }

        // 3. Regular lyric line (prefixed with space in OpenSong or normal text)
        const lyricStr = line.startsWith(' ') ? line.substring(1) : line;
        model.lines.push({
          kind: 'verse',
          lyric: lyricStr,
          chords: []
        });
        i++;
      }

      return model;
    }
"""

pos_target = text.find('function parseOpenSongLyricsToModel(rawText) {')
assert pos_target != -1, "parseOpenSongLyricsToModel not found"
text = text[:pos_target] + opensong_builder_fn + "\n    " + text[pos_target:]

# 3. Update openSongInVisualEditor:
# Check if song has OpenSong formatted lyrics (with leading dot or leading space lines)
old_open_visual = """      // 1. Build or retrieve model
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
      }"""

new_open_visual = """      // 1. Build or retrieve model
      let model = song.rawModel;
      if (!model) {
        const lyricsText = song.lyrics || song.body_plain || '';
        const chordProText = song.chordpro || song.body_chordpro || '';

        // ПРИОРИТЕТ 1: Если lyrics содержит OpenSong разметку (строки с точкой .Am или <lyrics>)
        if (lyricsText.includes('\\n.') || lyricsText.startsWith('.') || lyricsText.includes('<lyrics>')) {
          model = buildModelFromOpenSongLyrics(lyricsText, song);
        }
        // ПРИОРИТЕТ 2: Если есть ChordPro аккорды [Am]
        else if (chordProText && chordProText.includes('[')) {
          model = parseChordProTextToModel(chordProText, song);
        }
        // ПРИОРИТЕТ 3: Обычный чистый текст OpenSong / DOCX
        else if (lyricsText.trim()) {
          model = buildModelFromOpenSongLyrics(lyricsText, song);
        } else {
          model = parseRawBlockToSongModel(chordProText || lyricsText, song.id);
        }

        if (model) {
          if (!model.title) model.title = song.title;
          if (!model.key_default) model.key_default = song.key || song.key_default || '';
          if (!model.capo) model.capo = song.capo || '';
          if (!model.tempo) model.tempo = song.tempo || '';
        }
        song.rawModel = model;
      }"""

assert old_open_visual in text, "old_open_visual not found"
text = text.replace(old_open_visual, new_open_visual)

with open('data/admin.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("data/admin.html patched: OpenSong format cleanly parsed without breaking lines!")
