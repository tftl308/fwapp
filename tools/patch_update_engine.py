# -*- coding: utf-8 -*-
with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update manifest link in <head>
text = text.replace('href="manifest.json"', 'href="./manifest.webmanifest"')

# 2. Add Update Badge and Modal styles in <style>
update_css = """
    /* ONE-CLICK UPDATE BADGE & MODAL (GITHUB PAGES tftl308.github.io) */
    .btn-update-available {
      position: relative;
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
      background: #dc2626;
      color: #fff !important;
      border: 1px solid #b91c1c;
      padding: 0.3rem 0.65rem;
      border-radius: 9999px;
      font-size: 0.78rem;
      font-weight: 700;
      animation: pulse-update 2s infinite;
      cursor: pointer;
    }
    .badge-update-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #fef08a;
      box-shadow: 0 0 6px #fde047;
    }
    @keyframes pulse-update {
      0% { box-shadow: 0 0 0 0 rgba(220, 38, 38, 0.6); }
      70% { box-shadow: 0 0 0 8px rgba(220, 38, 38, 0); }
      100% { box-shadow: 0 0 0 0 rgba(220, 38, 38, 0); }
    }
    .update-modal-box {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      max-width: 480px;
      width: 90%;
      padding: 1.25rem;
      box-shadow: 0 10px 25px rgba(0,0,0,0.3);
      display: flex;
      flex-direction: column;
      gap: 0.8rem;
    }
"""
text = text.replace('</style>', update_css + '\n</style>')

