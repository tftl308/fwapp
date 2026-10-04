with open('tools/build-index.mjs', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Add catalogPageLimit in constructor
old_ctor = """  constructor() {
    this.searchEngine = null;
    this.debounceTimer = null;
    this.currentSongTranspose = 0;
    this.wakeLock = null;
    this.autoScrollAnimId = null;
    this.draggedType = null;
    this.draggedSongId = null;
    this.draggedPlaylistIndex = null;
    this.draggedPlaylistCardId = null;
  }"""

new_ctor = """  constructor() {
    this.searchEngine = null;
    this.debounceTimer = null;
    this.currentSongTranspose = 0;
    this.wakeLock = null;
    this.autoScrollAnimId = null;
    this.draggedType = null;
    this.draggedSongId = null;
    this.draggedPlaylistIndex = null;
    this.draggedPlaylistCardId = null;
    this.catalogLimit = 60;
  }"""

assert old_ctor in code, "old_ctor not found"
code = code.replace(old_ctor, new_ctor)
print("catalogLimit added to AppController constructor")

# 2. Render song list helper method renderCatalogSongItems
old_catalog_slice = """    const results = this.searchEngine ? this.searchEngine.search(state.searchQuery) : state.songs;
    const listWrap = Renderer.createElement('div', { className: 'song-list', style: 'max-height: 65vh; overflow-y: auto;' });
    const displayChunk = results.slice(0, 120);

    for (const song of displayChunk) {
      const card = Renderer.createElement('div', {
        className: 'song-card',
        draggable: true,
        dataset: { action: 'open-song', songId: song.id, dragSongId: song.id }
      });

      const info = Renderer.createElement('div', { className: 'song-card-info' });
      const titleSpan = Renderer.createElement('div', { className: 'song-card-title' });
      Renderer.renderHighlightedText(titleSpan, song.title, state.searchQuery);
      info.appendChild(titleSpan);

      if (song.alt_title) {
        info.appendChild(Renderer.createElement('div', { className: 'song-card-sub' }, [song.alt_title]));
      }
      card.appendChild(info);

      const metaWrap = Renderer.createElement('div', { className: 'flex items-center gap-2', style: 'flex-shrink: 0;' });

      const keyCapoText = Renderer.formatKeyCapo(song.key, song.capo);
      if (keyCapoText) {
        metaWrap.appendChild(Renderer.createElement('span', { className: 'badge-key-capo' }, [keyCapoText]));
      }

      const addBtn = Renderer.createElement('button', {
        className: 'btn btn-sm btn-outline',
        dataset: { action: 'add-song-to-current-playlist', songId: song.id },
        title: 'Добавить в текущий сетлист'
      }, ['+']);
      metaWrap.appendChild(addBtn);

      card.appendChild(metaWrap);
      listWrap.appendChild(card);
    }
    leftCol.appendChild(listWrap);"""

new_catalog_slice = """    const results = this.searchEngine ? this.searchEngine.search(state.searchQuery) : state.songs;
    const listWrap = Renderer.createElement('div', { className: 'song-list', id: 'catalog-song-list-wrap', style: 'max-height: 65vh; overflow-y: auto;' });
    this.renderCatalogSongCards(listWrap, results, state);
    leftCol.appendChild(listWrap);"""

assert old_catalog_slice in code, "old_catalog_slice not found"
code = code.replace(old_catalog_slice, new_catalog_slice)
print("renderCatalogView updated to use renderCatalogSongCards")

# Add renderCatalogSongCards method to AppController
render_cards_method = """  renderCatalogSongCards(listWrap, results, state) {
    listWrap.innerHTML = '';
    if (!results || results.length === 0) {
      const emptyMsg = Renderer.createElement('div', {
        className: 'empty-state-card',
        style: 'padding: 2rem; text-align: center; color: var(--text-muted);'
      }, ['Ничего не найдено по вашему запросу']);
      listWrap.appendChild(emptyMsg);
      return;
    }

    const displayChunk = results.slice(0, this.catalogLimit);

    for (const song of displayChunk) {
      const card = Renderer.createElement('div', {
        className: 'song-card',
        draggable: true,
        dataset: { action: 'open-song', songId: song.id, dragSongId: song.id }
      });

      const info = Renderer.createElement('div', { className: 'song-card-info' });
      const titleRow = Renderer.createElement('div', { className: 'song-card-title flex items-center gap-2' });
      const titleSpan = Renderer.createElement('span');
      Renderer.renderHighlightedText(titleSpan, song.title, state.searchQuery);
      titleRow.appendChild(titleSpan);

      if (song.is_empty_body === 'true') {
        titleRow.appendChild(Renderer.createElement('span', {
          className: 'badge-empty-body text-xs',
          style: 'font-size: 0.72rem; padding: 2px 6px; border-radius: 4px; background: rgba(120, 113, 108, 0.15); color: var(--text-muted);',
          title: 'Песня внесена в реестр, аккорды ожидаются'
        }, ['Только название']));
      }
      info.appendChild(titleRow);

      if (song.alt_title) {
        info.appendChild(Renderer.createElement('div', { className: 'song-card-sub' }, [song.alt_title]));
      }
      card.appendChild(info);

      const metaWrap = Renderer.createElement('div', { className: 'flex items-center gap-2', style: 'flex-shrink: 0;' });
      const keyCapoText = Renderer.formatKeyCapo(song.key, song.capo);
      if (keyCapoText) {
        metaWrap.appendChild(Renderer.createElement('span', { className: 'badge-key-capo' }, [keyCapoText]));
      }

      const addBtn = Renderer.createElement('button', {
        className: 'btn btn-sm btn-outline',
        dataset: { action: 'add-song-to-current-playlist', songId: song.id },
        title: 'Добавить в текущий сетлист'
      }, ['+']);
      metaWrap.appendChild(addBtn);

      card.appendChild(metaWrap);
      listWrap.appendChild(card);
    }

    if (results.length > this.catalogLimit) {
      const moreRow = Renderer.createElement('div', { style: 'padding: 0.75rem; text-align: center;' });
      const moreBtn = Renderer.createElement('button', {
        className: 'btn btn-outline btn-sm w-full',
        dataset: { action: 'catalog-show-more' }
      }, ['Показать ещё (' + (results.length - this.catalogLimit) + ' ост.)']);
      moreRow.appendChild(moreBtn);
      listWrap.appendChild(moreRow);
    }
  }

  updateCatalogResultsOnly() {
    const state = store.getState();
    const listWrap = document.getElementById('catalog-song-list-wrap');
    if (!listWrap) return;
    const results = this.searchEngine ? this.searchEngine.search(state.searchQuery) : state.songs;
    this.renderCatalogSongCards(listWrap, results, state);
  }
"""

idx_controller = code.find("renderCatalogView(container) {")
assert idx_controller != -1, "renderCatalogView not found"
code = code[:idx_controller] + render_cards_method + "\n  " + code[idx_controller:]
print("renderCatalogSongCards and updateCatalogResultsOnly added")

# Add catalog-show-more action in handleAction
old_action_switch = "      case 'clear-search': {"
new_action_switch = """      case 'catalog-show-more': {
        this.catalogLimit += 60;
        this.updateCatalogResultsOnly();
        break;
      }

      case 'clear-search': {"""

assert old_action_switch in code, "old_action_switch not found"
code = code.replace(old_action_switch, new_action_switch)
print("catalog-show-more action added")

with open('tools/build-index.mjs', 'w', encoding='utf-8') as f:
    f.write(code)
print("Phase 3 applied successfully!")
