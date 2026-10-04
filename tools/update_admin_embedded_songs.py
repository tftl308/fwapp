# -*- coding: utf-8 -*-
import json

with open('data/songs.csv', 'r', encoding='utf-8') as f:
    songs_csv = f.read()

# Parse songs_csv into objects
lines = songs_csv.strip().split('\n')
headers = [h.strip() for h in lines[0].split(';')]

def parse_row(line):
    row = []
    cur = ''
    in_quotes = False
    for i, ch in enumerate(line):
        if ch == '"':
            if in_quotes and i + 1 < len(line) and line[i+1] == '"':
                cur += '"'
            else:
                in_quotes = not in_quotes
        elif ch == ';' and not in_quotes:
            row.append(cur)
            cur = ''
        else:
            cur += ch
    row.append(cur)
    return row

records = []
current_line_acc = ''
inside_multiline = False

for line in lines[1:]:
    if inside_multiline:
        current_line_acc += '\n' + line
        if current_line_acc.count('"') % 2 == 0:
            inside_multiline = False
            vals = parse_row(current_line_acc)
            current_line_acc = ''
            rec = {headers[i]: vals[i] if i < len(vals) else '' for i in range(len(headers))}
            records.append(rec)
    else:
        if line.count('"') % 2 != 0:
            inside_multiline = True
            current_line_acc = line
        else:
            vals = parse_row(line)
            rec = {headers[i]: vals[i] if i < len(vals) else '' for i in range(len(headers))}
            records.append(rec)

print(f"Parsed {len(records)} songs from data/songs.csv")

with open('data/admin.html', 'r', encoding='utf-8') as f:
    admin_html = f.read()

# Replace dbSongs initial array: let dbSongs = [...]
start_tag = 'let dbSongs = '
pos = admin_html.find(start_tag)
assert pos != -1
pos_arr_start = pos + len(start_tag)
# Find closing ';'
pos_arr_end = admin_html.find(';\n', pos_arr_start)
assert pos_arr_end != -1

admin_html = admin_html[:pos_arr_start] + json.dumps(records, ensure_ascii=False) + admin_html[pos_arr_end:]

with open('data/admin.html', 'w', encoding='utf-8') as f:
    f.write(admin_html)

print("data/admin.html updated with full 700 canonical songs directly in dbSongs!")
