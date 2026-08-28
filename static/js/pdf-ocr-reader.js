/**
 * WEB SUPER v3.2 / v2.0 — Intelligent PDF Document AI & OCR Reader
 * Inspired by abbyy/JFK-OCR: Purpose-Built AI OCR, Searchable Text Layer Reconstruction, and RAG Semantic Chunking.
 */

const PdfOcrUI = (() => {
  let _currentFile = null;
  let _currentRelPath = null;
  let _ocrResult = null;
  let _notebooksList = [];

  function _getHeaders(isJson = false) {
    const headers = {};
    if (isJson) headers['Content-Type'] = 'application/json';
    if (window.AuthManager && AuthManager.token) {
      headers['Authorization'] = `Bearer ${AuthManager.token}`;
    }
    return headers;
  }

  function openModal(defaultRelPath = null) {
    const modal = document.getElementById('modal-pdf-ocr');
    if (!modal) return;
    modal.classList.add('active');
    modal.style.display = 'flex';

    _resetState();

    if (defaultRelPath) {
      _currentRelPath = defaultRelPath;
      document.getElementById('pdf-ocr-file-name').textContent = `📁 ${defaultRelPath}`;
      document.getElementById('pdf-ocr-file-info').style.display = 'block';
      _inspectPath(defaultRelPath);
    }
  }

  function closeModal() {
    const modal = document.getElementById('modal-pdf-ocr');
    if (!modal) return;
    modal.classList.remove('active');
    modal.style.display = 'none';
  }

  function _resetState() {
    _currentFile = null;
    _currentRelPath = null;
    _ocrResult = null;
    document.getElementById('pdf-ocr-file-input').value = '';
    document.getElementById('pdf-ocr-file-info').style.display = 'none';
    document.getElementById('pdf-ocr-inspect-badge').innerHTML = '';
    document.getElementById('pdf-ocr-results-panel').style.display = 'none';
    document.getElementById('pdf-ocr-loading').style.display = 'none';
    document.getElementById('pdf-ocr-btn-run').disabled = true;
  }

  function handleFileSelected(e) {
    const file = e.target.files[0];
    if (!file) return;
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      if (window.App) App.toast('Vui lòng chọn tệp định dạng .pdf', 'warning');
      return;
    }

    _currentFile = file;
    _currentRelPath = null;

    document.getElementById('pdf-ocr-file-name').textContent = `📄 ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
    document.getElementById('pdf-ocr-file-info').style.display = 'block';
    document.getElementById('pdf-ocr-inspect-badge').innerHTML = `<span class="badge badge-info">🔄 Đang nạp tệp...</span>`;
    document.getElementById('pdf-ocr-btn-run').disabled = false;
  }

  async function _inspectPath(relPath) {
    document.getElementById('pdf-ocr-inspect-badge').innerHTML = `<span class="badge badge-info">🔍 Đang phân tích lớp chữ...</span>`;
    try {
      const r = await fetch('/api/pdf-ocr/inspect', {
        method: 'POST',
        headers: _getHeaders(true),
        body: JSON.stringify({ rel_path: relPath })
      });
      if (r.ok) {
        const data = await r.json();
        _renderInspection(data);
        document.getElementById('pdf-ocr-btn-run').disabled = false;
      } else {
        document.getElementById('pdf-ocr-inspect-badge').innerHTML = `<span class="badge badge-warning">Không thể kiểm tra lớp chữ</span>`;
      }
    } catch (e) {
      document.getElementById('pdf-ocr-inspect-badge').innerHTML = `<span class="badge badge-warning">Lỗi kiểm tra</span>`;
    }
  }

  function _renderInspection(data) {
    const badgeEl = document.getElementById('pdf-ocr-inspect-badge');
    if (data.status !== 'success') return;

    let badgeClass = 'badge-success';
    let icon = '📖';
    if (data.doc_type === 'SCANNED_IMAGE_ONLY') {
      badgeClass = 'badge-warning';
      icon = '🖼️';
    } else if (data.doc_type === 'HYBRID_DEGRADED') {
      badgeClass = 'badge-info';
      icon = '📑';
    }

    badgeEl.innerHTML = `
      <span class="badge ${badgeClass}" style="font-size:12px; padding:4px 10px;">
        ${icon} ${data.doc_type_label} | ${data.total_pages} trang | ~${data.avg_chars_per_page} ký tự/trang
      </span>
    `;

    const modeSelect = document.getElementById('pdf-ocr-mode-select');
    if (modeSelect) {
      modeSelect.value = data.recommended_mode || 'auto';
    }
  }

  async function runOcr() {
    if (!_currentFile && !_currentRelPath) {
      if (window.App) App.toast('Vui lòng chọn hoặc kéo thả một tệp PDF.', 'warning');
      return;
    }

    const mode = document.getElementById('pdf-ocr-mode-select').value || 'auto';
    const maxPages = parseInt(document.getElementById('pdf-ocr-max-pages').value || '30', 10);
    const topicHint = document.getElementById('pdf-ocr-topic-hint').value.trim();

    document.getElementById('pdf-ocr-loading').style.display = 'block';
    document.getElementById('pdf-ocr-results-panel').style.display = 'none';
    document.getElementById('pdf-ocr-btn-run').disabled = true;

    try {
      let r, data;
      if (_currentFile) {
        const formData = new FormData();
        formData.append('file', _currentFile);
        const url = `/api/pdf-ocr/upload-and-process?mode=${encodeURIComponent(mode)}&max_pages=${maxPages}&topic_hint=${encodeURIComponent(topicHint)}`;
        r = await fetch(url, {
          method: 'POST',
          headers: _getHeaders(false),
          body: formData
        });
      } else {
        r = await fetch('/api/pdf-ocr/process', {
          method: 'POST',
          headers: _getHeaders(true),
          body: JSON.stringify({
            rel_path: _currentRelPath,
            mode: mode,
            max_pages: maxPages,
            topic_hint: topicHint
          })
        });
      }

      if (!r.ok) {
        const err = await r.json().catch(() => ({ detail: 'Lỗi không xác định' }));
        throw new Error(err.detail || 'Lỗi xử lý OCR');
      }

      data = await r.json();
      _ocrResult = data;
      _renderOcrResult(data);

      if (window.App) App.toast(`✅ Đã bóc tách thành công ${data.total_pages} trang (${data.total_words} từ)!`, 'success');
    } catch (e) {
      if (window.App) App.toast(`Lỗi OCR: ${e.message}`, 'error');
    } finally {
      document.getElementById('pdf-ocr-loading').style.display = 'none';
      document.getElementById('pdf-ocr-btn-run').disabled = false;
    }
  }

  function _renderOcrResult(data) {
    document.getElementById('pdf-ocr-results-panel').style.display = 'block';

    document.getElementById('pdf-ocr-stats-pills').innerHTML = `
      <span class="badge badge-info">📄 ${data.total_pages} Trang</span>
      <span class="badge badge-success">🔤 ${(data.total_words || 0).toLocaleString('vi-VN')} Từ</span>
      <span class="badge badge-warning">🤖 ${data.ocr_pages_count || 0} Trang AI OCR</span>
      <span class="badge badge-info">📊 ${data.total_tables || 0} Bảng Số Liệu</span>
      <span class="badge badge-success">🧩 ${data.rag_chunks_count || 0} RAG Chunks</span>
      <span class="badge badge-info">⏱️ ${data.elapsed_seconds || 0}s</span>
    `;

    const txtArea = document.getElementById('pdf-ocr-text-content');
    if (txtArea) {
      txtArea.value = data.full_markdown || '';
    }

    const tablesContainer = document.getElementById('pdf-ocr-tables-list');
    if (tablesContainer) {
      if (!data.tables || data.tables.length === 0) {
        tablesContainer.innerHTML = `<div style="color:#94a3b8; font-style:italic; padding:12px;">Không phát hiện bảng số liệu riêng biệt trong tài liệu.</div>`;
      } else {
        tablesContainer.innerHTML = data.tables.map((t, idx) => `
          <div style="background:rgba(15,23,42,0.6); border:1px solid rgba(59,130,246,0.3); border-radius:8px; padding:14px; margin-bottom:12px;">
            <div style="font-weight:700; color:#38bdf8; margin-bottom:8px;">📊 Bảng ${idx + 1} (${t.headers.length} cột, ${t.rows.length} hàng)</div>
            <div style="overflow-x:auto;">
              <table style="width:100%; border-collapse:collapse; font-size:12px;">
                <thead>
                  <tr style="background:rgba(59,130,246,0.2);">
                    ${t.headers.map(h => `<th style="padding:6px 10px; border:1px solid rgba(148,163,184,0.2); text-align:left; color:#f8fafc;">${h}</th>`).join('')}
                  </tr>
                </thead>
                <tbody>
                  ${t.rows.map(r => `
                    <tr>
                      ${r.map(c => `<td style="padding:6px 10px; border:1px solid rgba(148,163,184,0.15); color:#e2e8f0;">${c}</td>`).join('')}
                    </tr>
                  `).join('')}
                </tbody>
              </table>
            </div>
          </div>
        `).join('');
      }
    }

    const chunksContainer = document.getElementById('pdf-ocr-chunks-list');
    if (chunksContainer) {
      chunksContainer.innerHTML = (data.rag_chunks || []).map(c => `
        <div style="background:rgba(15,23,42,0.5); border-left:3px solid #38bdf8; padding:10px 14px; margin-bottom:10px; border-radius:0 8px 8px 0;">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
            <strong style="color:#60a5fa; font-size:12.5px;">📍 ${c.section_heading}</strong>
            <span style="font-size:11px; color:#94a3b8; font-family:monospace;">${c.citation_anchor} · ~${c.token_count_est} tokens</span>
          </div>
          <div style="font-size:12px; color:#cbd5e1; line-height:1.5;">${c.content}</div>
        </div>
      `).join('');
    }

    switchTab('text');
  }

  function switchTab(tabKey) {
    const tabs = ['text', 'tables', 'chunks'];
    tabs.forEach(t => {
      const btn = document.getElementById(`pdf-ocr-tab-btn-${t}`);
      const pane = document.getElementById(`pdf-ocr-tab-pane-${t}`);
      if (btn) btn.classList.toggle('active', t === tabKey);
      if (pane) pane.style.display = t === tabKey ? 'block' : 'none';
    });
  }

  async function exportDocx() {
    if (!_ocrResult) {
      if (window.App) App.toast('Chưa có kết quả OCR để xuất Word.', 'warning');
      return;
    }

    try {
      if (window.App) App.toast('Đang định dạng tệp Word In-Place DOM 300 DPI...', 'info');
      const r = await fetch('/api/pdf-ocr/export-docx', {
        method: 'POST',
        headers: _getHeaders(true),
        body: JSON.stringify({ ocr_result: _ocrResult })
      });

      if (!r.ok) throw new Error('Lỗi xuất bản Word .docx');
      const data = await r.json();

      if (data.status === 'success') {
        if (window.App) App.toast(`✅ Đã xuất tệp Word: ${data.docx_file}`, 'success');
        window.open(`/api/files/download?path=${encodeURIComponent(data.docx_file)}`, '_blank');
      }
    } catch (e) {
      if (window.App) App.toast(`Lỗi xuất Word: ${e.message}`, 'error');
    }
  }

  function copyMarkdown() {
    const txtArea = document.getElementById('pdf-ocr-text-content');
    if (!txtArea || !txtArea.value) return;
    navigator.clipboard.writeText(txtArea.value);
    if (window.App) App.toast('📋 Đã sao chép toàn bộ văn bản Markdown vào Clipboard!', 'success');
  }

  async function openIngestModal() {
    if (!_ocrResult) {
      if (window.App) App.toast('Chưa có dữ liệu OCR để nạp vào Kho Tri Thức.', 'warning');
      return;
    }

    try {
      const r = await fetch('/api/notebooklm/notebooks', { headers: _getHeaders(true) });
      if (r.ok) {
        const data = await r.json();
        _notebooksList = data.notebooks || [];
      }
    } catch (e) {
      _notebooksList = [];
    }

    if (_notebooksList.length === 0) {
      if (window.App) App.toast('Bạn chưa có Notebook nào trong Kho Tri Thức. Hãy tạo Notebook trước.', 'warning');
      return;
    }

    const selectHtml = _notebooksList.map(n => `<option value="${n.id}">${n.name} (${n.topic || 'Chung'})</option>`).join('');
    const modalHtml = `
      <div id="modal-ocr-ingest" class="modal active" style="display:flex; position:fixed; inset:0; z-index:10002; background:rgba(0,0,0,0.7); backdrop-filter:blur(4px); align-items:center; justify-content:center; padding:20px;">
        <div style="background:#111827; border:1px solid rgba(59,130,246,0.4); border-radius:16px; padding:24px; max-width:480px; width:100%; box-shadow:0 24px 64px rgba(0,0,0,0.7);">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
            <h3 style="font-size:16px; font-weight:700; color:#f8fafc; margin:0;">🧠 Nạp Vào Kho Tri Thức (Open-Notebook)</h3>
            <button onclick="document.getElementById('modal-ocr-ingest').remove()" style="background:none; border:none; color:#94a3b8; font-size:18px; cursor:pointer;">✕</button>
          </div>
          <p style="font-size:13px; color:#cbd5e1; line-height:1.5; margin-bottom:16px;">
            Tài liệu đã OCR sẽ được nạp trực tiếp vào Notebook làm nguồn RAG với đầy đủ trích dẫn phân đoạn.
          </p>
          <div style="margin-bottom:20px;">
            <label style="display:block; font-size:12.5px; font-weight:600; color:#94a3b8; margin-bottom:6px;">Chọn Notebook đích:</label>
            <select id="select-target-notebook-id" style="width:100%; padding:10px 12px; background:rgba(255,255,255,0.06); border:1px solid var(--border-color); border-radius:8px; color:#f8fafc; font-size:13px;">
              ${selectHtml}
            </select>
          </div>
          <div style="display:flex; justify-content:flex-end; gap:10px;">
            <button onclick="document.getElementById('modal-ocr-ingest').remove()" class="btn btn-secondary">Hủy</button>
            <button onclick="PdfOcrUI.executeIngest()" class="btn btn-primary">🚀 Nạp Ngay</button>
          </div>
        </div>
      </div>
    `;

    const oldM = document.getElementById('modal-ocr-ingest');
    if (oldM) oldM.remove();
    document.body.insertAdjacentHTML('beforeend', modalHtml);
  }

  async function executeIngest() {
    const selectEl = document.getElementById('select-target-notebook-id');
    if (!selectEl) return;
    const nbId = selectEl.value;

    const modal = document.getElementById('modal-ocr-ingest');
    if (modal) modal.remove();

    try {
      if (window.App) App.toast('Đang nạp nguồn tài liệu vào Notebook...', 'info');
      const r = await fetch('/api/pdf-ocr/ingest-to-notebook', {
        method: 'POST',
        headers: _getHeaders(true),
        body: JSON.stringify({
          ocr_result: _ocrResult,
          notebook_id: nbId
        })
      });

      if (!r.ok) throw new Error('Lỗi nạp vào Open-Notebook');
      const res = await r.json();

      if (window.App) App.toast(`🎉 Đã nạp thành công '${res.source ? res.source.title : 'Tài liệu'}' (${res.chunks_added || 0} chunks)!`, 'success');
      
      if (window.NotebookLMUI && window.NotebookLMUI.activeNotebookId === nbId) {
        window.NotebookLMUI.selectNotebook(nbId);
      }
    } catch (e) {
      if (window.App) App.toast(`Lỗi: ${e.message}`, 'error');
    }
  }

  return {
    openModal,
    closeModal,
    handleFileSelected,
    runOcr,
    switchTab,
    exportDocx,
    copyMarkdown,
    openIngestModal,
    executeIngest
  };
})();

window.PdfOcrUI = PdfOcrUI;
