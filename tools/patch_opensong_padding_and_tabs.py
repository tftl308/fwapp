# -*- coding: utf-8 -*-
import re

with open('data/admin.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update serializeSongToOpenSongLyrics with safety margin and trailing chord padding
old_func = '''function serializeSongToOpenSongLyrics(song) {
      const outputLines = [];
      let currentSection = '';

      for (const line of song.lines) {
        if (line.kind && line.kind !== 'verse' && line.kind !== 'blank') {
          const secHeader = `[${line.kind.toUpperCase()}]`;
          if (secHeader !== currentSection) {
            outputLines.push(secHeader);
            currentSection = secHeader;
          }
        }

        if (!line.lyric && (!line.chords || line.chords.length === 0)) {
          outputLines.push('');
          continue;
        }

        // If line has chords
        if (line.chords && line.chords.length > 0) {
          // Sort chords ascending by position
          const sortedChords = [...line.chords].sort((a, b) => a.charIndex - b.charIndex);
          let chordLineStr = '.';
          for (const c of sortedChords) {
            // Target column index in OpenSong format (guarantee minimum 1 space gap)
            const targetCol = Math.max(c.charIndex + 1, chordLineStr.length + (chordLineStr.length > 1 ? 1 : 0));
            while (chordLineStr.length < targetCol) chordLineStr += ' ';
            chordLineStr += c.name;
          }
          outputLines.push(chordLineStr);
        }

        // Lyric line prefixed with a space in OpenSong format
        if (line.lyric) {
          outputLines.push(' ' + line.lyric);
        }
      }
      return outputLines.join('\\n');
    }'''

new_func = '''function serializeSongToOpenSongLyrics(song) {
      const outputLines = [];
      let currentSection = '';

      for (const line of song.lines) {
        if (line.kind && line.kind !== 'verse' && line.kind !== 'blank') {
          const secHeader = `[${line.kind.toUpperCase()}]`;
          if (secHeader !== currentSection) {
            outputLines.push(secHeader);
            currentSection = secHeader;
          }
        }

        if (!line.lyric && (!line.chords || line.chords.length === 0)) {
          outputLines.push('');
          continue;
        }

        let lyricStr = line.lyric || '';
        let sortedChords = line.chords && line.chords.length > 0
          ? [...line.chords].sort((a, b) => a.charIndex - b.charIndex)
          : [];

        // If line has chords
        if (sortedChords.length > 0) {
          let chordLineStr = '.';
          for (const c of sortedChords) {
            // In OpenSong, dot '.' is column 0, character indices map to column index (charIndex + 1)
            // Guarantee at least 1 whitespace between consecutive chords to prevent collision
            const targetCol = Math.max(c.charIndex + 1, chordLineStr.length + (chordLineStr.length > 1 ? 1 : 0));
            while (chordLineStr.length < targetCol) chordLineStr += ' ';
            chordLineStr += c.name;
          }

          // Open Chords / OpenSong trailing overlap protection:
          // If the chord line extends beyond the lyric line, pad the lyric line with trailing spaces
          // (minus 1 for the leading space of the lyric line) so downstream parsers and page layout engines
          // maintain exact horizontal rhythm and don't wrap prematurely.
          const chordContentLen = chordLineStr.length - 1; // excluding leading dot
          if (chordContentLen > lyricStr.length) {
            lyricStr = lyricStr.padEnd(chordContentLen, ' ');
          }

          outputLines.push(chordLineStr);
        }

        // Lyric line prefixed with a single space in OpenSong format
        outputLines.push(' ' + lyricStr);
      }
      return outputLines.join('\\n');
    }'''

assert old_func in text, "old_func not matched!"
text = text.replace(old_func, new_func)

# 2. Update XML filename export to include 4-digit zero-padded ID
old_xml_export = '''    // 1. Export OpenSong XML file
    document.getElementById('btn-export-opensong-xml')?.addEventListener('click', () => {
      if (!activeSongModel) { alert('Сначала загрузите или выберите песню.'); return; }
      const xml = serializeSongToOpenSongXml(activeSongModel);
      const filename = `${activeSongModel.title || 'song'}.xml`;
      downloadTextFile(xml, filename, 'application/xml;charset=utf-8;');
    });'''

new_xml_export = '''    // 1. Export OpenSong XML file with normalized 4-digit ID prefix
    document.getElementById('btn-export-opensong-xml')?.addEventListener('click', () => {
      if (!activeSongModel) { alert('Сначала загрузите или выберите песню.'); return; }
      const xml = serializeSongToOpenSongXml(activeSongModel);
      const normId = String(activeSongModel.id || activeSongModel.number || '1').padStart(4, '0');
      const safeTitle = (activeSongModel.title || 'song').replace(/[\\\\/:*?"<>|]/g, '_');
      const filename = `${normId}_${safeTitle}.xml`;
      downloadTextFile(xml, filename, 'application/xml;charset=utf-8;');
    });'''

assert old_xml_export in text, "old_xml_export not matched!"
text = text.replace(old_xml_export, new_xml_export)

# 3. Update ChordPro export to also use normalized 4-digit ID
old_cho_export = '''    // 2. Export ChordPro .cho file
    document.getElementById('btn-export-chordpro-txt')?.addEventListener('click', () => {
      if (!activeSongModel) { alert('Сначала загрузите или выберите песню.'); return; }
      const cho = serializeSongToChordPro(activeSongModel);
      const filename = `${activeSongModel.title || 'song'}.cho`;
      downloadTextFile(cho, filename, 'text/plain;charset=utf-8;');
    });'''

new_cho_export = '''    // 2. Export ChordPro .cho file with normalized 4-digit ID prefix
    document.getElementById('btn-export-chordpro-txt')?.addEventListener('click', () => {
      if (!activeSongModel) { alert('Сначала загрузите или выберите песню.'); return; }
      const cho = serializeSongToChordPro(activeSongModel);
      const normId = String(activeSongModel.id || activeSongModel.number || '1').padStart(4, '0');
      const safeTitle = (activeSongModel.title || 'song').replace(/[\\\\/:*?"<>|]/g, '_');
      const filename = `${normId}_${safeTitle}.cho`;
      downloadTextFile(cho, filename, 'text/plain;charset=utf-8;');
    });'''

assert old_cho_export in text, "old_cho_export not matched!"
text = text.replace(old_cho_export, new_cho_export)

# 4. Fix preview tab switching: use resilient delegated event listener on container
old_preview_tabs = '''    // Bind Live Preview Tab Switching
    document.querySelectorAll('.preview-tab-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.preview-tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.ptab-content').forEach(c => c.style.display = 'none');
        btn.classList.add('active');
        const targetId = btn.dataset.ptab;
        const targetEl = document.getElementById(targetId);
        if (targetEl) targetEl.style.display = 'block';
      });
    });'''

new_preview_tabs = '''    // Resilient Delegated Live Preview Tab Switching
    document.addEventListener('click', (e) => {
      const btn = e.target.closest('.preview-tab-btn');
      if (!btn) return;
      document.querySelectorAll('.preview-tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.ptab-content').forEach(c => c.style.display = 'none');
      btn.classList.add('active');
      const targetId = btn.dataset.ptab;
      const targetEl = document.getElementById(targetId);
      if (targetEl) targetEl.style.display = 'block';
    });'''

assert old_preview_tabs in text, "old_preview_tabs not matched!"
text = text.replace(old_preview_tabs, new_preview_tabs)

with open('data/admin.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("All 3 updates successfully applied to data/admin.html!")
