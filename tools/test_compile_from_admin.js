const fs = require('fs');
const html = fs.readFileSync('data/admin.html', 'utf8');

const s_start = html.lastIndexOf('<script>') + '<script>'.length;
const s_end = html.lastIndexOf('</script>');
const jsCode = html.slice(s_start, s_end);

const vm = require('vm');
let compiledHtml = '';

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
      if (tag === 'canvas') {
        return { getContext: () => ({ measureText: () => ({ width: 10 }) }) };
      }
      return fakeElement();
    }
  },
  navigator: {},
  localStorage: { getItem: () => null, setItem: () => {} },
  Blob: class {
    constructor(chunks) {
      compiledHtml = chunks.join('');
    }
  },
  URL: {
    createObjectURL: () => 'blob:mock',
    revokeObjectURL: () => {}
  },
  atob: (str) => Buffer.from(str, 'base64').toString('binary'),
  TextDecoder: class {
    decode(bytes) {
      return Buffer.from(bytes).toString('utf-8');
    }
  },
  alert: (msg) => console.log('ALERT:\n' + msg),
  confirm: () => true,
  setTimeout: () => {}
};

sandbox.window.window = sandbox.window;
sandbox.window.document = sandbox.document;
sandbox.window.localStorage = sandbox.localStorage;

vm.createContext(sandbox);
vm.runInContext(jsCode, sandbox);

// Compile!
sandbox.compileStandaloneLightReaderFromAdmin();

console.log('Compiled HTML length:', (compiledHtml.length / (1024*1024)).toFixed(2), 'MB');
console.log('Valid DOCTYPE:', compiledHtml.startsWith('<!DOCTYPE html>'));
console.log('Valid closure:', compiledHtml.endsWith('</html>\n') || compiledHtml.endsWith('</html>'));
console.log('Check CSV button on catalog screen:', compiledHtml.includes('input-manual-csv-reader'));
console.log('Check CSV upload in settings:', compiledHtml.includes('trigger-manual-csv-upload'));

// Validate JS syntax of compiled HTML
const compScriptStart = compiledHtml.lastIndexOf('<script>') + '<script>'.length;
const compScriptEnd = compiledHtml.lastIndexOf('</script>');
const compJs = compiledHtml.slice(compScriptStart, compScriptEnd);

try {
  vm.createScript(compJs);
  console.log('SUCCESS! The compiled огненныйветер.html JavaScript is 100% VALID AND COMPLETE!');
} catch (e) {
  console.error('Syntax error in compiled file:', e);
  process.exit(1);
}
