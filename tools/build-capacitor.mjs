/**
 * build-capacitor.mjs — Capacitor Native Mobile Builder
 * Generates capacitor-app/www/ bundle ready for `npx cap sync`
 */

import fs from 'fs';
import path from 'path';

const ROOT = process.cwd();
const CAP_WWW = path.join(ROOT, 'capacitor-app', 'www');

console.log('--- [BUILD CAPACITOR] Generating capacitor-app/www artifact ---');

fs.mkdirSync(CAP_WWW, { recursive: true });
fs.mkdirSync(path.join(CAP_WWW, 'data'), { recursive: true });

// Copy web assets
const filesToCopy = [
  'index.html',
  'manifest.json'
];

for (const file of filesToCopy) {
  if (fs.existsSync(path.join(ROOT, file))) {
    fs.copyFileSync(path.join(ROOT, file), path.join(CAP_WWW, file));
  }
}

// Copy canonical data
const dataFiles = ['songs.csv', 'audio.csv', 'manifest.json'];
for (const df of dataFiles) {
  const src = path.join(ROOT, 'data', df);
  if (fs.existsSync(src)) {
    fs.copyFileSync(src, path.join(CAP_WWW, 'data', df));
  }
}

// Create minimal capacitor.config.json if not present
const capConfigPath = path.join(ROOT, 'capacitor.config.json');
if (!fs.existsSync(capConfigPath)) {
  const config = {
    appId: "com.ognennyveter.app",
    appName: "Огненный Ветер",
    webDir: "capacitor-app/www",
    bundledWebRuntime: false,
    plugins: {
      Filesystem: {},
      CapacitorSQLite: {
        iosDatabaseLocation: "Library/CapacitorDatabase",
        iosIsStoreLocation: true,
        androidIsStoreLocation: true
      }
    }
  };
  fs.writeFileSync(capConfigPath, JSON.stringify(config, null, 2), 'utf8');
}

console.log('✓ Successfully created capacitor-app/www ready for npx cap sync.');
