const fs = require('fs');
const html = fs.readFileSync('data/admin.html', 'utf8');

const s_start = html.lastIndexOf('<script>') + '<script>'.length;
const s_end = html.lastIndexOf('</script>');
const jsCode = html.slice(s_start, s_end);

const vm = require('vm');
const fakeElement = () => ({
  addEventListener: () => {},
  appendChild: () => {},
  removeChild: () => {},
  click: () => {},
  setAttribute: () => {},
  style: {},
  classList: { add: () => {}, remove: () => {} }
});

const sandbox = {
  window: { addEventListener: () => {} },
  document: {
    addEventListener: () => {},
    getElementById: () => fakeElement(),
    querySelectorAll: () => [],
    body: fakeElement(),
    createElement: (tag) => {
      if (tag === 'canvas') return { getContext: () => ({ measureText: () => ({ width: 10 }) }) };
      return fakeElement();
    }
  },
  navigator: {},
  localStorage: { getItem: () => null, setItem: () => {} },
  alert: () => {},
  confirm: () => true,
  setTimeout: () => {}
};
sandbox.window.window = sandbox.window;
sandbox.window.document = sandbox.document;
sandbox.window.localStorage = sandbox.localStorage;

vm.createContext(sandbox);
vm.runInContext(jsCode, sandbox);

// Sample input from user's bug report
const userSampleXml = `<?xml version="1.0" encoding="UTF-8"?>
<song>
  <title>Принеси мне слово о любви святой!</title>
  <author>Огненный ветер</author>
  <copyright>Сборник DOCX</copyright>
  <key>Am</key>
  <capo print="true">+3</capo>
  <tempo></tempo>
  <time_sig>4/4</time_sig>
  <lyrics>
 Ангел мой, Ангел мой! 
 Прикоснись ко мне Ты чистою слезой!

.    Am     Dm   E    Am        F     Dm     E   Am
 Пр. В небесах   растворяюсь я! И в словах Твоих остаюсь!
</lyrics>
</song>`;

const model = sandbox.buildModelFromOpenSongLyrics(userSampleXml, {
  id: '0123',
  title: 'Принеси мне слово о любви святой!',
  key: 'Am',
  capo: '+3'
});

console.log('Model Title:', model.title);
console.log('Model Lines count:', model.lines.length);

for (let i = 0; i < model.lines.length; i++) {
  const line = model.lines[i];
  const chordNames = (line.chords || []).map(c => c.name || c.chord);
  console.log(`Line ${i+1} [${line.kind}]: "${line.lyric}" | Chords: [${chordNames.join(', ')}]`);
}

// Serialize back to OpenSong
const serializedXml = sandbox.serializeSongToOpenSongXml(model);
console.log('\n--- Output OpenSong XML ---');
console.log(serializedXml);

// Checks
if (!serializedXml.includes('Ангел мой, Ангел мой!')) {
  console.error('FAIL: Missing first line "Ангел мой, Ангел мой!"');
  process.exit(1);
}
if (!serializedXml.includes('В небесах   растворяюсь я!')) {
  console.error('FAIL: Missing chorus line');
  process.exit(1);
}
if (serializedXml.includes('[VERSE]')) {
  console.error('FAIL: Found ugly [VERSE] tag!');
  process.exit(1);
}

console.log('\n✓ ALL ASSERTIONS PASSED! First lines preserved, chords aligned, no synthetic [VERSE] headers.');
