# -*- coding: utf-8 -*-
import json

with open('data/songs.csv', 'r', encoding='utf-8') as f:
    songs_csv = f.read()

with open('data/admin.html', 'r', encoding='utf-8') as f:
    admin_html = f.read()

# Replace songs embedded in EMBEDDED_TABLES_RAW
prefix = 'const EMBEDDED_TABLES_RAW = {'
pos = admin_html.find(prefix)
if pos != -1:
    pos_songs = admin_html.find('songs:', pos)
    if pos_songs != -1:
        # Find string start and end
        str_start = admin_html.find('"', pos_songs)
        # Find closing quote respecting escaping
        i = str_start + 1
        while i < len(admin_html):
            if admin_html[i] == '"' and admin_html[i-1] != '\\':
                break
            i += 1
        str_end = i
        
        # JSON serialize the new songs_csv
        new_songs_val = json.dumps(songs_csv)
        admin_html = admin_html[:str_start] + new_songs_val + admin_html[str_end+1:]
        
        with open('data/admin.html', 'w', encoding='utf-8') as f:
            f.write(admin_html)
        print('Successfully updated EMBEDDED_TABLES_RAW.songs in data/admin.html!')
    else:
        print('songs: not found in EMBEDDED_TABLES_RAW')
else:
    print('EMBEDDED_TABLES_RAW not found')
