# 📁 KHÔNG GIAN LÀM VIỆC (WORKSPACE) & LỊCH SỬ THAO TÁC (HISTORY PRO)

## 🎯 VỊ TRÍ & ĐẶC TẢ MODULE
- **Giao diện:** Tab Workspace (`#workspace-tab`), Tab Lịch Sử (`#history-tab`).
- **File Frontend:** `static/js/document-editor.js`, `static/js/history.js`, `static/js/pdf-ocr-reader.js`
- **File Backend:** `modules/workspace/docx_editor_engine.py`, `modules/workspace/workspace_router.py`, `modules/history/history_manager.py`, `modules/shared/file_manager.py`, `modules/shared/pdf_ocr_engine.py`

## 🔗 QUY TRÌNH LIÊN KẾT LIÊN THÔNG (INTERLINK PROTOCOL)
- **Đầu vào (Input Tiếp Nhận):**
  - Nhận toàn bộ tệp kết xuất (DOCX, PDF, JSON, PNG) và thông tin thao tác từ **TẤT CẢ các phân hệ nghiên cứu**.
- **Xử lý Lưu trữ & Quản Trị:**
  - Workspace: Trình đọc tài liệu trực quan, chỉnh sửa In-Place DOM Word (.docx), bộ công cụ PDF Document AI OCR, mở trực tiếp folder trong Windows Explorer.
  - History: Ghi nhận Audit Log chi tiết, hỗ trợ 2 chế độ hiển thị (Theo Phiên Session Mode / Toàn bộ Flat Mode), tìm kiếm, lọc theo module, khôi phục dữ liệu và chọn hàng loạt (Bulk Actions).
- **Đầu ra (Output Bàn Giao Liên Thông):**
  - ➔ **Cung cấp cho Người dùng:** Trích xuất báo cáo lịch sử và tải về tệp tin nghiên cứu hoàn chỉnh bất kỳ lúc nào.

## ⚖️ TUÂN THỦ 4 QUY TẮC BẤT BIẾN & ĐẠO ĐỨC NGHIÊN CỨU
1. **Evidence First & Zero Fabrication:** Lưu trữ nguyên bản 100% dữ liệu lịch sử thao tác.
2. **In-Place DOM Word (.docx):** Bảo toàn tệp Word trong Workspace.
3. **Chuẩn hóa số thập phân tiếng Việt:** Hiển thị trong bảng thống kê lịch sử.
4. **Chuẩn hóa hóa học & toán học:** Bảo toàn trong nhật ký.

## 📝 NHẬT KÝ YÊU CẦU & KẾT QUẢ XỬ LÝ
- **Yêu cầu 1:** Tự động ghi nhật ký lịch sử cho tất cả các thao tác nghiên cứu.
  - *Kết quả:* Đã tích hợp `history_mgr.add_entry()` trên toàn bộ các router backend.
- **[2026-08-25 11:18] Yêu cầu 2:** Cô lập lịch sử theo từng tài khoản (`history_{email}.json` và `sessions_{email}.json`), khắc phục triệt để việc nhìn thấy lịch sử tài khoản khác.
- **Yêu cầu 3 (2026-08-26):** Bổ sung chức năng đọc tệp Word (.docx) để bóc tách cấu trúc, trực tiếp chỉnh sửa nội dung văn bản và số liệu định lượng (Tables & Metrics Matrix) trong tài liệu được tải lên hoặc có sẵn trong Workspace.
  - *Kết quả:*
    - Xây dựng `modules/workspace/docx_editor_engine.py` với các hàm `parse_docx()`, `save_edited_docx()`, `batch_replace_in_docx()`.
    - Bổ sung 4 REST endpoints trong `modules/workspace/workspace_router.py`:
      - `POST /api/files/docx/upload-and-parse`: Nạp file Word từ máy tính và bóc tách tự động các đoạn văn, bảng biểu, danh mục số liệu/chỉ số định lượng.
      - `GET /api/files/docx/parse`: Đọc file .docx có sẵn trong Workspace.
      - `POST /api/files/docx/save`: Lưu nội dung & bảng số liệu đã sửa với chuẩn hóa In-Place DOM Word 100%.
      - `POST /api/files/docx/batch-replace`: Tìm và thay thế hàng loạt số liệu/thuật ngữ trong toàn bộ tệp Word.
    - Cập nhật giao diện `static/js/document-editor.js` và `static/index.html` với 3 chế độ: Soạn thảo văn bản, Hiệu chỉnh bảng & số liệu, Tìm & thay thế hàng loạt.
