# -*- coding: utf-8 -*-
with open('data/admin.html', 'r', encoding='utf-8') as f:
    text = f.read()

old_sec = """        // Section header in OpenSong format: [V1], [C], [B] or russian section
        if (/^\\[(v\\d*|c\\d*|b\\d*|t|e|intro|outro|куплет|припев|бридж|вступление|проигрыш)/i.test(trimmed)) {
          const kind = /припев|c/i.test(trimmed) ? 'chorus-header' : 'section-header';
          model.lines.push({ kind: kind, lyric: trimmed, chords: [] });
          continue;
        }"""

new_sec = """        // Section header in OpenSong format: [V1], [C], [B] strictly on its own: ^\\[(V\\d*|C\\d*|B\\d*|T|E|Intro|Outro|Куплет.*|Припев.*|Бридж.*)\\]$
        if (/^\\[(v\\d*|c\\d*|b\\d*|t|e|intro|outro|куплет[^\\]]*|припев[^\\]]*|бридж[^\\]]*|вступление[^\\]]*)\\]$/i.test(trimmed)) {
          const kind = /припев|c/i.test(trimmed) ? 'chorus-header' : 'section-header';
          model.lines.push({ kind: kind, lyric: trimmed, chords: [] });
          continue;
        }"""

assert old_sec in text, "old_sec not found"
text = text.replace(old_sec, new_sec)

with open('data/admin.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("Section regex fixed!")
