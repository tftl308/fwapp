import test from 'node:test';
import assert from 'node:assert/strict';

// FWP Validator & Serializer Logic
class FwpManager {
  static createLightweight(playlist, items) {
    return {
      format: 'FWP',
      version: '1.0',
      type: 'lightweight',
      createdAt: new Date().toISOString(),
      playlist: {
        id: playlist.id,
        title: playlist.title,
        date: playlist.date,
        purpose: playlist.purpose,
        items: items.map((it, idx) => ({
          songId: it.song_id,
          order: idx + 1,
          note: it.note || ''
        }))
      }
    };
  }

  static createStandalone(playlist, items, allSongs) {
    const songIdSet = new Set(items.map(it => it.song_id));
    const includedSongs = allSongs.filter(s => songIdSet.has(s.id));

    return {
      format: 'FWP',
      version: '1.0',
      type: 'standalone',
      createdAt: new Date().toISOString(),
      playlist: {
        id: playlist.id,
        title: playlist.title,
        date: playlist.date,
        purpose: playlist.purpose,
        items: items.map((it, idx) => ({
          songId: it.song_id,
          order: idx + 1,
          note: it.note || ''
        }))
      },
      songs: includedSongs.map(s => ({
        id: s.id,
        title: s.title,
        alt_title: s.alt_title || '',
        author: s.author || '',
        key: s.key || '',
        tempo: s.tempo || '',
        time_signature: s.time_signature || '',
        body_chordpro: s.body_chordpro || '',
        body_plain: s.body_plain || ''
      }))
    };
  }

  static parse(fwpJsonString) {
    const data = JSON.parse(fwpJsonString);
    if (data.format !== 'FWP') {
      throw new Error('Некорректный формат файла плейлиста. Ожидается заголовок FWP');
    }
    if (!data.playlist || !Array.isArray(data.playlist.items)) {
      throw new Error('Плейлист FWP поврежден: отсутствует список песен');
    }
    return data;
  }
}

// User Notes Layer & Merge Logic
class UserNotesManager {
  static getNote(userNotes, profile, songId) {
    return userNotes.find(n => n.user_profile === profile && n.song_id === songId) || null;
  }

  static saveNote(userNotes, profile, songId, patch) {
    const idx = userNotes.findIndex(n => n.user_profile === profile && n.song_id === songId);
    const existing = idx !== -1 ? userNotes[idx] : {
      user_profile: profile,
      song_id: songId,
      instrument_preset: '',
      personal_note: '',
      performance_rating: '0',
      is_favorite: '0'
    };

    const updated = Object.assign({}, existing, patch, { updated_at: new Date().toISOString() });
    const list = [...userNotes];
    if (idx !== -1) list[idx] = updated;
    else list.push(updated);
    return list;
  }

  static mergeWithCentralCatalog(centralSongs, localUserNotes) {
    // Центральный каталог обновляет тексты и аккорды песен,
    // но никогда не затирает пользовательский слой user_notes!
    return {
      updatedSongs: centralSongs,
      preservedNotes: localUserNotes
    };
  }
}

test('FWP: Lightweight playlist export & import', () => {
  const pl = { id: 'pl-test', title: 'Воскресенье', date: '2026-09-27', purpose: 'Служение' };
  const items = [{ song_id: 'song-001', note: 'Вступление фортепиано' }, { song_id: 'song-002', note: '' }];

  const pkg = FwpManager.createLightweight(pl, items);
  assert.equal(pkg.format, 'FWP');
  assert.equal(pkg.type, 'lightweight');
  assert.equal(pkg.playlist.items.length, 2);
  assert.equal(pkg.songs, undefined, 'Lightweight package must not include heavy songs body');

  const jsonStr = JSON.stringify(pkg);
  const parsed = FwpManager.parse(jsonStr);
  assert.equal(parsed.playlist.title, 'Воскресенье');
  assert.equal(parsed.playlist.items[0].songId, 'song-001');
});

test('FWP: Standalone playlist export & bundle unpack', () => {
  const pl = { id: 'pl-full', title: 'Пасха', date: '2026-04-12', purpose: 'Концерт' };
  const items = [{ song_id: 'song-001', note: '' }];
  const allSongs = [{ id: 'song-001', title: 'О, благодать', key: 'G', body_chordpro: '[G]Благодать' }];

  const pkg = FwpManager.createStandalone(pl, items, allSongs);
  assert.equal(pkg.type, 'standalone');
  assert.ok(Array.isArray(pkg.songs));
  assert.equal(pkg.songs[0].id, 'song-001');
  assert.equal(pkg.songs[0].title, 'О, благодать');
});

test('User Notes Layer: Independent musician presets & safe catalog merge', () => {
  let notes = [
    { user_profile: 'piano', song_id: 'song-001', instrument_preset: 'Grand Piano 14', personal_note: 'Аккуратно', performance_rating: '5', is_favorite: '1' }
  ];

  // Пианист меняет пресет инструмента
  notes = UserNotesManager.saveNote(notes, 'piano', 'song-001', { instrument_preset: 'Warm Pad + Piano 22' });
  const pianoNote = UserNotesManager.getNote(notes, 'piano', 'song-001');
  assert.equal(pianoNote.instrument_preset, 'Warm Pad + Piano 22');

  // Лидер добавляет свою заметку к этой же песне
  notes = UserNotesManager.saveNote(notes, 'leader', 'song-001', { personal_note: 'Песня прошла на ура, повторяем на Пасху' });
  const leaderNote = UserNotesManager.getNote(notes, 'leader', 'song-001');
  assert.equal(leaderNote.personal_note, 'Песня прошла на ура, повторяем на Пасху');

  // Проверяем, что заметка пианиста не затерта заметкой лидера
  assert.equal(UserNotesManager.getNote(notes, 'piano', 'song-001').instrument_preset, 'Warm Pad + Piano 22');

  // Имитация центрального обновления песен
  const incomingCentralSongs = [{ id: 'song-001', title: 'О, благодать (Новая редакция)', key: 'G' }];
  const mergeResult = UserNotesManager.mergeWithCentralCatalog(incomingCentralSongs, notes);
  assert.equal(mergeResult.updatedSongs[0].title, 'О, благодать (Новая редакция)');
  assert.equal(mergeResult.preservedNotes.length, 2, 'All user notes preserved after central update');
});
