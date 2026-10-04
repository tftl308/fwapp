# -*- coding: utf-8 -*-
with open('data/admin.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos_form = text.find('<form id="song-form">')
pos_form_end = text.find('</form>', pos_form) + 7
assert pos_form != -1 and pos_form_end != -1, "song-form not found"

new_modal_form = """<form id="song-form">
        <input type="hidden" id="edit-id">
        <div class="grid-2">
          <div class="form-group">
            <label>ID (4 цифры: 0042)</label>
            <input type="text" id="edit-num-id" class="form-control" required pattern="\\d{4}">
          </div>
          <div class="form-group">
            <label>Номер в сборнике (number)</label>
            <input type="text" id="edit-number" class="form-control" placeholder="42">
          </div>
        </div>

        <div class="grid-2">
          <div class="form-group">
            <label>Название песни (title)</label>
            <input type="text" id="edit-title" class="form-control" required>
          </div>
          <div class="form-group">
            <label>Автор (author)</label>
            <input type="text" id="edit-author" class="form-control" placeholder="Огненный ветер">
          </div>
        </div>

        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(110px, 1fr)); gap: 0.5rem;">
          <div class="form-group">
            <label>Тональность (key)</label>
            <input type="text" id="edit-key" class="form-control" placeholder="Am, C#m">
          </div>
          <div class="form-group">
            <label>Каподастр (capo)</label>
            <input type="text" id="edit-capo" class="form-control" placeholder="+2">
          </div>
          <div class="form-group">
            <label>Темп (tempo)</label>
            <input type="number" id="edit-tempo" class="form-control" placeholder="120">
          </div>
          <div class="form-group">
            <label>Размер (time_sig)</label>
            <input type="text" id="edit-time-sig" class="form-control" placeholder="4/4">
          </div>
          <div class="form-group">
            <label>Длительность (duration)</label>
            <input type="text" id="edit-duration" class="form-control" placeholder="04:20">
          </div>
          <div class="form-group">
            <label>Предзадержка (predelay)</label>
            <input type="text" id="edit-predelay" class="form-control" placeholder="2s">
          </div>
        </div>

        <div class="grid-2">
          <div class="form-group">
            <label>Тематика (theme)</label>
            <input type="text" id="edit-theme" class="form-control" placeholder="Поклонение, Призыв">
          </div>
          <div class="form-group">
            <label>Доп. тема (alttheme)</label>
            <input type="text" id="edit-alttheme" class="form-control" placeholder="Пасха, Рождество">
          </div>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 0.5rem;">
          <div class="form-group">
            <label>Пользовательское 1 (user1)</label>
            <input type="text" id="edit-user1" class="form-control" placeholder="Метка / Группа 1">
          </div>
          <div class="form-group">
            <label>Пользовательское 2 (user2)</label>
            <input type="text" id="edit-user2" class="form-control" placeholder="Метка / Группа 2">
          </div>
          <div class="form-group">
            <label>Пользовательское 3 (user3)</label>
            <input type="text" id="edit-user3" class="form-control" placeholder="Метка / Группа 3">
          </div>
        </div>

        <div class="grid-2">
          <div class="form-group">
            <label>Ссылка на аудио (link_audio)</label>
            <input type="text" id="edit-link-audio" class="form-control" placeholder="https://... или audio.mp3">
          </div>
          <div class="form-group">
            <label>Ссылка YouTube (link_youtube)</label>
            <input type="text" id="edit-link-youtube" class="form-control" placeholder="https://youtube.com/watch?v=...">
          </div>
        </div>

        <div class="form-group">
          <label>Особые аккорды (custom_chords)</label>
          <input type="text" id="edit-custom-chords" class="form-control" placeholder="Am7b5:x02013, D7sus4:xx0213">
        </div>

        <div class="form-group">
          <label>Текст с аккордами (chordpro: [Am]Белый снег)</label>
          <textarea id="edit-body" class="form-control" style="height: 160px; font-family: monospace;"></textarea>
        </div>

        <div class="form-group">
          <label>Чистый текст для поиска/чтения (lyrics)</label>
          <textarea id="edit-lyrics" class="form-control" style="height: 90px;"></textarea>
        </div>

        <div class="form-group">
          <label>Заметки и инструкции (notes)</label>
          <input type="text" id="edit-notes" class="form-control" placeholder="[leader] Вступление с припева...">
        </div>

        <div style="display: flex; justify-content: flex-end; gap: 0.5rem; margin-top: 1rem;">
          <button type="button" class="btn btn-outline" id="btn-close-modal">Отмена</button>
          <button type="submit" class="btn btn-success">Сохранить изменения</button>
        </div>
      </form>"""

text = text[:pos_form] + new_modal_form + text[pos_form_end:]

# 2. Update openEditModal and submit handlers
pos_fn = text.find('function openEditModal(songId) {')
pos_fn_end = text.find('}', text.find('modal-song-edit', pos_fn)) + 1

new_open_modal = """function openEditModal(songId) {
      const song = dbSongs.find(s => s.id === songId);
      if (!song) return;

      document.getElementById('modal-title').textContent = 'Редактирование: ' + song.title;
      document.getElementById('edit-id').value = song.id;
      document.getElementById('edit-num-id').value = String(song.id || '').padStart(4, '0');
      document.getElementById('edit-number').value = song.number || '';
      document.getElementById('edit-title').value = song.title || '';
      document.getElementById('edit-author').value = song.author || '';
      document.getElementById('edit-key').value = song.key || song.key_default || '';
      document.getElementById('edit-capo').value = song.capo || '';
      document.getElementById('edit-tempo').value = song.tempo || '';
      document.getElementById('edit-time-sig').value = song.time_signature || '';
      document.getElementById('edit-duration').value = song.duration || '';
      document.getElementById('edit-predelay').value = song.predelay || '';
      document.getElementById('edit-theme').value = song.theme || song.alt_title || '';
      document.getElementById('edit-alttheme').value = song.alttheme || '';
      document.getElementById('edit-user1').value = song.user1 || '';
      document.getElementById('edit-user2').value = song.user2 || '';
      document.getElementById('edit-user3').value = song.user3 || '';
      document.getElementById('edit-link-audio').value = song.link_audio || '';
      document.getElementById('edit-link-youtube').value = song.link_youtube || '';
      document.getElementById('edit-custom-chords').value = song.custom_chords || '';
      document.getElementById('edit-body').value = song.chordpro || song.body_chordpro || '';
      document.getElementById('edit-lyrics').value = song.lyrics || song.body_plain || '';
      document.getElementById('edit-notes').value = song.notes || '';

      document.getElementById('modal-song-edit').style.display = 'flex';
    }"""

text = text[:pos_fn] + new_open_modal + text[pos_fn_end:]

# 3. Update song-form submit
pos_sub = text.find("document.getElementById('song-form').addEventListener('submit'")
pos_sub_end = text.find('});', pos_sub) + 3

new_submit = """document.getElementById('song-form').addEventListener('submit', (e) => {
      e.preventDefault();
      const origId = document.getElementById('edit-id').value;
      const numId = document.getElementById('edit-num-id').value;

      let idx = dbSongs.findIndex(s => s.id === origId);
      let targetSong = idx !== -1 ? dbSongs[idx] : {};

      targetSong.id = String(numId).padStart(4, '0');
      targetSong.number = document.getElementById('edit-number').value || parseInt(numId, 10) || '1';
      targetSong.title = document.getElementById('edit-title').value;
      targetSong.author = document.getElementById('edit-author').value;
      targetSong.key = document.getElementById('edit-key').value;
      targetSong.key_default = targetSong.key;
      targetSong.capo = document.getElementById('edit-capo').value;
      targetSong.tempo = document.getElementById('edit-tempo').value;
      targetSong.time_signature = document.getElementById('edit-time-sig').value;
      targetSong.duration = document.getElementById('edit-duration').value;
      targetSong.predelay = document.getElementById('edit-predelay').value;
      targetSong.theme = document.getElementById('edit-theme').value;
      targetSong.alttheme = document.getElementById('edit-alttheme').value;
      targetSong.user1 = document.getElementById('edit-user1').value;
      targetSong.user2 = document.getElementById('edit-user2').value;
      targetSong.user3 = document.getElementById('edit-user3').value;
      targetSong.link_audio = document.getElementById('edit-link-audio').value;
      targetSong.link_youtube = document.getElementById('edit-link-youtube').value;
      targetSong.custom_chords = document.getElementById('edit-custom-chords').value;
      targetSong.chordpro = document.getElementById('edit-body').value;
      targetSong.body_chordpro = targetSong.chordpro;
      targetSong.lyrics = document.getElementById('edit-lyrics').value || targetSong.chordpro.replace(/\\[.*?\\]/g, '').replace(/\\s+/g, ' ').trim();
      targetSong.body_plain = targetSong.lyrics;
      targetSong.notes = document.getElementById('edit-notes').value;

      if (idx === -1) {
        dbSongs.push(targetSong);
      }

      saveDb();
      renderCatalog();
      document.getElementById('modal-song-edit').style.display = 'none';
      alert('Песня успешно обновлена со всеми 22 полями базы!');
    });"""

text = text[:pos_sub] + new_submit + text[pos_sub_end:]

with open('data/admin.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("data/admin.html successfully patched with all 22 fields modal form!")
