// History & Session Manager (Quản Lý Phiên Thao Tác, Chọn Nhiều & Xóa Hàng Loạt, Khôi Phục)
const HistoryUI = {
  viewMode: "session", // "session" | "flat"
  sessions: [],
  historyRecords: [],
  activeSession: null,
  currentFilter: "all",
  searchQuery: "",
  selectedSessionIds: new Set(),
  selectedEntryIds: new Set(),
  expandedSessionIds: new Set(),
  expandedItemIds: new Set(),

  async init() {
    await this.loadHistory();
  },

  async loadHistory() {
    try {
      if (this.viewMode === "session") {
        const url = `/api/history/sessions?limit=100&module=${encodeURIComponent(this.currentFilter)}&query=${encodeURIComponent(this.searchQuery)}`;
        const res = await fetch(url, { headers: (window.AuthManager && AuthManager.token) ? { "Authorization": `Bearer ${AuthManager.token}` } : {} });
        const data = await res.json();
        if (data.status === "success") {
          this.sessions = data.sessions || [];
          this.activeSession = data.active_session || null;
          // Auto expand the first session by default
          if (this.sessions.length > 0 && this.expandedSessionIds.size === 0) {
            this.expandedSessionIds.add(this.sessions[0].session_id);
          }
          this.renderActiveSessionBanner();
          this.renderBulkToolbar();
          this.renderHistoryList();

          let totalCount = 0;
          this.sessions.forEach(s => totalCount += (s.actions_count || 0));
          this.updateBadgeCount(totalCount);
        }
      } else {
        const url = `/api/history?limit=200&module=${encodeURIComponent(this.currentFilter)}&query=${encodeURIComponent(this.searchQuery)}`;
        const res = await fetch(url, { headers: (window.AuthManager && AuthManager.token) ? { "Authorization": `Bearer ${AuthManager.token}` } : {} });
        const data = await res.json();
        if (data.status === "success") {
          this.historyRecords = data.entries || data.history || [];
          this.renderActiveSessionBanner();
          this.renderBulkToolbar();
          this.renderHistoryList();
          this.updateBadgeCount(data.total || this.historyRecords.length);
        }
      }
    } catch (e) {
      console.warn("Lỗi tải lịch sử thao tác:", e);
    }
  },

  updateBadgeCount(count) {
    const badge = document.getElementById("history-badge-count");
    if (badge) {
      badge.innerText = count || 0;
      badge.style.display = (count > 0) ? "inline-block" : "none";
    }
  },

  switchViewMode(mode) {
    this.viewMode = mode;
    const btnSess = document.getElementById("btn-view-mode-session");
    const btnFlat = document.getElementById("btn-view-mode-flat");
    if (btnSess) {
      if (mode === "session") btnSess.classList.add("active");
      else btnSess.classList.remove("active");
    }
    if (btnFlat) {
      if (mode === "flat") btnFlat.classList.add("active");
      else btnFlat.classList.remove("active");
    }
    this.selectedSessionIds.clear();
    this.selectedEntryIds.clear();
    this.loadHistory();
  },

  filterByModule(mod) {
    this.currentFilter = mod;
    const filterBtns = document.querySelectorAll(".history-filter-btn");
    filterBtns.forEach(btn => {
      if (btn.getAttribute("data-module") === mod) {
        btn.classList.add("active");
      } else {
        btn.classList.remove("active");
      }
    });
    this.selectedSessionIds.clear();
    this.selectedEntryIds.clear();
    this.loadHistory();
  },

  onSearch(query) {
    this.searchQuery = query.trim();
    this.selectedSessionIds.clear();
    this.selectedEntryIds.clear();
    this.loadHistory();
  },

  renderActiveSessionBanner() {
    const banner = document.getElementById("history-active-session-banner");
    if (!banner) return;

    if (!this.activeSession) {
      banner.style.display = "none";
      return;
    }

    banner.style.display = "flex";
    banner.innerHTML = `
      <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
        <span style="font-size: 16px;">🚀</span>
        <div>
          <span style="color: #94a3b8; font-size: 11px;">Phiên đang hoạt động:</span>
          <strong style="color: #60a5fa; font-size: 13px; margin-left: 4px;">${this.activeSession.session_title || 'Phiên làm việc hiện tại'}</strong>
          <span style="font-size: 10px; color: #34d399; margin-left: 8px;">● Sẵn sàng ghi nhận tác vụ mới</span>
        </div>
      </div>
      <div style="display: flex; gap: 6px; align-items: center;">
        <button class="btn btn-secondary btn-sm" onclick="HistoryUI.renameSessionPrompt('${this.activeSession.session_id}', '${(this.activeSession.session_title || '').replace(/'/g, "\\'")}')" style="font-size: 11px; padding: 2px 8px;">
          ✏️ Đổi tên phiên
        </button>
        <button class="btn btn-secondary btn-sm" onclick="HistoryUI.createNewSessionPrompt()" style="font-size: 11px; padding: 2px 8px; color: #38bdf8;">
          ➕ Phiên mới
        </button>
      </div>
    `;
  },

  renderBulkToolbar() {
    const toolbar = document.getElementById("history-bulk-toolbar");
    if (!toolbar) return;

    const isSessionMode = this.viewMode === "session";
    let totalItems = 0;
    let selectedCount = 0;
    let isAllSelected = false;

    if (isSessionMode) {
      totalItems = this.sessions.length;
      selectedCount = this.selectedSessionIds.size;
      isAllSelected = totalItems > 0 && selectedCount === totalItems;
    } else {
      totalItems = this.historyRecords.length;
      selectedCount = this.selectedEntryIds.size;
      isAllSelected = totalItems > 0 && selectedCount === totalItems;
    }

    if (totalItems === 0) {
      toolbar.style.display = "none";
      return;
    }

    toolbar.style.display = "flex";
    toolbar.innerHTML = `
      <div style="display: flex; align-items: center; gap: 12px;">
        <label style="display: flex; align-items: center; gap: 8px; cursor: pointer; color: #cbd5e1; font-weight: 500; margin: 0;">
          <input type="checkbox" id="history-master-checkbox" ${isAllSelected ? 'checked' : ''} onchange="HistoryUI.toggleSelectAll(this.checked)" style="cursor: pointer; width: 15px; height: 15px;">
          <span>Chọn tất cả (${totalItems} ${isSessionMode ? 'phiên' : 'thao tác'})</span>
        </label>
        ${selectedCount > 0 ? `
          <span class="badge badge-blue" style="font-size: 11px;">
            Đã chọn ${selectedCount} ${isSessionMode ? 'phiên' : 'thao tác'}
          </span>
        ` : ''}
      </div>

      <div style="display: flex; gap: 8px; align-items: center;">
        ${selectedCount > 0 ? `
          <button class="btn btn-danger btn-sm" onclick="HistoryUI.deleteSelectedBatch()" style="font-weight: 600; font-size: 11px; padding: 4px 12px;">
            🗑️ Xóa Các Mục Đã Chọn (${selectedCount})
          </button>
          <button class="btn btn-secondary btn-sm" onclick="HistoryUI.clearSelection()" style="font-size: 11px; padding: 4px 8px;">
            ✕ Bỏ chọn
          </button>
        ` : `
          <span style="font-size: 11px; color: #94a3b8;">💡 Tích chọn để xóa nhiều mục cùng lúc</span>
        `}
      </div>
    `;

    const masterCheckbox = document.getElementById("history-master-checkbox");
    if (masterCheckbox) {
      masterCheckbox.indeterminate = selectedCount > 0 && !isAllSelected;
    }
  },

  toggleSelectAll(checked) {
    if (this.viewMode === "session") {
      if (checked) {
        this.sessions.forEach(s => {
          this.selectedSessionIds.add(s.session_id);
          (s.actions || []).forEach(a => this.selectedEntryIds.add(a.id));
        });
      } else {
        this.selectedSessionIds.clear();
        this.selectedEntryIds.clear();
      }
    } else {
      if (checked) {
        this.historyRecords.forEach(e => this.selectedEntryIds.add(e.id));
      } else {
        this.selectedEntryIds.clear();
      }
    }
    this.renderBulkToolbar();
    this.renderHistoryList();
  },

  clearSelection() {
    this.selectedSessionIds.clear();
    this.selectedEntryIds.clear();
    this.renderBulkToolbar();
    this.renderHistoryList();
  },

  toggleSessionSelect(sessionId, ev) {
    if (ev) ev.stopPropagation();
    const session = this.sessions.find(s => s.session_id === sessionId);
    if (this.selectedSessionIds.has(sessionId)) {
      this.selectedSessionIds.delete(sessionId);
      if (session) {
        (session.actions || []).forEach(a => this.selectedEntryIds.delete(a.id));
      }
    } else {
      this.selectedSessionIds.add(sessionId);
      if (session) {
        (session.actions || []).forEach(a => this.selectedEntryIds.add(a.id));
      }
    }
    this.renderBulkToolbar();
    this.renderHistoryList();
  },

  toggleEntrySelect(entryId, ev) {
    if (ev) ev.stopPropagation();
    if (this.selectedEntryIds.has(entryId)) {
      this.selectedEntryIds.delete(entryId);
    } else {
      this.selectedEntryIds.add(entryId);
    }
    this.renderBulkToolbar();
    this.renderHistoryList();
  },

  toggleSessionExpand(sessionId) {
    if (this.expandedSessionIds.has(sessionId)) {
      this.expandedSessionIds.delete(sessionId);
    } else {
      this.expandedSessionIds.add(sessionId);
    }
    this.renderHistoryList();
  },

  toggleDetails(entryId) {
    if (this.expandedItemIds.has(entryId)) {
      this.expandedItemIds.delete(entryId);
    } else {
      this.expandedItemIds.add(entryId);
    }
    this.renderHistoryList();
  },

  copyJson(entryId) {
    let entry = null;
    if (this.viewMode === "session") {
      for (const s of this.sessions) {
        const found = (s.actions || []).find(a => a.id === entryId);
        if (found) { entry = found; break; }
      }
    } else {
      entry = this.historyRecords.find(e => e.id === entryId);
    }

    if (!entry) return;
    const jsonStr = JSON.stringify(entry, null, 2);
    navigator.clipboard.writeText(jsonStr).then(() => {
      App.toast("📋 Đã sao chép toàn bộ JSON dữ liệu của bản ghi!", "success");
    }).catch(() => {
      App.toast("Không thể sao chép tự động.", "warning");
    });
  },

  async createNewSessionPrompt() {
    const title = prompt("Nhập tên hoặc đề tài cho Phiên Nghiên Cứu Mới:", "Nghiên cứu mới");
    if (title === null) return;

    try {
      const res = await fetch("/api/history/sessions", {
        method: "POST",
        headers: { "Content-Type": "application/json", ...((window.AuthManager && AuthManager.token) ? { "Authorization": `Bearer ${AuthManager.token}` } : {}) },
        body: JSON.stringify({ title: title.trim(), topic: title.trim() })
      });
      const data = await res.json();
      if (data.status === "success") {
        App.toast(`Đã khởi tạo "${data.session.session_title}" thành công!`, "success");
        this.expandedSessionIds.add(data.session.session_id);
        await this.loadHistory();
      }
    } catch (e) {
      App.toast("Lỗi tạo phiên: " + e.message, "error");
    }
  },

  async renameSessionPrompt(sessionId, currentTitle) {
    const newTitle = prompt("Đổi tên phiên làm việc:", currentTitle);
    if (!newTitle || newTitle.trim() === currentTitle) return;

    try {
      const res = await fetch("/api/history/sessions/rename", {
        method: "POST",
        headers: { "Content-Type": "application/json", ...((window.AuthManager && AuthManager.token) ? { "Authorization": `Bearer ${AuthManager.token}` } : {}) },
        body: JSON.stringify({ session_id: sessionId, title: newTitle.trim() })
      });
      const data = await res.json();
      if (data.status === "success") {
        App.toast("Đã đổi tên phiên làm việc!", "success");
        await this.loadHistory();
      }
    } catch (e) {
      App.toast("Lỗi đổi tên phiên: " + e.message, "error");
    }
  },

  async switchActiveSession(sessionId) {
    try {
      const res = await fetch("/api/history/sessions/active", {
        method: "POST",
        headers: { "Content-Type": "application/json", ...((window.AuthManager && AuthManager.token) ? { "Authorization": `Bearer ${AuthManager.token}` } : {}) },
        body: JSON.stringify({ session_id: sessionId })
      });
      const data = await res.json();
      if (data.status === "success") {
        App.toast("Đã chuyển phiên làm việc đang hoạt động!", "info");
        await this.loadHistory();
      }
    } catch (e) {
      App.toast("Lỗi chuyển phiên: " + e.message, "error");
    }
  },

  async deleteSelectedBatch() {
    const isSessionMode = this.viewMode === "session";
    
    if (isSessionMode && this.selectedSessionIds.size > 0) {
      const sessCount = this.selectedSessionIds.size;
      if (!confirm(`Bạn có chắc chắn muốn XÓA VĨNH VIỄN ${sessCount} phiên nghiên cứu đã chọn (kèm toàn bộ các bước thao tác bên trong)? Hành động này không thể hoàn tác.`)) {
        return;
      }

      try {
        const res = await fetch("/api/history/sessions/batch-delete", {
          method: "POST",
          headers: { "Content-Type": "application/json", ...((window.AuthManager && AuthManager.token) ? { "Authorization": `Bearer ${AuthManager.token}` } : {}) },
          body: JSON.stringify({ session_ids: Array.from(this.selectedSessionIds) })
        });
        const data = await res.json();
        if (data.status === "success") {
          App.toast(`Đã xóa thành công ${data.deleted_sessions_count} phiên làm việc!`, "success");
          this.selectedSessionIds.clear();
          this.selectedEntryIds.clear();
          await this.loadHistory();
        }
      } catch (e) {
        App.toast("Lỗi xóa phiên hàng loạt: " + e.message, "error");
      }
    } else if (this.selectedEntryIds.size > 0) {
      const entryCount = this.selectedEntryIds.size;
      if (!confirm(`Bạn có chắc chắn muốn XÓA VĨNH VIỄN ${entryCount} bản ghi thao tác đã chọn? Hành động này không thể hoàn tác.`)) {
        return;
      }

      try {
        const res = await fetch("/api/history/batch-delete", {
          method: "POST",
          headers: { "Content-Type": "application/json", ...((window.AuthManager && AuthManager.token) ? { "Authorization": `Bearer ${AuthManager.token}` } : {}) },
          body: JSON.stringify({ entry_ids: Array.from(this.selectedEntryIds) })
        });
        const data = await res.json();
        if (data.status === "success") {
          App.toast(`Đã xóa thành công ${data.deleted_count} bản ghi lịch sử!`, "success");
          this.selectedEntryIds.clear();
          await this.loadHistory();
        }
      } catch (e) {
        App.toast("Lỗi xóa thao tác hàng loạt: " + e.message, "error");
      }
    } else {
      App.toast("Vui lòng chọn ít nhất 1 mục để xóa.", "warning");
    }
  },

  async deleteSingleSession(sessionId) {
    if (!confirm("Bạn có chắc chắn muốn xóa TOÀN BỘ phiên làm việc này và mọi thao tác bên trong?")) return;

    try {
      const res = await fetch(`/api/history/sessions/${encodeURIComponent(sessionId)}`, {
        method: "DELETE"
      });
      const data = await res.json();
      if (data.status === "success") {
        App.toast("Đã xóa phiên làm việc thành công!", "info");
        this.selectedSessionIds.delete(sessionId);
        await this.loadHistory();
      }
    } catch (e) {
      App.toast("Lỗi xóa phiên: " + e.message, "error");
    }
  },

  async deleteItem(entryId) {
    if (!confirm("Bạn có chắc chắn muốn xóa bản ghi lịch sử này?")) return;

    try {
      const res = await fetch(`/api/history/${encodeURIComponent(entryId)}`, {
        method: "DELETE"
      });
      const data = await res.json();
      if (data.status === "success") {
        App.toast("Đã xóa bản ghi lịch sử thành công!", "info");
        this.selectedEntryIds.delete(entryId);
        await this.loadHistory();
      }
    } catch (e) {
      App.toast("Lỗi xóa lịch sử: " + e.message, "error");
    }
  },

  async clearAll() {
    const modNames = {
      all: "tất cả các phân hệ & phiên làm việc",
      pipeline: "Quy Trình 7 Bước",
      harvester: "Thu Thập Tài Liệu",
      notebooklm: "Kho Tri Thức",
      writer: "Viết Học Thuật 2-File",
      editorial: "Tòa Soạn Báo GATE",
      humanizer: "Khử Dấu Vết AI",
      zotero: "Chuyển Đổi Zotero",
      workspace: "Workspace Tệp"
    };
    const modLabel = modNames[this.currentFilter] || `phân hệ ${this.currentFilter}`;
    if (!confirm(`Bạn có chắc muốn XÓA TOÀN BỘ lịch sử của ${modLabel}? Hành động này không thể hoàn tác.`)) {
      return;
    }

    try {
      const res = await fetch(`/api/history?module=${encodeURIComponent(this.currentFilter)}`, {
        method: "DELETE"
      });
      const data = await res.json();
      if (data.status === "success") {
        App.toast(`Đã dọn dẹp ${data.cleared_count} bản ghi lịch sử!`, "success");
        this.selectedSessionIds.clear();
        this.selectedEntryIds.clear();
        await this.loadHistory();
      }
    } catch (e) {
      App.toast("Lỗi dọn dẹp lịch sử: " + e.message, "error");
    }
  },

  // RESTORE AND JUMP DIRECTLY TO MODULE
  restoreAndJump(entryId) {
    let entry = null;
    if (this.viewMode === "session") {
      for (const s of this.sessions) {
        const found = (s.actions || []).find(a => a.id === entryId);
        if (found) { entry = found; break; }
      }
    } else {
      entry = this.historyRecords.find(e => e.id === entryId);
    }

    if (!entry) {
      App.toast("Không tìm thấy dữ liệu bản ghi để khôi phục.", "warning");
      return;
    }

    const mod = entry.module;
    const inp = entry.inputs || {};
    const res = entry.result_data || {};

    try {
      if (mod === "pipeline") {
        App.switchTab("pipeline-tab");
        if (inp.topic) {
          const topicEl = document.getElementById("pipeline-topic-input");
          if (topicEl) topicEl.value = inp.topic;
          PipelineUI.topic = inp.topic;
        }

        if (res.results && typeof res.results === "object") {
          PipelineUI.stepOutputs = res.results;
          Object.values(res.results).forEach(s => {
            if (s && s.step_no) {
              PipelineUI.renderStepResult(s.step_no, s);
            }
          });
          PipelineUI.setStep(7);
        } else if (res.steps && Array.isArray(res.steps)) {
          res.steps.forEach(s => {
            if (s && s.step_no) {
              PipelineUI.renderStepResult(s.step_no, s);
            }
          });
          if (res.steps.length > 0) {
            PipelineUI.setStep(res.steps[res.steps.length - 1].step_no);
          }
        } else if (res.step_no) {
          PipelineUI.setStep(res.step_no);
          PipelineUI.renderStepResult(res.step_no, res);
        }
        App.toast(`🎯 Đã dẫn đến 'Quy Trình 7 Bước' & hiển thị lại kết quả của '${entry.action_title}'!`, "success");
      } 
      else if (mod === "harvester") {
        App.switchTab("harvester-tab");
        if (inp.topic) {
          const topicEl = document.getElementById("harvester-topic");
          if (topicEl) topicEl.value = inp.topic;
        }
        let papers = res.papers || res.files || [];
        if (papers.length === 0 && res.paper) {
          papers = [res.paper];
        }
        HarvesterUI.currentPapers = papers;
        HarvesterUI.renderHarvestResults(papers);
        App.toast(`🎯 Đã dẫn đến 'Thu Thập Dữ Liệu' & hiển thị lại ${papers.length} bài báo!`, "success");
      }
      else if (mod === "notebooklm") {
        App.switchTab("pipeline-tab");
        PipelineUI.setStep(3);
        if (inp.topic) {
          const topicEl = document.getElementById("pipeline-topic-input");
          if (topicEl) topicEl.value = inp.topic;
          PipelineUI.topic = inp.topic;
        }
        PipelineUI.renderStepResult(3, res);
        App.toast(`🎯 Đã dẫn đến 'Quy Trình Liên Kết (Bước 3: Kho Tri Thức)'!`, "success");
      }
      else if (mod === "writer") {
        App.switchTab("writer-tab");
        if (inp.topic) {
          const topicEl = document.getElementById("writer-topic");
          if (topicEl) topicEl.value = inp.topic;
        }
        if (inp.author_name) {
          const authorEl = document.getElementById("writer-author-name");
          if (authorEl) authorEl.value = inp.author_name;
        }
        if (inp.course_name) {
          const courseEl = document.getElementById("writer-course-name");
          if (courseEl) courseEl.value = inp.course_name;
        }
        if (inp.paper_type) {
          const typeEl = document.getElementById("writer-paper-type");
          if (typeEl) typeEl.value = inp.paper_type;
        }
        if (inp.custom_outline || res.outline) {
          const outlineEl = document.getElementById("writer-custom-outline");
          if (outlineEl) outlineEl.value = inp.custom_outline || res.outline;
        }
        if (res.file_a && res.file_b) {
          AcademicWriterUI.render2FilesResult(res);
        }
        App.toast(`🎯 Đã dẫn đến 'Viết Học Thuật 2-File' & hiển thị lại Bộ 2 Tệp!`, "success");
      }
      else if (mod === "editorial") {
        App.switchTab("editorial-tab");
        if (inp.topic) {
          const topicEl = document.getElementById("editorial-topic");
          if (topicEl) topicEl.value = inp.topic;
        }
        if (res.board_selection || res.gate_steps) {
          EditorialUI.currentAnalysis = res;
          EditorialUI.renderAnalysis(res);
        }
        if (res.execution_logs) {
          EditorialUI.renderExecutionResult(res);
        }
        App.toast(`🎯 Đã dẫn đến 'Tòa Soạn Báo AI' & hiển thị lại ấn phẩm GATE!`, "success");
      }
      else if (mod === "humanizer") {
        App.switchTab("humanizer-tab");
        if (inp.text || res.original_text) {
          const textEl = document.getElementById("humanizer-input-text");
          if (textEl) textEl.value = inp.text || res.original_text;
        }
        if (res.humanized_text) {
          const outEl = document.getElementById("humanizer-output-text");
          if (outEl) outEl.value = res.humanized_text;
        }
        const scoreData = res.after_analysis || res.analysis_after || res.analysis;
        if (scoreData) {
          HumanizerUI.renderScoreGauges(scoreData);
        }
        const origScore = res.original_analysis || res.analysis_before;
        if (origScore && origScore.highlighted_html) {
          const highEl = document.getElementById("humanizer-highlighted-pane");
          if (highEl) highEl.innerHTML = origScore.highlighted_html;
        }
        App.toast(`🎯 Đã dẫn đến 'Khử Dấu Vết AI' & hiển thị lại kết quả làm mượt!`, "success");
      }
      else if (mod === "zotero") {
        App.switchTab("zotero-tab");
        if (typeof ZoteroUI.renderConversionResult === "function") {
          ZoteroUI.renderConversionResult(res);
        } else if (typeof ZoteroUI.renderResult === "function") {
          ZoteroUI.renderResult(res);
        }
        App.toast(`🎯 Đã dẫn đến 'Chuyển Đổi Zotero' & hiển thị lại thống kê trích dẫn!`, "success");
      }
      else if (mod === "workspace" || mod === "editor") {
        App.switchTab("workspace-tab");
        const path = inp.rel_path || res.rel_path;
        if (path && window.DocEditor && DocEditor.loadFileDirect) {
          DocEditor.loadFileDirect(path);
        }
        App.toast(`🎯 Đã dẫn đến 'Không Gian Làm Việc' và mở tệp!`, "success");
      }
      else {
        App.toast(`Đã mở thông tin: ${entry.action_title}`, "info");
      }
    } catch (e) {
      App.toast("Lỗi hiển thị lại kết quả: " + e.message, "error");
    }
  },

  restoreSession(sessionId) {
    const session = this.sessions.find(s => s.session_id === sessionId);
    if (!session || !session.actions || session.actions.length === 0) {
      App.toast("Phiên làm việc chưa có thao tác để khôi phục.", "warning");
      return;
    }
    // Restore the latest action in this session
    const latestAction = session.actions[0];
    this.restoreAndJump(latestAction.id);
  },

  extractFiles(entry) {
    const files = [];
    const res = entry.result_data || {};
    const inp = entry.inputs || {};

    if (res.file_a) {
      files.push({ name: `📄 Tệp A: ${res.file_a.name}`, url: res.file_a.file_url, rel: res.file_a.docx_rel_path });
    }
    if (res.file_b) {
      files.push({ name: `📊 Tệp B: ${res.file_b.name}`, url: res.file_b.file_url, rel: res.file_b.docx_rel_path });
    }
    if (res.final_artifact) {
      files.push({ name: `📑 Báo Cáo Final`, url: res.final_artifact.file_url, rel: res.final_artifact.docx_rel_path });
    }
    if (res.paper && res.paper.file_url) {
      files.push({ name: `📘 ${res.paper.file_name || res.paper.title}`, url: res.paper.file_url, rel: res.paper.rel_path });
    }
    if (res.file_url && !res.paper) {
      files.push({ name: `📥 ${res.filename || res.output_filename || 'Tệp đính kèm'}`, url: res.file_url, rel: res.rel_path || res.output_rel_path });
    }
    if (res.output_file) {
      files.push({ name: `📰 ${res.output_file}`, url: null, rel: `Ban_Thao/${res.output_file}` });
    }
    if (inp.rel_path && !files.some(f => f.rel === inp.rel_path)) {
      files.push({ name: `📁 ${inp.rel_path}`, url: null, rel: inp.rel_path });
    }

    return files;
  },

  getModuleIcon(mod) {
    switch(mod) {
      case "pipeline": return "⚡";
      case "harvester": return "🌐";
      case "zotero": return "📚";
      case "writer": return "🎓";
      case "editorial": return "📰";
      case "humanizer": return "✨";
      case "notebooklm": return "🧠";
      case "workspace": return "📁";
      case "editor": return "📝";
      default: return "📌";
    }
  },

  getModuleBadgeColor(mod) {
    switch(mod) {
      case "pipeline": return "background: rgba(139, 92, 246, 0.2); color: #c084fc; border: 1px solid rgba(139, 92, 246, 0.4);";
      case "harvester": return "background: rgba(59, 130, 246, 0.2); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.4);";
      case "zotero": return "background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.4);";
      case "writer": return "background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.4);";
      case "editorial": return "background: rgba(236, 72, 153, 0.2); color: #f472b6; border: 1px solid rgba(236, 72, 153, 0.4);";
      case "humanizer": return "background: rgba(14, 165, 233, 0.2); color: #38bdf8; border: 1px solid rgba(14, 165, 233, 0.4);";
      case "notebooklm": return "background: rgba(244, 63, 94, 0.2); color: #fb7185; border: 1px solid rgba(244, 63, 94, 0.4);";
      case "workspace": return "background: rgba(234, 179, 8, 0.2); color: #fde047; border: 1px solid rgba(234, 179, 8, 0.4);";
      default: return "background: rgba(148, 163, 184, 0.2); color: #cbd5e1; border: 1px solid rgba(148, 163, 184, 0.4);";
    }
  },

  renderHistoryList() {
    const listEl = document.getElementById("history-items-container");
    if (!listEl) return;

    if (this.viewMode === "session") {
      this.renderSessionsList(listEl);
    } else {
      this.renderFlatList(listEl);
    }
  },

  renderSessionsList(listEl) {
    if (!this.sessions || this.sessions.length === 0) {
      listEl.innerHTML = `
        <div style="text-align: center; padding: 48px 16px; background: rgba(30, 41, 59, 0.3); border-radius: 8px; border: 1px dashed var(--border-color);">
          <span style="font-size: 36px; display: block; margin-bottom: 12px; opacity: 0.6;">📂</span>
          <h4 style="color: #cbd5e1; font-size: 15px; font-weight: 600;">Chưa có phiên làm việc nào</h4>
          <p style="color: #94a3b8; font-size: 12px; margin-top: 4px;">Bấm "➕ Tạo Phiên Mới" hoặc thực hiện bất kỳ thao tác nào, hệ thống sẽ tự động gom nhóm lịch sử theo từng phiên.</p>
        </div>
      `;
      return;
    }

    listEl.innerHTML = this.sessions.map(s => {
      const isSelected = this.selectedSessionIds.has(s.session_id);
      const isExpanded = this.expandedSessionIds.has(s.session_id);
      const isActive = this.activeSession && this.activeSession.session_id === s.session_id;

      return `
        <div class="card session-card ${isSelected ? 'selected' : ''}" style="margin-bottom: 16px; padding: 18px; background: ${isSelected ? 'rgba(59, 130, 246, 0.12)' : 'var(--bg-surface-elevated)'}; border: 1px solid ${isSelected ? 'rgba(59, 130, 246, 0.4)' : 'var(--border-color)'}; border-left: 5px solid ${isActive ? '#10b981' : '#3b82f6'}; border-radius: 10px;">
          <!-- Session Header Row -->
          <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; flex-wrap: wrap;">
            <div style="display: flex; align-items: center; gap: 10px; flex: 1; min-width: 260px;">
              <input type="checkbox" ${isSelected ? 'checked' : ''} onchange="HistoryUI.toggleSessionSelect('${s.session_id}', event)" style="cursor: pointer; width: 16px; height: 16px;">
              
              <div>
                <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                  <span style="font-size: 18px;">📂</span>
                  <h3 style="color: #fff; font-size: 15px; font-weight: 700; margin: 0;">${s.session_title}</h3>
                  ${isActive ? '<span class="badge badge-green" style="font-size: 10px; padding: 2px 6px;">● Đang hoạt động</span>' : ''}
                </div>
                <div style="font-size: 11px; color: #94a3b8; margin-top: 4px; display: flex; gap: 12px; flex-wrap: wrap;">
                  <span>🕒 Bắt đầu: ${s.created_at_display}</span>
                  <span>🔄 Cập nhật: ${s.updated_at_display}</span>
                  <span>⚡ <strong>${s.actions_count}</strong> thao tác</span>
                </div>
              </div>
            </div>

            <!-- Session Controls -->
            <div style="display: flex; gap: 6px; align-items: center; flex-wrap: wrap;">
              <button class="btn btn-secondary btn-sm" onclick="HistoryUI.renameSessionPrompt('${s.session_id}', '${(s.session_title || '').replace(/'/g, "\\'")}')" title="Đổi tên phiên này" style="font-size: 11px; padding: 3px 8px;">
                ✏️ Đổi tên
              </button>
              <button class="btn btn-primary btn-sm" onclick="HistoryUI.restoreSession('${s.session_id}')" title="Khôi phục tiến trình phiên này" style="font-size: 11px; padding: 3px 10px; font-weight: 600;">
                🎯 Khôi Phục Phiên
              </button>
              <button class="btn btn-secondary btn-sm" onclick="HistoryUI.deleteSingleSession('${s.session_id}')" title="Xóa toàn bộ phiên này" style="color: #ef4444; font-size: 11px; padding: 3px 8px;">
                🗑️ Xóa
              </button>
              <button class="btn btn-secondary btn-sm" onclick="HistoryUI.toggleSessionExpand('${s.session_id}')" style="font-size: 11px; padding: 3px 10px;">
                ${isExpanded ? '▲ Thu gọn' : `▼ Xem ${s.actions_count} bước`}
              </button>
            </div>
          </div>

          <!-- Modules used in session badge list -->
          <div style="display: flex; gap: 6px; flex-wrap: wrap; margin-top: 10px; align-items: center;">
            <span style="font-size: 11px; color: #94a3b8;">Phân hệ đã dùng:</span>
            ${(s.modules_used || []).map(m => `
              <span class="badge" style="${this.getModuleBadgeColor(m)} font-size: 10px; padding: 1px 6px;">
                ${this.getModuleIcon(m)} ${m}
              </span>
            `).join('')}
          </div>

          <!-- Expanded Session Timeline of Actions -->
          ${isExpanded ? `
            <div style="margin-top: 16px; border-top: 1px solid rgba(255,255,255,0.08); padding-top: 14px;">
              <h5 style="color: #cbd5e1; font-size: 12px; font-weight: 600; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 0.5px;">
                📋 Tiến Trình Thao Tác Trong Phiên (${s.actions_count} bước):
              </h5>
              <div style="display: flex; flex-direction: column; gap: 10px;">
                ${(s.actions || []).map((a, idx) => this.renderActionItemCard(a, idx + 1)).join('')}
              </div>
            </div>
          ` : ''}
        </div>
      `;
    }).join('');
  },

  renderFlatList(listEl) {
    if (!this.historyRecords || this.historyRecords.length === 0) {
      listEl.innerHTML = `
        <div style="text-align: center; padding: 48px 16px; background: rgba(30, 41, 59, 0.3); border-radius: 8px; border: 1px dashed var(--border-color);">
          <span style="font-size: 36px; display: block; margin-bottom: 12px; opacity: 0.6;">🕒</span>
          <h4 style="color: #cbd5e1; font-size: 15px; font-weight: 600;">Chưa có lịch sử thao tác nào</h4>
          <p style="color: #94a3b8; font-size: 12px; margin-top: 4px;">Mọi hoạt động thu thập, viết báo cáo, chuyển đổi Zotero, tòa soạn báo và khử AI sẽ tự động được ghi lại tại đây.</p>
        </div>
      `;
      return;
    }

    listEl.innerHTML = this.historyRecords.map((e, idx) => this.renderActionItemCard(e, idx + 1, true)).join('');
  },

  renderActionItemCard(e, stepNum = null, isFlatView = false) {
    const isSelected = this.selectedEntryIds.has(e.id);
    const isExpanded = this.expandedItemIds.has(e.id);
    const associatedFiles = this.extractFiles(e);
    const inpStr = JSON.stringify(e.inputs || {}, null, 2);
    const jsonFull = JSON.stringify(e, null, 2);

    return `
      <div class="action-item-card ${isSelected ? 'selected' : ''}" style="padding: 12px 14px; background: ${isSelected ? 'rgba(59, 130, 246, 0.15)' : 'rgba(0,0,0,0.25)'}; border: 1px solid ${isSelected ? 'rgba(59, 130, 246, 0.4)' : 'rgba(255,255,255,0.06)'}; border-radius: 8px; transition: all 0.15s ease;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 10px; flex-wrap: wrap;">
          <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
            <input type="checkbox" ${isSelected ? 'checked' : ''} onchange="HistoryUI.toggleEntrySelect('${e.id}', event)" style="cursor: pointer; width: 14px; height: 14px;">
            ${stepNum && !isFlatView ? `<span style="font-size: 11px; color: #94a3b8; font-weight: 600;">#${stepNum}</span>` : ''}
            <span class="badge" style="${this.getModuleBadgeColor(e.module)} font-size: 11px; padding: 2px 8px;">
              ${this.getModuleIcon(e.module)} ${e.module_label || e.module.toUpperCase()}
            </span>
            <span style="font-size: 11px; color: #94a3b8; font-weight: 500;">
              🕒 ${e.created_at_display}
            </span>
            ${isFlatView && e.session_title ? `
              <span class="badge" style="background: rgba(255,255,255,0.06); color: #93c5fd; font-size: 10px;">
                📂 ${e.session_title}
              </span>
            ` : ''}
          </div>

          <div style="display: flex; gap: 6px;">
            <button class="btn btn-secondary btn-sm" onclick="HistoryUI.toggleDetails('${e.id}')" style="font-size: 10px; padding: 2px 7px;">
              ${isExpanded ? '▲ Thu' : '👁️ Chi tiết'}
            </button>
            <button class="btn btn-secondary btn-sm" onclick="HistoryUI.copyJson('${e.id}')" title="Copy JSON" style="font-size: 10px; padding: 2px 7px;">
              📋 JSON
            </button>
            <button class="btn btn-secondary btn-sm" onclick="HistoryUI.deleteItem('${e.id}')" title="Xóa mục này" style="color: #ef4444; font-size: 10px; padding: 2px 7px;">
              🗑️
            </button>
          </div>
        </div>

        <h4 style="color: #fff; font-size: 13.5px; margin: 8px 0 4px 0; font-weight: 600;">
          ${e.action_title}
        </h4>

        <p style="font-size: 12px; color: #cbd5e1; margin-bottom: 8px; line-height: 1.4; background: rgba(0,0,0,0.2); padding: 6px 10px; border-radius: 4px;">
          📊 <strong>Tóm tắt:</strong> ${e.summary}
        </p>

        <!-- Associated Files -->
        ${associatedFiles.length > 0 ? `
          <div style="display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 8px; align-items: center;">
            <span style="font-size: 11px; color: #94a3b8;">Tệp:</span>
            ${associatedFiles.map(f => `
              <div style="display: inline-flex; align-items: center; gap: 4px; background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 4px; padding: 1px 6px; font-size: 11px;">
                <span style="color: #34d399; font-weight: 500;">${f.name}</span>
                ${f.url ? `<a href="${f.url}" target="_blank" style="color: #60a5fa; text-decoration: none; margin-left: 2px;" title="Mở tệp">↗</a>` : ''}
                ${f.rel ? `<button onclick="App.openWindowsExplorer('${f.rel}')" style="background: none; border: none; cursor: pointer; color: #fbbf24; font-size: 11px; padding: 0 2px;" title="Mở thư mục">📁</button>` : ''}
              </div>
            `).join('')}
          </div>
        ` : ''}

        <!-- Restore button -->
        <div style="margin-top: 6px;">
          <button class="btn btn-primary btn-sm" onclick="HistoryUI.restoreAndJump('${e.id}')" style="display: inline-flex; align-items: center; gap: 4px; font-size: 11px; padding: 3px 10px; font-weight: 600;">
            <span>🎯 Dẫn Đến & Hiển Thị Lại Kết Quả</span>
            <span>↗</span>
          </button>
        </div>

        <!-- Expanded Details Box -->
        ${isExpanded ? `
          <div style="margin-top: 10px; padding: 10px; background: rgba(0,0,0,0.4); border-radius: 6px; border: 1px solid var(--border-color); font-size: 11px;">
            <div style="margin-bottom: 8px;">
              <strong style="color: #cbd5e1; display: block; margin-bottom: 2px;">📥 Tham số đầu vào (Inputs):</strong>
              <pre style="background: rgba(0,0,0,0.3); padding: 6px 8px; border-radius: 4px; color: #a7f3d0; font-family: var(--font-mono); font-size: 10.5px; max-height: 100px; overflow-y: auto; white-space: pre-wrap; margin: 0;">${inpStr}</pre>
            </div>

            <div>
              <strong style="color: #cbd5e1; display: block; margin-bottom: 2px;">📦 JSON Snapshot Đầy Đủ:</strong>
              <pre style="background: rgba(0,0,0,0.3); padding: 6px 8px; border-radius: 4px; color: #93c5fd; font-family: var(--font-mono); font-size: 10.5px; max-height: 140px; overflow-y: auto; white-space: pre-wrap; margin: 0;">${jsonFull}</pre>
            </div>
          </div>
        ` : ''}
      </div>
    `;
  }
};

// Global Window Export
window.HistoryUI = HistoryUI;
