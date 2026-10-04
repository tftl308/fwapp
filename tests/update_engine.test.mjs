import { test } from 'node:test';
import assert from 'node:assert';
import fs from 'node:fs';

test('Update Engine: data/version.json format conforms to specification', () => {
  const version = JSON.parse(fs.readFileSync('data/version.json', 'utf8'));
  assert(version.app_version, 'Must have app_version');
  assert(version.app_build, 'Must have app_build');
  assert(version.data_version, 'Must have data_version');
  assert(version.songs_hash && version.songs_hash.startsWith('sha256-'), 'Must have sha256 songs_hash');
  assert(version.playlists_hash && version.playlists_hash.startsWith('sha256-'), 'Must have sha256 playlists_hash');
  assert(version.notes_hash && version.notes_hash.startsWith('sha256-'), 'Must have sha256 notes_hash');
  assert(version.released_at, 'Must have released_at timestamp');
  assert(version.changelog, 'Must have changelog text');
});

test('PWA Structure: manifest.webmanifest and sw.js exist and valid', () => {
  const manifest = JSON.parse(fs.readFileSync('manifest.webmanifest', 'utf8'));
  assert.strictEqual(manifest.display, 'standalone');
  assert(manifest.icons.length >= 2, 'Must have standard and maskable icons');

  const sw = fs.readFileSync('sw.js', 'utf8');
  assert(sw.includes('version.json'), 'SW must handle version.json with network-first');
  assert(sw.includes('skipWaiting'), 'SW must support instant activation');
  
  // Verify that PRECACHE_ASSETS contains zero media files
  const precacheMatch = sw.match(/const PRECACHE_ASSETS = \[([\s\S]*?)\];/);
  assert(precacheMatch, 'Must define PRECACHE_ASSETS');
  assert(!precacheMatch[1].includes('.mp3'), 'PRECACHE_ASSETS must not include mp3 files');
  assert(!precacheMatch[1].includes('/music/'), 'PRECACHE_ASSETS must not include music folder');
});

test('GitHub Actions: deploy.yml properly bumps version before deployment', () => {
  const deployYaml = fs.readFileSync('.github/workflows/deploy.yml', 'utf8');
  assert(deployYaml.includes('node tools/bump-version.mjs'), 'CI workflow must bump version before upload');
  assert(deployYaml.includes('actions/deploy-pages'), 'CI workflow must deploy to GitHub Pages');
});
