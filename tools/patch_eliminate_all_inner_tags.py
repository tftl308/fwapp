# -*- coding: utf-8 -*-
with open('data/admin.html', 'r', encoding='utf-8') as f:
    text = f.read()

old_code = """      doc.open();
      doc.write(
        '<!DOCTYPE html><html><head><meta charset="utf-8"><title>' + (activeSongModel.title || 'Песня') + '</title>' +
        '<style>@page{size:A4;margin:15mm;}body{font-family:"Times New Roman",Times,serif;font-size:14pt;line-height:1.4;color:#000;padding:15mm;}h1{text-align:center;font-size:20pt;margin-bottom:4px;text-transform:uppercase;}.meta{text-align:center;font-size:11pt;color:#555;margin-bottom:20px;}pre{font-family:"Times New Roman",Times,serif;font-size:13pt;line-height:1.35;white-space:pre-wrap;word-wrap:break-word;}.chord-line{font-weight:bold;color:#111;}</style>' +
        '</head><body>' +
        '<h1>' + (activeSongModel.title || '') + '</h1>' +
        '<div class="meta">' + keyStr + capoStr + tempoStr + '</div>' +
        '<pre>' + renderedLyrics + '</pre>' +
        '</body></html>'
      );
      doc.close();"""

new_code = """      doc.open();
      doc.write(
        '<' + '!DOCTYPE html><' + 'html><' + 'head><meta charset=\"utf-8\"><title>' + (activeSongModel.title || 'Песня') + '</title>' +
        '<' + 'style>@page{size:A4;margin:15mm;}body{font-family:\"Times New Roman\",Times,serif;font-size:14pt;line-height:1.4;color:#000;padding:15mm;}h1{text-align:center;font-size:20pt;margin-bottom:4px;text-transform:uppercase;}.meta{text-align:center;font-size:11pt;color:#555;margin-bottom:20px;}pre{font-family:\"Times New Roman\",Times,serif;font-size:13pt;line-height:1.35;white-space:pre-wrap;word-wrap:break-word;}.chord-line{font-weight:bold;color:#111;}<' + '/style>' +
        '<' + '/head><' + 'body>' +
        '<h1>' + (activeSongModel.title || '') + '</h1>' +
        '<div class=\"meta\">' + keyStr + capoStr + tempoStr + '</div>' +
        '<pre>' + renderedLyrics + '</pre>' +
        '<' + '/body><' + '/html>'
      );
      doc.close();"""

assert old_code in text, "old_code not found in admin.html"
text = text.replace(old_code, new_code)

with open('data/admin.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("Inner tags completely shielded from HTML parsers!")
