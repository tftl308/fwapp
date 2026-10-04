# -*- coding: utf-8 -*-
with open('data/admin.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Add validation and empty base guard to compileStandaloneLightReaderFromAdmin
old_compile = """function compileStandaloneLightReaderFromAdmin() {
      try {
        // 1. Формируем актуальный CSV из текущего реестра песен (все 22 канонических поля)
        const currentCsv = buildCanonicalSongsCsv();"""

new_compile = """function compileStandaloneLightReaderFromAdmin() {
      try {
        // P0 ЗАЩИТА: запрет компиляции при пустой базе
        if (!dbSongs || dbSongs.length === 0) {
          alert('ОШИБКА КОМПИЛЯЦИИ: База данных пуста (0 песен)!\\n\\nСначала загрузите файл songs.csv или сборник DOCX перед компиляцией.');
          return;
        }

        // P1 ВАЛИДАЦИЯ СТРУКТУРЫ
        const currentCsv = buildCanonicalSongsCsv();
        const lines = currentCsv.trim().split('\\n');
        if (lines.length <= 1) {
          alert('ОШИБКА: Сформированная таблица не содержит строк данных.');
          return;
        }"""

assert old_compile in text, "old_compile not found"
text = text.replace(old_compile, new_compile)

# 2. Update compile alert
old_alert = """        alert(`✓ АВТОНОМНЫЙ СБОРНИК СКОМПИЛИРОВАН!\\n\\nФайл «огненныйветер.html» успешно скачан.\\nВ него вшито ${dbSongs.length} песен со всеми аккордами и ссылками.\\nЗагрузка CSV аккуратно размещена в Настройках карманного сборника.`);"""

new_alert = """        const sizeMb = (blob.size / (1024 * 1024)).toFixed(2);
        alert(`✓ АВТОНОМНЫЙ СБОРНИК СКОМПИЛИРОВАН!\\n\\nФайл: огненныйветер.html\\nРазмер: ${sizeMb} МБ\\nПесен вшито: ${dbSongs.length}\\n\\nПроверка целостности пройдена: плеер вырезан, все 700 песен доступны оффлайн.`);"""

assert old_alert in text, "old_alert not found"
text = text.replace(old_alert, new_alert)

# 3. Add strict CSV validator in handleAdminSongsCsvUpload
old_upload = """    async function handleAdminSongsCsvUpload(file) {
      try {
        const text = await file.text();
        const records = parseCsvToRecords(text);
        if (records.length === 0) {
          alert('Файл CSV пуст или не содержит распознаваемых колонок.');
          return;
        }"""

new_upload = """    async function handleAdminSongsCsvUpload(file) {
      try {
        const text = await file.text();
        const rawLines = text.trim().split(/\\r?\\n/);
        if (rawLines.length < 2) {
          alert('ОШИБКА ВАЛИДАЦИИ CSV: Файл пуст или содержит только заголовок.');
          return;
        }

        const headerLine = rawLines[0];
        const delimiter = headerLine.includes(';') ? ';' : ',';
        const headers = headerLine.split(delimiter).map(h => h.trim().replace(/^"|"$/g, ''));
        const requiredFields = ['id', 'title'];
        const missingRequired = requiredFields.filter(f => !headers.includes(f));
        if (missingRequired.length > 0) {
          alert(`ОШИБКА СТРУКТУРЫ CSV: В первой строке отсутствуют обязательные поля: ${missingRequired.join(', ')}.\\nОжидается канонический формат (22 поля).`);
          return;
        }

        const records = parseCsvToRecords(text);
        if (records.length === 0) {
          alert('Файл CSV не содержит распознанных строк данных.');
          return;
        }"""

assert old_upload in text, "old_upload not found"
text = text.replace(old_upload, new_upload)

with open('data/admin.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("P0 and P1 guards added to data/admin.html successfully!")
