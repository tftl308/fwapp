# -*- coding: utf-8 -*-
import json
import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# =========================================================================
# 1. PWA MANIFEST: standalone / window-controls-overlay / separate window
# =========================================================================
manifest_path = 'manifest.webmanifest'
with open(manifest_path, 'r', encoding='utf-8') as mf:
    m_data = json.load(mf)

m_data["display_override"] = ["window-controls-overlay", "standalone", "fullscreen", "browser"]
m_data["display"] = "standalone"
m_data["launch_handler"] = { "client_mode": "focus-existing" }

with open(manifest_path, 'w', encoding='utf-8') as mf:
    json.dump(m_data, mf, indent=2, ensure_ascii=False)
print("Updated manifest.webmanifest with display_override and launch_handler")

# =========================================================================
# 2. SEARCH ENGINE RELEVANCE RANKING:
# 1. Максимальное количество слов в названии (title)
# 2. Максимальное количество слов в тексте (body)
# 3. Одно из слов найдено в названии
# 4. Одно из слов найдено в тексте
# =========================================================================
pos_start = html.find('const scored = [];')
pos_end = html.find('return scored.map(s => s.song);', pos_start) + len('return scored.map(s => s.song);')
assert pos_start != -1 and pos_end != -1, "Search loop not found"

search_engine_new = """const scored = [];

    for (const doc of candidates) {
      let titleMatchesCount = 0;
      let bodyMatchesCount = 0;
      let anyMatch = false;
      let score = 0;

      for (const term of terms) {
        let matchedInTitle = false;
        let matchedInBody = false;

        // ID номер песни
        if (term === doc.normId || term === doc.numId) {
          matchedInTitle = true;
          score += 500;
        }

        // Поиск в названии
        if (doc.normTitle.includes(term)) {
          matchedInTitle = true;
          score += 150;
        } else {
          for (const tw of doc.titleWords) {
            if (term.length >= 3 && isSubsequence(term, tw)) {
              matchedInTitle = true;
              score += 100;
              break;
            }
            if (term.length >= 3 && damerauLevenshtein(term, tw) <= (term.length >= 5 ? 2 : 1)) {
              matchedInTitle = true;
              score += 90;
              break;
            }
          }
        }

        // Поиск в тексте
        if (doc.normBody.includes(term)) {
          matchedInBody = true;
          score += 30;
        } else {
          for (const aw of doc.allWords) {
            if (term.length >= 3 && isSubsequence(term, aw)) {
              matchedInBody = true;
              score += 20;
              break;
            }
            if (term.length >= 3 && damerauLevenshtein(term, aw) <= (term.length >= 5 ? 2 : 1)) {
              matchedInBody = true;
              score += 15;
              break;
            }
          }
        }

        if (matchedInTitle) titleMatchesCount++;
        if (matchedInBody) bodyMatchesCount++;
        if (matchedInTitle || matchedInBody) anyMatch = true;
      }

      if (anyMatch) {
        // СТРОГАЯ ИЕРАРХИЯ РЕЛЕВАНТНОСТИ:
        // 1. Максимальное число совпадений в названии (titleMatchesCount * 10000)
        // 2. Максимальное число совпадений в тексте (bodyMatchesCount * 1000)
        // 3. Дополнительные баллы за точность
        let tierScore = (titleMatchesCount * 10000) + (bodyMatchesCount * 1000);
        if (doc.normTitle.includes(normalizedClean)) tierScore += 5000;
        else if (doc.normBody.includes(normalizedClean)) tierScore += 500;

        scored.push({ song: doc.song, score: tierScore + score });
      }
    }

    scored.sort((a, b) => b.score - a.score);
    return scored.map(s => s.song);"""

html = html[:pos_start] + search_engine_new + html[pos_end:]

# =========================================================================
# 3. FILTER / SORT ICON NEXT TO "А-Я" IN CATALOG HEADER
# =========================================================================
cat_header_old = """    const leftHeader = Renderer.createElement('div', { className: 'split-col-header' }, [
      Renderer.createElement('strong', { className: 'text-main' }, ['Каталог песен (' + state.songs.length + ')']),
      Renderer.createElement('span', { className: 'text-sm text-muted' }, ['А–Я'])
    ]);"""

