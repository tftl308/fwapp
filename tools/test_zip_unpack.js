const fs = require('fs');
const html = fs.readFileSync('data/admin.html', 'utf8');
const s_start = 10793 + 8;
const s_end = 108474;
const jsZipCode = html.slice(s_start, s_end);

const vm = require('vm');
const sandbox = { window: {}, document: {}, navigator: {} };
vm.createContext(sandbox);
vm.runInContext(jsZipCode, sandbox);
const JSZip = sandbox.window.JSZip || sandbox.JSZip;

const template = fs.readFileSync('tools/template_shell.b64', 'utf8');

async function testZip() {
  const zip = new JSZip();
  // Read clean shell from file
  const light_text = fs.readFileSync('огненныйветер.html', 'utf8');
  const marker = 'const INLINED_SONGS_CSV_DATA = ';
  const pos = light_text.indexOf(marker);
  const after_pos = light_text.indexOf(';\n\nfunction parseInlinedSongsCsv', pos);
  const template_shell = light_text.slice(0, pos) + 'const INLINED_SONGS_CSV_DATA = __CSV_DATA_JSON__;' + light_text.slice(after_pos + 1);

  zip.file('shell.html', template_shell);
  const zipB64 = await zip.generateAsync({
    type: 'base64',
    compression: 'DEFLATE',
    compressionOptions: { level: 9 }
  });
  console.log('Zip DEFLATE base64 length:', zipB64.length);

  // Unzip using JSZip
  const zip2 = new JSZip();
  await zip2.loadAsync(zipB64, { base64: true });
  const restored = await zip2.file('shell.html').async('string');
  console.log('Restored length:', restored.length);
  console.log('Has marker:', restored.includes('__CSV_DATA_JSON__'));

  fs.writeFileSync('tools/shell_zip.b64', zipB64, 'ascii');
}
testZip();
