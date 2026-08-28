/**
 * Google Authentication & AI Key Session Manager for WEB SUPER v2.0
 */

// Helper to decode JWT payload safely in browser with full UTF-8 & base64 padding support
function parseJwtPayload(token) {
  try {
    if (!token || typeof token !== 'string') return null;
    const parts = token.split('.');
    if (parts.length !== 3) return null;
    let base64Url = parts[1];
    let base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    while (base64.length % 4 !== 0) {
      base64 += '=';
    }
    const binaryStr = atob(base64);
    const bytes = new Uint8Array(binaryStr.length);
    for (let i = 0; i < binaryStr.length; i++) {
      bytes[i] = binaryStr.charCodeAt(i);
    }
    const jsonStr = new TextDecoder('utf-8').decode(bytes);
    const payload = JSON.parse(jsonStr);
    const email = (payload.email || payload.sub || "").toLowerCase().trim();
    
    // Strict Admin check: ONLY admin@websuper.edu.vn is admin
    if (email === "admin@websuper.edu.vn") {
      payload.role = "admin";
      payload.plan = "enterprise";
      payload.is_admin = true;
    } else {
      payload.is_admin = false;
      if (payload.role === "admin") {
        payload.role = "researcher";
      }
    }
    return payload;
  } catch (e) {
    try {
      const parts = token.split('.');
      let base64 = parts[1].replace(/-/g, '+').replace(/_/g, '/');
      while (base64.length % 4) base64 += '=';
      const payload = JSON.parse(decodeURIComponent(escape(atob(base64))));
      const email = (payload.email || payload.sub || "").toLowerCase().trim();
      if (email === "admin@websuper.edu.vn") {
        payload.role = "admin";
        payload.plan = "enterprise";
        payload.is_admin = true;
      } else {
        payload.is_admin = false;
        if (payload.role === "admin") {
          payload.role = "researcher";
        }
      }
      return payload;
    } catch (e2) {
      return null;
    }
  }
}

// ── Global Authenticated Fetch Interceptor ─────────────────────────────────
// Tự động gắn header 'Authorization: Bearer <token>' cho toàn bộ các lời gọi /api/*
(function() {
  const originalFetch = window.fetch;
  window.fetch = async function(url, options = {}) {
    const opts = options ? { ...options } : {};
    opts.headers = opts.headers ? { ...opts.headers } : {};

    // Nếu url là endpoint nội bộ /api/* (không phải URL ngoài như googleapis)
    const isApiUrl = (typeof url === 'string' && (url.startsWith('/api/') || url.startsWith('api/')));
    if (isApiUrl) {
      const hasAuth = Object.keys(opts.headers).some(k => k.toLowerCase() === 'authorization');
      if (!hasAuth) {
        const token = (window.AuthManager && AuthManager.token) || localStorage.getItem("web_super_jwt");
        if (token) {
          opts.headers['Authorization'] = `Bearer ${token}`;
        }
      }
    }

    return originalFetch.call(this, url, opts);
  };
})();

