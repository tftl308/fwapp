# -*- coding: utf-8 -*-
import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# =========================================================================
# 1. FUZZY SEARCH UPGRADE: 2 words with 2 typos match inside songs
# =========================================================================
# In SearchEngine.search:
search_old = """            for (const aw of doc.allWords) {
              if (term.length >= 3 && isSubsequence(term, aw)) {
                bestTermScore = Math.max(bestTermScore, 20);
                break;
              }
              if (term.length >= 3 && damerauLevenshtein(term, aw) <= 1) {
                bestTermScore = Math.max(bestTermScore, 15);
                break;
              }
            }"""

search_new = """            for (const aw of doc.allWords) {
              if (term.length >= 3 && isSubsequence(term, aw)) {
                bestTermScore = Math.max(bestTermScore, 20);
                break;
              }
              if (term.length >= 3) {
                const maxAllowedDist = term.length >= 5 ? 2 : 1;
                const d = damerauLevenshtein(term, aw);
                if (d <= maxAllowedDist) {
                  bestTermScore = Math.max(bestTermScore, 15 - d * 2);
                  break;
                }
              }
            }"""

assert search_old in html, "search_old pattern not found in index.html"
html = html.replace(search_old, search_new)

# =========================================================================
# 2. CONCERT MODE HEADER & CONTROLS UPGRADE:
# Header: Title, Key+Capo (e.g. Am+3), Gear (Settings) button, Close button
# Strip leading empty lines from lyrics
# Footer: Compact pagination with < and > and index
# =========================================================================

# 2.1 CSS for concert header and compact footer
concert_css_old = """.concert-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 0.4rem;
      padding: calc(0.4rem + env(safe-area-inset-top)) 0.75rem 0.4rem 0.75rem;
      border-bottom: 1px solid rgba(0, 0, 0, 0.1);
      flex-shrink: 0;
    }

    .concert-header .concert-title-info {
      min-width: 0;
      flex: 1 1 180px;
    }

    .concert-header .concert-actions-row {
      display: flex;
      align-items: center;
      gap: 0.35rem;
      flex-wrap: nowrap;
      overflow-x: auto;
      max-width: 100%;
      -webkit-overflow-scrolling: touch;
    }

    .concert-title {
      font-size: 1.3rem;
      font-weight: 800;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .concert-body {
      flex: 1;
      overflow-y: auto;
      overflow-x: hidden;
      padding: 1rem 0.75rem calc(2rem + env(safe-area-inset-bottom)) 0.75rem;
      scroll-behavior: smooth;
      touch-action: pan-y pinch-zoom;
    }
    .concert-body .lyrics-render-line {
      width: 100%;
      box-sizing: border-box;
      flex-wrap: wrap;
      margin-bottom: calc(var(--font-concert) * 0.4);
    }
    .concert-body .lyrics-render-line.empty-line {
      height: calc(var(--font-concert) * 0.65);
      margin-bottom: calc(var(--font-concert) * 0.35);
    }

    .concert-body .syllable-chord {
      color: var(--chord-concert, #c2410c);
      font-size: var(--font-concert);
      line-height: 1.15;
    }

    .concert-body .syllable-text {
      font-size: var(--font-concert);
      line-height: 1.25;
    }

    .concert-body .lyrics-render-line.section-header {
      color: var(--section-concert, #9a3412);
      font-size: calc(var(--font-concert) * 0.85);
    }

    .concert-footer {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0.5rem 1rem calc(0.5rem + env(safe-area-inset-bottom)) 1rem;
      border-top: 1px solid rgba(0, 0, 0, 0.1);
      flex-shrink: 0;
      gap: 0.5rem;
    }"""

