# -*- coding: utf-8 -*-
import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. UpdateEngine: Purge caches, preserve user notes layer, force update service worker
update_old = """      if (statusEl) statusEl.textContent = '3/4. Обновление Service Worker кэша...';
      if ('serviceWorker' in navigator) {
        const reg = await navigator.serviceWorker.getRegistration();
        if (reg) await reg.update();
      }

      // Сохраняем новую версию метаданных в IndexedDB
      await storage.saveSetting('app_version_meta', info.remote);
      await storage.saveSetting('db_initialized', 'true');
      AppLogger.info('UPDATE', 'Обновление базы успешно завершено: ' + (info.remote.app_build || 'v4.1.0'));

      if (statusEl) statusEl.textContent = '4/4. ✓ Успешно обновлено! Перезагрузка...';
      setTimeout(() => {
        window.location.reload();
      }, 800);"""

update_new = """      if (statusEl) statusEl.textContent = '3/4. Сброс кэша браузера и Service Worker...';
      // Очищаем HTTP CacheStorage браузера, чтобы не загружались устаревшие страницы
      if ('caches' in window) {
        try {
          const cacheKeys = await caches.keys();
          for (const key of cacheKeys) {
            await caches.delete(key);
          }
        } catch(e) {}
      }
      if ('serviceWorker' in navigator) {
        try {
          const regs = await navigator.serviceWorker.getRegistrations();
          for (const reg of regs) {
            await reg.update();
          }
        } catch(e) {}
      }

      // Сохраняем новую версию метаданных в IndexedDB (заметки музыкантов бережно сохранены)
      await storage.saveSetting('app_version_meta', info.remote);
      await storage.saveSetting('db_initialized', 'true');
      AppLogger.info('UPDATE', 'Обновление базы успешно завершено: ' + (info.remote.app_build || 'v4.1.0'));

      if (statusEl) statusEl.textContent = '4/4. ✓ Успешно обновлено! Перезагрузка...';
      setTimeout(() => {
        // Жесткая перезагрузка страницы в обход кэша
        window.location.href = window.location.pathname + '?_v=' + Date.now();
      }, 600);"""

assert update_old in html, "update_old pattern not found"
html = html.replace(update_old, update_new)

# 2. Fix concert modal click propagation: check buttons inside modal
modal_fix_old = """    box.addEventListener('click', (e) => e.stopPropagation());"""
modal_fix_new = """    box.addEventListener('click', (e) => {
      const actionEl = e.target.closest('[data-action]');
      if (!actionEl) {
        e.stopPropagation();
        return;
      }
      const act = actionEl.dataset.action;
      if (act === 'close-concert-settings') return;
      // Обрабатываем действия внутри модального окна настроек сцены
      if (act === 'concert-toggle-autoscroll') {
        window.appController.toggleAutoScroll();
        const btn = box.querySelector('[data-action="concert-toggle-autoscroll"]');
        if (btn) btn.textContent = store.getState().isAutoScrolling ? '⏸ Остановить' : '▶ Запустить';
      } else if (act === 'concert-font-minus') {
        const sz = Math.max(0.9, (store.getState().concertFontSize || 1.6) - 0.15);
        store.setState({ concertFontSize: sz });
        document.documentElement.style.setProperty('--font-concert', sz + 'rem');
      } else if (act === 'concert-font-plus') {
        const sz = Math.min(3.2, (store.getState().concertFontSize || 1.6) + 0.15);
        store.setState({ concertFontSize: sz });
        document.documentElement.style.setProperty('--font-concert', sz + 'rem');
      } else if (act === 'concert-transpose-minus') {
        window.appController.currentSongTranspose = (window.appController.currentSongTranspose || 0) - 1;
        window.appController.renderConcertSong(false);
      } else if (act === 'concert-transpose-plus') {
        window.appController.currentSongTranspose = (window.appController.currentSongTranspose || 0) + 1;
        window.appController.renderConcertSong(false);
      } else if (act === 'concert-toggle-theme') {
        const themes = ['paper', 'amber', 'dark'];
        const curTheme = store.getState().concertTheme || 'paper';
        const nextTheme = themes[(themes.indexOf(curTheme) + 1) % themes.length];
        store.setState({ concertTheme: nextTheme });
        const overlay = document.getElementById('concert-overlay');
        if (overlay) overlay.dataset.concertTheme = nextTheme;
        AppController.showToast('Тема: ' + nextTheme);
      }
      e.stopPropagation();
    });"""

assert modal_fix_old in html, "modal_fix_old pattern not found"
html = html.replace(modal_fix_old, modal_fix_new)

# 3. Add auto-fit calculation in concert mode and filter non-chord lines option
render_concert_old = """    if (bodyEl) {
      bodyEl.innerHTML = '';
      Renderer.renderLyrics(bodyEl, currentSong, 0);
    }
  }"""

