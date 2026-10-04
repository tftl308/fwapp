import re

with open('tools/build-index.mjs', 'r', encoding='utf-8') as f:
    code = f.read()

with open('tools/qrcode.min.js', 'r', encoding='utf-8') as f:
    qrcode_min_js = f.read()

# =========================================================================
# 1. EMBED PRODUCTION QRCODE LIBRARY (qrcode-generator MIT)
# =========================================================================
# Replace previous naive QrCodeHelper with production-grade QR Code generator
old_qr_helper = """// ==========================================
// 5.5. OFFLINE QR CODE GENERATOR (Pure SVG)
// ==========================================
class QrCodeHelper {
  static generateSvg(text, size = 220) {
"""

idx_qr_helper = code.find("// ==========================================\n// 5.5. OFFLINE QR CODE GENERATOR")
idx_audio_player_hdr = code.find("// ==========================================\n// 6. AUDIO PLAYER SERVICE")
assert idx_qr_helper != -1 and idx_audio_player_hdr != -1, "QR code helper location not found"

new_qr_section = f"""// ==========================================
// 5.5. OFFLINE QR CODE ENGINE (Standard Matrix Generator)
// ==========================================
{qrcode_min_js}

class QrCodeHelper {{
  static generateSvg(text, size = 220) {{
    try {{
      const qr = qrcode(0, 'M');
      qr.addData(text);
      qr.make();
      // createSvgTag(cellSize, margin)
      return qr.createSvgTag(6, 4);
    }} catch (e) {{
      console.error('QR generation error:', e);
      return '<div class="text-sm text-muted">Не удалось сгенерировать QR-код</div>';
    }}
  }}
}}
"""

code = code[:idx_qr_helper] + new_qr_section + "\n" + code[idx_audio_player_hdr:]
print("Production QR Code Engine embedded successfully")

# =========================================================================
# 2. RENAMINGS: "Сетлист" -> "Список", "Текущий выбор (Temp)" -> "Подбор"
# =========================================================================
code = code.replace("title: 'Текущий выбор (Temp)'", "title: 'Подбор'")
code = code.replace("title: 'Текущий список (Temp)'", "title: 'Подбор'")
code = code.replace("pageTitle.textContent = 'Песни и Сетлист';", "pageTitle.textContent = 'Песни и Список';")
code = code.replace("['Сетлист: ' + curPlaylist.title", "['Список: ' + curPlaylist.title")
code = code.replace("'Пользовательский сетлист'", "'Пользовательский список'")

# "Текущая очередь треков" -> "Играет сейчас"
code = code.replace("['Текущая очередь треков']", "['Играет сейчас']")
print("Text labels updated: Сетлист -> Список, Temp -> Подбор, Очередь -> Играет сейчас")

# =========================================================================
# 3. CSS: CONDENSED FONT RESEARCH & LINE-HEIGHT REDUCTION (~30%)
# =========================================================================
# Replace font declarations with modern system condensed font stack
old_font_system = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;'
new_font_condensed = '-apple-system, BlinkMacSystemFont, "Roboto Condensed", "Arial Narrow", "Segoe UI Condensed", "Noto Sans Condensed", sans-serif;'

code = code.replace(old_font_system, new_font_condensed)

# Reduce line-height and margin-bottom of lyrics lines by ~30%
# Old: margin-bottom: 0.85rem; line-height: 1.25;
# New: margin-bottom: 0.45rem; line-height: 1.05;
code = code.replace("margin-bottom: 0.85rem;\n      line-height: 1.25;", "margin-bottom: 0.45rem;\n      line-height: 1.05;")
code = code.replace("min-height: 1.25em;\n      line-height: 1.25;", "min-height: 1.1em;\n      line-height: 1.05;")
code = code.replace("margin-top: 1.1rem;\n      margin-bottom: 0.4rem;", "margin-top: 0.6rem;\n      margin-bottom: 0.2rem;")
code = code.replace(".lyrics-render-line.empty-line {\n      height: 1.2rem;", ".lyrics-render-line.empty-line {\n      height: 0.65rem;")
print("Typography updated: condensed font stack and 30% reduced line-height applied")

# =========================================================================
# 4. AUDIO PLAYER: SHUFFLE, REPEAT/ORDER, VOLUME
# =========================================================================
# Update AudioPlayerService constructor & methods
idx_audio_ctor = code.find("class AudioPlayerService {")
idx_setup_listeners = code.find("setupListeners() {", idx_audio_ctor)
assert idx_audio_ctor != -1 and idx_setup_listeners != -1, "AudioPlayerService ctor not found"

new_audio_ctor = """class AudioPlayerService {
  constructor() {
    this.audioElement = new Audio();
    this.currentTrack = null;
    this.playlistQueue = [];
    this.currentIndex = -1;
    this.isShuffle = false;
    this.volume = 1.0;
    this.audioElement.volume = this.volume;
    this.setupListeners();
  }
"""
code = code[:idx_audio_ctor] + new_audio_ctor + "\n  " + code[idx_setup_listeners:]

# Update AudioPlayerService playNext / playPrev for shuffle and volume
old_play_next = """  playNext() {
    if (this.playlistQueue.length > 0 && this.currentIndex < this.playlistQueue.length - 1) {
      this.currentIndex++;
      this.playIsolatedTrack(this.playlistQueue[this.currentIndex]);
    }
  }"""

new_play_next = """  setVolume(val) {
    this.volume = Math.max(0, Math.min(1, val));
    this.audioElement.volume = this.volume;
  }

  toggleShuffle() {
    this.isShuffle = !this.isShuffle;
    AppController.showToast(this.isShuffle ? 'Случайный порядок включен' : 'Порядок по списку');
  }

  playNext() {
    if (!this.playlistQueue || this.playlistQueue.length === 0) return;
    if (this.isShuffle) {
      const nextIdx = Math.floor(Math.random() * this.playlistQueue.length);
      this.currentIndex = nextIdx;
      this.playIsolatedTrack(this.playlistQueue[nextIdx]);
    } else if (this.currentIndex < this.playlistQueue.length - 1) {
      this.currentIndex++;
      this.playIsolatedTrack(this.playlistQueue[this.currentIndex]);
    }
  }"""

assert old_play_next in code, "old_play_next not found"
code = code.replace(old_play_next, new_play_next)
print("AudioPlayerService shuffle and volume logic integrated")

with open('tools/build-index.mjs', 'w', encoding='utf-8') as f:
    f.write(code)
print("Part 1 of update saved to build-index.mjs")
