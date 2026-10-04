# -*- coding: utf-8 -*-
with open('tools/b64_reader_template.txt', 'r', encoding='ascii') as f:
    b64_new = f.read().strip()

with open('data/admin.html', 'r', encoding='utf-8') as f:
    text = f.read()

marker = 'const LIGHT_READER_BASE64_TEMPLATE = "'
pos = text.find(marker)
assert pos != -1
pos_end = text.find('";', pos)
assert pos_end != -1

text = text[:pos + len(marker)] + b64_new + text[pos_end:]

with open('data/admin.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("data/admin.html updated with freshest clean template in Base64!")