# 3. Add UpdateEngine in client script
update_engine_js = """
// =========================================================================
// ONE-CLICK UPDATE ENGINE (tftl308.github.io / GitHub Pages)
// =========================================================================
class UpdateEngine {
  static async checkForUpdates(isManual = false) {
    try {
      const res = await fetch('./data/version.json?_t=' + Date.now(), { cache: 'no-store' });
      if (!res.ok) return { available: false };
      const remote = await res.json();
      
      const local = await storage.getSetting('app_version_meta') || {
        app_build: "0",
        songs_hash: "",
        playlists_hash: "",
        notes_hash: ""
      };

      const hasNewBuild = remote.app_build && remote.app_build !== local.app_build;
      const needsData = remote.songs_hash !== local.songs_hash ||
                        remote.playlists_hash !== local.playlists_hash ||
                        remote.notes_hash !== local.notes_hash;

      const result = {
        available: hasNewBuild || needsData,
        remote,
        local,
        needsApp: hasNewBuild,
        needsData: needsData
      };

      if (result.available) {
        UpdateEngine.renderHeaderBadge(result);
      } else if (isManual) {
        AppController.showToast('✓ У вас установлена самая свежая версия программы и песен!');
      }

      return result;
    } catch(err) {
      if (isManual) {
        AppController.showToast('Работа в офлайн-режиме: сервер недоступен');
      }
      return { available: false, offline: true };
    }
  }

  static renderHeaderBadge(updateInfo) {
    const headerActions = document.getElementById('header-actions');
    if (!headerActions) return;

    let badge = document.getElementById('btn-header-update-badge');
    if (!badge) {
      badge = Renderer.createElement('button', {
        id: 'btn-header-update-badge',
        className: 'btn-update-available',
        dataset: { action: 'open-update-modal' },
        title: 'Доступно обновление базы и приложения'
      }, [
        Renderer.createElement('span', { className: 'badge-update-dot' }),
        'Обновление'
      ]);
      headerActions.prepend(badge);
    }
    window._lastUpdateInfo = updateInfo;
  }

  static showUpdateModal(info) {
    const existing = document.getElementById('update-modal-overlay');
    if (existing) existing.remove();

    const overlay = Renderer.createElement('div', {
      id: 'update-modal-overlay',
      className: 'qr-modal-overlay',
      style: 'display: flex;'
    });

    const box = Renderer.createElement('div', { className: 'update-modal-box' });

    box.appendChild(Renderer.createElement('h3', { style: 'margin: 0; color: var(--accent);' }, ['🚀 Доступно обновление Огненный Ветер']));
    
    const verRow = Renderer.createElement('div', { className: 'text-xs text-muted' }, [
      `Текущая сборка: ${info.local.app_build || 'начальная'} ➔ Новая: ${info.remote.app_build || info.remote.app_version}`
    ]);
    box.appendChild(verRow);

    if (info.remote.changelog) {
      const chgBox = Renderer.createElement('div', {
        style: 'background: rgba(180, 83, 9, 0.08); border-radius: 6px; padding: 0.6rem; font-size: 0.82rem; border-left: 3px solid var(--accent);'
      }, [
        Renderer.createElement('strong', {}, ['Что нового: ']),
        info.remote.changelog
      ]);
      box.appendChild(chgBox);
    }

    const progressDiv = Renderer.createElement('div', {
      id: 'update-progress-status',
      className: 'text-xs',
      style: 'color: var(--text-muted); min-height: 1.2rem;'
    }, ['Нажмите кнопку ниже для загрузки одним нажатием.']);
    box.appendChild(progressDiv);

    const btnRow = Renderer.createElement('div', { style: 'display: flex; gap: 0.5rem; justify-content: flex-end; margin-top: 0.5rem;' }, [
      Renderer.createElement('button', {
        className: 'btn btn-outline btn-sm',
        dataset: { action: 'close-update-modal' }
      }, ['Позже']),
      Renderer.createElement('button', {
        className: 'btn btn-primary btn-sm',
        id: 'btn-run-update-now',
        style: 'background: var(--accent); border-color: var(--accent); font-weight: 700;',
        dataset: { action: 'apply-full-update' }
      }, ['⚡ Обновить сейчас'])
    ]);
    box.appendChild(btnRow);

    overlay.appendChild(box);
    document.body.appendChild(overlay);
  }

  static async applyFullUpdate(info) {
    const statusEl = document.getElementById('update-progress-status');
    const updateBtn = document.getElementById('btn-run-update-now');
    if (updateBtn) updateBtn.disabled = true;

    try {
      if (statusEl) statusEl.textContent = '1/4. Скачивание каталога песен (songs.csv)...';
      const songsRes = await fetch('./data/songs.csv?_t=' + Date.now(), { cache: 'no-store' });
      if (songsRes.ok) {
        const text = await songsRes.text();
        const records = CsvHelper.parse(text);
        if (records && records.length > 0) {
          const songsList = records.map(r => ({
            id: String(r.id || '').padStart(4, '0'),
            number: r.number || r.id,
            title: r.title || 'Без названия',
            author: r.author || '',
            key: r.key || '',
            key_default: r.key || '',
            capo: r.capo || '',
            tempo: r.tempo || '',
            time_signature: r.time_signature || '4/4',
            duration: r.duration || '',
            predelay: r.predelay || '',
            presentation: r.presentation || '',
            theme: r.theme || r.alt_title || '',
            alttheme: r.alttheme || '',
            user1: r.user1 || '',
            user2: r.user2 || '',
            user3: r.user3 || '',
            lyrics: r.lyrics || r.body_plain || '',
            body_plain: r.lyrics || r.body_plain || '',
            chordpro: r.chordpro || r.body_chordpro || '',
            body_chordpro: r.chordpro || r.body_chordpro || '',
            notes: r.notes || '',
            link_audio: r.link_audio || '',
            link_youtube: r.link_youtube || '',
            custom_chords: r.custom_chords || ''
          }));
          await storage.clear('songs');
          for (const s of songsList) {
            await storage.putOne('songs', s);
          }
        }
      }

      if (statusEl) statusEl.textContent = '2/4. Скачивание списков и заметок...';
      try {
        const plRes = await fetch('./data/playlists.csv?_t=' + Date.now(), { cache: 'no-store' });
        if (plRes.ok) {
          const pls = CsvHelper.parse(await plRes.text());
          for (const p of pls) await storage.putOne('playlists', p);
        }
        const plItemsRes = await fetch('./data/playlist_items.csv?_t=' + Date.now(), { cache: 'no-store' });
        if (plItemsRes.ok) {
          const its = CsvHelper.parse(await plItemsRes.text());
          for (const it of its) await storage.putOne('playlistItems', it);
        }
      } catch(e) {}

      if (statusEl) statusEl.textContent = '3/4. Обновление Service Worker кэша...';
      if ('serviceWorker' in navigator) {
        const reg = await navigator.serviceWorker.getRegistration();
        if (reg) await reg.update();
      }

      // Сохраняем новую версию метаданных в IndexedDB
      await storage.setSetting('app_version_meta', info.remote);
      await storage.setSetting('db_initialized', true);

      if (statusEl) statusEl.textContent = '4/4. ✓ Успешно обновлено! Перезагрузка...';
      setTimeout(() => {
        window.location.reload();
      }, 800);
    } catch(err) {
      if (statusEl) statusEl.textContent = 'Ошибка обновления: ' + err.message;
      if (updateBtn) updateBtn.disabled = false;
    }
  }
}
"""

