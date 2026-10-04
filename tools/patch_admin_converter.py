# -*- coding: utf-8 -*-
import sys
import re

print("Starting patch for data/admin.html...")

with open('data/admin.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update CSS
css_addition = """
    /* === MODERN DOCX/OPENSONG CONVERTER & DRAG-AND-DROP EDITOR STYLES === */
    .converter-toolbar {
      display: flex;
      gap: 0.5rem;
      align-items: center;
      flex-wrap: wrap;
      margin-bottom: 1rem;
      background: #f1f5f9;
      padding: 0.75rem;
      border-radius: 6px;
      border: 1px solid var(--border);
    }
    .converter-stat-badge {
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
      padding: 0.25rem 0.6rem;
      border-radius: 9999px;
      font-size: 0.8rem;
      font-weight: 600;
    }
    .badge-conf-green { background: #dcfce7; color: #15803d; border: 1px solid #86efac; }
    .badge-conf-yellow { background: #fef9c3; color: #a16207; border: 1px solid #fde047; }
    .badge-conf-red { background: #fee2e2; color: #b91c1c; border: 1px solid #fca5a5; }

    .editor-layout {
      display: grid;
      grid-template-columns: 1.2fr 1fr;
      gap: 1rem;
      margin-top: 1rem;
    }
    @media (max-width: 900px) {
      .editor-layout { grid-template-columns: 1fr; }
    }

    .song-list-scroll {
      max-height: 280px;
      overflow-y: auto;
      border: 1px solid var(--border);
      border-radius: 6px;
      background: #fff;
      margin-bottom: 1rem;
    }
    .song-list-item {
      padding: 0.5rem 0.75rem;
      border-bottom: 1px solid #f1f5f9;
      cursor: pointer;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 0.88rem;
    }
    .song-list-item:hover { background: #f8fafc; }
    .song-list-item.active { background: #e0f2fe; font-weight: bold; border-left: 4px solid var(--info); }

    /* Interactive DOM Editor */
    .chord-editor-container {
      background: #ffffff;
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 1.2rem;
      min-height: 380px;
      max-height: 580px;
      overflow-y: auto;
      font-family: 'Times New Roman', Times, serif;
      font-size: 16px;
      line-height: 1.5;
    }
    .editor-song-meta {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
      gap: 0.5rem;
      margin-bottom: 1rem;
      padding-bottom: 0.75rem;
      border-bottom: 1px dashed var(--border);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .editor-line-block {
      margin-bottom: 0.8rem;
      position: relative;
    }
    .editor-line-header {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      font-size: 0.72rem;
      font-weight: 600;
      color: var(--muted);
      text-transform: uppercase;
      margin-bottom: 0.15rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .editor-line-track {
      position: relative;
      background: #fafafa;
      border: 1px solid #e2e8f0;
      border-radius: 4px;
      padding: 1.8rem 0.6rem 0.4rem 0.6rem;
      min-height: 48px;
      user-select: none;
    }
    .editor-text-row {
      display: inline-block;
      white-space: pre;
      position: relative;
    }
    .char-cell {
      display: inline-block;
      position: relative;
      cursor: pointer;
    }
    .char-cell:hover {
      background: #e2e8f0;
      border-radius: 2px;
    }
    .char-cell.snap-target {
      background: #fed7aa;
      border-radius: 2px;
    }
    .chord-chip {
      position: absolute;
      top: 0.25rem;
      transform: translateX(-50%);
      background: #c2410c;
      color: #fff;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      font-size: 0.75rem;
      font-weight: bold;
      padding: 0.1rem 0.45rem;
      border-radius: 4px;
      cursor: grab;
      box-shadow: 0 1px 3px rgba(0,0,0,0.18);
      z-index: 5;
      display: inline-flex;
      align-items: center;
      gap: 0.25rem;
      transition: background 0.15s, transform 0.05s;
    }
    .chord-chip:active { cursor: grabbing; transform: translateX(-50%) scale(1.05); }
    .chord-chip.conf-high { background: #15803d; }
    .chord-chip.conf-med { background: #b45309; }
    .chord-chip.conf-low { background: #b91c1c; }
    .chord-chip.selected { outline: 2px solid #0284c7; outline-offset: 1px; }

    .chord-chip .btn-chip-del {
      cursor: pointer;
      font-size: 0.7rem;
      opacity: 0.7;
      margin-left: 2px;
    }
    .chord-chip .btn-chip-del:hover { opacity: 1; }

    /* Live Preview Tabs */
    .preview-tabs {
      display: flex;
      gap: 0.25rem;
      border-bottom: 1px solid var(--border);
      margin-bottom: 0.5rem;
    }
    .preview-tab-btn {
      padding: 0.4rem 0.8rem;
      background: none;
      border: 1px solid transparent;
      border-bottom: none;
      cursor: pointer;
      font-size: 0.82rem;
      border-radius: 4px 4px 0 0;
    }
    .preview-tab-btn.active {
      background: #fff;
      border-color: var(--border);
      font-weight: bold;
      color: var(--accent);
    }
    .live-code-view {
      font-family: monospace;
      font-size: 0.82rem;
      white-space: pre-wrap;
      word-break: break-all;
      background: #0f172a;
      color: #f8fafc;
      padding: 1rem;
      border-radius: 6px;
      max-height: 520px;
      overflow-y: auto;
    }
"""

if '/* === MODERN DOCX/OPENSONG CONVERTER' not in content:
    content = content.replace('</style>', css_addition + '\n</style>', 1)
    print("CSS updated!")

with open('data/admin.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("Admin HTML style successfully patched.")
