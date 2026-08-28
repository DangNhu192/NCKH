/**
 * document-editor.js
 * ==================
 * Workspace File Manager & Interactive DOCX Content & Numerical Data Editor
 * WEB SUPER v3.2 / v2.0
 */

const DocEditor = {
  currentFile: null,
  files: [],
  selectedPaths: new Set(),
  currentCategory: "",
  searchQuery: "",
  activeSubtab: "text", // "text" | "tables" | "replace"
  parsedDocxData: null,
  batchReplacements: [
    { find: "", replace: "" }
  ],

  async loadFileList(category = null) {
    if (category !== null) {
      this.currentCategory = category;
    }
    
    document.querySelectorAll(".workspace-cat-btn").forEach(btn => {
      const cat = btn.getAttribute("data-cat") || "";
      if (cat === this.currentCategory) {
        btn.classList.add("active");
      } else {
        btn.classList.remove("active");
      }
    });

    const listContainer = document.getElementById("workspace-file-list");
    if (!listContainer) return;

    listContainer.innerHTML = `<p style="color: #94a3b8; font-size: 13px; padding: 12px 0;">Đang tải danh sách file...</p>`;

    try {
      const url = this.currentCategory ? `/api/files?category=${this.currentCategory}` : "/api/files";
      const res = await fetch(url, { headers: (window.AuthManager && AuthManager.token) ? { "Authorization": `Bearer ${AuthManager.token}` } : {} });
      const data = await res.json();
      this.files = Array.isArray(data) ? data : [];
      this.selectedPaths.clear();
      this.renderFileList();
    } catch (e) {
      listContainer.innerHTML = `<p style="color: #f87171; font-size: 13px;">Lỗi tải file: ${e.message}</p>`;
    }
  },

  onSearch(query) {
    this.searchQuery = (query || "").trim().toLowerCase();
    this.renderFileList();
  },

  getFilteredFiles() {
    if (!this.searchQuery) return this.files;
    return this.files.filter(f => 
      f.name.toLowerCase().includes(this.searchQuery) || 
      f.rel_path.toLowerCase().includes(this.searchQuery)
    );
  },

  toggleSelect(relPath, ev) {
    if (ev) ev.stopPropagation();
    if (this.selectedPaths.has(relPath)) {
      this.selectedPaths.delete(relPath);
    } else {
      this.selectedPaths.add(relPath);
    }
    this.renderFileList();
  },

  toggleSelectAll(checked) {
    const visibleFiles = this.getFilteredFiles();
    if (checked) {
      visibleFiles.forEach(f => this.selectedPaths.add(f.rel_path));
    } else {
      this.selectedPaths.clear();
    }
    this.renderFileList();
  },

  clearSelection() {
    this.selectedPaths.clear();
    this.renderFileList();
  },

  async deleteBatch() {
    const paths = Array.from(this.selectedPaths);
    if (paths.length === 0) {
      App.toast("Vui lòng chọn ít nhất 1 tệp để xóa.", "warning");
      return;
    }

    const previewNames = paths.slice(0, 5).map(p => ` • ${p.split('/').pop()}`).join('\n');
    const moreTxt = paths.length > 5 ? `\n ... và ${paths.length - 5} tệp khác.` : '';
    
    if (!confirm(`Bạn có chắc chắn muốn XÓA VĨNH VIỄN ${paths.length} tệp đã chọn sau đây?\n\n${previewNames}${moreTxt}\n\nHành động này không thể hoàn tác.`)) {
      return;
    }

    try {
      const res = await fetch("/api/files/batch-delete", {
        method: "POST",
        headers: { "Content-Type": "application/json", ...((window.AuthManager && AuthManager.token) ? { "Authorization": `Bearer ${AuthManager.token}` } : {}) },
        body: JSON.stringify({ paths })
      });
      const data = await res.json();
      if (data.deleted_count > 0 || data.success) {
        App.toast(`Đã xóa thành công ${data.deleted_count} tệp khỏi Workspace!`, "success");
        this.selectedPaths.clear();
        await this.loadFileList();
        App.updateStatus();
      } else {
        App.toast("Lỗi xóa tệp: " + (data.detail || "Không thể hoàn tất do tệp đang mở hoặc không tồn tại"), "error");
      }
    } catch (e) {
      App.toast("Lỗi kết nối khi xóa hàng loạt: " + e.message, "error");
    }
  },

  renderFileList() {
    const listContainer = document.getElementById("workspace-file-list");
    const bulkToolbar = document.getElementById("workspace-bulk-toolbar");
    const selectAllCheckbox = document.getElementById("workspace-select-all-checkbox");
    if (!listContainer) return;

    const visibleFiles = this.getFilteredFiles();
    const selectedCount = this.selectedPaths.size;
    const isAllSelected = visibleFiles.length > 0 && visibleFiles.every(f => this.selectedPaths.has(f.rel_path));

    if (selectAllCheckbox) {
      selectAllCheckbox.checked = isAllSelected;
      selectAllCheckbox.indeterminate = selectedCount > 0 && !isAllSelected;
    }

    if (bulkToolbar) {
      if (selectedCount > 0) {
        let totalBytes = 0;
        this.files.forEach(f => {
          if (this.selectedPaths.has(f.rel_path)) {
            totalBytes += (f.size || 0);
          }
        });
        const sizeStr = totalBytes > 1024 * 1024 
          ? `${(totalBytes / (1024 * 1024)).toFixed(2)} MB` 
          : `${(totalBytes / 1024).toFixed(1)} KB`;

        bulkToolbar.style.display = "flex";
        bulkToolbar.innerHTML = `
          <div style="display: flex; align-items: center; gap: 8px;">
            <span class="badge badge-blue" style="font-size: 11px;">Đã chọn ${selectedCount}/${visibleFiles.length} tệp</span>
            <span style="font-size: 11px; color: #94a3b8;">(${sizeStr})</span>
          </div>
          <div style="display: flex; gap: 6px;">
            <button class="btn btn-danger btn-sm" onclick="DocEditor.deleteBatch()" style="font-size: 11px; padding: 3px 10px; font-weight: 600;">
              🗑️ Xóa Đã Chọn (${selectedCount})
            </button>
            <button class="btn btn-secondary btn-sm" onclick="DocEditor.clearSelection()" style="font-size: 11px; padding: 3px 8px;">
              ✕ Bỏ chọn
            </button>
          </div>
        `;
      } else {
        bulkToolbar.style.display = "none";
        bulkToolbar.innerHTML = "";
      }
    }

    if (!visibleFiles || visibleFiles.length === 0) {
      listContainer.innerHTML = `
        <div style="text-align: center; padding: 32px 16px; background: rgba(30, 41, 59, 0.3); border-radius: 8px; border: 1px dashed var(--border-color); margin-top: 8px;">
          <span style="font-size: 28px; display: block; margin-bottom: 8px; opacity: 0.5;">📁</span>
          <p style="color: #94a3b8; font-size: 13px; margin: 0;">Chưa có tệp nào trong mục này hoặc không khớp tìm kiếm.</p>
        </div>
      `;
      return;
    }

    listContainer.innerHTML = visibleFiles.map(f => {
      const isSelected = this.selectedPaths.has(f.rel_path);
      let icon = "📄";
      if (f.extension === ".docx") icon = "📘";
      else if (f.extension === ".pdf") icon = "📕";
      else if (f.extension === ".json") icon = "📋";
      else if (f.extension === ".md") icon = "📝";

      return `
        <div class="file-item-row ${isSelected ? 'selected' : ''}" style="display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; background: ${isSelected ? 'rgba(59, 130, 246, 0.15)' : 'var(--bg-surface-elevated)'}; border-radius: 6px; margin-bottom: 6px; border: 1px solid ${isSelected ? 'rgba(59, 130, 246, 0.4)' : 'var(--border-color)'}; transition: all 0.15s ease;">
          <div style="display: flex; align-items: center; gap: 10px; flex: 1; min-width: 0;">
            <input type="checkbox" ${isSelected ? 'checked' : ''} onchange="DocEditor.toggleSelect('${f.rel_path}', event)" style="cursor: pointer; width: 15px; height: 15px;">
            <div style="display: flex; align-items: center; gap: 8px; cursor: pointer; flex: 1; min-width: 0;" onclick="DocEditor.loadFileDirect('${f.rel_path}')" title="Bấm để đọc hoặc chỉnh sửa nội dung/số liệu">
              <span style="font-size: 16px;">${icon}</span>
              <div style="min-width: 0; flex: 1;">
                <div style="font-size: 13px; font-weight: 600; color: #fff; text-overflow: ellipsis; overflow: hidden; white-space: nowrap;">${f.name}</div>
                <div style="font-size: 11px; color: #94a3b8;">${f.rel_path} • ${(f.size / 1024).toFixed(1)} KB • ${f.mtime}</div>
              </div>
            </div>
          </div>
          <div style="display: flex; gap: 6px; margin-left: 8px;">
            <button class="btn btn-primary btn-sm" onclick="DocEditor.loadFileDirect('${f.rel_path}')" title="Đọc & Chỉnh sửa số liệu" style="padding: 2px 8px; font-size: 11px;">✏️ Sửa</button>
            <a href="${f.file_url}" target="_blank" class="btn btn-secondary btn-sm" title="Tải xuống" style="padding: 2px 8px; font-size: 11px;">📥</a>
            <button class="btn btn-danger btn-sm" onclick="DocEditor.deleteFile('${f.rel_path}')" title="Xóa tệp này" style="padding: 2px 8px; font-size: 11px;">🗑️</button>
          </div>
        </div>
      `;
    }).join('');
  },

  async handleDocxUpload(file) {
    if (!file) return;
    if (!file.name.toLowerCase().endsWith(".docx")) {
      App.toast("Vui lòng tải lên tệp Microsoft Word (.docx)!", "warning");
      return;
    }

    App.toast(`Đang nạp và phân tích tệp: ${file.name}...`, "info");
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("/api/files/docx/upload-and-parse", {
        method: "POST",
        headers: (window.AuthManager && AuthManager.token) ? { "Authorization": `Bearer ${AuthManager.token}` } : {},
        body: formData
      });
      const data = await res.json();
      if (res.ok && data.success) {
        this.currentFile = { relPath: data.rel_path, ...data };
        this.parsedDocxData = data;
        App.toast(`✅ Đã bóc tách thành công ${data.metadata?.paragraph_count || 0} đoạn, ${data.metadata?.table_count || 0} bảng và ${data.metadata?.data_points_count || 0} số liệu!`, "success");
        this.renderEditorContent();
        this.loadFileList();
      } else {
        App.toast("Lỗi nạp tệp Word: " + (data.detail || "Không thể đọc file"), "error");
      }
    } catch (e) {
      App.toast("Lỗi kết nối upload: " + e.message, "error");
    }
  },

  async loadFileDirect(relPath) {
    App.switchTab("workspace-tab");
    App.toast(`Đang nạp file: ${relPath}...`, "info");

    const isDocx = relPath.toLowerCase().endsWith(".docx");

    try {
      if (isDocx) {
        const res = await fetch(`/api/files/docx/parse?path=${encodeURIComponent(relPath)}`);
        const data = await res.json();
        if (res.ok && data.success) {
          this.currentFile = { relPath, ...data };
          this.parsedDocxData = data;
          this.renderEditorContent();
          App.toast("Đã nạp tệp Word (.docx) vào Trình Biên Tập Số Liệu!", "success");
        } else {
          App.toast("Lỗi đọc tệp docx: " + (data.detail || "Không thể mở file"), "error");
        }
      } else {
        const res = await fetch(`/api/files/read?path=${encodeURIComponent(relPath)}`);
        const data = await res.json();
        this.currentFile = { relPath, ...data };
        this.parsedDocxData = null;
        this.renderEditorContent();
        App.toast("Đã nạp nội dung tệp vào trình soạn thảo!", "success");
      }
    } catch (e) {
      App.toast("Lỗi đọc file: " + e.message, "error");
    }
  },

  switchEditorSubtab(subtabId) {
    this.activeSubtab = subtabId;
    document.querySelectorAll(".doc-subtab-btn").forEach(btn => {
      if (btn.getAttribute("data-subtab") === subtabId) {
        btn.classList.add("active");
      } else {
        btn.classList.remove("active");
      }
    });

    const paneText = document.getElementById("doc-subtab-pane-text");
    const paneTables = document.getElementById("doc-subtab-pane-tables");
    const paneReplace = document.getElementById("doc-subtab-pane-replace");

    if (paneText) paneText.style.display = subtabId === "text" ? "block" : "none";
    if (paneTables) paneTables.style.display = subtabId === "tables" ? "block" : "none";
    if (paneReplace) paneReplace.style.display = subtabId === "replace" ? "block" : "none";
  },

  renderEditorContent() {
    const nameEl = document.getElementById("editor-current-filename");
    const metaBadge = document.getElementById("editor-metadata-badge");
    const areaEl = document.getElementById("editor-content-area");

    if (nameEl) nameEl.innerText = this.currentFile?.relPath || "Chưa chọn file";

    if (this.parsedDocxData) {
      const meta = this.parsedDocxData.metadata || {};
      if (metaBadge) {
        metaBadge.innerHTML = `
          <span class="badge badge-blue" style="font-size: 11px;">📝 ${meta.word_count || 0} từ</span>
          <span class="badge badge-purple" style="font-size: 11px;">📑 ${meta.paragraph_count || 0} đoạn</span>
          <span class="badge badge-green" style="font-size: 11px;">📊 ${meta.table_count || 0} bảng</span>
          <span class="badge badge-yellow" style="font-size: 11px;">🔢 ${meta.data_points_count || 0} số liệu</span>
        `;
      }
      if (areaEl) areaEl.value = this.parsedDocxData.full_text || this.parsedDocxData.raw_text || "";
      this.renderTablesAndDataPane();
      this.renderBatchReplacePane();
    } else {
      if (metaBadge) metaBadge.innerHTML = "";
      if (areaEl) areaEl.value = this.currentFile?.content || "";
    }
  },

  renderTablesAndDataPane() {
    const container = document.getElementById("doc-subtab-pane-tables");
    if (!container || !this.parsedDocxData) return;

    const tables = this.parsedDocxData.tables || [];
    const metrics = this.parsedDocxData.extracted_data_points || [];

    let html = `
      <div style="display: flex; flex-direction: column; gap: 16px;">
        <!-- Extracted Metrics Quick-Editor Card -->
        <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 8px; padding: 14px;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <h5 style="color: #38bdf8; font-size: 13px; margin: 0; font-weight: 700;">
              🔢 Chỉ Số Định Lượng & Số Liệu Trích Xuất (${metrics.length} số liệu):
            </h5>
            <span style="font-size: 11px; color: #94a3b8;">Bấm vào giá trị để chỉnh sửa hoặc thay thế</span>
          </div>
          <div style="max-height: 180px; overflow-y: auto; display: flex; flex-direction: column; gap: 6px;">
            ${metrics.map(m => `
              <div style="display: flex; justify-content: space-between; align-items: center; background: rgba(255,255,255,0.03); padding: 6px 10px; border-radius: 6px; font-size: 12px;">
                <div style="flex: 1; margin-right: 8px;">
                  <span class="badge badge-blue" style="font-size: 10.5px;">${m.location}</span>
                  <span style="color: #cbd5e1; margin-left: 6px;">${m.context}</span>
                </div>
                <button type="button" class="btn btn-secondary btn-sm" onclick="DocEditor.fillReplaceInput('${m.value.replace(/'/g, "\\'")}')" style="padding: 2px 8px; font-size: 11px; font-weight: 700; color: #fbbf24;">
                  ${m.value} ✏️
                </button>
              </div>
            `).join('')}
          </div>
        </div>

        <!-- Editable Tables List -->
        ${tables.map((t, tIdx) => `
          <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 14px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
              <h5 style="color: #f8fafc; font-size: 13px; margin: 0; font-weight: 700;">
                📊 ${t.title} (${t.row_count} hàng x ${t.col_count} cột)
              </h5>
            </div>
            <div style="overflow-x: auto;">
              <table style="width: 100%; border-collapse: collapse; font-size: 12px;">
                <tbody>
                  ${t.rows.map((r, rIdx) => `
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.05); background: ${rIdx === 0 ? 'rgba(59,130,246,0.15)' : 'transparent'};">
                      ${r.map((c, cIdx) => `
                        <td style="padding: 6px 8px; border: 1px solid rgba(255,255,255,0.08);">
                          <input type="text" 
                                 class="form-control docx-cell-input" 
                                 data-table="${tIdx}" 
                                 data-row="${rIdx}" 
                                 data-col="${cIdx}" 
                                 value="${c.replace(/"/g, '&quot;')}" 
                                 onchange="DocEditor.updateTableCell(${tIdx}, ${rIdx}, ${cIdx}, this.value)"
                                 style="font-size: 11.5px; padding: 4px 6px; background: rgba(0,0,0,0.3); color: #fff; width: 100%; font-weight: ${rIdx === 0 ? '700' : 'normal'};">
                        </td>
                      `).join('')}
                    </tr>
                  `).join('')}
                </tbody>
              </table>
            </div>
          </div>
        `).join('')}
      </div>
    `;

    container.innerHTML = html;
  },

  updateTableCell(tableIdx, rowIdx, colIdx, newVal) {
    if (this.parsedDocxData && this.parsedDocxData.tables && this.parsedDocxData.tables[tableIdx]) {
      this.parsedDocxData.tables[tableIdx].rows[rowIdx][colIdx] = newVal;
      App.toast(`Đã cập nhật ô [${rowIdx + 1}, ${colIdx + 1}] Bảng ${tableIdx + 1}`, "info");
    }
  },

  renderBatchReplacePane() {
    const container = document.getElementById("doc-subtab-pane-replace");
    if (!container) return;

    container.innerHTML = `
      <div style="background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 8px; padding: 16px;">
        <h5 style="color: #38bdf8; font-size: 13.5px; margin: 0 0 10px; font-weight: 700;">
          🔍 Tìm & Thay Thế Hàng Loạt Số Liệu / Thuật Ngữ Trong File Word:
        </h5>
        <p style="font-size: 12px; color: #94a3b8; margin-bottom: 12px;">
          Tự động tìm kiếm và thay thế chính xác trong tất cả các đoạn văn, tiêu đề và bảng biểu của tệp Word (.docx):
        </p>

        <div id="batch-replace-rows-container" style="display: flex; flex-direction: column; gap: 8px; margin-bottom: 12px;">
          ${this.batchReplacements.map((rep, idx) => `
            <div style="display: flex; gap: 8px; align-items: center;">
              <input type="text" class="form-control rep-find-input" placeholder="Giá trị / Số liệu cũ..." value="${rep.find.replace(/"/g, '&quot;')}" style="flex: 1; font-size: 12px; padding: 6px 10px;">
              <span style="color: #60a5fa; font-weight: 700;">➔</span>
              <input type="text" class="form-control rep-replace-input" placeholder="Giá trị / Số liệu mới..." value="${rep.replace.replace(/"/g, '&quot;')}" style="flex: 1; font-size: 12px; padding: 6px 10px;">
              <button type="button" class="btn btn-secondary btn-sm" onclick="DocEditor.removeReplaceRow(${idx})" style="padding: 4px 8px; color: #f87171;">✕</button>
            </div>
          `).join('')}
        </div>

        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
          <button type="button" class="btn btn-secondary btn-sm" onclick="DocEditor.addReplaceRow()">+ Thêm Cặp Giá Trị</button>
          <button type="button" class="btn btn-primary btn-sm" onclick="DocEditor.applyBatchReplace()" style="font-weight: 700;">
            ⚡ Áp Dụng Thay Thế Toàn Bộ File
          </button>
        </div>
      </div>
    `;
  },

  addReplaceRow() {
    this.batchReplacements.push({ find: "", replace: "" });
    this.renderBatchReplacePane();
  },

  removeReplaceRow(idx) {
    this.batchReplacements.splice(idx, 1);
    if (this.batchReplacements.length === 0) this.batchReplacements.push({ find: "", replace: "" });
    this.renderBatchReplacePane();
  },

  fillReplaceInput(value) {
    this.switchEditorSubtab("replace");
    if (this.batchReplacements.length > 0) {
      this.batchReplacements[0].find = value;
    } else {
      this.batchReplacements.push({ find: value, replace: "" });
    }
    this.renderBatchReplacePane();
    App.toast(`Đã đưa giá trị "${value}" vào ô tìm kiếm thay thế.`, "info");
  },

  async applyBatchReplace() {
    if (!this.currentFile) {
      App.toast("Chưa chọn file Word để thực hiện thay thế.", "warning");
      return;
    }

    const findInputs = document.querySelectorAll(".rep-find-input");
    const replaceInputs = document.querySelectorAll(".rep-replace-input");
    const replacements = [];

    findInputs.forEach((fIn, idx) => {
      const fVal = fIn.value.trim();
      const rVal = replaceInputs[idx]?.value?.trim() || "";
      if (fVal) {
        replacements.push({ find: fVal, replace: rVal });
      }
    });

    if (replacements.length === 0) {
      App.toast("Vui lòng nhập ít nhất 1 cặp giá trị cần tìm và thay thế.", "warning");
      return;
    }

    App.toast("Đang áp dụng thay thế hàng loạt vào tệp Word...", "info");

    try {
      const res = await fetch("/api/files/docx/batch-replace", {
        method: "POST",
        headers: { "Content-Type": "application/json", ...((window.AuthManager && AuthManager.token) ? { "Authorization": `Bearer ${AuthManager.token}` } : {}) },
        body: JSON.stringify({
          rel_path: this.currentFile.relPath,
          replacements: replacements
        })
      });
      const data = await res.json();
      if (res.ok && data.success) {
        App.toast(`🎉 Thành công! Đã thay thế ${data.total_replacements} vị trí trong tệp Word.`, "success");
        await this.loadFileDirect(this.currentFile.relPath);
      } else {
        App.toast("Lỗi thay thế: " + (data.detail || "Không thể thực hiện"), "error");
      }
    } catch (e) {
      App.toast("Lỗi kết nối: " + e.message, "error");
    }
  },

  async saveCurrentFile() {
    if (!this.currentFile) {
      App.toast("Chưa chọn file để lưu.", "warning");
      return;
    }

    const content = document.getElementById("editor-content-area")?.value || "";
    const format = document.getElementById("editor-save-format")?.value || "docx";
    const relPath = this.currentFile.relPath;

    App.toast(`Đang lưu tệp: ${relPath}...`, "info");

    try {
      if (relPath.toLowerCase().endsWith(".docx") || format === "docx") {
        const res = await fetch("/api/files/docx/save", {
          method: "POST",
          headers: { "Content-Type": "application/json", ...((window.AuthManager && AuthManager.token) ? { "Authorization": `Bearer ${AuthManager.token}` } : {}) },
          body: JSON.stringify({
            rel_path: relPath,
            content_text: content,
            tables: this.parsedDocxData?.tables || null
          })
        });
        const data = await res.json();
        if (res.ok && data.success) {
          App.toast("✅ Đã lưu tệp Word (.docx) thành công với cấu trúc In-Place DOM!", "success");
          this.loadFileList();
        } else {
          App.toast("Lỗi lưu file .docx: " + (data.detail || "Lỗi lưu"), "error");
        }
      } else {
        const res = await fetch("/api/files/save", {
          method: "POST",
          headers: { "Content-Type": "application/json", ...((window.AuthManager && AuthManager.token) ? { "Authorization": `Bearer ${AuthManager.token}` } : {}) },
          body: JSON.stringify({
            rel_path: relPath,
            content: content,
            file_format: format
          })
        });
        const data = await res.json();
        if (data.success) {
          App.toast("Đã lưu file thành công!", "success");
          this.loadFileList();
        }
      }
    } catch (e) {
      App.toast("Lỗi lưu file: " + e.message, "error");
    }
  },

  async deleteFile(relPath) {
    if (!confirm(`Bạn có chắc chắn muốn xóa file: ${relPath}?`)) return;

    try {
      const res = await fetch(`/api/files/delete?path=${encodeURIComponent(relPath)}`, {
        method: "DELETE",
        headers: (window.AuthManager && AuthManager.token) ? { "Authorization": `Bearer ${AuthManager.token}` } : {}
      });
      const data = await res.json();
      if (res.ok && data.success) {
        App.toast("Đã xóa file thành công!", "success");
        this.selectedPaths.delete(relPath);
        this.loadFileList();
        App.updateStatus();
        if (this.currentFile && this.currentFile.relPath === relPath) {
          document.getElementById("editor-current-filename").innerText = "Chưa chọn file";
          document.getElementById("editor-content-area").value = "";
          this.currentFile = null;
        }
      } else {
        App.toast("Lỗi xóa file: " + (data.detail || data.message || "Không thể xóa tệp"), "error");
      }
    } catch (e) {
      App.toast("Lỗi xóa file: " + e.message, "error");
    }
  }
};

window.DocEditor = DocEditor;
