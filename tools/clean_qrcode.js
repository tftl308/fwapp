const fs = require('fs');

let code = fs.readFileSync('tools/build-index.mjs', 'utf8');

// Replace createASCII body or escape all newlines in the qrcode section
// Look for `createASCII` in build-index.mjs
code = code.replace(/f\.createASCII=[\s\S]*?f\.renderTo2dContext=/, 'f.createASCII=function(){return "";},f.renderTo2dContext=');

fs.writeFileSync('tools/build-index.mjs', code, 'utf8');
console.log('createASCII stripped');