render_concert_new = """    if (bodyEl) {
      bodyEl.innerHTML = '';
      Renderer.renderLyrics(bodyEl, currentSong, this.currentSongTranspose || 0, true);
      // Динамическая адаптация размера шрифта и межстрочного интервала под высоту и ширину экрана
      if (shouldAutoFit) {
        requestAnimationFrame(() => this.fitConcertSongToViewport());
      }
    }
  }

  fitConcertSongToViewport() {
    const bodyEl = document.getElementById('concert-body');
    if (!bodyEl) return;
    const availWidth = bodyEl.clientWidth;
    const availHeight = bodyEl.clientHeight;
    if (availWidth <= 0 || availHeight <= 0) return;

    let fontSize = 1.35; // Начальный размер шрифта rem
    document.documentElement.style.setProperty('--font-concert', fontSize + 'rem');
    document.documentElement.style.setProperty('--concert-line-margin', '0.2rem');

    // Проверяем заполнение по вертикали
    let attempts = 0;
    while (bodyEl.scrollHeight > availHeight && fontSize > 0.8 && attempts < 15) {
      fontSize -= 0.05;
      document.documentElement.style.setProperty('--font-concert', fontSize.toFixed(2) + 'rem');
      attempts++;
    }

    if (bodyEl.scrollHeight > availHeight) {
      document.documentElement.style.setProperty('--concert-line-margin', '0.1rem');
    }
    store.setState({ concertFontSize: fontSize });
  }"""

assert render_concert_old in html, "render_concert_old pattern not found"
html = html.replace(render_concert_old, render_concert_new)

# Update renderConcertSong signature
sig_old = """  renderConcertSong() {"""
sig_new = """  renderConcertSong(shouldAutoFit = true) {"""
assert sig_old in html, "sig_old pattern not found"
html = html.replace(sig_old, sig_new)

# 4. In Renderer.renderLyrics: support concert filter (remove lines without chords)
render_lyrics_func_old = """  static renderLyrics(container, song, transposeSemitones = 0) {
    container.innerHTML = '';"""

render_lyrics_func_new = """  static renderLyrics(container, song, transposeSemitones = 0, isConcertMode = false) {
    container.innerHTML = '';"""

assert render_lyrics_func_old in html, "render_lyrics_func_old not found"
html = html.replace(render_lyrics_func_old, render_lyrics_func_new)

# Update parsing in renderLyrics to skip lines without chords in concert mode
loop_target = """    for (const line of cleanLines) {
      if (line.type === 'empty') {
        container.appendChild(Renderer.createElement('div', { className: 'lyrics-render-line empty-line' }));
      } else if (line.type === 'section') {
        container.appendChild(Renderer.createElement('div', { className: 'lyrics-render-line section-header' }, [line.text]));
      } else if (line.type === 'line') {"""

loop_replacement = """    for (const line of cleanLines) {
      if (line.type === 'empty') {
        if (!isConcertMode) {
          container.appendChild(Renderer.createElement('div', { className: 'lyrics-render-line empty-line' }));
        }
      } else if (line.type === 'section') {
        container.appendChild(Renderer.createElement('div', { className: 'lyrics-render-line section-header' }, [line.text]));
      } else if (line.type === 'line') {
        // В режиме концерта: убираем строки, где нет ни одного аккорда!
        if (isConcertMode) {
          const hasAnyChord = line.units && line.units.some(u => u.chord && u.chord.trim().length > 0);
          if (!hasAnyChord) continue;
        }"""

assert loop_target in html, "loop_target pattern not found"
html = html.replace(loop_target, loop_replacement)

# Update CSS for concert line margins
concert_css_margin_old = """    .concert-body .lyrics-render-line {
      width: 100%;
      box-sizing: border-box;
      flex-wrap: wrap;
      margin-bottom: calc(var(--font-concert) * 0.4);
    }
    .concert-body .lyrics-render-line.empty-line {
      height: calc(var(--font-concert) * 0.65);
      margin-bottom: calc(var(--font-concert) * 0.35);
    }"""

concert_css_margin_new = """    .concert-body .lyrics-render-line {
      width: 100%;
      box-sizing: border-box;
      flex-wrap: wrap;
      margin-bottom: var(--concert-line-margin, 0.2rem);
      line-height: 1.05;
    }
    .concert-body .lyrics-render-line.empty-line {
      height: 0.2rem;
      margin-bottom: 0.15rem;
    }"""

assert concert_css_margin_old in html, "concert_css_margin_old pattern not found"
html = html.replace(concert_css_margin_old, concert_css_margin_new)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("index.html successfully patched with concert auto-fit, line filtering & cache purge!")
