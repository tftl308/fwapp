with open('tools/build-index.mjs', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. UPGRADE renderPlaylistsView:
# - Active playlists vs Archived playlists at the very bottom
# - Date AND Time of change: new Date(pl.updated_at).toLocaleString('ru-RU', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
# - Editable purpose/comment badge with click action 'edit-playlist-purpose'
# - '👁 Просмотр' button that opens modal without dragging into working list
# - Archive button '🗑 В архив' with confirmation
# - Archived section at the very bottom with Restore '↩ Вернуть' and Permanent Delete '✕ Удалить'

idx_render_pl = code.find("renderPlaylistsView(container, headerActions) {")
idx_render_pl_end = code.find("renderDedicatedPlayerView(container) {", idx_render_pl)
assert idx_render_pl != -1 and idx_render_pl_end != -1, "renderPlaylistsView markers not found"

new_full_playlists_view = """renderPlaylistsView(container, headerActions) {
    container.innerHTML = '';
    const state = store.getState();

    const createBtn = Renderer.createElement('button', {
      className: 'btn btn-brick btn-sm',
      dataset: { action: 'create-new-playlist' }
    }, ['+ Новый список']);
    headerActions.appendChild(createBtn);

    const wrap = Renderer.createElement('div', {
      id: 'playlists-list-container',
      className: 'flex',
      style: 'flex-direction: column; gap: 0.85rem;'
    });

    const activePlaylists = state.playlists.filter(p => p.is_archived !== '1');
    const archivedPlaylists = state.playlists.filter(p => p.is_archived === '1');

    // Функция форматирования даты и времени
    const formatDateTime = (isoStr) => {
      if (!isoStr) return '—';
      try {
        const d = new Date(isoStr);
        return d.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit', year: 'numeric' }) + ' ' +
               d.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
      } catch (e) {
        return isoStr;
      }
    };

    // 1. АКТИВНЫЕ СПИСКИ
    activePlaylists.forEach((pl) => {
      const isCur = pl.id === state.currentPlaylistId;
      const card = Renderer.createElement('div', {
        className: 'playlist-card-row',
        draggable: true,
        dataset: { dragPlaylistId: pl.id },
        style: 'border-color: ' + (isCur ? 'var(--accent)' : 'var(--border-color)') + '; background: var(--bg-card);'
      });

      const topInfoRow = Renderer.createElement('div', {
        style: 'display: flex; align-items: flex-start; justify-content: space-between; gap: 0.5rem;'
      });

      const titleGroup = Renderer.createElement('div', { style: 'flex: 1; min-width: 0;' }, [
        Renderer.createElement('div', { style: 'display: flex; align-items: center; gap: 0.4rem;' }, [
          Renderer.createElement('span', { style: 'color: var(--text-muted); font-size: 1rem; font-weight: 700; cursor: grab;' }, ['↕']),
          Renderer.createElement('span', {
            style: 'font-weight: 800; font-size: 1.05rem; color: var(--text-main); overflow: hidden; text-overflow: ellipsis; white-space: nowrap;'
          }, [pl.title])
        ]),
        Renderer.createElement('div', {
          className: 'text-sm text-muted flex items-center gap-2 flex-wrap',
          style: 'font-size: 0.8rem; margin-top: 0.25rem;'
        }, [
          Renderer.createElement('span', {
            className: 'badge-editable-purpose',
            dataset: { action: 'edit-playlist-purpose', playlistId: pl.id },
            title: 'Нажмите, чтобы изменить комментарий',
            style: 'background: rgba(180, 83, 9, 0.12); color: var(--accent); padding: 2px 7px; border-radius: 4px; font-weight: 600; cursor: pointer;'
          }, ['💬 ' + (pl.purpose || 'Без комментария') + ' ✎']),
          Renderer.createElement('span', {}, ['Изменён: ' + formatDateTime(pl.updated_at || pl.date)])
        ])
      ]);
      topInfoRow.appendChild(titleGroup);

      const items = state.playlistItems
        .filter(it => it.playlist_id === pl.id)
        .sort((a, b) => parseInt(a.order, 10) - parseInt(b.order, 10));

      const countBadge = Renderer.createElement('span', {
        className: 'badge-num',
        style: 'font-size: 0.8rem; padding: 0.25rem 0.6rem; border-radius: 999px; background: var(--badge-bg); color: var(--chord-color); font-weight: 700; flex-shrink: 0;'
      }, [items.length + ' песен']);
      topInfoRow.appendChild(countBadge);
      card.appendChild(topInfoRow);

      // Сетка действий: 5 кнопок для мобильных экранов
      const actionsGrid = Renderer.createElement('div', { className: 'playlist-actions-grid' }, [
        Renderer.createElement('button', {
          className: 'btn btn-outline btn-sm',
          dataset: { action: 'preview-playlist-modal', playlistId: pl.id },
          title: 'Просмотреть песни списка в модальном окне'
        }, ['👁 Просмотр']),
        Renderer.createElement('button', {
          className: 'btn btn-outline btn-sm',
          dataset: { action: 'edit-playlist-in-songs', playlistId: pl.id },
          title: 'Загрузить в рабочий каталог песен'
        }, ['✎ В работу']),
        Renderer.createElement('button', {
          className: 'btn btn-primary btn-sm',
          dataset: { action: 'play-playlist-in-player', playlistId: pl.id },
          title: 'Воспроизвести все треки в плеере'
        }, ['▶ В плеер']),
        Renderer.createElement('button', {
          className: 'btn btn-outline btn-sm',
          dataset: { action: 'show-playlist-qr', playlistId: pl.id },
          title: 'Показать QR-код сетлиста'
        }, ['📱 QR-код']),
        Renderer.createElement('button', {
          className: 'btn btn-brick btn-sm',
          dataset: { action: 'open-concert-from-playlist', playlistId: pl.id },
          title: 'Запустить режим концерта'
        }, ['★ Концерт']),
        Renderer.createElement('button', {
          className: 'btn btn-outline btn-sm text-muted',
          dataset: { action: 'archive-playlist', playlistId: pl.id },
          title: 'Переместить список в архив'
        }, ['🗑 В архив'])
      ]);
      card.appendChild(actionsGrid);

      wrap.appendChild(card);
    });

    // 2. РАЗДЕЛ АРХИВА В САМОМ НИЗУ
    if (archivedPlaylists.length > 0) {
      const archiveHeader = Renderer.createElement('div', {
        style: 'margin-top: 1.5rem; padding-top: 1rem; border-top: 2px dashed var(--border-color); display: flex; align-items: center; justify-content: space-between;'
      }, [
        Renderer.createElement('strong', { className: 'text-muted text-sm' }, ['📦 Архив списков (' + archivedPlaylists.length + ')']),
        Renderer.createElement('span', { className: 'text-xs text-muted' }, ['В архиве'])
      ]);
      wrap.appendChild(archiveHeader);

      archivedPlaylists.forEach((pl) => {
        const card = Renderer.createElement('div', {
          className: 'playlist-card-row',
          style: 'opacity: 0.75; background: var(--bg-card); border-left: 4px solid var(--text-muted);'
        });

        const topInfoRow = Renderer.createElement('div', {
          style: 'display: flex; align-items: flex-start; justify-content: space-between; gap: 0.5rem;'
        });

        const titleGroup = Renderer.createElement('div', { style: 'flex: 1; min-width: 0;' }, [
          Renderer.createElement('div', { style: 'font-weight: 700; font-size: 1rem; color: var(--text-main);' }, [pl.title]),
          Renderer.createElement('div', { className: 'text-sm text-muted', style: 'font-size: 0.8rem;' }, [
            (pl.purpose || 'Сетлист') + ' • Архивация: ' + formatDateTime(pl.updated_at)
          ])
        ]);
        topInfoRow.appendChild(titleGroup);

        const items = state.playlistItems.filter(it => it.playlist_id === pl.id);
        topInfoRow.appendChild(Renderer.createElement('span', { className: 'text-xs text-muted' }, [items.length + ' песен']));
        card.appendChild(topInfoRow);

        const archActions = Renderer.createElement('div', { className: 'flex gap-2 mt-2 justify-end' }, [
          Renderer.createElement('button', {
            className: 'btn btn-outline btn-sm',
            dataset: { action: 'preview-playlist-modal', playlistId: pl.id },
            title: 'Просмотреть состав архивного списка'
          }, ['👁 Просмотр']),
          Renderer.createElement('button', {
            className: 'btn btn-primary btn-sm',
            dataset: { action: 'restore-playlist', playlistId: pl.id },
            title: 'Восстановить список из архива'
          }, ['↩ Восстановить']),
          Renderer.createElement('button', {
            className: 'btn btn-outline btn-sm',
            style: 'color: #dc2626; border-color: rgba(220, 38, 38, 0.4);',
            dataset: { action: 'delete-playlist-permanent', playlistId: pl.id },
            title: 'Стереть навсегда после подтверждения'
          }, ['✕ Стереть'])
        ]);
        card.appendChild(archActions);

        wrap.appendChild(card);
      });
    }

    container.appendChild(wrap);
  }

  """

code = code[:idx_render_pl] + new_full_playlists_view + code[idx_render_pl_end:]
print("Full renderPlaylistsView with Archive, DateTime, Purpose, and Modal Preview applied")

# Update CSS for active state of player buttons and volume slider
player_css = """
    #player-btn-shuffle.active {
      background: var(--badge-bg) !important;
      border-color: var(--chord-color) !important;
      color: var(--chord-color) !important;
    }
    .badge-editable-purpose:hover {
      opacity: 0.8;
      text-decoration: underline;
    }
"""

idx_style = code.find("</style>")
assert idx_style != -1, "</style> not found"
code = code[:idx_style] + player_css + "\n  " + code[idx_style:]
print("Player shuffle and purpose badge CSS added")

with open('tools/build-index.mjs', 'w', encoding='utf-8') as f:
    f.write(code)
print("Part 3 successfully saved to build-index.mjs")
