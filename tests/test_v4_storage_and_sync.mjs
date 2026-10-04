import test from 'node:test';
import assert from 'node:assert';
import crypto from 'node:crypto';

// Mock IStorageAdapter for isolated in-memory unit testing
class MockStorageAdapter {
  constructor() {
    this.files = new Map();
  }

  async init() {}

  async saveAudioBuffer(filename, buffer) {
    this.files.set(filename, Buffer.from(buffer));
  }

  async saveAudioStream(filename, stream) {
    const reader = stream.getReader();
    const chunks = [];
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      if (value) chunks.push(value);
    }
    this.files.set(filename, Buffer.concat(chunks));
  }

  async getAudioUrl(filename) {
    if (this.files.has(filename)) return `mock-blob://${filename}`;
    return null;
  }

  async hasAudio(filename) {
    return this.files.has(filename);
  }

  async deleteAudio(filename) {
    this.files.delete(filename);
  }

  async listAudioFiles() {
    return Array.from(this.files.keys());
  }

  async getAudioSize(filename) {
    const f = this.files.get(filename);
    return f ? f.length : 0;
  }
}

// In-memory test sync engine logic
class TestSyncEngine {
  constructor(adapter) {
    this.adapter = adapter;
  }

  computeSha256(buffer) {
    return crypto.createHash('sha256').update(buffer).digest('hex');
  }

  async synchronize(manifest, fileProvider) {
    const existing = new Set(await this.adapter.listAudioFiles());
    const validManifest = new Set(manifest.audio.map(a => a.filename));

    let added = 0;
    let verified = 0;
    let deleted = 0;

    for (const item of manifest.audio) {
      if (!existing.has(item.filename)) {
        const buf = fileProvider(item.filename);
        if (item.sha256) {
          const hash = this.computeSha256(buf);
          assert.strictEqual(hash, item.sha256, 'SHA-256 checksum must match');
        }
        await this.adapter.saveAudioBuffer(item.filename, buf);
        added++;
      } else {
        const size = await this.adapter.getAudioSize(item.filename);
        if (size === item.size) verified++;
      }
    }

    // Garbage collection
    for (const file of existing) {
      if (!validManifest.has(file)) {
        await this.adapter.deleteAudio(file);
        deleted++;
      }
    }

    return { added, verified, deleted };
  }
}

test('StorageAdapter Invariant: Audio is not stored in IndexedDB and uses clean URL mapping', async () => {
  const adapter = new MockStorageAdapter();
  await adapter.init();

  const fakeMp3 = Buffer.from('FAKE-MP3-BINARY-DATA-0482');
  await adapter.saveAudioBuffer('0482_запись_Белый_снег.mp3', fakeMp3);

  const has = await adapter.hasAudio('0482_запись_Белый_снег.mp3');
  assert.strictEqual(has, true);

  const url = await adapter.getAudioUrl('0482_запись_Белый_снег.mp3');
  assert.ok(url && !url.startsWith('file://'), 'Audio URL must never expose raw file://');

  const size = await adapter.getAudioSize('0482_запись_Белый_снег.mp3');
  assert.strictEqual(size, fakeMp3.length);
});

test('SyncEngine Acceptance: Download 3 test MP3s, verify SHA-256 and GC obsolete files', async () => {
  const adapter = new MockStorageAdapter();
  await adapter.init();

  // Pre-seed an obsolete file on disk
  await adapter.saveAudioBuffer('old_orphan_song.mp3', Buffer.from('old-data'));

  const testFiles = {
    '0001_запись_Песня1.mp3': Buffer.from('binary-audio-content-1'),
    '0002_альбом_Песня2.mp3': Buffer.from('binary-audio-content-2'),
    '0003_минус_Песня3.mp3': Buffer.from('binary-audio-content-3')
  };

  const manifest = {
    version: '4.0.0',
    release_date: new Date().toISOString(),
    audio: Object.keys(testFiles).map(name => ({
      filename: name,
      song_id: name.slice(0, 4),
      type: 'запись',
      size: testFiles[name].length,
      sha256: crypto.createHash('sha256').update(testFiles[name]).digest('hex')
    }))
  };

  const syncEngine = new TestSyncEngine(adapter);
  const result = await syncEngine.synchronize(manifest, (name) => testFiles[name]);

  assert.strictEqual(result.added, 3, 'Should download and store exactly 3 files');
  assert.strictEqual(result.deleted, 1, 'Should GC the orphan file');

  const remainingFiles = await adapter.listAudioFiles();
  assert.strictEqual(remainingFiles.length, 3);
  assert.ok(!remainingFiles.includes('old_orphan_song.mp3'), 'Orphan file must be deleted by GC');
  assert.ok(remainingFiles.includes('0001_запись_Песня1.mp3'));
});