pos_app_ctrl = text.find('class AppController {')
assert pos_app_ctrl != -1
text = text[:pos_app_ctrl] + update_engine_js + "\n" + text[pos_app_ctrl:]

# 4. In AppController init: trigger checkForUpdates()
old_init_call = "await this.loadInitialData();"
new_init_call = """await this.loadInitialData();
    // Фоновая проверка обновлений с GitHub Pages (tftl308.github.io)
    setTimeout(() => UpdateEngine.checkForUpdates(false), 1500);"""
assert old_init_call in text
text = text.replace(old_init_call, new_init_call, 1)

# 5. In handleAction switch: handle update buttons
update_actions = """      case 'open-update-modal': {
        if (window._lastUpdateInfo) {
          UpdateEngine.showUpdateModal(window._lastUpdateInfo);
        } else {
          UpdateEngine.checkForUpdates(true).then(res => {
            if (res.available) UpdateEngine.showUpdateModal(res);
          });
        }
        break;
      }
      case 'close-update-modal': {
        const m = document.getElementById('update-modal-overlay');
        if (m) m.remove();
        break;
      }
      case 'apply-full-update': {
        if (window._lastUpdateInfo) {
          UpdateEngine.applyFullUpdate(window._lastUpdateInfo);
        }
        break;
      }
      case 'check-manual-updates': {
        UpdateEngine.checkForUpdates(true).then(res => {
          if (res.available) UpdateEngine.showUpdateModal(res);
        });
        break;
      }"""

pos_switch = text.find("switch (action) {")
assert pos_switch != -1
text = text[:pos_switch + len("switch (action) {")] + "\n" + update_actions + text[pos_switch + len("switch (action) {"):]

# 6. Add manual check button to Settings View
old_settings_proj = "// БЛОК АВТОНОМНОЙ СИНХРОНИЗАЦИИ ПАПКИ"
new_settings_update = """    // КНОПКА ПРОВЕРКИ ОБНОВЛЕНИЙ ПО ОДНОЙ КНОПКЕ С GITHUB PAGES
    const updateCard = Renderer.createElement('div', { className: 'song-card', style: 'flex-direction: column; align-items: stretch; gap: 0.75rem; border: 2px solid var(--accent); background: rgba(192, 48, 0, 0.04);' });
    updateCard.appendChild(Renderer.createElement('h3', { className: 'text-main text-sm', style: 'color: var(--accent);' }, ['☁️ Обновление с сервера (GitHub Pages)']));
    updateCard.appendChild(Renderer.createElement('div', { className: 'text-xs text-muted' }, [
      'Проверить сервер tftl308.github.io на наличие новых песен и обновлений приложения по одной кнопке. Работает оффлайн после загрузки.'
    ]));
    const updateBtns = Renderer.createElement('div', { className: 'flex gap-2 flex-wrap' }, [
      Renderer.createElement('button', {
        className: 'btn btn-brick btn-sm',
        dataset: { action: 'check-manual-updates' }
      }, ['🔄 Проверить и обновить сейчас'])
    ]);
    updateCard.appendChild(updateBtns);
    wrap.appendChild(updateCard);

    // БЛОК АВТОНОМНОЙ СИНХРОНИЗАЦИИ ПАПКИ"""

assert old_settings_proj in text
text = text.replace(old_settings_proj, new_settings_update, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("index.html successfully armed with One-Click Update Engine for tftl308.github.io!")
