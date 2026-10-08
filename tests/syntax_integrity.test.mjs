import test from 'node:test';
import assert from 'node:assert';
import fs from 'node:fs';
import vm from 'node:vm';
import path from 'node:path';

test('HTML Inline Scripts Syntax Verification (P0 Zero-Crash Invariant)', () => {
  const filesToCheck = [
    'index.html',
    'огненныйветер.html',
    'огненныйветер_шрифты.html',
    'data/admin.html'
  ];

  for (const relPath of filesToCheck) {
    const fullPath = path.resolve(relPath);
    if (!fs.existsSync(fullPath)) continue;
    
    const htmlContent = fs.readFileSync(fullPath, 'utf8');
    const scriptRegex = /<script(?![^>]*\bsrc\b)[^>]*>([\s\S]*?)<\/script>/gi;
    let match;
    let idx = 0;

    while ((match = scriptRegex.exec(htmlContent)) !== null) {
      idx++;
      const code = match[1];
      if (!code.trim()) continue;

      try {
        new vm.Script(code, { filename: `${relPath} [script #${idx}]` });
      } catch (err) {
        assert.fail(`Fatal syntax error in ${relPath} (script tag #${idx}): ${err.message}`);
      }
    }
  }
});
