# -*- coding: utf-8 -*-
with open('tools/build-index.mjs', 'r', encoding='utf-8') as f:
    text = f.read()

target = "fs.writeFileSync('огненныйветер.html', htmlContent, 'utf8');"
replacement = "// огненныйветер.html собирается отдельно как Light Reader SPA со вшитым songs.csv"

if target in text:
    text = text.replace(target, replacement)
    with open('tools/build-index.mjs', 'w', encoding='utf-8') as f:
        f.write(text)
    print('Successfully unhooked огненныйветер.html overwrite in build-index.mjs!')
else:
    print('Target not found in build-index.mjs')
