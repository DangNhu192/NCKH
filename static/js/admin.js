/**
 * Admin Panel & License Key Manager UI for WEB SUPER v2.0
 */
const AdminUI = {
  users: [],
  keys: [],
  currentSubtab: 'users',

  init() {
    if (window.AuthManager && AuthManager.isLoggedIn && (
      AuthManager.currentUser?.role === "admin" ||
      AuthManager.currentUser?.role === "reseller" ||
      AuthManager.currentUser?.email === "admin@websuper.edu.vn"
    )) {
      this.loadAllData();
    }
  },

  getAuthHeader() {
    const token = (window.AuthManager && AuthManager.token) ? AuthManager.token : (localStorage.getItem("web_super_jwt") || "");
    return token ? { "Authorization": `Bearer ${token}` } : {};
  },

  switchSubtab(subtabId) {
    this.currentSubtab = subtabId;
    document.querySelectorAll(".admin-subtab-pane").forEach(p => p.style.display = "none");
    document.querySelectorAll(".humanizer-subtabs-nav .subtab-btn").forEach(b => b.classList.remove("active"));

    const targetPane = document.getElementById(`admin-subtab-pane-${subtabId}`);
    const targetBtn = document.getElementById(`admin-subtab-btn-${subtabId}`);

    if (targetPane) targetPane.style.display = "block";
    if (targetBtn) targetBtn.classList.add("active");

    if (subtabId === 'users') this.loadUsers();
    if (subtabId === 'keys') this.loadKeys();
    if (subtabId === 'needle' && window.NeedleAdminUI) NeedleAdminUI.runAudit();
  },

  loadAllData() {
    if (!window.AuthManager || !AuthManager.isLoggedIn) return;
    this.loadUsers();
    this.loadKeys();
    if (window.NeedleAdminUI) NeedleAdminUI.runAudit(false);
  },

  async loadUsers() {
    const tableBody = document.getElementById("admin-users-table-body");
    if (!tableBody) return;

    try {
      const res = await fetch("/api/admin/users", {
        headers: this.getAuthHeader()
      });
      const data = await res.json();
      if (!data.success) {
        tableBody.innerHTML = `<tr><td colspan="7" style="text-align: center; padding: 30px; color: #f87171;">${data.detail || 'Không có quyền truy cập.'}</td></tr>`;
        return;
      }

      this.users = data.users || [];
      this.renderUserStats(this.users);
      this.renderUsersTable(this.users);
    } catch (e) {
      tableBody.innerHTML = `<tr><td colspan="7" style="text-align: center; padding: 30px; color: #f87171;">Lỗi tải dữ liệu: ${e.message}</td></tr>`;
    }
  },

  renderUserStats(users) {
    const total = users.length;
    const admins = users.filter(u => u.role === 'admin').length;
    const resellers = users.filter(u => u.role === 'reseller').length;
    const proUsers = users.filter(u => (u.plan === 'pro' || u.plan === 'enterprise') && !u.is_plan_expired).length;

    const elTotal = document.getElementById("admin-stat-total");
    const elAdmins = document.getElementById("admin-stat-admins");
    const elGemini = document.getElementById("admin-stat-gemini");
    const elPro = document.getElementById("admin-stat-pro-users");

    if (elTotal) elTotal.innerText = total;
    if (elAdmins) elAdmins.innerText = `${admins} Admin / ${resellers} CTV`;
    if (elGemini) elGemini.innerText = `${users.filter(u => u.has_gemini_key).length} User`;
    if (elPro) elPro.innerText = `${proUsers} Tài Khoản`;
  },

  renderUsersTable(users) {
    const tableBody = document.getElementById("admin-users-table-body");
    if (!tableBody) return;

    if (users.length === 0) {
      tableBody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 30px; color: #94a3b8;">Chưa có tài khoản nào trong hệ thống.</td></tr>';
      return;
    }

    tableBody.innerHTML = users.map(u => {
      const isMe = AuthManager.currentUser && AuthManager.currentUser.email.toLowerCase() === u.email.toLowerCase();
      const roleBadge = u.role === 'admin' 
        ? '<span class="badge badge-orange" style="font-size: 10px;">👑 Admin</span>' 
        : u.role === 'reseller'
          ? '<span class="badge badge-purple" style="font-size: 10px;">🤝 Đại Lý / CTV</span>'
          : '<span class="badge badge-blue" style="font-size: 10px;">🎓 Researcher</span>';
      
      const statusBadge = u.status === 'blocked'
        ? '<span class="badge" style="background: rgba(239,68,68,0.2); color: #f87171; font-size: 10px;">🔴 Bị khóa</span>'
        : '<span class="badge badge-green" style="font-size: 10px;">🟢 Hoạt động</span>';

      const isExpired = u.is_plan_expired;
      const planColor = u.plan === 'enterprise' ? '#f87171' : u.plan === 'pro' ? '#38bdf8' : '#94a3b8';
      const planBadge = `
        <div>
          <span class="badge" style="background: rgba(255,255,255,0.08); color: ${planColor}; font-size: 10.5px; font-weight: 700;">
            ${u.plan_name || u.plan?.toUpperCase() || 'PRO'}
          </span>
          <div style="font-size: 10.5px; margin-top: 3px; color: ${isExpired ? '#f87171' : '#94a3b8'};">
            ${isExpired ? '⚠️ Hết hạn: ' : '⏳ Hạn: '}${u.plan_expires_at ? u.plan_expires_at.split(' ')[0] : 'Vô hạn'}
          </div>
        </div>
      `;

      return `
        <tr style="border-bottom: 1px solid rgba(255,255,255,0.06);">
          <td style="padding: 12px 14px;">
            <div style="display: flex; align-items: center; gap: 10px;">
              <img src="${u.picture || 'https://api.dicebear.com/7.x/bottts/svg?seed=' + encodeURIComponent(u.name)}" style="width: 32px; height: 32px; border-radius: 50%; border: 1px solid var(--border-color);" alt="avatar">
              <div>
                <strong style="color: #fff; font-size: 13px;">${u.name}</strong>
                ${isMe ? '<span style="font-size: 10px; color: #34d399; margin-left: 6px;">(Bạn)</span>' : ''}
              </div>
            </div>
          </td>
          <td style="padding: 12px 14px;">
            <div style="font-size: 12px; color: #e2e8f0;">${u.email}</div>
            <div style="font-size: 10.5px; color: #94a3b8;">Provider: ${u.provider || 'google'}</div>
          </td>
          <td style="padding: 12px 14px; text-align: center;">
            ${roleBadge}
          </td>
          <td style="padding: 12px 14px; text-align: center;">
            ${planBadge}
          </td>
          <td style="padding: 12px 14px; text-align: center;">
            <div style="display: flex; gap: 4px; justify-content: center;">
              <span class="badge ${u.has_gemini_key ? 'badge-green' : 'badge-orange'}" style="font-size: 9.5px;" title="Khóa Google Gemini">
                ${u.has_gemini_key ? '✓ Gemini' : '✕ Gemini'}
              </span>
              <span class="badge ${u.has_zotero_key ? 'badge-blue' : 'badge-orange'}" style="font-size: 9.5px;" title="Khóa Zotero">
                ${u.has_zotero_key ? '✓ Zotero' : '✕ Zotero'}
              </span>
            </div>
          </td>
          <td style="padding: 12px 14px; text-align: center;">
            ${statusBadge}
          </td>
          <td style="padding: 12px 14px; text-align: right;">
            <div style="display: flex; gap: 4px; justify-content: flex-end; flex-wrap: wrap;">
              <button class="btn btn-secondary btn-sm" onclick="AdminUI.promptChangeRole('${u.email}', '${u.role}')" style="font-size: 10.5px; padding: 2px 6px;" title="Phân quyền Admin / CTV / User">
                👑 Quyền
              </button>
              <button class="btn btn-secondary btn-sm" onclick="AdminUI.promptChangePlan('${u.email}', '${u.plan}')" style="font-size: 10.5px; padding: 2px 6px;" title="Đổi gói & Gia hạn">
                📦 Gói
              </button>
              <button class="btn btn-secondary btn-sm" onclick="AdminUI.extendUserDays('${u.email}', 30)" style="font-size: 10.5px; padding: 2px 6px;" title="+30 Ngày">
                +30d
              </button>
              ${!isMe ? `
                <button class="btn btn-secondary btn-sm" onclick="AdminUI.toggleUserStatus('${u.email}', '${u.status}')" style="font-size: 10.5px; padding: 2px 6px; color: ${u.status === 'blocked' ? '#34d399' : '#f87171'};" title="Khóa/Mở">
                  ${u.status === 'blocked' ? 'Mở' : 'Khóa'}
                </button>
                <button class="btn btn-danger btn-sm" onclick="AdminUI.deleteUser('${u.email}')" style="font-size: 10.5px; padding: 2px 6px;" title="Xóa tài khoản">
                  🗑️
                </button>
              ` : ''}
            </div>
          </td>
        </tr>
      `;
    }).join('');
  },

  async loadKeys() {
    const tableBody = document.getElementById("admin-keys-table-body");
    if (!tableBody) return;

    try {
      const res = await fetch("/api/admin/license-keys", {
        headers: this.getAuthHeader()
      });
      const data = await res.json();
      if (!data.success) {
        tableBody.innerHTML = `<tr><td colspan="8" style="text-align: center; padding: 30px; color: #f87171;">${data.detail || 'Không thể tải License Keys.'}</td></tr>`;
        return;
      }

      this.keys = data.keys || [];
      this.renderKeysTable(this.keys);
    } catch (e) {
      tableBody.innerHTML = `<tr><td colspan="8" style="text-align: center; padding: 30px; color: #f87171;">Lỗi tải License Keys: ${e.message}</td></tr>`;
    }
  },

  renderKeysTable(keys) {
    const tableBody = document.getElementById("admin-keys-table-body");
    if (!tableBody) return;

    if (keys.length === 0) {
      tableBody.innerHTML = '<tr><td colspan="8" style="text-align: center; padding: 30px; color: #94a3b8;">Chưa có mã License Key nào được tạo. Hãy tạo mã mới ở khung phía trên!</td></tr>';
      return;
    }

    tableBody.innerHTML = keys.map(k => {
      const statusBadge = k.status === 'revoked'
        ? '<span class="badge" style="background: rgba(239,68,68,0.2); color: #f87171; font-size: 10px;">Đã thu hồi</span>'
        : k.activations_count >= k.max_activations 
          ? '<span class="badge badge-orange" style="font-size: 10px;">Đã dùng hết</span>' 
          : '<span class="badge badge-green" style="font-size: 10px;">🟢 Khả dụng</span>';

      return `
        <tr style="border-bottom: 1px solid rgba(255,255,255,0.06);">
          <td style="padding: 12px 14px;">
            <div style="display: flex; align-items: center; gap: 8px;">
              <code style="font-size: 13px; font-weight: 700; color: #38bdf8; background: rgba(56, 189, 248, 0.1); padding: 3px 8px; border-radius: 4px; border: 1px solid rgba(56, 189, 248, 0.3);">${k.key}</code>
              <button class="btn btn-secondary btn-sm" onclick="AdminUI.copyText('${k.key}')" style="font-size: 10px; padding: 2px 6px;" title="Sao chép key">📋</button>
            </div>
          </td>
          <td style="padding: 12px 14px; text-align: center;">
            <span class="badge badge-blue" style="font-size: 10.5px;">${k.plan.toUpperCase()}</span>
          </td>
          <td style="padding: 12px 14px; text-align: center; font-size: 12px; color: #fff;">
            ${k.duration_days} ngày
          </td>
          <td style="padding: 12px 14px; text-align: center; font-size: 12px;">
            <strong>${k.activations_count}</strong> / ${k.max_activations}
          </td>
          <td style="padding: 12px 14px; font-size: 11.5px; color: #cbd5e1;">
            ${(k.activated_by && k.activated_by.length > 0) ? k.activated_by.join(', ') : '<span style="color: #64748b; font-style: italic;">Chưa ai kích hoạt</span>'}
          </td>
          <td style="padding: 12px 14px; font-size: 11.5px; color: #94a3b8;">
            <div>${k.note || '---'}</div>
            <div style="font-size: 10px; color: #64748b; margin-top: 2px;">Tạo bởi: ${k.created_by || 'Admin'}</div>
          </td>
          <td style="padding: 12px 14px; text-align: center;">
            ${statusBadge}
          </td>
          <td style="padding: 12px 14px; text-align: right;">
            <div style="display: flex; gap: 4px; justify-content: flex-end;">
              ${k.status !== 'revoked' ? `
                <button class="btn btn-secondary btn-sm" onclick="AdminUI.revokeKey('${k.key}')" style="font-size: 10.5px; padding: 2px 6px; color: #f87171;" title="Thu hồi key">
                  Thu Hồi
                </button>
              ` : ''}
              <button class="btn btn-danger btn-sm" onclick="AdminUI.deleteKeyPermanent('${k.key}')" style="font-size: 10.5px; padding: 2px 6px;" title="Xóa vĩnh viễn">
                🗑️
              </button>
            </div>
          </td>
        </tr>
      `;
    }).join('');
  },

  async createNewLicenseKey() {
    const plan = document.getElementById("admin-new-key-plan")?.value || "pro";
    const duration_days = parseInt(document.getElementById("admin-new-key-days")?.value || 90);
    const max_activations = parseInt(document.getElementById("admin-new-key-activations")?.value || 1);
    const note = document.getElementById("admin-new-key-note")?.value.trim() || "";

    try {
      const headers = { "Content-Type": "application/json", ...this.getAuthHeader() };
      const res = await fetch("/api/admin/license-keys/create", {
        method: "POST",
        headers: headers,
        body: JSON.stringify({ plan, duration_days, max_activations, note })
      });
      const data = await res.json();
      if (data.success) {
        App.toast(`Đã tạo mã License Key mới: ${data.key_record.key}`, "success");
        if (document.getElementById("admin-new-key-note")) document.getElementById("admin-new-key-note").value = "";
        this.loadKeys();
      } else {
        App.toast(data.detail || "Lỗi tạo License Key", "error");
      }
    } catch (e) {
      App.toast("Lỗi tạo License Key: " + e.message, "error");
    }
  },

  async revokeKey(key) {
    if (!confirm(`Bạn có chắc chắn muốn THU HỒI mã ${key}? Mã này sẽ không thể dùng để kích hoạt được nữa.`)) return;

    try {
      const headers = { "Content-Type": "application/json", ...this.getAuthHeader() };
      const res = await fetch("/api/admin/license-keys/revoke", {
        method: "POST",
        headers: headers,
        body: JSON.stringify({ key, delete: false })
      });
      const data = await res.json();
      if (data.success) {
        App.toast("Đã thu hồi mã bản quyền thành công!", "success");
        this.loadKeys();
      }
    } catch (e) {
      App.toast("Lỗi thu hồi key: " + e.message, "error");
    }
  },

  async deleteKeyPermanent(key) {
    if (!confirm(`XÓA VĨNH VIỄN mã ${key} khỏi hệ thống?`)) return;

    try {
      const headers = { "Content-Type": "application/json", ...this.getAuthHeader() };
      const res = await fetch("/api/admin/license-keys/revoke", {
        method: "POST",
        headers: headers,
        body: JSON.stringify({ key, delete: true })
      });
      const data = await res.json();
      if (data.success) {
        App.toast("Đã xóa mã bản quyền!", "success");
        this.loadKeys();
      }
    } catch (e) {
      App.toast("Lỗi xóa key: " + e.message, "error");
    }
  },

  promptChangeRole(email, currentRole) {
    const choice = prompt(`Chọn vai trò mới cho ${email}:\n1. admin (Toàn quyền quản trị)\n2. reseller (Cộng tác viên bán key)\n3. researcher (User)`, currentRole);
    if (!choice) return;

    const roleMap = { '1': 'admin', '2': 'reseller', '3': 'researcher', 'admin': 'admin', 'reseller': 'reseller', 'researcher': 'researcher' };
    const newRole = roleMap[choice.toLowerCase().trim()];
    if (!newRole) {
      alert("Vai trò không hợp lệ. Vui lòng nhập admin, reseller hoặc researcher.");
      return;
    }

    const headers = { "Content-Type": "application/json", ...this.getAuthHeader() };
    fetch("/api/admin/users/update", {
      method: "POST",
      headers: headers,
      body: JSON.stringify({ email, role: newRole })
    }).then(r => r.json()).then(d => {
      if (d.success) {
        App.toast(`Đã đổi vai trò của ${email} sang ${newRole.toUpperCase()}!`, "success");
        AdminUI.loadUsers();
      }
    });
  },

  promptChangePlan(email, currentPlan) {
    const plans = ['free', 'standard', 'pro', 'enterprise'];
    const chosen = prompt(`Chọn gói dịch vụ mới cho ${email} (free / standard / pro / enterprise):`, currentPlan || 'pro');
    if (!chosen || !plans.includes(chosen.toLowerCase())) return;

    const headers = { "Content-Type": "application/json", ...this.getAuthHeader() };
    fetch("/api/admin/users/update", {
      method: "POST",
      headers: headers,
      body: JSON.stringify({ email, plan: chosen.toLowerCase() })
    }).then(r => r.json()).then(d => {
      if (d.success) {
        App.toast(`Đã cập nhật gói ${chosen.toUpperCase()} cho ${email}!`, "success");
        AdminUI.loadUsers();
      }
    });
  },

  extendUserDays(email, days = 30) {
    const addDays = prompt(`Nhập số ngày gia hạn thêm cho tài khoản ${email}:`, days);
    if (!addDays || isNaN(parseInt(addDays))) return;

    const headers = { "Content-Type": "application/json", ...this.getAuthHeader() };
    fetch("/api/admin/users/update", {
      method: "POST",
      headers: headers,
      body: JSON.stringify({ email, extend_days: parseInt(addDays) })
    }).then(r => r.json()).then(d => {
      if (d.success) {
        App.toast(`Đã gia hạn thêm +${addDays} ngày cho ${email}!`, "success");
        AdminUI.loadUsers();
      }
    });
  },

  async toggleUserStatus(email, currentStatus) {
    const newStatus = currentStatus === 'blocked' ? 'active' : 'blocked';
    const actionName = newStatus === 'blocked' ? 'KHÓA' : 'MỞ KHÓA';
    if (!confirm(`Bạn có chắc chắn muốn ${actionName} tài khoản ${email}?`)) return;

    const headers = { "Content-Type": "application/json", ...this.getAuthHeader() };
    fetch("/api/admin/users/update", {
      method: "POST",
      headers: headers,
      body: JSON.stringify({ email, status: newStatus })
    }).then(r => r.json()).then(d => {
      if (d.success) {
        App.toast(d.message, "success");
        AdminUI.loadUsers();
      }
    });
  },

  async deleteUser(email) {
    if (!confirm(`CẢNH BÁO: Xóa vĩnh viễn tài khoản ${email} và toàn bộ tệp tin cài đặt của họ?`)) return;

    const headers = { "Content-Type": "application/json", ...this.getAuthHeader() };
    fetch("/api/admin/users/delete", {
      method: "POST",
      headers: headers,
      body: JSON.stringify({ email })
    }).then(r => r.json()).then(d => {
      if (d.success) {
        App.toast(d.message, "success");
        AdminUI.loadUsers();
      }
    });
  },

  copyText(text) {
    navigator.clipboard.writeText(text).then(() => {
      App.toast(`📋 Đã sao chép License Key: ${text}`, "success");
    });
  }
};

// Global Window Export
window.AdminUI = AdminUI;
