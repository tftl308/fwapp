# -*- coding: utf-8 -*-
with open('data/admin.html', 'r', encoding='utf-8') as f:
    admin_html = f.read()

# 1. Update buildCanonicalSongsCsv in admin.html to output 22 canonical columns
pos_start = admin_html.find('function buildCanonicalSongsCsv() {')
pos_end = admin_html.find('function publishToApplicationStorage()', pos_start)
assert pos_start != -1 and pos_end != -1, "buildCanonicalSongsCsv boundaries not found"

new_build_func = """function buildCanonicalSongsCsv() {
      const headers = [
        'id', 'number', 'title', 'author', 'key', 'capo', 'tempo',
        'time_signature', 'duration', 'predelay', 'presentation',
        'theme', 'alttheme', 'user1', 'user2', 'user3',
        'lyrics', 'chordpro', 'notes', 'link_audio', 'link_youtube', 'custom_chords'
      ];
      const lines = [headers.join(';')];

      dbSongs.forEach(s => {
        const lyrics = s.lyrics || s.body_plain || (s.chordpro ? s.chordpro.replace(/\\[[^\\]]+\\]/g, '') : '');
        const chordpro = s.chordpro || s.body_chordpro || '';
        const row = [
          String(s.id || '').padStart(4, '0'),
          s.number || parseInt(s.id, 10) || '',
          s.title || '',
          s.author || 'Огненный ветер',
          s.key || s.key_default || '',
          s.capo || '',
          s.tempo || '',
          s.time_signature || '4/4',
          s.duration || '',
          s.predelay || '',
          s.presentation || '',
          s.theme || s.alt_title || '',
          s.alttheme || '',
          s.user1 || '',
          s.user2 || '',
          s.user3 || '',
          lyrics,
          chordpro,
          s.notes || '',
          s.link_audio || '',
          s.link_youtube || '',
          s.custom_chords || ''
        ];

        const escapedRow = row.map(val => {
          let str = String(val === undefined || val === null ? '' : val);
          if (str.includes(';') || str.includes('"') || str.includes('\\n') || str.includes('\\r')) {
            str = '"' + str.replace(/"/g, '""') + '"';
          }
          return str;
        });
        lines.push(escapedRow.join(';'));
      });

      return lines.join('\\n');
    }

    """

admin_html = admin_html[:pos_start] + new_build_func + admin_html[pos_end:]

# 2. Add CSV dropzone/input in Tab 1 (right next to DOCX and OpenSong)
old_dropzones = """      <!-- Источники ввода: DOCX, OpenSong файлы и Копипаст -->
      <div style="display: grid; grid-template-columns: 1.2fr 1.2fr 1fr; gap: 0.8rem; margin-bottom: 1rem;">
        <div class="dropzone" id="docx-dropzone" style="padding: 1rem; min-height: 110px;">
          <input type="file" id="input-docx-chords" accept=".docx" multiple style="display: none;">
          <div style="font-size: 1.6rem; margin-bottom: 0.2rem;">📄</div>
          <strong style="font-size: 0.88rem;">1. Загрузить DOCX файл(ы)</strong>
          <p style="color: var(--muted); font-size: 0.75rem; margin-top: 0.2rem;">Автораспознавание сеток аккордов и оглавления</p>
          <span id="docx-file-name" style="color: var(--info); font-size: 0.8rem; font-weight: bold; margin-top: 0.2rem; display: block;">Файл не выбран</span>
        </div>"""