concert_css_new = """.concert-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: calc(0.4rem + env(safe-area-inset-top)) 0.75rem 0.4rem 0.75rem;
      border-bottom: 1px solid rgba(0, 0, 0, 0.1);
      flex-shrink: 0;
      gap: 0.5rem;
      min-height: 48px;
    }

    .concert-header .concert-title-info {
      min-width: 0;
      flex: 1 1 auto;
      display: flex;
      align-items: baseline;
      gap: 0.5rem;
      overflow: hidden;
    }

    .concert-title {
      font-size: 1.15rem;
      font-weight: 800;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    #concert-song-meta {
      font-size: 0.95rem;
      font-weight: 700;
      color: var(--chord-concert, var(--accent));
      white-space: nowrap;
      flex-shrink: 0;
    }

    .concert-header-buttons {
      display: flex;
      align-items: center;
      gap: 0.4rem;
      flex-shrink: 0;
    }

    .concert-body {
      flex: 1;
      overflow-y: auto;
      overflow-x: hidden;
      padding: 0.5rem 0.75rem calc(1rem + env(safe-area-inset-bottom)) 0.75rem;
      scroll-behavior: smooth;
      touch-action: pan-y pinch-zoom;
    }
    .concert-body .lyrics-render-line {
      width: 100%;
      box-sizing: border-box;
      flex-wrap: wrap;
      margin-bottom: calc(var(--font-concert) * 0.4);
    }
    .concert-body .lyrics-render-line.empty-line {
      height: calc(var(--font-concert) * 0.65);
      margin-bottom: calc(var(--font-concert) * 0.35);
    }

    .concert-body .syllable-chord {
      color: var(--chord-concert, #c2410c);
      font-size: var(--font-concert);
      line-height: 1.15;
    }

    .concert-body .syllable-text {
      font-size: var(--font-concert);
      line-height: 1.25;
    }

    .concert-body .lyrics-render-line.section-header {
      color: var(--section-concert, #9a3412);
      font-size: calc(var(--font-concert) * 0.85);
    }

    /* КОМПАКТНЫЙ НИЖНИЙ БАР КОНЦЕРТА */
    .concert-footer {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0.25rem 0.75rem calc(0.25rem + env(safe-area-inset-bottom)) 0.75rem;
      border-top: 1px solid rgba(0, 0, 0, 0.1);
      flex-shrink: 0;
      gap: 0.5rem;
      height: 40px;
      min-height: 40px;
    }

    .concert-footer .btn-pager {
      background: transparent;
      border: 1px solid var(--border-color);
      color: var(--text-main);
      border-radius: 6px;
      padding: 0.2rem 0.6rem;
      font-size: 1.1rem;
      font-weight: 700;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      min-width: 44px;
      min-height: 32px;
    }"""

assert concert_css_old in html, "concert_css_old pattern not found"
html = html.replace(concert_css_old, concert_css_new)

# 2.2 Concert HTML markup in index.html
concert_markup_old = """  <!-- Сценический режим (Плеер здесь строго отключен!) -->
  <div class="concert-overlay hidden" id="concert-overlay">
    <div class="concert-header">
      <div class="concert-title-info">
        <div class="concert-title" id="concert-song-title">—</div>
        <div class="text-sm text-muted" id="concert-song-meta">—</div>
      </div>
      <div class="concert-actions-row">
        <button class="btn btn-outline" data-action="concert-toggle-autoscroll" id="btn-autoscroll" title="Автопрокрутка (Педаль / Пробел)">
          ▶ Скролл
        </button>
        <button class="btn btn-outline" data-action="concert-font-minus" aria-label="A-">A-</button>
        <button class="btn btn-outline" data-action="concert-font-plus" aria-label="A+">A+</button>
        <button class="btn btn-icon btn-outline" data-action="concert-toggle-theme" aria-label="Тема">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
        </button>
        <button class="btn btn-icon btn-outline" data-action="concert-exit" aria-label="Выход">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
      </div>
    </div>
    <div class="concert-body" id="concert-body"></div>
    <div class="concert-footer">
      <button class="btn btn-outline" data-action="concert-prev-song" id="btn-concert-prev">◀ Предыдущая (PageUp)</button>
      <div class="text-sm text-muted" id="concert-pager-info">1 / 1</div>
      <button class="btn btn-outline" data-action="concert-next-song" id="btn-concert-next">Следующая (PageDown) ▶</button>
    </div>
  </div>"""

concert_markup_new = """  <!-- Сценический режим (Плеер здесь строго отключен!) -->
  <div class="concert-overlay hidden" id="concert-overlay">
    <div class="concert-header">
      <div class="concert-title-info">
        <div class="concert-title" id="concert-song-title">—</div>
        <div id="concert-song-meta">—</div>
      </div>
      <div class="concert-header-buttons">
        <button class="btn btn-icon btn-outline" data-action="concert-open-settings" aria-label="Настройки" title="Настройки сцены">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
        </button>
        <button class="btn btn-icon btn-outline" data-action="concert-exit" aria-label="Выход" title="Выйти из режима концерта">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
      </div>
    </div>
    <div class="concert-body" id="concert-body"></div>
    <div class="concert-footer">
      <button class="btn-pager" data-action="concert-prev-song" id="btn-concert-prev" aria-label="Предыдущая" title="Предыдущая песня">◀</button>
      <div style="font-size: 0.85rem; font-weight: 700; color: var(--text-muted); font-variant-numeric: tabular-nums;" id="concert-pager-info">1 / 1</div>
      <button class="btn-pager" data-action="concert-next-song" id="btn-concert-next" aria-label="Следующая" title="Следующая песня">▶</button>
    </div>
  </div>"""

