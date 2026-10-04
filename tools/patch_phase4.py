with open('tools/build-index.mjs', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. AudioPlayer timeupdate: direct DOM with requestAnimationFrame, NO store.setState
old_timeupdate = """    this.audioElement.addEventListener('timeupdate', () => {
      const cur = this.audioElement.currentTime || 0;
      const dur = this.audioElement.duration || 1;
      store.setState({ currentTime: cur, duration: dur });

      const fill = document.getElementById('player-progress-fill');
      if (fill && dur > 0) fill.style.width = ((cur / dur) * 100) + '%';
      const mainFill = document.getElementById('main-player-fill');
      if (mainFill && dur > 0) mainFill.style.width = ((cur / dur) * 100) + '%';

      const curTimeLabel = document.getElementById('player-cur-time');
      if (curTimeLabel) curTimeLabel.textContent = AudioPlayerService.formatTime(cur);
      const durTimeLabel = document.getElementById('player-dur-time');
      if (durTimeLabel && dur > 1) durTimeLabel.textContent = AudioPlayerService.formatTime(dur);
    });"""

new_timeupdate = """    let rafPending = false;
    this.audioElement.addEventListener('timeupdate', () => {
      if (rafPending) return;
      rafPending = true;
      requestAnimationFrame(() => {
        rafPending = false;
        const cur = this.audioElement.currentTime || 0;
        const dur = this.audioElement.duration || 1;

        // Прямой DOM-апдейт полосы прогресса и таймкодов БЕЗ вызова setState
        const fill = document.getElementById('player-progress-fill');
        if (fill && dur > 0) fill.style.width = ((cur / dur) * 100) + '%';
        const mainFill = document.getElementById('main-player-fill');
        if (mainFill && dur > 0) mainFill.style.width = ((cur / dur) * 100) + '%';

        const curTimeLabel = document.getElementById('player-cur-time');
        if (curTimeLabel) curTimeLabel.textContent = AudioPlayerService.formatTime(cur);
        const durTimeLabel = document.getElementById('player-dur-time');
        if (durTimeLabel && dur > 1) durTimeLabel.textContent = AudioPlayerService.formatTime(dur);
      });
    });"""

assert old_timeupdate in code, "old_timeupdate not found"
code = code.replace(old_timeupdate, new_timeupdate)
print("AudioPlayer timeupdate changed to rAF + direct DOM without setState")

# 2. Search input: do NOT trigger full renderCurrentView, only updateCatalogResultsOnly
old_search_input = """    document.addEventListener('input', (e) => {
      if (e.target.id === 'search-input') {
        clearTimeout(this.debounceTimer);
        this.debounceTimer = setTimeout(() => {
          store.setState({ searchQuery: e.target.value });
        }, 150);
      }
    });"""

new_search_input = """    document.addEventListener('input', (e) => {
      if (e.target.id === 'search-input') {
        clearTimeout(this.debounceTimer);
        const query = e.target.value;
        this.debounceTimer = setTimeout(() => {
          this.catalogLimit = 60;
          store.state.searchQuery = query; // локально в state без полного ре-рендера представления
          this.updateCatalogResultsOnly();
        }, 150);
      }
    });"""

assert old_search_input in code, "old_search_input not found"
code = code.replace(old_search_input, new_search_input)
print("Search input event updated to isolated updateCatalogResultsOnly")

# Also clear-search action: update input value and updateCatalogResultsOnly
old_clear_search = """      case 'clear-search': {
        const input = document.getElementById('search-input');
        if (input) input.value = '';
        store.setState({ searchQuery: '' });
        break;
      }"""

new_clear_search = """      case 'clear-search': {
        const input = document.getElementById('search-input');
        if (input) input.value = '';
        this.catalogLimit = 60;
        store.state.searchQuery = '';
        this.updateCatalogResultsOnly();
        break;
      }"""

assert old_clear_search in code, "old_clear_search not found"
code = code.replace(old_clear_search, new_clear_search)
print("clear-search updated")

# 3. Disable Play buttons when no track is loaded/available
# In onStateChange: update disabled state of btn-docked-play and main-play-btn
old_play_icons_state = """    const playIcon = document.getElementById('icon-play');
    const pauseIcon = document.getElementById('icon-pause');
    if (playIcon && pauseIcon) {
      if (state.isPlaying) {
        playIcon.classList.add('hidden');
        pauseIcon.classList.remove('hidden');
      } else {
        playIcon.classList.remove('hidden');
        pauseIcon.classList.add('hidden');
      }
    }

    const mainPlayIcon = document.getElementById('main-play-icon');
    const mainPauseIcon = document.getElementById('main-pause-icon');
    if (mainPlayIcon && mainPauseIcon) {
      if (state.isPlaying) {
        mainPlayIcon.classList.add('hidden');
        mainPauseIcon.classList.remove('hidden');
      } else {
        mainPlayIcon.classList.remove('hidden');
        mainPauseIcon.classList.add('hidden');
      }
    }"""

new_play_icons_state = """    const playIcon = document.getElementById('icon-play');
    const pauseIcon = document.getElementById('icon-pause');
    const dockedPlayBtn = document.getElementById('btn-docked-play');
    const hasTrack = !!(audioPlayer.currentTrack || (audioPlayer.playlistQueue && audioPlayer.playlistQueue.length > 0));

    if (dockedPlayBtn) {
      dockedPlayBtn.disabled = !hasTrack;
      dockedPlayBtn.style.opacity = hasTrack ? '1' : '0.4';
      dockedPlayBtn.style.cursor = hasTrack ? 'pointer' : 'not-allowed';
    }

    if (playIcon && pauseIcon) {
      if (state.isPlaying) {
        playIcon.classList.add('hidden');
        pauseIcon.classList.remove('hidden');
      } else {
        playIcon.classList.remove('hidden');
        pauseIcon.classList.add('hidden');
      }
    }

    const mainPlayBtn = document.getElementById('main-play-btn');
    if (mainPlayBtn) {
      mainPlayBtn.disabled = !hasTrack;
      mainPlayBtn.style.opacity = hasTrack ? '1' : '0.4';
      mainPlayBtn.style.cursor = hasTrack ? 'pointer' : 'not-allowed';
    }

    const mainPlayIcon = document.getElementById('main-play-icon');
    const mainPauseIcon = document.getElementById('main-pause-icon');
    if (mainPlayIcon && mainPauseIcon) {
      if (state.isPlaying) {
        mainPlayIcon.classList.add('hidden');
        mainPauseIcon.classList.remove('hidden');
      } else {
        mainPlayIcon.classList.remove('hidden');
        mainPauseIcon.classList.add('hidden');
      }
    }"""

assert old_play_icons_state in code, "old_play_icons_state not found"
code = code.replace(old_play_icons_state, new_play_icons_state)
print("play icons and disabled state added to onStateChange")

# Add id: 'main-play-btn' to dedicated player playBtn
old_main_play_btn = """    const playBtn = Renderer.createElement('button', {
      className: 'btn-play-circle',
      dataset: { action: 'player-toggle-play' },
      ariaLabel: 'Воспроизведение / Пауза'
    }, ["""

new_main_play_btn = """    const playBtn = Renderer.createElement('button', {
      className: 'btn-play-circle',
      id: 'main-play-btn',
      dataset: { action: 'player-toggle-play' },
      ariaLabel: 'Воспроизведение / Пауза'
    }, ["""

assert old_main_play_btn in code, "old_main_play_btn not found"
code = code.replace(old_main_play_btn, new_main_play_btn)
print("main-play-btn id added")

# Check audioPlayer.togglePlay: if no track, show toast
old_toggle_play = """  togglePlay() {
    if (this.audioElement.paused) this.play();
    else this.pause();
  }"""

new_toggle_play = """  togglePlay() {
    if (!this.currentTrack && (!this.playlistQueue || this.playlistQueue.length === 0)) {
      AppController.showToast('Нет выбранного аудиофайла для воспроизведения');
      return;
    }
    if (this.audioElement.paused) this.play();
    else this.pause();
  }"""

assert old_toggle_play in code, "old_toggle_play not found"
code = code.replace(old_toggle_play, new_toggle_play)
print("togglePlay guarded when no track loaded")

# 4. renderSongDetailView: when currentProfile === 'none', label clearly as "Общие заметки (Лидер)"
old_detail_role_opt = """    MUSICIAN_PROFILES.forEach(p => {
      const opt = Renderer.createElement('option', { value: p.id }, [p.label]);
      if ((state.currentProfile === 'none' && p.id === 'leader') || state.currentProfile === p.id) {
        opt.selected = true;
      }
      roleSelect.appendChild(opt);
    });"""

new_detail_role_opt = """    MUSICIAN_PROFILES.forEach(p => {
      const labelText = (state.currentProfile === 'none' && p.id === 'leader') ? 'Общие заметки (Лидер)' : p.label;
      const opt = Renderer.createElement('option', { value: p.id }, [labelText]);
      if ((state.currentProfile === 'none' && p.id === 'leader') || state.currentProfile === p.id) {
        opt.selected = true;
      }
      roleSelect.appendChild(opt);
    });"""

assert old_detail_role_opt in code, "old_detail_role_opt not found"
code = code.replace(old_detail_role_opt, new_detail_role_opt)
print("detail role dropdown updated with Общие заметки (Лидер)")

# In renderSongDetailView: also add Print button in header actions
old_header_stage_btn = """    const stageBtn = Renderer.createElement('button', {
      className: 'btn btn-brick',
      dataset: { action: 'open-concert-single-song' }
    }, ['На сцену']);
    headerActions.appendChild(stageBtn);"""

new_header_stage_btn = """    const printBtn = Renderer.createElement('button', {
      className: 'btn btn-outline btn-sm no-print',
      dataset: { action: 'print-song' },
      title: 'Печать текста песни и аккордов (Ctrl+P)'
    }, ['🖨 Печать']);
    headerActions.appendChild(printBtn);

    const stageBtn = Renderer.createElement('button', {
      className: 'btn btn-brick btn-sm no-print',
      dataset: { action: 'open-concert-single-song' }
    }, ['На сцену']);
    headerActions.appendChild(stageBtn);"""

assert old_header_stage_btn in code, "old_header_stage_btn not found"
code = code.replace(old_header_stage_btn, new_header_stage_btn)
print("print-song button added to song view")

# Add print-song action in handleAction
old_action_print = """      case 'clear-search': {"""
new_action_print = """      case 'print-song': {
        window.print();
        break;
      }

      case 'clear-search': {"""

assert old_action_print in code, "old_action_print not found"
code = code.replace(old_action_print, new_action_print)
print("print-song action added")

with open('tools/build-index.mjs', 'w', encoding='utf-8') as f:
    f.write(code)
print("Phase 4 applied successfully!")
