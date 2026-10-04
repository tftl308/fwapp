# -*- coding: utf-8 -*-
with open('src/runtime-dualtrack.js', 'r', encoding='utf-8') as f:
    runtime_js = f.read()

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Inject runtime classes before class StorageRepository
marker = "class StorageRepository {"
assert marker in html, "Marker not found"

injected_runtime = runtime_js + """
// Dual-Track Global Singletons (v4.0.0)
const globalStorageAdapter = new StorageAdapter();
if (typeof window !== 'undefined') {
  globalStorageAdapter.init().catch(console.warn);
}
const globalSyncEngine = new SyncEngine(globalStorageAdapter);

"""

html = html.replace(marker, injected_runtime + marker)

# 2. Update AudioPlayerService to resolve URL through StorageAdapter (OPFS / Native)
pos_resolve = html.find('const storedBlob = await storage.getAudioBlob(fname);')
assert pos_resolve != -1, "pos_resolve not found"
block_start = html.rfind('if (!resolvedUrl && fname) {', 0, pos_resolve)
block_end = html.find('}', html.find('catch(e) {}', pos_resolve)) + 1

old_player_block = html[block_start:block_end]
new_player_block = """if (!resolvedUrl && fname) {
      try {
        const storageUrl = await globalStorageAdapter.getAudioUrl(fname);
        if (storageUrl) {
          resolvedUrl = storageUrl;
          AppLogger.info('PLAYER', 'Воспроизведение через StorageAdapter (OPFS/Native): ' + fname);
        }
      } catch(e) {
        console.warn('StorageAdapter getAudioUrl error:', e);
      }
    }"""

html = html[:block_start] + new_player_block + html[block_end:]

# 3. Add Sync Modal UI before closing </body>
sync_modal_html = """
  <!-- Dual-Track Manifest Sync Modal -->
  <div id="modal-sync-progress" class="modal-backdrop" style="display: none; align-items: center; justify-content: center; z-index: 10000; position: fixed; inset: 0; background: rgba(0,0,0,0.65);">
    <div style="background: var(--bg-card, #ffffff); border-radius: 12px; padding: 1.5rem; width: 90%; max-width: 440px; box-shadow: 0 10px 25px rgba(0,0,0,0.3); text-align: center;">
      <h3 style="margin-bottom: 0.5rem; font-size: 1.2rem;">🔄 Синхронизация фонограмм</h3>
      <p id="sync-status-phase" style="font-size: 0.85rem; color: var(--text-muted, #64748b); margin-bottom: 1rem;">Проверка релизного манифеста...</p>
      
      <div style="background: #e2e8f0; border-radius: 999px; height: 12px; overflow: hidden; margin-bottom: 0.8rem;">
        <div id="sync-progress-bar" style="background: #b45309; height: 100%; width: 0%; transition: width 0.2s;"></div>
      </div>
      
      <div style="display: flex; justify-content: space-between; font-size: 0.78rem; color: var(--text-muted, #64748b); margin-bottom: 1rem;">
        <span id="sync-file-counter">0 / 0 файлов</span>
        <span id="sync-size-counter">0 MB</span>
      </div>

      <p id="sync-current-file" style="font-size: 0.75rem; color: #b45309; font-family: monospace; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-bottom: 1.2rem;">—</p>
      
      <button type="button" class="btn btn-outline" id="btn-close-sync-modal" style="width: 100%; display: none;">Готово</button>
    </div>
  </div>
"""

html = html.replace('</body>', sync_modal_html + '\n</body>')

# 4. Add sync action handler in AppController
old_batch_upload_handler = """      case 'trigger-audio-batch-upload': {
        // Запуск физической синхронизации папки проекта без хардкода
        const syncBtn = document.querySelector('[data-action="sync-entire-project-folder"]');
        if (syncBtn) {
          syncBtn.click();
        } else {
          const fInput = document.getElementById('input-sync-project-folder');
          if (fInput) fInput.click();
        }
        break;
      }"""

new_batch_upload_handler = """      case 'trigger-audio-batch-upload': {
        // Запуск атомарной синхронизации Dual-Track через SyncEngine (OPFS / Native)
        AppController.startMediaSyncWorkflow();
        break;
      }"""

assert old_batch_upload_handler in html, "old_batch_upload_handler not matched"
html = html.replace(old_batch_upload_handler, new_batch_upload_handler)

# 5. Add startMediaSyncWorkflow method to AppController
workflow_code = """
  static async startMediaSyncWorkflow() {
    const modal = document.getElementById('modal-sync-progress');
    const phaseEl = document.getElementById('sync-status-phase');
    const barEl = document.getElementById('sync-progress-bar');
    const fileCountEl = document.getElementById('sync-file-counter');
    const sizeEl = document.getElementById('sync-size-counter');
    const currentFileEl = document.getElementById('sync-current-file');
    const closeBtn = document.getElementById('btn-close-sync-modal');

    if (modal) modal.style.display = 'flex';
    if (closeBtn) {
      closeBtn.style.display = 'none';
      closeBtn.onclick = () => { modal.style.display = 'none'; };
    }

    try {
      if (phaseEl) phaseEl.textContent = 'Получение манифеста (manifest.json)...';
      const manifest = await globalSyncEngine.fetchManifest();

      const result = await globalSyncEngine.synchronize(manifest, (progress) => {
        if (barEl) {
          const pct = progress.total > 0 ? Math.round((progress.completed / progress.total) * 100) : 0;
          barEl.style.width = pct + '%';
        }
        if (fileCountEl) fileCountEl.textContent = `${progress.completed} / ${progress.total} файлов`;
        if (sizeEl) {
          const mb = (progress.bytesLoaded / (1024 * 1024)).toFixed(1);
          const totalMb = (progress.bytesTotal / (1024 * 1024)).toFixed(1);
          sizeEl.textContent = `${mb} / ${totalMb} MB`;
        }
        if (currentFileEl) currentFileEl.textContent = progress.currentFile || '—';

        if (phaseEl) {
          if (progress.phase === 'checking') phaseEl.textContent = 'Проверка локального хранилища OPFS/Native...';
          else if (progress.phase === 'downloading') phaseEl.textContent = 'Загрузка и проверка SHA-256...';
          else if (progress.phase === 'gc') phaseEl.textContent = 'Очистка устаревших треков (GC)...';
          else if (progress.phase === 'done') phaseEl.textContent = 'Синхронизация успешно завершена!';
        }
      });

      if (phaseEl) phaseEl.textContent = `✓ Готово: загружено ${result.added}, проверено ${result.verified}, удалено устаревших ${result.deleted}`;
      if (closeBtn) closeBtn.style.display = 'block';
      AppController.showToast('Медиатека синхронизирована!');
    } catch (err) {
      if (phaseEl) phaseEl.textContent = 'Ошибка: ' + err.message;
      if (closeBtn) closeBtn.style.display = 'block';
      console.error('Media sync error:', err);
    }
  }
"""

pos_ctrl = html.find('class AppController {')
assert pos_ctrl != -1, "AppController not found"
html = html[:pos_ctrl + len('class AppController {')] + workflow_code + html[pos_ctrl + len('class AppController {'):]

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("index.html successfully updated with Dual-Track Sync Engine and StorageAdapter!")
