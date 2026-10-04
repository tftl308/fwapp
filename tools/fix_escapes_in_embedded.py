# -*- coding: utf-8 -*-
with open('data/admin.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace any literal <script> and </script> inside the embedded constants
pos1 = text.find('const LIGHT_READER_TEMPLATE_PART1 = ')
pos2 = text.find('const LIGHT_READER_TEMPLATE_PART2 = ')
pos3 = text.find('function compileStandaloneLightReaderFromAdmin()')

embedded_chunk = text[pos1:pos3]

# In HTML script tag, any occurrence of literal '</script' or '<script' triggers the HTML parser!
# Even inside string literals: '...<script>...' or '...</script>...'
# We must replace them with '<\\/script>' or '<\\/script'
fixed_chunk = embedded_chunk.replace('<script>', '<\\/script>').replace('</script>', '<\\/script>')
# More strictly: replace '<script' with '<\\/script'
fixed_chunk = fixed_chunk.replace('<script', '<\\/script')

text = text[:pos1] + fixed_chunk + text[pos3:]

with open('data/admin.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("Protected all script tags inside embedded literals!")
