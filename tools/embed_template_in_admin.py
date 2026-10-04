# -*- coding: utf-8 -*-
import json

with open('огненныйветер.html', 'r', encoding='utf-8') as f:
    light_html = f.read()

# Replace the bulky INLINED_SONGS_CSV_DATA in template with a single placeholder token
marker = 'const INLINED_SONGS_CSV_DATA = '
pos = light_html.find(marker)
assert pos != -1, "Marker not found in огненныйветер.html"

after_pos = light_html.find(';\n\nfunction parseInlinedSongsCsv', pos)
assert after_pos != -1, "after_pos not found in огненныйветер.html"

template_clean = light_html[:pos] + 'const INLINED_SONGS_CSV_DATA = "__INLINED_SONGS_CSV_PLACEHOLDER__"' + light_html[after_pos:]

with open('data/admin.html', 'r', encoding='utf-8') as f:
    admin_html = f.read()

# Replace compileStandaloneLightReaderFromAdmin function with a completely self-contained version
old_compile_fn_start = 'async function compileStandaloneLightReaderFromAdmin() {'
pos_fn = admin_html.find(old_compile_fn_start)
assert pos_fn != -1, "compileStandaloneLightReaderFromAdmin not found"

pos_fn_end = admin_html.find("document.getElementById('btn-admin-compile-light-spa')", pos_fn)
assert pos_fn_end != -1, "btn-admin-compile-light-spa not found"

# Serialize template_clean as JSON string, but protect closing </script> tags from breaking HTML parsing!
safe_template_json = json.dumps(template_clean).replace('</script>', '<\\/script>').replace('</Script>', '<\\/Script>')

new_compile_logic = f"""// ВШИТЫЙ ШАБЛОН LIGHT READER SPA (работает оффлайн без fetch и без запросов разрешений)
    const EMBEDDED_LIGHT_READER_TEMPLATE = {safe_template_json};

    function compileStandaloneLightReaderFromAdmin() {{
      try {{
        // 1. Формируем актуальный CSV из текущего реестра песен (все 22 канонических поля)
        const currentCsv = buildCanonicalSongsCsv();

        // 2. Вшиваем CSV в шаблон вместо плейсхолдера
        const serializedCsv = JSON.stringify(currentCsv);
        let finalHtml = EMBEDDED_LIGHT_READER_TEMPLATE.replace('"__INLINED_SONGS_CSV_PLACEHOLDER__"', serializedCsv);

        // 3. Мгновенно отдаем готовый автономный файл без единого всплывающего системного окна
        const blob = new Blob([finalHtml], {{ type: 'text/html;charset=utf-8;' }});
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = 'огненныйветер.html';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(a.href);

        alert(`✓ ГОТОВО!\\n\\nАвтономный файл «огненныйветер.html» успешно скомпилирован и сохранен в Загрузки.\\nВ него вшито ${{dbSongs.length}} песен со всеми аккордами и текстами.\\nФайл открывается на любых смартфонах и компьютерах.`);
      }} catch (err) {{
        alert('Ошибка компиляции: ' + err.message);
      }}
    }}

    """

admin_html = admin_html[:pos_fn] + new_compile_logic + admin_html[pos_fn_end:]

with open('data/admin.html', 'w', encoding='utf-8') as f:
    f.write(admin_html)

print("data/admin.html successfully upgraded: instant client-side offline compilation without any permissions or fetch!")