assert concert_markup_old in html, "concert_markup_old pattern not found"
html = html.replace(concert_markup_old, concert_markup_new)

# 2.3 Strip leading empty lines in SongParser and Renderer.renderLyrics
render_lyrics_start = """    const parsedLines = SongParser.parseChordProToSyllables(transposedChordPro);

    for (const line of parsedLines) {"""

render_lyrics_replacement = """    const parsedLines = SongParser.parseChordProToSyllables(transposedChordPro);

    // Удаляем все пустые строки в самом начале песни
    let firstContentIdx = 0;
    while (firstContentIdx < parsedLines.length && parsedLines[firstContentIdx].type === 'empty') {
      firstContentIdx++;
    }
    const cleanLines = parsedLines.slice(firstContentIdx);

    for (const line of cleanLines) {"""

assert render_lyrics_start in html, "render_lyrics_start pattern not found"
html = html.replace(render_lyrics_start, render_lyrics_replacement)

# 2.4 Update meta in renderConcertSong to match format: "Am+3"
meta_code_old = """    if (titleEl) titleEl.textContent = currentSong.title;
    if (metaEl) {
      const keyCapo = Renderer.formatKeyCapo(currentSong.key, currentSong.capo);
      const tempo = currentSong.tempo ? currentSong.tempo + ' BPM' : '';
      metaEl.textContent = [keyCapo, tempo].filter(Boolean).join(' • ');
    }"""

meta_code_new = """    if (titleEl) titleEl.textContent = currentSong.title;
    if (metaEl) {
      const state = store.getState();
      const useGerman = state.notation === 'H';
      const effKey = currentSong.key ? ChordTransposer.transposeChord(currentSong.key, this.currentSongTranspose || 0, useGerman) : '';
      const effCapo = currentSong.capo ? (String(currentSong.capo).startsWith('+') ? currentSong.capo : '+' + currentSong.capo) : '';
      const keyCapoShort = (effKey || '') + (effCapo || '');
      metaEl.textContent = keyCapoShort || '—';
    }"""

assert meta_code_old in html, "meta_code_old pattern not found"
html = html.replace(meta_code_old, meta_code_new)

# 2.5 Add concert-open-settings modal and handlers
settings_handlers_old = """      case 'concert-toggle-theme': {"""

settings_handlers_new = """      case 'concert-open-settings': {
        this.showConcertSettingsModal();
        break;
      }
      case 'concert-transpose-minus': {
        this.currentSongTranspose = (this.currentSongTranspose || 0) - 1;
        this.renderConcertSong();
        break;
      }
      case 'concert-transpose-plus': {
        this.currentSongTranspose = (this.currentSongTranspose || 0) + 1;
        this.renderConcertSong();
        break;
      }
      case 'concert-toggle-theme': {"""

assert settings_handlers_old in html, "settings_handlers_old pattern not found"
html = html.replace(settings_handlers_old, settings_handlers_new)

# Add showConcertSettingsModal method
method_target = """  toggleAutoScroll() {"""

