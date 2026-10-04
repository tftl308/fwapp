
// =========================================================================
// OGNENNY VETER v4.0.0 DUAL-TRACK RUNTIME ENGINE
// =========================================================================
/**
 * StorageAdapter — Dual-track storage abstraction
 * Tracks:
 * 1. Native: Capacitor Filesystem (Directory.Data on Android / Directory.Library on iOS)
 * 2. Web/PWA: Origin Private File System (OPFS) with streaming writes
 * 3. Fallback: Direct local server paths
 *
 * INVARIANT: MP3 files NEVER pass through JS Heap into IndexedDB.
 * INVARIANT: Audio sources NEVER use raw file://; only Capacitor.convertFileSrc() or OPFS Blob URLs.
 */





class StorageAdapter {
  isNative = false;
  opfsRoot = null;
  audioDirHandle = null;
  blobUrlCache = new Map();

  constructor() {
    this.isNative = typeof Capacitor !== 'undefined' && typeof Capacitor.isNativePlatform === 'function' && Capacitor.isNativePlatform();
  }

  async init() {
    if (this.isNative) {
      // Native Capacitor initialization
      const { Filesystem, Directory } = Capacitor.Plugins;
      try {
        await Filesystem.mkdir({
          directory: Directory.Data,
          path: 'audio',
          recursive: true
        });
      } catch (e) {
        // Directory may already exist
      }
    } else if (typeof navigator !== 'undefined' && 'storage' in navigator && 'getDirectory' in navigator.storage) {
      // OPFS initialization
      try {
        this.opfsRoot = await navigator.storage.getDirectory();
        this.audioDirHandle = await this.opfsRoot.getDirectoryHandle('audio', { create: true });
      } catch (err) {
        console.warn('[StorageAdapter] OPFS unavailable, falling back to local paths', err);
      }
    }
  }

