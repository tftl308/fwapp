# -*- coding: utf-8 -*-
import sys

converter_engine_code = r'''
    // =========================================================================
    // ADVANCED GEOMETRIC TYPOGRAPHY & CHORD-ALIGNMENT ENGINE (TypeScript-grade)
    // =========================================================================
    
    // Regular expression for chords (Latin A-G + European H/B notation + extensions)
    const CHORD_MATCH_REGEX = /^[A-H](#|b)?(m|maj|min|dim|aug|sus|add)?\d{0,2}(sus\d|add\d{1,2})?(\/[A-H](#|b)?)?$/;
    
    // Russian and English vowels for syllable snapping heuristics
    const VOWELS_REGEX = /[аеёиоуыэюяaeiouyАЕЁИОУЫЭЮЯAEIOUY]/;
    
    // Canvas text metrics cache for Times New Roman font
    const _metricsCanvas = typeof document !== 'undefined' ? document.createElement('canvas') : null;
    const _metricsCtx = _metricsCanvas ? _metricsCanvas.getContext('2d') : null;

    function measureTextWidth(text, font = '16px "Times New Roman", serif') {
      if (!_metricsCtx) return text.length * 8; // fallback
      _metricsCtx.font = font;
      return _metricsCtx.measureText(text).width;
    }

    /**
     * Measure cumulative X positions of every character (grapheme) in a line of lyrics
     */
    function computeCharXPositions(text, font = '16px "Times New Roman", serif') {
      const positions = [];
      const chars = Array.from(text);
      let runningPrefix = '';
      for (let i = 0; i < chars.length; i++) {
        const x = measureTextWidth(runningPrefix, font);
        positions.push(x);
        runningPrefix += chars[i];
      }
      // Ending anchor point
      positions.push(measureTextWidth(runningPrefix, font));
      return positions;
    }

    /**
     * Build magnetic snap points along the lyric line with phonetic cost penalties
     */
    function buildLyricSnapPoints(text, xs, emSize = 16) {
      const snaps = [];
      const chars = Array.from(text);
      let inWord = false;

      for (let i = 0; i < chars.length; i++) {
        const ch = chars[i];
        const isSpace = /\s/.test(ch);
        const isWordStart = !isSpace && !inWord;
        inWord = !isSpace;

        let penalty = 1.2 * emSize; // Default consonant / symbol penalty
        if (isWordStart) {
          penalty = 0; // Word start anchor: zero penalty (primary anchor)
        } else if (VOWELS_REGEX.test(ch)) {
          penalty = 0.35 * emSize; // Syllable vowel anchor: low penalty
        } else if (isSpace) {
          penalty = 1.6 * emSize; // Spaces are discouraged as chord targets
        }

        snaps.push({
          charIndex: i,
          x: xs[i],
          penalty: penalty,
          char: ch
        });
      }

      // End of line anchor (for instrumental or outro chords)
      snaps.push({
        charIndex: chars.length,
        x: xs[chars.length] || (chars.length * emSize * 0.5),
        penalty: 0.8 * emSize,
        char: ''
      });

      return snaps;
    }

    /**
     * Monotonic Dynamic Programming alignment of chords to lyric snap points.
     * Guaranteed: chords are preserved in left-to-right order without collision on same char.
     */
    function alignChordsDP(chordTokens, snaps, emSize = 16) {
      const M = chordTokens.length;
      const N = snaps.length;
      if (M === 0) return [];
      if (N === 0) return chordTokens.map((_, i) => i);

      // Cost function between chord token k and snap point i
      function calcCost(k, i) {
        const chordX = chordTokens[k].x;
        const snap = snaps[i];
        const dist = Math.abs(chordX - snap.x);
        return (dist / emSize) + snap.penalty;
      }

      // dp[k][i]: minimum cost to place chord k at snap point i
      const dp = Array.from({ length: M }, () => new Float64Array(N).fill(Infinity));
      const parent = Array.from({ length: M }, () => new Int32Array(N).fill(-1));

      // Base case: chord 0
      for (let i = 0; i < N; i++) {
        dp[0][i] = calcCost(0, i);
      }

      // Recurrence for chords 1..M-1
      for (let k = 1; k < M; k++) {
        let minPrevCost = Infinity;
        let bestPrevIndex = -1;

        for (let i = k; i < N; i++) {
          const prevJ = i - 1;
          if (dp[k - 1][prevJ] < minPrevCost) {
            minPrevCost = dp[k - 1][prevJ];
            bestPrevIndex = prevJ;
          }

          if (bestPrevIndex !== -1 && minPrevCost !== Infinity) {
            dp[k][i] = calcCost(k, i) + minPrevCost;
            parent[k][i] = bestPrevIndex;
          }
        }
      }

      // Find best finish
      let bestEndCost = Infinity;
      let bestEndIndex = -1;
      for (let i = M - 1; i < N; i++) {
        if (dp[M - 1][i] < bestEndCost) {
          bestEndCost = dp[M - 1][i];
          bestEndIndex = i;
        }
      }

      // Backtrack
      const resultSnapIndices = new Array(M);
      let curr = bestEndIndex >= 0 ? bestEndIndex : N - 1;
      for (let k = M - 1; k >= 0; k--) {
        resultSnapIndices[k] = curr;
        curr = parent[k][curr];
        if (curr === -1 && k > 0) curr = Math.max(0, resultSnapIndices[k] - 1);
      }

      return resultSnapIndices.map(snapIdx => snaps[snapIdx].charIndex);
    }

    /**
     * Compute confidence score (0.0 to 1.0) based on physical proximity
     */
    function computeChordConfidence(chordX, targetX, emSize = 16) {
      const dist = Math.abs(chordX - targetX);
      const conf = 1.0 - (dist / (2.5 * emSize));
      return Math.max(0.1, Math.min(1.0, conf));
    }

    // =========================================================================
    // CANONICAL SONG MODEL SERIALIZERS (OpenSong XML, ChordPro, Plain Text)
    // =========================================================================

    function serializeSongToChordPro(song) {
      const lines = [];
      if (song.title) lines.push(`{title: ${song.title}}`);
      if (song.key_default) lines.push(`{key: ${song.key_default}}`);
      if (song.capo) lines.push(`{capo: ${song.capo}}`);
      if (song.tempo) lines.push(`{tempo: ${song.tempo}}`);
      lines.push('');

      for (const line of song.lines) {
        if (!line.lyric && (!line.chords || line.chords.length === 0)) {
          lines.push('');
          continue;
        }

        if (!line.chords || line.chords.length === 0) {
          lines.push(line.lyric);
          continue;
        }

        // Sort chords descending by charIndex so insertion does not disrupt prior indices
        const sortedChords = [...line.chords].sort((a, b) => b.charIndex - a.charIndex);
        let result = line.lyric;
        for (const c of sortedChords) {
          const idx = Math.min(Math.max(0, c.charIndex), result.length);
          result = result.slice(0, idx) + `[${c.name}]` + result.slice(idx);
        }
        lines.push(result);
      }
      return lines.join('\n');
    }

    function serializeSongToOpenSongLyrics(song) {
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
      return outputLines.join('\n');
    }

    function serializeSongToOpenSongXml(song) {
      const escapeXml = (str) => String(str || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
      const lyricsBody = serializeSongToOpenSongLyrics(song);

      return `<?xml version="1.0" encoding="UTF-8"?>
<song>
  <title>${escapeXml(song.title)}</title>
  <author>${escapeXml(song.author || 'Огненный ветер')}</author>
  <copyright>${escapeXml(song.album || '')}</copyright>
  <key>${escapeXml(song.key_default || '')}</key>
  <capo print="true">${escapeXml(song.capo || '')}</capo>
  <tempo>${escapeXml(song.tempo || '')}</tempo>
  <time_sig>${escapeXml(song.time_signature || '4/4')}</time_sig>
  <lyrics>
${lyricsBody}
  </lyrics>
</song>`;
    }

    function serializeSongToPlainText(song) {
      return song.lines.map(l => l.lyric || '').join('\n');
    }
'''

with open('data/admin.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Inject this converter engine before convertTextToOpenSongData
m = text.find('function convertTextToOpenSongData')
assert m != -1, "Target function convertTextToOpenSongData not found"

new_text = text[:m] + converter_engine_code + '\n\n    ' + text[m:]

with open('data/admin.html', 'w', encoding='utf-8') as f:
    f.write(new_text)

print("Converter engine successfully injected!")