cat_header_new = """    const leftHeader = Renderer.createElement('div', { className: 'split-col-header flex items-center justify-between' }, [
      Renderer.createElement('strong', { className: 'text-main' }, ['Каталог песен (' + state.songs.length + ')']),
      Renderer.createElement('div', { className: 'flex items-center gap-2' }, [
        Renderer.createElement('span', { className: 'text-sm text-muted', style: 'font-weight: 700;' }, ['А–Я']),
        Renderer.createElement('button', {
          className: 'btn btn-icon btn-outline btn-sm',
          dataset: { action: 'toggle-catalog-sort-filter' },
          title: 'Фильтрация и сортировка каталога',
          style: 'padding: 0.2rem 0.4rem; font-size: 0.95rem; min-width: 28px; min-height: 28px;'
        }, ['⚡ ▾'])
      ])
    ]);"""

assert cat_header_old in html, "cat_header_old pattern not found"
html = html.replace(cat_header_old, cat_header_new)

# Add handler for toggle-catalog-sort-filter
sort_filter_handler = """      case 'toggle-catalog-sort-filter': {
        const options = ['По названию (А–Я)', 'По номеру (ID 0001–0700)', 'Только с фонограммами (Audio)', 'Только с текстом'];
        const choice = prompt('Сортировка и фильтрация каталога:\\n1. По названию (А–Я)\\n2. По номеру (ID)\\n3. Только с фонограммами\\n4. Только с текстом\\n\\nВведите номер (1-4):', '1');
        if (choice === '2') {
          const sorted = [...state.songs].sort((a, b) => parseInt(a.id, 10) - parseInt(b.id, 10));
          store.setState({ songs: sorted });
          AppController.showToast('Каталог отсортирован по номеру ID');
        } else if (choice === '3') {
          const audioSongIds = new Set(state.audio.map(a => a.song_id));
          const filtered = state.songs.filter(s => audioSongIds.has(s.id));
          this.searchEngine = new SearchEngine(filtered);
          store.setState({ songs: filtered });
          AppController.showToast('Отфильтровано: ' + filtered.length + ' песен с аудио');
        } else if (choice === '4') {
          const filtered = state.songs.filter(s => s.body_plain && s.body_plain.trim());
          this.searchEngine = new SearchEngine(filtered);
          store.setState({ songs: filtered });
          AppController.showToast('Отфильтровано: ' + filtered.length + ' песен с текстом');
        } else if (choice === '1') {
          const sorted = [...state.songs].sort((a, b) => a.title.localeCompare(b.title, 'ru'));
          store.setState({ songs: sorted });
          AppController.showToast('Каталог отсортирован по алфавиту (А–Я)');
        }
        break;
      }
      case 'open-song': {"""

assert "case 'open-song': {" in html, "case 'open-song' not found"
html = html.replace("case 'open-song': {", sort_filter_handler)

# =========================================================================
# 4. FIX CONCERT MODE:
# - Do NOT delete lines without chords! Output lyrics line cleanly even without chords.
# - Reset transpose to +0 button
# - Line-spacing control (- / +) in concert settings modal
# =========================================================================
render_lines_old = """        // В режиме концерта: убираем строки, где нет ни одного аккорда!
        if (isConcertMode) {
          const hasAnyChord = line.units && line.units.some(u => u.chord && u.chord.trim().length > 0);
          if (!hasAnyChord) continue;
        }"""

render_lines_new = """        // В режиме концерта: выводим ВСЕ строки текста (и с аккордами, и без них),
        // но без лишней высоты над блоком если аккордов нет!"""

assert render_lines_old in html, "render_lines_old pattern not found"
html = html.replace(render_lines_old, render_lines_new)

