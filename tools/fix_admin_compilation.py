# -*- coding: utf-8 -*-
with open('data/admin.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Find the injected template inside admin.html
pos_embed = text.find('const EMBEDDED_LIGHT_READER_TEMPLATE = ')
assert pos_embed != -1, "pos_embed not found"

pos_func_end = text.find("document.getElementById('btn-admin-compile-light-spa')", pos_embed)
assert pos_func_end != -1, "pos_func_end not found"

clean_compiler_script = """
    // КОМПИЛЯЦИЯ АВТОНОМНОГО СБОРНИКА огненныйветер.html ПРЯМО В БРАУЗЕРЕ (БЕЗ ЗАПРОСОВ И БЕЗ РАЗРЕШЕНИЙ)
    async function compileStandaloneLightReaderFromAdmin() {
      try {
        const currentCsv = buildCanonicalSongsCsv();

        // Попытка 1: чтение локального файла огненныйветер.html
        let templateHtml = '';
        try {
          const resp = await fetch('огненныйветер.html');
          if (resp.ok) templateHtml = await resp.text();
        } catch(e) {}

        if (!templateHtml) {
          try {
            const resp2 = await fetch('../огненныйветер.html');
            if (resp2.ok) templateHtml = await resp2.text();
          } catch(e) {}
        }

        // Попытка 2: чтение через index.html если огненныйветер недоступен напрямую
        if (!templateHtml) {
          try {
            const resp3 = await fetch('../index.html');
            if (resp3.ok) templateHtml = await resp3.text();
          } catch(e) {}
        }

        if (!templateHtml) {
          // Если файл запущен через file:// и браузер блокирует fetch, предлагаем выбрать файл шаблона или скачать CSV
          alert('Браузер в режиме file:// блокирует прямое чтение соседних файлов.\\nСейчас будет скачан готовый канонический файл songs.csv (22 поля).\\nЛибо запустите админку через локальный сервер (http://localhost).');
          downloadSongsCsvFile();
          return;
        }

        // Вшиваем свежий CSV в сборник
        const marker = 'const INLINED_SONGS_CSV_DATA = ';
        const posMarker = templateHtml.indexOf(marker);
        if (posMarker !== -1) {
          const strStart = templateHtml.indexOf('"', posMarker);
          let i = strStart + 1;
          while (i < templateHtml.length) {
            if (templateHtml[i] === '"' && templateHtml[i-1] !== '\\\\') {
              break;
            }
            i++;
          }
          const strEnd = i;
          templateHtml = templateHtml.slice(0, strStart) + JSON.stringify(currentCsv) + templateHtml.slice(strEnd + 1);
        } else {
          // Если это шаблон index.html, внедряем перед первым <script>
          const scriptTag = '<script>';
          const inlinedBlock = '<script>\\nconst INLINED_SONGS_CSV_DATA = ' + JSON.stringify(currentCsv) + ';\\n';
          templateHtml = templateHtml.replace(scriptTag, inlinedBlock);
        }

        // Отдаем скачивание готового файла сразу без запросов разрешений к папкам
        const blob = new Blob([templateHtml], { type: 'text/html;charset=utf-8;' });
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = 'огненныйветер.html';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        setTimeout(() => URL.revokeObjectURL(a.href), 1000);

        alert(`✓ ГОТОВО!\\n\\nФайл «огненныйветер.html» успешно скомпилирован и скачан.\\nВ него вшито ${dbSongs.length} песен со всеми аккордами и текстами.`);
      } catch (err) {
        alert('Ошибка компиляции: ' + err.message);
      }
    }
"""

text = text[:pos_embed] + clean_compiler_script + "\n    " + text[pos_func_end:]

with open('data/admin.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("data/admin.html successfully cleaned and restored!")
