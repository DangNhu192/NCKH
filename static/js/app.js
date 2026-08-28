// Main Application Coordinator for WEB SUPER v2.0
const App = {
  currentTab: "pipeline-tab",

  init() {
    this.setupTabs();
    this.setupModals();
    this.setupHeaderCompact();
    this.setupBranchAutoCollapse();
    this.setupKeyboardShortcuts();
    this.restoreSidebarPreference();
    this.updateStatus();
    AuthManager.init();

    // Default sync to active tab
    this.syncActiveBranch(this.currentTab || 'home-tab');

    // Initialize Dropzones across all modules
    if (window.PipelineUI && PipelineUI.init) PipelineUI.init();
    if (window.NotebookLMUI && NotebookLMUI.init) NotebookLMUI.init();
    if (window.ZoteroUI && ZoteroUI.init) ZoteroUI.init();
    if (window.EditorialUI && EditorialUI.init) EditorialUI.init();
    if (window.HumanizerUI && HumanizerUI.init) HumanizerUI.init();
    if (window.HistoryUI && HistoryUI.init) HistoryUI.init();
    if (window.AdminUI && AdminUI.init) AdminUI.init();

    // Auto-refresh status periodically
    setInterval(() => this.updateStatus(), 30000);
  },

  setupKeyboardShortcuts() {
    window.addEventListener('keydown', (e) => {
      // Ctrl+B: Toggle Sidebar Compact / Dock
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'b') {
        e.preventDefault();
        this.toggleSidebarCompact();
      }
      // Ctrl+K: Focus Feature Search
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        const searchInput = document.getElementById('sidebar-feature-search');
        if (searchInput) {
          const sidebar = document.querySelector('.app-sidebar');
          if (sidebar && sidebar.classList.contains('sidebar-compact')) {
            this.toggleSidebarCompact();
          }
          searchInput.focus();
          searchInput.select();
        }
      }
      // Escape in search: Clear search
      if (e.key === 'Escape') {
        const searchInput = document.getElementById('sidebar-feature-search');
        if (searchInput && document.activeElement === searchInput) {
          this.clearSidebarSearch();
          searchInput.blur();
        }
      }
    });
  },

  toggleSidebarCompact() {
    const sidebar = document.querySelector('.app-sidebar');
    if (!sidebar) return;
    const isNowCompact = sidebar.classList.toggle('sidebar-compact');
    localStorage.setItem('websuper_sidebar_compact', isNowCompact ? '1' : '0');

    const iconEl = document.getElementById('btn-toggle-sidebar-dock-icon');
    if (iconEl) {
      iconEl.textContent = isNowCompact ? '▶' : '◨';
    }
  },

  restoreSidebarPreference() {
    const isCompact = localStorage.getItem('websuper_sidebar_compact') === '1';
    if (isCompact) {
      const sidebar = document.querySelector('.app-sidebar');
      if (sidebar) sidebar.classList.add('sidebar-compact');
      const iconEl = document.getElementById('btn-toggle-sidebar-dock-icon');
      if (iconEl) iconEl.textContent = '▶';
    }
  },

  toggleAllBranches() {
    const groups = document.querySelectorAll('.nav-branch-group');
    const hasCollapsed = Array.from(groups).some(g => g.classList.contains('collapsed'));
    
    groups.forEach(g => {
      if (hasCollapsed) {
        g.classList.remove('collapsed');
      } else {
        g.classList.add('collapsed');
      }
    });

    const iconEl = document.getElementById('btn-toggle-all-branches-icon');
    if (iconEl) {
      iconEl.textContent = hasCollapsed ? '⇲' : '⇱';
    }
  },

  clearSidebarSearch() {
    const input = document.getElementById('sidebar-feature-search');
    if (input) {
      input.value = '';
      this.filterSidebarTabs('');
      input.focus();
    }
    const clearBtn = document.getElementById('sidebar-search-clear');
    if (clearBtn) clearBtn.style.display = 'none';
  },

  setupBranchAutoCollapse() {
    // 1. Tự động thu gọn các nhánh không được chọn khi click ra ngoài thanh sidebar
    document.addEventListener('click', (e) => {
      const sidebar = document.querySelector('.app-sidebar');
      if (sidebar && !sidebar.contains(e.target)) {
        this.collapseInactiveBranches();
      }
    });

    // 2. Tự động khôi phục thu gọn khi rời chuột khỏi sidebar sau 1 khoảng trễ tự nhiên (1.2s)
    const sidebarEl = document.querySelector('.app-sidebar');
    if (sidebarEl) {
      sidebarEl.addEventListener('mouseleave', () => {
        if (this._sidebarLeaveTimer) clearTimeout(this._sidebarLeaveTimer);
        this._sidebarLeaveTimer = setTimeout(() => {
          this.collapseInactiveBranches();
        }, 1200);
      });
      sidebarEl.addEventListener('mouseenter', () => {
        if (this._sidebarLeaveTimer) clearTimeout(this._sidebarLeaveTimer);
      });
    }
  },

  toggleBranch(headerEl, e) {
    if (e && e.stopPropagation) e.stopPropagation();
    if (!headerEl) return;
    const group = headerEl.closest('.nav-branch-group');
    if (!group) return;

    const isCollapsed = group.classList.contains('collapsed');

    // Accordion Mode: Thu gọn các nhánh khác
    document.querySelectorAll('.nav-branch-group').forEach(grp => {
      if (grp !== group) {
        grp.classList.add('collapsed');
      }
    });

    // Bật/Tắt nhánh hiện tại
    if (isCollapsed) {
      group.classList.remove('collapsed');
    } else {
      group.classList.add('collapsed');
    }
  },

  syncActiveBranch(tabId) {
    const targetTab = tabId || this.currentTab || 'home-tab';
    const activeItem = document.querySelector(`.nav-branch-item[data-tab="${targetTab}"]`);
    const activeGroup = activeItem ? activeItem.closest('.nav-branch-group') : null;

    document.querySelectorAll('.nav-branch-group').forEach(grp => {
      if (grp === activeGroup) {
        grp.classList.remove('collapsed');
      } else {
        grp.classList.add('collapsed');
      }
    });
  },

  collapseInactiveBranches() {
    // Nếu người dùng đang tìm kiếm trong ô search, giữ nguyên kết quả
    const searchInput = document.getElementById('sidebar-feature-search');
    if (searchInput && searchInput.value.trim().length > 0) return;

    this.syncActiveBranch(this.currentTab);
  },

  filterSidebarTabs(query) {
    const q = (query || "").toLowerCase().trim();
    const clearBtn = document.getElementById('sidebar-search-clear');
    if (clearBtn) clearBtn.style.display = q ? 'block' : 'none';

    const groups = document.querySelectorAll('.nav-branch-group');
    
    groups.forEach(grp => {
      const items = grp.querySelectorAll('.nav-branch-item');
      let visibleCount = 0;
      
      items.forEach(item => {
        const text = (item.textContent || "").toLowerCase();
        const title = (item.getAttribute('title') || "").toLowerCase();
        const tooltip = (item.getAttribute('data-tooltip') || "").toLowerCase();
        const match = !q || text.includes(q) || title.includes(q) || tooltip.includes(q);
        
        item.classList.toggle('search-hidden', !match);
        if (match) visibleCount++;
      });

      grp.classList.toggle('search-empty', visibleCount === 0);
      if (q && visibleCount > 0) {
        grp.classList.remove('collapsed');
      }
    });
  },

  setupHeaderCompact() {
    const mainEl = document.querySelector('.app-main');
    const headerEl = document.querySelector('.app-header');
    if (!mainEl || !headerEl) return;
    mainEl.addEventListener('scroll', () => {
      headerEl.classList.toggle('header-compact', mainEl.scrollTop > 40);
    }, { passive: true });
  },

  // ── Skeleton loading helpers ────────────────────────────────────────────
  showSkeleton(containerId, lines = 4) {
    const el = document.getElementById(containerId);
    if (!el) return;
    let html = '<div class="skeleton-card">';
    for (let i = 0; i < lines; i++) {
      const cls = i === 0 ? 'short' : i === lines - 1 ? 'medium' : 'long';
      html += `<div class="skeleton-block skeleton-line ${cls}"></div>`;
    }
    html += '</div>';
    el.innerHTML = html;
  },

  hideSkeleton(containerId) {
    // Content will replace skeleton when real data arrives
    const el = document.getElementById(containerId);
    if (el) { const sk = el.querySelector('.skeleton-card'); if (sk) sk.remove(); }
  },



  setupTabs() {
    const navItems = document.querySelectorAll(".nav-item[data-tab]");
    navItems.forEach(item => {
      item.addEventListener("click", () => {
        const tabId = item.getAttribute("data-tab");
        this.switchTab(tabId);
      });
    });
  },

  requireAuth(actionName = "sử dụng tính năng này") {
    if (!window.AuthManager || !AuthManager.isLoggedIn) {
      this.toast(`⚠️ Bạn cần đăng nhập tài khoản Google để ${actionName}!`, "warning");
      if (window.AuthManager && AuthManager.openAuthModal) {
        AuthManager.openAuthModal();
      }
      return false;
    }
    return true;
  },

  switchTab(tabId) {
    const auth = (typeof AuthManager !== "undefined" ? AuthManager : window.AuthManager);
    const user = auth?.currentUser;

    // If attempting to open functional tabs without login, warn user
    const publicTabs = ['home-tab', 'agency-tab', 'math-chem-tab'];
    if (!publicTabs.includes(tabId) && auth && !auth.isLoggedIn) {
      this.toast("⚠️ Vui lòng đăng nhập Google để truy cập đầy đủ các công cụ nghiên cứu.", "warning");
      if (auth.openAuthModal) {
        auth.openAuthModal();
      }
    }

    // If attempting to open admin tab without admin/reseller role
    if (tabId === "admin-tab") {
      const email = (user?.email || "").toLowerCase().trim();
      const role = (user?.role || "").toLowerCase().trim();
      const isSuperAdmin = (email === "admin@websuper.edu.vn");
      const isReseller = (role === "reseller");
      const isAllowedAdmin = auth && auth.isLoggedIn && (isSuperAdmin || isReseller);
      if (!isAllowedAdmin) {
        this.toast("⚠️ Bạn không có quyền truy cập trang Quản Trị Hệ Thống. Chỉ Quản trị viên (admin@websuper.edu.vn) mới có quyền này.", "warning");
        if (this.currentTab !== "admin-tab") {
          return;
        }
        tabId = "home-tab";
      }
    }

    document.querySelectorAll(".nav-item").forEach(el => el.classList.remove("active"));
    document.querySelectorAll(".tab-pane").forEach(el => el.classList.remove("active"));

    const targetNav = document.querySelector(`.nav-item[data-tab="${tabId}"]`);
    const targetPane = document.getElementById(tabId);

    if (targetNav) targetNav.classList.add("active");
    if (targetPane) targetPane.classList.add("active");
    this.currentTab = tabId;

    // Tự động mở nhánh chứa tab được chọn và thu gọn toàn bộ nhánh khác
    this.syncActiveBranch(tabId);

    // Trigger tab specific refreshes
    if (tabId === "workspace-tab" && window.DocEditor) {
      DocEditor.loadFileList();
    }
    if (tabId === "history-tab" && window.HistoryUI) {
      HistoryUI.loadHistory();
    }
    if (tabId === "admin-tab" && window.AdminUI) {
      AdminUI.loadAllData();
    }
    if (tabId === "agency-tab" && window.AgencyRosterUI) {
      AgencyRosterUI.renderRoster();
    }
    if (tabId === "math-chem-tab" && window.MathChemProUI) {
      MathChemProUI.init();
    }
    if (tabId === "zotero-tab" && window.ZoteroUI) {
      ZoteroUI.checkZoteroStatus();
    }
    if (tabId === "notebooklm-tab" && window.NotebookLMUI) {
      NotebookLMUI.loadNotebooks();
    }
    if (tabId === "bigquery-tab" && window.BigQueryMLUI) {
      BigQueryMLUI.init();
    }

    // Onboarding guide: hiển thị hướng dẫn lần đầu và kiểm tra trạng thái sẵn sàng
    if (window.OnboardingGuide) OnboardingGuide.checkAndShow(tabId);
  },

  async updateStatus() {
    try {
      const res = await fetch("/api/status", {
        headers: AuthManager.token ? { "Authorization": `Bearer ${AuthManager.token}` } : {}
      });
      const data = await res.json();
      
      const fileCountEl = document.getElementById("stat-total-files");
      if (fileCountEl) fileCountEl.innerText = `${data.total_files || 0} tệp`;

      const badgeGoogle = document.getElementById("badge-google-status");
      if (badgeGoogle) {
        badgeGoogle.className = data.has_google_auth ? "badge badge-green" : "badge badge-orange";
        badgeGoogle.innerText = data.has_google_auth ? "Google Auth: Bật" : "Google Auth: Nhập Gmail";
      }

      const badgeGemini = document.getElementById("badge-gemini-status");
      if (badgeGemini) {
        if (data.has_gemini_key) {
          badgeGemini.className = "badge badge-green";
          badgeGemini.innerText = `AI: ${data.active_gemini_model || 'Gemini'} 🚀 (Mới nhất)`;
        } else {
          badgeGemini.className = "badge badge-purple";
          badgeGemini.innerText = "AI: Offline Template Engine";
        }
      }

      // Update Home Tab live indicators
      const homeAiModel = document.getElementById("home-stat-ai-model");
      if (homeAiModel) {
        homeAiModel.innerText = data.has_gemini_key ? `${data.active_gemini_model || 'Gemini 2.5 Flash'} 🚀` : "Offline Template Mode";
        homeAiModel.className = data.has_gemini_key ? "text-cyan" : "text-purple";
      }
      const homeStorage = document.getElementById("home-stat-storage");
      if (homeStorage) {
        homeStorage.innerText = `${data.total_files || 0} tệp trong Workspace`;
      }

      // Update Writer AI Banner dynamically
      const writerBanner = document.getElementById("writer-ai-banner");
      if (writerBanner) {
        if (data.has_gemini_key) {
          writerBanner.style.background = "linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(6, 182, 212, 0.1) 100%)";
          writerBanner.style.borderColor = "rgba(52, 211, 153, 0.4)";
          writerBanner.innerHTML = `
            <div style="display: flex; align-items: center; gap: 12px;">
              <span style="font-size: 24px;">🤖</span>
              <div>
                <strong style="color: #34d399; font-size: 13px;">Google AI Đã Sẵn Sàng (Mô hình: ${data.active_gemini_model || 'Gemini'} 🚀):</strong>
                <p style="color: #cbd5e1; font-size: 11px; margin: 2px 0 0 0;">Đang đóng vai Senior Research Scientist (40 năm kinh nghiệm), sẵn sàng tổng hợp tri thức 4 tầng, xuất bản Bộ 2 Tệp Chuẩn mực và kiểm toán 100% trích dẫn.</p>
              </div>
            </div>
            <div style="display: flex; gap: 8px;">
              <span class="badge badge-green" style="font-size: 12px; padding: 6px 12px;">✅ Đã Kết Nối AI</span>
              <button class="btn btn-secondary btn-sm" onclick="App.openSettingsModal()" title="Tùy chỉnh mô hình">⚙️ Cấu Hình</button>
            </div>
          `;
        } else {
          writerBanner.style.background = "";
          writerBanner.style.borderColor = "";
          writerBanner.innerHTML = `
            <div style="display: flex; align-items: center; gap: 12px;">
              <span style="font-size: 24px;">🤖</span>
              <div>
                <strong style="color: #fff; font-size: 13px;">Kích hoạt Google AI (Gemini 1.5 Pro / Flash):</strong>
                <p style="color: #94a3b8; font-size: 11px; margin: 2px 0 0 0;">Đăng nhập Google hoặc kết nối Google Gemini API Key để mở khóa khả năng phân tích đa tầng và sinh bài viết chuyên sâu.</p>
              </div>
            </div>
            <button class="btn btn-google btn-sm" onclick="AuthManager.openAuthModal()">
              🔑 Đăng Nhập / Kết Nối Google AI
            </button>
          `;
        }
      }

      // Update Editorial AI Banner dynamically
      const editorialBanner = document.getElementById("editorial-ai-banner");
      if (editorialBanner) {
        if (data.has_gemini_key) {
          editorialBanner.style.background = "linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(139, 92, 246, 0.1) 100%)";
          editorialBanner.style.borderColor = "rgba(96, 165, 250, 0.4)";
          editorialBanner.innerHTML = `
            <div style="display: flex; align-items: center; gap: 12px;">
              <span style="font-size: 24px;">📰</span>
              <div>
                <strong style="color: #60a5fa; font-size: 13px;">Trợ Lý Tòa Soạn Google AI Đã Sẵn Sàng (Mô hình: ${data.active_gemini_model || 'Gemini'} 🚀):</strong>
                <p style="color: #cbd5e1; font-size: 11px; margin: 2px 0 0 0;">Hội đồng 6 Ban Biên Tập đã sẵn sàng phân tích ma trận đề tài, lập Content Brief và xuất bản theo chu trình 4 Trạm GATE.</p>
              </div>
            </div>
            <div style="display: flex; gap: 8px;">
              <span class="badge badge-purple" style="font-size: 12px; padding: 6px 12px;">✅ Tòa Soạn Online</span>
              <button class="btn btn-secondary btn-sm" onclick="App.openSettingsModal()" title="Tùy chỉnh mô hình">⚙️ Cấu Hình</button>
            </div>
          `;
        } else {
          editorialBanner.style.background = "";
          editorialBanner.style.borderColor = "";
          editorialBanner.innerHTML = `
            <div style="display: flex; align-items: center; gap: 12px;">
              <span style="font-size: 24px;">📰</span>
              <div>
                <strong style="color: #fff; font-size: 13px;">Kích hoạt Trợ lý Tòa Soạn Google AI:</strong>
                <p style="color: #94a3b8; font-size: 11px; margin: 2px 0 0 0;">Kết nối tài khoản Google để các Ban biên tập phân tích ma trận và điều phối quy trình tự động.</p>
              </div>
            </div>
            <button class="btn btn-google btn-sm" onclick="AuthManager.openAuthModal()">
              🔑 Đăng Nhập / Kết Nối Google AI
            </button>
          `;
        }
      }

      if (window.HistoryUI && HistoryUI.loadHistory) {
        HistoryUI.loadHistory();
      }
    } catch (e) {
      console.warn("Status update error:", e);
    }
  },

  setupModals() {
    // Close modal triggers
    document.querySelectorAll(".modal-close-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        document.querySelectorAll(".modal-backdrop").forEach(m => m.classList.remove("active"));
      });
    });
  },

  openSettingsModal() {
    fetch("/api/config", {
      headers: (window.AuthManager && AuthManager.token) ? { "Authorization": `Bearer ${AuthManager.token}` } : {}
    }).then(r => r.json()).then(cfg => {
      const gIdEl = document.getElementById("cfg-google-id");
      if (gIdEl) gIdEl.value = cfg.google_client_id || "";
      const geminiKeyEl = document.getElementById("cfg-gemini-key");
      if (geminiKeyEl) geminiKeyEl.value = cfg.gemini_api_key || "";
      const openaiKeyEl = document.getElementById("cfg-openai-key");
      if (openaiKeyEl) openaiKeyEl.value = cfg.openai_api_key || "";
      const zoteroIdEl = document.getElementById("cfg-zotero-id");
      if (zoteroIdEl) zoteroIdEl.value = cfg.zotero_user_id || "";
      const zoteroKeyEl = document.getElementById("cfg-zotero-key");
      if (zoteroKeyEl) zoteroKeyEl.value = cfg.zotero_api_key || "";
      const abbyyKeyEl = document.getElementById("cfg-abbyy-key");
      if (abbyyKeyEl) abbyyKeyEl.value = cfg.abbyy_api_key || "";
      const abbyyEndpointEl = document.getElementById("cfg-abbyy-endpoint");
      if (abbyyEndpointEl) abbyyEndpointEl.value = cfg.abbyy_endpoint || "";
      const storageDirEl = document.getElementById("cfg-custom-storage-dir");
      if (storageDirEl) storageDirEl.value = cfg.custom_storage_dir || "";
      
      this.loadGeminiModelsInSettings();
      if (window.ThemeManager && ThemeManager.openSync) {
        ThemeManager.openSync();
      }
      if (window.SettingsUI && SettingsUI.switchTab) {
        SettingsUI.switchTab('ai');
      }
      document.getElementById("modal-settings")?.classList.add("active");
    }).catch(err => {
      console.warn("Failed to load settings:", err);
      if (window.SettingsUI && SettingsUI.switchTab) {
        SettingsUI.switchTab('ai');
      }
      document.getElementById("modal-settings")?.classList.add("active");
    });
  },

  openConfiguredStorageFolder() {
    const customDir = document.getElementById("cfg-custom-storage-dir")?.value.trim() || "";
    this.openWindowsExplorer(customDir || "Tai_Lieu");
  },

  resetStorageDirToDefault() {
    const input = document.getElementById("cfg-custom-storage-dir");
    if (input) input.value = "";
    this.toast("Đã đặt lại thư mục lưu mặc định: workspace/Tai_Lieu (Bấm 'Lưu Cài Đặt' để lưu).", "info");
  },

  async loadGeminiModelsInSettings() {
    const listEl = document.getElementById("cfg-gemini-models-list");
    if (!listEl) return;

    listEl.innerHTML = `<span style="font-size: 11px; color: #94a3b8;"><span class="spinner-sm"></span> Đang kết nối trực tiếp đến Google AI để tải danh sách mô hình thực tế...</span>`;

    const key = document.getElementById("cfg-gemini-key")?.value.trim() || "";
    try {
      const url = key ? `/api/gemini/models?api_key=${encodeURIComponent(key)}` : "/api/gemini/models";
      const res = await fetch(url, {
        headers: (window.AuthManager && AuthManager.token) ? { "Authorization": `Bearer ${AuthManager.token}` } : {}
      });
      const data = await res.json();
      if (data.success && data.models && data.models.length > 0) {
        const selectedModel = data.active_model || "auto";
        listEl.innerHTML = `
          <div style="margin-top: 8px; display: flex; flex-direction: column; gap: 6px;">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px; flex-wrap: wrap; gap: 6px;">
              <span style="font-size: 11.5px; color: #34d399; font-weight: 700;">
                🟢 Đã tải trực tiếp ${data.models.length} mô hình từ Google AI API (${data.source === 'cache' ? 'Đã lưu đệm' : 'Trực tiếp'}):
              </span>
              <select id="cfg-selected-model" class="form-control" style="width: auto; padding: 3px 8px; font-size: 11.5px; border-color: #3b82f6;">
                <option value="auto" ${selectedModel === 'auto' ? 'selected' : ''}>⭐ Tự động chọn mô hình tối ưu nhất (${data.models[0].clean_name})</option>
                ${data.models.map(m => `
                  <option value="${m.clean_name}" ${selectedModel === m.clean_name ? 'selected' : ''}>
                    ${m.displayName} (${(m.inputTokenLimit / 1000).toFixed(0)}k context)
                  </option>
                `).join('')}
              </select>
            </div>

            <div style="max-height: 160px; overflow-y: auto; display: flex; flex-direction: column; gap: 5px; padding-right: 2px;">
              ${data.models.map(m => `
                <div style="padding: 6px 10px; background: rgba(0,0,0,0.3); border-radius: 6px; font-size: 11px; border: 1px solid ${m.is_latest ? 'rgba(52, 211, 153, 0.4)' : 'rgba(255,255,255,0.06)'};">
                  <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: ${m.is_latest ? '#34d399' : '#93c5fd'}; font-weight: 700; font-family: monospace;">
                      ${m.is_latest ? '🚀 ' : '🔹 '}${m.clean_name}
                    </span>
                    <div style="display: flex; gap: 6px; align-items: center;">
                      <span style="color: #94a3b8; font-size: 10px;">Ngữ cảnh: ${(m.inputTokenLimit / 1000).toFixed(0)}k</span>
                      ${m.is_latest ? '<span class="badge badge-green" style="font-size: 9px; padding: 1px 5px;">Ưu tiên</span>' : ''}
                    </div>
                  </div>
                  <p style="font-size: 10.5px; color: #cbd5e1; margin: 3px 0 0 0; line-height: 1.3;">
                    ${m.description || m.displayName}
                  </p>
                </div>
              `).join('')}
            </div>
          </div>
        `;
      } else {
        listEl.innerHTML = `
          <div style="padding: 10px 14px; background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 8px; font-size: 12px; color: #fca5a5; margin-top: 6px;">
            ⚠️ <strong>Chưa tải được mô hình:</strong> ${data.error || 'Vui lòng nhập API Key hợp lệ và bấm nút "🔄 Quét Mô Hình".'}
            <div style="margin-top: 4px; font-size: 11px; color: #94a3b8;">
              🔑 Lấy Google Gemini API Key miễn phí tại: <a href="https://aistudio.google.com/app/apikey" target="_blank" style="color: #60a5fa; text-decoration: underline;">Google AI Studio</a>
            </div>
          </div>
        `;
      }
    } catch (e) {
      listEl.innerHTML = `<span style="font-size: 11px; color: #f87171;">Lỗi tải mô hình: ${e.message}</span>`;
    }
  },

  async refreshGeminiModels() {
    const key = document.getElementById("cfg-gemini-key")?.value.trim() || "";
    if (!key) {
      this.toast("Vui lòng nhập Gemini API Key vào ô phía trên trước khi quét mô hình.", "warning");
      return;
    }
    this.toast("Đang kết nối Google AI để truy vấn danh sách mô hình thực tế...", "info");
    try {
      const res = await fetch("/api/gemini/refresh-models", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...((window.AuthManager && AuthManager.token) ? { "Authorization": `Bearer ${AuthManager.token}` } : {})
        },
        body: JSON.stringify({ api_key: key })
      });
      const data = await res.json();
      if (data.success && data.models && data.models.length > 0) {
        this.toast(`✅ Đã quét thành công ${data.total} mô hình thực tế từ Google AI API!`, "success");
        this.loadGeminiModelsInSettings();
        this.updateStatus();
      } else {
        this.toast(data.error || "Không thể tải mô hình từ Google AI với API Key này.", "error");
        this.loadGeminiModelsInSettings();
      }
    } catch (e) {
      this.toast("Lỗi quét mô hình: " + e.message, "error");
    }
  },

  async saveSettings() {
    const payload = {
      gemini_api_key: document.getElementById("cfg-gemini-key")?.value.trim() || "",
      selected_gemini_model: document.getElementById("cfg-selected-model")?.value || "auto",
      openai_api_key: document.getElementById("cfg-openai-key")?.value.trim() || "",
      zotero_user_id: document.getElementById("cfg-zotero-id")?.value.trim() || "",
      zotero_api_key: document.getElementById("cfg-zotero-key")?.value.trim() || "",
      abbyy_api_key: document.getElementById("cfg-abbyy-key")?.value.trim() || "",
      abbyy_endpoint: document.getElementById("cfg-abbyy-endpoint")?.value.trim() || "",
      custom_storage_dir: document.getElementById("cfg-custom-storage-dir")?.value.trim() || ""
    };
    const gIdEl = document.getElementById("cfg-google-id");
    if (gIdEl && gIdEl.value.trim()) {
      payload.google_client_id = gIdEl.value.trim();
    }

    try {
      const res = await fetch("/api/config", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...((window.AuthManager && AuthManager.token) ? { "Authorization": `Bearer ${AuthManager.token}` } : {})
        },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (data.success) {
        this.toast("✅ Đã lưu cài đặt API và cấu hình thành công!", "success");
        document.getElementById("modal-settings").classList.remove("active");
        this.updateStatus();
        if (window.AuthManager) AuthManager.renderUserUI();
      } else {
        this.toast("Lỗi lưu cấu hình: " + (data.detail || data.message || "Không xác định"), "error");
      }
    } catch (e) {
      this.toast("Lỗi lưu cấu hình: " + e.message, "error");
    }
  },

  async openWindowsExplorer(relPath = "") {
    const clean = (typeof relPath === "string" ? relPath.trim() : "");
    const customInput = document.getElementById("pipeline-storage-dir")?.value.trim() || document.getElementById("cfg-custom-storage-dir")?.value.trim() || "";
    const targetPath = clean || customInput || "Tai_Lieu";
    try {
      const res = await fetch(`/api/files/open-folder?custom_dir=${encodeURIComponent(targetPath)}&path=${encodeURIComponent(targetPath)}`);
      const data = await res.json();
      const folderPath = data.folder || data.path || targetPath;
      this.toast(`📂 Đã gửi lệnh mở thư mục: ${folderPath}`, "success");
    } catch (e) {
      this.toast("Lỗi mở thư mục: " + e.message, "error");
    }
  },

  async openFileInSystem(relPath = "") {
    const clean = (typeof relPath === "string" ? relPath.trim() : "");
    if (!clean || clean === "undefined" || clean === "null") {
      this.toast("Chưa tìm thấy tệp hoặc tệp đang được khởi tạo, vui lòng kiểm tra lại sau giây lát.", "warning");
      return;
    }
    const fileName = clean.split("/").pop() || "Tai_Lieu.docx";
    this.toast(`📝 Đang mở tệp '${fileName}' trực tiếp bằng Microsoft Word...`, "info");
    
    try {
      const res = await fetch(`/api/files/open-system?path=${encodeURIComponent(clean)}`);
      const data = await res.json();
      if (data.success) {
        this.toast(`✅ Đã gửi lệnh mở '${fileName}' trên Microsoft Word!`, "success");
      } else {
        this.toast(data.message || "Không thể mở trực tiếp.", "warning");
      }

      // Also trigger browser download so user can open in Word with 1-click
      this.downloadFile(clean);
    } catch (e) {
      console.warn("System open error:", e);
      this.downloadFile(clean);
    }
  },

  downloadFile(relPath = "") {
    const clean = (typeof relPath === "string" ? relPath.trim() : "");
    if (!clean || clean === "undefined" || clean === "null") return;
    const url = `/api/files/download?path=${encodeURIComponent(clean)}`;
    const a = document.createElement("a");
    a.href = url;
    a.download = clean.split("/").pop() || "download";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  },

  toast(message, type = "info") {
    const container = document.getElementById("toast-container");
    if (!container) return;

    const el = document.createElement("div");
    el.className = `toast toast-${type}`;
    
    let icon = "ℹ️";
    if (type === "success") icon = "✅";
    if (type === "error") icon = "❌";
    if (type === "warning") icon = "⚠️";

    el.innerHTML = `<span>${icon}</span> <span>${message}</span>`;
    container.appendChild(el);

    setTimeout(() => {
      el.style.opacity = "0";
      el.style.transform = "translateX(50px)";
      el.style.transition = "all 0.3s ease";
      setTimeout(() => el.remove(), 300);
    }, 4000);
  }
};

window.App = App;
document.addEventListener("DOMContentLoaded", () => App.init());