# Add line spacing control & transpose reset button in concert modal:
modal_transp_old = """    // Тональность
    const transpRow = Renderer.createElement('div', { style: 'display: flex; justify-content: space-between; align-items: center;' }, [
      Renderer.createElement('span', { style: 'font-weight: 600;' }, ['Тональность']),
      Renderer.createElement('div', { style: 'display: flex; gap: 0.5rem;' }, [
        Renderer.createElement('button', { className: 'btn btn-outline btn-sm', dataset: { action: 'concert-transpose-minus' } }, ['-1']),
        Renderer.createElement('button', { className: 'btn btn-outline btn-sm', dataset: { action: 'concert-transpose-plus' } }, ['+1'])
      ])
    ]);
    box.appendChild(transpRow);"""

modal_transp_new = """    // Тональность
    const transpRow = Renderer.createElement('div', { style: 'display: flex; justify-content: space-between; align-items: center;' }, [
      Renderer.createElement('span', { style: 'font-weight: 600;' }, ['Тональность']),
      Renderer.createElement('div', { style: 'display: flex; gap: 0.35rem; align-items: center;' }, [
        Renderer.createElement('button', { className: 'btn btn-outline btn-sm', dataset: { action: 'concert-transpose-minus' } }, ['-1']),
        Renderer.createElement('button', { className: 'btn btn-outline btn-sm', dataset: { action: 'concert-transpose-reset' }, title: 'Сбросить в исходную тональность' }, ['+0']),
        Renderer.createElement('button', { className: 'btn btn-outline btn-sm', dataset: { action: 'concert-transpose-plus' } }, ['+1'])
      ])
    ]);
    box.appendChild(transpRow);

    // Межстрочный интервал
    const spacingRow = Renderer.createElement('div', { style: 'display: flex; justify-content: space-between; align-items: center;' }, [
      Renderer.createElement('span', { style: 'font-weight: 600;' }, ['Интервал строк']),
      Renderer.createElement('div', { style: 'display: flex; gap: 0.35rem;' }, [
        Renderer.createElement('button', { className: 'btn btn-outline btn-sm', dataset: { action: 'concert-spacing-minus' }, title: 'Уменьшить интервал' }, ['Плотнее']),
        Renderer.createElement('button', { className: 'btn btn-outline btn-sm', dataset: { action: 'concert-spacing-plus' }, title: 'Увеличить интервал' }, ['Шире'])
      ])
    ]);
    box.appendChild(spacingRow);"""

assert modal_transp_old in html, "modal_transp_old pattern not found"
html = html.replace(modal_transp_old, modal_transp_new)

# Add action handlers for concert-transpose-reset, concert-spacing-minus, concert-spacing-plus
handler_old = """      } else if (act === 'concert-transpose-minus') {
        window.appController.currentSongTranspose = (window.appController.currentSongTranspose || 0) - 1;
        window.appController.renderConcertSong(false);
      } else if (act === 'concert-transpose-plus') {
        window.appController.currentSongTranspose = (window.appController.currentSongTranspose || 0) + 1;
        window.appController.renderConcertSong(false);"""

handler_new = """      } else if (act === 'concert-transpose-minus') {
        window.appController.currentSongTranspose = (window.appController.currentSongTranspose || 0) - 1;
        window.appController.renderConcertSong(false);
      } else if (act === 'concert-transpose-reset') {
        window.appController.currentSongTranspose = 0;
        window.appController.renderConcertSong(false);
      } else if (act === 'concert-transpose-plus') {
        window.appController.currentSongTranspose = (window.appController.currentSongTranspose || 0) + 1;
        window.appController.renderConcertSong(false);
      } else if (act === 'concert-spacing-minus') {
        let cur = parseFloat(document.documentElement.style.getPropertyValue('--concert-line-margin')) || 0.2;
        cur = Math.max(0.05, cur - 0.05);
        document.documentElement.style.setProperty('--concert-line-margin', cur.toFixed(2) + 'rem');
      } else if (act === 'concert-spacing-plus') {
        let cur = parseFloat(document.documentElement.style.getPropertyValue('--concert-line-margin')) || 0.2;
        cur = Math.min(0.8, cur + 0.05);
        document.documentElement.style.setProperty('--concert-line-margin', cur.toFixed(2) + 'rem');"""

