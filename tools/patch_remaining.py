with open('tools/build-index.mjs', 'r', encoding='utf-8') as f:
    code = f.read()

# save-user-note uses putOne
target = "await storage.saveBatch('songs', updatedSongs);"
replacement = "await storage.putOne('songs', song);"
# Ensure we replace the one in save-user-note
idx = code.find("case 'save-user-note':")
assert idx != -1, "save-user-note not found"
target_idx = code.find(target, idx)
assert target_idx != -1 and target_idx - idx < 800, "target saveBatch not found in save-user-note"
code = code[:target_idx] + replacement + code[target_idx + len(target):]
print("save-user-note updated to storage.putOne")

# 4. CsvHelper validation
old_csv_helper = """    if (rows.length === 0) return [];
    const headers = rows[0].map(h => h.trim());
    return rows.slice(1).map(row => {
      const obj = {};
      headers.forEach((h, idx) => { obj[h] = row[idx] !== undefined ? row[idx] : ''; });
      return obj;
    });"""

new_csv_helper = """    if (rows.length === 0) return [];
    const headers = rows[0].map(h => h.trim());
    const validRows = [];
    for (let r = 1; r < rows.length; r++) {
      const row = rows[r];
      if (row.length === 1 && !row[0].trim()) continue;
      const obj = {};
      headers.forEach((h, idx) => { obj[h] = row[idx] !== undefined ? row[idx] : ''; });
      if (obj.id !== undefined && !obj.id.trim()) continue;
      validRows.push(obj);
    }
    return validRows;"""

assert old_csv_helper in code, "old_csv_helper not found"
code = code.replace(old_csv_helper, new_csv_helper)
print("CsvHelper validation updated")

# 5. Fix draggable: 'true' -> draggable: true
code = code.replace("draggable: 'true'", "draggable: true")
print("draggable: true replaced")

# 6. openConcertMode: preserve currentPlaylistId, use concertPlaylistId
old_open_concert = """  openConcertMode(playlistId, startIndex = 0) {
    audioPlayer.pause();
    document.getElementById('docked-player').classList.add('hidden');

    const state = store.getState();
    const curPlaylist = state.playlists.find(p => p.id === playlistId) || state.playlists[0];
    const items = state.playlistItems
      .filter(it => it.playlist_id === curPlaylist.id)
      .sort((a, b) => parseInt(a.order, 10) - parseInt(b.order, 10));

    if (items.length === 0) {
      AppController.showToast('Этот список пуст');
      return;
    }

    store.setState({
      currentPlaylistId: curPlaylist.id,
      concertIndex: startIndex,
      isAutoScrolling: false
    });

    const overlay = document.getElementById('concert-overlay');
    overlay.dataset.concertTheme = state.concertTheme;
    overlay.classList.remove('hidden');
    this.renderConcertSong();
  }"""

new_open_concert = """  openConcertMode(playlistId, startIndex = 0) {
    audioPlayer.pause();
    document.getElementById('docked-player').classList.add('hidden');

    const state = store.getState();
    const curPlaylist = state.playlists.find(p => p.id === playlistId) || state.playlists[0];
    const items = state.playlistItems
      .filter(it => it.playlist_id === curPlaylist.id)
      .sort((a, b) => parseInt(a.order, 10) - parseInt(b.order, 10));

    if (items.length === 0) {
      AppController.showToast('Этот список пуст');
      return;
    }

    store.setState({
      concertPlaylistId: curPlaylist.id,
      concertIndex: startIndex,
      isAutoScrolling: false
    });

    const overlay = document.getElementById('concert-overlay');
    overlay.dataset.concertTheme = state.concertTheme;
    overlay.classList.remove('hidden');
    this.renderConcertSong();
  }"""

assert old_open_concert in code, "old_open_concert not found"
code = code.replace(old_open_concert, new_open_concert)
print("openConcertMode updated with concertPlaylistId")

# Update renderConcertSong and nextConcertSong to use concertPlaylistId
old_render_concert = """  renderConcertSong() {
    this.stopAutoScroll();
    const state = store.getState();
    const curPlaylist = state.playlists.find(p => p.id === state.currentPlaylistId) || state.playlists[0];"""

new_render_concert = """  renderConcertSong() {
    this.stopAutoScroll();
    const state = store.getState();
    const cPlId = state.concertPlaylistId || state.currentPlaylistId;
    const curPlaylist = state.playlists.find(p => p.id === cPlId) || state.playlists[0];"""

assert old_render_concert in code, "old_render_concert not found"
code = code.replace(old_render_concert, new_render_concert)
print("renderConcertSong updated to use concertPlaylistId")

old_next_concert = """  nextConcertSong() {
    const state = store.getState();
    const curPlaylist = state.playlists.find(p => p.id === state.currentPlaylistId) || state.playlists[0];"""

new_next_concert = """  nextConcertSong() {
    const state = store.getState();
    const cPlId = state.concertPlaylistId || state.currentPlaylistId;
    const curPlaylist = state.playlists.find(p => p.id === cPlId) || state.playlists[0];"""

assert old_next_concert in code, "old_next_concert not found"
code = code.replace(old_next_concert, new_next_concert)
print("nextConcertSong updated to use concertPlaylistId")

# prevConcertSong
old_prev_concert = """  prevConcertSong() {
    const state = store.getState();
    if (state.concertIndex > 0) {
      store.setState({ concertIndex: state.concertIndex - 1 });
      this.renderConcertSong();
    }
  }"""
# check if prevConcertSong needs anything or is already good
print("prevConcertSong already decrements concertIndex and calls renderConcertSong")

with open('tools/build-index.mjs', 'w', encoding='utf-8') as f:
    f.write(code)
print("All patch_remaining modifications applied successfully!")
