# -*- coding: utf-8 -*-
with open('tools/b64_reader_template.txt', 'r', encoding='ascii') as f:
    b64_template = f.read()

with open('data/admin.html', 'r', encoding='utf-8') as f:
    admin_html = f.read()

# Locate where the compiler templates and functions are
pos_start = admin_html.find('// ШАБЛОНЫ LIGHT READER SPA')
if pos_start == -1:
    pos_start = admin_html.find('const LIGHT_READER_TEMPLATE_PART1')
assert pos_start != -1

pos_end = admin_html.find("document.getElementById('btn-admin-compile-light-spa')", pos_start)
assert pos_end != -1

new_compiler_block = f"""// ШАБЛОН LIGHT READER SPA В BASE64 (100% ГАРАНТИЯ ЦЕЛОСТНОСТИ СИНТАКСИСА И АВТОНОМНОЙ СБОРКИ)
    const LIGHT_READER_BASE64_TEMPLATE = "{b64_template}";

    function compileStandaloneLightReaderFromAdmin() {{
      try {{
        // 1. Формируем актуальный CSV из текущего реестра песен (все 22 канонических поля)
        const currentCsv = buildCanonicalSongsCsv();

        // 2. Декодируем чистый шаблон HTML из Base64 (без единого риска для парсера браузера)
        const binaryStr = atob(LIGHT_READER_BASE64_TEMPLATE);
        const bytes = new Uint8Array(binaryStr.length);
        for (let i = 0; i < binaryStr.length; i++) {{
          bytes[i] = binaryStr.charCodeAt(i);
        }}
        const templateHtml = new TextDecoder('utf-8').decode(bytes);

        // 3. Вшиваем CSV данные в сборник вместо метки
        const finalHtml = templateHtml.replace('__CSV_DATA_JSON__', JSON.stringify(currentCsv));

        // 4. Отдаем скачивание файла прямо в браузер
        const blob = new Blob([finalHtml], {{ type: 'text/html;charset=utf-8;' }});
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = 'огненныйветер.html';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        setTimeout(() => URL.revokeObjectURL(a.href), 1000);

        alert(`✓ АВТОНОМНЫЙ СБОРНИК СКОМПИЛИРОВАН!\\n\\nФайл «огненныйветер.html» успешно скачан.\\nВ него вшито ${{dbSongs.length}} песен со всеми аккордами и ссылками.\\nЗагрузка CSV аккуратно размещена в Настройках карманного сборника.`);
      }} catch (err) {{
        alert('Ошибка компиляции: ' + err.message);
      }}
    }}
"""

admin_html = admin_html[:pos_start] + new_compiler_block + "\n    " + admin_html[pos_end:]

with open('data/admin.html', 'w', encoding='utf-8') as f:
    f.write(admin_html)

print("data/admin.html successfully armed with clean Base64 compiler!")
