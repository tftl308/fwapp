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

export interface SongRecord {
  id: string;
  number: string;
  title: string;
  alt_title?: string;
  author?: string;
  key?: string;
  capo?: string;
  tempo?: string;
  time_signature?: string;
  body_chordpro: string;
  body_plain: string;
  notes?: string;
  is_empty_body: boolean;
}

export interface ICatalogService {
  init(): Promise<void>;
  getAllSongs(): Promise<SongRecord[]>;
  getSongById(id: string): Promise<SongRecord | null>;
  searchSongs(query: string): Promise<SongRecord[]>;
  importSongs(songs: SongRecord[]): Promise<void>;
}

declare const Capacitor: any;

export class CatalogService implements ICatalogService {
  private isNative: boolean = false;
  private db: any = null;
  private memorySongs: SongRecord[] = [];

  constructor() {
    this.isNative = typeof Capacitor !== 'undefined' && typeof Capacitor.isNativePlatform === 'function' && Capacitor.isNativePlatform();
  }

  async init(): Promise<void> {
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

  async getAllSongs(): Promise<SongRecord[]> {
    if (this.db) {
      const res = await this.db.query({ statement: 'SELECT * FROM songs ORDER BY id ASC' });
      return res.values || [];
    }
    return this.memorySongs;
  }

  async getSongById(id: string): Promise<SongRecord | null> {
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

  async searchSongs(query: string): Promise<SongRecord[]> {
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

  async importSongs(songs: SongRecord[]): Promise<void> {
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
