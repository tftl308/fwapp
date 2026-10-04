# -*- coding: utf-8 -*-
with open('data/admin.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace print document.write with clean iframe printing
old_print_block = """    // 3. Print / Generate PDF (via browser print preview)
    document.getElementById('btn-print-html-pdf')?.addEventListener('click', () => {
      if (!activeSongModel) { alert('Сначала загрузите или выберите песню.'); return; }
      const osLyrics = serializeSongToOpenSongLyrics(activeSongModel);

      const printWin = window.open('', '_blank');
      printWin.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="utf-8">
          <title>${activeSongModel.title} — Огненный ветер</title>
          <style>
            @page { size: A4; margin: 15mm; }
            body { font-family: "Times New Roman", Times, serif; font-size: 14pt; line-height: 1.4; color: #000; margin: 0; padding: 15mm; }
            h1 { text-align: center; font-size: 20pt; margin-bottom: 4px; text-transform: uppercase; }
            .meta { text-align: center; font-size: 11pt; color: #555; margin-bottom: 20px; }
            pre { font-family: "Times New Roman", Times, serif; font-size: 13pt; line-height: 1.35; white-space: pre-wrap; word-wrap: break-word; }
            .chord-line { font-weight: bold; color: #111; }
          </style>
        </head>
        <body>
          <h1>${activeSongModel.title}</h1>
          <div class="meta">
            ${activeSongModel.key_default ? 'Тональность: <b>' + activeSongModel.key_default + '</b>' : ''}
            ${activeSongModel.capo ? ' | Капо: <b>' + activeSongModel.capo + '</b>' : ''}
            ${activeSongModel.tempo ? ' | Темп: <b>' + activeSongModel.tempo + '</b>' : ''}
          </div>
          <pre>${osLyrics.split('\\n').map(l => l.startsWith('.') ? `<span class="chord-line">${l.substring(1)}</span>` : l).join('\\n')}</pre>
          <img src="x" onerror="window.print()" style="display:none;" />
        </body>
        </html>
      `);
      printWin.document.close();
    });"""

new_print_block = """    // 3. Print / Generate PDF (clean isolated iframe print)
    document.getElementById('btn-print-html-pdf')?.addEventListener('click', () => {
      if (!activeSongModel) { alert('Сначала загрузите или выберите песню.'); return; }
      const osLyrics = serializeSongToOpenSongLyrics(activeSongModel);
      
      const iframe = document.createElement('iframe');
      iframe.style.position = 'fixed';
      iframe.style.right = '0';
      iframe.style.bottom = '0';
      iframe.style.width = '0';
      iframe.style.height = '0';
      iframe.style.border = '0';
      document.body.appendChild(iframe);

      const doc = iframe.contentWindow.document;
      const keyStr = activeSongModel.key_default ? 'Тональность: <b>' + activeSongModel.key_default + '</b>' : '';
      const capoStr = activeSongModel.capo ? ' | Капо: <b>' + activeSongModel.capo + '</b>' : '';
      const tempoStr = activeSongModel.tempo ? ' | Темп: <b>' + activeSongModel.tempo + '</b>' : '';
      const renderedLyrics = osLyrics.split('\\n').map(l => l.startsWith('.') ? '<span class=\"chord-line\">' + l.substring(1) + '</span>' : l).join('\\n');

      doc.open();
      doc.write(
        '<!DOCTYPE html><html><head><meta charset=\"utf-8\"><title>' + (activeSongModel.title || 'Песня') + '</title>' +
        '<style>@page{size:A4;margin:15mm;}body{font-family:\"Times New Roman\",Times,serif;font-size:14pt;line-height:1.4;color:#000;padding:15mm;}h1{text-align:center;font-size:20pt;margin-bottom:4px;text-transform:uppercase;}.meta{text-align:center;font-size:11pt;color:#555;margin-bottom:20px;}pre{font-family:\"Times New Roman\",Times,serif;font-size:13pt;line-height:1.35;white-space:pre-wrap;word-wrap:break-word;}.chord-line{font-weight:bold;color:#111;}</style>' +
        '</head><body>' +
        '<h1>' + (activeSongModel.title || '') + '</h1>' +
        '<div class=\"meta\">' + keyStr + capoStr + tempoStr + '</div>' +
        '<pre>' + renderedLyrics + '</pre>' +
        '</body></html>'
      );
      doc.close();

      setTimeout(() => {
        iframe.contentWindow.focus();
        iframe.contentWindow.print();
        setTimeout(() => document.body.removeChild(iframe), 2000);
      }, 300);
    });"""

assert old_print_block in text, "old_print_block not found in admin.html"
text = text.replace(old_print_block, new_print_block)

with open('data/admin.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("Admin HTML printing safely refactored to iframe without nested HTML tags!")
