/**
 * math-chem-pro.js
 * ================
 * Frontend Controller cho Phân hệ Biên Tập Toán - Hóa, Sơ Đồ Quy Trình & Biểu Đồ 300 DPI (Math-Chem-Chart Pro).
 */

const MathChemProUI = (() => {
  let _activeSubtab = 'equation';
  let _selectedDomain = 'all';
  let _searchKeyword = '';
  let _sourceMode = 'workspace'; // 'workspace' | 'upload'
  let _selectedEnhanceMode = 'both'; // 'math_chem_only', 'images_only', 'both'
  let _lastOmmlXml = '';

  let _chartCategories = ['Mẫu Đất A', 'Mẫu Đất B', 'Mẫu Đất C', 'Mẫu Đất D'];
  let _chartValues = [12.4, 25.8, 18.2, 31.5];
  let _flowchartSteps = [
    { title: 'Thu Thập Mẫu', desc: 'Lấy mẫu đất & nước thực địa' },
    { title: 'Phân Tích Lý Hóa', desc: 'Đo pH, Fe2+, SO4 2-, DO' },
    { title: 'Mô Hình Hóa', desc: 'Tính toán WQI & Đương lượng CO2eq' },
    { title: 'Đánh Giá & Báo Cáo', desc: 'Xuất bản theo chuẩn APA 7th' }
  ];

  const PRESET_EQUATIONS = [
    // 1. Môi trường & Đất Nước
    {
      name: "Oxy hóa phèn tiềm tàng Pyrite (Acid Sulfate)",
      latex: "2FeS_2 + 7O_2 + 2H_2O \\longrightarrow 2Fe^{2+} + 4SO_4^{2-} + 4H^+",
      num: "1.1",
      domain: "Môi Trường & Đất Nước"
    },
    {
      name: "Động học phân hủy BOD5 nước thải",
      latex: "L_t = L_0 \\cdot (1 - 10^{-k \\cdot t})",
      num: "1.2",
      domain: "Môi Trường & Đất Nước"
    },
    {
      name: "Đẳng nhiệt hấp phụ Langmuir",
      latex: "q_e = \\frac{q_{max} \\cdot K_L \\cdot C_e}{1 + K_L \\cdot C_e}",
      num: "1.3",
      domain: "Môi Trường & Đất Nước"
    },
    {
      name: "Chuỗi phản ứng Nitrat hóa nước mặt",
      latex: "2NH_4^+ + 3O_2 \\xrightarrow{Nitrosomonas} 2NO_2^- + 4H^+ + 2H_2O",
      num: "1.4",
      domain: "Môi Trường & Đất Nước"
    },
    {
      name: "Chỉ số chất lượng nước tổng hợp (WQI)",
      latex: "WQI = \\frac{WQI_{pH}}{100} \\times \\left( \\frac{1}{k} \\sum_{i=1}^k WQI_i \\right)",
      num: "1.5",
      domain: "Môi Trường & Đất Nước"
    },

    // 2. Hóa Sinh & Năng Lượng
    {
      name: "Động học Enzym Michaelis-Menten",
      latex: "v = \\frac{V_{max} \\cdot [S]}{K_m + [S]}",
      num: "2.1",
      domain: "Hóa Sinh & Năng Lượng"
    },
    {
      name: "Phương trình Arrhenius (Năng lượng hoạt hóa)",
      latex: "k = A \\cdot e^{-\\frac{E_a}{R \\cdot T}}",
      num: "2.2",
      domain: "Hóa Sinh & Năng Lượng"
    },
    {
      name: "Phương trình Nernst (Thế điện cực)",
      latex: "E = E^0 - \\frac{R \\cdot T}{n \\cdot F} \\cdot \\ln Q",
      num: "2.3",
      domain: "Hóa Sinh & Năng Lượng"
    },
    {
      name: "Năng lượng tự do Gibbs & Cân bằng",
      latex: "\\Delta G^0 = \\Delta H^0 - T \\cdot \\Delta S^0 = -R \\cdot T \\cdot \\ln K",
      num: "2.4",
      domain: "Hóa Sinh & Năng Lượng"
    },

    // 3. Kinh Tế Lượng & Định Lượng
    {
      name: "Hàm sản xuất Cobb-Douglas",
      latex: "Y = A \\cdot K^\\alpha \\cdot L^\\beta \\quad (\\alpha + \\beta = 1)",
      num: "3.1",
      domain: "Kinh Tế Lượng & Định Lượng"
    },
    {
      name: "Mô hình hồi quy OLS đa biến",
      latex: "Y_i = \\beta_0 + \\beta_1 X_{1i} + \\beta_2 X_{2i} + \\dots + \\beta_k X_{ki} + \\varepsilon_i",
      num: "3.2",
      domain: "Kinh Tế Lượng & Định Lượng"
    },
    {
      name: "Độ co giãn của cầu theo giá",
      latex: "E_p = \\frac{\\partial Q}{\\partial P} \\cdot \\frac{P}{Q}",
      num: "3.3",
      domain: "Kinh Tế Lượng & Định Lượng"
    },

    // 4. Thống Kê & Xác Suất
    {
      name: "Hàm mật độ phân phối chuẩn Gaussian",
      latex: "f(x) = \\frac{1}{\\sigma \\sqrt{2\\pi}} \\cdot e^{-\\frac{(x - \\mu)^2}{2\\sigma^2}}",
      num: "4.1",
      domain: "Thống Kê & Xác Suất"
    },
    {
      name: "Hệ số tương quan Pearson (r)",
      latex: "r = \\frac{\\sum (X_i - \\bar{X})(Y_i - \\bar{Y})}{\\sqrt{\\sum (X_i - \\bar{X})^2 \\sum (Y_i - \\bar{Y})^2}}",
      num: "4.2",
      domain: "Thống Kê & Xác Suất"
    },

    // 5. Khoa Học Dữ Liệu & AI
    {
      name: "Hàm kích hoạt Softmax đa lớp",
      latex: "\\sigma(z)_i = \\frac{e^{z_i}}{\\sum_{j=1}^K e^{z_j}}",
      num: "5.1",
      domain: "Khoa Học Dữ Liệu & AI"
    },
    {
      name: "Hàm mất mát Cross-Entropy Loss",
      latex: "\\mathcal{L} = -\\frac{1}{N} \\sum_{i=1}^N \\sum_{c=1}^C y_{i,c} \\cdot \\log(\\hat{y}_{i,c})",
      num: "5.2",
      domain: "Khoa Học Dữ Liệu & AI"
    },
    {
      name: "Độ tương đồng Cosine Vector Similarity",
      latex: "\\text{Cosine}(\\mathbf{u}, \\mathbf{v}) = \\frac{\\mathbf{u} \\cdot \\mathbf{v}}{\\|\\mathbf{u}\\|_2 \\cdot \\|\\mathbf{v}\\|_2}",
      num: "5.3",
      domain: "Khoa Học Dữ Liệu & AI"
    }
  ];

  function init() {
    renderPresets();
    renderChartRows();
    renderFlowchartRows();
    convertEquation();
    loadWorkspaceFiles();
  }

  function switchSubtab(subtabId) {
    _activeSubtab = subtabId;
    document.querySelectorAll('.mathchem-subtab-btn').forEach(btn => {
      btn.classList.toggle('active', btn.getAttribute('data-subtab') === subtabId);
    });
    document.querySelectorAll('.mathchem-subtab-pane').forEach(pane => {
      pane.style.display = (pane.id === `mathchem-pane-${subtabId}`) ? 'block' : 'none';
    });
    if (subtabId === 'enhance') {
      loadWorkspaceFiles();
    }
  }

  function selectDomain(domain) {
    _selectedDomain = domain;
    document.querySelectorAll('#mathchem-domain-pills .mathchem-domain-pill').forEach(pill => {
      const isMatch = (domain === 'all' && pill.innerText.includes('Tất cả')) ||
                      (domain !== 'all' && pill.innerText.includes(domain.split('&')[0].trim()));
      pill.classList.toggle('active', isMatch);
    });
    renderPresets();
  }

  function filterPresets(keyword) {
    _searchKeyword = (keyword || '').toLowerCase().trim();
    renderPresets();
  }

  function renderPresets() {
    const container = document.getElementById('mathchem-presets-list');
    if (!container) return;

    let filtered = PRESET_EQUATIONS.filter(eq => {
      const matchDomain = (_selectedDomain === 'all') || (eq.domain === _selectedDomain);
      const matchKey = !_searchKeyword ||
                       eq.name.toLowerCase().includes(_searchKeyword) ||
                       eq.latex.toLowerCase().includes(_searchKeyword) ||
                       eq.domain.toLowerCase().includes(_searchKeyword) ||
                       eq.num.includes(_searchKeyword);
      return matchDomain && matchKey;
    });

    if (filtered.length === 0) {
      container.innerHTML = '<div style="padding:12px; text-align:center; color:#94a3b8; font-size:12px;">Không có công thức nào phù hợp.</div>';
      return;
    }

    container.innerHTML = filtered.map((eq) => {
      const origIndex = PRESET_EQUATIONS.indexOf(eq);
      return `
        <button type="button" class="mathchem-preset-btn" onclick="MathChemProUI.loadPreset(${origIndex})">
          <div style="display:flex; align-items:center; gap:6px; overflow:hidden;">
            <span style="font-weight:700; color:#60a5fa; white-space:nowrap;">(${eq.num})</span>
            <span style="overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">${eq.name}</span>
          </div>
          <span style="font-size:10px; color:#94a3b8; background:rgba(255,255,255,0.06); padding:2px 6px; border-radius:4px; white-space:nowrap;">${eq.domain.split('&')[0].trim()}</span>
        </button>
      `;
    }).join('');
  }

  function loadPreset(index) {
    const eq = PRESET_EQUATIONS[index];
    if (!eq) return;
    const latexInput = document.getElementById('mathchem-latex-input');
    const numInput = document.getElementById('mathchem-eq-num');
    const domainInput = document.getElementById('mathchem-domain-input');
    const nameInput = document.getElementById('mathchem-name-input');

    if (latexInput) latexInput.value = eq.latex;
    if (numInput) numInput.value = eq.num;
    if (domainInput) domainInput.value = eq.domain;
    if (nameInput) nameInput.value = eq.name;

    convertEquation();
  }

  async function convertEquation() {
    const latex = document.getElementById('mathchem-latex-input')?.value?.trim();
    const num = document.getElementById('mathchem-eq-num')?.value?.trim() || "1.1";
    const previewNum = document.getElementById('mathchem-preview-num');
    if (previewNum) previewNum.innerText = `(${num})`;

    if (!latex) return;

    try {
      const res = await fetch('/api/math-chem/convert-equation', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ latex, equation_number: num })
      });
      const data = await res.json();
      if (data.success) {
        _lastOmmlXml = data.omml_xml || '';
        const renderEl = document.getElementById('mathchem-katex-render');
        if (renderEl) {
          renderEl.innerHTML = `$$${data.latex}$$`;
          if (window.renderMathInElement) {
            renderMathInElement(renderEl, { delimiters: [{ left: '$$', right: '$$', display: true }] });
          } else if (window.katex) {
            katex.render(data.latex, renderEl, { displayMode: true, throwOnError: false });
          }
        }
      }
    } catch (e) {
      console.error("Lỗi chuyển đổi công thức:", e);
    }
  }

  function copyOMML() {
    if (!_lastOmmlXml) {
      if (window.App) App.toast("Chưa có mã OMML XML sẵn sàng.", "warning");
      return;
    }
    navigator.clipboard.writeText(_lastOmmlXml).then(() => {
      if (window.App) App.toast("Đã sao chép mã Word OMML XML vào Clipboard!", "success");
    }).catch(err => {
      if (window.App) App.toast("Không thể sao chép: " + err.message, "error");
    });
  }

  async function generateInterpretation() {
    const latex = document.getElementById('mathchem-latex-input')?.value?.trim();
    const name = document.getElementById('mathchem-name-input')?.value?.trim();
    const domain = document.getElementById('mathchem-domain-input')?.value?.trim();

    if (!latex) {
      if (window.App) App.toast("Vui lòng nhập công thức LaTeX trước khi sinh diễn giải.", "warning");
      return;
    }

    const btn = document.getElementById('mathchem-btn-interpret');
    if (btn) btn.innerHTML = "⏳ Đang sinh diễn giải 4 yếu tố...";

    try {
      const res = await fetch('/api/math-chem/generate-interpretation', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ latex, equation_name: name, domain })
      });
      const data = await res.json();
      if (data.success) {
        const outBox = document.getElementById('mathchem-interp-output');
        if (outBox) {
          outBox.value = data.interpretation;
          outBox.style.display = 'block';
        }
        if (window.App) App.toast("Đã tạo lời diễn giải học thuật 4 yếu tố thành công!", "success");
      }
    } catch (e) {
      if (window.App) App.toast("Lỗi tạo lời diễn giải: " + e.message, "error");
    } finally {
      if (btn) btn.innerHTML = "🤖 AI Sinh Diễn Giải 4 Yếu Tố";
    }
  }

  function pushToWordEnhance() {
    const latex = document.getElementById('mathchem-latex-input')?.value?.trim();
    const num = document.getElementById('mathchem-eq-num')?.value?.trim();
    const interp = document.getElementById('mathchem-interp-output')?.value?.trim();

    const optLatex = document.getElementById('mathchem-opt-latex');
    const optNum = document.getElementById('mathchem-opt-eq-num');
    const optInterp = document.getElementById('mathchem-opt-interp');

    if (optLatex && latex) optLatex.value = latex;
    if (optNum && num) optNum.value = num;
    if (optInterp && interp) optInterp.value = interp;

    switchSubtab('enhance');
    if (window.App) App.toast("Đã chuyển công thức và diễn giải sang Tab Nâng Cấp File Word!", "success");
  }

  function pullFromSubtab1() {
    const latex = document.getElementById('mathchem-latex-input')?.value?.trim();
    const num = document.getElementById('mathchem-eq-num')?.value?.trim();
    const interp = document.getElementById('mathchem-interp-output')?.value?.trim();

    const optLatex = document.getElementById('mathchem-opt-latex');
    const optNum = document.getElementById('mathchem-opt-eq-num');
    const optInterp = document.getElementById('mathchem-opt-interp');

    if (optLatex && latex) optLatex.value = latex;
    if (optNum && num) optNum.value = num;
    if (optInterp && interp) optInterp.value = interp;

    if (window.App) App.toast("Đã lấy công thức từ Tab 1 thành công!", "info");
  }

  // --- CHART GENERATOR ---
  function renderChartRows() {
    const tbody = document.getElementById('mathchem-chart-table-body');
    if (!tbody) return;
    tbody.innerHTML = _chartCategories.map((cat, i) => `
      <tr>
        <td style="padding:6px;"><input type="text" class="form-control" value="${cat}" oninput="MathChemProUI.updateChartCat(${i}, this.value)" style="font-size:12px; padding:4px 8px;"></td>
        <td style="padding:6px;"><input type="number" step="0.1" class="form-control" value="${_chartValues[i]}" oninput="MathChemProUI.updateChartVal(${i}, this.value)" style="font-size:12px; padding:4px 8px;"></td>
        <td style="padding:6px; text-align:center;"><button type="button" class="btn btn-outline btn-sm" onclick="MathChemProUI.removeChartRow(${i})" style="color:#ef4444; padding:2px 6px;">✕</button></td>
      </tr>
    `).join('');
  }

  function addChartRow() {
    _chartCategories.push(`Mẫu ${_chartCategories.length + 1}`);
    _chartValues.push(15.0);
    renderChartRows();
  }

  function removeChartRow(idx) {
    if (_chartCategories.length <= 1) return;
    _chartCategories.splice(idx, 1);
    _chartValues.splice(idx, 1);
    renderChartRows();
  }

  function updateChartCat(idx, val) { _chartCategories[idx] = val; }
  function updateChartVal(idx, val) { _chartValues[idx] = parseFloat(val) || 0; }

  async function generateChart() {
    const title = document.getElementById('mathchem-chart-title')?.value || "Biểu đồ khoa học";
    const xlabel = document.getElementById('mathchem-chart-xlabel')?.value || "Nhóm";
    const ylabel = document.getElementById('mathchem-chart-ylabel')?.value || "Giá trị";
    const chart_type = document.getElementById('mathchem-chart-type')?.value || "bar";

    const btn = document.getElementById('mathchem-btn-create-chart');
    if (btn) btn.innerHTML = "⏳ Đang vẽ chuẩn 300 DPI...";

    try {
      const res = await fetch('/api/math-chem/generate-chart', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          chart_type, title, xlabel, ylabel,
          categories: _chartCategories,
          values: _chartValues
        })
      });
      const data = await res.json();
      if (data.success) {
        const preview = document.getElementById('mathchem-chart-preview');
        if (preview) {
          preview.innerHTML = `
            <div style="text-align:center;">
              <img src="${data.file_url}?t=${Date.now()}" alt="${data.title}" style="max-width:100%; max-height:340px; border-radius:8px; border:1px solid rgba(59,130,246,0.3); box-shadow:0 4px 16px rgba(0,0,0,0.3);">
              <p style="font-size:12px; font-weight:700; font-style:italic; margin-top:8px; color:#cbd5e1;">Hình: ${data.title} (Chuẩn 300 DPI)</p>
              <div style="display:flex; gap:8px; justify-content:center; margin-top:8px; flex-wrap:wrap;">
                <a href="${data.file_url}" download="${data.filename}" class="btn btn-primary btn-sm" style="display:inline-flex; gap:6px;">⬇️ Tải Ảnh 300 DPI</a>
                <button type="button" class="btn btn-secondary btn-sm" onclick="MathChemProUI.linkImageToWordEnhance('${data.filename}', 'Hình: ${data.title}')" style="color:#6ee7b7; border-color:rgba(110,231,183,0.4);">⚡ Nhúng Vào File Word</button>
              </div>
            </div>
          `;
        }
        if (window.App) App.toast("Đã xuất biểu đồ khoa học 300 DPI thành công!", "success");
        const optImg = document.getElementById('mathchem-opt-img-name'); if(optImg) optImg.value = data.filename;
        const optCap = document.getElementById('mathchem-opt-img-cap'); if(optCap) optCap.value = 'Hình: ' + data.title;
      }
    } catch (e) {
      if (window.App) App.toast("Lỗi tạo biểu đồ: " + e.message, "error");
    } finally {
      if (btn) btn.innerHTML = "📊 Xuất Biểu Đồ Chuẩn 300 DPI";
    }
  }

  // --- FLOWCHART BUILDER ---
  function renderFlowchartRows() {
    const list = document.getElementById('mathchem-flow-steps-list');
    if (!list) return;
    list.innerHTML = _flowchartSteps.map((step, i) => `
      <div style="display:flex; gap:8px; align-items:center; margin-bottom:8px; background:rgba(255,255,255,0.03); padding:8px 12px; border-radius:8px; border:1px solid rgba(255,255,255,0.08);">
        <span style="font-weight:800; color:#3b82f6; font-size:12px; width:60px;">Bước ${i+1}:</span>
        <input type="text" class="form-control" value="${step.title}" oninput="MathChemProUI.updateFlowTitle(${i}, this.value)" placeholder="Tên bước" style="flex:1; font-size:12px; padding:4px 8px;">
        <input type="text" class="form-control" value="${step.desc}" oninput="MathChemProUI.updateFlowDesc(${i}, this.value)" placeholder="Mô tả phụ" style="flex:1.5; font-size:12px; padding:4px 8px;">
        <button type="button" class="btn btn-outline btn-sm" onclick="MathChemProUI.removeFlowStep(${i})" style="color:#ef4444; padding:2px 6px;">✕</button>
      </div>
    `).join('');
  }

  function addFlowStep() {
    _flowchartSteps.push({ title: `Bước ${_flowchartSteps.length + 1}`, desc: 'Mô tả chi tiết' });
    renderFlowchartRows();
  }

  function removeFlowStep(idx) {
    if (_flowchartSteps.length <= 1) return;
    _flowchartSteps.splice(idx, 1);
    renderFlowchartRows();
  }

  function updateFlowTitle(idx, val) { _flowchartSteps[idx].title = val; }
  function updateFlowDesc(idx, val) { _flowchartSteps[idx].desc = val; }

  async function generateFlowchart() {
    const title = document.getElementById('mathchem-flow-title')?.value || "Sơ đồ quy trình công nghệ";
    const btn = document.getElementById('mathchem-btn-create-flow');
    if (btn) btn.innerHTML = "⏳ Đang xuất sơ đồ 300 DPI...";

    try {
      const res = await fetch('/api/math-chem/generate-flowchart', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, steps: _flowchartSteps })
      });
      const data = await res.json();
      if (data.success) {
        const preview = document.getElementById('mathchem-flow-preview');
        if (preview) {
          preview.innerHTML = `
            <div style="text-align:center;">
              <img src="${data.file_url}?t=${Date.now()}" alt="${data.title}" style="max-width:100%; max-height:340px; border-radius:8px; border:1px solid rgba(59,130,246,0.3); box-shadow:0 4px 16px rgba(0,0,0,0.3);">
              <p style="font-size:12px; font-weight:700; font-style:italic; margin-top:8px; color:#cbd5e1;">Hình: ${data.title} (Chuẩn 300 DPI)</p>
              <div style="display:flex; gap:8px; justify-content:center; margin-top:8px; flex-wrap:wrap;">
                <a href="${data.file_url}" download="${data.filename}" class="btn btn-primary btn-sm" style="display:inline-flex; gap:6px;">⬇️ Tải Sơ Đồ 300 DPI</a>
                <button type="button" class="btn btn-secondary btn-sm" onclick="MathChemProUI.linkImageToWordEnhance('${data.filename}', 'Hình: ${data.title}')" style="color:#6ee7b7; border-color:rgba(110,231,183,0.4);">⚡ Nhúng Vào File Word</button>
              </div>
            </div>
          `;
        }
        if (window.App) App.toast("Đã xuất sơ đồ quy trình 300 DPI thành công!", "success");
        const optImg = document.getElementById('mathchem-opt-img-name'); if(optImg) optImg.value = data.filename;
        const optCap = document.getElementById('mathchem-opt-img-cap'); if(optCap) optCap.value = 'Hình: ' + data.title;
      }
    } catch (e) {
      if (window.App) App.toast("Lỗi tạo sơ đồ: " + e.message, "error");
    } finally {
      if (btn) btn.innerHTML = "🔀 Xuất Sơ Đồ Quy Trình 300 DPI";
    }
  }

  function linkImageToWordEnhance(filename, caption) {
    const optImg = document.getElementById('mathchem-opt-img-name');
    const optCap = document.getElementById('mathchem-opt-img-cap');
    if (optImg) optImg.value = filename;
    if (optCap) optCap.value = caption;
    switchSubtab('enhance');
    if (window.App) App.toast(`Đã gán ảnh '${filename}' vào Tab Nâng Cấp File Word!`, "success");
  }

  // --- WIKIMEDIA IMAGE SEARCH ---
  function quickSearch(keyword) {
    const input = document.getElementById('mathchem-img-search-input');
    if (input) input.value = keyword;
    searchImages();
  }

  async function searchImages() {
    const q = document.getElementById('mathchem-img-search-input')?.value?.trim();
    if (!q) {
      if (window.App) App.toast("Vui lòng nhập từ khóa tìm kiếm ảnh.", "warning");
      return;
    }
    const container = document.getElementById('mathchem-img-search-results');
    if (container) container.innerHTML = '<div style="padding:20px; text-align:center; color:#94a3b8; grid-column:1/-1;">⏳ Đang tìm kiếm trên Wikimedia Commons...</div>';

    try {
      const res = await fetch('/api/math-chem/search-images', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: q, limit: 8 })
      });
      const data = await res.json();
      if (data.results && data.results.length > 0) {
        container.innerHTML = data.results.map((img) => `
          <div style="background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.1); border-radius:10px; padding:10px; display:flex; flex-direction:column; justify-content:space-between;">
            <img src="${img.thumb_url}" alt="${img.title}" style="width:100%; height:130px; object-fit:cover; border-radius:6px; margin-bottom:8px;">
            <div style="font-size:11px; color:#cbd5e1; font-weight:600; line-height:1.3; height:32px; overflow:hidden; text-overflow:ellipsis;" title="${img.title}">${img.title}</div>
            <div style="font-size:10px; color:#94a3b8; margin:4px 0;">Độ phân giải: ${img.width}x${img.height}</div>
            <button type="button" class="btn btn-primary btn-sm" onclick="MathChemProUI.downloadImage('${img.url}', '${img.title.replace(/'/g, "\\'")}')" style="font-size:11px; padding:4px 8px; margin-top:6px;">📥 Tải & Nhúng 300 DPI</button>
          </div>
        `).join('');
      } else {
        container.innerHTML = '<div style="padding:20px; text-align:center; color:#94a3b8; grid-column:1/-1;">Không tìm thấy hình ảnh phù hợp. Hãy thử từ khóa tiếng Anh học thuật.</div>';
      }
    } catch (e) {
      if (container) container.innerHTML = `<div style="color:#ef4444; padding:16px; grid-column:1/-1;">Lỗi tìm kiếm: ${e.message}</div>`;
    }
  }

  async function downloadImage(url, title = "") {
    try {
      if (window.App) App.toast("Đang tải và chuẩn hóa ảnh sang 300 DPI...", "info");
      const res = await fetch('/api/math-chem/download-image', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url })
      });
      const data = await res.json();
      if (data.success) {
        if (window.App) App.toast(`Đã lưu ảnh 300 DPI vào Workspace: ${data.filename}`, "success");
        linkImageToWordEnhance(data.filename, title ? `Hình: ${title}` : `Hình: ${data.filename}`);
      }
    } catch (e) {
      if (window.App) App.toast("Lỗi tải ảnh: " + e.message, "error");
    }
  }

  // --- DOCX ENHANCER (DUAL SOURCE & REPAIRED WORD PACKAGING) ---
  function selectEnhanceMode(mode) {
    _selectedEnhanceMode = mode;
    document.querySelectorAll('.enhance-mode-card').forEach(card => {
      card.classList.toggle('active', card.getAttribute('data-mode') === mode);
    });

    const mathOpts = document.getElementById('mathchem-section-math-opts');
    const imgOpts = document.getElementById('mathchem-section-img-opts');
    const btnText = document.getElementById('mathchem-btn-enhance-text');

    if (mode === 'math_chem_only') {
      if (mathOpts) mathOpts.style.display = 'block';
      if (imgOpts) imgOpts.style.display = 'none';
      if (btnText) btnText.innerText = '📐 Nâng Cấp File Word (Chỉ Fix Toán & Hóa)';
    } else if (mode === 'images_only') {
      if (mathOpts) mathOpts.style.display = 'none';
      if (imgOpts) imgOpts.style.display = 'block';
      if (btnText) btnText.innerText = '📊 Nâng Cấp File Word (Chỉ Thêm Hình Ảnh 300 DPI)';
    } else {
      if (mathOpts) mathOpts.style.display = 'block';
      if (imgOpts) imgOpts.style.display = 'block';
      if (btnText) btnText.innerText = '⚡ Nâng Cấp File Word 1-Click (Thực Hiện Cả 2)';
    }
  }

  let _uploadedFile = null;

  function setupDropZone() {
    const dropZone = document.getElementById('mathchem-drop-zone');
    if (!dropZone) return;

    ['dragenter', 'dragover'].forEach(eventName => {
      dropZone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropZone.style.borderColor = '#3b82f6';
        dropZone.style.background = 'rgba(59,130,246,0.1)';
      }, false);
    });

    ['dragleave', 'dragend'].forEach(eventName => {
      dropZone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropZone.style.borderColor = 'rgba(59,130,246,0.5)';
        dropZone.style.background = 'rgba(59,130,246,0.03)';
      }, false);
    });

    dropZone.addEventListener('drop', (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropZone.style.borderColor = 'rgba(59,130,246,0.5)';
      dropZone.style.background = 'rgba(59,130,246,0.03)';
      if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        handleFileSelected({ target: { files: e.dataTransfer.files } });
      }
    }, false);
  }

  function handleFileSelected(event) {
    const file = event.target?.files?.[0];
    if (!file) return;
    if (!file.name.toLowerCase().endsWith('.docx')) {
      if (window.App) App.toast('Vui lòng chọn hoặc kéo thả tệp Word (.docx).', 'warning');
      return;
    }
    _uploadedFile = file;
    const label = document.getElementById('mathchem-selected-file-label');
    if (label) {
      label.innerHTML = `📄 <strong>Đã chọn:</strong> <span style="color:#60a5fa; font-weight:700;">${file.name}</span> (${(file.size / 1024).toFixed(1)} KB)`;
    }
    if (window.App) App.toast(`Đã chọn tệp '${file.name}'! Sẵn sàng quét và nâng cấp.`, 'info');
  }

  function switchSourceMode(mode) {
    _sourceMode = mode;
    const wsBtn = document.getElementById('mathchem-src-ws-btn');
    const upBtn = document.getElementById('mathchem-src-up-btn');
    const wsPane = document.getElementById('mathchem-source-workspace-pane');
    const upPane = document.getElementById('mathchem-source-upload-pane');

    if (wsBtn) wsBtn.classList.toggle('active', mode === 'workspace');
    if (upBtn) upBtn.classList.toggle('active', mode === 'upload');
    if (wsPane) wsPane.style.display = (mode === 'workspace') ? 'block' : 'none';
    if (upPane) upPane.style.display = (mode === 'upload') ? 'block' : 'none';
    if (mode === 'upload') {
      setupDropZone();
    }
  }

  async function loadWorkspaceFiles() {
    const select = document.getElementById('mathchem-workspace-select');
    if (!select) return;

    try {
      const res = await fetch('/api/math-chem/workspace-docx-files');
      const data = await res.json();
      if (data.success && data.files && data.files.length > 0) {
        select.innerHTML = `
          <option value="">-- Chọn 1 tệp .docx trong Workspace (${data.files.length} tệp) --</option>
          ${data.files.map(f => {
            const sizeKb = Math.round(f.size / 1024);
            const badge = f.category === 'Ban_Thao' ? '📝 Bản Thảo' : f.category === 'Tai_Lieu' ? '📚 Tài Liệu' : f.category === 'Xuat_Ban' ? '🏆 Xuất Bản' : '🏷️ Zotero';
            return `<option value="${f.rel_path}">[${badge}] ${f.name} (${sizeKb} KB)</option>`;
          }).join('')}
        `;
      } else {
        select.innerHTML = '<option value="">-- Chưa có tệp .docx nào trong Workspace. Hãy tải tệp lên hoặc tạo bản thảo --</option>';
      }
    } catch (e) {
      select.innerHTML = '<option value="">-- Không thể nạp danh sách tệp --</option>';
    }
  }

  async function enhanceDocx() {
    const formData = new FormData();
    formData.append('mode', _selectedEnhanceMode);
    formData.append('normalize_chem', document.getElementById('mathchem-opt-chem')?.checked ? 'true' : 'false');
    formData.append('normalize_decimals', document.getElementById('mathchem-opt-decimal')?.checked ? 'true' : 'false');
    formData.append('convert_latex_blocks', document.getElementById('mathchem-opt-latex-blocks')?.checked ? 'true' : 'false');

    if (_sourceMode === 'workspace') {
      const wsPath = document.getElementById('mathchem-workspace-select')?.value;
      if (!wsPath) {
        if (window.App) App.toast("Vui lòng chọn 1 tệp Word có sẵn trong Workspace.", "warning");
        return;
      }
      formData.append('workspace_file_path', wsPath);
    } else {
      const fileInput = document.getElementById('mathchem-docx-file');
      const chosenFile = _uploadedFile || fileInput?.files?.[0];
      if (!chosenFile) {
        if (window.App) App.toast("Vui lòng kéo thả hoặc chọn 1 tệp Word (.docx) từ máy tính.", "warning");
        return;
      }
      formData.append('file', chosenFile);
    }

    const eqLatex = document.getElementById('mathchem-opt-latex')?.value?.trim();
    const eqNum = document.getElementById('mathchem-opt-eq-num')?.value?.trim();
    const eqInterp = document.getElementById('mathchem-opt-interp')?.value?.trim();
    const imgName = document.getElementById('mathchem-opt-img-name')?.value?.trim();
    const imgCap = document.getElementById('mathchem-opt-img-cap')?.value?.trim();

    if (eqLatex && _selectedEnhanceMode !== 'images_only') formData.append('add_equation_latex', eqLatex);
    if (eqNum && _selectedEnhanceMode !== 'images_only') formData.append('equation_number', eqNum);
    if (eqInterp && _selectedEnhanceMode !== 'images_only') formData.append('equation_interpretation', eqInterp);
    if (imgName && _selectedEnhanceMode !== 'math_chem_only') formData.append('image_filename', imgName);
    if (imgCap && _selectedEnhanceMode !== 'math_chem_only') formData.append('image_caption', imgCap);

    const btn = document.getElementById('mathchem-btn-enhance');
    if (btn) btn.innerHTML = "⏳ Đang quét cấu trúc, công thức Toán - Hóa & sửa lỗi đóng gói Word...";

    try {
      const res = await fetch('/api/math-chem/enhance-docx', {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      if (data.success) {
        const stats = data.stats || {};
        const resultBox = document.getElementById('mathchem-enhance-result');
        if (resultBox) {
          resultBox.innerHTML = `
            <div style="background:rgba(16,185,129,0.08); border:1.5px solid #10b981; border-radius:12px; padding:20px; text-align:center;">
              <h4 style="color:#6ee7b7; margin:0 0 12px 0; font-size:16.5px; font-weight:800; display:flex; align-items:center; justify-content:center; gap:8px;">
                <span>🎉</span> Quét &amp; Nâng Cấp File Word Thành Công!
              </h4>
              <div style="display:flex; justify-content:center; gap:8px; flex-wrap:wrap; margin-bottom:14px;">
                <span class="mathchem-stat-badge" style="background:rgba(16,185,129,0.2); color:#a7f3d0; padding:5px 12px; border-radius:8px; font-size:12px; font-weight:700;">🧪 ${stats.chem_normalized || stats.chem_fixes || 0} vị trí hóa học (FeS₂, H₂SO₄, NH₄⁺...)</span>
                <span class="mathchem-stat-badge" style="background:rgba(59,130,246,0.2); color:#93c5fd; padding:5px 12px; border-radius:8px; font-size:12px; font-weight:700;">📐 ${stats.equations_added || stats.block_equations || 0} công thức Word Equation OMML</span>
                <span class="mathchem-stat-badge" style="background:rgba(234,179,8,0.2); color:#fde047; padding:5px 12px; border-radius:8px; font-size:12px; font-weight:700;">🔢 ${stats.decimal_normalized || stats.decimal_fixes || 0} số thập phân chuẩn (1,5; 28,5%)</span>
                <span class="mathchem-stat-badge" style="background:rgba(168,85,247,0.2); color:#d8b4fe; padding:5px 12px; border-radius:8px; font-size:12px; font-weight:700;">📑 ${stats.tables_scanned || 0} bảng biểu đã xử lý</span>
              </div>
              <p style="font-size:12.5px; color:#cbd5e1; margin:0 0 16px 0; line-height:1.6;">
                ✅ <strong>Bảo toàn 100% In-Place DOM:</strong> Heading Styles, bảng mục lục động, hình ảnh &amp; mã trích dẫn Zotero XML.<br>
                📁 Tệp đã lưu tại: <code style="color:#60a5fa; font-weight:700;">workspace/${data.rel_path}</code>
              </p>
              <div style="display:flex; gap:10px; justify-content:center; flex-wrap:wrap;">
                <button type="button" class="btn btn-primary" onclick="App.openFileInSystem('${data.rel_path}')" style="font-size:13px; font-weight:700; display:inline-flex; align-items:center; gap:6px;">
                  📝 Mở Trực Tiếp Trên Word (.docx)
                </button>
                <a href="${data.file_url}" download="${data.filename}" class="btn btn-secondary" style="font-size:13px; font-weight:700; display:inline-flex; align-items:center; gap:6px;">
                  ⬇️ Tải Về (.docx)
                </a>
                <button type="button" class="btn btn-secondary" onclick="MathChemProUI.openInDocxEditor('${data.rel_path}')" style="font-size:13px; font-weight:700; color:#93c5fd; border-color:rgba(147,197,253,0.4);">
                  📊 Mở Trong Trình Biên Tập Số Liệu
                </button>
                <button type="button" class="btn btn-secondary" onclick="App.openWindowsExplorer('Ban_Thao')" style="font-size:13px; font-weight:700; color:#cbd5e1;">
                  📂 Mở Folder Workspace
                </button>
              </div>
            </div>
          `;
        }
        if (window.App) App.toast("Quét và chuẩn hóa công thức Toán - Hóa thành công!", "success");
        loadWorkspaceFiles();
      } else {
        throw new Error(data.detail || "Không thể nâng cấp file");
      }
    } catch (e) {
      if (window.App) App.toast("Lỗi nâng cấp file Word: " + e.message, "error");
      const resultBox = document.getElementById('mathchem-enhance-result');
      if (resultBox) {
        resultBox.innerHTML = `
          <div style="background:rgba(239,68,68,0.1); border:1px solid #ef4444; border-radius:10px; padding:14px; color:#fca5a5; font-size:13px;">
            ❌ <strong>Lỗi xử lý:</strong> ${e.message}
          </div>
        `;
      }
    } finally {
      if (btn) {
        btn.innerHTML = `<span id="mathchem-btn-enhance-text">🚀 Quét &amp; Nâng Cấp Công Thức Toán - Hóa Toàn Diện (.docx)</span>`;
      }
    }
  }

  function openInDocxEditor(relPath) {
    if (window.DocxEditorUI && typeof window.DocxEditorUI.loadDocxFromWorkspace === 'function') {
      if (window.App && typeof window.App.switchTab === 'function') {
        window.App.switchTab('workspace-tab');
      }
      setTimeout(() => {
        window.DocxEditorUI.loadDocxFromWorkspace(relPath);
      }, 200);
    } else if (window.App && typeof window.App.switchTab === 'function') {
      window.App.switchTab('workspace-tab');
    }
  }

  return {
    init,
    switchSubtab,
    selectDomain,
    filterPresets,
    loadPreset,
    convertEquation,
    copyOMML,
    generateInterpretation,
    pushToWordEnhance,
    pullFromSubtab1,
    addChartRow,
    removeChartRow,
    updateChartCat,
    updateChartVal,
    generateChart,
    addFlowStep,
    removeFlowStep,
    updateFlowTitle,
    updateFlowDesc,
    generateFlowchart,
    linkImageToWordEnhance,
    quickSearch,
    searchImages,
    downloadImage,
    selectEnhanceMode,
    switchSourceMode,
    loadWorkspaceFiles,
    setupDropZone,
    handleFileSelected,
    enhanceDocx,
    openInDocxEditor
  };
})();

// Auto-init on page load
document.addEventListener('DOMContentLoaded', () => {
  MathChemProUI.init();
});

