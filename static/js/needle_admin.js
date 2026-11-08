/**
 * WEB SUPER v2.0 — Needle AI Admin Assistant & Sentinel UI
 * Inspired by cactus-compute/needle (14MB embedded foundation model).
 * Automatically audits system health on Admin login and executes administrative tool calls.
 */

const NeedleAdminUI = (() => {
  let _lastAuditData = null;
  let _chatHistory = [];

  function init() {
    // Check if current user is admin and run background health check
    if (window.AuthManager && AuthManager.currentUser && (AuthManager.currentUser.role === 'admin' || AuthManager.currentUser.email === 'admin@websuper.edu.vn')) {
      runAudit(false);
    }
  }

  async function runAudit(showToast = true) {
    try {
      const headers = (window.AuthManager && AuthManager.token)
        ? { 'Authorization': `Bearer ${AuthManager.token}` } : {};

      const r = await fetch('/api/admin/needle/health-audit', { headers });
      if (!r.ok) {
        if (showToast) App.toast('Không thể tải dữ liệu chẩn đoán Needle AI.', 'error');
        return;
      }

      const data = await r.json();
      _lastAuditData = data;
      renderAuditUI(data);

      if (showToast) {
        App.toast(`🤖 Needle AI: Chẩn đoán hoàn tất! Điểm sức khỏe: ${data.health_score}/100 (${data.status_text})`, 'success');
      }
    } catch (e) {
      console.error('[Needle AI] Audit error:', e);
    }
  }

  function renderAuditUI(data) {
    // 1. Health Score Badge & Ring
    const scoreEl = document.getElementById('needle-health-score');
    if (scoreEl) scoreEl.textContent = `${data.health_score}/100`;

    const statusEl = document.getElementById('needle-health-status');
    if (statusEl) statusEl.textContent = data.status_text;

    // 2. Summary
    const sumEl = document.getElementById('needle-executive-summary');
    if (sumEl) sumEl.textContent = data.executive_summary;

    // 3. Metrics
    const m = data.metrics || {};
    const u = m.users || {};
    const s = m.storage || {};
    const k = m.keys || {};

    const elUsers = document.getElementById('needle-metric-users');
    if (elUsers) elUsers.textContent = `${u.active || 0} đang hoạt động / ${u.total || 0} tài khoản`;

    const elKeys = document.getElementById('needle-metric-keys');
    if (elKeys) elKeys.textContent = `${k.available || 0} key khả dụng / ${k.used || 0} đã dùng`;

    const elStorage = document.getElementById('needle-metric-storage');
    if (elStorage) elStorage.textContent = `${s.total_size_mb || 0} MB (${s.total_files || 0} tệp)`;

    const elApis = document.getElementById('needle-metric-apis');
    if (elApis) elApis.textContent = `Gemini: ${m.gemini_status} | OpenAI: ${m.openai_status}`;

    // 4. Warnings & Issues
    const warnContainer = document.getElementById('needle-warnings-container');
    if (warnContainer) {
      const allAlerts = [...(data.issues || []).map(i => `<li style="color: #ef4444;">❌ <strong>Lỗi:</strong> ${i}</li>`),
                         ...(data.warnings || []).map(w => `<li style="color: #f59e0b;">⚠️ <strong>Cảnh báo:</strong> ${w}</li>`)];
      if (allAlerts.length > 0) {
        warnContainer.innerHTML = `<ul style="margin: 0; padding-left: 20px; font-size: 12.5px; line-height: 1.7;">${allAlerts.join('')}</ul>`;
      } else {
        warnContainer.innerHTML = `<div style="color: #10b981; font-size: 13px; font-weight: 600;">✅ Không phát hiện lỗi hoặc cảnh báo nghiêm trọng. Toàn bộ 8 chức năng sẵn sàng 100%!</div>`;
      }
    }
  }

  async function sendAdminCommand(customPrompt) {
    const inputEl = document.getElementById('needle-chat-input');
    const prompt = (customPrompt || (inputEl ? inputEl.value : '')).trim();
    if (!prompt) return;

    if (inputEl) inputEl.value = '';

    const btn = document.getElementById('btn-needle-send-command');
    const originalText = btn ? btn.innerHTML : '';
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = `<span class="spinner" style="display:inline-block; width:12px; height:12px; border:2px solid #fff; border-top-color:transparent; border-radius:50%; animation:spin 0.8s linear infinite; margin-right:6px; vertical-align:middle;"></span>Đang gửi...`;
    }

    // Append User Message to Terminal
    appendChatMessage('admin', prompt);

    try {
      const headers = (window.AuthManager && AuthManager.token)
        ? { 'Authorization': `Bearer ${AuthManager.token}`, 'Content-Type': 'application/json' } : { 'Content-Type': 'application/json' };

      const r = await fetch('/api/admin/needle/chat', {
        method: 'POST',
        headers,
        body: JSON.stringify({ command: prompt })
      });

      if (!r.ok) {
        appendChatMessage('needle', '❌ Lỗi thực thi lệnh. Vui lòng kiểm tra quyền Quản trị viên.');
        return;
      }

      const res = await r.json();
      appendChatMessage('needle', res.response_message, res.action_executed);

      // Refresh admin data if keys or users created
      if (['create_keys', 'clean_logs', 'system_audit'].includes(res.action_executed)) {
        if (window.AdminUI) AdminUI.loadAllData();
        runAudit(false);
      }
    } catch (e) {
      appendChatMessage('needle', `❌ Ngoại lệ: ${e.message}`);
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = originalText;
      }
    }
  }

  function appendChatMessage(sender, text, action = null) {
    const container = document.getElementById('needle-chat-messages');
    if (!container) return;

    const isNeedle = sender === 'needle';
    const msgDiv = document.createElement('div');
    msgDiv.style.cssText = `margin-bottom: 12px; display: flex; gap: 10px; align-items: flex-start; animation: fadeIn 0.2s ease;`;

    const avatar = isNeedle ? '🤖' : '👑';
    const bg = isNeedle ? 'rgba(30, 58, 138, 0.25)' : 'rgba(255, 255, 255, 0.08)';
    const border = isNeedle ? 'rgba(59, 130, 246, 0.4)' : 'rgba(255, 255, 255, 0.15)';
    const name = isNeedle ? 'Needle AI Sentinel (14MB Engine)' : 'Admin (admin@websuper.edu.vn)';

    msgDiv.innerHTML = `
      <div style="font-size: 22px; line-height: 1;">${avatar}</div>
      <div style="flex: 1; background: ${bg}; border: 1px solid ${border}; border-radius: 10px; padding: 10px 14px;">
        <div style="font-size: 11px; font-weight: 700; color: ${isNeedle ? '#93c5fd' : '#fde68a'}; margin-bottom: 4px;">
          ${name}
        </div>
        <div style="font-size: 13px; color: #f8fafc; line-height: 1.6; white-space: pre-wrap;">${escapeHtml(text)}</div>
      </div>
    `;

    container.appendChild(msgDiv);
    container.scrollTop = container.scrollHeight;
  }

  function escapeHtml(text) {
    return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }

  function onAdminLoginNotification() {
    runAudit(false).then(() => {
      if (_lastAuditData) {
        App.toast(`🤖 Needle AI Sentinel: Chào mừng Admin! Hệ thống đạt ${_lastAuditData.health_score}/100 điểm sức khỏe.`, 'info');
      }
    });
  }

  return {
    init,
    runAudit,
    sendAdminCommand,
    onAdminLoginNotification
  };
})();

// Auto-run on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  NeedleAdminUI.init();
});

// Global Window Export
window.NeedleAdminUI = NeedleAdminUI;
