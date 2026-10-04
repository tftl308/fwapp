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

export interface IStorageAdapter {
  init(): Promise<void>;
  saveAudioStream(filename: string, stream: ReadableStream<Uint8Array>): Promise<void>;
  saveAudioBuffer(filename: string, buffer: ArrayBuffer): Promise<void>;
  getAudioUrl(filename: string): Promise<string | null>;
  hasAudio(filename: string): Promise<boolean>;
  deleteAudio(filename: string): Promise<void>;
  listAudioFiles(): Promise<string[]>;
  getAudioSize(filename: string): Promise<number>;
}

declare const Capacitor: any;

export class StorageAdapter implements IStorageAdapter {
  private isNative: boolean = false;
  private opfsRoot: FileSystemDirectoryHandle | null = null;
  private audioDirHandle: FileSystemDirectoryHandle | null = null;
  private blobUrlCache: Map<string, string> = new Map();

  constructor() {
    this.isNative = typeof Capacitor !== 'undefined' && typeof Capacitor.isNativePlatform === 'function' && Capacitor.isNativePlatform();
  }

  async init(): Promise<void> {
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

  async saveAudioStream(filename: string, stream: ReadableStream<Uint8Array>): Promise<void> {
    if (this.isNative) {
      // On Capacitor Native, download directly or stream via Filesystem
      const reader = stream.getReader();
      const chunks: Uint8Array[] = [];
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
      const writable = await (fileHandle as any).createWritable();
      await stream.pipeTo(writable);
    } else {
      throw new Error('[StorageAdapter] Neither Native nor OPFS available for streaming.');
    }
  }

  async saveAudioBuffer(filename: string, buffer: ArrayBuffer): Promise<void> {
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
      const writable = await (fileHandle as any).createWritable();
      await writable.write(buffer);
      await writable.close();
    }
  }

  async getAudioUrl(filename: string): Promise<string | null> {
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
          URL.revokeObjectURL(this.blobUrlCache.get(filename)!);
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

  async hasAudio(filename: string): Promise<boolean> {
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

  async deleteAudio(filename: string): Promise<void> {
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
      URL.revokeObjectURL(this.blobUrlCache.get(filename)!);
      this.blobUrlCache.delete(filename);
    }
  }

  async listAudioFiles(): Promise<string[]> {
    if (this.isNative) {
      const { Filesystem, Directory } = Capacitor.Plugins;
      try {
        const res = await Filesystem.readdir({
          directory: Directory.Data,
          path: 'audio'
        });
        // Capacitor readdir returns FileInfo[] or string[]
        return res.files.map((f: any) => typeof f === 'string' ? f : f.name);
      } catch (e) {
        return [];
      }
    } else if (this.audioDirHandle) {
      const names: string[] = [];
      for await (const name of (this.audioDirHandle as any).keys()) {
        names.push(name);
      }
      return names;
    }
    return [];
  }

  async getAudioSize(filename: string): Promise<number> {
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

  private arrayBufferToBase64(buffer: ArrayBuffer): string {
    let binary = '';
    const bytes = new Uint8Array(buffer);
    const len = bytes.byteLength;
    for (let i = 0; i < len; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary);
  }
}
