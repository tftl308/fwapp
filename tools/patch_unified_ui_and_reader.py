# -*- coding: utf-8 -*-
with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Fix .playlist-actions-grid to match the unified bar
# Old:
old_grid_css = """    /* АДАПТИВНАЯ СЕТКА КНОПОК СПИСКОВ НА МОБИЛЬНЫХ */
    .playlist-actions-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 0.5rem;
      margin-top: 0.5rem;
    }

    @media (min-width: 600px) {
      .playlist-actions-grid {
        grid-template-columns: repeat(4, auto);
        justify-content: flex-end;
      }
    }"""

new_grid_css = """    /* ЕДИНАЯ ПАНЕЛЬ ДЕЙСТВИЙ СО СПИСКАМИ (КАК ВО ВКЛАДКЕ ПЕСНИ) */
    .playlist-actions-grid {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 0.25rem;
      font-size: 0.875rem;
      flex-wrap: wrap;
      width: 100%;
      margin-top: 0.35rem;
      padding-top: 0.25rem;
      border-top: 1px dashed var(--border-color);
    }

    .playlist-actions-grid .btn-icon-pure {
      padding: 0.35rem 0.55rem;
      font-size: 1.05rem;
      min-width: 38px;
      min-height: 38px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      border-radius: 6px;
      border: 1px solid var(--border-color);
      background: var(--bg-card);
      touch-action: manipulation;
    }

    .playlist-actions-grid .btn-icon-pure:active {
      transform: scale(0.96);
      background: var(--badge-bg);
    }"""

assert old_grid_css in text, "old_grid_css not found"
text = text.replace(old_grid_css, new_grid_css)

# Also update where actionsGrid is rendered in playlist view
old_actions_markup = """      // Панель действий: badge-num слева, далее только иконки действий БЕЗ кнопки импорта (импорт только в шапке)
      const actionsGrid = Renderer.createElement('div', {
        className: 'playlist-actions-grid',
        style: 'display: flex; gap: 0.35rem; justify-content: flex-end; align-items: center; width: 100%; margin-top: 0.35rem;'
      }, [
        countBadge,
        Renderer.createElement('button', {
          className: 'btn-icon-pure',
          dataset: { action: 'preview-playlist-modal', playlistId: pl.id },
          title: 'Просмотр списка'
        }, ['📋']),
        Renderer.createElement('button', {
          className: 'btn-icon-pure',
          dataset: { action: 'edit-playlist-in-songs', playlistId: pl.id },
          title: 'Редактировать список (В работу)'
        }, ['✏️']),
        Renderer.createElement('button', {
          className: 'btn-icon-pure text-accent',
          dataset: { action: 'play-playlist-in-player', playlistId: pl.id },
          title: 'Воспроизвести в плеере'
        }, ['▶']),
        Renderer.createElement('button', {
          className: 'btn-icon-pure',
          dataset: { action: 'share-playlist', playlistId: pl.id },
          title: 'Поделиться списком'
        }, ['📤']),
        Renderer.createElement('button', {
          className: 'btn-icon-pure text-accent',
          dataset: { action: 'open-concert-from-playlist', playlistId: pl.id },
          title: 'Концертный режим'
        }, ['🎤']),
        ...(pl.id !== 'pl-temp' ? [
          Renderer.createElement('button', {
            className: 'btn-icon-pure text-muted',
            dataset: { action: 'archive-playlist', playlistId: pl.id },
            title: 'Переместить в архив'
          }, ['🗑'])
        ] : [])
      ]);"""

new_actions_markup = """      // Панель действий: flex items-center justify-between gap-1 text-sm flex-wrap (как во вкладке Песни)
      const actionsLeft = Renderer.createElement('div', { className: 'flex gap-1 items-center flex-wrap' }, [
        countBadge,
        Renderer.createElement('button', {
          className: 'btn btn-outline btn-sm btn-icon-pure',
          dataset: { action: 'preview-playlist-modal', playlistId: pl.id },
          title: 'Просмотр списка'
        }, ['📋']),
        Renderer.createElement('button', {
          className: 'btn btn-outline btn-sm btn-icon-pure',
          dataset: { action: 'edit-playlist-in-songs', playlistId: pl.id },
          title: 'Редактировать список (В работу)'
        }, ['✏️']),
        Renderer.createElement('button', {
          className: 'btn btn-outline btn-sm btn-icon-pure',
          dataset: { action: 'share-playlist', playlistId: pl.id },
          title: 'Поделиться списком'
        }, ['📤'])
      ]);

      const actionsRight = Renderer.createElement('div', { className: 'flex gap-1 items-center flex-wrap' }, [
        Renderer.createElement('button', {
          className: 'btn btn-primary btn-sm btn-icon-pure',
          dataset: { action: 'play-playlist-in-player', playlistId: pl.id },
          title: 'Воспроизвести в плеере'
        }, ['▶']),
        Renderer.createElement('button', {
          className: 'btn btn-primary btn-sm btn-icon-pure',
          dataset: { action: 'open-concert-from-playlist', playlistId: pl.id },
          title: 'Концертный режим'
        }, ['🎤']),
        ...(pl.id !== 'pl-temp' ? [
          Renderer.createElement('button', {
            className: 'btn btn-outline btn-sm btn-icon-pure text-muted',
            dataset: { action: 'archive-playlist', playlistId: pl.id },
            title: 'Переместить в архив'
          }, ['🗑'])
        ] : [])
      ]);

      const actionsGrid = Renderer.createElement('div', {
        className: 'playlist-actions-grid flex items-center justify-between gap-1 text-sm flex-wrap'
      }, [actionsLeft, actionsRight]);"""

assert old_actions_markup in text, "old_actions_markup not found"
text = text.replace(old_actions_markup, new_actions_markup)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("index.html playlist-actions-grid updated to match songs tab controls!")
