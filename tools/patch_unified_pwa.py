# -*- coding: utf-8 -*-
with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Check audio card in Settings: enhance to support direct folder selection seamlessly
old_audio_block = """    // Подгрузка аудиофайлов
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

new_audio_block = """    // Подгрузка аудиофайлов и локальная папка с музыкой (единая для всех устройств)
    const audioSyncCard = Renderer.createElement('div', { className: 'song-card', style: 'flex-direction: column; align-items: stretch; gap: 0.75rem;' });
    audioSyncCard.appendChild(Renderer.createElement('h3', { className: 'text-main text-sm' }, ['🎵 Локальная папка с музыкой']));
    audioSyncCard.appendChild(Renderer.createElement('div', { className: 'text-sm text-muted' }, [
      'Выберите аудиофайлы или папку с музыкой (.mp3, .wav, .m4a). Привязка выполняется строго по номеру песни в начале имени файла: ',
      Renderer.createElement('code', { style: 'font-weight: 700; color: var(--chord-color);' }, ['ID_title.mp3']),
      ' (например: 0042_Адонай.mp3 или 0482_запись_Белый_снег.mp3).'
    ]));

    const uploadBtns = Renderer.createElement('div', { className: 'flex gap-2 flex-wrap' }, [
      Renderer.createElement('button', {
        className: 'btn btn-brick',
        dataset: { action: 'trigger-audio-batch-upload' }
      }, ['📁 Обновить папку с музыкой']),
      Renderer.createElement('button', {
        className: 'btn btn-outline',
        dataset: { action: 'trigger-manifest-audio-sync' },
        title: 'Проверить сетевой сервер на новые треки'
      }, ['🔄 Проверить сервер'])
    ]);
    audioSyncCard.appendChild(uploadBtns);

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

assert old_audio_block in text, "old_audio_block not found in index.html"
text = text.replace(old_audio_block, new_audio_block)

# 2. Add action 'trigger-manifest-audio-sync'
marker_switch = "switch (action) {"
action_manifest = """      case 'trigger-manifest-audio-sync': {
        this.syncEngine.sync().then(res => {
          AppController.showToast(`Синхронизация завершена: загружено ${res.downloaded.length} треков`);
        }).catch(err => {
          AppController.showToast('Сервер недоступен или работает в офлайн-режиме');
        });
        break;
      }"""

assert marker_switch in text, "marker_switch not found"
text = text.replace(marker_switch, marker_switch + "\n" + action_manifest)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("Unified PWA index.html updated successfully!")
