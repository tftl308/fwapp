# -*- coding: utf-8 -*-
with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update CSS
css_additions = """
    /* Крупные плавающие кнопки листания песен на экране концерта */
    .concert-side-nav {
      position: absolute;
      top: 50%;
      transform: translateY(-50%);
      width: 52px;
      height: 72px;
      background: rgba(28, 25, 23, 0.7);
      backdrop-filter: blur(8px);
      color: #ffffff;
      border: 1px solid rgba(255, 255, 255, 0.2);
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.8rem;
      font-weight: 800;
      cursor: pointer;
      z-index: 50;
      user-select: none;
      transition: background 0.15s, transform 0.1s;
      box-shadow: 0 4px 14px rgba(0,0,0,0.4);
    }
    .concert-side-nav:active {
      background: var(--accent, #b45309);
      transform: translateY(-50%) scale(0.95);
    }
    .concert-side-prev { left: 10px; }
    .concert-side-next { right: 10px; }
    @media (max-width: 480px) {
      .concert-side-nav { width: 44px; height: 60px; font-size: 1.5rem; }
    }

    /* Стиль кнопок-иконок в карточках плейлистов: сочные, удобные для пальца */
    .playlist-card-row .btn-icon-pure {
      min-width: 42px;
      height: 42px;
      font-size: 1.35rem !important;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      border-radius: 8px;
      background: rgba(180, 83, 9, 0.08);
      border: 1px solid rgba(180, 83, 9, 0.2);
      cursor: pointer;
      transition: transform 0.1s, background 0.15s;
    }
    .playlist-card-row .btn-icon-pure:hover {
      background: rgba(180, 83, 9, 0.2);
    }
    .playlist-card-row .btn-icon-pure:active {
      transform: scale(0.92);
      background: rgba(180, 83, 9, 0.3);
    }
"""

if '/* Крупные плавающие кнопки листания песен' not in text:
    pos_css = text.find('</style>')
    assert pos_css != -1
    text = text[:pos_css] + css_additions + text[pos_css:]
    print('CSS added!')

# 2. Add floating side navigation buttons directly into #concert-overlay HTML
old_concert_html = """    <div class="concert-body" id="concert-body"></div>
    <div class="concert-footer">
      <button class="btn btn-outline" data-action="concert-prev-song" id="btn-concert-prev">◀ Предыдущая (PageUp)</button>
      <div class="text-sm text-muted" id="concert-pager-info">1 / 1</div>
      <button class="btn btn-outline" data-action="concert-next-song" id="btn-concert-next">Следующая (PageDown) ▶</button>
    </div>"""

new_concert_html = """    <!-- Крупные сценические кнопки листания песен -->
    <div class="concert-side-nav concert-side-prev" data-action="concert-prev-song" id="concert-nav-prev-btn" title="Предыдущая песня (Свайп вправо)">◀</div>
    <div class="concert-side-nav concert-side-next" data-action="concert-next-song" id="concert-nav-next-btn" title="Следующая песня (Свайп влево)">▶</div>

    <div class="concert-body" id="concert-body"></div>
    <div class="concert-footer">
      <button class="btn btn-outline" data-action="concert-prev-song" id="btn-concert-prev">◀ Предыдущая</button>
      <div class="text-sm text-muted" id="concert-pager-info" style="font-weight: 700; font-size: 0.95rem;">1 / 1</div>
      <button class="btn btn-outline" data-action="concert-next-song" id="btn-concert-next">Следующая ▶</button>
    </div>"""

if old_concert_html in text:
    text = text.replace(old_concert_html, new_concert_html)
    print('Concert HTML navigation updated!')

# 3. Add touch swipe handler on #concert-overlay in JavaScript
swipe_method = """
  setupConcertSwipeGestures() {
    const overlay = document.getElementById('concert-overlay');
    if (!overlay) return;
    let touchStartX = 0;
    let touchStartY = 0;
    let touchStartTime = 0;

    overlay.addEventListener('touchstart', (e) => {
      if (e.touches.length === 1) {
        touchStartX = e.touches[0].clientX;
        touchStartY = e.touches[0].clientY;
        touchStartTime = Date.now();
      }
    }, { passive: true });

    overlay.addEventListener('touchend', (e) => {
      if (e.changedTouches.length === 1) {
        const deltaX = e.changedTouches[0].clientX - touchStartX;
        const deltaY = e.changedTouches[0].clientY - touchStartY;
        const deltaTime = Date.now() - touchStartTime;

        if (Math.abs(deltaX) > 40 && Math.abs(deltaX) > Math.abs(deltaY) * 1.4 && deltaTime < 600) {
          if (deltaX < 0) {
            this.nextConcertSong();
          } else {
            this.prevConcertSong();
          }
        }
      }
    }, { passive: true });
  }
"""

