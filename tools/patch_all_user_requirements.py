# -*- coding: utf-8 -*-
import csv
import io
import re

print("=== STEP 1: FIXING 700 SONGS DUPLICATE IDs IN data/songs.csv ===")
with open('data/songs.csv', 'r', encoding='utf-8') as f:
    text = f.read()

reader = csv.DictReader(io.StringIO(text), delimiter=';')
songs = list(reader)
fieldnames = reader.fieldnames

print(f"Read {len(songs)} songs from data/songs.csv")

# Find missing numbers from 1..700
all_numbers = set()
for s in songs:
    try:
        all_numbers.add(int(s['id']))
    except:
        pass

missing_numbers = sorted([n for n in range(1, 701) if n not in all_numbers])
print("Missing numbers in 1..700:", missing_numbers)

# Reassign duplicate IDs
seen_ids = set()
reassigned_count = 0
for s in songs:
    raw_id = s['id']
    if raw_id in seen_ids:
        # This is a duplicate, give it a free number from missing_numbers
        new_num = missing_numbers.pop(0)
        new_id_str = str(new_num).padStart(4, '0') if hasattr(str(new_num), 'padStart') else f"{new_num:04d}"
        print(f"Reassigning duplicate ID {raw_id} (title '{s['title']}') -> {new_id_str}")
        s['id'] = new_id_str
        s['number'] = str(new_num)
        reassigned_count += 1
    else:
        seen_ids.add(raw_id)

print(f"Reassigned {reassigned_count} duplicate songs. Now total unique IDs: {len(seen_ids)}")
assert len(set(s['id'] for s in songs)) == 700, "Must have exactly 700 unique IDs!"

# Write back data/songs.csv
out_buf = io.StringIO()
writer = csv.DictWriter(out_buf, fieldnames=fieldnames, delimiter=';', lineterminator='\n')
writer.writeheader()
for s in songs:
    writer.writerow(s)

with open('data/songs.csv', 'w', encoding='utf-8') as f:
    f.write(out_buf.getvalue())
print("data/songs.csv successfully saved with 700 unique IDs!")


print("\n=== STEP 2: FIXING index.html ===")
with open('index.html', 'r', encoding='utf-8') as f:
    app_html = f.read()

# 2.1 Filter out {title}, {key}, {capo} and other {directives} from lyrics rendering in SongParser
song_parser_target = """    for (const rawLine of lines) {
      const trimmed = rawLine.trim();
      if (!trimmed) {
        parsedLines.push({ type: 'empty' });
        continue;
      }"""

song_parser_replacement = """    for (const rawLine of lines) {
      const trimmed = rawLine.trim();
      if (!trimmed) {
        parsedLines.push({ type: 'empty' });
        continue;
      }

      // ФИЛЬТРАЦИЯ СЛУЖЕБНЫХ ДИРЕКТИВ CHORDPRO: {title: ...}, {key: ...}, {capo: ...} и т.д.
      if (/^\{[a-zA-Z0-9_\-]+(?::.*)?\}$/.test(trimmed)) {
        continue;
      }"""

assert song_parser_target in app_html, "song_parser_target not found"
app_html = app_html.replace(song_parser_target, song_parser_replacement)

# 2.2 Dynamic line-height and line spacing based on font size
css_target = """.lyrics-render-line {
      display: flex;
      flex-wrap: wrap;
      align-items: flex-end;
      margin-bottom: 0.45rem;
      line-height: 1.05;
    }

    .lyrics-render-line.empty-line {
      height: 0.65rem;
      margin-bottom: 0.5rem;
    }"""

css_replacement = """.lyrics-render-line {
      display: flex;
      flex-wrap: wrap;
      align-items: flex-end;
      margin-bottom: calc(var(--font-lyrics) * 0.45);
      line-height: 1.15;
    }

    .lyrics-render-line.empty-line {
      height: calc(var(--font-lyrics) * 0.65);
      margin-bottom: calc(var(--font-lyrics) * 0.4);
    }"""

assert css_target in app_html, "css_target not found"
app_html = app_html.replace(css_target, css_replacement)

