# -*- coding: utf-8 -*-
with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update renderSongDetailView to add Sheet Music & File Attachments Hub
target_str = "detailsBox.appendChild(notesFields);"
assert target_str in text, "target_str not found"

notes_attachments_code = """detailsBox.appendChild(notesFields);

    // ============================================================
    // ФАЙЛЫ, НОТЫ И МАРКИРОВКИ ПЕСНИ (Маска: ID_notes1, ID_mark...)
    // ============================================================
    const attachSection = Renderer.createElement('div', {
      className: 'mt-3 pt-3',
      style: 'border-top: 1px dashed var(--border-color);'
    });

    const attachHdr = Renderer.createElement('div', {
      className: 'flex items-center justify-between flex-wrap gap-2 mb-2'
    }, [
      Renderer.createElement('strong', { className: 'text-main text-sm' }, ['📄 Партитуры, ноты и схемы (ID_notes, ID_mark)']),
      Renderer.createElement('label', {
        className: 'btn btn-outline btn-sm',
        style: 'cursor: pointer; font-size: 0.8rem; padding: 0.25rem 0.6rem;'
      }, [
        '+ Добавить файл/ноты',
        Renderer.createElement('input', {
          type: 'file',
          multiple: true,
          accept: '.pdf,.png,.jpg,.jpeg,.webp,.docx,.txt',
          style: 'display: none;',
          dataset: { action: 'upload-song-attachments', songId: song.id }
        })
      ])
    ]);
    attachSection.appendChild(attachHdr);

    // Получаем прикрепленные файлы для этой песни из постоянного хранилища
    const storedAttachments = JSON.parse(localStorage.getItem('ov_attachments_' + normSongId) || '[]');
    const attachList = Renderer.createElement('div', {
      className: 'attachments-list flex flex-col gap-1',
      id: 'attachments-list-' + normSongId
    });

    if (storedAttachments.length === 0) {
      attachList.appendChild(Renderer.createElement('div', {
        className: 'text-xs text-muted py-1'
      }, ['Нет прикрепленных партитур или схем. Нажмите «+ Добавить файл/ноты» для загрузки PDF, фото нот или схем.']));
    } else {
      storedAttachments.forEach((att, attIdx) => {
        const itemRow = Renderer.createElement('div', {
          className: 'flex items-center justify-between p-2 rounded',
          style: 'background: rgba(0,0,0,0.03); border: 1px solid var(--border-color); font-size: 0.82rem;'
        }, [
          Renderer.createElement('div', { className: 'flex items-center gap-2 overflow-hidden' }, [
            Renderer.createElement('span', { style: 'font-size: 1.1rem;' }, [att.type.includes('pdf') ? '📑' : (att.type.includes('image') ? '🖼️' : '📄')]),
            Renderer.createElement('strong', { style: 'white-space: nowrap; overflow: hidden; text-overflow: ellipsis;' }, [att.name]),
            Renderer.createElement('span', { className: 'text-xs text-muted' }, [Math.round(att.size / 1024) + ' KB'])
          ]),
          Renderer.createElement('div', { className: 'flex items-center gap-1 flex-shrink-0' }, [
            Renderer.createElement('button', {
              className: 'btn btn-sm btn-outline',
              style: 'padding: 0.2rem 0.5rem; font-size: 0.75rem;',
              dataset: { action: 'open-song-attachment', songId: song.id, attachIndex: attIdx },
              title: 'Открыть / Просмотреть'
            }, ['Открыть']),
            Renderer.createElement('button', {
              className: 'btn btn-sm btn-outline text-muted',
              style: 'padding: 0.2rem 0.4rem; font-size: 0.75rem;',
              dataset: { action: 'delete-song-attachment', songId: song.id, attachIndex: attIdx },
              title: 'Удалить'
            }, ['✕'])
          ])
        ]);
        attachList.appendChild(itemRow);
      });
    }

    attachSection.appendChild(attachList);
    detailsBox.appendChild(attachSection);
"""

text = text.replace(target_str, notes_attachments_code, 1)

# 2. Add action handlers for file attachments in setupDelegatedEvents or handleAction
attach_handlers = """      case 'open-song-attachment': {
        const songId = el.dataset.songId;
        const normId = String(songId).padStart(4, '0');
        const attIdx = parseInt(el.dataset.attachIndex, 10);
        const stored = JSON.parse(localStorage.getItem('ov_attachments_' + normId) || '[]');
        const att = stored[attIdx];
        if (att && att.data) {
          const win = window.open();
          if (win) {
            win.document.write(`<html><head><title>${att.name}</title></head><body style="margin:0; background:#111; display:flex; justify-content:center; align-items:center; min-height:100vh;">
              ${att.type.includes('image') ? `<img src="${att.data}" style="max-width:100%; max-height:100vh;" />` : `<iframe src="${att.data}" style="width:100vw; height:100vh; border:none;"></iframe>`}
            </body></html>`);
          }
        }
        break;
      }

      case 'delete-song-attachment': {
        const songId = el.dataset.songId;
        const normId = String(songId).padStart(4, '0');
        const attIdx = parseInt(el.dataset.attachIndex, 10);
        let stored = JSON.parse(localStorage.getItem('ov_attachments_' + normId) || '[]');
        if (confirm(`Удалить файл «${stored[attIdx]?.name}»?`)) {
          stored.splice(attIdx, 1);
          localStorage.setItem('ov_attachments_' + normId, JSON.stringify(stored));
          AppController.showToast('Файл удален');
          const state = store.getState();
          Renderer.renderCurrentView(state);
        }
        break;
      }"""

pos_handle = text.find("switch (action) {")
assert pos_handle != -1
text = text[:pos_handle + len("switch (action) {")] + "\n" + attach_handlers + "\n" + text[pos_handle + len("switch (action) {"):]

# 3. Add change event listener for upload-song-attachments
change_handler = """      if (e.target.dataset.action === 'upload-song-attachments') {
        const files = Array.from(e.target.files);
        const songId = e.target.dataset.songId;
        const normId = String(songId).padStart(4, '0');
        if (files.length === 0) return;

        let stored = JSON.parse(localStorage.getItem('ov_attachments_' + normId) || '[]');

        for (const file of files) {
          const reader = new FileReader();
          reader.onload = () => {
            // Нормализация имени по маске ID_notes1, ID_mark... если имя не задано
            let assignedName = file.name;
            if (!assignedName.startsWith(normId)) {
              const ext = file.name.slice(file.name.lastIndexOf('.'));
              const markType = file.name.toLowerCase().includes('mark') ? 'mark' : 'notes';
              const nextIndex = stored.length + 1;
              assignedName = `${normId}_${markType}${nextIndex}${ext}`;
            }

            stored.push({
              name: assignedName,
              type: file.type || 'application/octet-stream',
              size: file.size,
              data: reader.result,
              uploaded_at: Date.now()
            });

            localStorage.setItem('ov_attachments_' + normId, JSON.stringify(stored));
            AppController.showToast(`Файл «${assignedName}» прикреплен к песне`);
            const state = store.getState();
            Renderer.renderCurrentView(state);
          };
          reader.readAsDataURL(file);
        }
        return;
      }"""

pos_change = text.find("document.addEventListener('change', (e) => {")
assert pos_change != -1
text = text[:pos_change + len("document.addEventListener('change', (e) => {")] + "\n" + change_handler + "\n" + text[pos_change + len("document.addEventListener('change', (e) => {"):]

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(text)

print('Notes & Sheets attachments engine successfully integrated!')
