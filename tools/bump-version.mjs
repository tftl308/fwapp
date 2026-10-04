#!/usr/bin/env node
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { createHash } from 'node:crypto';
import path from 'node:path';

const ROOT = process.cwd();

const hashFile = (relPath) => {
  const fullPath = path.join(ROOT, relPath);
  if (!existsSync(fullPath)) return 'sha256-000000000000';
  const content = readFileSync(fullPath, 'utf8');
  return 'sha256-' + createHash('sha256').update(content).digest('hex').slice(0, 12);
};

const versionPath = path.join(ROOT, 'data', 'version.json');
let version = {
  app_version: "4.1.0",
  app_build: "",
  data_version: "",
  min_client_version: "4.0.0",
  songs_hash: "",
  playlists_hash: "",
  notes_hash: "",
  released_at: "",
  changelog: "Обновление каталога песен, PWA интеграция GitHub Pages, синхронизация в одну кнопку"
};

if (existsSync(versionPath)) {
  try {
    version = JSON.parse(readFileSync(versionPath, 'utf8'));
  } catch(e) {}
}

const now = new Date();
const buildStamp = now.toISOString().replace(/[-:T]/g, '').slice(0, 14);

version.app_build = buildStamp;
version.data_version = now.toISOString().slice(0, 10);
version.songs_hash = hashFile('data/songs.csv');
version.playlists_hash = hashFile('data/playlists.csv');
version.notes_hash = hashFile('data/user_notes.csv');
version.released_at = now.toISOString();

writeFileSync(versionPath, JSON.stringify(version, null, 2), 'utf8');
console.log('✅ data/version.json успешно обновлен:', version.app_build);