new_dropzones = """      <!-- Источники ввода: DOCX, songs.csv, OpenSong файлы и Копипаст -->
      <div style="display: grid; grid-template-columns: 1.2fr 1.2fr 1.2fr 1fr; gap: 0.8rem; margin-bottom: 1rem;">
        <div class="dropzone" id="docx-dropzone" style="padding: 1rem; min-height: 110px;">
          <input type="file" id="input-docx-chords" accept=".docx" multiple style="display: none;">
          <div style="font-size: 1.6rem; margin-bottom: 0.2rem;">📄</div>
          <strong style="font-size: 0.88rem;">1. Загрузить DOCX файл(ы)</strong>
          <p style="color: var(--muted); font-size: 0.75rem; margin-top: 0.2rem;">Автораспознавание сеток аккордов и оглавления</p>
          <span id="docx-file-name" style="color: var(--info); font-size: 0.8rem; font-weight: bold; margin-top: 0.2rem; display: block;">Файл не выбран</span>
        </div>

        <div class="dropzone" id="songs-csv-dropzone" style="padding: 1rem; min-height: 110px; border-color: #10b981; background: #ecfdf5; cursor: pointer;">
          <input type="file" id="input-admin-songs-csv" accept=".csv,text/csv" style="display: none;">
          <div style="font-size: 1.6rem; margin-bottom: 0.2rem;">📊</div>
          <strong style="font-size: 0.88rem; color: #047857;">2. Загрузить songs.csv</strong>
          <p style="color: var(--muted); font-size: 0.75rem; margin-top: 0.2rem;">Импортировать актуальный файл базы (22 поля)</p>
          <span id="csv-import-status" style="color: #047857; font-size: 0.8rem; font-weight: bold; margin-top: 0.2rem; display: block;">Нажмите для выбора CSV</span>
        </div>"""

assert old_dropzones in admin_html, "old_dropzones not found in admin.html"
admin_html = admin_html.replace(old_dropzones, new_dropzones)

# 3. Add compilation button to the top header and Tab 4 (publish tab)
new_header_action_button = """<button class="btn btn-primary" id="btn-admin-compile-light-spa" style="background: #b45309; border-color: #92400e; font-weight: 700;">📦 Скомпилировать огненныйветер.html</button>"""

admin_html = admin_html.replace(
  '<button class="btn btn-outline" id="btn-export-csv-bundle">📦 Экспорт CSV таблиц</button>',
  new_header_action_button + '\n      <button class="btn btn-outline" id="btn-export-csv-bundle">📦 Экспорт CSV таблиц</button>'
)

# 4. Add compilation card in Tab 4 (Publish Tab)
old_publish_card = """        <div style="border: 1px solid var(--border); border-radius: 0.6rem; padding: 1.25rem; background: #fff;">
          <h3 style="margin-bottom: 0.5rem;">Способ 2: Скачивание файлов для ручной замены или раздачи</h3>"""

new_publish_card = """        <div style="border: 2px solid #b45309; border-radius: 0.6rem; padding: 1.25rem; background: #fffbeb; grid-column: 1 / -1; margin-bottom: 0.5rem;">
          <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem;">
            <div>
              <h3 style="color: #92400e; margin-bottom: 0.3rem;">📦 Сборка автономного карманного сборника (Light Reader SPA)</h3>
              <p style="font-size: 0.85rem; color: #78350f; margin: 0;">
                Генерирует готовый файл <strong>огненныйветер.html</strong> со вшитой базой всех песен. Без плеера, со ссылками на внешние медиа, открывается двойным кликом на смартфонах и ПК.
              </p>
            </div>
            <button class="btn btn-primary" id="btn-publish-compile-spa" style="background: #b45309; border-color: #92400e; font-weight: 700; padding: 0.6rem 1.2rem;">
              ⚡ Скомпилировать и скачать огненныйветер.html
            </button>
          </div>
        </div>

        <div style="border: 1px solid var(--border); border-radius: 0.6rem; padding: 1.25rem; background: #fff;">
          <h3 style="margin-bottom: 0.5rem;">Способ 2: Скачивание файлов для ручной замены или раздачи</h3>"""

assert old_publish_card in admin_html, "old_publish_card not found"
admin_html = admin_html.replace(old_publish_card, new_publish_card)