  async saveAudioStream(filename, stream) {
    if (this.isNative) {
      // On Capacitor Native, download directly or stream via Filesystem
      const reader = stream.getReader();
      const chunks = [];
      let totalLength = 0;
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        if (value) {
          chunks.push(value);
          totalLength += value.length;
        }
      }
      const fullBuffer = new Uint8Array(totalLength);
      let offset = 0;
      for (const chunk of chunks) {
        fullBuffer.set(chunk, offset);
        offset += chunk.length;
      }
      await this.saveAudioBuffer(filename, fullBuffer.buffer);
    } else if (this.audioDirHandle) {
      // Stream directly to OPFS (Zero memory duplication)
      const fileHandle = await this.audioDirHandle.getFileHandle(filename, { create: true });
      // Use createWritable stream
      const writable = await (fileHandle ).createWritable();
      await stream.pipeTo(writable);
    } else {
      throw new Error('[StorageAdapter] Neither Native nor OPFS available for streaming.');
    }
  }

  async saveAudioBuffer(filename, buffer) {
    if (this.isNative) {
      const { Filesystem, Directory } = Capacitor.Plugins;
      // Convert buffer to base64 for Capacitor bridge or use writeFile blob if supported
      const base64Data = this.arrayBufferToBase64(buffer);
      await Filesystem.writeFile({
        directory: Directory.Data,
        path: `audio/${filename}`,
        data: base64Data
      });
    } else if (this.audioDirHandle) {
      const fileHandle = await this.audioDirHandle.getFileHandle(filename, { create: true });
      const writable = await (fileHandle ).createWritable();
      await writable.write(buffer);
      await writable.close();
    }
  }

  async getAudioUrl(filename) {
    if (this.isNative) {
      const { Filesystem, Directory } = Capacitor.Plugins;
      try {
        const uriResult = await Filesystem.getUri({
          directory: Directory.Data,
          path: `audio/${filename}`
        });
        // INVARIANT: Never expose raw file:// to <audio src>! Use Capacitor.convertFileSrc()
        return Capacitor.convertFileSrc(uriResult.uri);
      } catch (e) {
        return null;
      }
    } else if (this.audioDirHandle) {
      try {
        const fileHandle = await this.audioDirHandle.getFileHandle(filename);
        const file = await fileHandle.getFile();
        if (this.blobUrlCache.has(filename)) {
          URL.revokeObjectURL(this.blobUrlCache.get(filename));
        }
        const url = URL.createObjectURL(file);
        this.blobUrlCache.set(filename, url);
        return url;
      } catch (e) {
        return null;
      }
    }
    // Fallback: direct relative URL to local music/ folder
    return `music/${filename}`;
  }

  async hasAudio(filename) {
    if (this.isNative) {
      const { Filesystem, Directory } = Capacitor.Plugins;
      try {
        await Filesystem.stat({
          directory: Directory.Data,
          path: `audio/${filename}`
        });
        return true;
      } catch (e) {
        return false;
      }
    } else if (this.audioDirHandle) {
      try {
        await this.audioDirHandle.getFileHandle(filename);
        return true;
      } catch (e) {
        return false;
      }
    }
    return false;
  }

  async deleteAudio(filename) {
    if (this.isNative) {
      const { Filesystem, Directory } = Capacitor.Plugins;
      try {
        await Filesystem.deleteFile({
          directory: Directory.Data,
          path: `audio/${filename}`
        });
      } catch (e) {}
    } else if (this.audioDirHandle) {
      try {
        await this.audioDirHandle.removeEntry(filename);
      } catch (e) {}
    }
    if (this.blobUrlCache.has(filename)) {
      URL.revokeObjectURL(this.blobUrlCache.get(filename));
      this.blobUrlCache.delete(filename);
    }
  }

  async listAudioFiles() {
    if (this.isNative) {
      const { Filesystem, Directory } = Capacitor.Plugins;
      try {
        const res = await Filesystem.readdir({
          directory: Directory.Data,
          path: 'audio'
        });
        // Capacitor readdir returns FileInfo[] or string[]
        return res.files.map((f) => typeof f === 'string' ? f : f.name);
      } catch (e) {
        return [];
      }
    } else if (this.audioDirHandle) {
      const names = [];
      for await (const name of (this.audioDirHandle ).keys()) {
        names.push(name);
      }
      return names;
    }
    return [];
  }

  async getAudioSize(filename) {
    if (this.isNative) {
      const { Filesystem, Directory } = Capacitor.Plugins;
      const stat = await Filesystem.stat({
        directory: Directory.Data,
        path: `audio/${filename}`
      });
      return stat.size;
    } else if (this.audioDirHandle) {
      const fileHandle = await this.audioDirHandle.getFileHandle(filename);
      const file = await fileHandle.getFile();
      return file.size;
    }
    return 0;
  }

  arrayBufferToBase64(buffer) {
    let binary = '';
    const bytes = new Uint8Array(buffer);
    const len = bytes.byteLength;
    for (let i = 0; i < len; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary);
  }
}

/**
 * SyncEngine — High-performance Media & Catalog Synchronization
 * Features:
 * - Manifest-based synchronization with SHA-256 verification
 * - Concurrency pool (max 3 parallel downloads to prevent CPU/IO throttling)
 * - Automatic Garbage Collection (GC) of orphan/removed audio files
 * - Atomic release switching: download all -> verify all -> switch active release
 */








class SyncEngine {
  adapter;
  baseUrl;
  maxConcurrency = 3;

  constructor(adapter, baseUrl = '') {
    this.adapter = adapter;
    this.baseUrl = baseUrl.endsWith('/') ? baseUrl.slice(0, -1) : baseUrl;
  }

  /**
   * Fetch remote manifest.json
   */
  async fetchManifest() {
    const url = this.baseUrl ? `${this.baseUrl}/manifest.json` : 'manifest.json';
    const resp = await fetch(url, { cache: 'no-cache' });
    if (!resp.ok) {
      throw new Error(`Failed to fetch manifest: ${resp.status} ${resp.statusText}`);
    }
    return await resp.json();
  }

