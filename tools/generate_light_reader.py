# -*- coding: utf-8 -*-
import re

with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Modify title
text = text.replace('<title>Огненный Ветер</title>', '<title>Огненный Ветер — Карманный Песенник</title>')

# 2. Hide audio player tab button and docked mini-player in light reader mode
# Replace nav item for player
text = text.replace(
    '<button class="bottom-nav-btn" data-action="nav-tab" data-tab="player" aria-label="Плеер">',
    '<button class="bottom-nav-btn" data-action="nav-tab" data-tab="player" aria-label="Плеер" style="display: none !important;">'
)

# 3. Add light reader badge in header
header_badge = """      <div class="app-header-left flex items-center gap-2">
        <img src="data/image-3.png" alt="Огненный Ветер" class="app-header-logo" onerror="this.style.display='none'">
        <div class="app-header-title-block">
          <span class="app-header-title">Огненный Ветер</span>
          <span class="badge" style="font-size: 0.68rem; padding: 1px 6px; background: rgba(180,83,9,0.12); color: var(--accent); font-weight: 700;">Портативный Сборник</span>
        </div>
      </div>"""

# Replace logo header block if matched
pos_hdr = text.find('<span class="app-header-title">Огненный Ветер</span>')
if pos_hdr != -1:
    block_start = text.rfind('<div class="app-header-left', 0, pos_hdr)
    block_end = text.find('</div>', text.find('</div>', pos_hdr) + 1) + 6
    text = text[:block_start] + header_badge + text[block_end:]

# 4. Hide audio hub in song details
text = text.replace(
    "className: 'song-audio-bottom-hub'",
    "className: 'song-audio-bottom-hub', style: 'display: none !important;'"
)

# 5. Hide media sync button in light reader mode
text = text.replace(
    'data-action="trigger-audio-batch-upload"',
    'data-action="trigger-audio-batch-upload" style="display: none !important;"'
)

with open('dist/reader/index.html', 'w', encoding='utf-8') as f:
    f.write(text)

print('dist/reader/index.html successfully generated!')
