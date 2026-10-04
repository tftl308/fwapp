# -*- coding: utf-8 -*-
with open('data/admin.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Replace alignChordsDP and parseRawBlockToSongModel with calibrated typography physics
old_align_chunk = """    function alignChordsDP(chordTokens, snaps, emSize = 16) {
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
    }"""

new_align_chunk = """    /**
     * Enhanced Geometric DP Alignment with Dynamic Proportional Scale Compensation:
     * When spaces accumulate towards the end of a line, cumulative kerning drift increases.
     * We dynamically calibrate the space compression ratio (effectiveSpaceWidth / regularCharWidth)
     * so that end-of-line chords snap accurately to their intended lyric syllables.
     */
    function alignChordsDP(chordTokens, snaps, emSize = 16, lineLyric = '', rawChordLine = '') {
      const M = chordTokens.length;
      const N = snaps.length;
      if (M === 0) return [];
      if (N === 0) return chordTokens.map((_, i) => i);

      // Analyze end-of-line drift if both lines exist
      let spaceScaleFactor = 1.0;
      if (rawChordLine && lineLyric) {
        const chordLineLen = rawChordLine.length;
        const lyricLen = lineLyric.length;
        if (chordLineLen > 0 && lyricLen > 0 && chordTokens[M - 1].rawCol > 20) {
          // If the chord line uses wide monospace-like spacing for proportional text
          const lyricEndPx = snaps[N - 1].x;
          const lastChordEstPx = chordTokens[M - 1].x;
          if (lastChordEstPx > lyricEndPx * 1.05 && lyricEndPx > 0) {
            spaceScaleFactor = lyricEndPx / lastChordEstPx;
          }
        }
      }

      // Cost function with quadratic distance penalty to prevent drift hopping
      function calcCost(k, i) {
        const chordX = chordTokens[k].x * spaceScaleFactor;
        const snap = snaps[i];
        const dist = Math.abs(chordX - snap.x);
        // Normalized distance with quadratic damping
        const normDist = dist / emSize;
        return (normDist + 0.3 * (normDist * normDist)) + (snap.penalty / emSize);
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
    }"""

assert old_align_chunk in text, "old_align_chunk not matched"
text = text.replace(old_align_chunk, new_align_chunk)

# 2. Update parseRawBlockToSongModel to pass rawChordLine and lineLyric
old_parse_call = "const assignedCharIndices = alignChordsDP(chordTokens, snaps);"
new_parse_call = "const assignedCharIndices = alignChordsDP(chordTokens, snaps, 16, lyricText, currentLine);"
assert old_parse_call in text, "old_parse_call not matched"
text = text.replace(old_parse_call, new_parse_call)

# 3. Update preview tabs switching and 2-way live sync logic
old_sync_and_tabs = """    /**
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

    // Resilient Delegated Live Preview Tab Switching
    document.addEventListener('click', (e) => {
      const btn = e.target.closest('.preview-tab-btn');
      if (!btn) return;
      document.querySelectorAll('.preview-tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.ptab-content').forEach(c => c.style.display = 'none');
      btn.classList.add('active');
      const targetId = btn.dataset.ptab;
      const targetEl = document.getElementById(targetId);
      if (targetEl) targetEl.style.display = 'block';
    });"""

new_sync_and_tabs = """    let isInternalSyncing = false;

    /**
     * Refresh all live preview tabs (OpenSong, ChordPro, Plain Text)
     */
    function updateAllLivePreviews() {
      if (!activeSongModel || isInternalSyncing) return;
      const osView = document.getElementById('live-opensong-view');
      const cpView = document.getElementById('live-chordpro-view');
      const plainView = document.getElementById('live-plain-view');

      // Update without overwriting user cursor if they are currently typing in that textarea
      if (osView && document.activeElement !== osView) osView.value = serializeSongToOpenSongXml(activeSongModel);
      if (cpView && document.activeElement !== cpView) cpView.value = serializeSongToChordPro(activeSongModel);
      if (plainView && document.activeElement !== plainView) plainView.value = serializeSongToPlainText(activeSongModel);
    }

    /**
     * Parse OpenSong text or XML directly from the right-hand textarea and sync to activeSongModel + left editor
     */
    function parseOpenSongLyricsToModel(rawText) {
      if (!activeSongModel) return;
      let lyricsText = rawText;
      
      // If it contains <lyrics> XML tags, extract inner lyrics
      const matchLyrics = rawText.match(/<lyrics>([\\s\\S]*?)<\\/lyrics>/i);
      if (matchLyrics) {
        lyricsText = matchLyrics[1].trim();
        // Also extract title, key, capo if present
        const mTitle = rawText.match(/<title>([\\s\\S]*?)<\\/title>/i);
        if (mTitle) activeSongModel.title = mTitle[1].trim();
        const mKey = rawText.match(/<key>([\\s\\S]*?)<\\/key>/i);
        if (mKey) activeSongModel.key_default = mKey[1].trim();
        const mCapo = rawText.match(/<capo[^>]*>([\\s\\S]*?)<\\/capo>/i);
        if (mCapo) activeSongModel.capo = mCapo[1].trim();
        const mTempo = rawText.match(/<tempo>([\\s\\S]*?)<\\/tempo>/i);
        if (mTempo) activeSongModel.tempo = mTempo[1].trim();
      }

      const lines = lyricsText.split(/\\r?\\n/);
      const newLines = [];
      let i = 0;

      while (i < lines.length) {
        const line = lines[i];
        if (line.startsWith('.')) {
          // Chord line in OpenSong
          const chordLine = line.substring(1);
          const nextLine = lines[i + 1];
          let lyricStr = '';
          if (nextLine !== undefined && !nextLine.startsWith('.') && !nextLine.startsWith('[')) {
            lyricStr = nextLine.startsWith(' ') ? nextLine.substring(1) : nextLine;
            i += 2;
          } else {
            i += 1;
          }

          // Extract chords and character column offsets (each space = 1 charIndex)
          const chords = [];
          const regex = /\\S+/g;
          let m;
          while ((m = regex.exec(chordLine)) !== null) {
            chords.push({
              name: m[0],
              charIndex: Math.max(0, m.index),
              confidence: 1.0,
              manual: true
            });
          }

          newLines.push({
            kind: 'verse',
            lyric: lyricStr,
            chords: chords
          });
        } else if (line.startsWith('[')) {
          // Section header [V1], [C], etc.
          const sec = line.toLowerCase();
          const kind = sec.includes('c') ? 'chorus' : (sec.includes('b') ? 'bridge' : 'verse');
          newLines.push({ kind: kind, lyric: line, chords: [] });
          i++;
        } else if (!line.trim()) {
          newLines.push({ kind: 'blank', lyric: '', chords: [] });
          i++;
        } else {
          // Lyric line without chords
          const lyricStr = line.startsWith(' ') ? line.substring(1) : line;
          newLines.push({ kind: 'verse', lyric: lyricStr, chords: [] });
          i++;
        }
      }

      activeSongModel.lines = newLines;
      renderInteractiveEditor(activeSongModel);
    }

    /**
     * Parse ChordPro directly from the right-hand textarea
     */
    function parseChordProTextToModel(chordProText) {
      if (!activeSongModel) return;
      const lines = chordProText.split(/\\r?\\n/);
      const newLines = [];

      lines.forEach(line => {
        const trimmed = line.trim();
        if (!trimmed) {
          newLines.push({ kind: 'blank', lyric: '', chords: [] });
          return;
        }

        // Meta tags
        const mMeta = trimmed.match(/^{(title|key|capo|tempo):\\s*(.*?)}/i);
        if (mMeta) {
          const field = mMeta[1].toLowerCase();
          const val = mMeta[2].trim();
          if (field === 'title') activeSongModel.title = val;
          if (field === 'key') activeSongModel.key_default = val;
          if (field === 'capo') activeSongModel.capo = val;
          if (field === 'tempo') activeSongModel.tempo = val;
          return;
        }

        // Parse inline chords [Am]
        const chords = [];
        let cleanLyric = '';
        const regex = /\\[([^\\]]+)\\]|([^\\[]+)/g;
        let match;
        while ((match = regex.exec(line)) !== null) {
          if (match[1]) {
            chords.push({
              name: match[1],
              charIndex: cleanLyric.length,
              confidence: 1.0,
              manual: true
            });
          } else if (match[2]) {
            cleanLyric += match[2];
          }
        }

        newLines.push({
          kind: 'verse',
          lyric: cleanLyric,
          chords: chords
        });
      });

      activeSongModel.lines = newLines;
      renderInteractiveEditor(activeSongModel);
    }

    // Set up 2-way real-time input listeners on right-side editors
    function setupTwoWaySyncListeners() {
      const osView = document.getElementById('live-opensong-view');
      const cpView = document.getElementById('live-chordpro-view');

      if (osView) {
        let osTimer = null;
        osView.addEventListener('input', () => {
          clearTimeout(osTimer);
          osTimer = setTimeout(() => {
            isInternalSyncing = true;
            try {
              parseOpenSongLyricsToModel(osView.value);
              // Also sync ChordPro and Plain text views
              if (cpView) cpView.value = serializeSongToChordPro(activeSongModel);
              const plainView = document.getElementById('live-plain-view');
              if (plainView) plainView.value = serializeSongToPlainText(activeSongModel);
            } finally {
              isInternalSyncing = false;
            }
          }, 250);
        });
      }

      if (cpView) {
        let cpTimer = null;
        cpView.addEventListener('input', () => {
          clearTimeout(cpTimer);
          cpTimer = setTimeout(() => {
            isInternalSyncing = true;
            try {
              parseChordProTextToModel(cpView.value);
              if (osView) osView.value = serializeSongToOpenSongXml(activeSongModel);
              const plainView = document.getElementById('live-plain-view');
              if (plainView) plainView.value = serializeSongToPlainText(activeSongModel);
            } finally {
              isInternalSyncing = false;
            }
          }, 250);
        });
      }
    }

    // Guaranteed Bulletproof Tab Switching Mechanism
    function switchPreviewTab(targetPtabId) {
      const allBtns = document.querySelectorAll('.preview-tab-btn');
      const allPanes = document.querySelectorAll('.ptab-content');

      allBtns.forEach(btn => {
        if (btn.dataset.ptab === targetPtabId) btn.classList.add('active');
        else btn.classList.remove('active');
      });

      allPanes.forEach(pane => {
        if (pane.id === targetPtabId) {
          pane.style.setProperty('display', 'block', 'important');
        } else {
          pane.style.setProperty('display', 'none', 'important');
        }
      });
    }

    // Bind click directly to container and document
    document.addEventListener('click', (e) => {
      const btn = e.target.closest('.preview-tab-btn');
      if (!btn) return;
      e.preventDefault();
      e.stopPropagation();
      const targetPtab = btn.dataset.ptab;
      if (targetPtab) switchPreviewTab(targetPtab);
    });

    // Initialize 2-way sync
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', setupTwoWaySyncListeners);
    } else {
      setupTwoWaySyncListeners();
    }"""

assert old_sync_and_tabs in text, "old_sync_and_tabs not matched"
text = text.replace(old_sync_and_tabs, new_sync_and_tabs)

with open('data/admin.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("Advanced DP alignment and two-way real-time editor successfully patched!")
