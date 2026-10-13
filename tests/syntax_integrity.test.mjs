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
    'data/admin.html',
    'dist/pwa/index.html',
    'dist/reader/index.html'
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

      // 1. Static AST compile check
      try {
        new vm.Script(code, { filename: relPath + ' [script #' + idx + ']' });
      } catch (err) {
        assert.fail('Fatal syntax error in ' + relPath + ' (script #' + idx + '): ' + err.message);
      }

      // 2. Strict Identifier and Reference Verification:
      // Checks for unquoted identifiers in addEventListener/removeEventListener/getElementById
      const lines = code.split('\n');
      for (let lineNum = 0; lineNum < lines.length; lineNum++) {
        const line = lines[lineNum];
        
        const unquotedEventMatch = line.match(/(?:addEventListener|removeEventListener)\s*\(\s*([a-zA-Z0-9_\-]+)\s*,/);
        if (unquotedEventMatch) {
          const idName = unquotedEventMatch[1];
          if (['touchstart', 'touchmove', 'touchend', 'click', 'keydown', 'keyup', 'resize', 'popstate', 'play', 'pause'].includes(idName)) {
            assert.fail('Fatal unquoted event identifier in ' + relPath + ' line ' + (lineNum + 1) + ': addEventListener(' + idName + ') must be string literal (\'' + idName + '\')');
          }
        }

        const unquotedGetElementMatch = line.match(/getElementById\s*\(\s*([a-zA-Z0-9_\-]+)\s*\)/);
        if (unquotedGetElementMatch) {
          const idName = unquotedGetElementMatch[1];
          if (idName.includes('-')) {
            assert.fail('Fatal unquoted hyphenated element ID in ' + relPath + ' line ' + (lineNum + 1) + ': getElementById(' + idName + ') will cause ReferenceError/NaN');
          }
        }
      }
    }
  }
});