const AuthManager = {
  token: localStorage.getItem("web_super_jwt") || null,
  currentUser: parseJwtPayload(localStorage.getItem("web_super_jwt") || ""),

  get isLoggedIn() {
    return Boolean(this.token);
  },

  getAuthHeaders() {
    return this.token ? { "Authorization": `Bearer ${this.token}` } : {};
  },

  init() {
    // Synchronously decode token if available
    if (this.token && !this.currentUser) {
      this.currentUser = parseJwtPayload(this.token);
    }
    this.renderUserUI();
    this.checkSession();
  },

  async checkSession() {
    if (!this.token) {
      this.renderUserUI();
      return;
    }
    try {
      const res = await fetch("/api/auth/me", {
        headers: { "Authorization": `Bearer ${this.token}` }
      });
      if (res.ok) {
        const data = await res.json();
        if (data.success && data.user) {
          this.currentUser = data.user;
          this.renderUserUI();
          this.updatePlanBadgeInSettings(data.user);
          if (data.user.role === 'admin' && window.NeedleAdminUI) {
            NeedleAdminUI.init();
          }
        }
      } else if (res.status === 401) {
        this.token = null;
        this.currentUser = null;
        localStorage.removeItem("web_super_jwt");
        this.renderUserUI();
      }
    } catch (e) {
      console.warn("Session check fallback:", e);
      this.renderUserUI();
    }
  },

  updatePlanBadgeInSettings(user) {
    const badge = document.getElementById("user-current-plan-badge");
    const expText = document.getElementById("user-plan-expiry-text");
    if (badge && user) {
      const planName = user.plan_name || user.plan?.toUpperCase() || "PRO";
      badge.innerText = `Gói: ${planName}`;
      badge.className = user.plan === 'enterprise' ? 'badge badge-orange' : 'badge badge-blue';
    }
    if (expText && user) {
      expText.innerText = user.plan_expires_at ? `Hạn dùng: ${user.plan_expires_at.split(' ')[0]}` : 'Vô hạn';
    }
  },

  async activateUserKey(keyFromParam = null) {
    const input = document.getElementById("cfg-license-key-input");
    const key = (keyFromParam || (input ? input.value : "")).trim().toUpperCase();
    if (!key) {
      App.toast("Vui lòng nhập mã License Key để kích hoạt.", "warning");
      return;
    }
    if (!this.token) {
      App.toast("Vui lòng đăng nhập Google trước khi kích hoạt key.", "warning");
      this.openAuthModal();
      return;
    }

    try {
      App.toast("Đang xác thực và kích hoạt mã License Key...", "info");
      const res = await fetch("/api/auth/activate-key", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${this.token}`
        },
        body: JSON.stringify({ key })
      });
      const data = await res.json();
      if (data.success) {
        App.toast(data.message, "success");
        if (input) input.value = "";
        this.checkSession();
      } else {
        App.toast(data.detail || data.message || "Kích hoạt thất bại", "error");
      }
    } catch (e) {
      App.toast("Lỗi kích hoạt: " + e.message, "error");
    }
  },

  openAuthModal() {
    const modal = document.getElementById("modal-google-auth");
    if (modal) {
      modal.classList.add("active");
      this.initGoogleAuthUI();
    }
  },

  closeAuthModal() {
    const modal = document.getElementById("modal-google-auth");
    if (modal) {
      modal.classList.remove("active");
    }
  },

  initGoogleAuthUI() {
    const gBtnContainer = document.getElementById("google-signin-btn-box");
    if (!gBtnContainer) return;

    fetch("/api/status").then(r => r.json()).then(st => {
      const clientId = (st.google_client_id || "").trim();

      if (!clientId) {
        gBtnContainer.innerHTML = `
          <div style="text-align: center; padding: 16px; color: #94a3b8; font-size: 13px; line-height: 1.6;">
            ⚠️ Chưa có Google Client ID.<br>
            Vui lòng vào <button class="btn btn-secondary btn-sm" onclick="AuthManager.closeAuthModal(); App.openSettingsModal();" style="margin: 6px 4px 0;">⚙️ Cài Đặt</button> để nhập Client ID.
          </div>
        `;
        return;
      }

      const renderGIS = () => {
        if (window.google && google.accounts && google.accounts.id) {
          try {
            google.accounts.id.initialize({
              client_id: clientId,
              callback: (resp) => this.handleGoogleCallback(resp),
              auto_select: false
            });
            gBtnContainer.innerHTML = '<div id="g-button-render-slot" style="display: flex; justify-content: center;"></div>';
            google.accounts.id.renderButton(
              document.getElementById("g-button-render-slot"),
              { theme: "filled_blue", size: "large", width: 300, text: "signin_with", shape: "pill" }
            );
            google.accounts.id.prompt();
          } catch (e) {
            console.error("GIS initialization error:", e);
          }
        } else {
          gBtnContainer.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: center; gap: 8px; padding: 12px; color: #93c5fd; font-size: 13px;">
              <span class="spinner-sm"></span> Đang kết nối Google Identity Services...
            </div>
          `;
          setTimeout(renderGIS, 400);
        }
      };
      renderGIS();
    }).catch(err => {
      console.warn("Failed to check status:", err);
      gBtnContainer.innerHTML = `
        <div style="color: #ef4444; font-size: 13px; padding: 10px;">Không thể kết nối máy chủ để lấy Google Client ID.</div>
      `;
    });
  },

  async handleGoogleCallback(response) {
    if (!response || !response.credential) {
      App.toast("Đăng nhập Google không thành công.", "error");
      return;
    }
    try {
      App.toast("Đang xác thực chữ ký số tài khoản Google...", "info");
      const res = await fetch("/api/auth/google", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id_token: response.credential })
      });
      const data = await res.json();
      if (data.success) {
        this.token = data.token;
        this.currentUser = data.user;
        localStorage.setItem("web_super_jwt", data.token);
        this.renderUserUI();
        this.closeAuthModal();
        App.toast(`Đăng nhập Google thành công! Chào ${data.user.name}`, "success");
        App.updateStatus();
        if (window.OnboardingGuide) OnboardingGuide.checkReadyOnLogin();
        if (data.user.role === 'admin' && window.NeedleAdminUI) {
          NeedleAdminUI.onAdminLoginNotification();
        }

        setTimeout(() => this.checkApiSetupRequirement(), 800);
      } else {
        App.toast(data.detail || "Xác thực thất bại", "error");
      }
    } catch (e) {
      App.toast("Lỗi kết nối máy chủ xác thực: " + e.message, "error");
    }
  },

  async checkApiSetupRequirement() {
    if (!this.token) return;
    try {
      const res = await fetch("/api/config", {
        headers: { "Authorization": `Bearer ${this.token}` }
      });
      const cfg = await res.json();
      const hasGemini = Boolean(cfg.gemini_api_key && cfg.gemini_api_key !== "PENDING_SETUP");
      const hasZotero = Boolean(cfg.zotero_api_key);

      if (!hasGemini || !hasZotero) {
        App.toast("⚠️ Vui lòng cấu hình Gemini API Key và Zotero API Key để bắt đầu sử dụng đầy đủ tính năng!", "warning");
        if (window.App && App.openSettingsModal) {
          App.openSettingsModal();
        }
      }
    } catch (e) {
      console.warn("Failed to check api setup requirement:", e);
    }
  },

  logout() {
    this.token = null;
    this.currentUser = null;
    localStorage.removeItem("web_super_jwt");
    this.renderUserUI();
    App.toast("Đã đăng xuất tài khoản.", "info");
    App.updateStatus();
    if (window.App && App.switchTab) {
      App.switchTab('home-tab');
    }
  },

  renderUserUI() {
    const container = document.getElementById("auth-container");
    const isAuthed = Boolean(this.currentUser && this.token);

    // 1. Clear sidebar lock visual state
    document.querySelectorAll(".nav-item[data-tab]").forEach(item => {
      item.classList.remove("locked-feature");
    });

    // 1.1 Show Admin navigation item ONLY for Admin and CTV/Reseller
    const adminNav = document.getElementById("nav-item-admin");
    if (adminNav) {
      const email = (this.currentUser?.email || "").toLowerCase().trim();
      const role = (this.currentUser?.role || "").toLowerCase().trim();
      const isSuperAdmin = (email === "admin@websuper.edu.vn");
      const isReseller = (role === "reseller");
      const isAllowedAdmin = isAuthed && (isSuperAdmin || isReseller);
      if (isAllowedAdmin) {
        adminNav.style.display = "flex";
        const badgeEl = adminNav.querySelector(".badge");
        if (badgeEl) {
          const isReseller = role === "reseller";
          badgeEl.innerText = isReseller ? "CTV" : "ADMIN";
          badgeEl.className = isReseller ? "badge badge-blue" : "badge badge-orange";
        }
      } else {
        adminNav.style.display = "none";
      }
    }

    // 2. Update Home Hero CTA Button
    const homeCtaBox = document.getElementById("home-auth-cta-box");
    if (homeCtaBox) {
      if (isAuthed) {
        homeCtaBox.innerHTML = `
          <button class="btn btn-success btn-lg" onclick="App.switchTab('pipeline-tab')" style="box-shadow: 0 0 20px rgba(16, 185, 129, 0.4); font-size: 15px; padding: 12px 28px;">
            ⚡ Bắt Đầu Nghiên Cứu Ngay (Đã Đăng Nhập)
          </button>
        `;
      } else {
        homeCtaBox.innerHTML = `
          <button class="btn btn-primary btn-lg" onclick="AuthManager.openAuthModal()" style="box-shadow: 0 0 24px rgba(59, 130, 246, 0.5); font-size: 15px; padding: 12px 28px;">
            🚀 Đăng Nhập Google Để Mở Khóa Đầy Đủ
          </button>
        `;
      }
    }

    if (!container) return;

    if (this.currentUser) {
      const isAdmin = this.currentUser.role === "admin" || this.currentUser.email === "admin@websuper.edu.vn" || this.currentUser.email === "superadmin@local";
      container.innerHTML = `
        <div class="user-profile-badge">
          <img src="${this.currentUser.picture || 'https://api.dicebear.com/7.x/bottts/svg?seed=' + encodeURIComponent(this.currentUser.name)}" class="user-avatar" alt="Avatar">
          <div class="user-meta">
            <span class="user-name">${this.currentUser.name || 'User'}</span>
            <span class="user-email">${this.currentUser.email || 'local@user'} ${isAdmin ? '👑 Admin' : '🎓 User'}</span>
          </div>
          <button class="btn btn-secondary btn-sm" onclick="AuthManager.logout()" title="Đăng xuất" style="padding: 4px 8px; margin-left: 4px; font-size: 11px;">
            🚪 Đăng xuất
          </button>
        </div>
      `;
    } else {
      container.innerHTML = `
        <div style="display: flex; align-items: center; gap: 8px;">
          <button class="btn-google" onclick="AuthManager.openAuthModal()" title="Đăng nhập tài khoản Google để kích hoạt AI">
            <svg width="18" height="18" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/>
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/>
            </svg>
            <span>Đăng Nhập Google</span>
          </button>
        </div>
      `;
    }
  }
};

window.AuthManager = AuthManager;
window.handleGoogleSignIn = (resp) => AuthManager.handleGoogleCallback(resp);