# 2.3 Remove update badge on main page header: update only in Settings
# In UpdateEngine.renderHeaderBadge:
render_badge_target = """  static renderHeaderBadge(updateInfo) {
    const headerActions = document.getElementById('header-actions');
    if (!headerActions) return;

    let badge = document.getElementById('btn-header-update-badge');
    if (!badge) {
      badge = Renderer.createElement('button', {
        id: 'btn-header-update-badge',
        className: 'btn-update-available',
        dataset: { action: 'open-update-modal' },
        title: 'Доступно обновление базы и приложения'
      }, [
        Renderer.createElement('span', { className: 'badge-update-dot' }),
        'Обновление'
      ]);
      headerActions.prepend(badge);
    }
    window._lastUpdateInfo = updateInfo;
  }"""

render_badge_replacement = """  static renderHeaderBadge(updateInfo) {
    // По требованию: кнопка обновления на главной странице убрана,
    // обновление выполняется строго через вкладку «Опции» / «Настройки».
    window._lastUpdateInfo = updateInfo;
  }"""

assert render_badge_target in app_html, "render_badge_target not found"
app_html = app_html.replace(render_badge_target, render_badge_replacement)

# 2.4 Fix showPlaylistPreviewModal
preview_missing_case = """      case 'preview-playlist-modal': {
        const plId = el.dataset.playlistId;
        this.showPlaylistPreviewModal(plId);
        break;
      }"""

preview_modal_method = """  showPlaylistPreviewModal(playlistId) {
    const state = store.getState();
    const pl = state.playlists.find(p => p.id === playlistId);
    if (!pl) return;

    const items = state.playlistItems
      .filter(it => it.playlist_id === playlistId)
      .sort((a, b) => parseInt(a.order, 10) - parseInt(b.order, 10));

    const existing = document.getElementById('preview-modal-overlay');
    if (existing) existing.remove();

    const overlay = Renderer.createElement('div', {
      id: 'preview-modal-overlay',
      className: 'qr-modal-overlay',
      dataset: { action: 'close-preview-modal' },
      style: 'display: flex;'
    });

    const box = Renderer.createElement('div', {
      className: 'preview-modal-box',
      style: 'background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 1rem; padding: 1.25rem; max-width: 520px; width: 94%; max-height: 85vh; display: flex; flex-direction: column; gap: 0.75rem; box-shadow: 0 10px 30px rgba(0,0,0,0.25);'
    });
    box.addEventListener('click', (e) => {
      const actionEl = e.target.closest('[data-action]');
      if (actionEl && actionEl.dataset.action === 'close-preview-modal') return;
      e.stopPropagation();
    });

    const hdr = Renderer.createElement('div', {
      style: 'display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-color); padding-bottom: 0.5rem;'
    }, [
      Renderer.createElement('h3', { style: 'margin: 0; font-size: 1.15rem; color: var(--accent);' }, ['📋 ' + pl.title]),
      Renderer.createElement('button', { className: 'btn btn-outline btn-sm', dataset: { action: 'close-preview-modal' } }, ['✕'])
    ]);
    box.appendChild(hdr);

    if (pl.purpose) {
      box.appendChild(Renderer.createElement('div', { className: 'text-sm text-muted' }, ['💬 ' + pl.purpose]));
    }

    const listWrap = Renderer.createElement('div', {
      style: 'overflow-y: auto; flex: 1; display: flex; flex-direction: column; gap: 0.4rem; padding-right: 0.25rem;'
    });

    if (items.length === 0) {
      listWrap.appendChild(Renderer.createElement('div', { className: 'text-sm text-muted', style: 'padding: 1.5rem; text-align: center;' }, ['В этом списке пока нет песен']));
    } else {
      items.forEach((it, idx) => {
        const s = state.songs.find(x => x.id === it.song_id);
        const itemRow = Renderer.createElement('div', {
          className: 'song-card',
          dataset: { action: 'open-song', songId: it.song_id },
          style: 'display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 0.75rem; cursor: pointer;'
        }, [
          Renderer.createElement('div', { style: 'display: flex; align-items: center; gap: 0.5rem;' }, [
            Renderer.createElement('span', { className: 'badge-num text-xs' }, [String(idx + 1)]),
            Renderer.createElement('span', { style: 'font-weight: 700; color: var(--text-main);' }, [s ? s.title : ('Песня #' + it.song_id)])
          ]),
          Renderer.createElement('span', { style: 'color: var(--chord-color); font-weight: 700; font-size: 0.85rem;' }, [s ? (s.key || s.key_default || '—') : '—'])
        ]);
        listWrap.appendChild(itemRow);
      });
    }
    box.appendChild(listWrap);

    const btnRow = Renderer.createElement('div', { style: 'display: flex; gap: 0.5rem; justify-content: flex-end; border-top: 1px solid var(--border-color); padding-top: 0.5rem;' }, [
      Renderer.createElement('button', {
        className: 'btn btn-primary btn-sm',
        dataset: { action: 'open-concert-from-playlist', playlistId: playlistId }
      }, ['🎤 На сцену']),
      Renderer.createElement('button', {
        className: 'btn btn-outline btn-sm',
        dataset: { action: 'close-preview-modal' }
      }, ['Закрыть'])
    ]);
    box.appendChild(btnRow);

    overlay.appendChild(box);
    document.body.appendChild(overlay);
  }

  showPlaylistExportModal(playlistId) {"""

