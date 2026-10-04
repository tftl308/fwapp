import json, os, hashlib

def create_bundle():
    bundle = {}
    files = {
        'manifest': 'data/manifest.json',
        'songs': 'data/songs.csv',
        'tags': 'data/tags.csv',
        'songTags': 'data/song_tags.csv',
        'audio': 'data/audio.csv',
        'playlists': 'data/playlists.csv',
        'playlistItems': 'data/playlist_items.csv',
        'userNotes': 'data/user_notes.csv'
    }

    for key, rel_path in files.items():
        if os.path.exists(rel_path):
            with open(rel_path, 'r', encoding='utf-8') as f:
                bundle[key] = f.read()
        else:
            bundle[key] = ''

    # Save to demo_bundle.json
    with open('data/demo_bundle.json', 'w', encoding='utf-8') as f:
        json.dump(bundle, f, ensure_ascii=False)

    print("Created data/demo_bundle.json successfully!")

create_bundle()
