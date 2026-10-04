# -*- coding: utf-8 -*-
import gzip
import base64

with open('огненныйветер.html', 'r', encoding='utf-8') as f:
    text = f.read()

marker = 'const INLINED_SONGS_CSV_DATA = '
pos = text.find(marker)
assert pos != -1
after_pos = text.find(';\n\nfunction parseInlinedSongsCsv', pos)
assert after_pos != -1

# Replace raw CSV data with distinct marker token __CSV_DATA_JSON__
template_shell = text[:pos] + 'const INLINED_SONGS_CSV_DATA = __CSV_DATA_JSON__;' + text[after_pos+1:]

# Compress with gzip to make it super compact
compressed = gzip.compress(template_shell.encode('utf-8'), compresslevel=9)
b64 = base64.b64encode(compressed).decode('ascii')

print(f"Template shell length: {len(template_shell)} bytes")
print(f"Compressed Base64 length: {len(b64)} chars")

with open('tools/template_shell.b64', 'w', encoding='ascii') as f:
    f.write(b64)