assert 'showPlaylistExportModal(playlistId) {' in app_html, "showPlaylistExportModal not found"
app_html = app_html.replace('showPlaylistExportModal(playlistId) {', preview_modal_method)

# 2.5 Hardware back button protection and SPA history handling
history_setup_target = """    this.setupDelegatedEvents();
    this.setupKeyboardAndPedals();
    this.setupWakeLock();"""

history_setup_replacement = """    this.setupDelegatedEvents();
    this.setupKeyboardAndPedals();
    this.setupWakeLock();
    this.setupHistoryBackNavigation();"""

assert history_setup_target in app_html, "history_setup_target not found"
app_html = app_html.replace(history_setup_target, history_setup_replacement)

history_method = """  setupHistoryBackNavigation() {
    // Предотвращение случайного закрытия PWA при нажатии аппаратной кнопки «Назад» на телефоне
    history.pushState({ page: 'home' }, '');
    window.addEventListener('popstate', (e) => {
      const state = store.getState();
      const concertOverlay = document.getElementById('concert-overlay');
      const isConcertOpen = concertOverlay && !concertOverlay.classList.contains('hidden');
      const previewModal = document.getElementById('preview-modal-overlay');
      const qrModal = document.getElementById('qr-modal-overlay');
      const updateModal = document.getElementById('update-modal-overlay');

      if (previewModal) {
        previewModal.remove();
        history.pushState({ page: 'home' }, '');
      } else if (qrModal) {
        qrModal.remove();
        history.pushState({ page: 'home' }, '');
      } else if (updateModal) {
        updateModal.remove();
        history.pushState({ page: 'home' }, '');
      } else if (isConcertOpen) {
        this.exitConcertMode();
        history.pushState({ page: 'home' }, '');
      } else if (state.currentSongId) {
        store.setState({ currentSongId: null });
        history.pushState({ page: 'home' }, '');
      } else {
        // Если уже на главном экране, удерживаем приложение открытым
        history.pushState({ page: 'home' }, '');
      }
    });
  }

  setupDelegatedEvents() {"""

assert 'setupDelegatedEvents() {' in app_html, "setupDelegatedEvents() not found"
app_html = app_html.replace('setupDelegatedEvents() {', history_method)

# 2.6 Fullscreen on launch for PWA
pwa_fullscreen_target = """    store.subscribe((state) => this.onStateChange(state));
    this.renderCurrentView();"""

