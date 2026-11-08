// static/js/harvester.js
/**
 * Data & Paper Harvester (In-Memory Search & On-Demand Workspace Save)
 * Đồng bộ toàn diện theo quy trình Bước 1 (Từ khóa đa ngôn ngữ / Boolean Query) 
 * và Bước 2 (Tìm kiếm, Sàng lọc & Phân tách 2 Bảng Học Thuật theo chuẩn Skill Viết Chuyên Nghiệp 3.1)
 */

const HarvesterUI = {
  keywords: [],
  currentPapers: [],
  progressLogs: [],

  // ─── PHẦN 1: THIẾT KẾ TỪ KHÓA & BOOLEAN QUERY (TƯƠNG ĐƯƠNG BƯỚC 1) ─────────

  async generateKeywordsAndQuery() {
    if (window.App && App.requireAuth && !App.requireAuth('sinh Từ khóa & Boolean Query')) return;
    const topicInput = document.getElementById("harvester-topic");
    const topic = topicInput ? topicInput.value.trim() : "";
    if (!topic) {
      App.toast("Vui lòng nhập chủ đề / câu hỏi nghiên cứu.", "warning");
      if (topicInput) {
        topicInput.focus();
        topicInput.style.borderColor = "#f59e0b";
        setTimeout(() => { if (topicInput) topicInput.style.borderColor = ""; }, 2000);
      }
      return;
    }

    const btn = document.getElementById("btn-harvester-generate-kw");
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = '<span class="spinner-btn"></span> <span>Đang phân tích & sinh từ khóa...</span>';
    }

    try {
      App.toast("Đang phân tích chuyên sâu & sinh từ khóa đa ngôn ngữ...", "info");
      const res = await fetch("/api/harvester/query", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...((window.AuthManager && AuthManager.token) ? { "Authorization": `Bearer ${AuthManager.token}` } : {})
        },
        body: JSON.stringify({ topic })
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || data.message || "Lỗi máy chủ");
      }

      // Initialize keywords list
      const rawKws = data.keywords || [];
      if (rawKws.length > 0) {
        this.keywords = rawKws.map(kw => ({ text: kw, checked: true }));
      } else {
        this.keywords = [
          { text: topic, checked: true },
          { text: data.translated_title || "Academic Study", checked: true }
        ];
      }

      // Render keyword chips
      const box = document.getElementById("harvester-keywords-box");
      if (box) box.style.display = "block";
      this.renderKeywordChips();

      // Update textareas
      const enEl = document.getElementById("harvester-boolean-en");
      const viEl = document.getElementById("harvester-boolean-vi");
      if (enEl) enEl.value = data.boolean_en || "";
      if (viEl) viEl.value = data.boolean_vi || "";

      // Also set default custom query in Search section
      const customQEl = document.getElementById("harvester-custom-query");
      if (customQEl && !customQEl.value) {
        customQEl.value = data.boolean_en || topic;
      }

      const msg = data.translated_title ? `Đã dịch: "${data.translated_title}" & sinh Boolean Query thành công!` : "Đã sinh Boolean Query thành công!";
      App.toast(msg, "success");

    } catch (e) {
      App.toast("Lỗi tạo từ khóa: " + e.message, "error");
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = "⚡ Sinh Từ Khóa & Query";
      }
    }
  },

  renderKeywordChips() {
    const container = document.getElementById("harvester-keyword-chips");
    if (!container) return;

    if (!this.keywords || this.keywords.length === 0) {
      container.innerHTML = `<span style="font-size: 11.5px; color: #94a3b8;">Chưa có từ khóa nào. Bấm '+ Thêm từ khóa' để thêm.</span>`;
      return;
    }

    container.innerHTML = this.keywords.map((kw, idx) => `
      <div style="display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; border-radius: 20px; font-size: 11.5px; font-weight: 600; cursor: pointer; transition: all 0.2s; ${kw.checked ? 'background: rgba(59, 130, 246, 0.25); color: #93c5fd; border: 1px solid rgba(59, 130, 246, 0.6);' : 'background: rgba(255, 255, 255, 0.05); color: #64748b; border: 1px solid rgba(255, 255, 255, 0.1);'}" onclick="HarvesterUI.toggleKeywordChip(${idx})">
        <span>${kw.checked ? '✓' : '○'}</span>
        <span>${kw.text}</span>
        <span onclick="event.stopPropagation(); HarvesterUI.removeKeywordChip(${idx})" style="color: #f87171; font-weight: 700; margin-left: 2px; padding: 0 2px;" title="Xóa thẻ này">✕</span>
      </div>
    `).join('');
  },

  toggleKeywordChip(idx) {
    if (this.keywords[idx]) {
      this.keywords[idx].checked = !this.keywords[idx].checked;
      this.renderKeywordChips();
      this.rebuildBooleanQueries();
    }
  },

  removeKeywordChip(idx) {
    this.keywords.splice(idx, 1);
    this.renderKeywordChips();
    this.rebuildBooleanQueries();
  },

  promptAddKeyword() {
    const kw = prompt("Nhập từ khóa hoặc thuật ngữ chuyên ngành mới:");
    if (kw && kw.trim()) {
      this.keywords.push({ text: kw.trim(), checked: true });
      this.renderKeywordChips();
      this.rebuildBooleanQueries();
    }
  },

  rebuildBooleanQueries() {
    const activeKws = this.keywords.filter(k => k.checked).map(k => k.text);
    if (activeKws.length === 0) return;

    const enEl = document.getElementById("harvester-boolean-en");
    const viEl = document.getElementById("harvester-boolean-vi");
    const customQEl = document.getElementById("harvester-custom-query");

    const quoted = activeKws.map(k => k.includes(' ') ? `"${k}"` : k).join(' AND ');
    if (enEl) enEl.value = quoted;
    if (viEl) viEl.value = quoted;
    if (customQEl) customQEl.value = quoted;
  },

  copyQuery(elementId) {
    const el = document.getElementById(elementId);
    if (el && el.value) {
      navigator.clipboard.writeText(el.value).then(() => {
        App.toast("📋 Đã sao chép chuỗi Boolean Query!", "success");
      }).catch(() => {
        el.select();
        document.execCommand("copy");
        App.toast("📋 Đã sao chép chuỗi Boolean Query!", "success");
      });
    } else {
      App.toast("Chưa có chuỗi Boolean Query để sao chép.", "warning");
    }
  },

  useQueryForSearch(elementId, lang = 'en') {
    const el = document.getElementById(elementId);
    const query = el ? el.value.trim() : "";
    if (!query) {
      App.toast("Chưa có chuỗi Boolean Query để sử dụng.", "warning");
      return;
    }

    const customQEl = document.getElementById("harvester-custom-query");
    if (customQEl) customQEl.value = query;

    const langSel = document.getElementById("harvester-lang-select");
    if (langSel) langSel.value = lang;

    App.toast(`Đã áp dụng Boolean Query (${lang.toUpperCase()}) cho Phần 2! Bấm Tìm Kiếm để quét.`, "info");
    
    const s2 = document.getElementById("harvester-custom-query");
    if (s2) s2.scrollIntoView({ behavior: 'smooth', block: 'center' });
  },

  onLanguageChange(lang) {
    const enEl = document.getElementById("harvester-boolean-en");
    const viEl = document.getElementById("harvester-boolean-vi");
    const customQEl = document.getElementById("harvester-custom-query");
    const topic = document.getElementById("harvester-topic")?.value?.trim() || "";

    if (lang === "vi" && viEl && viEl.value) {
      if (customQEl) customQEl.value = viEl.value;
    } else if (lang === "en" && enEl && enEl.value) {
      if (customQEl) customQEl.value = enEl.value;
    } else if (topic && customQEl && !customQEl.value) {
      customQEl.value = topic;
    }
  },

  // ─── PHẦN 2: TÌM KIẾM, SÀNG LỌC & PHÂN TÁCH 2 BẢNG (TƯƠNG ĐƯƠNG BƯỚC 2) ───

  async startHarvest(customQuery = null) {
    if (window.App && App.requireAuth && !App.requireAuth('tìm kiếm và thu thập tài liệu')) return;
    const topicInput = document.getElementById("harvester-topic")?.value?.trim() || "";
    const customQInput = document.getElementById("harvester-custom-query")?.value?.trim() || "";
    const maxPapers = parseInt(document.getElementById("harvester-max-papers")?.value || 10);
    const source = document.getElementById("harvester-source-select")?.value || "all";
    const language = document.getElementById("harvester-lang-select")?.value || "en";

    const queryToSend = customQuery || customQInput || topicInput;
    if (!queryToSend) {
      App.toast("Vui lòng nhập chủ đề hoặc câu truy vấn tìm kiếm.", "warning");
      const targetInput = document.getElementById("harvester-custom-query") || document.getElementById("harvester-topic");
      if (targetInput) {
        targetInput.focus();
        targetInput.style.borderColor = "#f59e0b";
        setTimeout(() => { if (targetInput) targetInput.style.borderColor = ""; }, 2000);
      }
      return;
    }

    const btn = document.getElementById("btn-start-harvest");
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = '<span class="spinner-btn"></span> <span>Đang tìm kiếm & sàng lọc...</span>';
    }

    const resultsList = document.getElementById("harvester-results-list");
    if (resultsList) {
      resultsList.innerHTML = `
        <div class="loading-indicator-box">
          <div class="spinner-lg" style="border-top-color: #3b82f6; border-right-color: #60a5fa; box-shadow: 0 0 16px rgba(59, 130, 246, 0.35);"></div>
          <div class="loading-indicator-title">🌐 Đang quét & phân loại tài liệu khoa học theo chuẩn Skill 3.1<span class="loading-pulse-dots"></span></div>
          <div class="loading-indicator-desc">Truy vấn đồng thời EuropePMC, arXiv, OpenAlex, CrossRef, Scholar cho: <em>"${queryToSend}"</em>. Ngôn ngữ: <strong>${language.toUpperCase()}</strong>. Tối ưu RAM, phân tách 2 bảng minh bạch.</div>
        </div>
      `;
    }

    App.toast(`Đang tìm kiếm bài báo cho '${queryToSend.substring(0, 45)}...'...`, "info");

    try {
      const res = await fetch("/api/harvester/search", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...((window.AuthManager && AuthManager.token) ? { "Authorization": `Bearer ${AuthManager.token}` } : {})
        },
        body: JSON.stringify({
          topic: topicInput || queryToSend,
          custom_query: queryToSend,
          max_papers: maxPapers,
          source,
          language
        })
      });

      if (!res.ok) {
        let errMessage = `Máy chủ phản hồi mã lỗi ${res.status}`;
        try {
          const errData = await res.json();
          errMessage = errData.detail || errData.message || errMessage;
        } catch (_) {
          const rawText = await res.text();
          if (rawText && rawText.length < 150) errMessage = rawText;
        }
        App.toast("Lỗi từ máy chủ: " + errMessage, "error");
        if (resultsList) {
          resultsList.innerHTML = `<div style="background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.4); padding: 14px; border-radius: 8px; color: #fca5a5; font-size: 13px; margin-top: 14px;">❌ <strong>Không thể tìm kiếm:</strong> ${errMessage}</div>`;
        }
        return;
      }

      const data = await res.json();
      if (data.status === "success") {
        this.currentPapers = data.papers || [];
        App.toast(data.message || `Đã tìm thấy ${this.currentPapers.length} bài báo!`, "success");
        this.renderHarvestResults(this.currentPapers);
      } else {
        App.toast(data.detail || data.message || "Lỗi tìm kiếm dữ liệu", "error");
      }
    } catch (e) {
      App.toast("Lỗi kết nối hoặc xử lý dữ liệu: " + e.message, "error");
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = "🔍 Tìm Kiếm & Sàng Lọc Bài Báo";
      }
    }
  },

  renderHarvestResults(papers) {
    const listEl = document.getElementById("harvester-results-list");
    if (!listEl) return;

    if (!papers || papers.length === 0) {
      listEl.innerHTML = `
        <div class="empty-state" id="harvester-empty-state">
          <div class="empty-state-icon">🔬</div>
          <h4>Chưa có kết quả tìm kiếm</h4>
          <p>Nhập chủ đề và nhấn <strong>"🔍 Tìm Kiếm & Sàng Lọc Bài Báo"</strong> để bắt đầu quét các kho học thuật.</p>
        </div>
      `;
      return;
    }

    const total = papers.length;
    const downloadable = papers.filter(p => p.is_downloadable !== false);
    const manual = papers.filter(p => p.is_downloadable === false);
    const alreadySavedCount = papers.filter(p => p.already_saved || p.is_saved_to_disk).length;

    let html = `
      <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 12px; padding: 18px;">
        <!-- BẢNG 1: CÓ THỂ TẢI TOÀN VĂN MỞ -->
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 8px;">
          <div>
            <span class="gate-badge unlocked" style="font-size: 12px; background: rgba(16, 185, 129, 0.2); color: #34d399; border-color: rgba(16, 185, 129, 0.4);">
              📄 Danh Sách Có Thể Tải Toàn Văn (${downloadable.length}/${total} bài)
            </span>
            <span id="harvester-selected-badge" style="font-size: 11.5px; background: rgba(59, 130, 246, 0.2); color: #93c5fd; padding: 3px 10px; border-radius: 12px; font-weight: 700; margin-left: 6px;">
              Đã có trong thư viện: ${alreadySavedCount} bài
            </span>
          </div>
          ${downloadable.length > 0 ? `
            <div style="display: flex; gap: 6px; align-items: center;">
              <button type="button" class="btn btn-secondary btn-sm" onclick="HarvesterUI.toggleSelectAll(true)" style="padding: 3px 10px; font-size: 11px;">Tích Chọn Tất Cả</button>
              <button type="button" class="btn btn-outline btn-sm" onclick="HarvesterUI.toggleSelectAll(false)" style="padding: 3px 8px; font-size: 11px;">Bỏ Chọn</button>
            </div>
          ` : ''}
        </div>

        ${downloadable.length > 0 ? `
          <div class="candidate-table-wrapper">
            <table style="width: 100%; border-collapse: collapse; font-size: 12.5px;">
              <thead style="position: sticky; top: 0; background: #0f172a; z-index: 2; box-shadow: 0 1px 0 rgba(255,255,255,0.1);">
                <tr style="color: #94a3b8; text-align: left;">
                  <th style="padding: 10px 10px; width: 45px; text-align: center;">Chọn</th>
                  <th style="padding: 10px 10px;">Tên Bài Báo Khoa Học & Toàn Văn Mở</th>
                  <th style="padding: 10px 10px; width: 150px;">Tác Giả & Năm</th>
                  <th style="padding: 10px 10px; width: 130px;">Cơ Sở Dữ Liệu</th>
                  <th style="padding: 10px 10px; width: 140px; text-align: center;">Trạng Thái / Thao Tác</th>
                </tr>
              </thead>
              <tbody>
                ${downloadable.map((p, idx) => {
                  const isSaved = p.already_saved || p.is_saved_to_disk;
                  const cleanRelDocx = (p.rel_path || (p.file_name ? `Tai_Lieu/${p.file_name}` : '')).replace(/\\/g, '/');
                  const cleanRelMd = (p.rel_md_path || (p.md_file_name ? `Tai_Lieu/${p.md_file_name}` : cleanRelDocx.replace(/\.docx$/i, '.md'))).replace(/\\/g, '/');

                  return `
                    <tr id="harvester-row-${p.id}" class="candidate-row" style="background: ${isSaved ? 'rgba(16, 185, 129, 0.06)' : 'transparent'};">
                      <td style="padding: 10px; text-align: center;">
                        <input type="checkbox" class="harvester-candidate-cb" data-id="${p.id}" ${isSaved ? '' : 'checked'} onchange="HarvesterUI.updateSelectedCount()" style="cursor: pointer; width: 15px; height: 15px;">
                      </td>
                      <td style="padding: 10px;">
                        <a href="${p.source_url || (p.doi ? 'https://doi.org/' + p.doi : '#')}" target="_blank" rel="noopener noreferrer" style="color: #60a5fa; text-decoration: none; font-weight: 600; display: block; line-height: 1.45;">
                          ${idx + 1}. ${p.title} ↗
                        </a>
                        ${p.journal ? `<div style="font-size: 11px; color: #94a3b8; font-style: italic; margin-top: 3px;">📖 ${p.journal}</div>` : ''}
                        ${p.doi ? `<div style="font-size: 10.5px; color: #64748b; font-family: monospace; margin-top: 2px;">DOI: ${p.doi}</div>` : ''}
                        <div style="margin-top: 3px;">
                          ${p.pdf_url ? '<span class="badge badge-green" style="font-size: 10px; padding: 1px 6px;">📥 Có PDF Gốc</span>' : '<span class="badge badge-blue" style="font-size: 10px; padding: 1px 6px;">📑 Toàn văn PMC XML / Preprints</span>'}
                        </div>
                      </td>
                      <td style="padding: 10px; color: #cbd5e1;">
                        <strong style="color: #f8fafc; font-size: 12px;">${p.author || 'Nhiều tác giả'}</strong>
                        <div style="font-size: 11px; color: #94a3b8; margin-top: 2px;">📅 Năm: <strong>${p.year || '2024'}</strong></div>
                      </td>
                      <td style="padding: 10px; color: #94a3b8; font-size: 11px;">
                        <span style="font-weight: 600; color: #cbd5e1;">${p.source || 'EuropePMC'}</span>
                        <div style="margin-top: 3px;"><span class="badge badge-blue" style="font-size: 10px; padding: 1px 6px;">${(p.language || 'Quốc tế').toUpperCase()}</span></div>
                      </td>
                      <td id="harvester-status-${p.id}" style="padding: 10px; text-align: center;">
                        <div style="display: flex; flex-direction: column; gap: 4px; align-items: center;">
                          ${isSaved ? `
                            <span class="badge badge-green" style="font-size: 10.5px; margin-bottom: 2px; display: inline-block;">✅ Đã lưu vào thư viện</span>
                            ${cleanRelDocx ? `<button type="button" onclick="App.openFileInSystem('${cleanRelDocx}')" class="btn btn-primary btn-sm" style="padding: 3px 8px; font-size: 10.5px; width: 100%; font-weight: 600;">📝 Mở Word</button>` : ''}
                          ` : `
                            <span class="badge badge-yellow" style="font-size: 10.5px; font-weight: 600;">🆕 Sẵn sàng tải</span>
                          `}
                          <button type="button" onclick="HarvesterUI.readPaperWithAi('${p.id}')" class="btn btn-secondary btn-sm" style="padding: 3px 8px; font-size: 10.5px; width: 100%; background: #4f46e5; border-color: #4f46e5; color: #fff; font-weight: 600;" title="AI đọc toàn văn & kiểm tra tính toàn vẹn">
                            🤖 AI Đọc Văn Bản
                          </button>
                          ${p.pdf_url ? `
                            <button type="button" onclick="HarvesterUI.downloadPaperPdf('${p.id}')" class="btn btn-outline btn-sm" style="padding: 3px 8px; font-size: 10.5px; width: 100%; color: #38bdf8; border-color: #38bdf8;" title="Tải file PDF gốc về máy tính">
                              📥 Tải PDF Gốc
                            </button>
                          ` : ''}
                        </div>
                      </td>
                    </tr>
                  `;
                }).join('')}
              </tbody>
            </table>
          </div>

          <!-- Download Action Bar -->
          <div style="margin-top: 14px; display: flex; gap: 10px; align-items: center; justify-content: space-between; flex-wrap: wrap;">
            <button id="btn-save-selected-harvester" class="btn btn-primary btn-lg" onclick="HarvesterUI.saveSelectedPapers()">
              📥 Bắt Đầu Tải Toàn Văn (.docx & .md) Cho Các Bài Đã Chọn (${downloadable.length} bài)
            </button>
            <button class="btn btn-outline btn-lg" onclick="App.openFileInSystem ? App.openFileInSystem('Tai_Lieu') : null">
              📂 Mở Thư Mục Tai_Lieu/
            </button>
          </div>
        ` : `
          <div style="padding: 14px; background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 8px; color: #fde68a; font-size: 13px;">
            ⚠️ Không tìm thấy bài báo có bản mở trực tiếp cho truy vấn này. Vui lòng xem danh sách giới hạn bản quyền bên dưới để tự tra cứu hoặc nạp file.
          </div>
        `}

        <!-- BẢNG 2: BÀI BÁO GIỚI HẠN BẢN QUYỀN / TỰ TRA CỨU FILE -->
        ${manual.length > 0 ? `
          <div style="margin-top: 22px; background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(245, 158, 11, 0.35); border-radius: 12px; padding: 16px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; flex-wrap: wrap; gap: 8px;">
              <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 16px;">🔒</span>
                <h5 style="color: #fde68a; font-size: 13.5px; margin: 0; font-weight: 700;">
                  Danh Mục Bài Báo Giới Hạn Bản Quyền / Cần Tự Tra Cứu File (${manual.length} bài)
                </h5>
              </div>
              <span style="font-size: 11.5px; color: #fbbf24; background: rgba(245, 158, 11, 0.15); padding: 3px 10px; border-radius: 12px; font-weight: 600;">
                Không có toàn văn mở tự động
              </span>
            </div>
            <p style="font-size: 12px; color: #cbd5e1; margin-bottom: 12px; line-height: 1.5;">
              Các công trình khoa học dưới đây bị khóa bởi nhà xuất bản hoặc chỉ có chỉ mục trích dẫn. Bạn có thể bấm <strong>"🔍 Tìm trên Scholar"</strong> để tìm file PDF, hoặc bấm <strong>"📤 Nạp File PDF/Word (.md)"</strong> để hệ thống tự động bóc tách sang dữ liệu <code>.md</code> chuẩn Skill 3.1:
            </p>
            <div class="candidate-table-wrapper">
              <table style="width: 100%; border-collapse: collapse; font-size: 12px;">
                <thead style="background: rgba(0,0,0,0.4);">
                  <tr style="color: #94a3b8; text-align: left;">
                    <th style="padding: 8px 10px; width: 30px;">#</th>
                    <th style="padding: 8px 10px;">Tên Bài Báo</th>
                    <th style="padding: 8px 10px; width: 140px;">Tác Giả & Năm</th>
                    <th style="padding: 8px 10px; width: 130px;">Nguồn & Tình Trạng</th>
                    <th style="padding: 8px 10px; width: 210px; text-align: center;">Tra Cứu & Nạp File Sang .MD</th>
                  </tr>
                </thead>
                <tbody>
                  ${manual.map((p, mIdx) => {
                    const isUploaded = p.is_saved_to_disk || p.already_saved || p.is_user_uploaded;
                    const cleanRelDocx = (p.rel_path || (p.file_name ? `Tai_Lieu/${p.file_name}` : '')).replace(/\\/g, '/');
                    const cleanRelMd = (p.rel_md_path || (p.md_file_name ? `Tai_Lieu/${p.md_file_name}` : cleanRelDocx.replace(/\.docx$/i, '.md'))).replace(/\\/g, '/');

                    return `
                      <tr id="harvester-manual-row-${p.id}" style="border-bottom: 1px solid rgba(255,255,255,0.05); background: ${isUploaded ? 'rgba(16, 185, 129, 0.08)' : 'transparent'};">
                        <td style="padding: 8px 10px; color: #64748b;">${mIdx + 1}</td>
                        <td style="padding: 8px 10px;">
                          <a href="${p.source_url || (p.doi ? 'https://doi.org/' + p.doi : 'https://scholar.google.com/scholar?q=' + encodeURIComponent(p.title))}" target="_blank" rel="noopener noreferrer" style="color: #60a5fa; text-decoration: none; font-weight: 700; display: block; line-height: 1.45; margin-bottom: 2px;">
                            ${mIdx + 1}. ${p.title} ↗
                          </a>
                          ${p.journal ? `<span style="font-size: 11px; color: #94a3b8; font-style: italic;">📖 ${p.journal}</span>` : ''}
                          ${p.doi ? `<div style="font-size: 10.5px; color: #64748b; font-family: monospace; margin-top: 2px;">DOI: ${p.doi}</div>` : ''}
                          ${isUploaded ? `<div style="margin-top: 4px;"><span class="badge badge-green" style="font-size: 10px; padding: 2px 6px;">✅ Đã có dữ liệu toàn văn (.md & .docx)</span></div>` : ''}
                        </td>
                        <td style="padding: 8px 10px; color: #cbd5e1;">
                          <div>${p.author || 'Nhiều tác giả'}</div>
                          <div style="font-size: 11px; color: #94a3b8;">📅 Năm: ${p.year || '2024'}</div>
                        </td>
                        <td style="padding: 8px 10px; color: #f59e0b; font-size: 11px;">
                          ${p.source || 'CrossRef / Google Scholar'}
                          <div style="font-size: 10px; color: ${isUploaded ? '#34d399' : '#f87171'}; margin-top: 2px;">
                            ${isUploaded ? '📥 Đã nạp vào Kho Tri Thức' : '🔒 Giới hạn truy cập'}
                          </div>
                        </td>
                        <td style="padding: 8px 10px; text-align: center;">
                          <div id="harvester-manual-actions-${p.id}" style="display: flex; flex-direction: column; gap: 4px; align-items: center;">
                            ${isUploaded ? `
                              <button type="button" class="btn btn-primary btn-sm" onclick="App.openFileInSystem('${cleanRelDocx}')" style="padding: 3px 8px; font-size: 10.5px; width: 100%; font-weight: 600;">
                                📝 Mở File Word
                              </button>
                              <button type="button" class="btn btn-outline btn-sm" onclick="App.openFileInSystem('${cleanRelMd}')" style="padding: 3px 8px; font-size: 10.5px; width: 100%; font-weight: 600;">
                                📄 Xem Dữ Liệu .MD
                              </button>
                            ` : `
                              <a href="https://scholar.google.com/scholar?q=${encodeURIComponent(p.title)}" target="_blank" rel="noopener noreferrer" class="btn btn-secondary btn-sm" style="padding: 3px 8px; font-size: 10.5px; width: 100%; text-decoration: none;">
                                🔍 Tìm trên Scholar ↗
                              </a>
                              ${p.source_url ? `
                                <a href="${p.source_url}" target="_blank" rel="noopener noreferrer" class="btn btn-outline btn-sm" style="padding: 3px 8px; font-size: 10.5px; width: 100%; text-decoration: none;">
                                  🔗 Trang Nguồn ↗
                                </a>
                              ` : ''}
                              <input type="file" id="harvester-upload-input-${p.id}" accept=".pdf,.docx,.doc,.txt,.md" style="display:none;" onchange="HarvesterUI.uploadPaperFile('${p.id}', this)">
                              <button type="button" class="btn btn-primary btn-sm" onclick="document.getElementById('harvester-upload-input-${p.id}').click()" style="padding: 4px 8px; font-size: 10.5px; width: 100%; font-weight: 700; background: #0284c7; border-color: #0284c7;">
                                📤 Nạp File PDF/Word (.md)
                              </button>
                            `}
                          </div>
                        </td>
                      </tr>
                    `;
                  }).join('')}
                </tbody>
              </table>
            </div>
          </div>
        ` : ''}

        <!-- LIVE PROGRESS STREAM (Tích lũy & Lưu trữ thời gian thực) -->
        <div id="harvester-live-progress-box" style="${(this.progressLogs && this.progressLogs.length > 0) ? 'display: block;' : 'display: none;'} margin-top: 16px; background: rgba(0,0,0,0.3); border: 1px solid rgba(59, 130, 246, 0.35); border-radius: 10px; padding: 14px;">
          <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; flex-wrap: wrap; gap: 8px;">
            <h5 style="color: #f8fafc; font-size: 13px; margin: 0; display: flex; align-items: center; gap: 6px; font-weight: 700;">
              <span>⚡</span> Tiến Trình Tải & Chuyển Đổi Sang Word (.docx) Thời Gian Thực:
            </h5>
            <div style="display: flex; gap: 8px; align-items: center;">
              <span id="harvester-stream-counter" style="font-size: 12px; font-weight: 700; color: #38bdf8; background: rgba(56, 189, 248, 0.15); padding: 2px 8px; border-radius: 12px;">
                ${this.progressLogs ? this.progressLogs.length : 0} tài liệu
              </span>
              <button type="button" class="btn btn-outline btn-sm" onclick="HarvesterUI.clearProgressLogs()" style="padding: 2px 8px; font-size: 11px;" title="Xóa danh sách tiến trình đã lưu">
                🗑️ Xóa Nhật Ký
              </button>
            </div>
          </div>
          <div id="harvester-stream-log" style="max-height: 200px; overflow-y: auto; display: flex; flex-direction: column; gap: 6px;">
            ${(this.progressLogs || []).map(item => `
              <div style="font-size: 12px; display: flex; justify-content: space-between; align-items: center; background: rgba(255,255,255,0.04); padding: 6px 10px; border-radius: 6px;">
                <div style="flex: 1; margin-right: 8px;">
                  <span style="color: #94a3b8;">[${item.time}]</span>
                  <strong style="color: #cbd5e1; margin-left: 4px;">${item.title}</strong>
                  ${item.message ? `<div style="font-size: 11px; color: #38bdf8; margin-top: 2px;">${item.message}</div>` : ''}
                </div>
                <div style="display: flex; gap: 6px; align-items: center;">
                  <span class="badge ${item.status === 'error' ? 'badge-red' : 'badge-green'}" style="font-size: 11px;">
                    ${item.status === 'error' ? '❌ Thất bại' : '✅ Thành công'}
                  </span>
                  ${item.cleanRel ? `<button type="button" onclick="App.openFileInSystem('${item.cleanRel.replace(/\\/g, '/')}')" class="btn btn-primary btn-sm" style="padding: 2px 7px; font-size: 10.5px;">📝 Mở</button>` : ''}
                </div>
              </div>
            `).join('')}
          </div>
        </div>
      </div>
    `;

    listEl.innerHTML = html;
    this.updateSelectedCount();
  },

  toggleSelectAll(selectAll) {
    const cbs = document.querySelectorAll(".harvester-candidate-cb");
    cbs.forEach(cb => { cb.checked = selectAll; });
    this.updateSelectedCount();
  },

  updateSelectedCount() {
    const checked = document.querySelectorAll(".harvester-candidate-cb:checked").length;
    const btn = document.getElementById("btn-save-selected-harvester");
    if (btn) {
      btn.innerText = `📥 Bắt Đầu Tải Toàn Văn (.docx & .md) Cho Các Bài Đã Chọn (${checked} bài)`;
    }
  },

  async saveSelectedPapers() {
    const checkedBoxes = Array.from(document.querySelectorAll(".harvester-candidate-cb:checked"));
    const selectedIds = checkedBoxes.map(cb => cb.getAttribute("data-id")).filter(Boolean);

    if (selectedIds.length === 0) {
      App.toast("Vui lòng tích chọn ít nhất 1 bài báo để tải toàn văn!", "warning");
      return;
    }

    const btn = document.getElementById("btn-save-selected-harvester");
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = `<span class="spinner-btn"></span> <span>Đang tải và tạo file Word...</span>`;
    }

    const progressBox = document.getElementById("harvester-live-progress-box");
    const streamLog = document.getElementById("harvester-stream-log");
    const streamCounter = document.getElementById("harvester-stream-counter");
    if (progressBox) progressBox.style.display = "block";

    let completedCount = 0;
    if (!this.progressLogs) this.progressLogs = [];

    for (let i = 0; i < selectedIds.length; i++) {
      const pid = selectedIds[i];
      const paper = this.currentPapers.find(p => p.id === pid);
      const title = paper ? paper.title : pid;
      const currentTime = new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit', second: '2-digit' });

      if (streamCounter) streamCounter.innerText = `${i + 1} / ${selectedIds.length} (Tổng ${this.progressLogs.length + 1})`;

      const logItem = document.createElement("div");
      logItem.style.cssText = "font-size: 12px; display: flex; justify-content: space-between; align-items: center; background: rgba(255,255,255,0.03); padding: 6px 10px; border-radius: 6px;";
      logItem.innerHTML = `
        <div style="flex: 1; margin-right: 8px;">
          <span style="color: #94a3b8;">[${i + 1}/${selectedIds.length} · ${currentTime}]</span>
          <strong style="color: #cbd5e1; margin-left: 4px;">${title}</strong>
        </div>
        <span class="badge badge-yellow" style="font-size: 11px; white-space: nowrap;">⏳ Đang tải toàn văn...</span>
      `;
      if (streamLog) {
        streamLog.prepend(logItem);
      }

      const tableStatusCell = document.getElementById(`harvester-status-${pid}`);
      if (tableStatusCell) {
        tableStatusCell.innerHTML = `<span class="badge badge-yellow" style="font-size: 10.5px;">⏳ Đang tải...</span>`;
      }

      try {
        const res = await fetch("/api/harvest/save-to-zotero", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            ...((window.AuthManager && AuthManager.token) ? { "Authorization": `Bearer ${AuthManager.token}` } : {})
          },
          body: JSON.stringify({
            paper_id: pid,
            paper_data: paper
          })
        });

        const data = await res.json();
        if (data.status === "success") {
          completedCount++;
          const cleanRel = (data.rel_path || `Tai_Lieu/${data.file_name}`).replace(/\\/g, '/');

          if (paper) {
            paper.is_saved_to_disk = true;
            paper.already_saved = true;
            paper.file_name = data.file_name;
            paper.md_file_name = data.md_file_name;
            paper.rel_path = cleanRel;
            paper.rel_md_path = (data.rel_md_path || cleanRel.replace(/\.docx$/i, '.md')).replace(/\\/g, '/');
          }

          this.progressLogs.unshift({
            id: pid,
            title: title,
            status: "success",
            badgeText: "Đã tạo .docx & .md",
            fileName: data.file_name,
            cleanRel: cleanRel,
            time: currentTime
          });

          logItem.innerHTML = `
            <div style="flex: 1; margin-right: 8px;">
              <span style="color: #34d399;">✅ [${currentTime}]</span>
              <strong style="color: #f8fafc; margin-left: 4px;">${title}</strong>
              <div style="font-size: 11px; color: #94a3b8; margin-top: 2px;">📁 ${data.file_name}</div>
            </div>
            <div style="display: flex; gap: 4px; align-items: center;">
              <span class="badge badge-green" style="font-size: 10.5px;">Đã tạo .docx & .md</span>
              <button type="button" onclick="App.openFileInSystem('${cleanRel}')" class="btn btn-primary btn-sm" style="padding: 2px 8px; font-size: 10.5px;">📝 Mở đọc</button>
            </div>
          `;

          if (tableStatusCell) {
            tableStatusCell.innerHTML = `
              <span class="badge badge-green" style="font-size: 11px; margin-bottom: 4px; display: inline-block;">✅ Đã lưu</span>
              <button type="button" onclick="App.openFileInSystem('${cleanRel}')" class="btn btn-primary btn-sm" style="padding: 2px 8px; font-size: 10.5px; margin-top: 2px;">📝 Mở</button>
            `;
          }
        } else {
          const errDetail = data.detail || data.message || "Lỗi lưu file";
          logItem.innerHTML = `
            <div style="flex: 1; margin-right: 8px;">
              <span style="color: #f87171;">❌ [${currentTime}]</span>
              <strong style="color: #cbd5e1; margin-left: 4px;">${title}</strong>
            </div>
            <span class="badge badge-red" style="font-size: 10.5px;">${errDetail}</span>
          `;
          if (tableStatusCell) {
            tableStatusCell.innerHTML = `<span class="badge badge-red" style="font-size: 10.5px;">❌ ${errDetail}</span>`;
          }
        }
      } catch (e) {
        logItem.innerHTML = `
          <div style="flex: 1; margin-right: 8px;">
            <span style="color: #f87171;">❌ [${currentTime}]</span>
            <span style="color: #cbd5e1; margin-left: 4px;">${title}</span>
          </div>
          <span class="badge badge-red" style="font-size: 10.5px;">${e.message || "Lỗi kết nối"}</span>
        `;
        if (tableStatusCell) {
          tableStatusCell.innerHTML = `<span class="badge badge-red" style="font-size: 10.5px;">❌ Lỗi kết nối</span>`;
        }
      }
    }

    if (btn) {
      btn.disabled = false;
      btn.innerHTML = `📥 Bắt Đầu Tải Toàn Văn (.docx & .md) Cho Các Bài Đã Chọn`;
    }

    if (streamCounter) {
      streamCounter.innerText = `${this.progressLogs.length} tài liệu đã tải`;
    }

    App.toast(`Đã hoàn tất tải & tạo bản thảo Word / MD cho ${completedCount} tài liệu!`, "success");
  },

  async uploadPaperFile(paperId, inputEl) {
    if (!inputEl || !inputEl.files || !inputEl.files[0]) return;
    const file = inputEl.files[0];
    const paper = this.currentPapers ? this.currentPapers.find(p => p.id === paperId) : null;

    const actionBox = document.getElementById(`harvester-manual-actions-${paperId}`);
    if (actionBox) {
      actionBox.innerHTML = `<span class="badge badge-yellow" style="font-size: 11px; padding: 6px 10px;">⏳ Đang bóc tách sang .MD...</span>`;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("paper_id", paperId);
    if (paper) {
      formData.append("paper_data", JSON.stringify(paper));
    }

    try {
      const res = await fetch("/api/harvest/upload-paper-file", {
        method: "POST",
        headers: {
          ...((window.AuthManager && AuthManager.token) ? { "Authorization": `Bearer ${AuthManager.token}` } : {})
        },
        body: formData
      });

      const data = await res.json();
      if (!res.ok || data.status === "error") {
        const errMsg = data.message || "Không thể chuyển đổi tệp PDF.";
        App.toast(errMsg, "error");
        
        if (data.error_code === "PDF_SCAN_UNEXTRACTABLE") {
          alert(`⚠️ CẢNH BÁO TỆP PDF KHÔNG THỂ CHUYỂN ĐỔI:

${errMsg}`);
        }

        if (actionBox) {
          actionBox.innerHTML = `
            <a href="https://scholar.google.com/scholar?q=${encodeURIComponent(paper ? paper.title : '')}" target="_blank" rel="noopener noreferrer" class="btn btn-secondary btn-sm" style="padding: 3px 8px; font-size: 10.5px; width: 100%;">
              🔍 Tìm trên Scholar ↗
            </a>
            <input type="file" id="harvester-upload-input-${paperId}" accept=".pdf,.docx,.doc,.txt,.md" style="display:none;" onchange="HarvesterUI.uploadPaperFile('${paperId}', this)">
            <button type="button" class="btn btn-primary btn-sm" onclick="document.getElementById('harvester-upload-input-${paperId}').click()" style="padding: 4px 8px; font-size: 10.5px; width: 100%; font-weight: 700; background: #0284c7; border-color: #0284c7;">
              📤 Thử lại Tải Lên (.md)
            </button>
          `;
        }
        return;
      }

      App.toast(data.message || "Đã nạp và chuyển đổi tệp thành công sang dữ liệu .md và .docx!", "success");

      if (paper) {
        paper.is_saved_to_disk = true;
        paper.already_saved = true;
        paper.is_downloadable = true;
        paper.is_user_uploaded = true;
        paper.file_name = data.file_name;
        paper.md_file_name = data.md_file_name;
        paper.rel_path = data.rel_path;
        paper.rel_md_path = data.rel_md_path;
        paper.abs_path = data.abs_path;
      }

      if (!this.progressLogs) this.progressLogs = [];
      const currentTime = new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
      this.progressLogs.unshift({
        id: paperId,
        time: currentTime,
        title: paper ? paper.title : file.name,
        fileName: data.file_name,
        cleanRel: data.rel_path,
        status: 'success',
        badgeText: 'Đã nạp .MD & .DOCX',
        message: `Đã nạp tệp '${file.name}' (${data.word_count || 0} từ) & lưu ${data.md_file_name}`
      });

      this.renderHarvestResults(this.currentPapers);

    } catch (e) {
      App.toast(`Lỗi gửi tệp: ${e.message}`, "error");
      if (actionBox) {
        actionBox.innerHTML = `
          <input type="file" id="harvester-upload-input-${paperId}" accept=".pdf,.docx,.doc,.txt,.md" style="display:none;" onchange="HarvesterUI.uploadPaperFile('${paperId}', this)">
          <button type="button" class="btn btn-primary btn-sm" onclick="document.getElementById('harvester-upload-input-${paperId}').click()" style="padding: 4px 8px; font-size: 10.5px; width: 100%;">
            📤 Tải Lên PDF/Word (.md)
          </button>
        `;
      }
    }
  },

  clearProgressLogs() {
    this.progressLogs = [];
    const streamLog = document.getElementById("harvester-stream-log");
    const streamCounter = document.getElementById("harvester-stream-counter");
    if (streamLog) streamLog.innerHTML = "";
    if (streamCounter) streamCounter.innerText = "0 tài liệu";
    App.toast("Đã làm sạch nhật ký tiến trình tải.", "info");
  },

  async clearTempCache() {
    try {
      await fetch("/api/harvester/clear-cache", {
        method: "POST",
        headers: {
          ...((window.AuthManager && AuthManager.token) ? { "Authorization": `Bearer ${AuthManager.token}` } : {})
        }
      });
      this.currentPapers = [];
      this.renderHarvestResults([]);
      App.toast("Đã giải phóng bộ nhớ tạm thành công!", "info");
    } catch (e) {
      App.toast("Lỗi xóa cache: " + e.message, "error");
    }
  },

  quickSearchReactome(kw) {
    const input = document.getElementById("harvester-reactome-query");
    if (input) input.value = kw;
    this.searchReactome(kw);
  },

  async searchReactome(customQuery = null) {
    const queryInput = document.getElementById("harvester-reactome-query");
    const query = customQuery || (queryInput ? queryInput.value.trim() : "");
    if (!query) {
      App.toast("Vui lòng nhập từ khóa con đường sinh học Reactome.", "warning");
      return;
    }

    const btn = document.getElementById("btn-harvester-reactome-search");
    const resultsContainer = document.getElementById("harvester-reactome-results");
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = '<span class="spinner-btn"></span> <span>Đang truy vấn Reactome...</span>';
    }
    if (resultsContainer) {
      resultsContainer.innerHTML = '<div style="text-align: center; padding: 20px; color: #6ee7b7;"><span class="spinner-btn"></span> Đang kết nối Reactome Content Service API...</div>';
    }

    try {
      const res = await fetch("/api/harvester/reactome-search", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...((window.AuthManager && AuthManager.token) ? { "Authorization": `Bearer ${AuthManager.token}` } : {})
        },
        body: JSON.stringify({ query, max_results: 6 })
      });
      const data = await res.json();
      if (res.ok && data.status === "success") {
        this.renderReactomeResults(data.pathways || []);
        App.toast(`Đã tìm thấy ${data.total_found || 0} con đường sinh học Reactome!`, "success");
      } else {
        App.toast(data.detail || data.message || "Không tìm thấy con đường sinh học phù hợp", "warning");
        if (resultsContainer) {
          resultsContainer.innerHTML = `<div style="padding: 12px; color: #fca5a5; font-size: 12.5px;">${data.detail || "Không có dữ liệu phù hợp."}</div>`;
        }
      }
    } catch (e) {
      App.toast("Lỗi tra cứu Reactome: " + e.message, "error");
      if (resultsContainer) {
        resultsContainer.innerHTML = `<div style="padding: 12px; color: #fca5a5; font-size: 12.5px;">Lỗi: ${e.message}</div>`;
      }
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = "🧬 Tra Cứu Reactome";
      }
    }
  },

  renderReactomeResults(pathways) {
    const container = document.getElementById("harvester-reactome-results");
    if (!container) return;

    if (!pathways || pathways.length === 0) {
      container.innerHTML = `<div style="padding: 14px; text-align: center; color: #94a3b8; font-size: 12.5px;">Không có con đường sinh học nào cho từ khóa này. Thử 'nitrogen', 'ammonia', 'detoxification', hoặc 'glycolysis'.</div>`;
      return;
    }

    container.innerHTML = `
      <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 12px; margin-top: 10px;">
        ${pathways.map((pw, i) => `
          <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(52, 211, 153, 0.3); border-radius: 8px; padding: 12px; display: flex; flex-direction: column; justify-content: space-between;">
            <div>
              <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; margin-bottom: 6px;">
                <span style="font-size: 11px; font-weight: 700; color: #34d399; background: rgba(52, 211, 153, 0.15); padding: 2px 6px; border-radius: 4px;">${pw.stId || pw.id || 'R-HSA'}</span>
                <span style="font-size: 11px; color: #94a3b8;">${pw.species || 'All Species'}</span>
              </div>
              <h5 style="color: #f8fafc; font-size: 13px; font-weight: 700; margin: 0 0 6px 0;">${pw.name || 'Con đường sinh học'}</h5>
              <div style="font-size: 11.5px; color: #cbd5e1; line-height: 1.5; margin-bottom: 10px;">
                Phản ứng cấu thành: <strong>${pw.reactions_count || (pw.events ? pw.events.length : 0) || 'N/A'}</strong> phản ứng hóa sinh.
              </div>
            </div>
            <div style="display: flex; gap: 6px; margin-top: 8px;">
              <a href="https://reactome.org/content/detail/${encodeURIComponent(pw.stId || pw.id || '')}" target="_blank" rel="noopener noreferrer" class="btn btn-ghost btn-sm" style="flex: 1; font-size: 11px; text-align: center; padding: 5px 6px; color: #6ee7b7; border: 1px solid rgba(52,211,153,0.3);">
                🌐 Mở Reactome
              </a>
              <button type="button" class="btn btn-green btn-sm" onclick="HarvesterUI.importReactomeToVault('${encodeURIComponent(pw.stId || pw.id || '')}', '${encodeURIComponent(pw.name || '')}', '${encodeURIComponent(pw.species || '')}', ${pw.reactions_count || 0})" style="flex: 1.3; font-size: 11px; font-weight: 700; padding: 5px 8px;">
                📥 Thêm Vào Vault
              </button>
            </div>
          </div>
        `).join('')}
      </div>
    `;
  },

  async importReactomeToVault(stIdEnc, nameEnc, speciesEnc, reactionsCount) {
    const stId = decodeURIComponent(stIdEnc);
    const name = decodeURIComponent(nameEnc);
    const species = decodeURIComponent(speciesEnc);

    App.toast(`Đang nạp con đường sinh học ${stId} vào Evidence Vault...`, "info");
    try {
      const res = await fetch("/api/evidence-db/extract-and-feed", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...((window.AuthManager && AuthManager.token) ? { "Authorization": `Bearer ${AuthManager.token}` } : {})
        },
        body: JSON.stringify({
          text_content: `Con đường sinh học: ${name} (${stId}, Loài: ${species}). Bao gồm ${reactionsCount} phản ứng hóa sinh được kiểm chứng thực nghiệm từ cơ sở dữ liệu Reactome Content Service. Được chuẩn hóa và sử dụng làm cơ sở đối soát sinh học trong nghiên cứu.`,
          document_id: `reactome_${stId.toLowerCase().replace(/[^a-z0-9_]/g, '_')}`,
          metadata: {
            title: `Reactome Pathway: ${name} [${stId}]`,
            authors: ["Reactome Consortium", "Fabregat, A.", "Sidiropoulos, K."],
            year: 2024,
            doi: "10.1093/nar/gky1079",
            journal: "Nucleic Acids Research",
            source_type: "biological_database"
          }
        })
      });
      const data = await res.json();
      if (res.ok && data.status === "success") {
        App.toast(`✨ Đã nạp thành công "${name}" vào Evidence Vault!`, "success");
        if (window.PipelineUI && PipelineUI.refreshVaultList) {
          PipelineUI.refreshVaultList();
        }
      } else {
        App.toast(data.detail || data.message || "Lỗi lưu vào Evidence Vault", "error");
      }
    } catch (e) {
      App.toast("Lỗi nạp vào Vault: " + e.message, "error");
    }
  }
};

// Global Window Export
window.HarvesterUI = HarvesterUI;
