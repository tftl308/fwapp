with open('tools/build-index.mjs', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. ADD SHUFFLE AND VOLUME CONTROLS TO PLAYER UI
# In renderDedicatedPlayerView:
idx_controls = code.find("const controls = Renderer.createElement('div', { className: 'player-controls-row' });")
assert idx_controls != -1, "player-controls-row not found"

old_controls_block = """    const controls = Renderer.createElement('div', { className: 'player-controls-row' });
    const prevBtn = Renderer.createElement('button', {
      className: 'btn btn-icon btn-outline',
      dataset: { action: 'player-prev-track' },
      ariaLabel: 'Предыдущий трек'
    }, [
      Renderer.createElement('svg', { width: 24, height: 24, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor' }, [
        Renderer.createElement('polygon', { points: '19 20 9 12 19 4 19 20' }),
        Renderer.createElement('line', { x1: '5', y1: '19', x2: '5', y2: '5' })
      ])
    ]);
    controls.appendChild(prevBtn);

    const playBtn = Renderer.createElement('button', {
      className: 'btn-play-circle',
      id: 'main-play-btn',
      dataset: { action: 'player-toggle-play' },
      ariaLabel: 'Воспроизведение / Пауза'
    }, [
      Renderer.createElement('svg', {
        id: 'main-play-icon',
        className: state.isPlaying ? 'hidden' : '',
        width: 28,
        height: 28,
        viewBox: '0 0 24 24',
        fill: 'currentColor'
      }, [
        Renderer.createElement('polygon', { points: '5 3 19 12 5 21 5 3' })
      ]),
      Renderer.createElement('svg', {
        id: 'main-pause-icon',
        className: !state.isPlaying ? 'hidden' : '',
        width: 28,
        height: 28,
        viewBox: '0 0 24 24',
        fill: 'currentColor'
      }, [
        Renderer.createElement('rect', { x: '6', y: '4', width: '4', height: '16' }),
        Renderer.createElement('rect', { x: '14', y: '4', width: '4', height: '16' })
      ])
    ]);
    controls.appendChild(playBtn);

    const nextBtn = Renderer.createElement('button', {
      className: 'btn btn-icon btn-outline',
      dataset: { action: 'player-next-track' },
      ariaLabel: 'Следующий трек'
    }, [
      Renderer.createElement('svg', { width: 24, height: 24, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor' }, [
        Renderer.createElement('polygon', { points: '5 4 15 12 5 20 5 4' }),
        Renderer.createElement('line', { x1: '19', y1: '5', x2: '19', y2: '19' })
      ])
    ]);
    controls.appendChild(nextBtn);
    leftCard.appendChild(controls);"""

new_controls_block = """    const controls = Renderer.createElement('div', { className: 'player-controls-row' });

    // Кнопка случайного порядка / по порядку
    const shuffleBtn = Renderer.createElement('button', {
      className: 'btn btn-icon btn-outline ' + (audioPlayer.isShuffle ? 'active' : ''),
      id: 'player-btn-shuffle',
      dataset: { action: 'player-toggle-shuffle' },
      title: audioPlayer.isShuffle ? 'Случайный порядок (вкл)' : 'По порядку'
    }, [
      Renderer.createElement('svg', { width: 20, height: 20, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor' }, [
        Renderer.createElement('polyline', { points: '16 3 21 3 21 8' }),
        Renderer.createElement('line', { x1: '4', y1: '20', x2: '21', y2: '3' }),
        Renderer.createElement('polyline', { points: '21 16 21 21 16 21' }),
        Renderer.createElement('line', { x1: '15', y1: '15', x2: '21', y2: '21' }),
        Renderer.createElement('line', { x1: '4', y1: '4', x2: '9', y2: '9' })
      ])
    ]);
    controls.appendChild(shuffleBtn);

    const prevBtn = Renderer.createElement('button', {
      className: 'btn btn-icon btn-outline',
      dataset: { action: 'player-prev-track' },
      ariaLabel: 'Предыдущий трек'
    }, [
      Renderer.createElement('svg', { width: 24, height: 24, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor' }, [
        Renderer.createElement('polygon', { points: '19 20 9 12 19 4 19 20' }),
        Renderer.createElement('line', { x1: '5', y1: '19', x2: '5', y2: '5' })
      ])
    ]);
    controls.appendChild(prevBtn);

    const playBtn = Renderer.createElement('button', {
      className: 'btn-play-circle',
      id: 'main-play-btn',
      dataset: { action: 'player-toggle-play' },
      ariaLabel: 'Воспроизведение / Пауза'
    }, [
      Renderer.createElement('svg', {
        id: 'main-play-icon',
        className: state.isPlaying ? 'hidden' : '',
        width: 28,
        height: 28,
        viewBox: '0 0 24 24',
        fill: 'currentColor'
      }, [
        Renderer.createElement('polygon', { points: '5 3 19 12 5 21 5 3' })
      ]),
      Renderer.createElement('svg', {
        id: 'main-pause-icon',
        className: !state.isPlaying ? 'hidden' : '',
        width: 28,
        height: 28,
        viewBox: '0 0 24 24',
        fill: 'currentColor'
      }, [
        Renderer.createElement('rect', { x: '6', y: '4', width: '4', height: '16' }),
        Renderer.createElement('rect', { x: '14', y: '4', width: '4', height: '16' })
      ])
    ]);
    controls.appendChild(playBtn);

    const nextBtn = Renderer.createElement('button', {
      className: 'btn btn-icon btn-outline',
      dataset: { action: 'player-next-track' },
      ariaLabel: 'Следующий трек'
    }, [
      Renderer.createElement('svg', { width: 24, height: 24, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor' }, [
        Renderer.createElement('polygon', { points: '5 4 15 12 5 20 5 4' }),
        Renderer.createElement('line', { x1: '19', y1: '5', x2: '19', y2: '19' })
      ])
    ]);
    controls.appendChild(nextBtn);
    leftCard.appendChild(controls);

    // Ползунок громкости
    const volumeRow = Renderer.createElement('div', {
      className: 'player-volume-row flex items-center justify-center gap-2 mt-2',
      style: 'width: 100%; max-width: 260px; margin: 0.75rem auto 0 auto;'
    }, [
      Renderer.createElement('span', { style: 'color: var(--text-muted); font-size: 0.9rem;' }, ['🔈']),
      Renderer.createElement('input', {
        type: 'range',
        id: 'player-volume-slider',
        min: '0',
        max: '1',
        step: '0.05',
        value: audioPlayer.volume.toString(),
        style: 'flex: 1; accent-color: var(--chord-color); cursor: pointer;'
      }),
      Renderer.createElement('span', { style: 'color: var(--text-muted); font-size: 0.9rem;' }, ['🔊'])
    ]);
    leftCard.appendChild(volumeRow);"""

assert old_controls_block in code, "old_controls_block not found"
code = code.replace(old_controls_block, new_controls_block)
print("Shuffle and Volume controls added to player view")

# 2. SAVE WORKING LIST AS NEW PLAYLIST
# In renderCatalogView: in plControlsBar, add "+ Сохранить как..." button
old_pl_controls_bar = """        Renderer.createElement('button', { className: 'btn btn-outline btn-sm', dataset: { action: 'create-new-playlist' } }, ['+ Создать']),"""

new_pl_controls_bar = """        Renderer.createElement('button', { className: 'btn btn-outline btn-sm', dataset: { action: 'create-new-playlist' } }, ['+ Создать']),
        Renderer.createElement('button', { className: 'btn btn-brick btn-sm', dataset: { action: 'save-active-playlist-as' }, title: 'Сохранить сформированный список под новым именем' }, ['💾 Сохранить как']),"""

assert old_pl_controls_bar in code, "old_pl_controls_bar not found"
code = code.replace(old_pl_controls_bar, new_pl_controls_bar)
print("Save active playlist as button added to catalog")

# Add actions in handleAction for:
# player-toggle-shuffle
# save-active-playlist-as
# preview-playlist-modal
# archive-playlist
# restore-playlist
# delete-playlist-permanent
# edit-playlist-purpose
action_cases = """      case 'player-toggle-shuffle': {
        audioPlayer.toggleShuffle();
        const btn = document.getElementById('player-btn-shuffle');
        if (btn) btn.classList.toggle('active', audioPlayer.isShuffle);
        break;
      }

      case 'save-active-playlist-as': {
        const curItems = state.playlistItems.filter(it => it.playlist_id === state.currentPlaylistId);
        if (curItems.length === 0) {
          AppController.showToast('Текущий список пуст! Добавьте песни перед сохранением.');
          return;
        }
        const name = prompt('Введите имя для нового сохранённого списка:');
        if (name && name.trim()) {
          const newId = 'pl-' + Date.now();
          const newPl = {
            id: newId,
            title: name.trim(),
            date: new Date().toISOString().split('T')[0],
            purpose: 'Пользовательский список',
            is_public: '1',
            is_archived: '0',
            updated_at: new Date().toISOString()
          };
          // Клонируем песни в новый список
          const newItems = curItems.map((it, idx) => ({
            id: 'item-' + newId + '-' + idx,
            playlist_id: newId,
            song_id: it.song_id,
            order: it.order,
            note: it.note || ''
          }));

          undoManager.pushState('Сохранение списка ' + name.trim(), {
            playlists: state.playlists,
            playlistItems: state.playlistItems
          });

          const updatedPlaylists = [newPl, ...state.playlists];
          const updatedItems = [...state.playlistItems, ...newItems];

          await storage.saveBatch('playlists', updatedPlaylists);
          await storage.saveBatch('playlistItems', updatedItems);
          store.setState({
            playlists: updatedPlaylists,
            playlistItems: updatedItems,
            currentPlaylistId: newId
          });
          AppController.showToast('Список "' + name.trim() + '" успешно сохранён!');
        }
        break;
      }

      case 'preview-playlist-modal': {
        const plId = el.dataset.playlistId;
        this.showPlaylistPreviewModal(plId);
        break;
      }

      case 'close-preview-modal': {
        const modal = document.getElementById('preview-modal-overlay');
        if (modal) modal.remove();
        break;
      }

      case 'archive-playlist': {
        const plId = el.dataset.playlistId;
        const pl = state.playlists.find(p => p.id === plId);
        if (!pl) return;
        if (confirm('Переместить список "' + pl.title + '" в архив?')) {
          undoManager.pushState('Архивация списка ' + pl.title, { playlists: state.playlists });
          pl.is_archived = '1';
          pl.updated_at = new Date().toISOString();
          const updated = [...state.playlists];
          await storage.saveBatch('playlists', updated);
          store.setState({ playlists: updated });
          AppController.showToast('Список перемещён в архив');
        }
        break;
      }

      case 'restore-playlist': {
        const plId = el.dataset.playlistId;
        const pl = state.playlists.find(p => p.id === plId);
        if (!pl) return;
        undoManager.pushState('Восстановление списка ' + pl.title, { playlists: state.playlists });
        pl.is_archived = '0';
        pl.updated_at = new Date().toISOString();
        const updated = [...state.playlists];
        await storage.saveBatch('playlists', updated);
        store.setState({ playlists: updated });
        AppController.showToast('Список восстановлен из архива');
        break;
      }

      case 'delete-playlist-permanent': {
        const plId = el.dataset.playlistId;
        const pl = state.playlists.find(p => p.id === plId);
        if (!pl) return;
        if (confirm('ВНИМАНИЕ! Безвозвратно удалить список "' + pl.title + '" из архива?')) {
          undoManager.pushState('Удаление списка ' + pl.title, {
            playlists: state.playlists,
            playlistItems: state.playlistItems
          });
          const updatedPlaylists = state.playlists.filter(p => p.id !== plId);
          const updatedItems = state.playlistItems.filter(it => it.playlist_id !== plId);
          await storage.saveBatch('playlists', updatedPlaylists);
          await storage.saveBatch('playlistItems', updatedItems);
          store.setState({
            playlists: updatedPlaylists,
            playlistItems: updatedItems,
            currentPlaylistId: state.currentPlaylistId === plId ? 'pl-temp' : state.currentPlaylistId
          });
          AppController.showToast('Список безвозвратно удалён');
        }
        break;
      }

      case 'edit-playlist-purpose': {
        const plId = el.dataset.playlistId;
        const pl = state.playlists.find(p => p.id === plId);
        if (!pl) return;
        const newPurpose = prompt('Редактировать комментарий/назначение списка:', pl.purpose || '');
        if (newPurpose !== null) {
          undoManager.pushState('Изменение комментария списка ' + pl.title, { playlists: state.playlists });
          pl.purpose = newPurpose.trim();
          pl.updated_at = new Date().toISOString();
          const updated = [...state.playlists];
          await storage.saveBatch('playlists', updated);
          store.setState({ playlists: updated });
          AppController.showToast('Комментарий обновлён');
        }
        break;
      }
"""

idx_show_qr = code.find("case 'show-playlist-qr': {")
assert idx_show_qr != -1, "show-playlist-qr not found"
code = code[:idx_show_qr] + action_cases + "\n      " + code[idx_show_qr:]
print("New action cases added to handleAction")

# In setupDelegatedEvents: add listener for volume slider input
old_input_delegation = """    document.addEventListener('input', (e) => {
      if (e.target.id === 'search-input') {"""

new_input_delegation = """    document.addEventListener('input', (e) => {
      if (e.target.id === 'player-volume-slider') {
        audioPlayer.setVolume(parseFloat(e.target.value));
        return;
      }
      if (e.target.id === 'search-input') {"""

assert old_input_delegation in code, "old_input_delegation not found"
code = code.replace(old_input_delegation, new_input_delegation)
print("Volume slider input event added")

# Method showPlaylistPreviewModal
preview_modal_method = """  showPlaylistPreviewModal(playlistId) {
    const state = store.getState();
    const pl = state.playlists.find(p => p.id === playlistId);
    if (!pl) return;

    const items = state.playlistItems
      .filter(it => it.playlist_id === playlistId)
      .sort((a, b) => parseInt(a.order, 10) - parseInt(b.order, 10));

    const existing = document.getElementById('preview-modal-overlay');
    if (existing) existing.remove();

    const overlay = Renderer.createElement('div', {
      id: 'preview-modal-overlay',
      className: 'qr-modal-overlay',
      dataset: { action: 'close-preview-modal' }
    });

    const box = Renderer.createElement('div', {
      className: 'preview-modal-box',
      style: 'background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 1rem; padding: 1.25rem; max-width: 480px; width: 92%; max-height: 80vh; display: flex; flex-direction: column; gap: 0.75rem; box-shadow: 0 10px 30px rgba(0,0,0,0.25);'
    });
    box.addEventListener('click', (e) => e.stopPropagation());

    const hdr = Renderer.createElement('div', { style: 'display: flex; align-items: flex-start; justify-content: space-between; gap: 0.5rem;' }, [
      Renderer.createElement('div', {}, [
        Renderer.createElement('h3', { style: 'font-weight: 800; color: var(--text-main); font-size: 1.15rem;' }, [pl.title]),
        Renderer.createElement('div', { className: 'text-sm text-muted' }, [
          (pl.purpose || 'Сетлист') + ' • Песен: ' + items.length
        ])
      ]),
      Renderer.createElement('button', {
        className: 'btn btn-icon btn-outline btn-sm',
        dataset: { action: 'close-preview-modal' },
        style: 'flex-shrink: 0;'
      }, ['✕'])
    ]);
    box.appendChild(hdr);

    const listScroll = Renderer.createElement('div', {
      style: 'flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 0.4rem; padding-right: 0.25rem;'
    });

    if (items.length === 0) {
      listScroll.appendChild(Renderer.createElement('div', { className: 'text-sm text-muted', style: 'padding: 1.5rem; text-align: center;' }, ['В этом списке пока нет песен']));
    } else {
      items.forEach((it, idx) => {
        const s = state.songs.find(x => x.id === it.song_id);
        const row = Renderer.createElement('div', {
          style: 'display: flex; align-items: center; justify-content: space-between; padding: 0.5rem 0.65rem; border-radius: 0.4rem; background: var(--bg-primary); gap: 0.5rem;'
        }, [
          Renderer.createElement('div', { style: 'display: flex; align-items: center; gap: 0.5rem; min-width: 0;' }, [
            Renderer.createElement('span', { style: 'color: var(--text-muted); font-size: 0.85rem; font-weight: 700;' }, [(idx + 1) + '.']),
            Renderer.createElement('span', { style: 'font-weight: 600; font-size: 0.95rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;' }, [s ? s.title : 'Песня #' + it.song_id])
          ]),
          Renderer.createElement('span', { className: 'badge-key-capo', style: 'flex-shrink: 0;' }, [s ? Renderer.formatKeyCapo(s.key, s.capo) : ''])
        ]);
        listScroll.appendChild(row);
      });
    }
    box.appendChild(listScroll);

    const footer = Renderer.createElement('div', { style: 'display: flex; gap: 0.5rem; justify-content: flex-end; margin-top: 0.5rem;' }, [
      Renderer.createElement('button', {
        className: 'btn btn-outline btn-sm',
        dataset: { action: 'close-preview-modal' }
      }, ['Закрыть']),
      Renderer.createElement('button', {
        className: 'btn btn-primary btn-sm',
        dataset: { action: 'edit-playlist-in-songs', playlistId: pl.id }
      }, ['✎ Открыть в работу'])
    ]);
    box.appendChild(footer);

    overlay.appendChild(box);
    document.body.appendChild(overlay);
  }

  """

idx_show_qr_method = code.find("showPlaylistQrModal(playlistId) {")
assert idx_show_qr_method != -1, "showPlaylistQrModal not found"
code = code[:idx_show_qr_method] + preview_modal_method + code[idx_show_qr_method:]
print("showPlaylistPreviewModal method added")

with open('tools/build-index.mjs', 'w', encoding='utf-8') as f:
    f.write(code)
print("Part 2 update saved to build-index.mjs")
