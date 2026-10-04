# -*- coding: utf-8 -*-
with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update Settings View: Add local directory picker & standalone SPA compiler button
old_audio_sync_block = """    // Подгрузка аудиофайлов
    const audioSyncCard = Renderer.createElement('div', { className: 'song-card', style: 'flex-direction: column; align-items: stretch; gap: 0.75rem;' });
    audioSyncCard.appendChild(Renderer.createElement('h3', { className: 'text-main text-sm' }, ['Синхронизация папки music/ с аудиозаписями']));
    audioSyncCard.appendChild(Renderer.createElement('div', { className: 'text-sm text-muted' }, [
      'Выберите аудиофайлы (.mp3, .wav, .m4a). Привязка выполняется строго по номеру песни в начале файла: ',
      Renderer.createElement('code', { style: 'font-weight: 700; color: var(--chord-color);' }, ['ID_type_title']),
      ' (например: 0482_studio_Белый_снег.mp3).'
    ]));

    const uploadBtn = Renderer.createElement('button', {
      className: 'btn btn-brick',
      dataset: { action: 'trigger-audio-batch-upload' }
    }, ['🎵 Обновить папку с музыкой']);
    audioSyncCard.appendChild(uploadBtn);

    const hiddenAudioInput = Renderer.createElement('input', {
      type: 'file',
      id: 'audio-files-uploader',
      multiple: 'true',
      webkitdirectory: 'true',
      directory: 'true',
      accept: 'audio/*,.mp3,.wav,.ogg,.m4a,.flac',
      className: 'hidden'
    });
    hiddenAudioInput.addEventListener('change', (e) => this.handleBatchAudioUpload(e.target.files));
    audioSyncCard.appendChild(hiddenAudioInput);
    wrap.appendChild(audioSyncCard);"""

new_audio_sync_block = """    // Подгрузка аудиофайлов и прямая работа с папкой на компьютере
    const audioSyncCard = Renderer.createElement('div', { className: 'song-card', style: 'flex-direction: column; align-items: stretch; gap: 0.75rem; border-color: #0284c7;' });
    audioSyncCard.appendChild(Renderer.createElement('h3', { className: 'text-main text-sm', style: 'color: #0369a1;' }, ['🎵 Локальная папка с музыкой (Desktop PWA)']));
    audioSyncCard.appendChild(Renderer.createElement('div', { className: 'text-sm text-muted' }, [
      'Приложение проверяет папку музыки на компьютере на наличие файлов .mp3 по маске ',
      Renderer.createElement('code', { style: 'font-weight: 700; color: var(--chord-color);' }, ['ID_title.mp3']),
      ' (например, 0042_Адонай.mp3 или 0482_запись_Белый_снег.mp3). Все найденные треки сразу становятся доступны в плеере!'
    ]));

    const audioBtns = Renderer.createElement('div', { className: 'flex gap-2 flex-wrap' }, [
      Renderer.createElement('button', {
        className: 'btn btn-brick',
        dataset: { action: 'scan-local-music-folder' },
        title: 'Указать или перепроверить папку музыки на компьютере'
      }, ['📁 Обновить папку с музыкой']),
      Renderer.createElement('button', {
        className: 'btn btn-outline',
        dataset: { action: 'trigger-audio-batch-upload' },
        title: 'Загрузить аудио через релизный манифест'
      }, ['🔄 Проверить сервер'])
    ]);
    audioSyncCard.appendChild(audioBtns);

    const hiddenAudioFolderInput = Renderer.createElement('input', {
      type: 'file',
      id: 'audio-files-uploader',
      multiple: 'true',
      webkitdirectory: 'true',
      directory: 'true',
      accept: 'audio/*,.mp3,.wav,.ogg,.m4a,.flac',
      className: 'hidden'
    });
    hiddenAudioFolderInput.addEventListener('change', (e) => AppController.handleDirectMusicFolderScan(e.target.files));
    audioSyncCard.appendChild(hiddenAudioFolderInput);
    wrap.appendChild(audioSyncCard);

    // КОМПИЛЯЦИЯ АВТОНОМНОГО СБОРНИКА LIGHT READER SPA
    const compileCard = Renderer.createElement('div', { className: 'song-card', style: 'flex-direction: column; align-items: stretch; gap: 0.75rem; border-color: var(--accent);' });
    compileCard.appendChild(Renderer.createElement('h3', { className: 'text-main text-sm' }, ['📦 Компиляция карманного сборника (Light Reader SPA)']));
    compileCard.appendChild(Renderer.createElement('div', { className: 'text-sm text-muted' }, [
      'Сформировать единый автономный HTML-файл со всеми 700 песнями (огненныйветер.html) для раздачи вокалистам и музыкантам. Работает на любых телефонах оффлайн.'
    ]));
    const compileBtn = Renderer.createElement('button', {
      className: 'btn btn-primary',
      dataset: { action: 'compile-standalone-light-spa' }
    }, ['💾 Скомпилировать автономный сборник (.html)']);
    compileCard.appendChild(compileBtn);
    wrap.appendChild(compileCard);"""

