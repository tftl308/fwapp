import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const html = fs.readFileSync('index.html', 'utf-8');

const scriptStart = html.indexOf('<script>');
const scriptEnd = html.lastIndexOf('</script>');
const scriptContent = html.slice(scriptStart + 8, scriptEnd);

const codeToRun = `
${scriptContent.slice(scriptContent.indexOf('function normalizeSearchText'), scriptContent.indexOf('class SearchEngine'))}
${scriptContent.slice(scriptContent.indexOf('class SearchEngine'), scriptContent.indexOf('// ==========================================\n// 5.5'))}
globalThis.SearchEngine = SearchEngine;
`;

const sandbox = {
  window: {},
  document: { addEventListener: () => {}, querySelector: () => null, getElementById: () => null },
  store: { getState: () => ({ catalogSortMode: 'alpha-asc' }) },
  AppLogger: { info: () => {}, warn: () => {}, error: () => {} }
};
vm.createContext(sandbox);
vm.runInContext(codeToRun, sandbox);

test('SearchEngine: multi-word query matches arbitrary word permutations', () => {
  const songs = [
    { id: '0001', title: 'Белый снег', body_plain: 'зима пришла', theme: '', alttheme: '', author: '', key: '' },
    { id: '0002', title: 'Огонь горит', body_plain: 'ветер воет в ночи', theme: '', alttheme: '', author: '', key: '' }
  ];

  const engine = new sandbox.SearchEngine(songs);
  
  // Forward order
  const res1 = engine.search('белый снег');
  assert.equal(res1[0].id, '0001');

  // Reverse order
  const res2 = engine.search('снег белый');
  assert.equal(res2[0].id, '0001');

  // Permuted across body
  const res3 = engine.search('воет огонь');
  assert.equal(res3[0].id, '0002');
});

test('SearchEngine: exact match in lyrics has higher priority than fuzzy match with typo in title', () => {
  const songs = [
    {
      id: '0001',
      title: 'Белый снек', // опечатка в названии (снек вместо снег)
      body_plain: 'тра ла ла ла ла',
      theme: '', alttheme: '', author: '', key: ''
    },
    {
      id: '0002',
      title: 'Песня о зиме',
      body_plain: 'кругом лежит белый снег и сверкает на солнце', // точное совпадение слов в тексте
      theme: '', alttheme: '', author: '', key: ''
    }
  ];

  const engine = new sandbox.SearchEngine(songs);
  const results = engine.search('белый снег');

  // Song 0002 (exact matches in body) must be ranked ahead of Song 0001 (fuzzy match in title)
  assert.equal(results[0].id, '0002', 'Песня с точным совпадением слов в тексте должна ранжироваться выше, чем нечеткое совпадение с опечаткой в названии');
  assert.equal(results[1].id, '0001');
});
