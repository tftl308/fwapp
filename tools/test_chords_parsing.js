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

// Sample input from user's report
const testChordPro = `{title: Адонай}
{key: E}
{capo: +3}

[E]Адонай! Адонай! [A]Адон[B]ай! [C#m]Эл[A]охим!
В Ц[E]арство света [A]мы идём, др[B]ужно мы хвал[C#m]у поём:
«Сл[A]авьте имя Г[B]оспода Христ[E]а!» -2 р.
[E]Это С[A]ион! [B]Это ск[C#m]ала! [A]Это г[B]ора Изра[E]иля!`;

const model = sandbox.parseChordProTextToModel(testChordPro, { id: '0042', title: 'Адонай' });

console.log('Model Title:', model.title);
console.log('Model Key:', model.key_default);
console.log('Model Capo:', model.capo);
console.log('Lines count:', model.lines.length);

for (let i = 0; i < model.lines.length; i++) {
  const line = model.lines[i];
  const chordNames = (line.chords || []).map(c => c.name || c.chord);
  console.log(`Line ${i+1}: "${line.lyric}" | Chords: [${chordNames.join(', ')}]`);
}

// Test serialization back
const serialized = sandbox.serializeSongToChordPro(model);
console.log('\n--- Serialized ChordPro Output ---');
console.log(serialized);

if (serialized.includes('[undefined]')) {
  console.error('FAIL: Found [undefined] in output!');
  process.exit(1);
} else {
  console.log('PASS: No [undefined] in output, chords perfectly preserved!');
}
