// Zotero Word Dynamic Citation Converter & Reference Normalizer (Universal Academic & Legal Edition)
const ZoteroUI = {
  selectedFile: null,
  selectedMode: 'A',
  selectedSubtab: 'convert',
  normStyle: 'APA',
  normInputMode: 'text',
  normDocxFile: null,
  lastNormItems: [],

  init() {
    const dropZone = document.getElementById("zotero-drop-zone");
    const fileInput = document.getElementById("zotero-file-input");

    if (dropZone && fileInput) {
      ["dragenter", "dragover"].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
          e.preventDefault();
          e.stopPropagation();
          dropZone.classList.add("dragover");
        }, false);
      });

      ["dragleave", "dragend"].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
          e.preventDefault();
          e.stopPropagation();
          dropZone.classList.remove("dragover");
        }, false);
      });

      dropZone.addEventListener("drop", (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.remove("dragover");
        if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files.length > 0) {
          this.handleFileSelected(e.dataTransfer.files[0]);
        }
      }, false);
    }

    this.setupNormDocxDropZone();
    this.checkZoteroStatus();
  },

  switchSubtab(subtabId) {
    this.selectedSubtab = subtabId;
    document.querySelectorAll('.zotero-subtab-btn').forEach(btn => {
      btn.classList.toggle('active', btn.getAttribute('data-zsubtab') === subtabId);
    });
    document.querySelectorAll('.zotero-subtab-pane').forEach(pane => {
      pane.style.display = (pane.id === `zotero-pane-${subtabId}`) ? 'block' : 'none';
    });
  },

  selectMode(mode) {
    this.selectedMode = mode;
    document.querySelectorAll('[data-zmode]').forEach(el => {
      el.classList.toggle('active', el.getAttribute('data-zmode') === mode);
      const radio = el.querySelector('input[type="radio"]');
      if (radio) radio.checked = (el.getAttribute('data-zmode') === mode);
    });
  },

  selectNormStyle(style) {
    this.normStyle = style;
    document.querySelectorAll('[data-norm-style]').forEach(el => {
      const isMatch = el.getAttribute('data-norm-style') === style;
      el.classList.toggle('active', isMatch);
      const radio = el.querySelector('input[type="radio"]');
      if (radio) radio.checked = isMatch;
    });
  },

  switchNormInputMode(mode) {
    this.normInputMode = mode;
    const textBtn = document.getElementById('zotero-norm-mode-text-btn');
    const docxBtn = document.getElementById('zotero-norm-mode-docx-btn');
    const textPane = document.getElementById('zotero-norm-text-pane');
    const docxPane = document.getElementById('zotero-norm-docx-pane');

    if (textBtn) textBtn.classList.toggle('active', mode === 'text');
    if (docxBtn) docxBtn.classList.toggle('active', mode === 'docx');
    if (textPane) textPane.style.display = (mode === 'text') ? 'block' : 'none';
    if (docxPane) docxPane.style.display = (mode === 'docx') ? 'block' : 'none';
  },

  setupNormDocxDropZone() {
    const dropZone = document.getElementById("zotero-norm-docx-drop-zone");
    if (!dropZone) return;

    ['dragenter', 'dragover'].forEach(eventName => {
      dropZone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.add("dragover");
      }, false);
    });

    ['dragleave', 'dragend'].forEach(eventName => {
      dropZone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.remove("dragover");
      }, false);
    });

    dropZone.addEventListener("drop", (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropZone.classList.remove("dragover");
      if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        this.handleNormDocxSelected(e.dataTransfer.files[0]);
      }
    }, false);
  },

  handleNormDocxSelected(file) {
    if (!file.name.toLowerCase().endsWith(".docx")) {
      if (window.App) App.toast("Vui lòng chọn tệp Word (.docx).", "error");
      return;
    }
    this.normDocxFile = file;
    const label = document.getElementById("zotero-norm-selected-docx-label");
    if (label) label.innerHTML = `📄 <strong>Đã chọn:</strong> <span style="color:#60a5fa; font-weight:700;">${file.name}</span> (${(file.size / 1024).toFixed(1)} KB)`;
    if (window.App) App.toast(`Đã nạp file '${file.name}'! Sẵn sàng chuẩn hóa.`, "info");
  },

  async checkZoteroStatus() {
    const textEl = document.getElementById("zotero-status-text");
    if (!textEl) return;
    textEl.innerText = "Đang kiểm tra Zotero...";

    try {
      const res = await fetch("/api/zotero/status");
      if (res.ok) {
        const data = await res.json();
        if (data.desktop_running) {
          textEl.innerHTML = `🟢 <strong>Zotero Desktop Sẵn Sàng</strong> (${data.total_library_items} tài liệu)`;
        } else if (data.has_cloud_config) {
          textEl.innerHTML = `☁️ <strong>Zotero Cloud Kết Nối</strong> (${data.total_library_items} tài liệu)`;
        } else {
          textEl.innerHTML = `📁 <strong>Zotero Cục Bộ</strong> (${data.total_library_items} tài liệu)`;
        }
      } else {
        textEl.innerText = "⚠️ Chưa mở Zotero Desktop";
      }
    } catch (e) {
      textEl.innerText = "📁 Zotero Sẵn sàng";
    }
  },

  handleFileSelected(file) {
    if (!file.name.toLowerCase().endsWith(".docx")) {
      if (window.App) App.toast("Vui lòng chọn tệp Microsoft Word (.docx).", "error");
      return;
    }
    this.selectedFile = file;
    const label = document.getElementById("zotero-selected-file-name");
    if (label) label.innerText = `📄 Đã chọn: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
    const btn = document.getElementById("zotero-convert-btn");
    if (btn) btn.disabled = false;
  },

  async startConversion() {
    if (window.App && App.requireAuth && !App.requireAuth('chuyển đổi mã trích dẫn Zotero')) return;
    if (!this.selectedFile) {
      if (window.App) App.toast("Vui lòng chọn hoặc kéo thả file Word .docx trước.", "warning");
      return;
    }

    const mode = this.selectedMode || "A";
    const btn = document.getElementById("zotero-convert-btn");
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = '<span class="spinner-btn"></span> <span>Đang quét & chuyển đổi mã Zotero...</span>';
    }

    const resultBox = document.getElementById("zotero-result-container");
    if (resultBox) {
      resultBox.innerHTML = `
        <div class="loading-indicator-box">
          <div class="spinner-lg" style="border-top-color: #06b6d4; border-right-color: #38bdf8; box-shadow: 0 0 16px rgba(6, 182, 212, 0.25);"></div>
          <div class="loading-indicator-title">📚 Đang quét trích dẫn & nhúng trường động Zotero (CSL Codes)<span class="loading-pulse-dots"></span></div>
          <div class="loading-indicator-desc">Phân tích văn bản chuẩn APA 7th & Văn bản Pháp luật (Chế độ ${mode}), đồng bộ mã trường CSL Field Codes vào tệp Word.</div>
        </div>
      `;
    }

    if (window.App) App.toast(`Đang phân tích trích dẫn theo Chế độ ${mode}...`, "info");

    const formData = new FormData();
    formData.append("file", this.selectedFile);

    try {
      const res = await fetch(`/api/zotero/convert?mode=${encodeURIComponent(mode)}`, {
        method: "POST",
        headers: (window.AuthManager && AuthManager.token) ? { "Authorization": `Bearer ${AuthManager.token}` } : {},
        body: formData
      });

      const data = await res.json().catch(() => ({ detail: `Máy chủ phản hồi lỗi ${res.status}: ${res.statusText}` }));

      if (res.ok && data.status === "success") {
        if (window.App) App.toast(data.message || "Chuyển đổi Zotero thành công!", "success");
        this.renderConversionResult(data);
        if (window.App && App.updateStatus) App.updateStatus();
      } else {
        const errMsg = data.detail || data.message || "Lỗi chuyển đổi mã trích dẫn";
        if (window.App) App.toast(errMsg, "error");
        if (resultBox) {
          resultBox.innerHTML = `
            <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.4); padding: 14px; border-radius: 8px; color: #fca5a5; font-size: 13px; margin-top: 14px;">
              ❌ <strong>Không thể chuyển đổi:</strong> ${errMsg}
            </div>
          `;
        }
      }
    } catch (e) {
      if (window.App) App.toast("Lỗi kết nối máy chủ: " + e.message, "error");
      if (resultBox) {
        resultBox.innerHTML = `
          <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.4); padding: 14px; border-radius: 8px; color: #fca5a5; font-size: 13px; margin-top: 14px;">
            ❌ <strong>Lỗi kết nối:</strong> ${e.message}
          </div>
        `;
      }
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = "🚀 Bắt Đầu Chuyển Đổi Sang Zotero Field Codes";
      }
    }
  },

  renderConversionResult(data) {
    const resEl = document.getElementById("zotero-result-container");
    if (!resEl) return;

    const st = data.stats || {};
    const refs = st.references_parsed || [];
    const harvested = data.harvested_files || [];
    const rel = data.rel_path || data.output_rel_path || (data.output_filename ? `Zotero_Converted/${data.output_filename}` : '') || '';
    const convertedName = data.output_filename || 'Bản thảo Word đã nhúng mã Zotero';
    const doiSoatRel = data.doi_soat_file_rel || '';
    const taiLieuRel = data.tai_lieu_dir_rel || '';
    const dedicatedRel = data.dedicated_dir_rel || '';

    const matchRate = st.total_citations_found > 0 
      ? Math.round((st.matched_citations / st.total_citations_found) * 100) 
      : 100;

    resEl.innerHTML = `
      <div class="card" style="margin-top: 20px; border-color: rgba(6, 182, 212, 0.4); background: rgba(15, 23, 42, 0.7);">
        <div class="card-header" style="border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 14px;">
          <div>
            <h4 style="color: #38bdf8; font-size: 16.5px; font-weight:800; margin:0 0 4px 0;">🎉 Chuyển Đổi Zotero Thành Công (${data.mode || 'MODE A'})!</h4>
            <p style="color: #cbd5e1; font-size: 12.5px; margin: 0;">Tệp Word đã được nhúng Dynamic CSL Field Codes sẵn sàng Refresh trên Microsoft Word.</p>
          </div>
          ${dedicatedRel ? `
            <button class="btn btn-green btn-sm" onclick="App.openWindowsExplorer('${dedicatedRel}')" style="font-weight:700;">
              📂 Mở Thư Mục Phiên Làm Việc
            </button>
          ` : ''}
        </div>

        <!-- STATS SUMMARY -->
        <div class="grid-4" style="margin: 18px 0; gap: 12px;">
          <div class="stat-card" style="background: rgba(255,255,255,0.03); padding:14px; border-radius:10px; border:1px solid rgba(255,255,255,0.08);">
            <div class="stat-label" style="font-size:11px; color:#94a3b8;">Trích Dẫn Phát Hiện</div>
            <div class="stat-value text-cyan" style="font-size:22px; font-weight:800;">${st.total_citations_found || 0}</div>
          </div>
          <div class="stat-card" style="background: rgba(255,255,255,0.03); padding:14px; border-radius:10px; border:1px solid rgba(255,255,255,0.08);">
            <div class="stat-label" style="font-size:11px; color:#94a3b8;">Khớp Thư Viện Zotero</div>
            <div class="stat-value text-green" style="font-size:22px; font-weight:800;">${st.matched_citations || 0}</div>
          </div>
          <div class="stat-card" style="background: rgba(255,255,255,0.03); padding:14px; border-radius:10px; border:1px solid rgba(255,255,255,0.08);">
            <div class="stat-label" style="font-size:11px; color:#94a3b8;">Tài Liệu Nạp Mới (Mode B)</div>
            <div class="stat-value" style="font-size:22px; font-weight:800; color:#fbbf24;">${harvested.length}</div>
          </div>
          <div class="stat-card" style="background: rgba(255,255,255,0.03); padding:14px; border-radius:10px; border:1px solid rgba(255,255,255,0.08);">
            <div class="stat-label" style="font-size:11px; color:#94a3b8;">Tỷ Lệ Khớp Nối</div>
            <div class="stat-value text-purple" style="font-size:22px; font-weight:800;">${matchRate}%</div>
          </div>
        </div>

        <!-- ACTION BUTTONS -->
        <div style="display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 20px;">
          <button class="btn btn-primary btn-md" onclick="App.openFileInSystem('${rel}')" style="font-weight:700;">📝 Mở Bằng Microsoft Word</button>
          <button class="btn btn-secondary btn-md" onclick="App.downloadFile('${rel}')" style="font-weight:700;">📥 Tải File Word Nhúng Mã (.docx)</button>
          ${doiSoatRel ? `
            <button class="btn btn-outline btn-md" onclick="App.openFileInSystem('${doiSoatRel}')" style="color:#6ee7b7; border-color:rgba(16,185,129,0.4); font-weight:700;">
              📊 Mở Bảng Đối Soát (.docx)
            </button>
          ` : ''}
          ${taiLieuRel ? `
            <button class="btn btn-outline btn-md" onclick="App.openWindowsExplorer('${taiLieuRel}')" style="color:#93c5fd; border-color:rgba(59,130,246,0.4);">
              📁 Mở Thư Mục Tài Liệu (${harvested.length} bài)
            </button>
          ` : ''}
        </div>

        <!-- HARVESTED PAPERS LIST (MODE B) -->
        ${harvested.length > 0 ? `
          <div style="margin-bottom: 18px; background: rgba(16, 185, 129, 0.05); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 10px; padding: 14px;">
            <h5 style="color: #6ee7b7; font-size: 13.5px; margin: 0 0 10px 0; font-weight:700;">📰 Tài Liệu Đã Tự Động Tra Cứu &amp; Nạp Vào Zotero (Mode B):</h5>
            <div style="display: flex; flex-direction: column; gap: 8px;">
              ${harvested.map(h => `
                <div style="background: rgba(255,255,255,0.03); padding: 8px 12px; border-radius: 6px; border-left: 3px solid #10b981; display: flex; justify-content: space-between; align-items: center; gap:10px;">
                  <span style="font-size: 12px; color: #e2e8f0; font-weight:600;">${h.title || 'Bài báo khoa học'} <span style="color:#94a3b8; font-weight:normal;">(${h.year || 'Năm'})</span></span>
                  <span class="badge badge-green" style="white-space:nowrap; font-size:10.5px;">✓ Đã nạp Zotero</span>
                </div>
              `).join('')}
            </div>
          </div>
        ` : ''}

        <!-- INSTRUCTIONS FOR USER -->
        <div style="background: rgba(59, 130, 246, 0.06); border: 1px solid rgba(59, 130, 246, 0.2); border-radius: 10px; padding: 14px;">
          <h5 style="color: #93c5fd; font-size: 13px; font-weight: 700; margin: 0 0 8px 0;">📋 Các bước hoàn tất trên Microsoft Word:</h5>
          <ol style="margin: 0; padding-left: 20px; font-size: 12px; color: #cbd5e1; line-height: 1.7;">
            <li>Mở file Word đã tải về bằng Microsoft Word.</li>
            <li>Trên thanh công cụ, chọn thẻ <strong>Zotero</strong> ➔ bấm nút <strong>Refresh</strong> để Zotero tự động kết nối toàn bộ trích dẫn.</li>
            <li>Để sinh danh mục tham khảo tự động chuẩn APA: Đặt con trỏ ở cuối bài ➔ bấm nút <strong>Add/Edit Bibliography</strong>.</li>
          </ol>
        </div>
      </div>
    `;
  },

  // =========================================================================
  // SUBTAB 2: CITATION NORMALIZER (APA, MLA, ISO 690 & GOOGLE SCHOLAR SYNC)
  // =========================================================================

  async runCitationNormalization() {
    if (window.App && App.requireAuth && !App.requireAuth('chuẩn hóa trích dẫn')) return;

    const style = this.normStyle || 'APA';
    const btn = document.getElementById('zotero-btn-run-norm');
    const resultContainer = document.getElementById('zotero-norm-results-container');

    if (this.normInputMode === 'text') {
      const rawText = document.getElementById('zotero-norm-text-input')?.value?.trim();
      if (!rawText) {
        if (window.App) App.toast("Vui lòng nhập hoặc dán danh sách trích dẫn thô vào ô văn bản.", "warning");
        return;
      }

      if (btn) {
        btn.disabled = true;
        btn.innerHTML = `⏳ Đang tra cứu Google Scholar &amp; Chuẩn hóa theo chuẩn ${style}...`;
      }

      if (resultContainer) {
        resultContainer.innerHTML = `
          <div class="loading-indicator-box" style="margin-top:20px;">
            <div class="spinner-lg" style="border-top-color: #3b82f6; border-right-color: #60a5fa;"></div>
            <div class="loading-indicator-title">🔍 Đang tra cứu Google Scholar, OpenAlex &amp; CrossRef<span class="loading-pulse-dots"></span></div>
            <div class="loading-indicator-desc">Đối soát siêu dữ liệu 100% thực tế, trích xuất DOI và định dạng theo chuẩn ${style}...</div>
          </div>
        `;
      }

      try {
        const res = await fetch('/api/zotero/normalize-references', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(window.AuthManager && AuthManager.token ? { "Authorization": `Bearer ${AuthManager.token}` } : {})
          },
          body: JSON.stringify({
            references: rawText,
            style: style
          })
        });

        const data = await res.json();
        if (res.ok && data.success) {
          this.lastNormItems = data.items || [];
          this.renderNormResults(data);
          if (window.App) App.toast(data.message || `Chuẩn hóa ${data.total} tài liệu thành công!`, "success");
        } else {
          throw new Error(data.detail || data.message || "Lỗi chuẩn hóa trích dẫn");
        }
      } catch (e) {
        if (window.App) App.toast("Lỗi: " + e.message, "error");
        if (resultContainer) {
          resultContainer.innerHTML = `
            <div style="background:rgba(239,68,68,0.1); border:1px solid #ef4444; border-radius:10px; padding:14px; color:#fca5a5; font-size:13px; margin-top:16px;">
              ❌ <strong>Lỗi chuẩn hóa:</strong> ${e.message}
            </div>
          `;
        }
      } finally {
        if (btn) {
          btn.disabled = false;
          btn.innerHTML = "🚀 Chuẩn Hóa Danh Mục &amp; Tra Cứu Google Scholar";
        }
      }
    } else {
      // Docx mode
      if (!this.normDocxFile) {
        if (window.App) App.toast("Vui lòng chọn hoặc kéo thả tệp Word (.docx) chứa danh mục tham khảo.", "warning");
        return;
      }

      if (btn) {
        btn.disabled = true;
        btn.innerHTML = `⏳ Đang quét file Word &amp; Chuẩn hóa mục Tham khảo theo ${style}...`;
      }

      if (resultContainer) {
        resultContainer.innerHTML = `
          <div class="loading-indicator-box" style="margin-top:20px;">
            <div class="spinner-lg" style="border-top-color: #10b981; border-right-color: #34d399;"></div>
            <div class="loading-indicator-title">📄 Đang quét mục Tài Liệu Tham Khảo trong file Word<span class="loading-pulse-dots"></span></div>
            <div class="loading-indicator-desc">Tra cứu DOI thực tế trên Google Scholar &amp; OpenAlex, cập nhật In-Place Word DOM và xuất file RIS...</div>
          </div>
        `;
      }

      const formData = new FormData();
      formData.append('file', this.normDocxFile);
      formData.append('style', style);

      try {
        const res = await fetch('/api/zotero/normalize-docx-references', {
          method: 'POST',
          headers: (window.AuthManager && AuthManager.token) ? { "Authorization": `Bearer ${AuthManager.token}` } : {},
          body: formData
        });

        const data = await res.json();
        if (res.ok && data.success) {
          this.lastNormItems = data.items || [];
          this.renderNormDocxResults(data);
          if (window.App) App.toast(data.message || "Chuẩn hóa file Word thành công!", "success");
        } else {
          throw new Error(data.detail || data.message || "Lỗi chuẩn hóa file Word");
        }
      } catch (e) {
        if (window.App) App.toast("Lỗi: " + e.message, "error");
        if (resultContainer) {
          resultContainer.innerHTML = `
            <div style="background:rgba(239,68,68,0.1); border:1px solid #ef4444; border-radius:10px; padding:14px; color:#fca5a5; font-size:13px; margin-top:16px;">
              ❌ <strong>Lỗi chuẩn hóa file Word:</strong> ${e.message}
            </div>
          `;
        }
      } finally {
        if (btn) {
          btn.disabled = false;
          btn.innerHTML = "🚀 Chuẩn Hóa Danh Mục &amp; Tra Cứu Google Scholar";
        }
      }
    }
  },

  renderNormResults(data) {
    const container = document.getElementById('zotero-norm-results-container');
    if (!container) return;

    const items = data.items || [];
    const style = data.style || 'APA';

    container.innerHTML = `
      <div class="card" style="margin-top: 20px; border-color: rgba(59,130,246,0.4); background: rgba(15, 23, 42, 0.75);">
        <div class="card-header" style="border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 14px;">
          <div>
            <h4 style="color: #60a5fa; font-size: 16.5px; font-weight:800; margin:0 0 4px 0;">
              🎉 Kết Quả Chuẩn Hóa Danh Mục Tham Khảo (${style})
            </h4>
            <p style="color: #cbd5e1; font-size: 12.5px; margin: 0;">
              Đã đối soát với Google Scholar / OpenAlex / CrossRef và định dạng chuẩn mực 100% có liên kết DOI/URL.
            </p>
          </div>
          <div style="display:flex; gap:8px; flex-wrap:wrap;">
            <a href="${data.ris_file_url}" download="Zotero_References.ris" class="btn btn-success btn-sm" style="font-weight:700; display:inline-flex; align-items:center; gap:6px;">
              📥 Tải File .RIS (Zotero)
            </a>
            <a href="${data.bib_file_url}" download="Zotero_References.bib" class="btn btn-secondary btn-sm" style="font-weight:700; display:inline-flex; align-items:center; gap:6px;">
              📥 Tải File .BIB (BibTeX)
            </a>
            <button type="button" class="btn btn-primary btn-sm" onclick="ZoteroUI.syncToZotero()" style="font-weight:700; display:inline-flex; align-items:center; gap:6px;">
              🔄 Nạp Trực Tiếp Vào Zotero
            </button>
          </div>
        </div>

        <!-- STATS BADGES -->
        <div class="grid-4" style="margin: 16px 0; gap: 12px;">
          <div class="stat-card" style="background: rgba(255,255,255,0.03); padding:12px; border-radius:8px;">
            <div class="stat-label" style="font-size:11px; color:#94a3b8;">Tổng Tài Liệu</div>
            <div class="stat-value text-cyan" style="font-size:20px; font-weight:800;">${data.total || items.length}</div>
          </div>
          <div class="stat-card" style="background: rgba(255,255,255,0.03); padding:12px; border-radius:8px;">
            <div class="stat-label" style="font-size:11px; color:#94a3b8;">Có Mã DOI Thực Tế</div>
            <div class="stat-value text-green" style="font-size:20px; font-weight:800;">${data.matched_dois || 0}</div>
          </div>
          <div class="stat-card" style="background: rgba(255,255,255,0.03); padding:12px; border-radius:8px;">
            <div class="stat-label" style="font-size:11px; color:#94a3b8;">Chuẩn Định Dạng</div>
            <div class="stat-value text-purple" style="font-size:20px; font-weight:800;">${style}</div>
          </div>
          <div class="stat-card" style="background: rgba(255,255,255,0.03); padding:12px; border-radius:8px;">
            <div class="stat-label" style="font-size:11px; color:#94a3b8;">Tệp Zotero Sẵn Sàng</div>
            <div class="stat-value" style="font-size:20px; font-weight:800; color:#fbbf24;">.RIS / .BIB</div>
          </div>
        </div>

        <!-- FORMATTED CITATION LIST -->
        <div style="background: rgba(0,0,0,0.25); border: 1px solid rgba(255,255,255,0.06); border-radius: 10px; padding: 16px;">
          <h5 style="color: #93c5fd; font-size: 13.5px; margin: 0 0 12px 0; font-weight:700;">
            📋 Danh Mục Tài Liệu Tham Khảo Đã Chuẩn Hóa (${style}):
          </h5>
          <div style="display: flex; flex-direction: column; gap: 12px; max-height: 400px; overflow-y: auto;">
            ${items.map((it, idx) => `
              <div style="background: rgba(255,255,255,0.02); padding: 10px 14px; border-radius: 8px; border-left: 3px solid #3b82f6; font-size: 12.5px; line-height: 1.6; color: #e2e8f0;">
                <div style="margin-bottom:6px;">
                  <span style="font-weight:700; color:#60a5fa; margin-right:6px;">[${idx + 1}]</span>
                  ${it.html_citation || it.formatted_citation}
                </div>
                <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap; margin-top:6px; font-size:11px;">
                  <a href="https://scholar.google.com/scholar?q=${encodeURIComponent(it.title || it.raw_text)}" target="_blank" class="btn btn-ghost btn-sm" style="padding:2px 8px; font-size:11px; color:#93c5fd; border:1px solid rgba(59,130,246,0.3); border-radius:4px; text-decoration:none; display:inline-flex; align-items:center; gap:4px;">
                    🎓 Xem trên Google Scholar ↗
                  </a>
                  ${it.doi ? `
                    <span class="badge badge-green" style="font-size:10.5px;">DOI: ${it.doi}</span>
                    <a href="https://doi.org/${it.doi}" target="_blank" style="color:#6ee7b7; text-decoration:underline;">🔗 Mở bài báo gốc ↗</a>
                  ` : it.source_url ? `
                    <a href="${it.source_url}" target="_blank" style="color:#93c5fd; text-decoration:underline;">🔗 Mở liên kết tài liệu ↗</a>
                  ` : ''}
                </div>
              </div>
            `).join('')}
          </div>
        </div>
      </div>
    `;
  },

  renderNormDocxResults(data) {
    const container = document.getElementById('zotero-norm-results-container');
    if (!container) return;

    const items = data.items || [];
    const style = data.style || 'APA';

    container.innerHTML = `
      <div class="card" style="margin-top: 20px; border-color: rgba(16,185,129,0.4); background: rgba(15, 23, 42, 0.75);">
        <div class="card-header" style="border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 14px;">
          <div>
            <h4 style="color: #6ee7b7; font-size: 16.5px; font-weight:800; margin:0 0 4px 0;">
              🎉 Chuẩn Hóa File Word &amp; Danh Mục Tham Khảo Thành Công (${style})!
            </h4>
            <p style="color: #cbd5e1; font-size: 12.5px; margin: 0;">
              Đã cập nhật mục Tài Liệu Tham Khảo trong file Word theo chuẩn ${style} và sinh file .RIS / .BIB đồng hành.
            </p>
          </div>
          <div style="display:flex; gap:8px; flex-wrap:wrap;">
            <button type="button" class="btn btn-primary btn-sm" onclick="App.openFileInSystem('${data.rel_path}')" style="font-weight:700;">
              📝 Mở Trực Tiếp Trên Word
            </button>
            <a href="${data.file_url}" download="${data.output_filename}" class="btn btn-secondary btn-sm" style="font-weight:700;">
              ⬇️ Tải File Word (.docx)
            </a>
            <a href="${data.ris_file_url}" download="Zotero_Library.ris" class="btn btn-success btn-sm" style="font-weight:700;">
              📥 Tải File .RIS
            </a>
            <button type="button" class="btn btn-secondary btn-sm" onclick="ZoteroUI.syncToZotero()" style="font-weight:700;">
              🔄 Nạp Vào Zotero
            </button>
          </div>
        </div>

        <!-- STATS BADGES -->
        <div class="grid-4" style="margin: 16px 0; gap: 12px;">
          <div class="stat-card" style="background: rgba(255,255,255,0.03); padding:12px; border-radius:8px;">
            <div class="stat-label" style="font-size:11px; color:#94a3b8;">Tài Liệu Đã Quét</div>
            <div class="stat-value text-cyan" style="font-size:20px; font-weight:800;">${data.total_references || items.length}</div>
          </div>
          <div class="stat-card" style="background: rgba(255,255,255,0.03); padding:12px; border-radius:8px;">
            <div class="stat-label" style="font-size:11px; color:#94a3b8;">Khớp DOI Google Scholar</div>
            <div class="stat-value text-green" style="font-size:20px; font-weight:800;">${data.matched_dois || 0}</div>
          </div>
          <div class="stat-card" style="background: rgba(255,255,255,0.03); padding:12px; border-radius:8px;">
            <div class="stat-label" style="font-size:11px; color:#94a3b8;">Chuẩn Áp Dụng</div>
            <div class="stat-value text-purple" style="font-size:20px; font-weight:800;">${style}</div>
          </div>
          <div class="stat-card" style="background: rgba(255,255,255,0.03); padding:12px; border-radius:8px;">
            <div class="stat-label" style="font-size:11px; color:#94a3b8;">Vị Trí Lưu Tệp</div>
            <div class="stat-value" style="font-size:13px; font-weight:700; color:#fbbf24; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">workspace/${data.rel_path}</div>
          </div>
        </div>

        <!-- FORMATTED CITATION LIST -->
        <div style="background: rgba(0,0,0,0.25); border: 1px solid rgba(255,255,255,0.06); border-radius: 10px; padding: 16px;">
          <h5 style="color: #6ee7b7; font-size: 13.5px; margin: 0 0 12px 0; font-weight:700;">
            📋 Danh Mục Tham Khảo Đã Ghi Vào File Word (.docx):
          </h5>
          <div style="display: flex; flex-direction: column; gap: 10px; max-height: 350px; overflow-y: auto;">
            ${items.map((it, idx) => `
              <div style="background: rgba(255,255,255,0.02); padding: 8px 12px; border-radius: 6px; border-left: 3px solid #10b981; font-size: 12px; line-height: 1.5; color: #cbd5e1;">
                <div style="margin-bottom:4px;">
                  <span style="font-weight:700; color:#a7f3d0; margin-right:6px;">[${idx + 1}]</span>
                  ${it.html_citation || it.formatted_citation}
                </div>
                <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap; margin-top:4px; font-size:11px;">
                  <a href="https://scholar.google.com/scholar?q=${encodeURIComponent(it.title || it.raw_text)}" target="_blank" class="btn btn-ghost btn-sm" style="padding:1px 6px; font-size:10.5px; color:#a7f3d0; border:1px solid rgba(16,185,129,0.3); border-radius:4px; text-decoration:none;">
                    🎓 Xem trên Google Scholar ↗
                  </a>
                  ${it.doi ? `
                    <a href="https://doi.org/${it.doi}" target="_blank" style="color:#6ee7b7; text-decoration:underline;">🔗 DOI: ${it.doi} ↗</a>
                  ` : ''}
                </div>
              </div>
            `).join('')}
          </div>
        </div>
      </div>
    `;
  },

  async syncToZotero() {
    if (!this.lastNormItems || this.lastNormItems.length === 0) {
      if (window.App) App.toast("Chưa có danh sách tài liệu nào để nạp vào Zotero.", "warning");
      return;
    }

    if (window.App) App.toast("Đang đồng bộ danh mục tham khảo vào Zotero...", "info");

    try {
      const res = await fetch('/api/zotero/sync-references-to-zotero', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(window.AuthManager && AuthManager.token ? { "Authorization": `Bearer ${AuthManager.token}` } : {})
        },
        body: JSON.stringify({ items: this.lastNormItems })
      });

      const data = await res.json();
      if (res.ok && data.success) {
        if (window.App) App.toast(data.message || `Đã nạp ${data.desktop_synced || data.total} mục vào Zotero!`, "success");
        this.checkZoteroStatus();
      } else {
        throw new Error(data.detail || data.message || "Lỗi đồng bộ Zotero");
      }
    } catch (e) {
      if (window.App) App.toast("Lỗi nạp Zotero: " + e.message, "error");
    }
  }
};

document.addEventListener("DOMContentLoaded", () => ZoteroUI.init());
if (document.readyState === "complete" || document.readyState === "interactive") {
  ZoteroUI.init();
}

window.ZoteroUI = ZoteroUI;