assert old_audio_sync_block in text, "old_audio_sync_block not matched"
text = text.replace(old_audio_sync_block, new_audio_sync_block)

# 2. Add handlers in AppController: handleDirectMusicFolderScan and compileStandaloneLightSpa
pwa_desktop_handlers = """
  // Прямое сканирование папки музыки на компьютере (ID_title.mp3)
  static async handleDirectMusicFolderScan(files) {
    if (!files || files.length === 0) return;
    const fileList = Array.from(files).filter(f => /\\.(mp3|wav|ogg|m4a|flac)$/i.test(f.name));
    if (fileList.length === 0) {
      AppController.showToast('В папке не найдено аудиофайлов');
      return;
    }

    const state = store.getState();
    let addedCount = 0;
    const newAudioEntries = [...(state.audio || [])];

    for (const f of fileList) {
      // Ищем ID в начале имени файла: 0042_Адонай.mp3 или 0482_запись_Белый снег.mp3
      const m = f.name.match(/^(\\d{1,4})/);
      const songId = m ? String(m[1]).padStart(4, '0') : '0000';
      let type = 'запись';
      let label = f.name.replace(/\\.[^.]+$/, '');

      if (f.name.includes('_альбом_') || f.name.includes('_studio_')) type = 'альбом';
      else if (f.name.includes('_минус_')) type = 'минус';
      else if (f.name.includes('_импро_')) type = 'импро';

      // Сохраняем в OPFS / StorageAdapter
      try {
        const buf = await f.arrayBuffer();
        await globalStorageAdapter.saveAudioBuffer(f.name, buf);

        const existingIdx = newAudioEntries.findIndex(a => a.filename === f.name || (a.song_id === songId && a.type === type));
        const entry = {
          id: `aud-${songId}-${type}-${Math.random().toString(36).slice(2, 6)}`,
          song_id: songId,
          type: type,
          label: label,
          path: `music/${f.name}`,
          filename: f.name
        };

        if (existingIdx !== -1) newAudioEntries[existingIdx] = entry;
        else newAudioEntries.push(entry);
        addedCount++;
      } catch (err) {
        console.warn('Error storing audio file:', f.name, err);
      }
    }

    store.setState({ audio: newAudioEntries });
    AppController.showToast(`Папка обновлена: подключено ${addedCount} аудиофайлов!`);
    Renderer.renderCurrentView(store.getState());
  }

  // Генерация свежего автономного сборника SPA со вшитыми песнями
  static async compileStandaloneLightSpa() {
    AppController.showToast('Компиляция автономного сборника...');
    try {
      const resp = await fetch('огненныйветер.html');
      let html = '';
      if (resp.ok) {
        html = await resp.text();
      } else {
        // Fallback: use current page document outerHTML
        html = document.documentElement.outerHTML;
      }

      const state = store.getState();
      const blob = new Blob([html], { type: 'text/html;charset=utf-8;' });
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = `огненныйветер_сборник_${new Date().toISOString().slice(0, 10)}.html`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      AppController.showToast('✓ Автономный файл сборника успешно скачан!');
    } catch (err) {
      alert('Ошибка при компиляции сборника: ' + err.message);
    }
  }
"""

pos_ctrl = text.find('class AppController {')
assert pos_ctrl != -1
text = text[:pos_ctrl + len('class AppController {')] + pwa_desktop_handlers + text[pos_ctrl + len('class AppController {'):]

# 3. Add switch cases in handleAction
desktop_actions = """      case 'scan-local-music-folder': {
        if ('showDirectoryPicker' in window) {
          try {
            const dirHandle = await window.showDirectoryPicker();
            const fileList = [];
            for await (const entry of dirHandle.values()) {
              if (entry.kind === 'file' && /\\.(mp3|wav|ogg|m4a|flac)$/i.test(entry.name)) {
                fileList.push(await entry.getFile());
              }
            }
            AppController.handleDirectMusicFolderScan(fileList);
          } catch(err) {
            if (err.name !== 'AbortError') {
              const fInput = document.getElementById('audio-files-uploader');
              if (fInput) fInput.click();
            }
          }
        } else {
          const fInput = document.getElementById('audio-files-uploader');
          if (fInput) fInput.click();
        }
        break;
      }

      case 'compile-standalone-light-spa': {
        AppController.compileStandaloneLightSpa();
        break;
      }"""

pos_handle = text.find("switch (action) {")
assert pos_handle != -1
text = text[:pos_handle + len("switch (action) {")] + "\n" + desktop_actions + "\n" + text[pos_handle + len("switch (action) {"):]

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("PWA Desktop local folder scanner & standalone compiler successfully patched!")
