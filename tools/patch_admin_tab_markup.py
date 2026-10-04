# -*- coding: utf-8 -*-
with open('data/admin.html', 'r', encoding='utf-8') as f:
    content = f.read()

m1 = content.find('id="tab-docx-songs"')
m2 = content.find('id="tab-docx-ids"')
assert m1 != -1 and m2 != -1, "Tabs not found"

# Find end of section for tab-docx-songs
section_end = content.rfind('</section>', m1, m2)
assert section_end != -1, "section_end not found"

new_tab_html = """id="tab-docx-songs" class="tab-pane">
    <div class="card">
      <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.8rem; flex-wrap: wrap; gap: 0.5rem;">
        <div>
          <h2><span class="step-number">1</span> Оцифровка DOCX & OpenSong/ChordPro Студия</h2>
          <p style="color: var(--muted); font-size: 0.88rem; margin-top: 0.3rem;">
            Геометрическое выравнивание пропорционального шрифта Times New Roman (Dynamic Programming), визуальный Drag-and-Drop редактор аккордов и экспорт в OpenSong, ChordPro, CSV и печать PDF/DOCX.
          </p>
        </div>
        <div style="display: flex; gap: 0.5rem; align-items: center;">
          <span class="badge badge-info">Geometric DP Align v2.0</span>
          <span class="converter-stat-badge badge-conf-green" id="stat-high-conf" title="Высокая уверенность (conf > 0.8)">🟢 0</span>
          <span class="converter-stat-badge badge-conf-yellow" id="stat-med-conf" title="Средняя уверенность (0.5–0.8)">🟡 0</span>
          <span class="converter-stat-badge badge-conf-red" id="stat-low-conf" title="Требует проверки (< 0.5)">🔴 0</span>
        </div>
      </div>

      <!-- Источники ввода: DOCX или Копипаст текста -->
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem;">
        <div class="dropzone" id="docx-dropzone" style="padding: 1.2rem; min-height: 120px;">
          <input type="file" id="input-docx-chords" accept=".docx" multiple style="display: none;">
          <div style="font-size: 1.8rem; margin-bottom: 0.3rem;">📄</div>
          <strong>Загрузить .docx файл(ы) сборника</strong>
          <p style="color: var(--muted); font-size: 0.78rem; margin-top: 0.2rem;">Распаковка через JSZip, извлечение стилей w:b и геометрических отступов</p>
          <span id="docx-file-name" style="color: var(--info); font-size: 0.82rem; font-weight: bold; margin-top: 0.3rem; display: block;">Файл не выбран</span>
        </div>

        <div style="border: 1px dashed var(--border); border-radius: 6px; padding: 0.8rem; background: #fafafa; display: flex; flex-direction: column;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem;">
            <strong style="font-size: 0.85rem;">📝 Или вставьте текст песни:</strong>
            <button class="btn btn-sm btn-outline" id="btn-parse-pasted-text">Распознать вставку</button>
          </div>
          <textarea id="paste-text-input" placeholder="Вставьте сюда песню (текст с аккордами сверху, формат ChordPro [Am] или OpenSong с точкой .Am)..." style="flex: 1; min-height: 65px; font-family: monospace; font-size: 0.78rem; padding: 0.4rem; border: 1px solid var(--border); border-radius: 4px; resize: none;"></textarea>
        </div>
      </div>

      <!-- Панель управления и экспорта -->
      <div class="converter-toolbar">
        <button class="btn" id="btn-parse-docx-chords" disabled>⚡ 1. Запустить точный DP-парсинг</button>
        <button class="btn btn-outline" id="btn-realign-current-song" title="Автоматически пересчитать привязку аккордов для текущей песни">⟲ Автовыравнивание</button>
        <div style="height: 24px; width: 1px; background: #cbd5e1; margin: 0 0.3rem;"></div>
        
        <button class="btn btn-success" id="btn-apply-docx-songs" disabled>📥 Сохранить в базу (songs.csv)</button>
        
        <!-- Выгрузки -->
        <button class="btn btn-outline" id="btn-export-opensong-xml">XML OpenSong</button>
        <button class="btn btn-outline" id="btn-export-chordpro-txt">ChordPro (.cho)</button>
        <button class="btn btn-outline" id="btn-print-html-pdf">🖨️ Печать / PDF</button>
        <button class="btn btn-outline" id="btn-export-song-docx">📄 Экспорт DOCX</button>
        <button class="btn btn-outline" id="btn-export-all-zip" title="Скачать все распознанные песни в одном ZIP-архиве">📦 Скачать ZIP всех песен</button>
      </div>

      <!-- Список извлеченных песен из сборника (для быстрого переключения) -->
      <div id="docx-parsed-songs-container" style="display: none; margin-bottom: 1rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem;">
          <strong style="font-size: 0.88rem;">Распознанные песни сборника (<span id="parsed-songs-count">0</span>):</strong>
          <span style="font-size: 0.8rem; color: var(--muted);">Кликните на песню для перехода в визуальный редактор</span>
        </div>
        <div class="song-list-scroll" id="parsed-songs-list"></div>
      </div>
    </div>

    <!-- ВИЗУАЛЬНЫЙ РЕДАКТОР И LIVE-ПРЕДПРОСМОТР -->
    <div class="editor-layout">
      <!-- Левая колонка: DOM Редактор со снапами -->
      <div class="card" style="margin-bottom: 0;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.6rem;">
          <h3>🎨 Интерактивный редактор аккордов</h3>
          <div style="font-size: 0.78rem; color: var(--muted);">
            💡 Двигайте аккорды мышью над слогами • Клик по аккорду для правки
          </div>
        </div>

        <div class="chord-editor-container" id="interactive-editor">
          <div style="text-align: center; color: var(--muted); padding: 3rem 1rem;">
            Загрузите .docx сборник или вставьте текст песни, чтобы открыть интерактивный редактор с магнитными слогами.
          </div>
        </div>
      </div>

      <!-- Правая колонка: Live Preview и Журнал -->
      <div class="card" style="margin-bottom: 0;">
        <div class="preview-tabs">
          <button class="preview-tab-btn active" data-ptab="preview-opensong">OpenSong XML</button>
          <button class="preview-tab-btn" data-ptab="preview-chordpro">ChordPro</button>
          <button class="preview-tab-btn" data-ptab="preview-plain">Чистый текст</button>
          <button class="preview-tab-btn" data-ptab="preview-log">Журнал парсинга</button>
        </div>

        <div id="ptab-preview-opensong" class="ptab-content">
          <div class="live-code-view" id="live-opensong-view">// Здесь генерируется OpenSong в реальном времени...</div>
        </div>
        <div id="ptab-preview-chordpro" class="ptab-content" style="display: none;">
          <div class="live-code-view" id="live-chordpro-view">// Здесь генерируется ChordPro в реальном времени...</div>
        </div>
        <div id="ptab-preview-plain" class="ptab-content" style="display: none;">
          <div class="live-code-view" id="live-plain-view">// Чистый текст без аккордов...</div>
        </div>
        <div id="ptab-preview-log" class="ptab-content" style="display: none;">
          <div class="live-code-view" id="docx-log" style="color: #38bdf8;">[Ожидание выбора файла DOCX или вставки песни...]</div>
        </div>
      </div>
    </div>
  """

content = content[:m1] + new_tab_html + content[section_end:]

with open('data/admin.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("Tab markup successfully patched in admin.html!")
