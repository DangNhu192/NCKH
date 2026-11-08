/**
 * WEB SUPER v2.0 — The Academic Agency Agents Controller
 * Pattern: msitarzewski/agency-agents
 * Manages the AI Specialists Roster, Agent Persona Cards, and Active Agent Badges across tabs.
 */

const AgencyRosterUI = {
  agents: [],
  activeModalAgent: null,

  async init() {
    await this.loadAgents();
    this.renderRoster();
    this.injectActiveAgentBadges();
  },

  async loadAgents() {
    try {
      const res = await fetch('/api/agency/agents');
      const data = await res.json();
      if (data.success && Array.isArray(data.agents)) {
        this.agents = data.agents;
      }
    } catch (e) {
      console.warn("Lỗi tải danh mục Agency Agents:", e);
    }
  },

  renderRoster() {
    const container = document.getElementById("agency-roster-grid");
    if (!container) return;

    if (!this.agents || this.agents.length === 0) {
      container.innerHTML = `<p style="color:#94a3b8; font-size:13px;">Đang tải danh sách Chuyên gia AI...</p>`;
      return;
    }

    container.innerHTML = this.agents.map(agent => {
      return `
        <div class="card agency-agent-card" onclick="AgencyRosterUI.openAgentModal('${agent.id}')" style="border-color: ${agent.color}40; background: rgba(255,255,255,0.03); transition: all 0.25s ease; cursor: pointer; position: relative; overflow: hidden;">
          <div style="position: absolute; top: 0; left: 0; width: 4px; height: 100%; background: ${agent.color};"></div>
          
          <div style="display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 12px;">
            <div style="display: flex; align-items: center; gap: 12px;">
              <span style="font-size: 32px; filter: drop-shadow(0 2px 8px ${agent.color}60);">${agent.emoji}</span>
              <div>
                <h4 style="color: #f8fafc; font-size: 16px; margin: 0; font-weight: 700;">${agent.name}</h4>
                <span class="badge ${agent.badge_class}" style="font-size: 10px; margin-top: 4px; display: inline-block;">${agent.division}</span>
              </div>
            </div>
            <button class="btn btn-secondary btn-sm" style="font-size: 11px; padding: 3px 8px;" onclick="event.stopPropagation(); AgencyRosterUI.openAgentModal('${agent.id}')">
              🔍 Chi Tiết
            </button>
          </div>

          <div style="font-size: 12px; color: ${agent.color}; font-weight: 600; margin-bottom: 8px;">
            ${agent.title}
          </div>

          <p style="font-size: 12px; color: #cbd5e1; font-style: italic; line-height: 1.5; margin-bottom: 12px; min-height: 36px;">
            "${agent.vibe}"
          </p>

          <div style="border-top: 1px solid rgba(255,255,255,0.06); padding-top: 10px; margin-top: auto;">
            <div style="font-size: 11px; color: #94a3b8; margin-bottom: 4px;"><strong>📦 Sản phẩm đầu ra:</strong></div>
            <ul style="font-size: 11px; color: #e2e8f0; padding-left: 16px; margin: 0; line-height: 1.6;">
              ${agent.deliverables.slice(0, 2).map(d => `<li>${d}</li>`).join('')}
            </ul>
          </div>
        </div>
      `;
    }).join('');
  },

  openAgentModal(agentId) {
    const agent = this.agents.find(a => a.id === agentId);
    if (!agent) return;
    this.activeModalAgent = agent;

    const modal = document.getElementById("modal-agent-detail");
    if (!modal) return;

    document.getElementById("modal-agent-emoji").innerText = agent.emoji;
    document.getElementById("modal-agent-name").innerText = agent.name;
    document.getElementById("modal-agent-title").innerText = agent.title;
    document.getElementById("modal-agent-division").innerText = agent.division;
    document.getElementById("modal-agent-division").className = `badge ${agent.badge_class}`;
    document.getElementById("modal-agent-vibe").innerText = `"${agent.vibe}"`;
    document.getElementById("modal-agent-identity").innerText = agent.identity;

    const missionList = document.getElementById("modal-agent-missions");
    if (missionList) {
      missionList.innerHTML = agent.mission.map(m => `<li>${m}</li>`).join('');
    }

    const rulesList = document.getElementById("modal-agent-rules");
    if (rulesList) {
      rulesList.innerHTML = agent.critical_rules.map(r => `<li style="color: #fca5a5;">⚠️ ${r}</li>`).join('');
    }

    const deliverableList = document.getElementById("modal-agent-deliverables");
    if (deliverableList) {
      deliverableList.innerHTML = agent.deliverables.map(d => `<li style="color: #a7f3d0;">✅ ${d}</li>`).join('');
    }

    modal.classList.add("active");
  },

  closeAgentModal() {
    const modal = document.getElementById("modal-agent-detail");
    if (modal) modal.classList.remove("active");
  },

  injectActiveAgentBadges() {
    const tabBadges = {
      "harvester-tab": { emoji: "🌐", name: "Prof. Lexicon Drake", role: "Literature Intelligence & Harvester Chair", color: "#0ea5e9" },
      "scibot-tab": { emoji: "🧠", name: "Prof. Synapse Vance & Prof. Methodius Sterling", role: "Knowledge Architecture & Methodology Chairs", color: "#8b5cf6" },
      "writer-tab": { emoji: "✍️", name: "Prof. Scholaris Thorne & Prof. Veritas Proctor", role: "Academic Monograph & 6-Column Integrity Chairs", color: "#10b981" },
      "editorial-tab": { emoji: "🏢", name: "Prof. Victor Aurelius & Prof. Adversarius Grimm", role: "Editorial Board & Adversarial Reviewer 2 Chairs", color: "#ec4899" },
      "humanizer-tab": { emoji: "✨", name: "Prof. Stylus Artisan", role: "Human Authenticity & Anti-AI Rhythm Chair", color: "#eab308" },
      "math-chem-tab": { emoji: "🔬", name: "Prof. Quantus Maxwell", role: "Quantitative Analytics & Computational Precision Chair", color: "#3b82f6" },
      "admin-tab": { emoji: "🛡️", name: "Prof. Sentinel Needle", role: "System Governance & Reproducibility Chair", color: "#14b8a6" },
      "pipeline-tab": { emoji: "⚡", name: "Hội Đồng 10 Giáo Sư Nghiêm Khắc", role: "Autonomous Council of 10 Academic Chairs", color: "#8b5cf6" }
    };

    Object.entries(tabBadges).forEach(([tabId, info]) => {
      const tabPane = document.getElementById(tabId);
      if (tabPane) {
        const header = tabPane.querySelector(".card-header") || tabPane.querySelector("h2")?.parentElement;
        if (header && !header.querySelector(".agency-active-agent-badge")) {
          const badge = document.createElement("div");
          badge.className = "agency-active-agent-badge";
          badge.style.cssText = `display: inline-flex; align-items: center; gap: 8px; padding: 6px 12px; background: rgba(255,255,255,0.04); border: 1px solid ${info.color}40; border-radius: 20px; font-size: 11px; margin-bottom: 12px;`;
          badge.innerHTML = `
            <span style="font-size: 14px;">${info.emoji}</span>
            <span style="color: #94a3b8;">Đặc vụ vận hành:</span>
            <strong style="color: ${info.color}; cursor: pointer;" onclick="App.switchTab('agency-tab')">${info.name}</strong>
            <span style="color: #64748b; font-size: 10px;">(${info.role})</span>
          `;
          tabPane.insertBefore(badge, tabPane.firstChild);
        }
      }
    });
  }
};

document.addEventListener("DOMContentLoaded", () => AgencyRosterUI.init());
if (document.readyState === "complete" || document.readyState === "interactive") {
  AgencyRosterUI.init();
}

// Global Window Export
window.AgencyRosterUI = AgencyRosterUI;
window.AgencyUI = AgencyRosterUI;
