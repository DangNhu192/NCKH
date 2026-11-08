/**
 * WEB SUPER v2.0 — SettingsUI & ThemeManager (Smart Contrast & Tabbed System)
 * Tự động phân tích độ sáng ảnh nền (Luminance Analysis), tính toán tỷ lệ tương phản
 * và đổi màu chữ (Đen / Trắng) tự động để đảm bảo người dùng đọc văn bản rõ nét 100%.
 */

const ThemeManager = (() => {
  const STORAGE_KEY  = 'ws_theme_mode';
  const STORAGE_BG   = 'ws_theme_custom_bg';
  const STORAGE_OVL  = 'ws_theme_overlay';
  const STORAGE_LUM  = 'ws_theme_bg_is_light';
  const STORAGE_HC   = 'ws_theme_high_contrast';
  const ALL_THEME_CLASSES = [
    'theme-dark', 'theme-light', 'theme-oxford-dark', 'theme-cambridge-light',
    'theme-nature-emerald', 'theme-ieee-computational', 'theme-system',
    'theme-custom-bg', 'bg-is-light'
  ];

  function _analyzeImageBrightness(dataUrl, callback) {
    const img = new Image();
    img.crossOrigin = 'Anonymous';
    img.onload = () => {
      try {
        const canvas = document.createElement('canvas');
        canvas.width = 40;
        canvas.height = 40;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0, 40, 40);
        const imgData = ctx.getImageData(0, 0, 40, 40).data;
        let colorSum = 0;
        const count = imgData.length / 4;
        for (let x = 0; x < imgData.length; x += 4) {
          // Standard Perceived Luminance formula (ITU-R BT.709)
          const r = imgData[x];
          const g = imgData[x + 1];
          const b = imgData[x + 2];
          const avg = 0.2126 * r + 0.7152 * g + 0.0722 * b;
          colorSum += avg;
        }
        const brightness = Math.floor(colorSum / count);
        // If brightness > 130, image is considered light
        callback(brightness > 130);
      } catch (err) {
        callback(false);
      }
    };
    img.onerror = () => callback(false);
    img.src = dataUrl;
  }

  function _syncHeaderQuickButton(mode) {
    const quickBtn = document.getElementById('header-theme-quick-btn');
    const quickItems = document.querySelectorAll('.theme-quick-item');
    const shortNames = {
      'oxford-dark': '🏛️ Oxford Dark',
      'cambridge-light': '📜 Cambridge Light',
      'nature-emerald': '🌿 Nature Emerald',
      'ieee-computational': '⚡ IEEE Tech',
      'dark': '🌙 Cổ Điển Tối',
      'light': '☀️ Cổ Điển Sáng',
      'system': '💻 Hệ Thống',
      'custom': '🖼️ Ảnh Nền'
    };
    if (quickBtn) {
      const labelSpan = quickBtn.querySelector('.theme-quick-label');
      if (labelSpan) {
        labelSpan.textContent = shortNames[mode] || '🎨 Theme';
      }
    }
    quickItems.forEach(item => {
      item.classList.toggle('active', item.dataset.theme === mode);
    });
  }

  function _applyTheme(mode, bgDataUrl, overlayOpacity, isBgLight) {
    const body = document.body;
    if (!body) return;

    body.classList.remove(...ALL_THEME_CLASSES);

    const isSystemLight = (mode === 'system' && window.matchMedia('(prefers-color-scheme: light)').matches);
    const isLightMode = (mode === 'light' || mode === 'cambridge-light') || (mode === 'system' && isSystemLight);
    const isCustomLight = (mode === 'custom' && isBgLight && (overlayOpacity < 55));
    const isEffectiveLight = isLightMode || isCustomLight;

    document.documentElement.setAttribute('data-theme', mode);
    document.documentElement.setAttribute('data-contrast', isEffectiveLight ? 'light' : 'dark');

    const isHighContrast = localStorage.getItem(STORAGE_HC) === 'true';
    body.classList.toggle('high-contrast-mode', isHighContrast);

    if (mode === 'oxford-dark') {
      body.classList.add('theme-oxford-dark');
      body.style.backgroundImage = 'none';
      body.style.removeProperty('--custom-bg-overlay');
    } else if (mode === 'cambridge-light') {
      body.classList.add('theme-cambridge-light');
      body.style.backgroundImage = 'none';
      body.style.removeProperty('--custom-bg-overlay');
    } else if (mode === 'nature-emerald') {
      body.classList.add('theme-nature-emerald');
      body.style.backgroundImage = 'none';
      body.style.removeProperty('--custom-bg-overlay');
    } else if (mode === 'ieee-computational') {
      body.classList.add('theme-ieee-computational');
      body.style.backgroundImage = 'none';
      body.style.removeProperty('--custom-bg-overlay');
    } else if (mode === 'light') {
      body.classList.add('theme-light');
      body.style.backgroundImage = 'none';
      body.style.removeProperty('--custom-bg-overlay');
    } else if (mode === 'system') {
      body.classList.add('theme-system');
      if (isSystemLight) {
        body.classList.add('theme-cambridge-light');
      } else {
        body.classList.add('theme-oxford-dark');
      }
      body.style.backgroundImage = 'none';
      body.style.removeProperty('--custom-bg-overlay');
    } else if (mode === 'custom') {
      if (bgDataUrl) {
        body.classList.add('theme-custom-bg');
        body.style.backgroundImage = `url("${bgDataUrl}")`;
        
        const pct = overlayOpacity !== undefined ? overlayOpacity : 70;
        const alpha = (pct / 100).toFixed(2);

        if (isBgLight && pct < 55) {
          body.classList.add('bg-is-light');
          body.style.setProperty('--custom-bg-overlay', `rgba(255, 255, 255, ${alpha})`);
        } else {
          body.style.setProperty('--custom-bg-overlay', `rgba(11, 15, 23, ${alpha})`);
        }
      } else {
        body.classList.add('theme-oxford-dark');
        body.style.backgroundImage = 'none';
        body.style.removeProperty('--custom-bg-overlay');
      }
    } else {
      // Default: dark
      body.classList.add('theme-dark');
      body.style.backgroundImage = 'none';
      body.style.removeProperty('--custom-bg-overlay');
    }

    _syncHeaderQuickButton(mode);
  }

  function _syncRadios(mode) {
    document.querySelectorAll('.theme-option-btn, .theme-preview-card').forEach(el => {
      const isTarget = el.dataset.theme === mode;
      el.classList.toggle('active', isTarget);
      const radio = el.querySelector('input[type="radio"]');
      if (radio) radio.checked = isTarget;
    });
    const customOpts = document.getElementById('theme-custom-options');
    if (customOpts) customOpts.style.display = (mode === 'custom') ? 'block' : 'none';

    const hcCheckbox = document.getElementById('cfg-high-contrast-toggle');
    if (hcCheckbox) {
      hcCheckbox.checked = localStorage.getItem(STORAGE_HC) === 'true';
    }

    _syncHeaderQuickButton(mode);
  }

  function _syncBgPreview(bgDataUrl) {
    const preview = document.getElementById('theme-bg-preview');
    const noneLabel = document.getElementById('theme-bg-none');
    if (!preview) return;
    if (bgDataUrl) {
      preview.style.backgroundImage = `url("${bgDataUrl}")`;
      if (noneLabel) noneLabel.style.display = 'none';
    } else {
      preview.style.backgroundImage = 'none';
      if (noneLabel) noneLabel.style.display = 'flex';
    }
  }

  function _syncOverlaySlider(opacity) {
    const slider = document.getElementById('theme-overlay-opacity');
    const valEl  = document.getElementById('theme-overlay-val');
    if (slider) slider.value = opacity;
    if (valEl)  valEl.textContent = opacity + '%';
  }

  function load() {
    const mode        = localStorage.getItem(STORAGE_KEY) || 'dark';
    const bgData      = localStorage.getItem(STORAGE_BG)  || '';
    const overlay     = parseInt(localStorage.getItem(STORAGE_OVL) || '70', 10);
    const isBgLight   = localStorage.getItem(STORAGE_LUM) === 'true';
    _applyTheme(mode, bgData, overlay, isBgLight);
  }

  function openSync() {
    const mode    = localStorage.getItem(STORAGE_KEY) || 'dark';
    const bgData  = localStorage.getItem(STORAGE_BG)  || '';
    const overlay = parseInt(localStorage.getItem(STORAGE_OVL) || '70', 10);
    _syncRadios(mode);
    _syncBgPreview(bgData);
    _syncOverlaySlider(overlay);
  }

  function setMode(mode) {
    const bgData    = localStorage.getItem(STORAGE_BG)  || '';
    const overlay   = parseInt(localStorage.getItem(STORAGE_OVL) || '70', 10);
    const isBgLight = localStorage.getItem(STORAGE_LUM) === 'true';
    localStorage.setItem(STORAGE_KEY, mode);
    _applyTheme(mode, bgData, overlay, isBgLight);
    _syncRadios(mode);

    if (window.App && App.toast) {
      const modeNames = {
        'oxford-dark': 'Oxford Academic Dark 🏛️ (Hoàng Gia & Vàng Đồng)',
        'cambridge-light': 'Cambridge Academic Light 📜 (Nền Giấy Ngà Sắc Nét)',
        'nature-emerald': 'Nature Scientific Emerald 🌿 (Ngọc Lục Bảo Khoa Học)',
        'ieee-computational': 'IEEE Computational Modern ⚡ (Than Chì & Cyber Indigo)',
        'dark': 'Cổ Điển Tối 🌙 (Chữ sáng sắc nét)',
        'light': 'Cổ Điển Sáng ☀️ (Tương phản cao)',
        'system': 'Theo Hệ Thống 💻',
        'custom': 'Tùy Chỉnh Hình Nền 🖼️'
      };
      App.toast(`Đã đổi chế độ giao diện: ${modeNames[mode] || mode}`, 'success');
    }
  }

  function toggleHighContrast(enabled) {
    localStorage.setItem(STORAGE_HC, enabled ? 'true' : 'false');
    const mode        = localStorage.getItem(STORAGE_KEY) || 'dark';
    const bgData      = localStorage.getItem(STORAGE_BG)  || '';
    const overlay     = parseInt(localStorage.getItem(STORAGE_OVL) || '70', 10);
    const isBgLight   = localStorage.getItem(STORAGE_LUM) === 'true';
    _applyTheme(mode, bgData, overlay, isBgLight);

    if (window.App && App.toast) {
      App.toast(enabled ? '⚡ Đã bật Chế Độ Siêu Tương Phản (WCAG AAA) - Chữ rõ nét tuyệt đối!' : 'Đã tắt Chế Độ Siêu Tương Phản.', 'info');
    }
  }

  function pickCustomBg() {
    const input = document.getElementById('theme-bg-file-input');
    if (input) input.click();
  }

  function onBgFileChange(event) {
    const file = event.target.files && event.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (e) => {
      const dataUrl = e.target.result;
      if (dataUrl.length > 5 * 1024 * 1024) {
        if (window.App) App.toast('Ảnh quá lớn (>4 MB). Vui lòng chọn ảnh nhỏ hơn.', 'warning');
        return;
      }
      
      // Auto analyze brightness and calculate contrast
      _analyzeImageBrightness(dataUrl, (isLight) => {
        localStorage.setItem(STORAGE_BG, dataUrl);
        localStorage.setItem(STORAGE_LUM, isLight ? 'true' : 'false');
        _syncBgPreview(dataUrl);
        setMode('custom');
        if (window.App) {
          App.toast(`Đã cập nhật ảnh nền! Hệ thống tự động phân tích độ tương phản (${isLight ? 'Ảnh nền Sáng ➔ Đổi sang chữ Đen Đậm' : 'Ảnh nền Tối ➔ Đổi sang chữ Trắng Sáng'}).`, 'success');
        }
      });
    };
    reader.readAsDataURL(file);
  }

  function clearCustomBg() {
    localStorage.removeItem(STORAGE_BG);
    localStorage.removeItem(STORAGE_LUM);
    _syncBgPreview('');
    const mode = localStorage.getItem(STORAGE_KEY) || 'dark';
    if (mode === 'custom') setMode('dark');
    if (window.App) App.toast('Đã xóa hình nền tùy chỉnh.', 'info');
  }

  function updateOverlay(val) {
    const pct = parseInt(val, 10);
    localStorage.setItem(STORAGE_OVL, pct);
    const mode        = localStorage.getItem(STORAGE_KEY) || 'dark';
    const bgData      = localStorage.getItem(STORAGE_BG)  || '';
    const isBgLight   = localStorage.getItem(STORAGE_LUM) === 'true';
    
    _applyTheme(mode, bgData, pct, isBgLight);
    
    const valEl = document.getElementById('theme-overlay-val');
    if (valEl) valEl.textContent = pct + '%';
  }

  function toggleQuickMenu(forceState) {
    const menu = document.getElementById('header-theme-quick-menu');
    if (!menu) return;
    if (typeof forceState === 'boolean') {
      menu.classList.toggle('active', forceState);
    } else {
      menu.classList.toggle('active');
    }
  }

  function init() {
    load();
    document.querySelectorAll('.theme-option-btn, .theme-preview-card, .theme-quick-item').forEach(btn => {
      btn.addEventListener('click', function(e) {
        const mode = this.dataset.theme;
        if (mode) {
          setMode(mode);
          const menu = document.getElementById('header-theme-quick-menu');
          if (menu) menu.classList.remove('active');
        }
      });
    });

    document.addEventListener('click', (e) => {
      const dropdown = document.querySelector('.theme-quick-switch');
      if (dropdown && !dropdown.contains(e.target)) {
        const menu = document.getElementById('header-theme-quick-menu');
        if (menu) menu.classList.remove('active');
      }
    });

    const mq = window.matchMedia('(prefers-color-scheme: light)');
    mq.addEventListener('change', () => {
      if ((localStorage.getItem(STORAGE_KEY) || 'oxford-dark') === 'system') load();
    });
  }

  return { init, load, openSync, setMode, toggleHighContrast, pickCustomBg, onBgFileChange, clearCustomBg, updateOverlay, toggleQuickMenu };
})();

