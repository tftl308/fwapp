const fs = require('fs');
const html = fs.readFileSync('data/admin.html', 'utf8');
const jszipPos = html.indexOf('JSZip');
console.log('JSZip inside admin.html pos:', jszipPos);