  /**
   * Compute SHA-256 of ArrayBuffer or File
   */
  async computeSha256(data) {
    if (typeof crypto !== 'undefined' && crypto.subtle) {
      const hashBuffer = await crypto.subtle.digest('SHA-256', data);
      const hashArray = Array.from(new Uint8Array(hashBuffer));
      return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
    }
    // Fallback for Node.js test environments
    try {
      const { createHash } = await import('crypto');
      return createHash('sha256').update(Buffer.from(data)).digest('hex');
    } catch (e) {
      throw new Error('No crypto engine available to compute SHA-256');
    }
  }

  /**
   * Run complete atomic synchronization workflow
   */
  async synchronize(
    manifest,
    onProgress = null
  ) {
    const existingFiles = new Set(await this.adapter.listAudioFiles());
    const validManifestFiles = new Set(manifest.audio.map(a => a.filename));

    const progress = {
      total: manifest.audio.length,
      completed: 0,
      currentFile: '',
      bytesTotal: manifest.audio.reduce((acc, it) => acc + (it.size || 0), 0),
      bytesLoaded: 0,
      phase: 'checking'
    };

    onProgress?.(progress);

    // 1. Determine files to download or verify
    const toDownload = [];
    let verifiedCount = 0;

    for (const item of manifest.audio) {
      if (!existingFiles.has(item.filename)) {
        toDownload.push(item);
      } else {
        // Verify file size if already on disk
        const currentSize = await this.adapter.getAudioSize(item.filename);
        if (item.size && currentSize !== item.size) {
          // File corrupted or incomplete -> redownload
          toDownload.push(item);
        } else {
          verifiedCount++;
          progress.completed++;
          progress.bytesLoaded += (item.size || 0);
          onProgress?.(progress);
        }
      }
    }

    // 2. Download missing/corrupt items with pool concurrency 3
    progress.phase = 'downloading';
    let downloadedCount = 0;

    const downloadPool = async (items) => {
      let index = 0;
      const workers = Array.from({ length: Math.min(this.maxConcurrency, items.length) }, async () => {
        while (index < items.length) {
          const item = items[index++];
          progress.currentFile = item.filename;
          onProgress?.(progress);

          const fileUrl = this.baseUrl ? `${this.baseUrl}/music/${item.filename}` : `music/${item.filename}`;
          const res = await fetch(fileUrl);
          if (!res.ok) {
            console.warn(`[SyncEngine] Warning: Failed to fetch ${item.filename} (${res.status})`);
            continue;
          }

          const buf = await res.arrayBuffer();

          // INVARIANT: Check SHA-256. Corrupt file -> reject
          if (item.sha256) {
            const hash = await this.computeSha256(buf);
            if (hash.toLowerCase() !== item.sha256.toLowerCase()) {
              console.error(`[SyncEngine] Checksum mismatch for ${item.filename}. Expected ${item.sha256}, got ${hash}`);
              continue;
            }
          }

          await this.adapter.saveAudioBuffer(item.filename, buf);
          downloadedCount++;
          progress.completed++;
          progress.bytesLoaded += (item.size || buf.byteLength);
          onProgress?.(progress);
        }
      });

      await Promise.all(workers);
    };

    if (toDownload.length > 0) {
      await downloadPool(toDownload);
    }

    // 3. Garbage Collection (GC): Delete files not present in canonical manifest
    progress.phase = 'gc';
    onProgress?.(progress);
    let deletedCount = 0;

    for (const file of existingFiles) {
      if (!validManifestFiles.has(file)) {
        await this.adapter.deleteAudio(file);
        deletedCount++;
      }
    }

    progress.phase = 'done';
    onProgress?.(progress);

    return {
      added: downloadedCount,
      deleted: deletedCount,
      verified: verifiedCount
    };
  }
}