pwa_fullscreen_replacement = """    store.subscribe((state) => this.onStateChange(state));
    this.renderCurrentView();

    // Автоматический переход в полноэкранный режим при запуске как PWA
    const isStandalone = window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone === true;
    if (isStandalone && document.documentElement.requestFullscreen && !document.fullscreenElement) {
      document.addEventListener('click', () => {
        if (!document.fullscreenElement) {
          document.documentElement.requestFullscreen().catch(() => {});
        }
      }, { once: true });
    }"""

assert pwa_fullscreen_target in app_html, "pwa_fullscreen_target not found"
app_html = app_html.replace(pwa_fullscreen_target, pwa_fullscreen_replacement)

# 2.7 CONCERT MODE ENHANCEMENTS:
# - Swipe navigation between songs (left/right swipe)
# - Pinch-to-zoom font scaling
# - High contrast header & buttons in dark theme
# - Adaptive header for narrow screens
# - Full-width lines (word-wrap)

concert_css_target = """.concert-overlay[data-concert-theme="dark"] {
      background: #0c0a09 !important;
      color: #fafaf9 !important;
    }
    .concert-overlay[data-concert-theme="dark"] .concert-header {
      background: #1c1917 !important;
      border-bottom-color: #292524 !important;
    }
    .concert-overlay[data-concert-theme="dark"] .concert-title {
      color: #fafaf9 !important;
    }
    .concert-overlay[data-concert-theme="dark"] .syllable-chord {
      color: #f97316 !important;
    }
    .concert-overlay[data-concert-theme="dark"] .syllable-text {
      color: #fafaf9 !important;
    }

    .concert-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: calc(0.5rem + env(safe-area-inset-top)) 1rem 0.5rem 1rem;
      border-bottom: 1px solid rgba(0, 0, 0, 0.1);
      flex-shrink: 0;
    }"""

concert_css_replacement = """.concert-overlay[data-concert-theme="dark"] {
      background: #050505 !important;
      color: #ffffff !important;
    }
    .concert-overlay[data-concert-theme="dark"] .concert-header {
      background: #18181b !important;
      border-bottom: 1px solid #3f3f46 !important;
    }
    .concert-overlay[data-concert-theme="dark"] .concert-title {
      color: #ffffff !important;
    }
    .concert-overlay[data-concert-theme="dark"] #concert-song-meta {
      color: #d4d4d8 !important;
    }
    .concert-overlay[data-concert-theme="dark"] .btn-outline {
      background: #27272a !important;
      border-color: #52525b !important;
      color: #fafafa !important;
    }
    .concert-overlay[data-concert-theme="dark"] .syllable-chord {
      color: #fb923c !important;
    }
    .concert-overlay[data-concert-theme="dark"] .syllable-text {
      color: #f4f4f5 !important;
    }
    .concert-overlay[data-concert-theme="dark"] .concert-footer {
      background: #18181b !important;
      border-top: 1px solid #3f3f46 !important;
    }

    .concert-overlay[data-concert-theme="amber"] {
      background: #000000 !important;
      color: #f59e0b !important;
    }
    .concert-overlay[data-concert-theme="amber"] .concert-header {
      background: #121008 !important;
      border-bottom: 1px solid #78350f !important;
    }
    .concert-overlay[data-concert-theme="amber"] .concert-title {
      color: #f59e0b !important;
    }
    .concert-overlay[data-concert-theme="amber"] #concert-song-meta {
      color: #d97706 !important;
    }
    .concert-overlay[data-concert-theme="amber"] .btn-outline {
      background: #1c1917 !important;
      border-color: #b45309 !important;
      color: #fbbf24 !important;
    }
    .concert-overlay[data-concert-theme="amber"] .syllable-chord {
      color: #fbbf24 !important;
    }
    .concert-overlay[data-concert-theme="amber"] .syllable-text {
      color: #f59e0b !important;
    }
    .concert-overlay[data-concert-theme="amber"] .concert-footer {
      background: #121008 !important;
      border-top: 1px solid #78350f !important;
    }

    .concert-header {
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
    }"""

assert concert_css_target in app_html, "concert_css_target not found"
app_html = app_html.replace(concert_css_target, concert_css_replacement)

