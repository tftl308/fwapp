import sys

with open('tools/build-index.mjs', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update TaggedNotesHelper
old_tagged = """class TaggedNotesHelper {
  static parseNotes(rawNotesStr) {
    const result = {
      leader: '',
      piano: '',
      bayan: '',
      electric: '',
      bass: '',
      drums: '',
      general: ''
    };
    if (!rawNotesStr) return result;

    const regex = /\\[(leader|vocal|acoustic|piano|bayan|electric|bass|drums)\\]([^\\[]*)/gi;
    let match;
    let hasTags = false;
    while ((match = regex.exec(rawNotesStr)) !== null) {
      hasTags = true;
      let tag = match[1].toLowerCase();
      if (tag === 'vocal' || tag === 'acoustic') tag = 'leader';
      const val = match[2].trim();
      if (result[tag]) result[tag] += ' ' + val;
      else result[tag] = val;
    }

    if (!hasTags) {
      result.general = rawNotesStr.trim();
    }
    return result;
  }

  static serializeNotes(notesObj) {
    const parts = [];
    for (const prof of MUSICIAN_PROFILES) {
      const val = notesObj[prof.id];
      if (val && val.trim()) {
        parts.push('[' + prof.id + '] ' + val.trim());
      }
    }
    if (notesObj.general && notesObj.general.trim()) {
      parts.push(notesObj.general.trim());
    }
    return parts.join('\\n');
  }

  static getNoteForProfile(rawNotesStr, profileId) {
    if (!profileId || profileId === 'none') return '';
    const parsed = TaggedNotesHelper.parseNotes(rawNotesStr);
    return parsed[profileId] || (profileId === 'leader' ? parsed.general : '');
  }

  static updateNoteForProfile(rawNotesStr, profileId, newText) {
    if (!profileId || profileId === 'none') profileId = 'leader';
    const parsed = TaggedNotesHelper.parseNotes(rawNotesStr);
    parsed[profileId] = newText.trim();
    return TaggedNotesHelper.serializeNotes(parsed);
  }
}"""

new_tagged = """class TaggedNotesHelper {
  static parseNotes(rawNotesStr) {
    const result = {
      leader: '',
      piano: '',
      bayan: '',
      electric: '',
      bass: '',
      drums: '',
      general: ''
    };
    if (!rawNotesStr) return result;

    const regex = /\\[(leader|vocal|acoustic|piano|bayan|electric|bass|drums)\\]([^\\[]*)/gi;
    let match;
    let hasTags = false;
    const matchedSegments = [];
    while ((match = regex.exec(rawNotesStr)) !== null) {
      hasTags = true;
      let tag = match[1].toLowerCase();
      if (tag === 'vocal' || tag === 'acoustic') tag = 'leader';
      const val = match[2].trim();
      matchedSegments.push({ start: match.index, end: regex.lastIndex });
      if (result[tag]) result[tag] += ' ' + val;
      else result[tag] = val;
    }

    if (!hasTags) {
      result.general = rawNotesStr.trim();
    } else {
      let untagged = rawNotesStr;
      for (let i = matchedSegments.length - 1; i >= 0; i--) {
        const seg = matchedSegments[i];
        untagged = untagged.slice(0, seg.start) + untagged.slice(seg.end);
      }
      untagged = untagged.trim();
      if (untagged) result.general = untagged;
    }
    return result;
  }

  static serializeNotes(notesObj) {
    const parts = [];
    for (const prof of MUSICIAN_PROFILES) {
      const val = notesObj[prof.id];
      if (val && val.trim()) {
        parts.push('[' + prof.id + '] ' + val.trim());
      }
    }
    const gen = (notesObj.general || '').trim();
    if (gen) {
      const isDuplicate = MUSICIAN_PROFILES.some(p => (notesObj[p.id] || '').trim() === gen);
      if (!isDuplicate) {
        parts.push(gen);
      }
    }
    return parts.join('\\n');
  }

  static getNoteForProfile(rawNotesStr, profileId) {
    if (!profileId || profileId === 'none') return '';
    const parsed = TaggedNotesHelper.parseNotes(rawNotesStr);
    return parsed[profileId] || (profileId === 'leader' ? parsed.general : '');
  }

  static updateNoteForProfile(rawNotesStr, profileId, newText) {
    if (!profileId || profileId === 'none') profileId = 'leader';
    const parsed = TaggedNotesHelper.parseNotes(rawNotesStr);
    parsed[profileId] = newText.trim();
    return TaggedNotesHelper.serializeNotes(parsed);
  }
}"""

assert old_tagged in code, 'old_tagged not found in build-index.mjs'
code = code.replace(old_tagged, new_tagged)
print('TaggedNotesHelper replaced')

# 2. Store: shallow copy & separate concertPlaylistId & concertIndex
old_store = """  getState() { return this.state; }
  setState(patch) {
    this.state = Object.assign({}, this.state, patch);
    this.notify();
  }"""

new_store = """  getState() { return Object.assign({}, this.state); }
  setState(patch) {
    this.state = Object.assign({}, this.state, patch);
    this.notify();
  }"""

assert old_store in code, 'old_store not found'
code = code.replace(old_store, new_store)
print('Store.getState shallow copy added')

old_store_state = """      currentPlaylistId: 'pl-temp',
      concertIndex: 0,"""
new_store_state = """      currentPlaylistId: 'pl-temp',
      concertPlaylistId: 'pl-temp',
      concertIndex: 0,"""
assert old_store_state in code, 'old_store_state not found'
code = code.replace(old_store_state, new_store_state)
print('concertPlaylistId added to Store state')

# 3. StorageRepository: putOne, QuotaExceededError handling, toast export
old_storage_save_batch = """  async saveBatch(storeName, items) {
    if (this.fallbackStorage || !this.db) {
      try { localStorage.setItem('songbook_' + storeName, JSON.stringify(items)); } catch (e) {}
      return;
    }
    return new Promise((resolve, reject) => {
      const tx = this.db.transaction([storeName], 'readwrite');
      const os = tx.objectStore(storeName);
      os.clear();
      for (const item of items) os.put(item);
      tx.oncomplete = () => resolve();
      tx.onerror = () => reject(tx.error);
    });
  }"""

new_storage_save_batch = """  async saveBatch(storeName, items) {
    if (this.fallbackStorage || !this.db) {
      try {
        localStorage.setItem('songbook_' + storeName, JSON.stringify(items));
      } catch (e) {
        if (e && (e.name === 'QuotaExceededError' || e.code === 22)) {
          AppController.showToast('Память устройства заполнена! Экспортируйте базу.');
        }
      }
      return;
    }
    return new Promise((resolve, reject) => {
      const tx = this.db.transaction([storeName], 'readwrite');
      const os = tx.objectStore(storeName);
      os.clear();
      for (const item of items) os.put(item);
      tx.oncomplete = () => resolve();
      tx.onerror = () => {
        const err = tx.error;
        if (err && (err.name === 'QuotaExceededError' || err.name === 'QuotaExceeded')) {
          AppController.showToast('Превышена квота IndexedDB! Экспортируйте данные.');
        }
        reject(err);
      };
    });
  }

  async putOne(storeName, item) {
    if (this.fallbackStorage || !this.db) {
      const items = await this.getAll(storeName);
      const idx = items.findIndex(it => (it.id && it.id === item.id) || (it.key && it.key === item.key));
      if (idx !== -1) items[idx] = item;
      else items.push(item);
      try {
        localStorage.setItem('songbook_' + storeName, JSON.stringify(items));
      } catch (e) {
        if (e && (e.name === 'QuotaExceededError' || e.code === 22)) {
          AppController.showToast('Память устройства заполнена! Экспортируйте базу.');
        }
      }
      return;
    }
    return new Promise((resolve, reject) => {
      const tx = this.db.transaction([storeName], 'readwrite');
      const os = tx.objectStore(storeName);
      os.put(item);
      tx.oncomplete = () => resolve();
      tx.onerror = () => {
        const err = tx.error;
        if (err && (err.name === 'QuotaExceededError' || err.name === 'QuotaExceeded')) {
          AppController.showToast('Превышена квота IndexedDB! Экспортируйте данные.');
        }
        reject(err);
      };
    });
  }"""

assert old_storage_save_batch in code, 'old_storage_save_batch not found'
code = code.replace(old_storage_save_batch, new_storage_save_batch)
print('StorageRepository saveBatch and putOne updated')

old_save_note = """        const updatedSongs = [...state.songs];
        const sIdx = updatedSongs.findIndex(s => s.id === songId);
        if (sIdx !== -1) updatedSongs[sIdx] = song;

        await storage.saveBatch('songs', updatedSongs);
        this.searchEngine.updateIndex(updatedSongs);
        store.setState({ songs: updatedSongs });
        AppController.showToast('Заметка сохранена под тэгом [' + effectiveProfile + ']');"""

new_save_note = """        const updatedSongs = [...state.songs];
        const sIdx = updatedSongs.findIndex(s => s.id === songId);
        if (sIdx !== -1) updatedSongs[sIdx] = song;

        await storage.putOne('songs', song);
        this.searchEngine.updateIndex(updatedSongs);
        store.setState({ songs: updatedSongs });
        AppController.showToast('Заметка сохранена под тэгом [' + effectiveProfile + ']');"""

assert old_save_note in code, 'old_save_note not found'
code = code.replace(old_save_note, new_save_note)
print('save-user-note now uses storage.putOne')

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

assert old_csv_helper in code, 'old_csv_helper not found'
code = code.replace(old_csv_helper, new_csv_helper)
print('CsvHelper validation updated')

# 5. Fix draggable: 'true' -> draggable: true
code = code.replace("draggable: 'true'", "draggable: true")
print('draggable: true replaced')

with open('tools/build-index.mjs', 'w', encoding='utf-8') as f:
    f.write(code)
print('Phase 1 changes written to build-index.mjs successfully!')
