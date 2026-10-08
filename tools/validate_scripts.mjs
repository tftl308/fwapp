import fs from 'fs';
import vm from 'vm';

const filesToCheck = [
  'index.html',
  'огненныйветер.html',
  'огненныйветер_шрифты.html',
  'data/admin.html',
  'dist/reader/index.html'
];

let failed = false;

for (const file of filesToCheck) {
  if (!fs.existsSync(file)) continue;
  const content = fs.readFileSync(file, 'utf8');
  
  // Extract all inline <script> tags (without src attribute)
  const scriptRegex = /<script(?![^>]*\bsrc\b)[^>]*>([\s\S]*?)<\/script>/gi;
  let match;
  let scriptIndex = 0;

  while ((match = scriptRegex.exec(content)) !== null) {
    scriptIndex++;
    const code = match[1];
    if (!code.trim()) continue;

    try {
      new vm.Script(code, { filename: `${file} [script #${scriptIndex}]` });
    } catch (err) {
      console.error(`❌ SYNTAX ERROR in ${file} (script #${scriptIndex}):`, err.message);
      failed = true;
    }
  }
}

if (failed) {
  console.error('\n❌ Script validation failed! Fix syntax errors before proceeding.');
  process.exit(1);
} else {
  console.log('✅ All inline scripts across all HTML files passed syntax check!');
}
