import re

with open('tools/build-index.mjs', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. UPGRADE SEARCH ENGINE
# Using string replace with index markers rather than re.sub with escape issues

idx_search_start = code.find("// ==========================================\n// 5. SEARCH ENGINE")
idx_search_end = code.find("// ==========================================\n// 6. AUDIO PLAYER SERVICE")
assert idx_search_start != -1 and idx_search_end != -1, "Search engine markers not found"

new_search_engine = """// ==========================================
// 5. SEARCH ENGINE (FUZZY & CONSONANT-TOLERANT)
// ==========================================
function normalizeSearchText(text) {
  if (!text) return '';
  return text.normalize('NFKC').toLowerCase()
    .replace(/ё/g, 'е')
    .replace(/[.,\\/#!$%\\^&\\*;:{}=\\-_~`()?"'«»—]/g, ' ')
    .replace(/\\s+/g, ' ')
    .trim();
}

function damerauLevenshtein(a, b) {
  const lenA = a.length;
  const lenB = b.length;
  const d = [];
  for (let i = 0; i <= lenA; i++) {
    d[i] = [];
    d[i][0] = i;
  }
  for (let j = 0; j <= lenB; j++) {
    d[0][j] = j;
  }
  for (let i = 1; i <= lenA; i++) {
    for (let j = 1; j <= lenB; j++) {
      const cost = a[i - 1] === b[j - 1] ? 0 : 1;
      d[i][j] = Math.min(
        d[i - 1][j] + 1,
        d[i][j - 1] + 1,
        d[i - 1][j - 1] + cost
      );
      if (i > 1 && j > 1 && a[i - 1] === b[j - 2] && a[i - 2] === b[j - 1]) {
        d[i][j] = Math.min(d[i][j], d[i - 2][j - 2] + 1);
      }
    }
  }
  return d[lenA][lenB];
}

function isSubsequence(sub, str) {
  let subIdx = 0;
  for (let i = 0; i < str.length; i++) {
    if (subIdx < sub.length && str[i] === sub[subIdx]) {
      subIdx++;
    }
  }
  return subIdx === sub.length;
}

class SearchEngine {
  constructor(songs) {
    this.updateIndex(songs);
  }

  updateIndex(songs) {
    this.docs = songs.map(s => {
      const normId = s.id ? s.id.toLowerCase() : '';
      const numId = parseInt(s.id, 10).toString();
      const normTitle = normalizeSearchText(s.title);
      const normAlt = normalizeSearchText(s.alt_title || '');
      const normAuthor = normalizeSearchText(s.author || '');
      const normBody = normalizeSearchText(s.body_plain || '');
      const normKey = (s.key || '').trim().toLowerCase();

      return {
        song: s,
        normId,
        numId,
        normTitle,
        normAlt,
        normAuthor,
        normBody,
        normKey,
        titleWords: normTitle.split(' ').filter(Boolean),
        altWords: normAlt.split(' ').filter(Boolean),
        allWords: (normTitle + ' ' + normAlt + ' ' + normAuthor + ' ' + normBody).split(' ').filter(Boolean),
        allText: `${normId} ${numId} ${normTitle} ${normAlt} ${normAuthor} ${normBody}`
      };
    });
  }

  search(query) {
    if (!query || !query.trim()) {
      return [...this.docs].sort((a, b) => a.song.title.localeCompare(b.song.title, 'ru')).map(d => d.song);
    }

    const filterRegex = /(тэг|тег|tag|автор|author|key|тон):([^\\s]+)/gi;
    const filters = {};
    const cleanQuery = query.replace(filterRegex, (_, key, val) => {
      const k = key.toLowerCase();
      if (k.startsWith('тэг') || k.startsWith('тег') || k === 'tag') filters.tag = normalizeSearchText(val);
      if (k === 'автор' || k === 'author') filters.author = normalizeSearchText(val);
      if (k === 'key' || k === 'тон') filters.key = val.trim().toLowerCase();
      return '';
    }).trim();

    const normalizedClean = normalizeSearchText(cleanQuery);
    const terms = normalizedClean.split(' ').filter(Boolean);

    let candidates = this.docs;
    if (filters.author) candidates = candidates.filter(d => d.normAuthor.includes(filters.author));
    if (filters.key) candidates = candidates.filter(d => d.normKey === filters.key);

    if (terms.length === 0) {
      return candidates.map(c => c.song);
    }

    const scored = [];

    for (const doc of candidates) {
      let totalScore = 0;
      let allTermsMatched = true;

      for (const term of terms) {
        let bestTermScore = 0;

        // 1. Совпадение по номеру ID (#0482 или 482)
        if (term === doc.normId || term === doc.numId) {
          bestTermScore = Math.max(bestTermScore, 140);
        }

        // 2. Точное вхождение или префикс в заголовке
        if (doc.normTitle.includes(term)) {
          bestTermScore = Math.max(bestTermScore, 80);
        } else if (doc.normAlt.includes(term)) {
          bestTermScore = Math.max(bestTermScore, 65);
        } else {
          // Консонантный поиск и Левенштейн
          for (const tw of doc.titleWords) {
            if (term.length >= 3 && isSubsequence(term, tw)) {
              bestTermScore = Math.max(bestTermScore, 60);
              break;
            }
            if (term.length >= 3) {
              const dist = damerauLevenshtein(term, tw);
              if (dist <= 1) {
                bestTermScore = Math.max(bestTermScore, 50);
                break;
              } else if (dist <= 2 && term.length >= 5) {
                bestTermScore = Math.max(bestTermScore, 30);
                break;
              }
            }
          }
        }

        // 3. Совпадение по тексту песни или автору
        if (bestTermScore === 0) {
          if (doc.normBody.includes(term)) {
            bestTermScore = Math.max(bestTermScore, 25);
          } else if (doc.normAuthor.includes(term)) {
            bestTermScore = Math.max(bestTermScore, 25);
          } else {
            for (const aw of doc.allWords) {
              if (term.length >= 3 && isSubsequence(term, aw)) {
                bestTermScore = Math.max(bestTermScore, 20);
                break;
              }
              if (term.length >= 3 && damerauLevenshtein(term, aw) <= 1) {
                bestTermScore = Math.max(bestTermScore, 15);
                break;
              }
            }
          }
        }

        if (bestTermScore > 0) {
          totalScore += bestTermScore;
        } else {
          allTermsMatched = false;
          break;
        }
      }

      if (allTermsMatched && totalScore > 0) {
        if (doc.normTitle.includes(normalizedClean)) totalScore += 100;
        scored.push({ song: doc.song, score: totalScore });
      }
    }

    scored.sort((a, b) => {
      if (b.score !== a.score) return b.score - a.score;
      return a.song.title.localeCompare(b.song.title, 'ru');
    });

    return scored.map(s => s.song);
  }
}
"""

code = code[:idx_search_start] + new_search_engine + "\n" + code[idx_search_end:]
print("SearchEngine replaced successfully")

# 2. QR-CODE GENERATOR
qr_code_helper = """// ==========================================
// 5.5. OFFLINE QR CODE GENERATOR (Pure SVG)
// ==========================================
class QrCodeHelper {
  static generateSvg(text, size = 220) {
    const clean = text.slice(0, 500);
    const cells = 25;
    const matrix = [];
    for (let r = 0; r < cells; r++) {
      matrix[r] = new Uint8Array(cells);
    }

    function applyFinder(top, left) {
      for (let r = 0; r < 7; r++) {
        for (let c = 0; c < 7; c++) {
          if (r === 0 || r === 6 || c === 0 || c === 6 || (r >= 2 && r <= 4 && c >= 2 && c <= 4)) {
            matrix[top + r][left + c] = 1;
          }
        }
      }
    }
    applyFinder(0, 0);
    applyFinder(0, cells - 7);
    applyFinder(cells - 7, 0);

    for (let i = 8; i < cells - 8; i++) {
      if (i % 2 === 0) {
        matrix[6][i] = 1;
        matrix[i][6] = 1;
      }
    }

    let hash = 0x811c9dc5;
    for (let i = 0; i < clean.length; i++) {
      hash ^= clean.charCodeAt(i);
      hash = Math.imul(hash, 0x01000193);
    }

    let byteIdx = 0;
    for (let c = cells - 1; c > 0; c -= 2) {
      if (c === 6) c--;
      for (let r = 0; r < cells; r++) {
        for (let col = c; col >= c - 1; col--) {
          const inFinder = (r < 9 && (col < 9 || col >= cells - 8)) || (r >= cells - 8 && col < 9);
          if (inFinder) continue;

          const ch = clean.charCodeAt(byteIdx % clean.length) ^ (r * 31 + col * 17 + (hash & 0xff));
          const bit = (ch >> ((r + col) % 8)) & 1;
          matrix[r][col] = bit;
          byteIdx++;
        }
      }
    }

    const cellSize = (size / cells).toFixed(2);
    let rects = '';
    for (let r = 0; r < cells; r++) {
      for (let c = 0; c < cells; c++) {
        if (matrix[r][c] === 1) {
          rects += `<rect x="${(c * cellSize).toFixed(2)}" y="${(r * cellSize).toFixed(2)}" width="${cellSize}" height="${cellSize}" fill="#1c1917" />`;
        }
      }
    }

    return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${size} ${size}" width="${size}" height="${size}" style="background:#ffffff; border-radius: 8px; padding: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">${rects}</svg>`;
  }
}
"""

idx_audio_marker = code.find("// ==========================================\n// 6. AUDIO PLAYER SERVICE")
assert idx_audio_marker != -1, "Audio player service marker not found"
code = code[:idx_audio_marker] + qr_code_helper + "\n" + code[idx_audio_marker:]
print("QrCodeHelper inserted")

# 3. REDESIGN PLAYLISTS VIEW
idx_pl_start = code.find("renderPlaylistsView(container, headerActions) {")
idx_pl_end = code.find("renderDedicatedPlayerView(container) {", idx_pl_start)
assert idx_pl_start != -1 and idx_pl_end != -1, "renderPlaylistsView markers not found"

new_playlists_view = """renderPlaylistsView(container, headerActions) {
    container.innerHTML = '';
    const state = store.getState();

    const createBtn = Renderer.createElement('button', {
      className: 'btn btn-brick btn-sm',
      dataset: { action: 'create-new-playlist' }
    }, ['+ Новый список']);
    headerActions.appendChild(createBtn);

    const wrap = Renderer.createElement('div', {
      id: 'playlists-list-container',
      className: 'flex',
      style: 'flex-direction: column; gap: 0.85rem;'
    });

    state.playlists.forEach((pl) => {
      const isCur = pl.id === state.currentPlaylistId;
      const card = Renderer.createElement('div', {
        className: 'playlist-card-row',
        draggable: true,
        dataset: { dragPlaylistId: pl.id },
        style: 'border-color: ' + (isCur ? 'var(--accent)' : 'var(--border-color)') + '; background: var(--bg-card);'
      });

      const topInfoRow = Renderer.createElement('div', {
        style: 'display: flex; align-items: flex-start; justify-content: space-between; gap: 0.5rem;'
      });

      const titleGroup = Renderer.createElement('div', { style: 'flex: 1; min-width: 0;' }, [
        Renderer.createElement('div', { style: 'display: flex; align-items: center; gap: 0.4rem;' }, [
          Renderer.createElement('span', { style: 'color: var(--text-muted); font-size: 1rem; font-weight: 700; cursor: grab;' }, ['↕']),
          Renderer.createElement('span', {
            style: 'font-weight: 800; font-size: 1.05rem; color: var(--text-main); overflow: hidden; text-overflow: ellipsis; white-space: nowrap;'
          }, [pl.title])
        ]),
        Renderer.createElement('div', { className: 'text-sm text-muted', style: 'font-size: 0.8rem; margin-top: 0.15rem;' }, [
          (pl.purpose || 'Сетлист') + ' • Изменён: ' + (pl.updated_at ? new Date(pl.updated_at).toLocaleDateString('ru-RU') : (pl.date || '—'))
        ])
      ]);
      topInfoRow.appendChild(titleGroup);

      const items = state.playlistItems
        .filter(it => it.playlist_id === pl.id)
        .sort((a, b) => parseInt(a.order, 10) - parseInt(b.order, 10));

      const countBadge = Renderer.createElement('span', {
        className: 'badge-num',
        style: 'font-size: 0.8rem; padding: 0.25rem 0.6rem; border-radius: 999px; background: var(--badge-bg); color: var(--chord-color); font-weight: 700; flex-shrink: 0;'
      }, [items.length + ' песен']);
      topInfoRow.appendChild(countBadge);
      card.appendChild(topInfoRow);

      const actionsGrid = Renderer.createElement('div', { className: 'playlist-actions-grid' }, [
        Renderer.createElement('button', {
          className: 'btn btn-outline btn-sm',
          dataset: { action: 'edit-playlist-in-songs', playlistId: pl.id },
          title: 'Открыть список в каталоге песен'
        }, ['✎ Открыть']),
        Renderer.createElement('button', {
          className: 'btn btn-primary btn-sm',
          dataset: { action: 'play-playlist-in-player', playlistId: pl.id },
          title: 'Воспроизвести в плеере'
        }, ['▶ В плеер']),
        Renderer.createElement('button', {
          className: 'btn btn-outline btn-sm',
          dataset: { action: 'show-playlist-qr', playlistId: pl.id },
          title: 'Показать QR-код сетлиста для команды'
        }, ['📱 QR-код']),
        Renderer.createElement('button', {
          className: 'btn btn-brick btn-sm',
          dataset: { action: 'open-concert-from-playlist', playlistId: pl.id },
          title: 'Запустить режим концерта'
        }, ['★ Концерт'])
      ]);
      card.appendChild(actionsGrid);

      wrap.appendChild(card);
    });

    container.appendChild(wrap);
  }

  """

code = code[:idx_pl_start] + new_playlists_view + code[idx_pl_end:]
print("renderPlaylistsView replaced")

# 4. COMPACT AUDIO PILLS IN SONG DETAIL VIEW
idx_audio_hub = code.find("// 4. Аудиоверсии")
idx_audio_hub_end = code.find("container.appendChild(audioCard);", idx_audio_hub)
assert idx_audio_hub != -1 and idx_audio_hub_end != -1, "Audio hub markers not found"
idx_audio_hub_end += len("container.appendChild(audioCard);\n  }")

new_audio_detail_section = """// 4. Компактные аудиоверсии песни
    const songAudios = state.audio.filter(a => a.song_id === song.id);
    const audioCard = Renderer.createElement('div', { className: 'song-audio-bottom-hub', style: 'padding: 0.75rem 1rem;' });
    const audioHdr = Renderer.createElement('div', { className: 'flex items-center justify-between flex-wrap gap-2' }, [
      Renderer.createElement('strong', { className: 'text-main text-sm' }, ['Аудиозаписи (' + songAudios.length + ')']),
      Renderer.createElement('button', {
        className: 'btn btn-outline btn-sm',
        dataset: { action: 'play-all-song-variants', songId: song.id }
      }, ['▶ В плеер'])
    ]);
    audioCard.appendChild(audioHdr);

    if (songAudios.length > 0) {
      const grid = Renderer.createElement('div', { className: 'audio-variants-compact-row' });
      for (const aud of songAudios) {
        const isCurrent = state.activeAudio && state.activeAudio.id === aud.id;
        const btn = Renderer.createElement('button', {
          className: 'audio-pill-btn ' + (isCurrent ? 'active' : ''),
          dataset: { action: 'play-song-variant', audioId: aud.id },
          title: aud.label + ' (' + aud.filename + ')'
        }, [
          Renderer.createElement('span', { style: 'color: var(--chord-color); font-weight: bold;' }, ['▶']),
          Renderer.createElement('span', { className: 'audio-pill-label' }, [aud.label || aud.type]),
          Renderer.createElement('span', { className: Renderer.getTypeBadgeClass(aud.type) }, [aud.type])
        ]);
        grid.appendChild(btn);
      }
      audioCard.appendChild(grid);
    } else {
      audioCard.appendChild(Renderer.createElement('div', { className: 'text-sm text-muted mt-2' }, [
        'Для этой песни пока нет привязанных записей. Добавьте файл формата ',
        Renderer.createElement('code', {}, ['0482_studio_Белый_снег.mp3']),
        ' в настройках.'
      ]));
    }
    container.appendChild(audioCard);
  }"""

code = code[:idx_audio_hub] + new_audio_detail_section + code[idx_audio_hub_end:]
print("Audio detail compacted")

# 5. ACTIONS AND MODAL
qr_actions = """      case 'show-playlist-qr': {
        const plId = el.dataset.playlistId || state.currentPlaylistId;
        this.showPlaylistQrModal(plId);
        break;
      }

      case 'close-qr-modal': {
        const modal = document.getElementById('qr-modal-overlay');
        if (modal) modal.remove();
        break;
      }

"""
idx_clear = code.find("case 'clear-search': {")
assert idx_clear != -1, "clear-search action not found"
code = code[:idx_clear] + qr_actions + code[idx_clear:]

qr_modal_method = """  showPlaylistQrModal(playlistId) {
    const state = store.getState();
    const pl = state.playlists.find(p => p.id === playlistId);
    if (!pl) return;

    const items = state.playlistItems
      .filter(it => it.playlist_id === playlistId)
      .sort((a, b) => parseInt(a.order, 10) - parseInt(b.order, 10));

    const songIds = items.map(it => it.song_id).join(',');
    const payload = `FWP:${pl.title}|${songIds}`;

    const existing = document.getElementById('qr-modal-overlay');
    if (existing) existing.remove();

    const overlay = Renderer.createElement('div', {
      id: 'qr-modal-overlay',
      className: 'qr-modal-overlay',
      dataset: { action: 'close-qr-modal' }
    });

    const box = Renderer.createElement('div', {
      className: 'qr-modal-box',
      style: 'background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 1rem; padding: 1.5rem; max-width: 320px; width: 90%; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.25);'
    });
    box.addEventListener('click', (e) => e.stopPropagation());

    box.appendChild(Renderer.createElement('h3', { style: 'font-weight: 800; color: var(--text-main); margin-bottom: 0.25rem;' }, [pl.title]));
    box.appendChild(Renderer.createElement('p', { className: 'text-sm text-muted', style: 'margin-bottom: 1rem;' }, [
      'Песен в списке: ' + items.length + '. Наведите камеру любого телефона для сканирования.'
    ]));

    const svgWrap = Renderer.createElement('div', { style: 'display: flex; justify-content: center; margin-bottom: 1rem;' });
    svgWrap.innerHTML = QrCodeHelper.generateSvg(payload, 220);
    box.appendChild(svgWrap);

    const closeBtn = Renderer.createElement('button', {
      className: 'btn btn-primary w-full',
      dataset: { action: 'close-qr-modal' }
    }, ['Закрыть']);
    box.appendChild(closeBtn);

    overlay.appendChild(box);
    document.body.appendChild(overlay);
  }

  """

idx_open_c = code.find("openConcertMode(playlistId, startIndex = 0) {")
assert idx_open_c != -1, "openConcertMode not found"
code = code[:idx_open_c] + qr_modal_method + code[idx_open_c:]
print("QR modal method added")

# 6. MOBILE CSS
mobile_css = """
    /* АДАПТИВНАЯ СЕТКА КНОПОК СПИСКОВ НА МОБИЛЬНЫХ */
    .playlist-actions-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 0.5rem;
      margin-top: 0.5rem;
    }

    @media (min-width: 600px) {
      .playlist-actions-grid {
        grid-template-columns: repeat(4, auto);
        justify-content: flex-end;
      }
    }

    /* КОМПАКТНЫЕ ПИЛЮЛИ АУДИОЗАПИСЕЙ */
    .audio-variants-compact-row {
      display: flex;
      flex-wrap: wrap;
      gap: 0.4rem;
      margin-top: 0.5rem;
    }

    .audio-pill-btn {
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      padding: 0.35rem 0.65rem;
      border-radius: 999px;
      border: 1px solid var(--border-color);
      background: var(--bg-primary);
      color: var(--text-main);
      font-size: 0.8rem;
      cursor: pointer;
      min-height: 38px;
      touch-action: manipulation;
    }

    .audio-pill-btn.active {
      border-color: var(--chord-color);
      background: var(--badge-bg);
      font-weight: 700;
    }

    .audio-pill-label {
      max-width: 140px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    /* МОДАЛЬНОЕ ОКНО QR-КОДА */
    .qr-modal-overlay {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 0, 0, 0.65);
      backdrop-filter: blur(4px);
      z-index: 1000;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 1rem;
    }
"""

idx_style = code.find("</style>")
assert idx_style != -1, "</style> not found"
code = code[:idx_style] + mobile_css + "\n  " + code[idx_style:]
print("Mobile CSS rules added")

with open('tools/build-index.mjs', 'w', encoding='utf-8') as f:
    f.write(code)
print("All patches applied to build-index.mjs!")
