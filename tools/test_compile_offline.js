const fs = require('fs');
const html = fs.readFileSync('data/admin.html', 'utf8');

const s_start = html.lastIndexOf('<script>') + '<script>'.length;
const s_end = html.lastIndexOf('</script>');
const jsCode = html.slice(s_start, s_end);

const vm = require('vm');
let downloadedFilename = '';
let downloadedBlobContent = '';

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
  window: {
    addEventListener: () => {}
  },
  document: {
    addEventListener: () => {},
    getElementById: () => fakeElement(),
    querySelectorAll: () => [],
    body: fakeElement(),
    createElement: (tag) => {
      if (tag === 'canvas') {
        return { getContext: () => ({ measureText: () => ({ width: 10 }) }) };
      }
      return fakeElement();
    }
  },
  navigator: {},
  localStorage: {
    getItem: () => null,
    setItem: () => {}
  },
  Blob: class {
    constructor(chunks, opts) {
      downloadedBlobContent = chunks.join('');
    }
  },
  URL: {
    createObjectURL: () => 'blob:mock',
    revokeObjectURL: () => {}
  },
  alert: (msg) => console.log('ALERT CALLED:\n' + msg),
  confirm: () => true,
  setTimeout: () => {}
};

sandbox.window.window = sandbox.window;
sandbox.window.document = sandbox.document;
sandbox.window.localStorage = sandbox.localStorage;

vm.createContext(sandbox);
vm.runInContext(jsCode, sandbox);

// Run the compilation
sandbox.compileStandaloneLightReaderFromAdmin();

console.log('Resulting compiled HTML length:', (downloadedBlobContent.length / (1024 * 1024)).toFixed(2), 'MB');
console.log('Contains INLINED_SONGS_CSV_DATA:', downloadedBlobContent.includes('INLINED_SONGS_CSV_DATA'));
console.log('Contains song 0042 Адонай:', downloadedBlobContent.includes('0042;42;Адонай'));
console.log('Contains song 0690 Я шепчу молитву:', downloadedBlobContent.includes('0690;690;Я шепчу молитву'));
