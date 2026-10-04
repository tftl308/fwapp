# -*- coding: utf-8 -*-
with open('data/admin.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace any raw literal '<script>' or '</script>' inside string constants
old_snippet = """        } else {
          // Если это шаблон index.html, внедряем перед первым <script>
          const scriptTag = '<script>';
          const inlinedBlock = '<script>\\nconst INLINED_SONGS_CSV_DATA = ' + JSON.stringify(currentCsv) + ';\\n';
          templateHtml = templateHtml.replace(scriptTag, inlinedBlock);
        }"""

new_snippet = """        } else {
          // Если это шаблон index.html, внедряем перед первым script
          const scriptTag = '<' + 'script>';
          const inlinedBlock = '<' + 'script>\\nconst INLINED_SONGS_CSV_DATA = ' + JSON.stringify(currentCsv) + ';\\n';
          templateHtml = templateHtml.replace(scriptTag, inlinedBlock);
        }"""

assert old_snippet in text, "old_snippet not found"
text = text.replace(old_snippet, new_snippet)

with open('data/admin.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("Escaped raw script tags inside strings in data/admin.html!")
