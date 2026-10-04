# -*- coding: utf-8 -*-
def patch_content(text):
    # 1. CSS for .playlist-actions-grid and .btn-icon-pure
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

    new_grid_css = """    /* ЕДИНАЯ ПАНЕЛЬ ДЕЙСТВИЙ СО СПИСКАМИ (ТОЧНО ТАКАЯ ЖЕ КАК ВО ВКЛАДКЕ ПЕСНИ) */
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

    .playlist-actions-grid .btn {
      padding: 0.35rem 0.6rem !important;
      font-size: 1.05rem !important;
      min-width: 38px !important;
      min-height: 38px !important;
      display: inline-flex !important;
      align-items: center !important;
      justify-content: center !important;
      touch-action: manipulation !important;
    }"""

    if old_grid_css in text:
        text = text.replace(old_grid_css, new_grid_css)

    # 2. Update renderPlaylistsView actions markup
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

    new_actions_markup = """      // Панель действий: flex items-center justify-between gap-1 text-sm flex-wrap (точно такой же размер и стиль как в песнях)
      const actionsLeft = Renderer.createElement('div', { className: 'flex gap-1 items-center flex-wrap' }, [
        countBadge,
        Renderer.createElement('button', {
          className: 'btn btn-outline btn-sm',
          style: 'padding: 0.35rem 0.6rem; font-size: 1.05rem; min-width: 38px; min-height: 38px;',
          dataset: { action: 'preview-playlist-modal', playlistId: pl.id },
          title: 'Просмотр списка'
        }, ['📋']),
        Renderer.createElement('button', {
          className: 'btn btn-outline btn-sm',
          style: 'padding: 0.35rem 0.6rem; font-size: 1.05rem; min-width: 38px; min-height: 38px;',
          dataset: { action: 'edit-playlist-in-songs', playlistId: pl.id },
          title: 'Редактировать список (В работу)'
        }, ['✏️']),
        Renderer.createElement('button', {
          className: 'btn btn-outline btn-sm',
          style: 'padding: 0.35rem 0.6rem; font-size: 1.05rem; min-width: 38px; min-height: 38px;',
          dataset: { action: 'share-playlist', playlistId: pl.id },
          title: 'Поделиться списком'
        }, ['📤'])
      ]);

      const actionsRight = Renderer.createElement('div', { className: 'flex gap-1 items-center flex-wrap' }, [
        Renderer.createElement('button', {
          className: 'btn btn-primary btn-sm',
          style: 'padding: 0.35rem 0.6rem; font-size: 1.05rem; min-width: 38px; min-height: 38px;',
          dataset: { action: 'play-playlist-in-player', playlistId: pl.id },
          title: 'Воспроизвести в плеере'
        }, ['▶']),
        Renderer.createElement('button', {
          className: 'btn btn-primary btn-sm',
          style: 'padding: 0.35rem 0.6rem; font-size: 1.05rem; min-width: 38px; min-height: 38px;',
          dataset: { action: 'open-concert-from-playlist', playlistId: pl.id },
          title: 'Концертный режим'
        }, ['🎤']),
        ...(pl.id !== 'pl-temp' ? [
          Renderer.createElement('button', {
            className: 'btn btn-outline btn-sm text-muted',
            style: 'padding: 0.35rem 0.6rem; font-size: 1.05rem; min-width: 38px; min-height: 38px;',
            dataset: { action: 'archive-playlist', playlistId: pl.id },
            title: 'Переместить в архив'
          }, ['🗑'])
        ] : [])
      ]);

      const actionsGrid = Renderer.createElement('div', {
        className: 'playlist-actions-grid flex items-center justify-between gap-1 text-sm flex-wrap',
        style: 'margin-top: 0.35rem; padding-top: 0.25rem;'
      }, [actionsLeft, actionsRight]);"""

    if old_actions_markup in text:
        text = text.replace(old_actions_markup, new_actions_markup)

    return text

with open('tools/build-index.mjs', 'r', encoding='utf-8') as f:
    b_text = f.read()
b_patched = patch_content(b_text)
with open('tools/build-index.mjs', 'w', encoding='utf-8') as f:
    f.write(b_patched)

with open('index.html', 'r', encoding='utf-8') as f:
    i_text = f.read()
i_patched = patch_content(i_text)
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(i_patched)

print("Both tools/build-index.mjs and index.html successfully patched with matching playlist action buttons!")
