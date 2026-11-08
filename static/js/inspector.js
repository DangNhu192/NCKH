/**
 * static/js/inspector.js
 * ======================
 * Frontend Controller cho Trình Đối Soát Dữ Liệu Gốc Song Song
 * & Cổng Kiểm Duyệt 4 Tầng Tự Động (Dual-Pane Evidence Inspector v4.2)
 */

const InspectorUI = (() => {
  let _catalog = {};
  let _lastReport = null;

  async function init() {
    loadCatalog();
  }

  async function loadCatalog() {
    try {
      const res = await fetch("/api/inspector/catalog");
      const data = await res.json();
      if (res.ok && data.status === "success") {
        _catalog = data.catalog || {};
        renderCatalogTable(_catalog);
        const countBadge = document.getElementById("inspector-catalog-count");
        if (countBadge) countBadge.innerText = `${data.total || Object.keys(_catalog).length} vi luận điểm`;
      }
    } catch (e) {
      console.warn("Không thể nạp catalog đối soát:", e);
    }
  }

  function renderCatalogTable(catalog) {
    const tbody = document.getElementById("inspector-catalog-tbody");
    if (!tbody) return;

    const items = Object.entries(catalog);
    if (items.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:24px; color:#94a3b8;">Chưa có danh mục vi luận điểm nào. Bấm <strong>"⚡ Tạo Gói Đối Soát &amp; Kiểm Duyệt 4 Tầng"</strong> để khởi tạo.</td></tr>`;
      return;
    }

    tbody.innerHTML = items.map(([id, item], idx) => {
      const cleanDoi = item.doi ? item.doi.replace(/^https?:\/\/(?:dx\.)?doi\.org\//i, '').trim() : '';
      return `
        <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
          <td style="text-align:center; font-weight:700; color:#94a3b8; font-size:11px;">${idx + 1}</td>
          <td>
            <div style="font-weight:700; color:#60a5fa; font-size:12px;">${id}</div>
            <div style="font-size:11px; color:#cbd5e1;">${item.author || 'Tác giả'}</div>
            ${cleanDoi ? `
              <div style="display:flex; gap:4px; margin-top:4px;">
                <a href="https://doi.org/${encodeURIComponent(cleanDoi)}" target="_blank" class="badge badge-blue" style="font-size:10px; text-decoration:none;">🌐 DOI</a>
                <a href="https://sci-hub.se/${encodeURIComponent(cleanDoi)}" target="_blank" class="badge badge-red" style="font-size:10px; text-decoration:none; background:rgba(220,38,38,0.2); color:#fca5a5; border:1px solid rgba(220,38,38,0.4);">⚡ Sci-Hub</a>
              </div>
            ` : ''}
          </td>
          <td>
            <div style="font-size:11.5px; color:#f8fafc; font-family:monospace; max-width:200px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;" title="${item.pdf || ''}">
              📄 ${item.pdf || 'N/A'}
            </div>
          </td>
          <td style="text-align:center;">
            <span class="badge badge-green" style="font-size:11px; padding:2px 8px;">Trang ${item.page || 1}</span>
          </td>
          <td>
            <div style="font-size:11.5px; color:#e2e8f0; font-style:italic; max-width:320px; max-height:48px; overflow:hidden; text-overflow:ellipsis;" title="${item.quote_en || ''}">
              "${item.quote_en || ''}"
            </div>
            <div style="font-size:11px; color:#94a3b8; margin-top:2px;">
              ${item.quote_vi || ''}
            </div>
          </td>
          <td>
            <span style="font-size:11px; color:#f59e0b; background:rgba(245,158,11,0.1); padding:2px 6px; border-radius:4px;">
              ${item.params || 'N/A'}
            </span>
          </td>
        </tr>
      `;
    }).join('');
  }

  async function generateBundle() {
    const btn = document.getElementById("btn-inspector-gen-bundle");
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = '<span class="spinner-btn"></span> <span>Đang tạo gói đối soát v4.2...</span>';
    }

    App.toast("🔬 Đang đóng gói Bộ 4 Sản Phẩm Đối Soát & Kiểm Duyệt 4 Tầng...", "info");

    try {
      const res = await fetch("/api/inspector/generate-bundle", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          article_title: "BÁO CÁO KHOA HỌC CHUẨN MỰC THẠC SĨ (KÈM BỘ ĐỐI SOÁT THỰC CHỨNG)"
        })
      });

      const data = await res.json();
      if (res.ok && data.status === "success") {
        App.toast("✅ Đã tạo thành công Trọn bộ Đối Soát Song Song v4.2!", "success");
        await loadCatalog();
        await runGateVerification();
      } else {
        App.toast(data.detail || "Lỗi tạo gói đối soát", "error");
      }
    } catch (e) {
      App.toast("Lỗi kết nối máy chủ: " + e.message, "error");
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = '⚡ Tạo Gói Đối Soát &amp; Kiểm Duyệt 4 Tầng';
      }
    }
  }

  async function runGateVerification() {
    const btn = document.getElementById("btn-inspector-verify-gate");
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = '<span class="spinner-btn"></span> <span>Đang kiểm toán 4 tầng...</span>';
    }

    App.toast("🛡️ Đang chạy Pre-Commit Verification Gate 4 Tầng...", "info");

    try {
      const res = await fetch("/api/inspector/verify-gate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({})
      });

      const data = await res.json();
      if (res.ok && data.status === "success") {
        _lastReport = data.report || {};
        renderGateScorecard(_lastReport);
        if (data.gate_passed) {
          App.toast("🎉 CHÚC MỪNG: Cổng Kiểm Duyệt 4 Tầng Đạt 100% (Zero-Hallucination Verified)!", "success");
        } else {
          App.toast(`⚠️ Phát hiện ${_lastReport.total_errors || 0} điểm chưa khớp trong kiểm toán 4 tầng.`, "warning");
        }
      } else {
        App.toast(data.detail || "Lỗi chạy cổng kiểm duyệt", "error");
      }
    } catch (e) {
      App.toast("Lỗi kết nối kiểm toán: " + e.message, "error");
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = '🛡️ Chạy Kiểm Duyệt 4 Tầng';
      }
    }
  }

  function renderGateScorecard(report) {
    const box = document.getElementById("inspector-gate-scorecard");
    if (!box) return;

    box.style.display = "block";
    const l1 = report.layer1 || {};
    const l2 = report.layer2 || {};
    const l3 = report.layer3 || {};
    const l4 = report.layer4 || {};

    box.innerHTML = `
      <div style="background: rgba(15, 23, 42, 0.9); border: 1.5px solid ${report.passed ? '#10b981' : '#f59e0b'}; border-radius: 8px; padding: 18px; margin-bottom: 20px;">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px; margin-bottom:14px; border-bottom:1px solid rgba(255,255,255,0.08); padding-bottom:10px;">
          <div>
            <h4 style="color:${report.passed ? '#34d399' : '#fbbf24'}; font-size:16px; font-weight:800; margin:0;">
              ${report.passed ? '✅ PRE-COMMIT VERIFICATION GATE: 100% PASS' : '⚠️ PRE-COMMIT AUDIT: PHÁT HIỆN ĐIỂM CẦN ĐIỀU CHỈNH'}
            </h4>
            <p style="color:#94a3b8; font-size:12px; margin:3px 0 0 0;">Quy chuẩn Kiểm duyệt 4 Tầng Tự Động • Giao Thức Liêm Chính Học Thuật v4.2</p>
          </div>
          <span class="badge ${report.passed ? 'badge-green' : 'badge-yellow'}" style="font-size:12px; padding:6px 14px; font-weight:700;">
            ${l4.status || (report.passed ? 'APPROVED' : 'ACTION REQUIRED')}
          </span>
        </div>

        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:12px; margin-bottom:14px;">
          <!-- LAYER 1 -->
          <div style="background:rgba(0,0,0,0.3); padding:12px; border-radius:6px; border-left:3px solid ${l1.passed ? '#10b981' : '#f87171'};">
            <div style="font-size:11px; color:#94a3b8;">TẦNG 1: Đối Soát Chữ Thô PDF</div>
            <div style="font-size:14px; font-weight:700; color:#f8fafc; margin:4px 0;">
              ${l1.passed ? '✓ Khớp Mặt Chữ' : '✕ Có Lệch Chữ'}
            </div>
            <div style="font-size:11px; color:#cbd5e1;">Xác thực: <strong>${l1.total_verified || 0}</strong> bài (Match >= 0,60)</div>
          </div>

          <!-- LAYER 2 -->
          <div style="background:rgba(0,0,0,0.3); padding:12px; border-radius:6px; border-left:3px solid ${l2.passed ? '#10b981' : '#f87171'};">
            <div style="font-size:11px; color:#94a3b8;">TẦNG 2: Nút Bấm &amp; Chống Gian Lận</div>
            <div style="font-size:14px; font-weight:700; color:#f8fafc; margin:4px 0;">
              ${l2.passed ? '✓ Anti-Topic Fraud Sạch' : '✕ Cảnh Báo Nút'}
            </div>
            <div style="font-size:11px; color:#cbd5e1;">Tổng nút: <strong>${l2.total_buttons || 0}</strong> nút trích dẫn</div>
          </div>

          <!-- LAYER 3 -->
          <div style="background:rgba(0,0,0,0.3); padding:12px; border-radius:6px; border-left:3px solid ${l3.passed ? '#10b981' : '#f87171'};">
            <div style="font-size:11px; color:#94a3b8;">TẦNG 3: Đồng Bộ Word DOCX &amp; HTML</div>
            <div style="font-size:14px; font-weight:700; color:#f8fafc; margin:4px 0;">
              ${l3.passed ? '✓ Khóa Số Liệu Chuẩn' : '✕ Lệch Số Liệu'}
            </div>
            <div style="font-size:11px; color:#cbd5e1;">Chỉ số khóa: <strong>${l3.locked_metrics_count || 0}</strong> thông số</div>
          </div>

          <!-- LAYER 4 -->
          <div style="background:rgba(0,0,0,0.3); padding:12px; border-radius:6px; border-left:3px solid ${l4.passed ? '#10b981' : '#f87171'};">
            <div style="font-size:11px; color:#94a3b8;">TẦNG 4: Ngắt Mạch Liêm Chính</div>
            <div style="font-size:14px; font-weight:700; color:${l4.passed ? '#34d399' : '#fca5a5'}; margin:4px 0;">
              ${l4.passed ? '✓ Zero-Hallucination' : '✕ Bị Chặn Nghiệm Thu'}
            </div>
            <div style="font-size:11px; color:#cbd5e1;">Tổng lỗi: <strong>${report.total_errors || 0}</strong></div>
          </div>
        </div>

        ${(report.total_errors > 0) ? `
          <div style="background:rgba(239,68,68,0.1); border:1px solid rgba(239,68,68,0.3); border-radius:6px; padding:10px 14px; font-size:12px; color:#fca5a5;">
            <strong>Chi tiết các điểm cần lưu ý:</strong>
            <ul style="margin:4px 0 0 16px;">
              ${[...(l1.errors || []), ...(l2.errors || []), ...(l3.errors || [])].map(e => `<li>${e}</li>`).join('')}
            </ul>
          </div>
        ` : ''}
      </div>
    `;
  }

  function openStandaloneWindow() {
    window.open("/api/inspector/view-html", "_blank");
  }

  async function downloadMatrixDocx() {
    App.toast("Đang xuất bản Bảng Ma trận Truy xuất Nguồn gốc (.docx Khổ Ngang)...", "info");
    try {
      const res = await fetch("/api/inspector/generate-matrix", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({})
      });
      const data = await res.json();
      if (res.ok && data.status === "success") {
        App.toast("✅ Đã xuất bản Bảng Ma trận A4 Landscape thành công!", "success");
        if (data.docx_path && window.App && App.downloadFile) {
          App.downloadFile(data.docx_path);
        }
      } else {
        App.toast(data.detail || "Lỗi xuất bảng ma trận", "error");
      }
    } catch (e) {
      App.toast("Lỗi tải bảng: " + e.message, "error");
    }
  }

  return {
    init,
    loadCatalog,
    generateBundle,
    runGateVerification,
    openStandaloneWindow,
    downloadMatrixDocx
  };
})();

document.addEventListener("DOMContentLoaded", () => InspectorUI.init());
window.InspectorUI = InspectorUI;