# 5. Add JavaScript handlers: CSV loading into dbSongs + compiling огненныйветер.html
js_logic = """
    // =========================================================================
    // ПРЯМАЯ ЗАГРУЗКА songs.csv В АДМИН-ПАНЕЛЬ
    // =========================================================================
    const csvDropzone = document.getElementById('songs-csv-dropzone');
    const csvInput = document.getElementById('input-admin-songs-csv');

    if (csvDropzone && csvInput) {
      csvDropzone.addEventListener('click', () => csvInput.click());

      csvDropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        csvDropzone.style.borderColor = '#059669';
        csvDropzone.style.background = '#d1fae5';
      });

      csvDropzone.addEventListener('dragleave', () => {
        csvDropzone.style.borderColor = '#10b981';
        csvDropzone.style.background = '#ecfdf5';
      });

      csvDropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        csvDropzone.style.borderColor = '#10b981';
        csvDropzone.style.background = '#ecfdf5';
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
          handleAdminSongsCsvUpload(e.dataTransfer.files[0]);
        }
      });

      csvInput.addEventListener('change', (e) => {
        if (e.target.files && e.target.files[0]) {
          handleAdminSongsCsvUpload(e.target.files[0]);
        }
      });
    }

    async function handleAdminSongsCsvUpload(file) {
      try {
        const text = await file.text();
        const records = parseCsvToRecords(text);
        if (records.length === 0) {
          alert('Файл CSV пуст или не содержит распознаваемых колонок.');
          return;
        }

        const normalizedSongs = records.map(r => ({
          id: String(r.id || '').padStart(4, '0'),
          number: r.number || parseInt(r.id, 10) || '',
          title: r.title || 'Без названия',
          author: r.author || '',
          key: r.key || '',
          key_default: r.key || '',
          capo: r.capo || '',
          tempo: r.tempo || '',
          time_signature: r.time_signature || '4/4',
          duration: r.duration || '',
          predelay: r.predelay || '',
          presentation: r.presentation || '',
          theme: r.theme || r.alt_title || '',
          alttheme: r.alttheme || '',
          user1: r.user1 || '',
          user2: r.user2 || '',
          user3: r.user3 || '',
          lyrics: r.lyrics || r.body_plain || '',
          body_plain: r.lyrics || r.body_plain || '',
          chordpro: r.chordpro || r.body_chordpro || '',
          body_chordpro: r.chordpro || r.body_chordpro || '',
          notes: r.notes || '',
          link_audio: r.link_audio || '',
          link_youtube: r.link_youtube || '',
          custom_chords: r.custom_chords || '',
          is_empty_body: (!r.lyrics && !r.chordpro && !r.body_plain && !r.body_chordpro) ? 'true' : 'false'
        }));

        dbSongs = normalizedSongs;
        dbTables.songs = normalizedSongs;
        localStorage.setItem('ov_admin_songs', JSON.stringify(dbSongs));
        localStorage.setItem('ov_admin_songs_table', JSON.stringify(dbSongs));

        saveDb();
        renderCatalog();
        updateTableStatCounts();

        const statusEl = document.getElementById('csv-import-status');
        if (statusEl) {
          statusEl.textContent = `✓ Загружено ${normalizedSongs.length} песен!`;
        }

        alert(`УСПЕШНО!\\n\\nБаза songs.csv успешно импортирована в Data Studio.\\nВсего загружено песен: ${normalizedSongs.length}.\\nРеестр и все 22 поля обновлены.`);
      } catch (err) {
        alert('Ошибка при чтении CSV файла: ' + err.message);
      }
    }

    // =========================================================================
    // КОМПИЛЯЦИЯ АВТОНОМНОГО СБОРНИКА огненныйветер.html ПРЯМО ИЗ АДМИНКИ
    // =========================================================================
    async function compileStandaloneLightReaderFromAdmin() {
      try {
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

        if (!templateHtml) {
          alert('Не удалось получить шаблон огненныйветер.html. Убедитесь, что файл доступен в корне проекта.');
          return;
        }

        // Generate the exact canonical CSV with current dbSongs
        const currentCsv = buildCanonicalSongsCsv();

        // Replace INLINED_SONGS_CSV_DATA in templateHtml
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
        }

        const blob = new Blob([templateHtml], { type: 'text/html;charset=utf-8;' });
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = 'огненныйветер.html';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);

        alert(`✓ АВТОНОМНЫЙ СБОРНИК СКОМПИЛИРОВАН!\\n\\nФайл огненныйветер.html успешно скачан.\\nВ него вшито ${dbSongs.length} песен из текущей базы админки.`);
      } catch (err) {
        alert('Ошибка компиляции: ' + err.message);
      }
    }

    document.getElementById('btn-admin-compile-light-spa')?.addEventListener('click', compileStandaloneLightReaderFromAdmin);
    document.getElementById('btn-publish-compile-spa')?.addEventListener('click', compileStandaloneLightReaderFromAdmin);
"""

pos_close_script = admin_html.rfind('</script>')
assert pos_close_script != -1
admin_html = admin_html[:pos_close_script] + js_logic + admin_html[pos_close_script:]

with open('data/admin.html', 'w', encoding='utf-8') as f:
    f.write(admin_html)

print("data/admin.html successfully patched with direct CSV loading and SPA compilation!")