# Update concert body style to support smooth touch pinch and wrap lines
concert_body_css_target = """.concert-body {
      flex: 1;
      overflow-y: auto;
      overflow-x: hidden;
      padding: 1.5rem 1rem calc(2rem + env(safe-area-inset-bottom)) 1rem;
      scroll-behavior: smooth;
    }"""

concert_body_css_replacement = """.concert-body {
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
    }"""

assert concert_body_css_target in app_html, "concert_body_css_target not found"
app_html = app_html.replace(concert_body_css_target, concert_body_css_replacement)

# Update HTML concert-header to wrap buttons in .concert-actions-row
header_markup_target = """<div class="concert-header">
      <div class="concert-title-info">
        <div class="concert-title" id="concert-song-title">—</div>
        <div class="text-sm text-muted" id="concert-song-meta">—</div>
      </div>
      <div class="flex items-center gap-2">"""

header_markup_replacement = """<div class="concert-header">
      <div class="concert-title-info">
        <div class="concert-title" id="concert-song-title">—</div>
        <div class="text-sm text-muted" id="concert-song-meta">—</div>
      </div>
      <div class="concert-actions-row">"""

assert header_markup_target in app_html, "header_markup_target not found"
app_html = app_html.replace(header_markup_target, header_markup_replacement)

# Add Swipe & Pinch-to-zoom listeners for Concert mode
concert_touch_target = """    this.setupKeyboardAndPedals();
    this.setupWakeLock();"""

concert_touch_replacement = """    this.setupKeyboardAndPedals();
    this.setupWakeLock();
    this.setupConcertTouchGestures();"""

assert concert_touch_target in app_html, "concert_touch_target not found"
app_html = app_html.replace(concert_touch_target, concert_touch_replacement)

concert_touch_method = """  setupConcertTouchGestures() {
    const overlay = document.getElementById('concert-overlay');
    if (!overlay) return;

    let touchStartX = 0;
    let touchStartY = 0;
    let initialPinchDist = 0;
    let initialFontSize = 1.6;

    overlay.addEventListener('touchstart', (e) => {
      if (e.touches.length === 1) {
        touchStartX = e.touches[0].clientX;
        touchStartY = e.touches[0].clientY;
      } else if (e.touches.length === 2) {
        initialPinchDist = Math.hypot(
          e.touches[0].clientX - e.touches[1].clientX,
          e.touches[0].clientY - e.touches[1].clientY
        );
        initialFontSize = store.getState().concertFontSize || 1.6;
      }
    }, { passive: true });

    overlay.addEventListener('touchmove', (e) => {
      if (e.touches.length === 2 && initialPinchDist > 0) {
        const currentDist = Math.hypot(
          e.touches[0].clientX - e.touches[1].clientX,
          e.touches[0].clientY - e.touches[1].clientY
        );
        const scale = currentDist / initialPinchDist;
        const newSize = Math.max(1.1, Math.min(3.2, initialFontSize * scale));
        store.setState({ concertFontSize: newSize });
        document.documentElement.style.setProperty('--font-concert', newSize + 'rem');
      }
    }, { passive: true });

    overlay.addEventListener('touchend', (e) => {
      if (e.changedTouches.length === 1 && initialPinchDist === 0) {
        const dx = e.changedTouches[0].clientX - touchStartX;
        const dy = e.changedTouches[0].clientY - touchStartY;
        // Горизонтальный свайп для перехода между песнями в режиме концерта
        if (Math.abs(dx) > 60 && Math.abs(dy) < 50) {
          if (dx < -60) {
            // Свайп влево -> следующая песня
            this.nextConcertSong();
          } else if (dx > 60) {
            // Свайп вправо -> предыдущая песня
            this.prevConcertSong();
          }
        }
      }
      if (e.touches.length === 0) {
        initialPinchDist = 0;
      }
    }, { passive: true });
  }

  setupDelegatedEvents() {"""

assert 'setupDelegatedEvents() {' in app_html, "setupDelegatedEvents target not found"
app_html = app_html.replace('setupDelegatedEvents() {', concert_touch_method)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(app_html)

print("=== index.html successfully patched! ===")
