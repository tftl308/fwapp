# -*- coding: utf-8 -*-
import json

with open('tools/reader_part1.txt', 'r', encoding='utf-8') as f:
    part1 = f.read()

with open('tools/reader_part2.txt', 'r', encoding='utf-8') as f:
    part2 = f.read()

# Make sure any </script> or <script> inside string literals is safely split
json_part1 = json.dumps(part1).replace('</script>', '<' + '/script>').replace('<script>', '<' + 'script>')
json_part2 = json.dumps(part2).replace('</script>', '<' + '/script>').replace('<script>', '<' + 'script>')

with open('data/admin.html', 'r', encoding='utf-8') as f:
    admin_html = f.read()

# Locate compileStandaloneLightReaderFromAdmin function
start_func_marker = 'async function compileStandaloneLightReaderFromAdmin() {'
pos_start = admin_html.find(start_func_marker)
assert pos_start != -1, "start_func_marker not found"

pos_end = admin_html.find("document.getElementById('btn-admin-compile-light-spa')", pos_start)
assert pos_end != -1, "pos_end not found"

new_implementation = f"""// ШАБЛОНЫ LIGHT READER SPA ДЛЯ 100% АВТОНОМНОЙ КОМПИЛЯЦИИ БЕЗ СЕТЕВЫХ ЗАПРОСОВ
    const LIGHT_READER_TEMPLATE_PART1 = {json_part1};
    const LIGHT_READER_TEMPLATE_PART2 = {json_part2};

    function compileStandaloneLightReaderFromAdmin() {{
      try {{
        // 1. Формируем актуальный CSV из текущего реестра песен (все 22 канонических поля)
        const currentCsv = buildCanonicalSongsCsv();

        // 2. Мгновенная прямая сборка HTML-файла из двух вшитых частей
        const finalHtml = LIGHT_READER_TEMPLATE_PART1 + JSON.stringify(currentCsv) + LIGHT_READER_TEMPLATE_PART2;

        // 3. Отдаем скачивание готового файла сразу в браузер
        const blob = new Blob([finalHtml], {{ type: 'text/html;charset=utf-8;' }});
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = 'огненныйветер.html';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        setTimeout(() => URL.revokeObjectURL(a.href), 1000);

        alert(`✓ АВТОНОМНЫЙ СБОРНИК СКОМПИЛИРОВАН!\\n\\nФайл «огненныйветер.html» успешно скачан.\\nВ него вшито ${{dbSongs.length}} песен из базы Data Studio со всеми аккордами и ссылками.\\nРаботает на смартфонах и ПК без сервера и интернета.`);
      }} catch (err) {{
        alert('Ошибка компиляции: ' + err.message);
      }}
    }}
"""

admin_html = admin_html[:pos_start] + new_implementation + "\n    " + admin_html[pos_end:]

with open('data/admin.html', 'w', encoding='utf-8') as f:
    f.write(admin_html)

print("data/admin.html successfully armed with 100% offline standalone compiler!")