- **Yêu cầu 4 (2026-08-26):** Bổ sung chức năng đọc file PDF thông minh theo chuẩn AI OCR chuyên dụng (`abbyy/JFK-OCR` model):
  - *Kết quả:*
    - Xây dựng `modules/shared/pdf_ocr_engine.py` (Purpose-Built Document AI OCR Engine: Fast Native, Gemini Multimodal Vision AI, ABBYY Vantage, RAG Semantic Chunking).
    - Tích hợp 5 REST endpoints trong `modules/workspace/workspace_router.py`:
      - `POST /api/pdf-ocr/inspect`: Đánh giá lớp chữ PDF (Digital Searchable vs Scanned Image vs Hybrid).
      - `POST /api/pdf-ocr/upload-and-process`: Upload và OCR tự động tạo Searchable Markdown + Grid Tables + RAG Chunks.
      - `POST /api/pdf-ocr/process`: Xử lý OCR trên file PDF trong Workspace.
      - `POST /api/pdf-ocr/export-docx`: Xuất kết quả OCR sang Word .docx chuẩn In-Place DOM 300 DPI.
      - `POST /api/pdf-ocr/ingest-to-notebook`: Nạp 1-click toàn văn OCR vào Open-Notebook.
    - Bổ sung nút bấm và giao diện Studio `static/js/pdf-ocr-reader.js` tại `#workspace-tab`.
- **Yêu cầu 5 (2026-08-26 - Milestone M2 DOM Preservation):** Hoàn thiện tương thích In-Place DOM giữa `DocxEditorEngine` và `DocxStyler`.
  - *Kết quả:*
    - Bổ sung đầy đủ 6 class methods (`apply_document_styles`, `add_heading_1`, `add_heading_2`, `add_heading_3`, `add_paragraph`, `add_styled_table`) vào `DocxStyler`, xử lý triệt để lỗi `AttributeError` khi lưu file trong Workspace.
    - Cải tiến `batch_replace_in_docx` sử dụng `replace_text_in_paragraph_runs`, bảo toàn 100% font chữ, in đậm, in nghiêng, màu sắc và cấu trúc XML trong từng đoạn văn và bảng biểu.
- **Yêu cầu 6 (2026-08-26 - Multi-Agent & E2E Validation):**
  - *Kết quả:* Đạt kết quả **100% PASS** trên toàn bộ các bài test `test_docx_editor_engine.py` (10/10 tests PASS) và `test_pdf_ocr_full_flow.py` (11/11 tests PASS).
- **Yêu cầu 7 (2026-08-27 - Milestone M4 UI/UX Route Fixes & Snapshot Packaging):**
  - *Kết quả:*
    - Khắc phục lỗi đường dẫn trong `static/js/pdf-ocr-reader.js:287` chuyển từ `/api/open-notebook/list` sang `/api/notebooklm/notebooks`.
    - Bổ sung alias route `@notebooklm_router.get("/api/open-notebook/list")` trong `modules/notebooklm/notebooklm_router.py` đảm bảo tương thích ngược 100%.
    - Nâng cấp công cụ `Xac_Nhan_Hoan_Hao/archive_manager.py` với danh mục `VERIFIED_MODULES_CATALOG` và đóng gói 6 module hoàn chỉnh (Harvester, Zotero Converter, Math-Chem Pro, BigQuery AI, PDF OCR Workspace, Open-Notebook RAG) vào `Xac_Nhan_Hoan_Hao/Modules_Source_Code/` có kèm file `manifest.json`.
    - Toàn bộ 170 nút bấm và 101 lời gọi API Frontend khớp nối chính xác 100% với Backend routes.
- **Yêu cầu 8 (2026-09-07 - Tối ưu hóa điều khiển nút bấm & Tinh gọn tương tác toàn diện):**
  - *Kết quả:*
    - Khắc phục triệt để nguy cơ `TypeError` trong `App.openWindowsExplorer()` bằng chuỗi optional chaining `?.value?.trim()` tại `static/js/app.js`.
    - Bổ sung hàm `App.closeSettingsModal()` và gắn trực tiếp `onclick="App.closeSettingsModal()"` vào các nút `✕` và `Hủy` trong `#modal-settings`.
    - Thêm endpoint alias `@workspace_router.get("/api/files/download/{file_path:path}")` trong `modules/workspace/workspace_router.py` để tải tệp theo cả hai chuẩn path parameter và query string.
    - Hoàn thiện thẻ Tệp B (Ma trận 6 cột) với đầy đủ bộ 3 nút bấm mở file Word, tải .docx, tải .md trong `static/js/academic-writer.js`.
    - Trang bị cơ chế chống spam click (`disabled = true` + spinner phản hồi lập tức) cho tất cả các nút BigQuery AI/ML và Math-Chem Pro.
- **Yêu cầu 9 (2026-09-07 - Khắc phục điểm nghẽn xóa bản ghi lịch sử & đồng bộ hóa ID tương tác):**
  - *Kết quả:*
    - Bổ sung endpoint RESTful `@history_router.delete("/api/history/{entry_id}")` trong `modules/history/history_router.py`, kết nối trực tiếp với `history_mgr.delete_entry(entry_id, user_email)` để người dùng xóa từng bản ghi hoạt động cá nhân nhanh chóng mà không gặp lỗi 404/405.
    - Bổ sung định danh `id="pdf-ocr-btn-export-docx"` và `id="pdf-ocr-btn-ingest"` trong modal PDF Document AI OCR, trang bị cơ chế chống double-click (`btn.disabled = true` + spinner phản hồi lập tức) trong `static/js/pdf-ocr-reader.js`.


