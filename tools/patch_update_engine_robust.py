import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update saveSetting for db_initialized and app_version_meta on initial load
boot_pattern = """          await storage.saveBatch('songs', songs);
          AppLogger.info('BOOT', 'Каталог успешно инициализирован: ' + songs.length + ' песен.');"""

boot_replacement = """          await storage.saveBatch('songs', songs);
          AppLogger.info('BOOT', 'Каталог успешно инициализирован: ' + songs.length + ' песен.');
          try {
            const vRes = await fetch('./data/version.json?_t=' + Date.now(), { cache: 'no-store' });
            if (vRes.ok) {
              const vData = await vRes.json();
              await storage.saveSetting('app_version_meta', vData);
            }
          } catch(e) {}"""

assert boot_pattern in html, "boot_pattern not found"
html = html.replace(boot_pattern, boot_replacement)

# 2. Fix static async applyFullUpdate: replace storage.setSetting with storage.saveSetting
# and add rich logging
update_old = """      // Сохраняем новую версию метаданных в IndexedDB
      await storage.setSetting('app_version_meta', info.remote);
      await storage.setSetting('db_initialized', true);

      if (statusEl) statusEl.textContent = '4/4. ✓ Успешно обновлено! Перезагрузка...';
      setTimeout(() => {
        window.location.reload();
      }, 800);
    } catch(err) {
      if (statusEl) statusEl.textContent = 'Ошибка обновления: ' + err.message;
      if (updateBtn) updateBtn.disabled = false;
    }"""

update_new = """      // Сохраняем новую версию метаданных в IndexedDB
      await storage.saveSetting('app_version_meta', info.remote);
      await storage.saveSetting('db_initialized', 'true');
      AppLogger.info('UPDATE', 'Обновление базы успешно завершено: ' + (info.remote.app_build || 'v4.1.0'));

      if (statusEl) statusEl.textContent = '4/4. ✓ Успешно обновлено! Перезагрузка...';
      setTimeout(() => {
        window.location.reload();
      }, 800);
    } catch(err) {
      AppLogger.error('UPDATE', 'Ошибка обновления: ' + err.message);
      if (statusEl) statusEl.textContent = 'Ошибка обновления: ' + err.message;
      if (updateBtn) updateBtn.disabled = false;
    }"""

assert update_old in html, "update_old not found"
html = html.replace(update_old, update_new)

# 3. Add detailed logging to checkForUpdates
check_old = """      const result = {
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

      return result;"""

check_new = """      const result = {
        available: hasNewBuild || needsData,
        remote,
        local,
        needsApp: hasNewBuild,
        needsData: needsData
      };

      AppLogger.info('UPDATE', `Сверка версии: local=${local.app_build} remote=${remote.app_build} (доступно: ${result.available})`);

      if (result.available) {
        UpdateEngine.renderHeaderBadge(result);
        if (isManual) {
          UpdateEngine.showUpdateModal(result);
        }
      } else if (isManual) {
        AppController.showToast('✓ У вас установлена самая свежая версия программы и песен!');
      }

      return result;"""

assert check_old in html, "check_old not found"
html = html.replace(check_old, check_new)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("index.html successfully patched with robust update logging and correct storage.saveSetting!")
