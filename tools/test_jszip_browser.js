const fs = require('fs');
const html = fs.readFileSync('data/admin.html', 'utf8');

const s_start = html.indexOf('<script>\n\n    // Embedded JSZip') + 8;
const s_end = html.indexOf('</script>\n</head>');
const jsZipCode = html.slice(s_start, s_end);

const vm = require('vm');
const sandbox = { window: {}, document: {}, navigator: {} };
sandbox.window = sandbox;
sandbox.global = sandbox;
sandbox.self = sandbox;
vm.createContext(sandbox);
vm.runInContext(jsZipCode, sandbox);

console.log('JSZip available:', typeof sandbox.JSZip);
