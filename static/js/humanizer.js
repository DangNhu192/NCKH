// Humanizer UI v1.1 / v3.2 — Turnitin Rephrase Pro, AI Detector Scanner, Wikipedia Tells & ContentBeta 300+, CS519.M11
const HumanizerUI = {
  selectedFile: null,
  currentPersona: "professor",
  currentCitationStyle: "apa7",

  init() {
    const dropZone = document.getElementById("humanizer-drop-zone");
    const fileInput = document.getElementById("humanizer-file-input");

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

  setPersona(persona) {
    this.currentPersona = persona;
    document.querySelectorAll(".persona-btn").forEach(btn => {
      if (btn.dataset.persona === persona) {
        btn.classList.add("active");
        btn.style.borderColor = "#38bdf8";
        btn.style.background = "rgba(56, 189, 248, 0.2)";
      } else {
        btn.classList.remove("active");
        btn.style.borderColor = "var(--border-color)";
        btn.style.background = "rgba(255, 255, 255, 0.05)";
      }
    });
    if (window.App) {
      const pNames = {
        "undergraduate": "Sinh Viên (Undergraduate)",
        "graduate": "Nghiên Cứu Sinh ThS/TS (Master/Ph.D.)",
        "faculty": "Giảng Viên (Faculty/Lecturer)",
        "professor": "Giáo Sư & CS519.M11 (Professor Mode)"
      };
      App.toast(`Đã kích hoạt: ${pNames[persona] || persona}`, "info");
    }
  },

  setCitationStyle(style) {
    this.currentCitationStyle = style;
  },

  onInputChanged() {
    const text = document.getElementById("humanizer-input-text").value || "";
    const words = text.trim() ? text.trim().split(/\s+/).length : 0;
    const chars = text.length;
    const counterEl = document.getElementById("humanizer-input-count");
    if (counterEl) {
      counterEl.innerText = `${words} từ | ${chars} ký tự`;
    }
  },

  switchSubTab(tabId) {
    const tabs = ['output', 'audit', 'cs519', 'matrix', 'highlight', 'issues'];
    tabs.forEach(t => {
      const btn = document.getElementById(`subtab-btn-${t}`);
      const pane = document.getElementById(`subtab-content-${t}`);
      if (btn) {
        if (t === tabId) {
          btn.classList.add("active");
          btn.style.color = "#38bdf8";
          btn.style.borderBottom = "2px solid #38bdf8";
        } else {
          btn.classList.remove("active");
          btn.style.color = "#94a3b8";
          btn.style.borderBottom = "none";
        }
      }
      if (pane) {
        pane.style.display = (t === tabId) ? "block" : "none";
      }
    });
  },

  async handleFileSelected(file) {
    if (!file.name.toLowerCase().endsWith(".docx")) {
      App.toast("Vui lòng chọn hoặc kéo thả tệp Word (.docx).", "error");
      return;
    }

    this.selectedFile = file;
    const badgeEl = document.getElementById("humanizer-selected-file-badge");
    if (badgeEl) {
      badgeEl.innerHTML = `📄 <strong style="color: #38bdf8;">Đang nạp:</strong> ${file.name} (${(file.size / 1024).toFixed(1)} KB) — Đang đọc nội dung...`;
    }

    App.toast(`Đang trích xuất nội dung từ tệp "${file.name}"...`, "info");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("/api/files/extract-docx-text", {
        method: "POST",
        body: formData
      });
      const data = await res.json();
      if (data.success) {
        document.getElementById("humanizer-input-text").value = data.text;
        this.onInputChanged();

        if (badgeEl) {
          badgeEl.innerHTML = `📄 <strong style="color: #34d399;">Đã nạp thành công:</strong> ${file.name} (${data.word_count} từ, ${data.paragraph_count} đoạn)`;
        }
        
        const exportBtn = document.getElementById("btn-humanize-docx-export");
        if (exportBtn) exportBtn.style.display = "inline-block";

        App.toast(`Đã trích xuất ${data.word_count} từ. Đang tự động phân tích chỉ số AI & Turnitin...`, "success");
        this.analyzeText();
      } else {
        App.toast(data.detail || "Không thể đọc tệp Word", "error");
      }
    } catch (e) {
      App.toast("Lỗi trích xuất tệp: " + e.message, "error");
    }
  },

  updateGauges(analysis) {
    if (!analysis) return;

    // 1. Human Score
    const hScore = analysis.human_score !== undefined ? analysis.human_score : 50;
    const gH = document.getElementById("gauge-human-score");
    if (gH) gH.innerText = `${hScore}%`;
    const ringH = document.getElementById("ring-fill-human");
    if (ringH) ringH.style.strokeDasharray = `${hScore} 100`;

    // 2. Turnitin Similarity Index
    const simIndex = analysis.similarity_index !== undefined ? analysis.similarity_index : 15;
    const gSim = document.getElementById("gauge-similarity-index");
    if (gSim) {
      gSim.innerText = `${simIndex}%`;
      gSim.style.color = simIndex <= 10 ? "#34d399" : simIndex <= 20 ? "#fbbf24" : "#f87171";
    }
    const ringSim = document.getElementById("ring-fill-similarity");
    if (ringSim) {
      ringSim.style.strokeDasharray = `${Math.min(100, simIndex * 2)} 100`;
      ringSim.style.stroke = simIndex <= 10 ? "#34d399" : simIndex <= 20 ? "#fbbf24" : "#f87171";
    }

    // 3. AI Probability
    const aiProb = analysis.ai_probability !== undefined ? analysis.ai_probability : 50;
    const gAi = document.getElementById("gauge-ai-prob");
    if (gAi) gAi.innerText = `${aiProb}%`;
    const ringAi = document.getElementById("ring-fill-ai");
    if (ringAi) ringAi.style.strokeDasharray = `${aiProb} 100`;

    const gRisk = document.getElementById("gauge-risk-level");
    if (gRisk) gRisk.innerText = analysis.risk_level || "Chưa phân tích";

    // 4. Burstiness (Sóng 3 tầng)
    const burst = analysis.burstiness_score || 0;
    const gBurst = document.getElementById("gauge-burstiness");
    if (gBurst) gBurst.innerText = burst.toFixed(1);
    const ringBurst = document.getElementById("ring-fill-burst");
    if (ringBurst) ringBurst.style.strokeDasharray = `${Math.min(100, burst * 10)} 100`;

    // 5. Clichés & Tells
    const clichesCount = analysis.cliches_count || 0;
    const gCliche = document.getElementById("gauge-cliches-count");
    if (gCliche) gCliche.innerText = clichesCount;
    const ringCliche = document.getElementById("ring-fill-cliche");
    if (ringCliche) ringCliche.style.strokeDasharray = `${Math.min(100, clichesCount * 10)} 100`;

    // Stats bar
    const statsBar = document.getElementById("humanizer-stats-bar");
    if (statsBar) {
      statsBar.style.display = "flex";
      document.getElementById("stat-words").innerText = analysis.total_words || 0;
      document.getElementById("stat-sentences").innerText = analysis.sentence_count || 0;
      document.getElementById("stat-avg-len").innerText = analysis.avg_sentence_len || 0;
      document.getElementById("stat-min-len").innerText = analysis.shortest_sentence_len || 0;
      document.getElementById("stat-max-len").innerText = analysis.longest_sentence_len || 0;
      
      const waveEl = document.getElementById("stat-wave-dist");
      if (waveEl && analysis.wave_distribution) {
        waveEl.innerText = `Sóng 3 tầng: Ngắn (4-8 từ): ${analysis.wave_distribution.short_4_8} | Vừa (12-18 từ): ${analysis.wave_distribution.medium_12_18} | Dài (25-35 từ): ${analysis.wave_distribution.long_25_35}`;
      }
    }

    // Badges
    const badgeMatrix = document.getElementById("subtab-matrix-badge");
    if (badgeMatrix) badgeMatrix.innerText = clichesCount;

    // Highlight Pane
    const hlPane = document.getElementById("humanizer-highlighted-pane");
    if (hlPane) hlPane.innerHTML = analysis.highlighted_html || "<p style='color:#94a3b8;'>Không có điểm cần tô màu.</p>";

    // Clichés Table
    this.renderClichesTable(analysis.found_cliches || [], analysis.wikipedia_tells || []);

    // Issues Pane
    this.renderIssuesPane(analysis.structural_issues || []);

    // CS519.M11 Critical Thinking Pane
    this.renderCS519Audit(analysis.cs519_audit || {});
  },

  renderClichesTable(cliches, wikipediaTells) {
    const container = document.getElementById("humanizer-cliches-table-container");
    if (!container) return;

    if (cliches.length === 0 && wikipediaTells.length === 0) {
      container.innerHTML = `<div style="padding: 24px; text-align: center; color: #34d399;">
        🎉 Tuyệt vời! Văn bản sạch 100% không phát hiện cụm từ sáo rỗng ContentBeta 300+ hay dấu hiệu Wikipedia Tells!
      </div>`;
      return;
    }

    let rows = "";
    cliches.forEach(c => {
      rows += `<tr>
        <td style="padding: 8px 12px; color: #f87171; font-weight: 600;"><mark class="ai-cliche">${c.phrase}</mark></td>
        <td style="padding: 8px 12px; text-align: center; color: #fbbf24;">${c.count}</td>
        <td style="padding: 8px 12px; color: #60a5fa; font-size: 11.5px;">${c.category || 'ContentBeta Cliché'}</td>
        <td style="padding: 8px 12px; color: #34d399; font-weight: 500;">${c.suggestion}</td>
      </tr>`;
    });

    wikipediaTells.forEach(t => {
      rows += `<tr>
        <td style="padding: 8px 12px; color: #f87171; font-weight: 600;"><mark class="ai-fingerprint">${t.name}</mark></td>
        <td style="padding: 8px 12px; text-align: center; color: #fbbf24;">${t.count}</td>
        <td style="padding: 8px 12px; color: #c084fc; font-size: 11.5px;">Wikipedia AI Tell</td>
        <td style="padding: 8px 12px; color: #38bdf8; font-weight: 500;">Xóa bỏ cấu trúc máy móc, chuyển thành câu phân tích tự nhiên</td>
      </tr>`;
    });

    container.innerHTML = `<table style="width: 100%; border-collapse: collapse; font-size: 12px; text-align: left;">
      <thead>
        <tr style="background: rgba(255,255,255,0.06); border-bottom: 1px solid rgba(255,255,255,0.12); color: #cbd5e1;">
          <th style="padding: 8px 12px;">Cụm Từ / Cấu Trúc Máy Móc</th>
          <th style="padding: 8px 12px; text-align: center;">Số Lần</th>
          <th style="padding: 8px 12px;">Phân Loại</th>
          <th style="padding: 8px 12px;">Gợi Ý Thay Thế (Chuẩn Học Thuật)</th>
        </tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>`;
  },

  renderIssuesPane(issues) {
    const el = document.getElementById("humanizer-structural-details");
    if (!el) return;
    if (issues.length === 0) {
      el.innerHTML = `<div style="padding: 20px; text-align: center; color: #34d399;">
        ✅ Không phát hiện cảnh báo cấu trúc nhịp điệu hay lạm dụng danh sách gạch đầu dòng!
      </div>`;
      return;
    }
    el.innerHTML = `<ul style="margin: 0; padding-left: 20px; color: #fca5a5; font-size: 12.5px; line-height: 1.8;">
      ${issues.map(i => `<li>${i}</li>`).join("")}
    </ul>`;
  },

  renderCS519Audit(audit) {
    const el = document.getElementById("subtab-content-cs519-body");
    if (!el) return;

    el.innerHTML = `
      <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 16px;">
        <div style="background: rgba(255,255,255,0.04); padding: 12px; border-radius: 8px; border: 1px solid ${audit.has_causal_mechanism ? '#10b981' : '#f59e0b'};">
          <div style="font-weight: 700; color: #fff; font-size: 13px; margin-bottom: 4px;">1. Cơ Chế Giải Thích Sâu (Causal Mechanism)</div>
          <div style="font-size: 11.5px; color: ${audit.has_causal_mechanism ? '#34d399' : '#fbbf24'};">
            ${audit.has_causal_mechanism ? '🟢 Đã giải thích cơ chế TẠI SAO' : '⚠️ Cần bổ sung nguyên nhân cốt lõi'}
          </div>
        </div>
        <div style="background: rgba(255,255,255,0.04); padding: 12px; border-radius: 8px; border: 1px solid ${audit.has_research_gap ? '#10b981' : '#f59e0b'};">
          <div style="font-weight: 700; color: #fff; font-size: 13px; margin-bottom: 4px;">2. Khoảng Trống Tri Thức (Research Gap)</div>
          <div style="font-size: 11.5px; color: ${audit.has_research_gap ? '#34d399' : '#fbbf24'};">
            ${audit.has_research_gap ? '🟢 Đã chỉ ra giới hạn công trình trước' : '⚠️ Cần nhấn mạnh điểm mới nghiên cứu'}
          </div>
        </div>
        <div style="background: rgba(255,255,255,0.04); padding: 12px; border-radius: 8px; border: 1px solid ${audit.has_threats_to_validity ? '#10b981' : '#f59e0b'};">
          <div style="font-weight: 700; color: #fff; font-size: 13px; margin-bottom: 4px;">3. Đe Dọa Tính Hợp Lệ (Threats to Validity)</div>
          <div style="font-size: 11.5px; color: ${audit.has_threats_to_validity ? '#34d399' : '#fbbf24'};">
            ${audit.has_threats_to_validity ? '🟢 Đã phân tích điều kiện biên & ranh giới' : 'ℹ️ Khuyến nghị đánh giá tính tổng quát hóa'}
          </div>
        </div>
      </div>
      <div style="background: rgba(56, 189, 248, 0.08); padding: 12px 16px; border-radius: 8px; border: 1px solid rgba(56, 189, 248, 0.2); font-size: 12px; color: #cbd5e1; line-height: 1.6;">
        💡 <strong>Khung Tư Duy CS519.M11:</strong> Đảm bảo chuỗi 4 bước: [Luận điểm] ➔ [Dẫn chứng thực chứng] ➔ [Cơ chế giải thích sâu] ➔ [Hàm ý ứng dụng].
      </div>
    `;
  },

  async analyzeText() {
    if (window.App && App.requireAuth && !App.requireAuth('phân tích chỉ số AI')) return;
    const text = document.getElementById("humanizer-input-text").value;
    if (!text.trim()) {
      App.toast("Vui lòng nhập văn bản hoặc kéo thả tệp Word .docx.", "warning");
      return;
    }

    const btn = document.getElementById("btn-humanize-analyze");
    if (btn) { btn.disabled = true; btn.innerText = "⏳ Đang Quét Chỉ Số..."; }

    try {
      const headers = (window.AuthManager && AuthManager.token)
        ? { 'Content-Type': 'application/json', 'Authorization': `Bearer ${AuthManager.token}` }
        : { 'Content-Type': 'application/json' };

      const res = await fetch("/api/humanize/analyze", {
        method: "POST",
        headers,
        body: JSON.stringify({ text })
      });
      const data = await res.json();
      if (!res.ok || data.detail) {
        App.toast(data.detail || "Lỗi phân tích máy chủ", "error");
        return;
      }
      this.updateGauges(data);
      const hScore = data.human_score !== undefined ? data.human_score : 50;
      const simIndex = data.similarity_index !== undefined ? data.similarity_index : 5.0;
      App.toast(`Đã quét xong: Điểm Human ${hScore}% | Turnitin Sim: ${simIndex}%`, "success");
    } catch (e) {
      App.toast("Lỗi phân tích: " + e.message, "error");
    } finally {
      if (btn) { btn.disabled = false; btn.innerText = "🔍 Phân Tích Chỉ Số AI Chi Tiết"; }
    }
  },

  async processUnifiedHumanizeTurnitin() {
    if (window.App && App.requireAuth && !App.requireAuth('khử dấu vết AI & chống đạo văn Turnitin')) return;
    const text = document.getElementById("humanizer-input-text").value;
    if (!text.trim()) {
      App.toast("Vui lòng nhập văn bản hoặc kéo thả tệp Word (.docx) cần xử lý.", "warning");
      return;
    }

    const btn = document.getElementById("btn-humanize-unified") || document.getElementById("btn-humanize-process");
    if (btn) {
      btn.disabled = true;
      btn.innerText = "⚡ Đang Khử AI & Chống Đạo Văn Turnitin...";
    }

    App.toast(`Đang áp dụng đồng bộ Khử AI (Wikipedia/ContentBeta 300+) + 5 Kỹ thuật chống Turnitin [${this.currentPersona.toUpperCase()}]...`, "info");

    try {
      const headers = (window.AuthManager && AuthManager.token)
        ? { 'Content-Type': 'application/json', 'Authorization': `Bearer ${AuthManager.token}` }
        : { 'Content-Type': 'application/json' };

      const res = await fetch("/api/humanize/unified-process", {
        method: "POST",
        headers,
        body: JSON.stringify({
          text,
          persona: this.currentPersona,
          citation_style: this.currentCitationStyle
        })
      });
      const data = await res.json();
      if (!res.ok || data.detail) {
        App.toast(data.detail || "Lỗi xử lý máy chủ", "error");
        return;
      }
      if (data.success) {
        const outText = data.processed_text || data.humanized_text || data.rephrased_text || "";
        document.getElementById("humanizer-output-text").value = outText;
        this.updateGauges(data.after_analysis);
        this.switchSubTab("output");
        App.toast(`🎉 Xử lý hoàn tất! Điểm Human: ${data.after_analysis.human_score}% | Turnitin Sim: ${data.after_analysis.similarity_index}% (Chuẩn An Toàn)`, "success");
      } else {
        App.toast(data.detail || "Lỗi xử lý", "error");
      }
    } catch (e) {
      App.toast("Lỗi xử lý: " + e.message, "error");
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.innerText = "⚡ Khử AI & Chống Đạo Văn Turnitin (1-Click)";
      }
    }
  },

  async processHumanization() {
    return this.processUnifiedHumanizeTurnitin();
  },

  async processTurnitinRephrase() {
    return this.processUnifiedHumanizeTurnitin();
  },

  async processPlagiarismAudit() {
    if (window.App && App.requireAuth && !App.requireAuth('kiểm định tính nguyên bản')) return;
    const text = document.getElementById("humanizer-input-text").value;
    if (!text.trim()) {
      App.toast("Vui lòng nhập văn bản cần kiểm định tính nguyên bản.", "warning");
      return;
    }

    const btn = document.getElementById("btn-plagiarism-audit");
    if (btn) { btn.disabled = true; btn.innerText = "🔍 Đang Thẩm Định Toàn Diện..."; }

    try {
      const headers = (window.AuthManager && AuthManager.token)
        ? { 'Content-Type': 'application/json', 'Authorization': `Bearer ${AuthManager.token}` }
        : { 'Content-Type': 'application/json' };

      const res = await fetch("/api/humanize/plagiarism-audit", {
        method: "POST",
        headers,
        body: JSON.stringify({
          text,
          persona: this.currentPersona
        })
      });
      const data = await res.json();
      if (!res.ok || data.detail) {
        App.toast(data.detail || "Lỗi kiểm định máy chủ", "error");
        return;
      }
      if (data.success) {
        if (data.analysis) this.updateGauges(data.analysis);
        const auditEl = document.getElementById("subtab-content-audit-body");
        if (auditEl) {
          const reportContent = data.audit_report || "Không có dữ liệu báo cáo.";
          let formattedHtml = reportContent;
          if (window.marked && typeof marked.parse === 'function') {
            try {
              formattedHtml = marked.parse(reportContent);
            } catch (e) {
              formattedHtml = `<div style="white-space: pre-wrap; font-family: monospace;">${reportContent}</div>`;
            }
          } else {
            formattedHtml = `<div style="white-space: pre-wrap; font-family: monospace;">${reportContent}</div>`;
          }
          auditEl.innerHTML = `<div style="padding: 20px; background: rgba(15,23,42,0.6); border: 1px solid rgba(59,130,246,0.3); border-radius: 12px; font-size: 13.5px; line-height: 1.8; color: #e2e8f0;">${formattedHtml}</div>`;
        }
        this.switchSubTab("audit");
        App.toast("Đã hoàn tất Báo Cáo Kiểm Định Tính Nguyên Bản & Trùng Lặp!", "success");
      }
    } catch (e) {
      App.toast("Lỗi kiểm định: " + e.message, "error");
    } finally {
      if (btn) { btn.disabled = false; btn.innerText = "📋 Báo Cáo Kiểm Định Tính Nguyên Bản"; }
    }
  },

  async processAndExportDocx() {
    if (!this.selectedFile) {
      App.toast("Vui lòng chọn tệp Word .docx trước khi xuất bản.", "warning");
      return;
    }

    const btn = document.getElementById("btn-humanize-docx-export");
    if (btn) { btn.disabled = true; btn.innerText = "⏳ Đang Xử Lý In-Place DOM..."; }

    App.toast(`Đang khử AI tệp Word "${this.selectedFile.name}" và bảo toàn 100% cấu trúc đề mục, bảng biểu, công thức OMML...`, "info");

    const formData = new FormData();
    formData.append("file", this.selectedFile);
    formData.append("persona", this.currentPersona);
    formData.append("citation_style", this.currentCitationStyle);

    try {
      const headers = (window.AuthManager && AuthManager.token)
        ? { 'Authorization': `Bearer ${AuthManager.token}` } : {};

      const res = await fetch("/api/humanize/process-docx", {
        method: "POST",
        headers,
        body: formData
      });
      const data = await res.json();
      if (data.success) {
        this.updateGauges(data.analysis_after);
        document.getElementById("humanizer-output-text").value = data.humanized_text;

        const issuesEl = document.getElementById("humanizer-issues-list");
        if (issuesEl) {
          issuesEl.innerHTML = `
            <div style="background: rgba(16, 185, 129, 0.15); border: 1px solid #10b981; border-radius: 8px; padding: 14px; margin-top: 12px;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-weight: 700; color: #34d399; font-size: 14px;">✅ Đã Khử AI & Xuất Bản Tệp Word Thành Công (In-Place DOM)</span>
                <span style="font-size: 12px; color: #cbd5e1;">${data.word_count} từ | Loại bỏ ${data.cliches_removed} từ sáo rỗng</span>
              </div>
              <div style="font-size: 12px; color: #94a3b8; margin-bottom: 10px;">
                Tệp: <strong style="color: #fff;">${data.filename}</strong> (Bảo toàn 100% Heading styles, bảng biểu, ảnh, công thức và mã Zotero).
              </div>
              <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                <a href="${data.file_url}" class="btn btn-green btn-sm" download style="text-decoration: none; display: inline-flex; align-items: center; gap: 6px;">
                  ⬇️ Tải Về Tệp Word Đã Khử AI (${data.filename})
                </a>
                <button class="btn btn-secondary btn-sm" onclick="App.openWindowsExplorer('${data.rel_path}')">
                  📁 Mở Thư Mục Chứa Tệp
                </button>
              </div>
            </div>
          `;
        }
        App.toast("Xuất bản tệp Word đã khử AI thành công!", "success");
      } else {
        App.toast(data.detail || "Lỗi xử lý tệp Word", "error");
      }
    } catch (e) {
      App.toast("Lỗi: " + e.message, "error");
    } finally {
      if (btn) { btn.disabled = false; btn.innerText = "📑 Xuất File Word Đã Khử AI (.docx)"; }
    }
  },

  copyOutput() {
    const text = document.getElementById("humanizer-output-text").value;
    if (!text) {
      App.toast("Chưa có nội dung để sao chép.", "warning");
      return;
    }
    navigator.clipboard.writeText(text).then(() => {
      App.toast("Đã sao chép toàn bộ văn bản vào bộ nhớ tạm!", "success");
    }).catch(() => {
      App.toast("Không thể sao chép tự động, vui lòng chọn và Ctrl+C.", "error");
    });
  }
};
