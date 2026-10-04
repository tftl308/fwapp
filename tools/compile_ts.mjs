/**
 * Simple in-browser/runtime bundler for TypeScript/ES modules into client bundle
 */
import fs from 'fs';
import path from 'path';

const ROOT = process.cwd();
console.log('Compiling src modules into runtime bundle...');

const storageAdapterSrc = fs.readFileSync(path.join(ROOT, 'src', 'storage-adapter.ts'), 'utf8');
const syncEngineSrc = fs.readFileSync(path.join(ROOT, 'src', 'sync-engine.ts'), 'utf8');
const catalogSrc = fs.readFileSync(path.join(ROOT, 'src', 'catalog.ts'), 'utf8');

function cleanClassTs(code) {
  return code
    .replace(/^import\s+.*?;\s*$/gm, '')
    .replace(/^export\s+/gm, '')
    .replace(/\b(private|protected|public)\s+/g, '')
    .replace(/\bimplements\s+[A-Za-z0-9_,\s]+/g, '')
    .replace(/onProgress\?\s*:\s*\(p:\s*SyncProgress\)\s*=>\s*void/g, 'onProgress = null')
    .replace(/:\s*ReadableStream<Uint8Array>/g, '')
    .replace(/:\s*ArrayBuffer/g, '')
    .replace(/:\s*Uint8Array\[\]/g, '')
    .replace(/:\s*Uint8Array/g, '')
    .replace(/:\s*Promise<[^>]+>/g, '')
    .replace(/:\s*boolean/g, '')
    .replace(/:\s*string\[\]/g, '')
    .replace(/:\s*string/g, '')
    .replace(/:\s*number/g, '')
    .replace(/:\s*any/g, '')
    .replace(/:\s*void/g, '')
    .replace(/:\s*FileSystemDirectoryHandle\s*\|\s*null/g, '')
    .replace(/:\s*Map<string,\s*string>/g, '')
    .replace(/:\s*ManifestItem\[\]/g, '')
    .replace(/:\s*ManifestItem/g, '')
    .replace(/:\s*CatalogManifest/g, '')
    .replace(/:\s*SyncProgress/g, '')
    .replace(/:\s*SongRecord\[\]/g, '')
    .replace(/:\s*SongRecord/g, '')
    .replace(/:\s*IStorageAdapter/g, '')
    .replace(/interface\s+[A-Za-z0-9_]+\s*\{[\s\S]*?\}/g, '')
    .replace(/declare\s+const\s+Capacitor.*?;/g, '')
    .replace(/\bas\s+any\b/g, '')
    .replace(/!\)/g, ')')
    .replace(/!\./g, '.');
}

const bundledJs = `
// =========================================================================
// OGNENNY VETER v4.0.0 DUAL-TRACK RUNTIME ENGINE
// =========================================================================
${cleanClassTs(storageAdapterSrc)}
${cleanClassTs(syncEngineSrc)}
${cleanClassTs(catalogSrc)}
`;

fs.writeFileSync(path.join(ROOT, 'src', 'runtime-dualtrack.js'), bundledJs, 'utf8');
console.log('✓ Successfully generated src/runtime-dualtrack.js');