/**
 * SettingsUI Module - Quản lý thanh chuyển thẻ trong Settings Modal
 */
const SettingsUI = (() => {
  function switchTab(tabId) {
    if (!tabId) tabId = 'ai';
    const allBtns = document.querySelectorAll('.settings-subtab-btn');
    const allPanes = document.querySelectorAll('.settings-subtab-pane');

    allBtns.forEach(btn => {
      const isTarget = btn.getAttribute('data-subtab') === tabId;
      btn.classList.toggle('active', isTarget);
    });

    allPanes.forEach(pane => {
      const isTarget = pane.id === `settings-subtab-${tabId}`;
      pane.classList.toggle('active', isTarget);
      pane.style.display = isTarget ? 'block' : 'none';
    });
  }

  function resetAllGuides() {
    if (window.OnboardingGuide && OnboardingGuide.resetAllGuides) {
      OnboardingGuide.resetAllGuides();
    } else {
      localStorage.clear();
      if (window.App) App.toast('Đã xóa toàn bộ trạng thái hướng dẫn sử dụng!', 'success');
    }
  }

  function clearSystemCache() {
    if (window.OnboardingGuide) OnboardingGuide.clearReadyCache();
    sessionStorage.clear();
    if (window.App) App.toast('Đã dọn dẹp bộ nhớ đệm (Cache) tạm thời của phiên làm việc!', 'success');
  }

  return { switchTab, resetAllGuides, clearSystemCache };
})();

// Apply theme instantly on DOM load
ThemeManager.load();
document.addEventListener('DOMContentLoaded', () => ThemeManager.init());

// Global Window Exports
window.ThemeManager = ThemeManager;
window.SettingsUI = SettingsUI;
