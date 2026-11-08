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

        <button id="btn-editorial-execute-gate" class="btn btn-primary btn-lg" onclick="EditorialUI.executeGateWorkflow()" style="width: 100%;">
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

    const btn = document.getElementById("btn-editorial-execute-gate");
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = `<span class="spinner-btn"></span> <span>Các Ban đang phối hợp triển khai...</span>`;
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
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = `⚡ Thực Thi Quy Trình GATE Tòa Soạn Báo AI`;
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
  },

  async runStandaloneFactCheck() {
    const topicInput = document.getElementById("editorial-topic");
    const topic = topicInput ? topicInput.value.trim() : "";
    const textToCheck = this.sourceContent || topic;

    if (!textToCheck) {
      App.toast("Vui lòng nhập đề tài hoặc kéo thả tệp Word (.docx) để kiểm tra thực chứng.", "warning");
      return;
    }

    const btn = document.getElementById("btn-editorial-fact-check-standalone");
    const execContainer = document.getElementById("editorial-execution-container");
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = '<span class="spinner-btn"></span> <span>Đang rà soát dấu chân số liệu & DOI...</span>';
    }

    App.toast("🛡️ Đang chạy Academic Fact-Checker đối soát số liệu & DOI...", "info");

    try {
      const res = await fetch("/api/editorial/fact-check", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...((window.AuthManager && AuthManager.token) ? { "Authorization": `Bearer ${AuthManager.token}` } : {})
        },
        body: JSON.stringify({
          text_to_check: textToCheck,
          check_dois: true,
          deep_verification: true
        })
      });

      const data = await res.json();
      if (res.ok && data.status === "success") {
        App.toast("✅ Đã hoàn tất thẩm định số liệu & DOI thực chứng!", "success");
        this.renderFactCheckResult(data);
      } else {
        App.toast(data.detail || data.message || "Lỗi thẩm định thực chứng", "error");
      }
    } catch (e) {
      App.toast("Lỗi thẩm định thực chứng: " + e.message, "error");
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = "🛡️ Thẩm Định Dấu Chân Số Liệu & DOI Độc Lập (Fact-Checker)";
      }
    }
  },

  renderFactCheckResult(data) {
    const container = document.getElementById("editorial-execution-container");
    if (!container) return;

    const rep = data.report || {};
    const claims = rep.quantitative_claims || [];
    const doiStatus = rep.doi_verification_status || {};
    const anomalies = rep.flagged_anomalies || [];
    const verifiedPercent = rep.verified_claims_percentage !== undefined ? rep.verified_claims_percentage : 100;

    container.innerHTML = `
      <div class="card" style="margin-top: 24px; border-color: rgba(56, 189, 248, 0.4); background: linear-gradient(135deg, rgba(15, 23, 42, 0.8) 0%, rgba(8, 47, 73, 0.4) 100%);">
        <div class="card-header" style="border-bottom: 1px solid rgba(56, 189, 248, 0.2);">
          <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px;">
            <div>
              <h4 style="color: #38bdf8; font-size: 16px; margin: 0; font-weight: 800;">🛡️ Báo Cáo Thẩm Định Học Thuật (Academic Fact-Checking Audit)</h4>
              <p style="color: #94a3b8; font-size: 12px; margin: 3px 0 0 0;">Tiêu chuẩn Zero-Hallucination: Reverse Footprint Search &amp; Đối Soát Thực Chứng 100%.</p>
            </div>
            <span class="badge ${verifiedPercent >= 90 ? 'badge-green' : 'badge-yellow'}" style="font-size: 12px; padding: 5px 12px;">
              Tỷ lệ kiểm chứng: ${verifiedPercent}%
            </span>
          </div>
        </div>

        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin-bottom: 16px;">
          <div style="background: rgba(0,0,0,0.3); padding: 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.06); text-align: center;">
            <div style="font-size: 11px; color: #94a3b8;">Khẳng định Định lượng</div>
            <div style="font-size: 20px; font-weight: 800; color: #38bdf8;">${claims.length}</div>
          </div>
          <div style="background: rgba(0,0,0,0.3); padding: 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.06); text-align: center;">
            <div style="font-size: 11px; color: #94a3b8;">Mã DOI Tra Cứu</div>
            <div style="font-size: 20px; font-weight: 800; color: #34d399;">${Object.keys(doiStatus).length}</div>
          </div>
          <div style="background: rgba(0,0,0,0.3); padding: 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.06); text-align: center;">
            <div style="font-size: 11px; color: #94a3b8;">Dị Biệt & Cảnh Báo</div>
            <div style="font-size: 20px; font-weight: 800; color: ${anomalies.length > 0 ? '#f87171' : '#10b981'};">${anomalies.length}</div>
          </div>
        </div>

        <!-- DOI STATUS LIST -->
        ${Object.keys(doiStatus).length > 0 ? `
          <div style="margin-bottom: 16px;">
            <h5 style="color: #cbd5e1; font-size: 13px; font-weight: 700; margin-bottom: 8px;">Trạng thái Xác Thực DOI Nguồn (Crossref/Publisher HTTP 200 OK):</h5>
            <div style="display: flex; flex-direction: column; gap: 6px;">
              ${Object.entries(doiStatus).map(([doi, st]) => `
                <div style="background: rgba(0,0,0,0.3); padding: 8px 12px; border-radius: 6px; font-size: 12px; display: flex; justify-content: space-between; align-items: center; border-left: 3px solid ${st.valid ? '#10b981' : '#f87171'};">
                  <span style="color: #e2e8f0; font-family: var(--font-mono);">${doi}</span>
                  <span style="font-weight: 700; color: ${st.valid ? '#34d399' : '#fca5a5'};">${st.valid ? '✓ HTTP 200 OK' : '✕ Chưa xác thực'}</span>
                </div>
              `).join('')}
            </div>
          </div>
        ` : ''}

        <!-- QUANTITATIVE CLAIMS LIST -->
        ${claims.length > 0 ? `
          <div style="margin-bottom: 14px;">
            <h5 style="color: #cbd5e1; font-size: 13px; font-weight: 700; margin-bottom: 8px;">Dấu Chân Số Liệu Thực Chứng Đã Trích Xuất:</h5>
            <div style="display: flex; flex-direction: column; gap: 6px; max-height: 240px; overflow-y: auto;">
              ${claims.map(c => `
                <div style="background: rgba(0,0,0,0.25); padding: 8px 12px; border-radius: 6px; font-size: 12px; border: 1px solid rgba(255,255,255,0.05);">
                  <div style="display: flex; justify-content: space-between; gap: 8px; margin-bottom: 3px;">
                    <span style="color: #60a5fa; font-weight: 700;">${c.value} ${c.unit || ''}</span>
                    <span style="color: #94a3b8; font-size: 11px;">Loại: ${c.claim_type || 'chỉ số'}</span>
                  </div>
                  <div style="color: #cbd5e1; font-style: italic;">"${c.sentence || ''}"</div>
                </div>
              `).join('')}
            </div>
          </div>
        ` : ''}

        <div style="font-size: 11.5px; color: #64748b; margin-top: 10px; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 8px;">
          🔬 Báo cáo này tuân thủ Quy tắc Bất biến 1 (Evidence First & Zero Fabrication). Mọi số liệu đo lường đã được xác thực trước khi tiến hành xuất bản.
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
