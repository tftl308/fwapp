import test from 'node:test';
import assert from 'node:assert/strict';

const MUSICIAN_PROFILES = [
  { id: 'leader', label: 'Руководитель' },
  { id: 'piano', label: 'Фортепиано' },
  { id: 'bayan', label: 'Баян' },
  { id: 'electric', label: 'Электрогитара' },
  { id: 'bass', label: 'Бас-гитара' },
  { id: 'drums', label: 'Барабаны' }
];

class TaggedNotesHelper {
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

    const regex = /\[(leader|vocal|acoustic|piano|bayan|electric|bass|drums)\]([^\[]*)/gi;
    let match;
    let hasTags = false;
    let matchedSegments = [];
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
      // Check untagged prefix or leftover text
      let untagged = rawNotesStr;
      // remove matched tag blocks
      for (let i = matchedSegments.length - 1; i >= 0; i--) {
        const seg = matchedSegments[i];
        untagged = untagged.slice(0, seg.start) + untagged.slice(seg.end);
      }
      untagged = untagged.trim();
      if (untagged) {
        result.general = untagged;
      }
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
    // General note: deduplicate if identical to any profile note
    const gen = (notesObj.general || '').trim();
    if (gen) {
      const isDuplicate = MUSICIAN_PROFILES.some(p => (notesObj[p.id] || '').trim() === gen);
      if (!isDuplicate) {
        parts.push(gen);
      }
    }
    return parts.join('\n');
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
}

test('TaggedNotesHelper: basic parse and serialize', () => {
  const raw = '[leader] Играем тихо\n[piano] Вступление Solo';
  const parsed = TaggedNotesHelper.parseNotes(raw);
  assert.equal(parsed.leader, 'Играем тихо');
  assert.equal(parsed.piano, 'Вступление Solo');
  assert.equal(parsed.general, '');

  const serialized = TaggedNotesHelper.serializeNotes(parsed);
  assert.equal(serialized, '[leader] Играем тихо\n[piano] Вступление Solo');
});

test('TaggedNotesHelper: deduplicates general if identical to profile note', () => {
  const parsed = {
    leader: 'Общая заметка лидера',
    piano: '',
    bayan: '',
    electric: '',
    bass: '',
    drums: '',
    general: 'Общая заметка лидера'
  };
  const serialized = TaggedNotesHelper.serializeNotes(parsed);
  assert.equal(serialized, '[leader] Общая заметка лидера');
  assert.ok(!serialized.includes('\nОбщая заметка лидера'), 'General note must be removed when matching profile note');
});

test('TaggedNotesHelper: keeps independent general note if different', () => {
  const parsed = {
    leader: 'Заметка лидера',
    piano: '',
    bayan: '',
    electric: '',
    bass: '',
    drums: '',
    general: 'Старая неразмеченная заметка'
  };
  const serialized = TaggedNotesHelper.serializeNotes(parsed);
  assert.ok(serialized.includes('[leader] Заметка лидера'));
  assert.ok(serialized.includes('Старая неразмеченная заметка'));
});

test('TaggedNotesHelper: updateNoteForProfile leader does not create redundant general', () => {
  const initial = 'Неразмеченная заметка';
  const updated = TaggedNotesHelper.updateNoteForProfile(initial, 'leader', 'Неразмеченная заметка');
  // Since leader note is set to 'Неразмеченная заметка' and matches general, general is suppressed!
  assert.equal(updated, '[leader] Неразмеченная заметка');
});

test('TaggedNotesHelper: legacy acoustic and vocal map to leader', () => {
  const raw = '[vocal] Петь мягко [acoustic] Бой шестерка';
  const parsed = TaggedNotesHelper.parseNotes(raw);
  assert.equal(parsed.leader, 'Петь мягко Бой шестерка');
});
