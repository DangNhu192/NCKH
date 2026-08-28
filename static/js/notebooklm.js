/**
 * static/js/notebooklm.js
 * Open-Notebook (Open Source NotebookLM) User Interface Module for WEB SUPER.
 * Manages Notebooks, Sources, Hybrid Retrieval, Grounded Chat with Citations, Literature Matrix, and Transformations.
 */

const NotebookLMUI = {
  activeNotebookId: null,
  notebooksList: [],
  currentNotebook: null,
  activeTab: "chat", // "chat" | "search" | "transform" | "matrix"

  _getHeaders(isJson = true) {
    const headers = {};
    if (isJson) {
      headers["Content-Type"] = "application/json";
    }
    if (window.AuthManager && AuthManager.token) {
      headers["Authorization"] = `Bearer ${AuthManager.token}`;
    }
    return headers;
  },

  async init() {
    console.log("Initializing Open-Notebook UI...");
    await this.loadNotebooks();
  },

  // ==========================================
  // 1. NOTEBOOKS LOADING & SELECTION
  // ==========================================

  async loadNotebooks() {
    try {
      const res = await fetch("/api/notebooklm/notebooks", {
        headers: this._getHeaders(false)
      });
      const data = await res.json();
      if (res.ok && data.status === "success" && data.notebooks) {
        this.notebooksList = data.notebooks;
        this.renderNotebookSelector();
        if (this.notebooksList.length > 0) {
          if (!this.activeNotebookId || !this.notebooksList.find(n => n.id === this.activeNotebookId)) {
            this.activeNotebookId = this.notebooksList[0].id;
          }
          await this.loadNotebookDetails(this.activeNotebookId);
        } else {
          this.renderEmptyNotebooks();
        }
      } else if (res.status === 401 || res.status === 403) {
        if (window.App) App.toast("⚠️ Vui lòng đăng nhập Google & kiểm tra cấu hình API để sử dụng Kho Tri Thức.", "warning");
      }
    } catch (e) {
      console.error("Lỗi tải danh sách Notebooks:", e);
    }
  },

  renderNotebookSelector() {
    const selectEl = document.getElementById("open-notebook-selector");
    if (!selectEl) return;
    
    selectEl.innerHTML = this.notebooksList.map(nb => `
      <option value="${nb.id}" ${nb.id === this.activeNotebookId ? "selected" : ""}>
        📘 ${nb.name} (${nb.source_count || 0} tài liệu)
      </option>
    `).join("");
  },

  async onNotebookChange(notebookId) {
    this.activeNotebookId = notebookId;
    await this.loadNotebookDetails(notebookId);
  },

  async loadNotebookDetails(notebookId) {
    if (!notebookId) return;
    try {
      const res = await fetch(`/api/notebooklm/notebooks/${notebookId}`, {
        headers: this._getHeaders(false)
      });
      const data = await res.json();
      if (res.ok && data.status === "success") {
        this.currentNotebook = data;
        this.renderNotebookHeader();
        this.renderSourcesList();
        this.renderChatHistory();
        this.renderArtifactsList();
      }
    } catch (e) {
      console.error("Lỗi nạp chi tiết Notebook:", e);
    }
  },

  renderNotebookHeader() {
    const titleEl = document.getElementById("open-notebook-active-title");
    const metaEl = document.getElementById("open-notebook-active-meta");
    if (!this.currentNotebook || !titleEl) return;

    const nb = this.currentNotebook.notebook;
    titleEl.textContent = nb.name || "Kho Tri Thức";
    if (metaEl) {
      metaEl.innerHTML = `
        <span class="badge badge-blue">📚 ${this.currentNotebook.sources.length} Nguồn</span>
        <span class="badge badge-purple" style="margin-left: 6px;">🧩 ${this.currentNotebook.chunks_count} Đoạn Trích</span>
        <span style="font-size: 11.5px; color: #94a3b8; margin-left: 10px;">Cập nhật: ${nb.updated_at || "Vừa xong"}</span>
      `;
    }
  },

  renderEmptyNotebooks() {
    const listEl = document.getElementById("open-notebook-sources-list");
    if (listEl) {
      listEl.innerHTML = `<div style="text-align: center; color: #94a3b8; padding: 20px; font-size: 13px;">Chưa có Notebook nào. Hãy bấm "Tạo Mới" để bắt đầu!</div>`;
    }
  },

  // ==========================================
  // 2. CREATE / DELETE NOTEBOOK MODAL
  // ==========================================

  openCreateNotebookModal() {
    const name = prompt("Nhập tên cho Notebook / Đề tài nghiên cứu mới:", "Nghiên cứu ");
    if (!name || !name.trim()) return;
    const topic = prompt("Nhập chủ đề / mô tả tóm tắt của đề tài:", name.trim());
    
    this.createNotebook(name.trim(), topic ? topic.trim() : name.trim());
  },

  async createNotebook(name, topic) {
    try {
      const res = await fetch("/api/notebooklm/notebooks", {
        method: "POST",
        headers: this._getHeaders(true),
        body: JSON.stringify({ name, topic, description: `Kho tri thức cho ${topic}` })
      });
      const data = await res.json();
      if (res.ok && data.status === "success" && data.notebook) {
        if (window.App) App.toast(`Đã tạo Notebook '${data.notebook.name}' thành công!`, "success");
        await this.loadNotebooks();
        this.activeNotebookId = data.notebook.id;
        await this.loadNotebookDetails(data.notebook.id);
      } else {
        if (window.App) App.toast(data.detail || "Không thể tạo Notebook.", "error");
      }
    } catch (e) {
      console.error("Lỗi tạo Notebook:", e);
      if (window.App) App.toast("Lỗi kết nối khi tạo Notebook: " + e.message, "error");
    }
  },

  async deleteCurrentNotebook() {
    if (!this.activeNotebookId) return;
    if (!confirm("Bạn có chắc chắn muốn xóa Notebook này cùng toàn bộ chỉ mục liên quan?")) return;

    try {
      const res = await fetch(`/api/notebooklm/notebooks/${this.activeNotebookId}`, {
        method: "DELETE",
        headers: this._getHeaders(false)
      });
      const data = await res.json();
      if (res.ok && data.status === "success") {
        if (window.App) App.toast("Đã xóa Notebook thành công.", "success");
        this.activeNotebookId = null;
        await this.loadNotebooks();
      } else {
        if (window.App) App.toast(data.detail || "Không thể xóa Notebook.", "error");
      }
    } catch (e) {
      console.error("Lỗi xóa Notebook:", e);
    }
  },

  // ==========================================
  // 3. SOURCES MANAGEMENT
  // ==========================================

  renderSourcesList() {
    const listEl = document.getElementById("open-notebook-sources-list");
    if (!listEl || !this.currentNotebook) return;

    const sources = this.currentNotebook.sources || [];
    if (sources.length === 0) {
      listEl.innerHTML = `
        <div style="text-align: center; color: #64748b; padding: 24px 12px; font-size: 12.5px;">
          <div style="font-size: 24px; margin-bottom: 6px;">📂</div>
          Chưa có tài liệu nguồn.<br>Nhấn nút bên dưới để nạp tệp Word, PDF hoặc chọn từ Thư viện.
        </div>
      `;
      return;
    }

    listEl.innerHTML = sources.map(s => {
      let icon = "📄";
      if (s.source_type === "PDF") icon = "📕";
      else if (s.source_type === "DOCX" || s.source_type === "DOC") icon = "📘";
      else if (s.source_type === "MD") icon = "📝";

      return `
        <div class="source-item-card" style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255,255,255,0.07); border-radius: 8px; padding: 10px 12px; margin-bottom: 8px; transition: all 0.2s ease;">
          <div style="display: flex; align-items: flex-start; justify-content: space-between; gap: 8px;">
            <div style="display: flex; gap: 8px; align-items: flex-start; flex: 1; min-width: 0;">
              <span style="font-size: 16px; margin-top: 2px;">${icon}</span>
              <div style="flex: 1; min-width: 0;">
                <div style="color: #f8fafc; font-size: 13px; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="${s.title}">
                  ${s.title}
                </div>
                <div style="font-size: 11.5px; color: #94a3b8; margin-top: 2px;">
                  <span>👤 ${s.cite_author} (${s.year})</span> · 
                  <span style="color: #60a5fa;">🧩 ${s.chunks_count || 0} đoạn</span>
                </div>
              </div>
            </div>
            <button class="btn btn-sm btn-ghost" onclick="NotebookLMUI.deleteSource('${s.id}')" title="Xóa tài liệu này" style="padding: 2px 6px; color: #f87171;">
              🗑️
            </button>
          </div>
        </div>
      `;
    }).join("");
  },

  async uploadSourceFile(input) {
    if (!this.activeNotebookId) {
      if (window.App) App.toast("Vui lòng chọn hoặc tạo một Notebook trước.", "warning");
      return;
    }
    const file = input.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    const statusEl = document.getElementById("open-notebook-upload-status");
    if (statusEl) statusEl.innerHTML = `<span style="color: #60a5fa;">⏳ Đang bóc tách và phân đoạn '${file.name}'...</span>`;

    try {
      const res = await fetch(`/api/notebooklm/notebooks/${this.activeNotebookId}/sources/upload`, {
        method: "POST",
        headers: this._getHeaders(false),
        body: formData
      });
      const data = await res.json();
      if (res.ok && data.status === "success") {
        if (window.App) App.toast(data.message || `Đã nạp thành công '${file.name}'!`, "success");
        if (statusEl) statusEl.innerHTML = "";
        input.value = "";
        await this.loadNotebookDetails(this.activeNotebookId);
      } else {
        if (window.App) App.toast(data.detail || "Lỗi nạp tệp.", "error");
        if (statusEl) statusEl.innerHTML = "";
      }
    } catch (e) {
      console.error("Lỗi upload source:", e);
      if (statusEl) statusEl.innerHTML = `<span style="color: #f87171;">Lỗi tải lên tệp: ${e.message}</span>`;
    }
  },

  async openImportFromWorkspaceModal() {
    if (!this.activeNotebookId) {
      if (window.App) App.toast("Vui lòng chọn hoặc tạo một Notebook trước.", "warning");
      return;
    }
    try {
      const res = await fetch("/api/files", {
        headers: this._getHeaders(false)
      });
      const files = await res.json();
      const fileList = Array.isArray(files) ? files : [];
      const docFiles = fileList.filter(f => (f.extension === ".docx" || f.extension === ".pdf" || f.extension === ".md"));

      if (docFiles.length === 0) {
        if (window.App) App.toast("Chưa có tệp Word/PDF nào trong Workspace. Hãy thu thập tài liệu từ Tab Thu Thập Dữ Liệu.", "info");
        return;
      }

      let promptMsg = "Chọn số thứ tự tệp trong Workspace để nạp vào Notebook:\n\n";
      docFiles.slice(0, 15).forEach((f, i) => {
        promptMsg += `${i + 1}. ${f.name} (${f.rel_path})\n`;
      });
      promptMsg += "\nNhập số thứ tự (1-" + Math.min(docFiles.length, 15) + "):";

      const choice = prompt(promptMsg, "1");
      if (!choice) return;
      const idx = parseInt(choice) - 1;
      if (idx >= 0 && idx < docFiles.length) {
        const selectedFile = docFiles[idx];
        await this.importSourceFromWorkspace(selectedFile.name);
      }
    } catch (e) {
      console.error("Lỗi nạp file từ Workspace:", e);
    }
  },

  async importSourceFromWorkspace(fileName) {
    try {
      const res = await fetch(`/api/notebooklm/notebooks/${this.activeNotebookId}/sources/import-workspace`, {
        method: "POST",
        headers: this._getHeaders(true),
        body: JSON.stringify({ file_name: fileName })
      });
      const data = await res.json();
      if (res.ok && data.status === "success") {
        if (window.App) App.toast(data.message || `Đã nạp tệp '${fileName}' vào Kho Tri Thức!`, "success");
        await this.loadNotebookDetails(this.activeNotebookId);
      } else {
        if (window.App) App.toast(data.detail || "Không thể nạp tệp.", "error");
      }
    } catch (e) {
      console.error("Lỗi nạp file:", e);
      if (window.App) App.toast("Lỗi nạp file: " + e.message, "error");
    }
  },

  openAddRawTextModal() {
    if (!this.activeNotebookId) {
      if (window.App) App.toast("Vui lòng chọn hoặc tạo một Notebook trước.", "warning");
      return;
    }
    const title = prompt("Nhập tiêu đề cho đoạn văn / ghi chú:", "Ghi chú Nghiên cứu");
    if (!title) return;
    const content = prompt("Dán nội dung văn bản học thuật hoặc bài báo trực tuyến vào đây:");
    if (!content || !content.trim()) return;

    this.addRawTextSource(title.trim(), content.trim());
  },

  async addRawTextSource(title, content) {
    try {
      const res = await fetch(`/api/notebooklm/notebooks/${this.activeNotebookId}/sources/raw`, {
        method: "POST",
        headers: this._getHeaders(true),
        body: JSON.stringify({ title, content, author: "Ghi chú Cá nhân", year: "2026" })
      });
      const data = await res.json();
      if (res.ok && data.status === "success") {
        if (window.App) App.toast(data.message || "Đã nạp ghi chú thành công!", "success");
        await this.loadNotebookDetails(this.activeNotebookId);
      } else {
        if (window.App) App.toast(data.detail || "Lỗi lưu ghi chú.", "error");
      }
    } catch (e) {
      console.error("Lỗi thêm raw text:", e);
    }
  },

  async deleteSource(sourceId) {
    if (!confirm("Bạn có chắc muốn xóa tài liệu nguồn này khỏi Notebook?")) return;
    try {
      const res = await fetch(`/api/notebooklm/notebooks/${this.activeNotebookId}/sources/${sourceId}`, {
        method: "DELETE",
        headers: this._getHeaders(false)
      });
      const data = await res.json();
      if (res.ok && data.status === "success") {
        if (window.App) App.toast(data.message || "Đã xóa tài liệu nguồn thành công.", "success");
        await this.loadNotebookDetails(this.activeNotebookId);
      } else {
        if (window.App) App.toast(data.detail || "Không thể xóa nguồn.", "error");
      }
    } catch (e) {
      console.error("Lỗi xóa source:", e);
    }
  },

  // ==========================================
  // 4. GROUNDED CHAT & Q&A
  // ==========================================

  renderChatHistory() {
    const boxEl = document.getElementById("open-notebook-chat-messages");
    if (!boxEl || !this.currentNotebook) return;

    const history = this.currentNotebook.chat_history || [];
    if (history.length === 0) {
      boxEl.innerHTML = `
        <div style="text-align: center; color: #64748b; padding: 40px 20px; font-size: 13px;">
          <div style="font-size: 32px; margin-bottom: 8px;">🧠</div>
          <strong>Trợ Lý Đối Soát Tri Thức Open-Notebook</strong><br>
          <span style="font-size: 12px; color: #94a3b8;">Đặt bất kỳ câu hỏi nào. AI sẽ truy xuất đoạn trích trong tài liệu và gán nhãn trích dẫn [Tác giả, Năm] thực tế.</span>
        </div>
      `;
      return;
    }

    boxEl.innerHTML = history.map(msg => {
      const isUser = msg.role === "user";
      let citationsHtml = "";
      if (msg.citations && msg.citations.length > 0) {
        citationsHtml = `
          <div class="grounding-citations-box" style="margin-top: 10px; padding: 8px 12px; background: rgba(59, 130, 246, 0.08); border-left: 3px solid #3b82f6; border-radius: 4px; font-size: 11.5px;">
            <strong style="color: #60a5fa;">📚 Nguồn Dẫn Chứng Đối Soát:</strong>
            <ul style="margin: 4px 0 0 16px; padding: 0; color: #94a3b8;">
              ${msg.citations.map(c => `<li><strong>${c.citation_tag}</strong>: <em>${c.source_title}</em> (${c.section})</li>`).join("")}
            </ul>
          </div>
        `;
      }

      return `
        <div class="chat-msg-row ${isUser ? 'chat-msg-user' : 'chat-msg-assistant'}" style="display: flex; gap: 10px; margin-bottom: 14px; align-items: flex-start;">
          <div style="width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 14px; background: ${isUser ? '#3b82f6' : '#8b5cf6'}; color: #fff; flex-shrink: 0;">
            ${isUser ? '👤' : '🤖'}
          </div>
          <div style="flex: 1; background: ${isUser ? 'rgba(59, 130, 246, 0.15)' : 'rgba(30, 41, 59, 0.7)'}; border: 1px solid ${isUser ? 'rgba(59, 130, 246, 0.3)' : 'rgba(255,255,255,0.08)'}; border-radius: 8px; padding: 12px 14px;">
            <div style="color: #f8fafc; font-size: 13.5px; line-height: 1.6; white-space: pre-wrap;">${this.formatMarkdownLinks(msg.content)}</div>
            ${citationsHtml}
            <div style="font-size: 10.5px; color: #64748b; margin-top: 6px; text-align: right;">${msg.timestamp || ''}</div>
          </div>
        </div>
      `;
    }).join("");

    boxEl.scrollTop = boxEl.scrollHeight;
  },

  formatMarkdownLinks(text) {
    if (!text) return "";
    let formatted = text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/\[([^\]]+)\]/g, '<span class="badge badge-blue" style="font-size: 11px; padding: 1px 6px;">$1</span>');
    return formatted;
  },

  sendFastPrompt(text) {
    const inputEl = document.getElementById("open-notebook-chat-input");
    if (inputEl) {
      inputEl.value = text;
      this.sendChatMessage();
    }
  },

  async sendChatMessage() {
    if (!this.activeNotebookId) {
      if (window.App) App.toast("Vui lòng chọn một Notebook.", "warning");
      return;
    }
    const inputEl = document.getElementById("open-notebook-chat-input");
    const msg = inputEl.value.trim();
    if (!msg) return;

    inputEl.value = "";
    const boxEl = document.getElementById("open-notebook-chat-messages");
    if (boxEl) {
      boxEl.innerHTML += `
        <div class="chat-msg-row chat-msg-user" style="display: flex; gap: 10px; margin-bottom: 14px; align-items: flex-start;">
          <div style="width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 14px; background: #3b82f6; color: #fff; flex-shrink: 0;">👤</div>
          <div style="flex: 1; background: rgba(59, 130, 246, 0.15); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 8px; padding: 12px 14px; color: #f8fafc; font-size: 13.5px;">${msg}</div>
        </div>
        <div id="open-notebook-loading-bubble" style="display: flex; gap: 10px; margin-bottom: 14px; align-items: center; color: #60a5fa; font-size: 13px;">
          <span class="spinner" style="width: 16px; height: 16px; border: 2px solid #3b82f6; border-top-color: transparent; border-radius: 50%; animation: spin 0.8s linear infinite;"></span>
          Đang truy xuất ngữ cảnh và đối soát dẫn chứng...
        </div>
      `;
      boxEl.scrollTop = boxEl.scrollHeight;
    }

    try {
      const res = await fetch(`/api/notebooklm/notebooks/${this.activeNotebookId}/chat`, {
        method: "POST",
        headers: this._getHeaders(true),
        body: JSON.stringify({ message: msg })
      });
      const data = await res.json();
      if (res.ok && data.status === "success") {
        await this.loadNotebookDetails(this.activeNotebookId);
      } else {
        if (window.App) App.toast(data.detail || "Lỗi khi xử lý câu hỏi.", "error");
        const loadEl = document.getElementById("open-notebook-loading-bubble");
        if (loadEl) loadEl.remove();
      }
    } catch (e) {
      console.error("Lỗi gửi chat:", e);
      const loadEl = document.getElementById("open-notebook-loading-bubble");
      if (loadEl) loadEl.remove();
    }
  },

  async clearChatHistory() {
    if (!confirm("Bạn có chắc muốn xóa toàn bộ lịch sử trò chuyện của Notebook này?")) return;
    try {
      await fetch(`/api/notebooklm/notebooks/${this.activeNotebookId}/chat/history`, {
        method: "DELETE",
        headers: this._getHeaders(false)
      });
      await this.loadNotebookDetails(this.activeNotebookId);
    } catch (e) {
      console.error("Lỗi xóa chat:", e);
    }
  },

  // ==========================================
  // 5. HYBRID SEARCH
  // ==========================================

  async executeHybridSearch() {
    if (!this.activeNotebookId) {
      if (window.App) App.toast("Vui lòng chọn một Notebook.", "warning");
      return;
    }
    const inputEl = document.getElementById("open-notebook-search-input");
    const query = inputEl ? inputEl.value.trim() : "";
    if (!query) return;

    const resBox = document.getElementById("open-notebook-search-results");
    if (resBox) resBox.innerHTML = `<div style="text-align: center; color: #60a5fa; padding: 20px;">🔍 Đang tìm kiếm lai (BM25 + Semantic Cosine)...</div>`;

    try {
      const res = await fetch(`/api/notebooklm/notebooks/${this.activeNotebookId}/search`, {
        method: "POST",
        headers: this._getHeaders(true),
        body: JSON.stringify({ query, top_k: 8 })
      });
      const data = await res.json();
      if (res.ok && data.status === "success") {
        this.renderSearchResults(data.results);
      } else {
        if (resBox) resBox.innerHTML = `<div style="color: #f87171; padding: 10px;">${data.detail || "Lỗi tìm kiếm."}</div>`;
      }
    } catch (e) {
      console.error("Lỗi hybrid search:", e);
    }
  },

  renderSearchResults(results) {
    const resBox = document.getElementById("open-notebook-search-results");
    if (!resBox) return;

    if (!results || results.length === 0) {
      resBox.innerHTML = `<div style="text-align: center; color: #64748b; padding: 30px;">Không tìm thấy đoạn trích phù hợp.</div>`;
      return;
    }

    resBox.innerHTML = results.map((r, i) => `
      <div class="search-result-card" style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 12px; margin-bottom: 10px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
          <strong style="color: #60a5fa; font-size: 13px;">${i + 1}. [${r.author}, ${r.year}] ${r.source_title}</strong>
          <span class="badge badge-purple" style="font-size: 10.5px;">Điểm: ${r.score}</span>
        </div>
        <div style="font-size: 11px; color: #94a3b8; margin-bottom: 6px;">Mục: <em>${r.section_heading}</em> (BM25: ${r.bm25_score} | Cosine: ${r.semantic_score})</div>
        <p style="color: #cbd5e1; font-size: 12.5px; line-height: 1.5; margin: 0;">${r.text}</p>
      </div>
    `).join("");
  },

  // ==========================================
  // 6. TRANSFORMATIONS & LITERATURE MATRIX
  // ==========================================

  generateTransform(type) {
    return this.executeTransformation(type);
  },

  async executeTransformation(type) {
    if (!this.activeNotebookId) {
      if (window.App) App.toast("Vui lòng chọn một Notebook.", "warning");
      return;
    }

    if (type === "literature_matrix") {
      return this.executeLiteratureMatrix();
    }

    const previewEl = document.getElementById("open-notebook-transform-preview");
    if (previewEl) {
      previewEl.innerHTML = `
        <div style="text-align: center; color: #60a5fa; padding: 40px;">
          <span class="spinner" style="width: 24px; height: 24px; border: 2px solid #3b82f6; border-top-color: transparent; border-radius: 50%; animation: spin 0.8s linear infinite; display: inline-block; margin-bottom: 8px;"></span>
          <br>Đang tổng hợp và kiến tạo sản phẩm tri thức (${type})...
        </div>
      `;
    }

    try {
      const res = await fetch(`/api/notebooklm/notebooks/${this.activeNotebookId}/transform`, {
        method: "POST",
        headers: this._getHeaders(true),
        body: JSON.stringify({ transform_type: type })
      });
      const data = await res.json();
      if (res.ok && data.status === "success") {
        if (window.App) App.toast(`Đã tạo thành công: ${data.artifact_name}`, "success");
        this.renderTransformResult(data);
        await this.loadNotebookDetails(this.activeNotebookId);
      } else {
        if (window.App) App.toast(data.detail || "Không thể sinh sản phẩm.", "error");
      }
    } catch (e) {
      console.error("Lỗi sinh transform:", e);
    }
  },

  async executeLiteratureMatrix() {
    if (!this.activeNotebookId) {
      if (window.App) App.toast("Vui lòng chọn một Notebook.", "warning");
      return;
    }

    const previewEl = document.getElementById("open-notebook-transform-preview");
    if (previewEl) {
      previewEl.innerHTML = `
        <div style="text-align: center; color: #38bdf8; padding: 40px;">
          <span class="spinner" style="width: 24px; height: 24px; border: 2px solid #38bdf8; border-top-color: transparent; border-radius: 50%; animation: spin 0.8s linear infinite; display: inline-block; margin-bottom: 8px;"></span>
          <br>Đang lập Ma Trận Tổng Thuật Y Văn 7 Cột Chuẩn Mực Quốc Tế...
        </div>
      `;
    }

    try {
      const res = await fetch(`/api/notebooklm/notebooks/${this.activeNotebookId}/literature-matrix`, {
        method: "POST",
        headers: this._getHeaders(true),
        body: JSON.stringify({})
      });
      const data = await res.json();
      if (res.ok && data.status === "success") {
        if (window.App) App.toast(`Đã lập Ma Trận Y Văn với ${data.total_papers || 0} bài báo!`, "success");
        this.renderLiteratureMatrixResult(data);
        await this.loadNotebookDetails(this.activeNotebookId);
      } else {
        if (window.App) App.toast(data.detail || "Không thể lập ma trận y văn.", "error");
      }
    } catch (e) {
      console.error("Lỗi lập ma trận y văn:", e);
    }
  },

  renderLiteratureMatrixResult(data) {
    const previewEl = document.getElementById("open-notebook-transform-preview");
    if (!previewEl) return;

    const matrix = data.matrix || [];
    let rowsHtml = matrix.map((row, idx) => `
      <tr style="border-bottom: 1px solid rgba(255,255,255,0.07);">
        <td style="padding: 8px 10px; font-weight: 700; color: #60a5fa;">${row.citation}</td>
        <td style="padding: 8px 10px; color: #f8fafc;">${row.title}</td>
        <td style="padding: 8px 10px; color: #cbd5e1;">${row.objective}</td>
        <td style="padding: 8px 10px; color: #a78bfa;">${row.methodology}</td>
        <td style="padding: 8px 10px; color: #34d399;">${row.key_findings}</td>
        <td style="padding: 8px 10px; color: #f87171;">${row.limitations}</td>
        <td style="padding: 8px 10px; color: #fde047;">${row.theoretical_contribution}</td>
      </tr>
    `).join("");

    previewEl.innerHTML = `
      <div style="background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 10px; padding: 18px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; flex-wrap: wrap; gap: 8px;">
          <div>
            <h4 style="color: #38bdf8; font-size: 15px; margin: 0; font-weight: 800;">
              📊 Ma Trận Tổng Thuật Y Văn (Literature Review Matrix)
            </h4>
            <span style="font-size: 12px; color: #94a3b8;">Đề tài: ${data.topic} · ${data.total_papers} bài báo</span>
          </div>
          <div style="display: flex; gap: 8px;">
            ${data.docx_file ? `<a href="/api/files/download?path=${encodeURIComponent(data.docx_file)}" target="_blank" class="btn btn-sm btn-primary">📥 Tải Word (.docx)</a>` : ''}
            ${data.md_file ? `<a href="/api/files/download?path=${encodeURIComponent(data.md_file)}" target="_blank" class="btn btn-sm btn-secondary">📥 Tải Markdown (.md)</a>` : ''}
          </div>
        </div>

        <div style="overflow-x: auto; max-height: 480px;">
          <table style="width: 100%; border-collapse: collapse; font-size: 12px; min-width: 900px;">
            <thead>
              <tr style="background: rgba(59, 130, 246, 0.2); color: #fff; text-align: left;">
                <th style="padding: 8px 10px;">Tác giả & Năm</th>
                <th style="padding: 8px 10px;">Tiêu đề bài báo</th>
                <th style="padding: 8px 10px;">Mục tiêu nghiên cứu</th>
                <th style="padding: 8px 10px;">Phương pháp / Dữ liệu</th>
                <th style="padding: 8px 10px;">Kết quả cốt lõi</th>
                <th style="padding: 8px 10px;">Lỗ hổng (Gaps)</th>
                <th style="padding: 8px 10px;">Đóng góp lý thuyết</th>
              </tr>
            </thead>
            <tbody>
              ${rowsHtml}
            </tbody>
          </table>
        </div>
      </div>
    `;
  },

  renderTransformResult(data) {
    const previewEl = document.getElementById("open-notebook-transform-preview");
    if (!previewEl) return;

    previewEl.innerHTML = `
      <div style="background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 10px; padding: 18px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 8px;">
          <h4 style="color: #60a5fa; font-size: 15px; margin: 0; font-weight: 700;">✨ ${data.artifact_name}</h4>
          <div style="display: flex; gap: 8px;">
            <a href="/api/files/download?path=${encodeURIComponent(data.docx_file)}" target="_blank" class="btn btn-sm btn-primary">📥 Tải Word (.docx)</a>
            <a href="/api/files/download?path=${encodeURIComponent(data.md_file)}" target="_blank" class="btn btn-sm btn-secondary">📥 Tải Markdown (.md)</a>
          </div>
        </div>
        <div style="background: rgba(0,0,0,0.3); border-radius: 6px; padding: 14px; max-height: 420px; overflow-y: auto; color: #f8fafc; font-size: 13px; line-height: 1.6; white-space: pre-wrap;">
          ${data.content}
        </div>
      </div>
    `;
  },

  renderArtifactsList() {
    const boxEl = document.getElementById("open-notebook-artifacts-list");
    if (!boxEl || !this.currentNotebook) return;

    const artifacts = this.currentNotebook.artifacts || [];
    if (artifacts.length === 0) {
      boxEl.innerHTML = `<span style="font-size: 11.5px; color: #64748b;">Chưa có sản phẩm biến đổi nào được sinh ra.</span>`;
      return;
    }

    boxEl.innerHTML = artifacts.map(a => `
      <div style="display: flex; justify-content: space-between; align-items: center; background: rgba(255,255,255,0.03); padding: 4px 8px; border-radius: 4px; margin-bottom: 4px; font-size: 11.5px;">
        <span style="color: #cbd5e1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 160px;" title="${a.title}">📄 ${a.title}</span>
        <a href="/api/files/download?path=${encodeURIComponent(a.file_path)}" target="_blank" style="color: #60a5fa; text-decoration: none; font-weight: 600;">⬇️ Tải</a>
      </div>
    `).join("");
  },

  switchViewTab(tabName) {
    this.activeTab = tabName;
    document.querySelectorAll(".open-nb-tab-btn").forEach(b => {
      if (b.getAttribute("data-tab") === tabName) b.classList.add("active");
      else b.classList.remove("active");
    });

    const chatPane = document.getElementById("open-nb-pane-chat");
    const searchPane = document.getElementById("open-nb-pane-search");
    const transformPane = document.getElementById("open-nb-pane-transform");

    if (chatPane) chatPane.style.display = tabName === "chat" ? "flex" : "none";
    if (searchPane) searchPane.style.display = tabName === "search" ? "flex" : "none";
    if (transformPane) transformPane.style.display = tabName === "transform" ? "flex" : "none";
  }
};

window.NotebookLMUI = NotebookLMUI;