assert handler_old in html, "handler_old pattern not found"
html = html.replace(handler_old, handler_new)

# =========================================================================
# 5. CHORD FINGERING DIAGRAMS (Аппликатура аккордов):
# Click chord in song detail view -> show finger diagram modal
# Disabled in concert mode!
# =========================================================================

chord_diagram_db_script = """// ВСТРОЕННАЯ БАЗА АППЛИКАТУРЫ ГИТАРНЫХ АККОРДОВ
const GUITAR_CHORD_FINGERINGS = {
  "C": { frets: [-1, 3, 2, 0, 1, 0], fingers: [0, 3, 2, 0, 1, 0], baseFret: 1 },
  "Cm": { frets: [-1, 3, 5, 5, 4, 3], fingers: [0, 1, 3, 4, 2, 1], baseFret: 3, barres: [3] },
  "C7": { frets: [-1, 3, 2, 3, 1, 0], fingers: [0, 3, 2, 4, 1, 0], baseFret: 1 },
  "D": { frets: [-1, -1, 0, 2, 3, 2], fingers: [0, 0, 0, 1, 3, 2], baseFret: 1 },
  "Dm": { frets: [-1, -1, 0, 2, 3, 1], fingers: [0, 0, 0, 2, 3, 1], baseFret: 1 },
  "D7": { frets: [-1, -1, 0, 2, 1, 2], fingers: [0, 0, 0, 2, 1, 3], baseFret: 1 },
  "Dsus4": { frets: [-1, -1, 0, 2, 3, 3], fingers: [0, 0, 0, 1, 3, 4], baseFret: 1 },
  "D/F#": { frets: [2, 0, 0, 2, 3, 2], fingers: [1, 0, 0, 2, 4, 3], baseFret: 1 },
  "E": { frets: [0, 2, 2, 1, 0, 0], fingers: [0, 2, 3, 1, 0, 0], baseFret: 1 },
  "Em": { frets: [0, 2, 2, 0, 0, 0], fingers: [0, 2, 3, 0, 0, 0], baseFret: 1 },
  "E7": { frets: [0, 2, 0, 1, 0, 0], fingers: [0, 2, 0, 1, 0, 0], baseFret: 1 },
  "Esus4": { frets: [0, 2, 2, 2, 0, 0], fingers: [0, 2, 3, 4, 0, 0], baseFret: 1 },
  "F": { frets: [1, 3, 3, 2, 1, 1], fingers: [1, 3, 4, 2, 1, 1], baseFret: 1, barres: [1] },
  "Fm": { frets: [1, 3, 3, 1, 1, 1], fingers: [1, 3, 4, 1, 1, 1], baseFret: 1, barres: [1] },
  "F7": { frets: [1, 3, 1, 2, 1, 1], fingers: [1, 3, 1, 2, 1, 1], baseFret: 1, barres: [1] },
  "F#": { frets: [2, 4, 4, 3, 2, 2], fingers: [1, 3, 4, 2, 1, 1], baseFret: 2, barres: [2] },
  "F#m": { frets: [2, 4, 4, 2, 2, 2], fingers: [1, 3, 4, 1, 1, 1], baseFret: 2, barres: [2] },
  "F#7": { frets: [2, 4, 2, 3, 2, 2], fingers: [1, 3, 1, 2, 1, 1], baseFret: 2, barres: [2] },
  "G": { frets: [3, 2, 0, 0, 0, 3], fingers: [2, 1, 0, 0, 0, 3], baseFret: 1 },
  "Gm": { frets: [3, 5, 5, 3, 3, 3], fingers: [1, 3, 4, 1, 1, 1], baseFret: 3, barres: [3] },
  "G7": { frets: [3, 2, 0, 0, 0, 1], fingers: [3, 2, 0, 0, 0, 1], baseFret: 1 },
  "A": { frets: [-1, 0, 2, 2, 2, 0], fingers: [0, 0, 1, 2, 3, 0], baseFret: 1 },
  "Am": { frets: [-1, 0, 2, 2, 1, 0], fingers: [0, 0, 2, 3, 1, 0], baseFret: 1 },
  "A7": { frets: [-1, 0, 2, 0, 2, 0], fingers: [0, 0, 2, 0, 3, 0], baseFret: 1 },
  "Asus4": { frets: [-1, 0, 2, 2, 3, 0], fingers: [0, 0, 1, 2, 4, 0], baseFret: 1 },
  "A/C#": { frets: [-1, 4, 2, 2, 2, 0], fingers: [0, 4, 1, 2, 3, 0], baseFret: 1 },
  "B": { frets: [-1, 2, 4, 4, 4, 2], fingers: [0, 1, 2, 3, 4, 1], baseFret: 2, barres: [2] },
  "Bm": { frets: [-1, 2, 4, 4, 3, 2], fingers: [0, 1, 3, 4, 2, 1], baseFret: 2, barres: [2] },
  "H": { frets: [-1, 2, 4, 4, 4, 2], fingers: [0, 1, 2, 3, 4, 1], baseFret: 2, barres: [2] },
  "Hm": { frets: [-1, 2, 4, 4, 3, 2], fingers: [0, 1, 3, 4, 2, 1], baseFret: 2, barres: [2] },
  "Bb": { frets: [-1, 1, 3, 3, 3, 1], fingers: [0, 1, 2, 3, 4, 1], baseFret: 1, barres: [1] },
  "Bbm": { frets: [-1, 1, 3, 3, 2, 1], fingers: [0, 1, 3, 4, 2, 1], baseFret: 1, barres: [1] }
};

function renderChordSvg(chordName) {
  const normChord = chordName.trim().replace(/h/i, 'H');
  const chordData = GUITAR_CHORD_FINGERINGS[normChord] || GUITAR_CHORD_FINGERINGS[normChord.replace(/m$/, '')] || null;

  if (!chordData) {
    return `<div style="text-align: center; padding: 1rem; color: var(--text-muted);">Аппликатура для аккорда <strong>${chordName}</strong> в разработке</div>`;
  }

  const { frets, baseFret, barres } = chordData;
  const startX = 25;
  const startY = 30;
  const stringDist = 18;
  const fretDist = 22;
  const width = startX * 2 + stringDist * 5;
  const height = startY + fretDist * 5 + 15;

  let svg = `<svg width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" style="display:block; margin: 0 auto;">`;
  svg += `<text x="${width / 2}" y="18" text-anchor="middle" font-weight="bold" font-size="14" fill="currentColor">${normChord}</text>`;

  if (baseFret > 1) {
    svg += `<text x="${startX - 12}" y="${startY + 15}" font-size="11" fill="currentColor">${baseFret}fr</text>`;
  }

  // Лады (горизонтальные линии)
  for (let f = 0; f <= 4; f++) {
    const y = startY + f * fretDist;
    const strokeW = (f === 0 && baseFret === 1) ? 3 : 1;
    svg += `<line x1="${startX}" y1="${y}" x2="${startX + stringDist * 5}" y2="${y}" stroke="currentColor" stroke-width="${strokeW}"/>`;
  }

  // Струны (вертикальные линии)
  for (let s = 0; s < 6; s++) {
    const x = startX + s * stringDist;
    svg += `<line x1="${x}" y1="${startY}" x2="${x}" y2="${startY + fretDist * 4}" stroke="currentColor" stroke-width="1"/>`;
  }

  // Баррэ
  if (barres && barres.length > 0) {
    const barreFret = barres[0];
    const y = startY + (barreFret - 0.5) * fretDist;
    svg += `<rect x="${startX - 2}" y="${y - 4}" width="${stringDist * 5 + 4}" height="8" rx="4" fill="var(--chord-color)"/>`;
  }

  // Пальцы / открытые струны / крестики
  frets.forEach((fret, sIdx) => {
    const x = startX + sIdx * stringDist;
    if (fret === -1) {
      svg += `<text x="${x}" y="${startY - 5}" text-anchor="middle" font-size="11" fill="var(--text-muted)">✕</text>`;
    } else if (fret === 0) {
      svg += `<circle cx="${x}" cy="${startY - 7}" r="3.5" fill="none" stroke="currentColor" stroke-width="1.2"/>`;
    } else {
      const y = startY + (fret - 0.5) * fretDist;
      svg += `<circle cx="${x}" cy="${y}" r="5.5" fill="var(--chord-color)"/>`;
    }
  });

  svg += `</svg>`;
  return svg;
}
"""