modal_method = """  showConcertSettingsModal() {
    const existing = document.getElementById('concert-settings-modal');
    if (existing) { existing.remove(); return; }

    const state = store.getState();
    const overlay = Renderer.createElement('div', {
      id: 'concert-settings-modal',
      className: 'qr-modal-overlay',
      style: 'display: flex; z-index: 250;',
      dataset: { action: 'close-concert-settings' }
    });

    const box = Renderer.createElement('div', {
      className: 'update-modal-box',
      style: 'background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; padding: 1.25rem; max-width: 360px; width: 90%; display: flex; flex-direction: column; gap: 1rem; box-shadow: 0 10px 25px rgba(0,0,0,0.4);'
    });
    box.addEventListener('click', (e) => e.stopPropagation());

    const hdr = Renderer.createElement('div', { style: 'display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-color); padding-bottom: 0.5rem;' }, [
      Renderer.createElement('h3', { style: 'margin: 0; font-size: 1.05rem; color: var(--accent);' }, ['⚙️ Опции сцены']),
      Renderer.createElement('button', { className: 'btn btn-outline btn-sm', dataset: { action: 'close-concert-settings' } }, ['✕'])
    ]);
    box.appendChild(hdr);

    // Автопрокрутка
    const scrollRow = Renderer.createElement('div', { style: 'display: flex; justify-content: space-between; align-items: center;' }, [
      Renderer.createElement('span', { style: 'font-weight: 600;' }, ['Автопрокрутка']),
      Renderer.createElement('button', {
        className: 'btn btn-outline btn-sm',
        dataset: { action: 'concert-toggle-autoscroll' }
      }, [state.isAutoScrolling ? '⏸ Остановить' : '▶ Запустить'])
    ]);
    box.appendChild(scrollRow);

    // Размер шрифта
    const fontRow = Renderer.createElement('div', { style: 'display: flex; justify-content: space-between; align-items: center;' }, [
      Renderer.createElement('span', { style: 'font-weight: 600;' }, ['Размер шрифта']),
      Renderer.createElement('div', { style: 'display: flex; gap: 0.5rem;' }, [
        Renderer.createElement('button', { className: 'btn btn-outline btn-sm', dataset: { action: 'concert-font-minus' } }, ['A-']),
        Renderer.createElement('button', { className: 'btn btn-outline btn-sm', dataset: { action: 'concert-font-plus' } }, ['A+'])
      ])
    ]);
    box.appendChild(fontRow);

    // Тональность
    const transpRow = Renderer.createElement('div', { style: 'display: flex; justify-content: space-between; align-items: center;' }, [
      Renderer.createElement('span', { style: 'font-weight: 600;' }, ['Тональность']),
      Renderer.createElement('div', { style: 'display: flex; gap: 0.5rem;' }, [
        Renderer.createElement('button', { className: 'btn btn-outline btn-sm', dataset: { action: 'concert-transpose-minus' } }, ['-1']),
        Renderer.createElement('button', { className: 'btn btn-outline btn-sm', dataset: { action: 'concert-transpose-plus' } }, ['+1'])
      ])
    ]);
    box.appendChild(transpRow);

    // Цветовая схема
    const themeRow = Renderer.createElement('div', { style: 'display: flex; justify-content: space-between; align-items: center;' }, [
      Renderer.createElement('span', { style: 'font-weight: 600;' }, ['Цветовая схема']),
      Renderer.createElement('button', {
        className: 'btn btn-outline btn-sm',
        dataset: { action: 'concert-toggle-theme' }
      }, ['🎨 Сменить тему'])
    ]);
    box.appendChild(themeRow);

    overlay.appendChild(box);
    document.body.appendChild(overlay);
  }

  toggleAutoScroll() {"""

assert method_target in html, "method_target pattern not found"
html = html.replace(method_target, modal_method)

# Close modal on click
close_modal_old = """      case 'close-preview-modal': {
        const modal = document.getElementById('preview-modal-overlay');
        if (modal) modal.remove();
        break;
      }"""

close_modal_new = """      case 'close-concert-settings': {
        const m = document.getElementById('concert-settings-modal');
        if (m) m.remove();
        break;
      }
      case 'close-preview-modal': {
        const modal = document.getElementById('preview-modal-overlay');
        if (modal) modal.remove();
        break;
      }"""

assert close_modal_old in html, "close_modal_old pattern not found"
html = html.replace(close_modal_old, close_modal_new)

# =========================================================================
# 3. REMOVE "Синхронизация папки с проектом" FROM SETTINGS
# =========================================================================
project_card_pattern = """    // БЛОК АВТОНОМНОЙ СИНХРОНИЗАЦИИ ПАПКИ (ДЛЯ МАКСИМАЛЬНОЙ ПРОСТОТЫ ПОЛЬЗОВАТЕЛЯ)
    const projectFolderCard = Renderer.createElement('div', { className: 'song-card', style: 'flex-direction: column; align-items: stretch; gap: 0.75rem; border: 2px solid var(--accent);' });
    projectFolderCard.appendChild(Renderer.createElement('h3', { className: 'text-main text-sm', style: 'color: var(--accent); font-weight: 800;' }, ['⚡ Синхронизация папки с проектом (1 клик)']));
    projectFolderCard.appendChild(Renderer.createElement('div', { className: 'text-xs text-muted' }, [
      'Если вы обновили файл songs.csv (добавили новые песни) или закинули треки в music/, нажмите кнопку ниже и выберите всю вашу общую папку проекта. Приложение само автоматически найдёт data/songs.csv, music/ и обновит всю базу без лишних вопросов!'
    ]));

    const projectFolderBtns = Renderer.createElement('div', { className: 'flex gap-2 flex-wrap' }, [
      Renderer.createElement('button', {
        className: 'btn btn-brick',
        style: 'font-weight: 700; padding: 0.6rem 1rem;',
        dataset: { action: 'sync-entire-project-folder' },
        title: 'Выбрать общую папку проекта и синхронизировать песни и аудио'
      }, ['📂 Выбрать и обновить папку проекта'])
    ]);
    projectFolderCard.appendChild(projectFolderBtns);
    wrap.appendChild(projectFolderCard);"""

assert project_card_pattern in html, "project_card_pattern not found"
html = html.replace(project_card_pattern, "    // Блок синхронизации папки удалён из меню настроек по запросу")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("index.html successfully updated with search, concert mode & settings cleanups!")