pos_events = text.find('setupDelegatedEvents() {')
assert pos_events != -1
if 'setupConcertSwipeGestures' not in text:
    text = text[:pos_events] + swipe_method + "\n  " + text[pos_events:]
    # Call setupConcertSwipeGestures in init()
    pos_init = text.find('this.setupDelegatedEvents();')
    if pos_init != -1:
        text = text[:pos_init] + "this.setupConcertSwipeGestures();\n    " + text[pos_init:]
    print('Swipe gestures added!')

# 4. Add "Share current song" button into renderSongDetailView
old_stage_btn = """    const stageBtn = Renderer.createElement('button', {
      className: 'btn btn-brick btn-sm no-print',
      dataset: { action: 'open-concert-single-song', songId: song.id }
    }, ['На сцену']);
    headerActions.appendChild(stageBtn);"""

new_stage_btn = """    const shareBtn = Renderer.createElement('button', {
      className: 'btn btn-outline btn-sm no-print',
      dataset: { action: 'share-current-song', songId: song.id },
      title: 'Поделиться песней (текст с аккордами)'
    }, ['📤 Поделиться']);
    headerActions.appendChild(shareBtn);

    const stageBtn = Renderer.createElement('button', {
      className: 'btn btn-brick btn-sm no-print',
      dataset: { action: 'open-concert-single-song', songId: song.id }
    }, ['На сцену']);
    headerActions.appendChild(stageBtn);"""

if old_stage_btn in text:
    text = text.replace(old_stage_btn, new_stage_btn)
    print('Share button added to header!')

# 5. Add action handler for share-current-song in handleAction
share_action_case = """      case 'share-current-song': {
        const targetId = el.dataset.songId || state.currentSongId;
        const song = state.songs.find(s => s.id === targetId);
        if (!song) return;

        const songText = `🎵 ${song.title}\\nТональность: ${song.key || '—'} | Капо: ${song.capo || '—'}\\n\\n` + (song.body_plain || song.body_chordpro || '');
        if (navigator.share) {
          navigator.share({
            title: song.title,
            text: songText
          }).catch(() => {});
        } else if (navigator.clipboard) {
          navigator.clipboard.writeText(songText).then(() => {
            AppController.showToast('Текст песни скопирован в буфер обмена!');
          });
        } else {
          alert(songText);
        }
        break;
      }"""

if "case 'share-current-song':" not in text:
    pos_handle = text.find("switch (action) {")
    assert pos_handle != -1
    text = text[:pos_handle + len("switch (action) {")] + "\n" + share_action_case + "\n" + text[pos_handle + len("switch (action) {"):]
    print('Share action handler injected!')

# 6. Update single song concert mode: if opened from catalog, enable cycling through all songs!
old_next_song = """  nextConcertSong() {
    const state = store.getState();
    if (!state.concertPlaylistId) return;
    const items = state.playlistItems.filter(it => it.playlist_id === state.concertPlaylistId);
    if (state.concertIndex < items.length - 1) {
      store.setState({ concertIndex: state.concertIndex + 1 });
      this.renderConcertSong();
    }
  }

  prevConcertSong() {
    const state = store.getState();
    if (!state.concertPlaylistId) return;
    if (state.concertIndex > 0) {
      store.setState({ concertIndex: state.concertIndex - 1 });
      this.renderConcertSong();
    }
  }"""

new_next_song = """  nextConcertSong() {
    const state = store.getState();
    if (state.concertPlaylistId) {
      const items = state.playlistItems.filter(it => it.playlist_id === state.concertPlaylistId);
      if (state.concertIndex < items.length - 1) {
        store.setState({ concertIndex: state.concertIndex + 1 });
        this.renderConcertSong();
      }
    } else if (state.concertSingleSongId) {
      // Листание по всему каталогу песен
      const curIdx = state.songs.findIndex(s => s.id === state.concertSingleSongId);
      if (curIdx >= 0 && curIdx < state.songs.length - 1) {
        const nextSong = state.songs[curIdx + 1];
        store.setState({ concertSingleSongId: nextSong.id, concertIndex: curIdx + 1 });
        this.renderConcertSong();
      }
    }
  }

  prevConcertSong() {
    const state = store.getState();
    if (state.concertPlaylistId) {
      if (state.concertIndex > 0) {
        store.setState({ concertIndex: state.concertIndex - 1 });
        this.renderConcertSong();
      }
    } else if (state.concertSingleSongId) {
      const curIdx = state.songs.findIndex(s => s.id === state.concertSingleSongId);
      if (curIdx > 0) {
        const prevSong = state.songs[curIdx - 1];
        store.setState({ concertSingleSongId: prevSong.id, concertIndex: curIdx - 1 });
        this.renderConcertSong();
      }
    }
  }"""

if old_next_song in text:
    text = text.replace(old_next_song, new_next_song)
    print('Concert song cycling updated!')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(text)

print('All patches applied successfully to index.html!')
