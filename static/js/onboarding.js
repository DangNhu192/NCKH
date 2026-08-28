/**
 * WEB SUPER v2.0 — OnboardingGuide
 * Hiển thị hướng dẫn sử dụng cho từng chức năng:
 * - Khi người dùng mở chức năng lần đầu tiên
 * - Khi người dùng thiếu thông tin cần thiết (API key, Zotero...)
 * - Lưu trạng thái đã xem vào localStorage
 */

const OnboardingGuide = (() => {
  const STORAGE_PREFIX = 'ws_onboard_seen_';
  const READY_KEY = 'ws_user_ready';
  const READY_TTL = 5 * 60 * 1000; // Cache 5 phút

  const GUIDES = {
    'home-tab': {
      title: '👋 Chào mừng đến WEB SUPER v2.0!',
      icon: '🏠',
      steps: [
        '🔐 <strong>Đăng nhập Google</strong> ở góc trên phải để bắt đầu sử dụng.',
        '🔑 Vào <strong>⚙️ Cài Đặt</strong> để nhập <strong>API Gemini cá nhân</strong> và cấu hình Zotero.',
        '🎫 Nếu chưa có gói, bấm <strong>💳 Nâng Cấp Gói</strong> để mua key kích hoạt.',
        '📚 Sau khi đủ điều kiện, tất cả 8 chức năng nghiên cứu sẽ mở khóa hoàn toàn.'
      ]
    },
    'pipeline-tab': {
      title: '⚡ Quy Trình Nghiên Cứu 7 Bước',
      icon: '🔬',
      steps: [
        '📌 Nhập <strong>chủ đề nghiên cứu</strong> vào ô Chủ Đề ở đầu trang.',
        '▶️ Nhấn <strong>"Chạy Từng Bước"</strong> để đi qua 7 bước liên kết IMRaD & GATE.',
        '🤖 Mỗi bước sẽ tự động gọi AI Gemini cá nhân của bạn để xử lý.',
        '💾 Kết quả mỗi bước được lưu tự động vào Workspace.',
        '⚠️ Yêu cầu: Đã nhập API Gemini cá nhân + Gói Pro/Enterprise.'
      ],
      requires_api: true
    },
    'harvester-tab': {
      title: '📰 Thu Thập Tài Liệu Đa Nguồn',
      icon: '🔍',
      steps: [
        '🔎 Nhập <strong>chủ đề hoặc từ khóa</strong> vào ô tìm kiếm.',
        '📚 Chọn nguồn tìm kiếm: <strong>Google Scholar, PubMed, ArXiv, CrossRef</strong> hoặc tất cả.',
        '📋 Xem lại kết quả và <strong>tích chọn</strong> các bài báo phù hợp.',
        '💾 Bấm <strong>"Lưu vào Zotero"</strong> để lưu vào thư viện Zotero cá nhân và Workspace.',
        '⚠️ Yêu cầu: Đã cấu hình <strong>Zotero API Key + User ID</strong> trong Cài Đặt.'
      ],
      requires_zotero: true
    },
    'zotero-tab': {
      title: '📚 Chuyển Đổi Mã Trích Dẫn Zotero',
      icon: '🔄',
      steps: [
        '📂 Tải lên file <strong>Word (.docx)</strong> có chứa mã trích dẫn Zotero CSL.',
        '🎯 Chọn <strong>phong cách trích dẫn</strong> mong muốn (APA 7th, Harvard, Vancouver...).',
        '⚡ Nhấn <strong>"Chuyển Đổi"</strong> để hệ thống tự động thay thế toàn bộ mã trích dẫn.',
        '⬇️ Tải về file Word đã được định dạng trích dẫn chuẩn.',
        '⚠️ Yêu cầu: Đã kết nối <strong>Zotero Library</strong> qua Cài Đặt.'
      ],
      requires_zotero: true
    },
    'writer-tab': {
      title: '🎓 Viết Học Thuật 2-File Chuẩn APA 7th',
      icon: '✍️',
      steps: [
        '📝 Nhập <strong>chủ đề bài viết</strong> và loại bài báo (Báo cáo, Luận văn, Tạp chí...).',
        '📋 Xem lại <strong>đề cương AI đề xuất</strong> và chỉnh sửa nếu cần.',
        '⚡ Nhấn <strong>"Tạo 2 File"</strong> để sinh tự động: File A (nội dung học thuật) + File B (danh mục tài liệu tham khảo APA 7th).',
        '⬇️ Tải về 2 file Word chuẩn định dạng học thuật.',
        '⚠️ Yêu cầu: API Gemini cá nhân + Gói Pro/Enterprise.'
      ],
      requires_api: true
    },
    'editorial-tab': {
      title: '🏢 Tòa Soạn Báo AI v3.1 (6 Ban GATE)',
      icon: '📰',
      steps: [
        '📰 Nhập <strong>chủ đề bài báo</strong> và mục đích xuất bản.',
        '🏛️ Chọn <strong>Ban biên tập</strong>: Ban Nghiên Cứu, Ban Thực Tiễn, Ban Lý Luận...',
        '🔬 Hệ thống sẽ tự động chạy qua <strong>6 trạm GATE kiểm duyệt</strong> học thuật.',
        '📄 Kết quả là bài báo hoàn chỉnh đạt chuẩn xuất bản.',
        '⚠️ Yêu cầu: API Gemini cá nhân + Gói Pro/Enterprise.'
      ],
      requires_api: true
    },
    'math-chem-tab': {
      title: '📐 Biên Tập Toán - Hóa & Biểu Đồ 300 DPI',
      icon: '📐',
      steps: [
        '📐 Nhập <strong>công thức LaTeX</strong> để chuyển đổi sang Microsoft Word Equation (<m:oMath>) gốc.',
        '🤖 Nhấn <strong>"AI Sinh Lời Diễn Giải"</strong> để tạo đoạn văn 4 yếu tố (Tên, Biến số, Đơn vị, Ý nghĩa).',
        '📊 Dùng <strong>Máy Tạo Biểu Đồ & Sơ Đồ</strong> để xuất ảnh khoa học tiếng Việt chuẩn 300 DPI.',
        '⚡ Kéo thả file Word vào <strong>Nâng Cấp 1-Click</strong> để tự động chuẩn hóa hóa học & công thức.'
      ]
    },
    'bigquery-tab': {
      title: '📊 Phân Tích Dữ Liệu Lớn (BigQuery AI/ML)',
      icon: '📊',
      steps: [
        '📂 Tải lên tệp <strong>CSV / JSON</strong> dữ liệu đo đạc hoặc chọn <strong>Dữ Liệu Mẫu</strong>.',
        '📈 Tab <strong>\"Dự Báo Chuỗi Thời Gian\"</strong>: Mô hình hóa ARIMA_PLUS với khoảng tin cậy 95%.',
        '🚨 Tab <strong>\"Phát Hiện Dị Biệt\"</strong>: Rà soát ngoại lai và sai số đo đạc thực nghiệm.',
        '🔑 Tab <strong>\"Động Lực Cốt Lõi\"</strong>: Xác định nhân tố chi phối mạnh nhất đến kết quả.',
        '📝 Bấm <strong>\"Xuất Báo Cáo Word\"</strong> để tạo file .docx kèm biểu đồ 300 DPI tự động.'
      ],
      requires_api: true
    },
    'humanizer-tab': {
      title: '🤖➡️👤 Khử Dấu Vết AI (Humanizer)',
      icon: '🧠',
      steps: [
        '📄 Dán hoặc tải lên <strong>văn bản do AI tạo ra</strong> cần được nhân hóa.',
        '⚙️ Chọn mức độ nhân hóa: <strong>Nhẹ, Trung bình, Nâng cao</strong>.',
        '✨ Nhấn <strong>"Khử Dấu Vết"</strong> để AI viết lại theo phong cách con người tự nhiên.',
        '📊 Hệ thống hiển thị % độ tương đồng AI trước và sau xử lý.',
        '⚠️ Yêu cầu: API Gemini cá nhân + Gói Pro/Enterprise.'
      ],
      requires_api: true
    },
    'admin-tab': {
      title: '👑 Quản Trị Viên & Cộng Tác Viên',
      icon: '🛡️',
      steps: [
        '👥 Tab <strong>"Danh Sách Tài Khoản"</strong>: Xem, phân quyền, đổi gói, gia hạn, khóa/mở tài khoản.',
        '🔑 Tab <strong>"Quản Lý License Key"</strong>: Tạo mã kích hoạt cho từng gói (Standard/Pro/Enterprise) và theo dõi trạng thái.',
        '📊 Tab <strong>"Bảng Tính Năng Gói"</strong>: Xem ma trận quyền hạn của từng gói.',
        '🤝 Quyền <strong>CTV/Reseller</strong>: Được tạo key và quản lý khách hàng cá nhân.',
        '⚠️ Chỉ Admin và CTV mới có quyền truy cập mục này.'
      ]
    }
  };

  let _noticeBar = null;

  function _hasSeen(tabId) {
    return localStorage.getItem(STORAGE_PREFIX + tabId) === '1';
  }

  function _markSeen(tabId) {
    localStorage.setItem(STORAGE_PREFIX + tabId, '1');
  }

  function _getReadyCache() {
    try {
      const cached = JSON.parse(localStorage.getItem(READY_KEY) || 'null');
      if (cached && (Date.now() - cached.ts) < READY_TTL) return cached.data;
    } catch (e) {}
    return null;
  }

  function _setReadyCache(data) {
    localStorage.setItem(READY_KEY, JSON.stringify({ ts: Date.now(), data }));
  }

  function clearReadyCache() {
    localStorage.removeItem(READY_KEY);
  }

  async function _fetchReadyStatus() {
    const cached = _getReadyCache();
    if (cached) return cached;
    try {
      const headers = (window.AuthManager && AuthManager.token)
        ? { 'Authorization': `Bearer ${AuthManager.token}` } : {};
      const r = await fetch('/api/user/check-ready', { headers });
      if (!r.ok) return null;
      const data = await r.json();
      _setReadyCache(data);
      return data;
    } catch (e) {
      return null;
    }
  }

  function _showNoticeBar(reason, action) {
    if (_noticeBar) _noticeBar.remove();
    let msg = '', btnHtml = '';
    if (reason === 'no_plan') {
      msg = '⚠️ Bạn chưa có gói sử dụng hợp lệ. Vui lòng mua key kích hoạt để sử dụng đầy đủ tính năng.';
      btnHtml = `<button class="notice-btn" onclick="OnboardingGuide.openPaymentModal()">💳 Mua Key Ngay</button>`;
    } else if (reason === 'no_api') {
      msg = '🔑 Bạn chưa nhập API Gemini / ChatGPT cá nhân. Vào Cài Đặt để cấu hình trước khi sử dụng.';
      btnHtml = `<button class="notice-btn" onclick="App.openSettingsModal()">⚙️ Mở Cài Đặt</button>`;
    } else {
      return;
    }
    const bar = document.createElement('div');
    bar.className = 'onboard-notice-bar';
    bar.innerHTML = `
      <span class="notice-text">${msg}</span>
      ${btnHtml}
      <button class="notice-close" onclick="this.parentElement.remove()" title="Đóng">✕</button>
    `;
    document.body.insertBefore(bar, document.body.firstChild);
    _noticeBar = bar;
  }

  function _hideNoticeBar() {
    if (_noticeBar) { _noticeBar.remove(); _noticeBar = null; }
  }

  async function checkAndShow(tabId) {
    const guide = GUIDES[tabId];
    if (!guide) return;

    // Check user readiness from API
    if (window.AuthManager && AuthManager.isLoggedIn) {
      const status = await _fetchReadyStatus();
      if (status && !status.ready) {
        _showNoticeBar(status.reason, status.action);
      } else {
        _hideNoticeBar();
      }
    }

    // Show feature guide if first time
    if (!_hasSeen(tabId)) {
      showFeatureGuide(tabId);
      _markSeen(tabId);
    }
  }

  function showFeatureGuide(tabId) {
    const guide = GUIDES[tabId];
    if (!guide) return;
    const stepsHtml = guide.steps.map(s => `<li>${s}</li>`).join('');
    const modal = document.createElement('div');
    modal.className = 'onboard-modal-overlay';
    modal.innerHTML = `
      <div class="onboard-modal">
        <div class="onboard-header">
          <span class="onboard-icon">${guide.icon}</span>
          <h3>${guide.title}</h3>
        </div>
        <ul class="onboard-steps">${stepsHtml}</ul>
        <div class="onboard-footer">
          <label class="onboard-skip-label">
            <input type="checkbox" onchange="if(this.checked){ localStorage.setItem('ws_onboard_seen_${tabId}', '1'); }"> Không hiện lại
          </label>
          <button class="btn btn-primary" onclick="this.closest('.onboard-modal-overlay').remove()">✅ Đã Hiểu, Bắt Đầu!</button>
        </div>
      </div>
    `;
    modal.addEventListener('click', (e) => { if (e.target === modal) modal.remove(); });
    document.body.appendChild(modal);
  }

  function openPaymentModal() {
    const el = document.getElementById('modal-payment');
    if (el) el.classList.add('active');
  }

  function closePaymentModal() {
    const el = document.getElementById('modal-payment');
    if (el) el.classList.remove('active');
  }

  function resetAllGuides() {
    Object.keys(GUIDES).forEach(k => localStorage.removeItem(STORAGE_PREFIX + k));
    clearReadyCache();
    if (window.App) App.toast('Đã đặt lại hướng dẫn sử dụng. Mỗi chức năng sẽ hiển thị hướng dẫn khi bạn vào lần sau.', 'info');
  }

  async function checkReadyOnLogin() {
    clearReadyCache();
    const status = await _fetchReadyStatus();
    if (status && !status.ready) {
      _showNoticeBar(status.reason, status.action);
    } else {
      _hideNoticeBar();
    }
  }

  return { checkAndShow, showFeatureGuide, openPaymentModal, closePaymentModal, resetAllGuides, checkReadyOnLogin, clearReadyCache };
})();

// Global Window Export
window.OnboardingGuide = OnboardingGuide;
