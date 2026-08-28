/**
 * WEB SUPER v3.2 / v2.0 - BigQuery AI & ML Analytics Module
 * Điều khiển Giao diện Phân Tích Dữ Liệu Lớn & Mô Hình Hóa Học Thuật:
 * 1. 📈 Dự Báo Chuỗi Thời Gian (AI.FORECAST / ARIMA_PLUS)
 * 2. 🚨 Phát Hiện Điểm Dị Biệt (AI.DETECT_ANOMALIES)
 * 3. 🔑 Phân Tích Động Lực Cốt Lõi (AI.KEY_DRIVERS)
 * 4. 💻 Trợ Lý Chuyển Đổi BigQuery SQL (AI.GENERATE / NL2SQL)
 */

const BigQueryMLUI = (() => {
  let _activeSubtab = 'forecast';
  let _loadedDataset = null;
  let _lastAnalysisResult = null;
  let _lastAnalysisType = null;

  function init() {
    console.log("🚀 Khởi tạo BigQuery AI & ML Analytics Module...");
    _bindEvents();
  }

  function _bindEvents() {
    // Dataset file upload
    const fileInput = document.getElementById('bq-dataset-file');
    if (fileInput) {
      fileInput.addEventListener('change', (e) => {
        if (e.target.files && e.target.files[0]) {
          uploadDataset(e.target.files[0]);
        }
      });
    }
  }

  function switchSubtab(subtabId) {
    _activeSubtab = subtabId;
    
    // Update button states
    ['forecast', 'anomalies', 'drivers', 'nl2sql'].forEach(t => {
      const btn = document.getElementById(`bq-subtab-btn-${t}`);
      const pane = document.getElementById(`bq-subtab-pane-${t}`);
      if (btn) {
        if (t === subtabId) {
          btn.classList.add('active');
          btn.style.borderColor = 'var(--accent-primary, #3b82f6)';
          btn.style.background = 'rgba(59, 130, 246, 0.15)';
        } else {
          btn.classList.remove('active');
          btn.style.borderColor = 'var(--border-color, rgba(255,255,255,0.1))';
          btn.style.background = 'transparent';
        }
      }
      if (pane) {
        pane.style.display = (t === subtabId) ? 'block' : 'none';
      }
    });
  }

  // ══════════════════════════════════════════════════════════════════════
  // NẠP DỮ LIỆU & DỮ LIỆU MẪU NHANH
  // ══════════════════════════════════════════════════════════════════════
  async function uploadDataset(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const infoBox = document.getElementById('bq-dataset-status');
    if (infoBox) infoBox.innerHTML = '<span style="color:#fde68a;">⏳ Đang đọc và phân tích cấu trúc tệp dữ liệu...</span>';

    try {
      const res = await fetch('/api/bigquery/upload-dataset', {
        method: 'POST',
        headers: {
          ...((window.AuthManager && AuthManager.token) ? { 'Authorization': `Bearer ${AuthManager.token}` } : {})
        },
        body: formData
      });
      const data = await res.json();
      if (data.status === 'success') {
        _loadedDataset = data;
        _renderDatasetSummary(data);
        _populateColumnSelects(data.columns);
        if (window.App) App.toast(data.message || "Nạp dữ liệu thành công!", "success");
      } else {
        if (window.App) App.toast(data.message || "Lỗi đọc tệp dữ liệu", "error");
      }
    } catch (e) {
      if (window.App) App.toast("Lỗi tải tệp: " + e.message, "error");
    }
  }

  function loadSamplePreset(presetType) {
    let sampleData = [];
    let timeCol = 'year';
    let valCol = 'papers';
    let targetCol = 'efficiency';

    if (presetType === 'microplastics_trend') {
      sampleData = [
        {"year": "2015", "papers": 120},
        {"year": "2016", "papers": 145},
        {"year": "2017", "papers": 190},
        {"year": "2018", "papers": 260},
        {"year": "2019", "papers": 340},
        {"year": "2020", "papers": 480},
        {"year": "2021", "papers": 620},
        {"year": "2022", "papers": 810},
        {"year": "2023", "papers": 1050},
        {"year": "2024", "papers": 1340}
      ];
      document.getElementById('bq-forecast-metric').value = "Số Lượng Bài Báo Vi Nhựa (Microplastics)";
      document.getElementById('bq-forecast-topic').value = "Xu Hướng Nghiên Cứu Ô Nhiễm Vi Nhựa Toàn Cầu";
    } else if (presetType === 'water_quality_anomalies') {
      sampleData = [
        {"station": "ST01_ThuongLuu", "cod": 25.4, "do": 6.8, "bod5": 12.1},
        {"station": "ST02_CauSong", "cod": 28.1, "do": 6.5, "bod5": 13.4},
        {"station": "ST03_KhuDanCu", "cod": 26.8, "do": 6.4, "bod5": 12.8},
        {"station": "ST04_KhuCN_A", "cod": 29.3, "do": 6.2, "bod5": 14.0},
        {"station": "ST05_CuaXaThai", "cod": 88.5, "do": 2.1, "bod5": 48.2}, // Outlier
        {"station": "ST06_HaLuu_1", "cod": 27.2, "do": 6.3, "bod5": 13.0},
        {"station": "ST07_HaLuu_2", "cod": 24.9, "do": 6.7, "bod5": 11.9},
        {"station": "ST08_CuaBien", "cod": 30.1, "do": 6.1, "bod5": 14.5},
        {"station": "ST09_DauNguon", "cod": 4.2, "do": 8.4, "bod5": 2.1}, // Low outlier
        {"station": "ST10_KiemChung", "cod": 26.5, "do": 6.6, "bod5": 12.5}
      ];
      timeCol = 'station';
      valCol = 'cod';
      document.getElementById('bq-anomaly-metric').value = "Nồng Độ COD Nước Mặt (mg/L)";
      document.getElementById('bq-anomaly-topic').value = "Đánh Giá Chất Lượng Môi Trường Nước Sông";
    } else if (presetType === 'catalyst_efficiency') {
      sampleData = [
        {"temp": 120, "ph": 4.5, "catalyst_dose": 0.5, "efficiency": 45.2},
        {"temp": 140, "ph": 5.0, "catalyst_dose": 1.0, "efficiency": 62.4},
        {"temp": 160, "ph": 6.5, "catalyst_dose": 1.5, "efficiency": 78.9},
        {"temp": 180, "ph": 7.0, "catalyst_dose": 2.0, "efficiency": 91.5},
        {"temp": 200, "ph": 8.0, "catalyst_dose": 2.5, "efficiency": 95.8},
        {"temp": 220, "ph": 9.0, "catalyst_dose": 3.0, "efficiency": 94.2},
        {"temp": 240, "ph": 9.5, "catalyst_dose": 3.2, "efficiency": 92.1}
      ];
      targetCol = 'efficiency';
      document.getElementById('bq-drivers-topic').value = "Tối Ưu Hóa Phản Ứng Xúc Tác Quang Hóa Xử Lý Ô Nhiễm";
    }

    _loadedDataset = {
      filename: `sample_${presetType}.json`,
      total_rows: sampleData.length,
      columns: Object.keys(sampleData[0]),
      all_data: sampleData
    };

    _renderDatasetSummary(_loadedDataset);
    _populateColumnSelects(_loadedDataset.columns, timeCol, valCol, targetCol);
    if (window.App) App.toast("Đã nạp bộ dữ liệu mẫu khoa học thực nghiệm!", "success");
  }

  function _renderDatasetSummary(data) {
    const infoBox = document.getElementById('bq-dataset-status');
    if (!infoBox) return;
    infoBox.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
        <span style="color:#34d399; font-weight:700;">✅ Đã nạp: <em>${data.filename}</em> (${data.total_rows} dòng, ${data.columns.length} cột)</span>
        <span style="color:#94a3b8; font-size:11.5px;">Cột: ${data.columns.map(c => `<code>${c}</code>`).join(', ')}</span>
      </div>
    `;
  }

  function _populateColumnSelects(columns, defTime = 'time', defVal = 'value', defTarget = 'target') {
    const selects = [
      { id: 'bq-fc-time-col', def: defTime },
      { id: 'bq-fc-val-col', def: defVal },
      { id: 'bq-an-id-col', def: defTime },
      { id: 'bq-an-val-col', def: defVal },
      { id: 'bq-kd-target-col', def: defTarget }
    ];
    selects.forEach(s => {
      const el = document.getElementById(s.id);
      if (el) {
        el.innerHTML = columns.map(c => `<option value="${c}" ${(c.toLowerCase() === s.def.toLowerCase() || columns.indexOf(c) === 0) ? 'selected' : ''}>${c}</option>`).join('');
      }
    });
  }

  // ══════════════════════════════════════════════════════════════════════
  // 1. CHẠY DỰ BÁO CHUỖI THỜI GIAN (AI.FORECAST)
  // ══════════════════════════════════════════════════════════════════════
  async function runForecast() {
    if (!_loadedDataset || !_loadedDataset.all_data || _loadedDataset.all_data.length < 3) {
      if (window.App) App.toast("Vui lòng nạp tệp dữ liệu hoặc chọn Dữ Liệu Mẫu trước khi chạy dự báo.", "warning");
      return;
    }

    const timeKey = document.getElementById('bq-fc-time-col')?.value || 'year';
    const valKey = document.getElementById('bq-fc-val-col')?.value || 'papers';
    const horizon = parseInt(document.getElementById('bq-fc-horizon')?.value || '4');
    const metricName = document.getElementById('bq-forecast-metric')?.value || 'Chỉ Số Khảo Sát';
    const topic = document.getElementById('bq-forecast-topic')?.value || 'Nghiên Cứu Khoa Học';

    const btn = document.getElementById('bq-btn-run-forecast');
    if (btn) btn.innerHTML = "⏳ Đang mô hình hóa BigQuery AI.FORECAST (ARIMA_PLUS)...";

    try {
      const res = await fetch('/api/bigquery/forecast', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...((window.AuthManager && AuthManager.token) ? { 'Authorization': `Bearer ${AuthManager.token}` } : {})
        },
        body: JSON.stringify({
          data_points: _loadedDataset.all_data,
          time_key: timeKey,
          value_key: valKey,
          horizon: horizon,
          confidence_level: 0.95,
          metric_name: metricName,
          topic: topic
        })
      });
      const data = await res.json();
      if (data.status === 'success') {
        _lastAnalysisResult = data;
        _lastAnalysisType = 'forecast';
        _renderForecastResult(data);
        if (window.App) App.toast("Mô hình hóa chuỗi thời gian thành công!", "success");
      } else {
        if (window.App) App.toast(data.message || "Lỗi mô hình hóa", "error");
      }
    } catch (e) {
      if (window.App) App.toast("Lỗi kết nối: " + e.message, "error");
    } finally {
      if (btn) btn.innerHTML = "📈 Chạy Mô Hình Dự Báo AI.FORECAST";
    }
  }

  function _renderForecastResult(data) {
    const box = document.getElementById('bq-analysis-output-container');
    if (!box) return;
    box.style.display = 'block';

    let tableRows = data.forecast_results.map((f, i) => `
      <tr style="border-bottom:1px solid rgba(255,255,255,0.06); font-size:12.5px;">
        <td style="padding:8px 10px; font-weight:700; color:#38bdf8;">${f.time}</td>
        <td style="padding:8px 10px; font-weight:800; color:#f8fafc;">${f.forecast_value.toLocaleString('vi-VN')}</td>
        <td style="padding:8px 10px; color:#94a3b8;">${f.lower_bound.toLocaleString('vi-VN')}</td>
        <td style="padding:8px 10px; color:#94a3b8;">${f.upper_bound.toLocaleString('vi-VN')}</td>
        <td style="padding:8px 10px; color:#34d399; font-weight:600;">95%</td>
      </tr>
    `).join('');

    box.innerHTML = `
      <div style="background:#0f172a; border:1px solid #3b82f6; border-radius:14px; padding:22px; margin-top:20px;">
        <!-- Header -->
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; flex-wrap:wrap; gap:10px;">
          <div>
            <span style="background:rgba(59,130,246,0.2); color:#60a5fa; padding:3px 10px; border-radius:12px; font-size:11.5px; font-weight:700;">
              📈 KẾT QUẢ DỰ BÁO CHUỖI THỜI GIAN (BIGQUERY AI.FORECAST)
            </span>
            <h3 style="font-size:17px; font-weight:800; color:#f8fafc; margin:6px 0 0 0;">${data.topic}</h3>
          </div>
          <button type="button" class="btn btn-primary btn-sm" onclick="BigQueryMLUI.exportReportDocx()" style="font-weight:700;">
            📝 Xuất Báo Cáo Word (.docx & 300 DPI)
          </button>
        </div>

        <!-- Metric Badges -->
        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(180px, 1fr)); gap:12px; margin-bottom:20px;">
          <div style="background:rgba(255,255,255,0.04); padding:12px; border-radius:10px; border:1px solid rgba(255,255,255,0.08);">
            <div style="font-size:11px; color:#94a3b8;">Xu Hướng Phát Triển</div>
            <div style="font-size:15px; font-weight:800; color:#34d399; margin-top:2px;">${data.trend_direction}</div>
          </div>
          <div style="background:rgba(255,255,255,0.04); padding:12px; border-radius:10px; border:1px solid rgba(255,255,255,0.08);">
            <div style="font-size:11px; color:#94a3b8;">Tốc Độ Biến Thiên Bình Quân</div>
            <div style="font-size:15px; font-weight:800; color:#38bdf8; margin-top:2px;">${data.annual_growth_rate}</div>
          </div>
          <div style="background:rgba(255,255,255,0.04); padding:12px; border-radius:10px; border:1px solid rgba(255,255,255,0.08);">
            <div style="font-size:11px; color:#94a3b8;">Chu Kỳ Dự Báo</div>
            <div style="font-size:15px; font-weight:800; color:#fde68a; margin-top:2px;">+${data.horizon} giai đoạn tiếp theo</div>
          </div>
        </div>

        <!-- 300 DPI Chart -->
        ${data.chart_url ? `
          <div style="text-align:center; margin-bottom:20px; background:#ffffff; border-radius:12px; padding:12px;">
            <img src="${data.chart_url}" alt="Biểu đồ dự báo BigQuery 300 DPI" style="max-width:100%; border-radius:8px; height:auto;">
            <div style="font-size:11.5px; color:#475569; margin-top:6px; font-style:italic;">Hình: Đồ thị chuỗi thời gian thực nghiệm và dự báo xu hướng tương lai kèm khoảng tin cậy 95% (Chuẩn In Ấn 300 DPI)</div>
          </div>
        ` : ''}

        <!-- Forecast Table -->
        <div style="overflow-x:auto; margin-bottom:20px;">
          <table style="width:100%; border-collapse:collapse; text-align:left;">
            <thead>
              <tr style="background:rgba(0,0,0,0.4); color:#94a3b8; font-size:12px;">
                <th style="padding:8px 10px;">Giai Đoạn / Mốc</th>
                <th style="padding:8px 10px;">Giá Trị Dự Báo (${data.metric_name})</th>
                <th style="padding:8px 10px;">Giới Hạn Dưới (95% CI)</th>
                <th style="padding:8px 10px;">Giới Hạn Trên (95% CI)</th>
                <th style="padding:8px 10px;">Độ Tin Cậy</th>
              </tr>
            </thead>
            <tbody>${tableRows}</tbody>
          </table>
        </div>

        <!-- Academic Interpretation -->
        <div style="background:rgba(59,130,246,0.08); border-left:4px solid #3b82f6; border-radius:0 10px 10px 0; padding:16px; margin-bottom:18px;">
          <h5 style="color:#60a5fa; font-size:13.5px; margin:0 0 6px 0; font-weight:700;">🎓 Nhận Định Phân Tích Học Thuật (ISI/Scopus Interpretation):</h5>
          <p style="font-size:13px; color:#e2e8f0; line-height:1.7; margin:0;">${data.academic_interpretation}</p>
        </div>

        <!-- SQL Syntax -->
        <div style="background:#020617; border-radius:8px; padding:12px; font-family:monospace; font-size:11.5px; color:#93c5fd; overflow-x:auto;">
          <div style="color:#64748b; margin-bottom:4px;">// Cú pháp Google BigQuery AI.FORECAST tương đương:</div>
          <pre style="margin:0;">${data.bigquery_sql_equivalent}</pre>
        </div>
      </div>
    `;

    box.scrollIntoView({ behavior: 'smooth' });
  }

  // ══════════════════════════════════════════════════════════════════════
  // 2. CHẠY PHÁT HIỆN DỊ BIỆT (AI.DETECT_ANOMALIES)
  // ══════════════════════════════════════════════════════════════════════
  async function runAnomalyDetection() {
    if (!_loadedDataset || !_loadedDataset.all_data || _loadedDataset.all_data.length < 4) {
      if (window.App) App.toast("Vui lòng nạp tệp dữ liệu (tối thiểu 4 mẫu) hoặc chọn Dữ Liệu Mẫu.", "warning");
      return;
    }

    const idKey = document.getElementById('bq-an-id-col')?.value || 'station';
    const valKey = document.getElementById('bq-an-val-col')?.value || 'cod';
    const metricName = document.getElementById('bq-anomaly-metric')?.value || 'Thông Số Đo Đạc';
    const topic = document.getElementById('bq-anomaly-topic')?.value || 'Kiểm Định Dữ Liệu';

    const btn = document.getElementById('bq-btn-run-anomaly');
    if (btn) btn.innerHTML = "⏳ Đang chạy BigQuery AI.DETECT_ANOMALIES...";

    try {
      const res = await fetch('/api/bigquery/detect-anomalies', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...((window.AuthManager && AuthManager.token) ? { 'Authorization': `Bearer ${AuthManager.token}` } : {})
        },
        body: JSON.stringify({
          data_points: _loadedDataset.all_data,
          id_key: idKey,
          value_key: valKey,
          contamination: 0.05,
          metric_name: metricName,
          topic: topic
        })
      });
      const data = await res.json();
      if (data.status === 'success') {
        _lastAnalysisResult = data;
        _lastAnalysisType = 'anomalies';
        _renderAnomalyResult(data);
        if (window.App) App.toast(`Đã phát hiện ${data.anomaly_points_count} điểm dị biệt!`, "success");
      } else {
        if (window.App) App.toast(data.message || "Lỗi kiểm định", "error");
      }
    } catch (e) {
      if (window.App) App.toast("Lỗi kết nối: " + e.message, "error");
    } finally {
      if (btn) btn.innerHTML = "🚨 Chạy Phát Hiện Dị Biệt AI.DETECT_ANOMALIES";
    }
  }

  function _renderAnomalyResult(data) {
    const box = document.getElementById('bq-analysis-output-container');
    if (!box) return;
    box.style.display = 'block';

    let anomRows = data.anomalies_detected.map(an => `
      <tr style="border-bottom:1px solid rgba(255,255,255,0.06); font-size:12.5px; background:rgba(239,68,68,0.08);">
        <td style="padding:8px 10px; font-weight:700; color:#fca5a5;">${an.id}</td>
        <td style="padding:8px 10px; font-weight:800; color:#ffffff;">${an.value.toLocaleString('vi-VN')}</td>
        <td style="padding:8px 10px; color:#f87171;">${an.z_score}</td>
        <td style="padding:8px 10px; color:#f87171; font-weight:700;">${(an.anomaly_probability*100).toFixed(0)}%</td>
        <td style="padding:8px 10px; color:#fde68a;">${an.deviation_type}</td>
        <td style="padding:8px 10px; color:#94a3b8;">${an.expected_range}</td>
      </tr>
    `).join('');

    box.innerHTML = `
      <div style="background:#0f172a; border:1px solid #ef4444; border-radius:14px; padding:22px; margin-top:20px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; flex-wrap:wrap; gap:10px;">
          <div>
            <span style="background:rgba(239,68,68,0.2); color:#f87171; padding:3px 10px; border-radius:12px; font-size:11.5px; font-weight:700;">
              🚨 KẾT QUẢ PHÁT HIỆN ĐIỂM DỊ BIỆT (BIGQUERY AI.DETECT_ANOMALIES)
            </span>
            <h3 style="font-size:17px; font-weight:800; color:#f8fafc; margin:6px 0 0 0;">${data.topic}</h3>
          </div>
          <button type="button" class="btn btn-primary btn-sm" onclick="BigQueryMLUI.exportReportDocx()" style="font-weight:700;">
            📝 Xuất Báo Cáo Word (.docx)
          </button>
        </div>

        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(180px, 1fr)); gap:12px; margin-bottom:20px;">
          <div style="background:rgba(255,255,255,0.04); padding:12px; border-radius:10px; border:1px solid rgba(255,255,255,0.08);">
            <div style="font-size:11px; color:#94a3b8;">Tổng Mẫu Khảo Sát</div>
            <div style="font-size:16px; font-weight:800; color:#f8fafc; margin-top:2px;">${data.total_points} mẫu</div>
          </div>
          <div style="background:rgba(255,255,255,0.04); padding:12px; border-radius:10px; border:1px solid rgba(255,255,255,0.08);">
            <div style="font-size:11px; color:#94a3b8;">Số Điểm Bất Thường</div>
            <div style="font-size:16px; font-weight:800; color:#f87171; margin-top:2px;">${data.anomaly_points_count} (${data.anomaly_rate})</div>
          </div>
          <div style="background:rgba(255,255,255,0.04); padding:12px; border-radius:10px; border:1px solid rgba(255,255,255,0.08);">
            <div style="font-size:11px; color:#94a3b8;">Khoảng Chấp Nhận Hợp Lệ</div>
            <div style="font-size:14px; font-weight:700; color:#34d399; margin-top:2px;">[${data.acceptable_bounds.lower}, ${data.acceptable_bounds.upper}]</div>
          </div>
        </div>

        ${data.anomaly_points_count > 0 ? `
          <div style="overflow-x:auto; margin-bottom:20px;">
            <table style="width:100%; border-collapse:collapse; text-align:left;">
              <thead>
                <tr style="background:rgba(0,0,0,0.4); color:#94a3b8; font-size:12px;">
                  <th style="padding:8px 10px;">Mẫu / Trạm</th>
                  <th style="padding:8px 10px;">Giá Trị Đo Được</th>
                  <th style="padding:8px 10px;">Độ Lệch Z-score</th>
                  <th style="padding:8px 10px;">Xác Suất Dị Biệt</th>
                  <th style="padding:8px 10px;">Phân Loại</th>
                  <th style="padding:8px 10px;">Ngưỡng Hợp Lệ</th>
                </tr>
              </thead>
              <tbody>${anomRows}</tbody>
            </table>
          </div>
        ` : `
          <div style="padding:14px; background:rgba(16,185,129,0.1); border:1px solid #10b981; border-radius:8px; color:#6ee7b7; font-size:13px; margin-bottom:16px;">
            ✅ Tuyệt vời! Không phát hiện điểm dị biệt nào trong tập dữ liệu. Toàn bộ số liệu đều nằm trong khoảng phân bố chuẩn 95%.
          </div>
        `}

        <div style="background:rgba(239,68,68,0.08); border-left:4px solid #ef4444; border-radius:0 10px 10px 0; padding:16px; margin-bottom:18px;">
          <h5 style="color:#f87171; font-size:13.5px; margin:0 0 6px 0; font-weight:700;">🎓 Giải Trình Khoa Học & Khuyến Nghị Xử Lý:</h5>
          <p style="font-size:13px; color:#e2e8f0; line-height:1.7; margin:0;">${data.academic_explanation}</p>
        </div>
      </div>
    `;

    box.scrollIntoView({ behavior: 'smooth' });
  }

  // ══════════════════════════════════════════════════════════════════════
  // 3. CHẠY PHÂN TÍCH ĐỘNG LỰC CỐT LÕI (AI.KEY_DRIVERS)
  // ══════════════════════════════════════════════════════════════════════
  async function runKeyDrivers() {
    if (!_loadedDataset || !_loadedDataset.all_data || _loadedDataset.all_data.length < 5) {
      if (window.App) App.toast("Vui lòng nạp tệp dữ liệu đa biến (tối thiểu 5 mẫu) hoặc chọn Dữ Liệu Mẫu.", "warning");
      return;
    }

    const targetKey = document.getElementById('bq-kd-target-col')?.value || 'efficiency';
    const topic = document.getElementById('bq-drivers-topic')?.value || 'Phân Tích Tương Quan Đa Biến';

    const btn = document.getElementById('bq-btn-run-drivers');
    if (btn) btn.innerHTML = "⏳ Đang phân tích BigQuery AI.KEY_DRIVERS...";

    try {
      const res = await fetch('/api/bigquery/key-drivers', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...((window.AuthManager && AuthManager.token) ? { 'Authorization': `Bearer ${AuthManager.token}` } : {})
        },
        body: JSON.stringify({
          data_points: _loadedDataset.all_data,
          target_key: targetKey,
          topic: topic
        })
      });
      const data = await res.json();
      if (data.status === 'success') {
        _lastAnalysisResult = data;
        _lastAnalysisType = 'key_drivers';
        _renderKeyDriversResult(data);
        if (window.App) App.toast("Phân tích động lực cốt lõi thành công!", "success");
      } else {
        if (window.App) App.toast(data.message || "Lỗi phân tích", "error");
      }
    } catch (e) {
      if (window.App) App.toast("Lỗi kết nối: " + e.message, "error");
    } finally {
      if (btn) btn.innerHTML = "🔑 Chạy Phân Tích Động Lực AI.KEY_DRIVERS";
    }
  }

  function _renderKeyDriversResult(data) {
    const box = document.getElementById('bq-analysis-output-container');
    if (!box) return;
    box.style.display = 'block';

    let driverRows = data.drivers_ranked.map((dr, rank) => `
      <tr style="border-bottom:1px solid rgba(255,255,255,0.06); font-size:12.5px;">
        <td style="padding:8px 10px; font-weight:800; color:#38bdf8;">#${rank + 1}</td>
        <td style="padding:8px 10px; font-weight:700; color:#f8fafc;">${dr.driver_name}</td>
        <td style="padding:8px 10px; color:#cbd5e1;">${dr.correlation_coefficient}</td>
        <td style="padding:8px 10px;">
          <div style="display:flex; align-items:center; gap:8px;">
            <div style="flex:1; background:rgba(255,255,255,0.1); height:8px; border-radius:4px; overflow:hidden;">
              <div style="width:${dr.importance_score}%; background:linear-gradient(90deg, #3b82f6, #8b5cf6); height:100%;"></div>
            </div>
            <strong style="color:#a855f7; font-size:12px;">${dr.importance_score}%</strong>
          </div>
        </td>
        <td style="padding:8px 10px; color:#34d399;">${dr.impact_direction}</td>
        <td style="padding:8px 10px; color:#fde68a; font-size:11.5px;">${dr.significance}</td>
      </tr>
    `).join('');

    box.innerHTML = `
      <div style="background:#0f172a; border:1px solid #8b5cf6; border-radius:14px; padding:22px; margin-top:20px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; flex-wrap:wrap; gap:10px;">
          <div>
            <span style="background:rgba(139,92,246,0.2); color:#c084fc; padding:3px 10px; border-radius:12px; font-size:11.5px; font-weight:700;">
              🔑 PHÂN TÍCH ĐỘNG LỰC CỐT LÕI (BIGQUERY AI.KEY_DRIVERS)
            </span>
            <h3 style="font-size:17px; font-weight:800; color:#f8fafc; margin:6px 0 0 0;">${data.topic}</h3>
          </div>
          <button type="button" class="btn btn-primary btn-sm" onclick="BigQueryMLUI.exportReportDocx()" style="font-weight:700;">
            📝 Xuất Báo Cáo Word (.docx)
          </button>
        </div>

        <div style="margin-bottom:18px;">
          <table style="width:100%; border-collapse:collapse; text-align:left;">
            <thead>
              <tr style="background:rgba(0,0,0,0.4); color:#94a3b8; font-size:12px;">
                <th style="padding:8px 10px; width:40px;">#</th>
                <th style="padding:8px 10px;">Tên Biến / Nhân Tố</th>
                <th style="padding:8px 10px;">Hệ Số Tương Quan (r)</th>
                <th style="padding:8px 10px; width:180px;">Mức Độ Đóng Góp (%)</th>
                <th style="padding:8px 10px;">Chiều Hướng</th>
                <th style="padding:8px 10px;">Ý Nghĩa Thống Kê</th>
              </tr>
            </thead>
            <tbody>${driverRows}</tbody>
          </table>
        </div>

        <div style="background:rgba(139,92,246,0.08); border-left:4px solid #8b5cf6; border-radius:0 10px 10px 0; padding:16px; margin-bottom:18px;">
          <h5 style="color:#c084fc; font-size:13.5px; margin:0 0 6px 0; font-weight:700;">🎓 Luận Giải Tương Quan Thực Nghiệm (Key Drivers Discussion):</h5>
          <p style="font-size:13px; color:#e2e8f0; line-height:1.7; margin:0;">${data.academic_explanation}</p>
        </div>
      </div>
    `;

    box.scrollIntoView({ behavior: 'smooth' });
  }

  // ══════════════════════════════════════════════════════════════════════
  // 4. TRỢ LÝ SINH BIGQUERY SQL (NL2SQL)
  // ══════════════════════════════════════════════════════════════════════
  async function generateSQL() {
    const prompt = document.getElementById('bq-sql-prompt')?.value?.trim();
    const schema = document.getElementById('bq-sql-schema')?.value?.trim();
    if (!prompt) {
      if (window.App) App.toast("Vui lòng nhập câu hỏi hoặc yêu cầu phân tích.", "warning");
      return;
    }

    const btn = document.getElementById('bq-btn-gen-sql');
    if (btn) btn.innerHTML = "⏳ Đang thiết kế câu lệnh BigQuery SQL AI...";

    try {
      const res = await fetch('/api/bigquery/generate-sql', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...((window.AuthManager && AuthManager.token) ? { 'Authorization': `Bearer ${AuthManager.token}` } : {})
        },
        body: JSON.stringify({
          prompt: prompt,
          schema_context: schema
        })
      });
      const data = await res.json();
      if (data.status === 'success') {
        const outBox = document.getElementById('bq-sql-output');
        if (outBox) {
          outBox.style.display = 'block';
          outBox.innerHTML = `
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
              <span style="color:#60a5fa; font-weight:700; font-size:13px;">💻 Câu Lệnh BigQuery SQL Chuẩn Google:</span>
              <button type="button" class="btn btn-secondary btn-sm" onclick="navigator.clipboard.writeText(document.getElementById('bq-sql-code').innerText); App.toast('Đã sao chép SQL!', 'success');" style="font-size:11px;">📋 Sao Chép SQL</button>
            </div>
            <pre id="bq-sql-code" style="background:#020617; border:1px solid rgba(255,255,255,0.1); border-radius:8px; padding:14px; font-family:monospace; color:#38bdf8; font-size:12.5px; overflow-x:auto; margin-bottom:14px;">${data.sql_query}</pre>
            <div style="background:rgba(255,255,255,0.03); padding:12px; border-radius:8px; font-size:12.5px; color:#cbd5e1; line-height:1.6;">
              <strong style="color:#fde68a;">📖 Giải Thích Kỹ Thuật:</strong><br>${data.explanation}
              ${data.estimated_cost_note ? `<div style="margin-top:6px; color:#94a3b8; font-size:11.5px;">💡 <em>${data.estimated_cost_note}</em></div>` : ''}
            </div>
          `;
        }
        if (window.App) App.toast("Sinh câu lệnh BigQuery SQL thành công!", "success");
      }
    } catch (e) {
      if (window.App) App.toast("Lỗi sinh SQL: " + e.message, "error");
    } finally {
      if (btn) btn.innerHTML = "✨ Chuyển Đổi Thành BigQuery SQL";
    }
  }

  // ══════════════════════════════════════════════════════════════════════
  // XUẤT BẢN FILE WORD BÁO CÁO
  // ══════════════════════════════════════════════════════════════════════
  async function exportReportDocx() {
    if (!_lastAnalysisResult || !_lastAnalysisType) {
      if (window.App) App.toast("Chưa có kết quả phân tích để xuất bản.", "warning");
      return;
    }

    try {
      const res = await fetch('/api/bigquery/export-docx', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...((window.AuthManager && AuthManager.token) ? { 'Authorization': `Bearer ${AuthManager.token}` } : {})
        },
        body: JSON.stringify({
          analysis_type: _lastAnalysisType,
          result_data: _lastAnalysisResult,
          topic: _lastAnalysisResult.topic || "Phân Tích Dữ Liệu Lớn BigQuery"
        })
      });
      const data = await res.json();
      if (data.status === 'success') {
        if (window.App) {
          App.toast(data.message || "Xuất bản file Word thành công!", "success");
          if (App.openFileInSystem && data.rel_path) {
            App.openFileInSystem(data.rel_path);
          }
        }
      } else {
        if (window.App) App.toast(data.message || "Lỗi xuất bản file", "error");
      }
    } catch (e) {
      if (window.App) App.toast("Lỗi xuất bản: " + e.message, "error");
    }
  }

  return {
    init,
    switchSubtab,
    loadSamplePreset,
    uploadDataset,
    runForecast,
    runAnomalyDetection,
    runKeyDrivers,
    generateSQL,
    exportReportDocx
  };
})();

// Auto-init on DOMContentLoaded
document.addEventListener('DOMContentLoaded', () => {
  BigQueryMLUI.init();
});
