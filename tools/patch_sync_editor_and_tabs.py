# -*- coding: utf-8 -*-
with open('data/admin.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update Preview column markup: make OpenSong & ChordPro views editable textareas
old_preview_col = """        <div id="ptab-preview-opensong" class="ptab-content">
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
        </div>"""

new_preview_col = """        <div id="ptab-preview-opensong" class="ptab-content">
          <div style="font-size:0.75rem; color:var(--muted); margin-bottom:0.3rem;">✏️ Редактируйте прямо здесь: перемещайте аккорды пробелами в строках с точкой (.) — левое окно обновится на лету!</div>
          <textarea class="live-code-view" id="live-opensong-view" spellcheck="false" style="width: 100%; min-height: 480px; resize: vertical; box-sizing: border-box; font-family: monospace; line-height: 1.35; padding: 0.75rem; border: 1px solid var(--border); border-radius: 6px; background: #0f172a; color: #f8fafc; font-size: 0.85rem;">// Здесь генерируется OpenSong в реальном времени...</textarea>
        </div>
        <div id="ptab-preview-chordpro" class="ptab-content" style="display: none;">
          <div style="font-size:0.75rem; color:var(--muted); margin-bottom:0.3rem;">✏️ Формат ChordPro: двигайте [Аккорды] в тексте — обе панели синхронизируются автоматически!</div>
          <textarea class="live-code-view" id="live-chordpro-view" spellcheck="false" style="width: 100%; min-height: 480px; resize: vertical; box-sizing: border-box; font-family: monospace; line-height: 1.35; padding: 0.75rem; border: 1px solid var(--border); border-radius: 6px; background: #0f172a; color: #f8fafc; font-size: 0.85rem;">// Здесь генерируется ChordPro в реальном времени...</textarea>
        </div>
        <div id="ptab-preview-plain" class="ptab-content" style="display: none;">
          <textarea class="live-code-view" id="live-plain-view" spellcheck="false" style="width: 100%; min-height: 480px; resize: vertical; box-sizing: border-box; font-family: monospace; line-height: 1.35; padding: 0.75rem; border: 1px solid var(--border); border-radius: 6px; background: #0f172a; color: #f8fafc; font-size: 0.85rem;">// Чистый текст без аккордов...</textarea>
        </div>
        <div id="ptab-preview-log" class="ptab-content" style="display: none;">
          <div class="live-code-view" id="docx-log" style="color: #38bdf8; min-height: 480px; max-height: 520px; overflow-y: auto;">[Ожидание выбора файла DOCX или вставки песни...]</div>
        </div>"""

assert old_preview_col in text, "old_preview_col not found in admin.html"
text = text.replace(old_preview_col, new_preview_col)

# 2. Update preview tab buttons to have type="button" and explicit inline onclick fallback
old_tabs_html = """        <div class="preview-tabs">
          <button class="preview-tab-btn active" data-ptab="preview-opensong">OpenSong XML</button>
          <button class="preview-tab-btn" data-ptab="preview-chordpro">ChordPro</button>
          <button class="preview-tab-btn" data-ptab="preview-plain">Чистый текст</button>
          <button class="preview-tab-btn" data-ptab="preview-log">Журнал парсинга</button>
        </div>"""

new_tabs_html = """        <div class="preview-tabs" id="main-preview-tabs-bar">
          <button type="button" class="preview-tab-btn active" data-ptab="ptab-preview-opensong">OpenSong XML</button>
          <button type="button" class="preview-tab-btn" data-ptab="ptab-preview-chordpro">ChordPro</button>
          <button type="button" class="preview-tab-btn" data-ptab="ptab-preview-plain">Чистый текст</button>
          <button type="button" class="preview-tab-btn" data-ptab="ptab-preview-log">Журнал парсинга</button>
        </div>"""

assert old_tabs_html in text, "old_tabs_html not found in admin.html"
text = text.replace(old_tabs_html, new_tabs_html)

with open('data/admin.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("Markup successfully updated for 2-way sync and tabs!")