# Insert chord diagram script before class SongParser
html = html.replace('class SongParser {', chord_diagram_db_script + '\nclass SongParser {')

# Make chords clickable in detail view (with data-action="show-chord-diagram")
chord_div_target = """          const unitBlock = Renderer.createElement('div', { className: 'syllable-chord-block' });
          const chordDiv = Renderer.createElement('div', { className: 'syllable-chord' }, [unit.chord || ' ']);"""

chord_div_replacement = """          const unitBlock = Renderer.createElement('div', { className: 'syllable-chord-block' });
          const chordAttrs = { className: 'syllable-chord' };
          // В режиме просмотра песни (не концерт) делаем аккорды интерактивными для просмотра аппликатуры
          if (!isConcertMode && unit.chord && unit.chord.trim()) {
            chordAttrs.style = 'cursor: pointer; text-decoration: underline dotted 1px;';
            chordAttrs.dataset = { action: 'show-chord-diagram', chordName: unit.chord.trim() };
            chordAttrs.title = 'Нажмите, чтобы увидеть аппликатуру аккорда на грифе';
          }
          const chordDiv = Renderer.createElement('div', chordAttrs, [unit.chord || ' ']);"""

assert chord_div_target in html, "chord_div_target not found"
html = html.replace(chord_div_target, chord_div_replacement)