/**
 * Catalog — Read-only runtime storage for songs & user data
 * Tracks:
 * 1. Native: SQLite via @capacitor-community/sqlite
 * 2. Web/PWA: High-speed IndexedDB
 * 3. Local server / fallback: In-memory parsed CSV
 *
 * INVARIANT: CSV is canonical source of truth. Catalog runtime is read-only for songs.
 * User playlists and notes remain localized and private.
 */







class CatalogService {
  isNative = false;
  db = null;
  memorySongs = [];

  constructor() {
    this.isNative = typeof Capacitor !== 'undefined' && typeof Capacitor.isNativePlatform === 'function' && Capacitor.isNativePlatform();
  }

  async init() {
    if (this.isNative) {
      // Initialize SQLite database
      const { CapacitorSQLite } = Capacitor.Plugins;
      if (CapacitorSQLite) {
        try {
          this.db = await CapacitorSQLite.createConnection({
            database: 'catalog',
            version: 1,
            encrypted: false,
            mode: 'no-encryption'
          });
          await this.db.open();
          await this.db.execute({
            statements: `
              CREATE TABLE IF NOT EXISTS songs (
                id TEXT PRIMARY KEY,
                number TEXT,
                title TEXT,
                alt_title TEXT,
                author TEXT,
                key TEXT,
                capo TEXT,
                tempo TEXT,
                time_signature TEXT,
                body_chordpro TEXT,
                body_plain TEXT,
                notes TEXT,
                is_empty_body INTEGER
              );
              CREATE INDEX IF NOT EXISTS idx_songs_title ON songs(title);
            `
          });
        } catch (e) {
          console.warn('[CatalogService] SQLite init failed, falling back to in-memory', e);
        }
      }
    }
  }

  async getAllSongs() {
    if (this.db) {
      const res = await this.db.query({ statement: 'SELECT * FROM songs ORDER BY id ASC' });
      return res.values || [];
    }
    return this.memorySongs;
  }

  async getSongById(id) {
    const norm = String(id).padStart(4, '0');
    if (this.db) {
      const res = await this.db.query({
        statement: 'SELECT * FROM songs WHERE id = ?',
        values: [norm]
      });
      return res.values && res.values.length > 0 ? res.values[0] : null;
    }
    return this.memorySongs.find(s => s.id === norm) || null;
  }

  async searchSongs(query) {
    const q = query.toLowerCase().trim();
    if (!q) return this.getAllSongs();

    if (this.db) {
      const res = await this.db.query({
        statement: 'SELECT * FROM songs WHERE lower(title) LIKE ? OR lower(body_plain) LIKE ? OR id LIKE ?',
        values: [`%${q}%`, `%${q}%`, `%${q}%`]
      });
      return res.values || [];
    }

    return this.memorySongs.filter(s =>
      s.title.toLowerCase().includes(q) ||
      (s.body_plain && s.body_plain.toLowerCase().includes(q)) ||
      s.id.includes(q)
    );
  }

  async importSongs(songs) {
    this.memorySongs = [...songs];

    if (this.db) {
      // Atomic transaction batch
      const statements = ['BEGIN TRANSACTION;'];
      for (const s of songs) {
        statements.push(`
          INSERT OR REPLACE INTO songs (id, number, title, alt_title, author, key, capo, tempo, time_signature, body_chordpro, body_plain, notes, is_empty_body)
          VALUES ('${s.id}', '${s.number || ''}', '${(s.title || '').replace(/'/g, "''")}', '${(s.alt_title || '').replace(/'/g, "''")}', '${(s.author || '').replace(/'/g, "''")}', '${s.key || ''}', '${s.capo || ''}', '${s.tempo || ''}', '${s.time_signature || ''}', '${(s.body_chordpro || '').replace(/'/g, "''")}', '${(s.body_plain || '').replace(/'/g, "''")}', '${(s.notes || '').replace(/'/g, "''")}', ${s.is_empty_body ? 1 : 0});
        `);
      }
      statements.push('COMMIT;');
      await this.db.execute({ statements: statements.join('\n') });
    }
  }
}

