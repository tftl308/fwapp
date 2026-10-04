with open('tools/build-index.mjs', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. AudioPlayer: do not store Blob URLs in IndexedDB
old_set_queue = """  setQueue(tracks, startIndex = 0) {
    this.playlistQueue = tracks;
    this.currentIndex = startIndex;
    if (tracks[startIndex]) this.playIsolatedTrack(tracks[startIndex]);
    storage.saveBatch('playerQueue', tracks);
  }"""

new_set_queue = """  setQueue(tracks, startIndex = 0) {
    this.playlistQueue = tracks;
    this.currentIndex = startIndex;
    if (tracks[startIndex]) this.playIsolatedTrack(tracks[startIndex]);
    // Сохраняем в IndexedDB только чистые метаданные без временных blob URL
    const metaQueue = tracks.map(t => {
      const copy = Object.assign({}, t);
      delete copy.url;
      return copy;
    });
    storage.saveBatch('playerQueue', metaQueue);
  }"""

assert old_set_queue in code, "old_set_queue not found"
code = code.replace(old_set_queue, new_set_queue)
print("AudioPlayer.setQueue updated to strip blob URL")

# Also when loading playerQueue in init(): resolve URL dynamically from state.audio
old_init_queue = """    let savedQueue = await storage.getAll('playerQueue');
    if (savedQueue.length === 0) {
      savedQueue = store.getState().audio;
      await storage.saveBatch('playerQueue', savedQueue);
    }
    audioPlayer.playlistQueue = savedQueue;
    audioPlayer.currentIndex = 0;
    audioPlayer.currentTrack = savedQueue[0] || null;"""

new_init_queue = """    let savedQueue = await storage.getAll('playerQueue');
    if (savedQueue.length === 0) {
      savedQueue = store.getState().audio;
      const metaQueue = savedQueue.map(t => {
        const copy = Object.assign({}, t);
        delete copy.url;
        return copy;
      });
      await storage.saveBatch('playerQueue', metaQueue);
    }
    // Резолвим треки через state.audio, чтобы подтянуть живые url если они есть
    const currentAudioCatalog = store.getState().audio;
    const resolvedQueue = savedQueue.map(t => {
      const catalogMatch = currentAudioCatalog.find(a => a.id === t.id);
      return catalogMatch ? Object.assign({}, t, { url: catalogMatch.url, path: catalogMatch.path }) : t;
    });
    audioPlayer.playlistQueue = resolvedQueue;
    audioPlayer.currentIndex = 0;
    audioPlayer.currentTrack = resolvedQueue[0] || null;"""

assert old_init_queue in code, "old_init_queue not found"
code = code.replace(old_init_queue, new_init_queue)
print("init queue resolving updated")

# Also when playIsolatedTrack is called, if track has no url, check if it's in state.audio
old_play_isolated = """  playIsolatedTrack(track) {
    if (!track) return;
    this.currentTrack = track;
    const src = track.url || track.path || '';
    this.audioElement.src = src;"""

new_play_isolated = """  playIsolatedTrack(track) {
    if (!track) return;
    const catalogAudio = store.getState().audio.find(a => a.id === track.id);
    const resolvedUrl = (catalogAudio && catalogAudio.url) ? catalogAudio.url : (track.url || track.path || '');
    this.currentTrack = Object.assign({}, track, { url: resolvedUrl });
    this.audioElement.src = resolvedUrl;"""

assert old_play_isolated in code, "old_play_isolated not found"
code = code.replace(old_play_isolated, new_play_isolated)
print("playIsolatedTrack updated with dynamic URL resolution")

with open('tools/build-index.mjs', 'w', encoding='utf-8') as f:
    f.write(code)
print("Phase 2 audio URL patch complete!")