# Add show-chord-diagram handler in handleAction
action_switch_target = """      case 'open-song': {"""

action_switch_replacement = """      case 'show-chord-diagram': {
        const chordName = el.dataset.chordName;
        if (!chordName) break;
        const existing = document.getElementById('chord-diagram-modal');
        if (existing) existing.remove();

        const modal = Renderer.createElement('div', {
          id: 'chord-diagram-modal',
          className: 'qr-modal-overlay',
          style: 'display: flex; z-index: 300;',
          dataset: { action: 'close-chord-diagram' }
        });
        const box = Renderer.createElement('div', {
          className: 'update-modal-box',
          style: 'background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; padding: 1.25rem; max-width: 280px; width: 85%; display: flex; flex-direction: column; gap: 0.75rem; box-shadow: 0 10px 25px rgba(0,0,0,0.4); text-align: center;'
        });
        box.addEventListener('click', (e) => e.stopPropagation());

        box.appendChild(Renderer.createElement('div', { style: 'display: flex; justify-content: space-between; align-items: center;' }, [
          Renderer.createElement('h3', { style: 'margin: 0; font-size: 1.1rem; color: var(--accent);' }, ['Аппликатура: ' + chordName]),
          Renderer.createElement('button', { className: 'btn btn-outline btn-sm', dataset: { action: 'close-chord-diagram' } }, ['✕'])
        ]));

        const svgWrap = Renderer.createElement('div', { style: 'margin: 0.5rem 0;' });
        svgWrap.innerHTML = renderChordSvg(chordName);
        box.appendChild(svgWrap);

        box.appendChild(Renderer.createElement('button', {
          className: 'btn btn-outline btn-sm',
          dataset: { action: 'close-chord-diagram' },
          style: 'width: 100%;'
        }, ['Закрыть']));

        modal.appendChild(box);
        document.body.appendChild(modal);
        break;
      }
      case 'close-chord-diagram': {
        const m = document.getElementById('chord-diagram-modal');
        if (m) m.remove();
        break;
      }
      case 'open-song': {"""

assert action_switch_target in html, "action_switch_target not found"
html = html.replace(action_switch_target, action_switch_replacement)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("=== index.html successfully updated with all new requested features! ===")
