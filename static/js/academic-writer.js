// Academic Writer 2-File Paradigm & Deep Research UI (RhinoInsight / arXiv:2511.18743)
const AcademicWriterUI = {
  currentOutlineTree: null,
  isOutlineLocked: false,

  async proposeOutline() {
    if (window.App && App.requireAuth && !App.requireAuth('đề xuất cấu trúc bài viết')) return;
    const topic = document.getElementById("writer-topic") ? document.getElementById("writer-topic").value.trim() : "";
    const paperType = document.getElementById("writer-paper-type") ? document.getElementById("writer-paper-type").value : "Báo cáo khoa học";

    if (!topic) {
      if (window.App && App.toast) App.toast("Vui lòng nhập Đề tài nghiên cứu.", "warning");
      return;
    }

    const btn = document.getElementById("btn-writer-outline");
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = '<span class="spinner-btn"></span> <span>Đang khởi tạo Cây Đề Cương Phân Nhánh...</span>';
    }

    try {
      const res = await fetch("/api/writer/outline/structured", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...((window.AuthManager && AuthManager.token) ? { "Authorization": `Bearer ${AuthManager.token}` } : {})
        },
        body: JSON.stringify({ topic, paper_type: paperType, depth_level: "comprehensive" })
      });
      const data = await res.json().catch(() => ({ detail: `Lỗi máy chủ (${res.status})` }));
      if (res.ok && data.status === "success") {
        this.currentOutlineTree = data.outline_tree || null;
        this.isOutlineLocked = false;

        const outlineText = data.markdown_outline || data.outline || "";
        const outlineTextarea = document.getElementById("writer-custom-outline");
        if (outlineTextarea) {
          outlineTextarea.value = outlineText;
        }

        this.renderOutlineTree(this.currentOutlineTree);
        if (window.App && App.toast) App.toast("Đã lập Cây Đề Cương Phân Nhánh (Phase 1) thành công!", "success");
      } else {
        if (window.App && App.toast) App.toast(data.detail || data.message || "Không thể tạo cấu trúc lúc này.", "warning");
      }
    } catch (e) {
      if (window.App && App.toast) App.toast("Lỗi đề xuất cấu trúc: " + e.message, "error");
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = "💡 AI Gợi Ý Đề Cương Mẫu";
      }
    }
  },

  renderOutlineTree(tree) {
    if (!tree || !tree.items) return;

    let treeBox = document.getElementById("writer-interactive-tree-container");
    const outlineTextarea = document.getElementById("writer-custom-outline");

    if (!treeBox && outlineTextarea && outlineTextarea.parentNode) {
      treeBox = document.createElement("div");
      treeBox.id = "writer-interactive-tree-container";
      treeBox.style.cssText = "margin-bottom: 14px; background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(139, 92, 246, 0.35); border-radius: 10px; padding: 14px;";
      outlineTextarea.parentNode.insertBefore(treeBox, outlineTextarea);
    }

    if (!treeBox) return;

    const isLocked = this.isOutlineLocked || tree.is_locked;
    const items = tree.items || [];
    const dimensions = tree.dimensions || [];

    let dimsHtml = dimensions.map(d => `
      <span style="display: inline-flex; align-items: center; background: rgba(59, 130, 246, 0.15); border: 1px solid rgba(59, 130, 246, 0.4); color: #93c5fd; padding: 3px 9px; border-radius: 20px; font-size: 11px;">
        🏷️ ${d}
      </span>
    `).join("");

    let itemsHtml = items.map((sec, sIdx) => {
      const subs = sec.subsections || [];
      let subsListHtml = subs.map(sub => `
        <div style="display: flex; justify-content: space-between; align-items: flex-start; background: rgba(0,0,0,0.25); border-radius: 6px; padding: 6px 10px; margin-top: 5px; font-size: 12px;">
          <div>
            <strong style="color: #cbd5e1;">${sub.title || sub}</strong>
            ${sub.focus ? `<div style="font-size: 11px; color: #94a3b8; margin-top: 2px;">🎯 <em>${sub.focus}</em></div>` : ''}
          </div>
          <span style="font-size: 10.5px; color: #34d399; background: rgba(52, 211, 153, 0.1); padding: 2px 6px; border-radius: 4px; white-space: nowrap; margin-left: 8px;">Node ${sub.subsection_number || ''}</span>
        </div>
      `).join("");

      return `
        <div style="border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 10px 12px; margin-bottom: 10px; background: rgba(30, 41, 59, 0.45);">
          <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
            <div style="display: flex; align-items: center; gap: 6px;">
              <span style="color: #a78bfa; font-weight: 700; font-size: 13px;">${sec.title || (sIdx + 1) + '. ' + sec.name}</span>
            </div>
            <div style="display: flex; gap: 6px;">
              <button type="button" class="btn btn-secondary btn-sm" onclick="AcademicWriterUI.expandBranch('${sec.id || sIdx + 1}')" style="padding: 2px 8px; font-size: 11px;" ${isLocked ? 'disabled' : ''}>
                ➕ Thêm Nhánh Con
              </button>
            </div>
          </div>
          <div style="margin-top: 6px;">
            ${subsListHtml}
          </div>
        </div>
      `;
    }).join("");

    treeBox.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; flex-wrap: wrap; gap: 8px;">
        <div style="display: flex; align-items: center; gap: 8px;">
          <span style="font-size: 15px;">🌳</span>
          <strong style="color: #c084fc; font-size: 13.5px;">CÂY ĐỀ CƯƠNG PHÂN NHÁNH (RHINOINSIGHT INTERACTIVE TREE)</strong>
          <span class="badge ${isLocked ? 'badge-green' : 'badge-purple'}" style="font-size: 11px;">
            ${isLocked ? '🔒 ĐÃ DUYỆT & KHÓA (LOCKED)' : '✏️ ĐANG HIỆU CHỈNH'}
          </span>
        </div>
        <div style="display: flex; gap: 6px;">
          <button type="button" class="btn btn-secondary btn-sm" onclick="AcademicWriterUI.addDimension()" style="font-size: 11px; padding: 3px 8px;" ${isLocked ? 'disabled' : ''}>
            ➕ Thêm Chiều Phân Tích
          </button>
          <button type="button" class="btn ${isLocked ? 'btn-secondary' : 'btn-primary'} btn-sm" onclick="AcademicWriterUI.lockOutline()" style="font-size: 11px; padding: 3px 10px; font-weight: 700;" title="${isLocked ? 'Nhấp để mở khóa và hiệu chỉnh nhánh/chiều' : 'Phê duyệt đề cương để chuyển sang Giai đoạn 2'}">
            ${isLocked ? '🔓 Mở Khóa Đề Cương' : '🔒 Khóa & Duyệt Đề Cương (Approval Gate)'}
          </button>
        </div>
      </div>

      <!-- Dimensions Tag Bar -->
      <div style="display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 12px; align-items: center;">
        <span style="font-size: 11.5px; color: #94a3b8; font-weight: 600;">Khung đối soát 5 chiều:</span>
        ${dimsHtml}
      </div>

      <!-- Tree Nodes List -->
      <div style="max-height: 320px; overflow-y: auto; padding-right: 4px;">
        ${itemsHtml}
      </div>
    `;
  },

  async expandBranch(targetNodeId) {
    if (this.isOutlineLocked) {
      if (window.App && App.toast) App.toast("Đề cương đã được khóa. Vui lòng mở khóa trước khi chỉnh sửa.", "warning");
      return;
    }

    const topic = document.getElementById("writer-topic") ? document.getElementById("writer-topic").value.trim() : "";
    const promptInput = window.prompt("Nhập nội dung nhánh luận điểm mới hoặc để trống để AI tự động mở rộng theo phương pháp luận RhinoInsight:", "");
    if (promptInput === null) return;

    if (window.App && App.toast) App.toast("⏳ Đang phân nhánh và cập nhật cấu trúc đề cương...", "info");

    try {
      const res = await fetch("/api/writer/outline/expand-branch", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...((window.AuthManager && AuthManager.token) ? { "Authorization": `Bearer ${AuthManager.token}` } : {})
        },
        body: JSON.stringify({
          topic: topic || (this.currentOutlineTree ? this.currentOutlineTree.topic : ""),
          outline_tree: this.currentOutlineTree || {},
          target_node_id: targetNodeId,
          expansion_prompt: promptInput
        })
      });
      const data = await res.json().catch(() => ({ detail: `Lỗi (${res.status})` }));
      if (res.ok && data.status === "success") {
        this.currentOutlineTree = data.outline_tree || data.updated_tree || this.currentOutlineTree;
        const outlineTextarea = document.getElementById("writer-custom-outline");
        if (outlineTextarea && data.markdown_outline) {
          outlineTextarea.value = data.markdown_outline;
        }
        this.renderOutlineTree(this.currentOutlineTree);
        if (window.App && App.toast) App.toast(`Đã bổ sung nhánh mới vào mục ${targetNodeId}!`, "success");
      } else {
        if (window.App && App.toast) App.toast(data.detail || "Không thể mở rộng nhánh lúc này.", "warning");
      }
    } catch (e) {
      if (window.App && App.toast) App.toast("Lỗi mở rộng nhánh: " + e.message, "error");
    }
  },

  async addDimension() {
    if (this.isOutlineLocked) {
      if (window.App && App.toast) App.toast("Đề cương đã được khóa.", "warning");
      return;
    }

    const topic = document.getElementById("writer-topic") ? document.getElementById("writer-topic").value.trim() : "";
    const dimName = window.prompt("Nhập tên Chiều Phân Tích / Tiêu Chí Đối Soát mới (ví dụ: 'Rủi ro an ninh mạng', 'Chi phí LCOE', 'Khả năng tái sinh thái'):", "");
    if (!dimName || !dimName.trim()) return;

    if (window.App && App.toast) App.toast("⏳ Đang thiết lập chiều phân tích mới...", "info");

    try {
      const res = await fetch("/api/writer/outline/add-dimension", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...((window.AuthManager && AuthManager.token) ? { "Authorization": `Bearer ${AuthManager.token}` } : {})
        },
        body: JSON.stringify({
          topic: topic || (this.currentOutlineTree ? this.currentOutlineTree.topic : ""),
          outline_tree: this.currentOutlineTree || {},
          dimension_name: dimName.trim()
        })
      });
      const data = await res.json().catch(() => ({ detail: `Lỗi (${res.status})` }));
      if (res.ok && data.status === "success") {
        this.currentOutlineTree = data.outline_tree || data.updated_tree || this.currentOutlineTree;
        const outlineTextarea = document.getElementById("writer-custom-outline");
        if (outlineTextarea && data.markdown_outline) {
          outlineTextarea.value = data.markdown_outline;
        }
        this.renderOutlineTree(this.currentOutlineTree);
        if (window.App && App.toast) App.toast(`Đã thêm chiều phân tích '${dimName.trim()}'!`, "success");
      } else {
        if (window.App && App.toast) App.toast(data.detail || "Không thể thêm chiều phân tích.", "warning");
      }
    } catch (e) {
      if (window.App && App.toast) App.toast("Lỗi thêm chiều phân tích: " + e.message, "error");
    }
  },

  async lockOutline() {
    if (this.isOutlineLocked) {
      this.isOutlineLocked = false;
      this.renderOutlineTree(this.currentOutlineTree);
      if (window.App && App.toast) App.toast("🔓 Đã mở khóa đề cương để tiếp tục hiệu chỉnh nhánh và chiều!", "info");
      return;
    }

    const topic = document.getElementById("writer-topic") ? document.getElementById("writer-topic").value.trim() : "";

    try {
      const res = await fetch("/api/writer/outline/lock", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...((window.AuthManager && AuthManager.token) ? { "Authorization": `Bearer ${AuthManager.token}` } : {})
        },
        body: JSON.stringify({
          topic: topic || (this.currentOutlineTree ? this.currentOutlineTree.topic : ""),
          outline_tree: this.currentOutlineTree || {}
        })
      });
      const data = await res.json().catch(() => ({ detail: `Lỗi (${res.status})` }));
      if (res.ok && data.status === "success") {
        this.isOutlineLocked = true;
        this.currentOutlineTree = data.outline_tree || data.updated_tree || this.currentOutlineTree;
        this.renderOutlineTree(this.currentOutlineTree);
        if (window.App && App.toast) App.toast("✅ Đã Khóa & Phê Duyệt Đề Cương (Approval Gate Passed)! Sẵn sàng Soạn thảo Giai đoạn 2.", "success");
      }
    } catch (e) {
      this.isOutlineLocked = true;
      this.renderOutlineTree(this.currentOutlineTree);
      if (window.App && App.toast) App.toast("Đã khóa đề cương cục bộ!", "success");
    }
  },

  async generate2Files() {
    if (window.App && App.requireAuth && !App.requireAuth('soạn thảo học thuật 2 tệp')) return;
    const topic = document.getElementById("writer-topic") ? document.getElementById("writer-topic").value.trim() : "";
    const paperType = document.getElementById("writer-paper-type") ? document.getElementById("writer-paper-type").value : "Báo cáo khoa học";
    const authorName = (document.getElementById("writer-author-name") ? document.getElementById("writer-author-name").value.trim() : "") || "Học viên";
    const courseName = (document.getElementById("writer-course-name") ? document.getElementById("writer-course-name").value.trim() : "") || "Chuyên đề Cao học";
    const customOutline = document.getElementById("writer-custom-outline") ? document.getElementById("writer-custom-outline").value.trim() : "";

    if (!topic) {
      if (window.App && App.toast) App.toast("Vui lòng nhập Đề tài nghiên cứu.", "warning");
      return;
    }

    const btn = document.getElementById("btn-writer-generate");
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = '<span class="spinner-btn"></span> <span>Giai đoạn 2: Deep Investigation & Xuất bản 2 Tệp...</span>';
    }

    const resultContainer = document.getElementById("writer-result-container");
    if (resultContainer) {
      resultContainer.innerHTML = `
        <div class="loading-indicator-box">
          <div class="spinner-lg" style="border-top-color: #8b5cf6; border-right-color: #c084fc; box-shadow: 0 0 16px rgba(139, 92, 246, 0.25);"></div>
          <div class="loading-indicator-title">🎓 RhinoInsight Deep Investigation đang thực thi Giai đoạn 2<span class="loading-pulse-dots"></span></div>
          <div class="loading-indicator-desc">Điều tra thực chứng đa nguồn, trích xuất số liệu định lượng, đối soát 1-1 và xuất bản đồng thời <strong>Tệp A (Báo cáo APA 7th)</strong> & <strong>Tệp B (Bảng ma trận truy xuất 6 cột)</strong> cho đề tài: <em>"${topic}"</em>.</div>
        </div>
      `;
    }

    if (window.App && App.toast) App.toast(`Khởi động Deep Investigation cho '${topic}'...`, "info");

    try {
      const res = await fetch("/api/writer/generate-2file", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...((window.AuthManager && AuthManager.token) ? { "Authorization": `Bearer ${AuthManager.token}` } : {})
        },
        body: JSON.stringify({
          topic,
          paper_type: paperType,
          author_name: authorName,
          course_name: courseName,
          custom_outline: customOutline,
          outline_tree: this.currentOutlineTree || null
        })
      });

      const data = await res.json().catch(() => ({ detail: `Lỗi máy chủ (${res.status})` }));
      if (res.ok && data.status === "success") {
        if (window.App && App.toast) App.toast("Xuất bản Bộ 2 Tệp thành công!", "success");
        this.render2FilesResult(data);
        if (window.App && App.updateStatus) App.updateStatus();
      } else {
        const errMsg = data.detail || data.message || "Lỗi tạo bài viết";
        if (window.App && App.toast) App.toast(errMsg, "error");
        if (resultContainer) {
          resultContainer.innerHTML = `
            <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.4); padding: 14px; border-radius: 8px; color: #fca5a5; font-size: 13px; margin-top: 14px;">
              ❌ <strong>Không thể tạo bài viết:</strong> ${errMsg}
            </div>
          `;
        }
      }
    } catch (e) {
      if (window.App && App.toast) App.toast("Lỗi kết nối: " + e.message, "error");
      if (resultContainer) {
        resultContainer.innerHTML = `
          <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.4); padding: 14px; border-radius: 8px; color: #fca5a5; font-size: 13px; margin-top: 14px;">
            ❌ <strong>Lỗi kết nối:</strong> ${e.message}
          </div>
        `;
      }
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = "🚀 Soạn Thảo Theo Đề Cương & Xuất Bản 2 Tệp";
      }
    }
  },

  render2FilesResult(data) {
    const container = document.getElementById("writer-result-container");
    if (!container) return;

    const fileA = data.file_a || {};
    const fileB = data.file_b || {};
    const fileRis = data.file_ris || {};
    const fileBib = data.file_bib || {};
    const pathA = fileA.rel_path || fileA.docx_rel_path || (fileA.docx ? `Tai_Lieu/${fileA.docx}` : '') || '';
    const pathB = fileB.rel_path || fileB.docx_rel_path || (fileB.docx ? `Tai_Lieu/${fileB.docx}` : '') || '';
    const pathRis = fileRis.rel_path || (fileRis.name ? `Tai_Lieu/${fileRis.name}` : '') || '';
    const pathBib = fileBib.rel_path || (fileBib.name ? `Tai_Lieu/${fileBib.name}` : '') || '';
    const uncertainCount = data.uncertain_count || (data.uncertain_flags ? data.uncertain_flags.length : 0);

    container.innerHTML = `
      <div class="card" style="margin-top: 24px; border-color: rgba(139, 92, 246, 0.4);">
        <div class="card-header">
          <div>
            <h4 style="color: #c084fc; font-size: 16px;">✅ Xuất Bản Bộ 2 Tệp Học Thuật Thành Công!</h4>
            <p style="color: #94a3b8; font-size: 12px; margin-top: 4px;">Định dạng chuẩn APA 7th & Ma trận liên kết trích dẫn Zotero CSL (Zero Fabrication 100%).</p>
          </div>
          <button class="btn btn-green btn-sm" onclick="App.openWindowsExplorer('${pathA}')">
            📂 Mở Thư Mục Chứa Tệp
          </button>
        </div>

        <div style="margin-bottom: 16px;">
          <!-- File A Card -->
          <div class="card" style="background: rgba(139, 92, 246, 0.08); border-color: rgba(139, 92, 246, 0.3); margin-bottom: 14px;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; margin-bottom: 8px;">
              <h5 style="color: #a78bfa; font-size: 14px; margin: 0;">📄 TỆP A: Báo Cáo Chuyên Đề / Bài Báo Học Thuật (APA 7th)</h5>
              <span class="badge badge-green" style="font-size: 11px;">Tích hợp Xu hướng OpenAlex</span>
            </div>
            <p style="font-size: 12px; color: #cbd5e1; margin-bottom: 12px;">Bản thảo học thuật IMRaD hoàn chỉnh, tích hợp mã trường Zotero XML DOM và đồ họa phân giải cao 300 DPI.</p>
            <div style="display: flex; gap: 8px; flex-wrap: wrap;">
              <button class="btn btn-primary btn-sm" onclick="App.openFileInSystem('${pathA}')">📝 Mở Word (.docx)</button>
              <button class="btn btn-secondary btn-sm" onclick="App.downloadFile('${pathA}')">📥 Tải về (.docx)</button>
              <button class="btn btn-secondary btn-sm" onclick="App.downloadFile('${pathA.replace(/\.docx$/i, '.md')}')">📥 Tải về (.md)</button>
            </div>
          </div>

          <!-- File B Card -->
          <div class="card" style="background: rgba(59, 130, 246, 0.08); border-color: rgba(59, 130, 246, 0.3);">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; margin-bottom: 8px;">
              <h5 style="color: #60a5fa; font-size: 14px; margin: 0;">📊 TỆP B: Ma Trận Truy Xuất Y Văn 6 Cột & Đối Soát Bằng Chứng</h5>
              <span class="badge badge-blue" style="font-size: 11px;">Đối Soát 1-1 Bằng Chứng Thực</span>
            </div>
            <p style="font-size: 12px; color: #cbd5e1; margin-bottom: 12px;">Bảng ma trận truy xuất nguồn gốc học thuật (ID, Tác giả & Năm, Luận điểm, Bằng chứng định lượng nguyên bản, Lỗ hổng & Đóng góp lý thuyết).</p>
            <div style="display: flex; gap: 8px; flex-wrap: wrap;">
              ${pathB ? `<button class="btn btn-primary btn-sm" onclick="App.openFileInSystem('${pathB}')">📝 Mở Word (.docx)</button>` : ''}
              ${pathB ? `<button class="btn btn-secondary btn-sm" onclick="App.downloadFile('${pathB}')">📥 Tải về (.docx)</button>` : ''}
              ${pathB ? `<button class="btn btn-secondary btn-sm" onclick="App.downloadFile('${pathB.replace(/\.docx$/i, '.md')}')">📥 Tải về (.md)</button>` : ''}
            </div>
          </div>
        </div>

        <!-- Companion Bibliography Export (.RIS & .BIB) -->
        <div class="card" style="background: rgba(16, 185, 129, 0.08); border-color: rgba(16, 185, 129, 0.3); margin-bottom: 20px;">
          <h5 style="color: #34d399; font-size: 14px; margin-bottom: 6px;">📚 TỆP DANH MỤC THAM KHẢO ĐỒNG HÀNH (COMPANION BIBLIOGRAPHY)</h5>
          <p style="font-size: 12px; color: #cbd5e1; margin-bottom: 12px;">Xuất danh mục toàn bộ tài liệu thực chứng với 100% mã DOI thực để nhập 1-click vào Zotero / Mendeley hoặc trình biên dịch LaTeX BibTeX.</p>
          <div style="display: flex; gap: 10px; flex-wrap: wrap;">
            ${pathRis ? `<button class="btn btn-green btn-sm" onclick="App.downloadFile('${pathRis}')">📥 Tải Tệp .RIS (Zotero 1-Click)</button>` : ''}
            ${pathBib ? `<button class="btn btn-secondary btn-sm" style="border-color: #10b981; color: #6ee7b7;" onclick="App.downloadFile('${pathBib}')">📥 Tải Tệp .BIB (BibTeX)</button>` : ''}
          </div>
        </div>

        ${uncertainCount > 0 ? `
          <div style="background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.35); border-radius: 8px; padding: 10px 14px; margin-bottom: 14px; color: #fbbf24; font-size: 12.5px;">
            ⚠️ <strong>Cảnh báo Tính Không Chắc Chắn:</strong> Phát hiện ${uncertainCount} điểm nghi vấn/chưa có bằng chứng đầy đủ đã được gắn cờ <code>[uncertain]</code> để chuyên gia kiểm chứng độc lập.
          </div>
        ` : ''}

        ${data.looped_flows_audit ? `
          <div class="card" style="background: rgba(99, 102, 241, 0.09); border-color: rgba(99, 102, 241, 0.35); margin-bottom: 16px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
              <h5 style="color: #a5b4fc; font-size: 13.5px; margin: 0;">🧠 KIỂM ĐỊNH SUY LUẬN LUỒNG LẶP (LOOPED FLOWS / arXiv:2609.11801)</h5>
              <span class="badge ${data.looped_flows_audit.spurious_attractor_detected ? 'badge-orange' : 'badge-green'}" style="font-size: 11px;">
                ${data.looped_flows_audit.spurious_attractor_detected ? '⚠️ Cảnh báo Ngụy biện tự tin' : '🛡️ Hội tụ an toàn'}
              </span>
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 8px; margin: 8px 0; font-size: 12px;">
              <div style="background: rgba(15, 23, 42, 0.5); padding: 6px 10px; border-radius: 6px;">
                <span style="color: #94a3b8;">Chỉ số Bão hòa ACT q(z):</span>
                <strong style="color: #60a5fa; margin-left: 4px;">${data.looped_flows_audit.act_score || 0.0}</strong>
              </div>
              <div style="background: rgba(15, 23, 42, 0.5); padding: 6px 10px; border-radius: 6px;">
                <span style="color: #94a3b8;">Hội tụ Sai số R_i:</span>
                <strong style="color: #34d399; margin-left: 4px;">${data.looped_flows_audit.final_residual || 0.03}</strong>
              </div>
              <div style="background: rgba(15, 23, 42, 0.5); padding: 6px 10px; border-radius: 6px;">
                <span style="color: #94a3b8;">Số liệu Đo lường:</span>
                <strong style="color: #fbbf24; margin-left: 4px;">${data.looped_flows_audit.metric_count || 0}</strong>
              </div>
            </div>
            <p style="font-size: 11.5px; color: #cbd5e1; margin: 4px 0 0 0;">${data.looped_flows_audit.recommendation || ''}</p>
          </div>
        ` : ''}

        <div class="form-group">
          <label class="form-label">Xem Trước Nội Dung Tệp A (Trích Đoạn):</label>
          <div class="preview-pane" style="max-height: 250px;">
            <pre style="white-space: pre-wrap; font-family: inherit; margin: 0; color: #e2e8f0;">${fileA.preview || "Nội dung tệp A đã được tạo thành công."}</pre>
          </div>
        </div>
      </div>
    `;
  }
};

// Global Window Export
window.AcademicWriterUI = AcademicWriterUI;
