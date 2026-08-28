// Editorial Office AI v3.1 (Tòa soạn Báo AI & GATE Workflow + Word DOCX Drag & Drop)
const EditorialUI = {
  currentAnalysis: null,
  selectedFile: null,
  sourceContent: "",

  init() {
    const dropZone = document.getElementById("editorial-drop-zone");
    const fileInput = document.getElementById("editorial-file-input");

    if (dropZone && fileInput) {
      ["dragenter", "dragover"].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
          e.preventDefault();
          e.stopPropagation();
          dropZone.classList.add("dragover");
          dropZone.style.borderColor = "#38bdf8";
          dropZone.style.background = "rgba(56, 189, 248, 0.15)";
        }, false);
      });

      ["dragleave", "dragend"].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
          e.preventDefault();
          e.stopPropagation();
          dropZone.classList.remove("dragover");
          dropZone.style.borderColor = "var(--border-color)";
          dropZone.style.background = "rgba(0,0,0,0.15)";
        }, false);
      });

      dropZone.addEventListener("drop", (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.remove("dragover");
        dropZone.style.borderColor = "var(--border-color)";
        dropZone.style.background = "rgba(0,0,0,0.15)";
        if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files.length > 0) {
          this.handleFileSelected(e.dataTransfer.files[0]);
        }
      }, false);
    }
  },

  async handleFileSelected(file) {
    if (window.App && App.requireAuth && !App.requireAuth('tải lên tệp tư liệu')) return;
    if (!file.name.toLowerCase().endsWith(".docx")) {
      App.toast("Vui lòng chọn hoặc kéo thả tệp Word (.docx).", "error");
      return;
    }

    this.selectedFile = file;
    const badgeEl = document.getElementById("editorial-selected-file-badge");
    if (badgeEl) {
      badgeEl.innerHTML = `📂 <strong style="color: #38bdf8;">Đang tiếp nhận:</strong> ${file.name} (${(file.size / 1024).toFixed(1)} KB)...`;
    }

    App.toast(`Tòa soạn đang đọc và trích xuất dữ liệu từ "${file.name}"...`, "info");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("/api/files/extract-docx-text", {
        method: "POST",
        headers: (window.AuthManager && AuthManager.token) ? { "Authorization": `Bearer ${AuthManager.token}` } : {},
        body: formData
      });
      const data = await res.json().catch(() => ({ detail: `Lỗi máy chủ (${res.status})` }));
      if (res.ok && data.success) {
        this.sourceContent = data.text;
        
        // Auto-fill topic
        const topicInput = document.getElementById("editorial-topic");
        if (topicInput) {
          topicInput.value = data.title;
        }

        // Set user-input mode to 'bài viết cũ'
        const inputModeSelect = document.getElementById("editorial-user-input");
        if (inputModeSelect) {
          inputModeSelect.value = "bài viết cũ";
        }

        if (badgeEl) {
          badgeEl.innerHTML = `📂 <strong style="color: #34d399;">Đã tiếp nhận tư liệu:</strong> ${file.name} (${data.word_count} từ, ${data.paragraphs_count} đoạn)`;
        }

        App.toast(`Đã tiếp nhận tư liệu "${file.name}" (${data.word_count} từ). Tổng Biên Tập đang lập ma trận phân ban...`, "success");
        this.analyzeRequest();
      } else {
        App.toast(data.detail || "Không thể đọc tệp Word", "error");
      }
    } catch (e) {
      App.toast("Lỗi đọc tệp tư liệu: " + e.message, "error");
    }
  },

  async analyzeRequest() {
    if (window.App && App.requireAuth && !App.requireAuth('sử dụng Tòa Soạn Báo AI')) return;
    const topic = document.getElementById("editorial-topic").value.trim();
    const userInput = document.getElementById("editorial-user-input").value;
    const purpose = document.getElementById("editorial-purpose").value;
    const audience = document.getElementById("editorial-audience").value;
    const platform = document.getElementById("editorial-platform").value;
    const needFactCheck = document.getElementById("editorial-fact-check").checked;

    if (!topic) {
      App.toast("Vui lòng nhập Đề tài / Chủ đề cho Tòa soạn hoặc kéo thả tệp Word .docx.", "warning");
      return;
    }

    const btn = document.getElementById("btn-editorial-analyze");
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-btn"></span> <span>Tổng Biên Tập đang phân tích...</span>';

    const analysisBox = document.getElementById("editorial-analysis-container");
    if (analysisBox) {
      analysisBox.innerHTML = `
        <div class="loading-indicator-box">
          <div class="spinner-lg" style="border-top-color: #f59e0b; border-right-color: #fbbf24; box-shadow: 0 0 16px rgba(245, 158, 11, 0.25);"></div>
          <div class="loading-indicator-title">📰 Tổng Biên Tập đang đánh giá & phân công 6 Ban<span class="loading-pulse-dots"></span></div>
          <div class="loading-indicator-desc">Phân tích mục đích, đối tượng độc giả, dữ liệu đầu vào để lập ma trận GATE điều phối cho đề tài: <em>"${topic}"</em>.</div>
        </div>
      `;
    }

    try {
      const res = await fetch("/api/editorial/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json", ...((window.AuthManager && AuthManager.token) ? { "Authorization": `Bearer ${AuthManager.token}` } : {}) },
        body: JSON.stringify({
          topic,
          user_input: userInput,
          purpose,
          audience,
          platform,
          need_fact_check: needFactCheck
        })
      });

      const data = await res.json().catch(() => ({ detail: `Lỗi máy chủ (${res.status})` }));
      if (res.ok && data.board_selection) {
        this.currentAnalysis = data;
        this.renderAnalysis(data);
        App.toast("Tổng Biên Tập đã lập Ma Trận & Phân Ban hoàn tất!", "success");
      } else {
        const errMsg = data.detail || data.message || "Lỗi phân tích đề bài";
        App.toast(errMsg, "error");
        if (analysisBox) {
          analysisBox.innerHTML = `
            <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.4); padding: 14px; border-radius: 8px; color: #fca5a5; font-size: 13px; margin-top: 14px;">
              ❌ <strong>Không thể phân tích:</strong> ${errMsg}
            </div>
          `;
        }
      }
    } catch (e) {
      App.toast("Lỗi phân tích: " + e.message, "error");
      if (analysisBox) {
        analysisBox.innerHTML = `
          <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.4); padding: 14px; border-radius: 8px; color: #fca5a5; font-size: 13px; margin-top: 14px;">
            ❌ <strong>Lỗi kết nối:</strong> ${e.message}
          </div>
        `;
      }
    } finally {
      btn.disabled = false;
      btn.innerHTML = "🔍 Phân Tích Đề Bài & Lập Ma Trận Ban (TBT)";
    }
  },

  renderAnalysis(data) {
    const container = document.getElementById("editorial-analysis-container");
    if (!container) return;

    const b = data.board_selection;
    const hasSource = Boolean(this.sourceContent);

    container.innerHTML = `
      <div class="card" style="background: var(--bg-surface-elevated); margin-top: 18px;">
        <div class="card-header">
          <h4 style="color: #fff; font-size: 15px;">Quyết Định Của Tổng Biên Tập (TBT)</h4>
          <span class="badge badge-purple">${data.gate_model}</span>
        </div>

        ${hasSource ? `
          <div style="background: rgba(56, 189, 248, 0.1); border: 1px solid rgba(56, 189, 248, 0.3); padding: 10px 14px; border-radius: 6px; margin-bottom: 14px; font-size: 11px; color: #bae6fd;">
            📄 <strong>Nguồn dữ liệu đầu vào:</strong> Đang sử dụng nội dung từ tệp Word tư liệu đã nạp (${this.sourceContent.split(/\s+/).length} từ).
          </div>
        ` : ''}

        <h5 style="color: #cbd5e1; font-size: 13px; margin-bottom: 10px;">Phân Công 3 Ban Trọng Tâm:</h5>
        <div class="grid-3" style="margin-bottom: 16px;">
          <div class="dept-card role-primary">
            <span class="badge" style="background: rgba(239,68,68,0.2); color: #fca5a5;">🔴 Ban Chủ Trì</span>
            <h5 style="color: #fff; font-size: 14px; margin: 6px 0;">${b.primary.name}</h5>
            <p style="font-size: 11px; color: #94a3b8;">${b.primary.description}</p>
          </div>
          <div class="dept-card role-coordinating">
            <span class="badge" style="background: rgba(245,158,11,0.2); color: #fcd34d;">🟡 Ban Phối Hợp</span>
            <h5 style="color: #fff; font-size: 14px; margin: 6px 0;">${b.coordinating.name}</h5>
            <p style="font-size: 11px; color: #94a3b8;">${b.coordinating.description}</p>
          </div>
          <div class="dept-card role-checker">
            <span class="badge" style="background: rgba(16,185,129,0.2); color: #6ee7b7;">🟢 Ban Kiểm Tra</span>
            <h5 style="color: #fff; font-size: 14px; margin: 6px 0;">${b.checker.name}</h5>
            <p style="font-size: 11px; color: #94a3b8;">${b.checker.description}</p>
          </div>
        </div>

        <h5 style="color: #cbd5e1; font-size: 13px; margin-bottom: 10px;">Quy Trình GATE Được Thiết Kế:</h5>
        <div style="background: rgba(0,0,0,0.3); padding: 14px; border-radius: 8px; margin-bottom: 16px;">
          ${data.gate_steps.map((st, i) => `
            <div style="display: flex; align-items: center; justify-content: space-between; padding: 8px 0; border-bottom: ${i < data.gate_steps.length - 1 ? '1px solid rgba(255,255,255,0.06)' : 'none'};">
              <span style="font-size: 12px; color: #e2e8f0;">Bước ${st.step_no}: ${st.action}</span>
              <span class="gate-badge">${st.gate}</span>
            </div>
          `).join('')}
        </div>

        <button class="btn btn-primary btn-lg" onclick="EditorialUI.executeGateWorkflow()" style="width: 100%;">
          ⚡ Thực Thi Quy Trình GATE Tòa Soạn Báo AI
        </button>
      </div>
    `;
  },

  async executeGateWorkflow() {
    if (window.App && App.requireAuth && !App.requireAuth('thực thi quy trình GATE Tòa Soạn')) return;
    if (!this.currentAnalysis) {
      App.toast("Vui lòng phân tích đề bài trước.", "warning");
      return;
    }

    const execContainer = document.getElementById("editorial-execution-container");
    if (execContainer) {
      execContainer.innerHTML = `
        <div class="loading-indicator-box">
          <div class="spinner-lg" style="border-top-color: #10b981; border-right-color: #34d399; box-shadow: 0 0 16px rgba(16, 185, 129, 0.25);"></div>
          <div class="loading-indicator-title">🚀 Các Ban đang phối hợp triển khai qua 4 Trạm GATE<span class="loading-pulse-dots"></span></div>
          <div class="loading-indicator-desc">Thu thập dữ liệu ➔ Soạn thảo bản thảo ➔ Kiểm duyệt Fact-check ➔ Xuất bản hoàn tất tệp .docx chuẩn mực.</div>
        </div>
      `;
    }

    App.toast("Các Ban đang phối hợp triển khai bản thảo theo quy chuẩn GATE...", "info");

    try {
      const res = await fetch("/api/editorial/execute-gate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...((window.AuthManager && AuthManager.token) ? { "Authorization": `Bearer ${AuthManager.token}` } : {})
        },
        body: JSON.stringify({
          topic: this.currentAnalysis.topic,
          gate_steps: this.currentAnalysis.gate_steps,
          source_content: this.sourceContent || ""
        })
      });

      const data = await res.json().catch(() => ({ detail: `Lỗi máy chủ (${res.status})` }));
      if (res.ok && data.status === "success") {
        App.toast("Đã xuất bản bài viết tòa soạn báo AI thành công!", "success");
        this.renderExecutionResult(data);
        App.updateStatus();
      } else {
        const errMsg = data.detail || data.message || "Lỗi thực thi quy trình GATE";
        App.toast(errMsg, "error");
        if (execContainer) {
          execContainer.innerHTML = `
            <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.4); padding: 14px; border-radius: 8px; color: #fca5a5; font-size: 13px; margin-top: 14px;">
              ❌ <strong>Lỗi thực thi:</strong> ${errMsg}
            </div>
          `;
        }
      }
    } catch (e) {
      App.toast("Lỗi thực thi GATE: " + e.message, "error");
      if (execContainer) {
        execContainer.innerHTML = `
          <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.4); padding: 14px; border-radius: 8px; color: #fca5a5; font-size: 13px; margin-top: 14px;">
            ❌ <strong>Lỗi kết nối:</strong> ${e.message}
          </div>
        `;
      }
    }
  },

  renderExecutionResult(data) {
    const container = document.getElementById("editorial-execution-container");
    if (!container) return;

    const mdPath = data.output_file || data.md_rel_path || data.md_file || '';
    const docxPath = data.docx_file || data.docx_rel_path || (data.output_file ? data.output_file.replace('.md', '.docx') : '') || '';

    container.innerHTML = `
      <div class="card" style="margin-top: 24px; border-color: rgba(52, 211, 153, 0.4);">
        <div class="card-header">
          <div>
            <h4 style="color: #34d399; font-size: 16px;">✅ Ấn Phẩm Tòa Soạn AI Đã Hoàn Thành Qua 4 Trạm GATE</h4>
            <p style="color: #94a3b8; font-size: 12px; margin-top: 4px;">Đã lưu trữ đồng thời tệp Markdown và tệp Microsoft Word (.docx).</p>
          </div>
          <button class="btn btn-green btn-sm" onclick="App.openWindowsExplorer('${docxPath || mdPath}')">
            📂 Mở Thư Mục Bản Thảo
          </button>
        </div>

        <div style="margin-bottom: 16px;">
          <h5 style="color: #cbd5e1; font-size: 13px; margin-bottom: 8px;">Nhật Ký Điều Phối Tòa Soạn:</h5>
          <div style="background: rgba(0,0,0,0.4); padding: 12px; border-radius: 6px; font-family: monospace; font-size: 11px; color: #a7f3d0;">
            ${(data.execution_logs || []).map(log => `<div>▶ ${log}</div>`).join('')}
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Xem Trước Nội Dung Bài Báo:</label>
          <div class="preview-pane" style="max-height: 280px;">
            <pre style="white-space: pre-wrap; font-family: inherit; margin: 0; color: #e2e8f0;">${data.content || ''}</pre>
          </div>
        </div>

        <div style="display: flex; gap: 10px; margin-top: 16px; flex-wrap: wrap;">
          <button class="btn btn-primary btn-md" onclick="App.openFileInSystem('${docxPath}')">📝 Mở Bằng Word (.docx)</button>
          <button class="btn btn-secondary btn-md" onclick="App.downloadFile('${docxPath}')">📥 Tải File Word (.docx)</button>
          <button class="btn btn-secondary btn-md" onclick="App.downloadFile('${mdPath}')">📥 Tải Bản Thảo (.md)</button>
          <button class="btn btn-outline btn-md" onclick="App.openWindowsExplorer('${docxPath || mdPath}')">📂 Mở Thư Mục Bản Thảo</button>
        </div>
      </div>
    `;
  }
};

document.addEventListener("DOMContentLoaded", () => EditorialUI.init());
if (document.readyState === "complete" || document.readyState === "interactive") {
  EditorialUI.init();
}

// Global Window Export
window.EditorialUI = EditorialUI;
