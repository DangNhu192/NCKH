# 🖥️ CẤU TRÚC KIẾN TRÚC & THIẾT KẾ GIAO DIỆN HỆ THỐNG (WEB SUPER v3.2 / v2.0 UI/UX ARCHITECTURE)

> **File này lưu trữ toàn diện:**
> 1. Sơ đồ Cấu trúc Thư mục và File mã nguồn của toàn bộ dự án WEB SUPER.
> 2. Kiến trúc Giao diện Người dùng (UI/UX Layout): Cấu trúc 8 Tab nghiên cứu chính, Hệ thống Modal, Thanh điều hướng (Navbar), Thanh trạng thái (Status Bar) và Theme System.
> 3. Cơ chế ánh xạ (Mapping) giữa các thành phần Giao diện Frontend (`static/index.html`, `static/js/`, `static/css/`) và các Module Backend FastAPI (`server.py`, `modules/`).

---

## 🏗️ PHẦN I: SƠ ĐỒ CẤU TRÚC DỰ ÁN (PROJECT DIRECTORY STRUCTURE)

```text
H:\My Drive\Ho so ca nhan\b. ThS KHMT\Skill\Web Super\
│
├── server.py                                  # Cổng khởi động chính FastAPI Server (Mount routers, Middleware, Static files)
├── config.json                                # Cấu hình toàn cục mặc định (API keys, ports, models)
├── AGENTS.md                                  # Chỉ dẫn trung tâm bắt buộc cho AI Agent & Nhà phát triển
├── PROJECT.md                                 # Đặc tả kiến trúc, tiêu chuẩn chất lượng và layout dự án
├── TEST_INFRA.md                              # Khung triết lý và kiến trúc kiểm thử 4 tầng
├── TEST_READY.md                              # Biên bản bàn giao và xác nhận chất lượng test suite E2E
│
├── test_pdf_ocr_full_flow.py                  # Bộ kiểm thử E2E: PDF Document AI OCR Engine (11 tests PASS)
├── test_open_notebook_full_flow.py            # Bộ kiểm thử E2E: Kho tri thức Open-Notebook RAG Vault (10 tests PASS)
├── test_docx_editor_engine.py                 # Bộ kiểm thử E2E: Word .docx DOM Preservation & Math/Chem (10 tests PASS)
├── test_server_load.py                        # Bộ kiểm thử E2E: FastAPI Endpoints & Tải đồng thời (8 tests PASS)
├── test_worker_m1_verification.py             # Bộ kiểm thử M1: Liêm chính học thuật & Zero-Fabrication (34 tests PASS)
├── test_m2_docx_math_chem.py                  # Bộ kiểm thử M2: Word In-Place DOM & Math/Chem Engine (5 tests PASS)
│
├── docs_chuc_nang_va_chinh_sua/               # 📁 THƯ MỤC LƯU TRỮ ĐẶC TẢ & NHẬT KÝ CHỈNH SỬA TỪNG CHỨC NĂNG
│   ├── 00_TONG_QUAN_VA_MUC_LUC.md             # Mục lục danh mục tài liệu & Nguyên tắc phát triển
│   ├── 00_CAU_TRUC_VA_GIAO_DIEN_WEB_SUPER.md  # [CHÍNH LÀ FILE NÀY] Cấu trúc hệ thống & Thiết kế giao diện
│   ├── 00_MA_TRAN_QUY_TRINH_LIEN_KET_LIEN_THONG.md # Ma trận quy trình nghiên cứu liên kết liên thông
│   ├── 00_QUY_TAC_BAT_BIEN_VA_DAO_DUC_NGHIEN_CUU.md # 4 Quy tắc bất biến & Đạo đức nghiên cứu khoa học
│   ├── 01_QUY_TRINH_7_BUOC_PIPELINE.md        # Đặc tả Tab 1: Quy trình 7 Bước IMRaD & GATE
│   ├── 02_THU_THAP_TAI_LIEU_HARVESTER.md      # Đặc tả Tab 2: Thu thập tài liệu & Ảnh 300 DPI (Harvester Pro)
│   ├── 03_KHO_TRI_THUC_NOTEBOOKLM.md          # Đặc tả Tab 3: Kho tri thức & Open-Notebook RAG Vault
│   ├── 04_CHUYEN_DOI_MA_TRICH_DAN_ZOTERO.md   # Đặc tả Tab 4: Chuyển đổi mã trích dẫn Zotero trong Word
│   ├── 05_VIET_HOC_THUAT_2_FILE.md            # Đặc tả Tab 5: Viết học thuật 2-File chuẩn APA 7th & Ma trận 6 Cột
│   ├── 06_TOA_SOAN_BAO_AI_EDITORIAL_GATE.md   # Đặc tả Tab 6: Tòa soạn Báo AI 6 Ban & Chu trình 4 Trạm GATE
│   ├── 07_KHU_AI_VA_CHONG_DAO_VAN_TURNITIN.md # Đặc tả Tab 7: Khử Dấu vết AI & Chống Đạo văn Turnitin 1-Click
│   ├── 08_CHUAN_HOA_TOAN_HOA_HOC_MATH_CHEM_PRO.md # Đặc tả Tab 8: Chuẩn hóa Toán - Hóa & Ảnh 300 DPI
│   ├── 09_QUAN_LY_TAI_KHOAN_VA_AUTH_VAULT.md  # Đặc tả Tab 9 & Vault: Quản lý bản quyền & Auth Vault
│   ├── 10_WORKSPACE_VA_LICH_SU_HISTORY.md     # Đặc tả Workspace & Lịch sử thao tác
│   ├── 11_PHAN_TICH_DU_LIEU_BIGQUERY_AI_ML.md # Đặc tả Phân tích dữ liệu lớn BigQuery AI/ML & PDF OCR
│   └── tools_cross_validate_docs.py           # Công cụ kiểm tra chéo và đối soát 4 lớp tự động
│
├── auth_vault/                                # 📁 KHO LƯU TRỮ BẢO MẬT & MÃ HÓA (ISOLATED SECURITY VAULT)
│   ├── _master_vault_metadata.json            # Metadata Vault, phiên bản và Checksum SHA-256
│   ├── users_registry.vault.json              # Danh bạ người dùng, mã hóa mật khẩu PBKDF2-HMAC-SHA256
│   ├── license_keys.vault.json                # Kho License Keys kèm chữ ký số HMAC-SHA256
│   ├── profiles/                              # Thư mục chứa cấu hình riêng của từng user (user_*.vault.json)
│   │                                          # ➔ TẤT CẢ API KEYS (Gemini, OpenAI, Zotero) ĐƯỢC MÃ HÓA AES-256-CBC
│   ├── PHUONG_THUC_MA_HOA_VA_GIAI_MA.md       # Tài liệu đặc tả toán học thuật toán mã hóa / giải mã
│   └── tools_decrypt_vault.py                 # Công cụ CLI độc lập (1-Click kiểm tra, giải mã và export backup)
│
├── modules/                                   # 📁 CÁC PHÂN HỆ BACKEND (PYTHON LOGIC & FASTAPI ROUTERS)
│   ├── auth/                                  # Quản lý xác thực Google, Token JWT, Phân quyền & User Config
│   │   ├── auth_router.py                     # API: /api/auth/google, /api/auth/me, /api/config, /api/user/activate-key
│   │   ├── auth_service.py                    # Xác thực Google OAuth2 & JWT Token decode
│   │   ├── user_config_manager.py             # Quản lý đọc/ghi User Profiles & License Keys qua Auth Vault
│   │   └── vault_crypto_engine.py             # Thuật toán AES-256-CBC, PBKDF2, HMAC-SHA256
│   ├── pipeline/                              # Phân hệ Quy trình nghiên cứu 7 bước liên kết
│   │   ├── pipeline_router.py                 # API: /api/pipeline/steps, /api/pipeline/run-step, /api/pipeline/run-full
│   │   └── pipeline_engine.py                 # Logic thực thi 7 bước chuẩn IMRaD & GATE
│   ├── harvester/                             # Phân hệ Thu thập tài liệu học thuật đa nguồn
│   │   ├── harvester_router.py                # API: /api/harvest/run, /api/harvest/save-to-zotero, /api/harvest/download-pdf
│   │   └── data_harvesting_engine.py          # Trình thu thập Scholar, EuropePMC, arXiv, OpenAlex, CrossRef, Wikimedia
│   ├── notebooklm/                            # Phân hệ Kho tri thức & SciBot Semantic RAG Vault (DOI: 10.1039/D3DD00112A)
│   │   ├── notebooklm_router.py               # API: /api/notebooklm/notebooks, /api/notebooklm/notebooks/{id}/search, /api/notebooklm/literature-matrix
│   │   └── notebooklm_engine.py               # ScientificSectioner IMRaD, Okapi BM25, Multi-Scale N-Gram & Grounded Chat
│   ├── zotero/                                # Phân hệ Chuyển đổi mã trích dẫn Zotero Word (.docx)
│   │   ├── zotero_router.py                   # API: /api/zotero/convert-docx, /api/zotero/status
│   │   └── zotero_converter_engine.py        # Bộ giải mã CSL In-Place DOM và định dạng trích dẫn APA 7th, IEEE, Vancouver, Harvard
│   ├── academic_writer/                       # Phân hệ Viết học thuật RhinoInsight 2-Phase (arXiv:2511.18743)
│   │   ├── writer_router.py                   # API: /api/writer/outline/structured, /api/writer/outline/expand-branch, /api/writer/outline/add-dimension, /api/writer/outline/lock, /api/writer/generate-2file
│   │   └── academic_writer_engine.py          # Sinh Outline Tree, Phase 2 Deep Investigation, Uncertainty Flagging & Bộ đôi 2-File Word
│   ├── editorial_office/                      # Phân hệ Tòa soạn Báo AI 6 Ban & Chu trình 4 Trạm GATE
│   │   ├── editorial_router.py                # API: /api/editorial/analyze, /api/editorial/execute-gate, /api/editorial/evaluate-q1, /api/editorial/adversarial-review
│   │   └── editorial_engine.py                # Điều phối Hội đồng 6 Ban, Q1 ISI 100-point Rubric & 2-Reviewer Adversarial Peer Review
│   ├── humanizer/                             # Phân hệ Khử Dấu vết AI & Chống Đạo văn Turnitin 1-Click
│   │   ├── humanizer_router.py                # API: /api/humanize/unified-process, /api/humanize/analyze, /api/humanize/plagiarism-audit
│   │   └── humanizer_engine.py                # Bộ đo lường Burstiness, Triệt tiêu Wikipedia Signs & ContentBeta 300+
│   ├── math_chem_pro/                         # Phân hệ Chuẩn hóa Công thức Toán - Hóa Học
│   │   └── math_chem_router.py                # API: /api/math-chem/upgrade-docx, /api/math-chem/convert-math
│   ├── bigquery/                              # Phân hệ Phân tích dữ liệu lớn & BigQuery AI/ML
│   │   ├── bigquery_router.py                 # API: /api/bigquery/forecast, /api/bigquery/detect-anomalies, /api/bigquery/key-drivers
│   │   └── bigquery_engine.py                 # Mô hình hóa ARIMA_PLUS, IQR/Z-score Anomaly, Pearson Drivers, NL2SQL
│   ├── workspace/                             # Phân hệ Không gian làm việc & Soạn thảo Word
│   │   ├── workspace_router.py                # API: /api/files/docx/*, /api/pdf-ocr/*
│   │   └── docx_editor_engine.py              # Bóc tách & chỉnh sửa In-Place DOM Word (.docx)
│   ├── admin_needle/                          # Phân hệ Quản trị hệ thống, Tài khoản & License Keys
│   │   ├── admin_router.py                    # API: /api/admin/users, /api/admin/keys, /api/admin/needle/health-audit
│   │   └── admin_service.py                   # Logic kiểm tra sức khỏe hệ thống (Health Audit)
│   ├── history/                               # Phân hệ Lịch sử thao tác (Audit Log)
│   │   ├── history_router.py                  # API: /api/history/sessions, /api/history/delete
│   │   └── history_manager.py                 # Ghi nhận và truy vấn lịch sử phiên làm việc
│   └── shared/                                # 📁 CÁC THƯ VIỆN DÙNG CHUNG (SHARED SERVICES)
│       ├── gemini_service.py                  # Kết nối Google Gemini API (2.5 Pro, 2.5 Flash, 2.0 Flash) & Auto Cache
│       ├── openai_service.py                  # Kết nối OpenAI / ChatGPT API
│       ├── skill_prompts.py                   # Toàn bộ LLM Prompts chuẩn hóa (CS519.M11, ISI/Scopus, Turnitin Rephrase)
│       ├── docx_styler.py                     # Quản lý Style, Heading 1/2/3, Bảng biểu, Chuẩn hóa số thập phân tiếng Việt
│       ├── docx_formula_engine.py             # Quản lý 109 hợp chất hóa học UNICODE_CHEM_MAP & Công thức toán OMML
│       ├── docx_math_chem_styler.py           # Bộ tích hợp chuẩn hóa Toán - Hóa và nhúng đồ họa
│       ├── pdf_ocr_engine.py                  # Purpose-Built Document AI OCR Engine (Digital vs Scan, RAG Chunks, Ingest Open-Notebook)
│       ├── chart_generator.py                 # Sinh biểu đồ khoa học 300 DPI (Matplotlib)
│       └── file_manager.py                    # Quản lý tệp trong Workspace và sao lưu
│
└── static/                                    # 📁 GIAO DIỆN NGƯỜI DÙNG (FRONTEND CLIENT)
    ├── index.html                             # File HTML chính chứa toàn bộ layout các Tab, Header, Modals và Footer
    ├── css/                                   # Thư mục chứa bảng mã giao diện (Stylesheets)
    │   ├── style.css                          # CSS chính (Dark Mode, Grid layout, Typography, Buttons, Responsive)
    │   ├── modern-theme.css                   # CSS bổ sung màu sắc học thuật hiện đại
    │   ├── contrast-modes.css                 # CSS Chế độ Siêu Tương Phản (WCAG AAA)
    │   └── theme-addon.css                    # CSS cho Onboarding Guide, Modal Thanh toán và Score Gauges
    └── js/                                    # Thư mục chứa các module điều khiển JavaScript
        ├── app.js                             # Điều phối trung tâm, chuyển tab, đồng bộ Header/Footer, thông báo Toast
        ├── auth.js                            # Xử lý đăng nhập Google, quản lý Token JWT, hiển thị User Profile
        ├── pipeline.js                        # Điều khiển Giao diện Tab 1 (Quy trình 7 Bước)
        ├── harvester.js                       # Điều khiển Giao diện Tab 2 (Thu thập tài liệu & Quick Chips)
        ├── notebooklm.js                      # Điều khiển Giao diện Tab 3 (Kho tri thức Open-Notebook RAG Vault)
        ├── zotero-converter.js                # Điều khiển Giao diện Tab 4 (Kéo thả Word .docx & Chuyển đổi Zotero)
        ├── academic-writer.js                 # Điều khiển Giao diện Tab 5 (Đề xuất Dàn ý & Sinh 2-File Word)
        ├── editorial-office.js                # Điều khiển Giao diện Tab 6 (Tòa soạn Báo AI 6 Ban & GATE Workflow)
        ├── humanizer.js                       # Điều khiển Giao diện Tab 7 (Nút gộp 1-Click Khử AI/Turnitin, Đồng hồ đo chỉ số)
        ├── math-chem-pro.js                   # Điều khiển Giao diện Tab 8 (3 Chế độ nâng cấp Word .docx Toán - Hóa)
        ├── bigquery-ml.js                     # Điều khiển Giao diện Tab BigQuery AI & ML (4 Subtabs)
        ├── document-editor.js                 # Điều khiển Giao diện Workspace & Soạn thảo Word
        ├── pdf-ocr-reader.js                  # Điều khiển Giao diện Studio PDF AI OCR Reader
        ├── history.js                         # Điều khiển Giao diện Tab Lịch sử (Session / Flat mode, Bulk actions)
        ├── admin.js                           # Điều khiển Giao diện Tab 9 Quản trị viên (Danh sách User, Tạo License Key)
        ├── needle_admin.js                    # Điều khiển Kiểm toán sức khỏe hệ thống (System Health Audit)
        ├── settings.js                        # Điều khiển Modal Cài Đặt (Theme, Background, API Keys, Gemini Models)
        └── onboarding.js                      # Trợ lý hướng dẫn sử dụng từng chức năng & Modal Thanh toán
```

---

## 🎨 PHẦN II: THIẾT KẾ KIẾN TRÚC GIAO DIỆN (UI/UX ARCHITECTURE)

### 1. Bố Cục Tổng Thể (Master Layout Framework)
Giao diện Web Super được thiết kế theo cấu trúc ứng dụng học thuật một trang (Single Page Application - SPA), bao gồm 4 tầng giao diện chính:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 1. THANH TIÊU ĐỀ TRÊN CÙNG (TOP NAVIGATION BAR)                                        │
│    • Logo & Tiêu đề Web Super v3.2 / v2.0                                             │
│    • Trạng thái AI: 🟢 Google AI (Gemini 2.5 Flash 🚀) / Offline Template Engine      │
│    • Trạng thái Lưu trữ: 📁 Workspace File Count                                      │
│    • 💳 Nâng Cấp Gói · ⚙️ Cài Đặt · 👤 User Profile (Avatar Google, Tên, Gói Dịch Vụ)│
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 2. THANH ĐIỀU HƯỚNG TỪNG CHỨC NĂNG (FEATURE TABS NAVIGATION)                           │
│    [⚡ 1. Quy Trình 7 Bước]   [🌐 2. Thu Thập Tài Liệu]   [🧠 3. Kho Tri Thức]       │
│    [📚 4. Chuyển Đổi Zotero]  [🎓 5. Viết Học Thuật 2-File] [🏢 6. Tòa Soạn Báo GATE]   │
│    [✨ 7. Khử AI & Chống Turnitin (1-Click)]  [📐 8. Toán - Hóa Pro]  [👑 9. Quản Trị] │
│    [📊 BigQuery AI & ML]     [📁 Không Gian Workspace]  [📜 Lịch Sử Hoạt Động]        │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 3. KHUNG NỘI DUNG TỪNG PHÂN HỆ (DYNAMIC TAB CONTENT VIEWPORT)                          │
│    • Hiển thị nội dung tương ứng khi người dùng chuyển Tab                             │
│    • Tích hợp Kéo & Thả tệp Word (.docx) chuyên nghiệp (Drop-Zone)                     │
│    • Khung phân tích 2 cột: Cột Trái (Dữ liệu nhập / Tác vụ) - Cột Phải (Kết quả / Đồ thị)│
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 4. HỆ THỐNG CỬA SỔ BẬT (MODAL DIALOGS & OVERLAYS)                                      │
│    • Modal Cài Đặt (⚙️ Settings): Quản lý API Key, Quét mô hình Gemini, Đổi Theme       │
│    • Modal Nâng Cấp Gói (💳 Payment): Bảng 4 gói dịch vụ, Mã QR Momo/ZaloPay, Kích hoạt│
│    • Modal Hướng Dẫn Từng Chức Năng (👋 Onboarding Guide Steps)                         │
│    • Modal Studio PDF Document AI OCR Reader (`#modal-pdf-ocr`)                        │
│    • Hệ thống Thông Báo Nổi (🔔 Toast Notification System ở góc dưới phải)             │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📑 PHẦN III: DANH SÁCH CÁC TAB NGHIÊN CỨU & ÁNH XẠ CODE

| Tab ID trên HTML | Tiêu Đề Hiển Thị Trên UI | File JS Điều Khiển | File Router Backend |
| :--- | :--- | :--- | :--- |
| `pipeline-tab` | **⚡ 1. Quy Trình 7 Bước** | `static/js/pipeline.js` | `modules/pipeline/pipeline_router.py` |
| `harvester-tab` | **🌐 2. Thu Thập Tài Liệu** | `static/js/harvester.js` | `modules/harvester/harvester_router.py` |
| `notebooklm-tab` | **🧠 3. Kho Tri Thức** | `static/js/notebooklm.js` | `modules/notebooklm/notebooklm_router.py` |
| `zotero-tab` | **📚 4. Chuyển Đổi Zotero** | `static/js/zotero-converter.js` | `modules/zotero/zotero_router.py` |
| `writer-tab` | **🎓 5. Viết Học Thuật 2-File** | `static/js/academic-writer.js` | `modules/academic_writer/writer_router.py` |
| `editorial-tab` | **🏢 6. Tòa Soạn Báo GATE** | `static/js/editorial-office.js` | `modules/editorial_office/editorial_router.py` |
| `humanizer-tab` | **✨ 7. Khử AI & Chống Turnitin** | `static/js/humanizer.js` | `modules/humanizer/humanizer_router.py` |
| `math-chem-tab` | **📐 8. Toán - Hóa Học Pro** | `static/js/math-chem-pro.js` | `modules/math_chem_pro/math_chem_router.py` |
| `admin-tab` | **👑 9. Quản Trị Hệ Thống** | `static/js/admin.js` | `modules/admin_needle/admin_router.py` |
| `workspace-tab` | **📁 Không Gian Workspace** | `static/js/document-editor.js`, `static/js/pdf-ocr-reader.js` | `modules/workspace/workspace_router.py` |
| `history-tab` | **📜 Lịch Sử Hoạt Động** | `static/js/history.js` | `modules/history/history_router.py` |
| `bigquery-tab` | **📊 BigQuery AI & ML** | `static/js/bigquery-ml.js` | `modules/bigquery/bigquery_router.py` |

---

## 🔍 PHẦN IV: KẾT QUẢ KIỂM TOÁN GIAO DIỆN UI/UX & ĐÓNG GÓI SNAPSHOT (MILESTONE M4)

### 1. Kết Quả Kiểm Toán 170 Nút Bấm & 101 Lời Gọi API Frontend
- **Tổng số nút bấm trên giao diện (`static/index.html`):** 170 nút phân bố trên 12 thẻ và 4 modal dialogs.
- **Tình trạng phản hồi:** 170/170 nút có event handler / listener hợp lệ (100% Active, 0 nút chết).
- **Khắc phục lỗi Route Endpoint:**
  - **Vị trí lỗi:** `static/js/pdf-ocr-reader.js:287` gọi sai `/api/open-notebook/list`.
  - **Xử lý triệt để:** Sửa frontend thành `/api/notebooklm/notebooks` và bổ sung alias backend `@notebooklm_router.get("/api/open-notebook/list")` trong `modules/notebooklm/notebooklm_router.py` để bảo đảm tương thích ngược 100%.
- **Độ phủ API Frontend vs Backend:** 101/101 lời gọi `fetch()` trong 19 file JS khớp nối chính xác 100% với 130 router endpoints của FastAPI backend.

### 2. Đóng Gói Lưu Trữ Snapshot Hoàn Hảo (`Xac_Nhan_Hoan_Hao/`)
- **Công cụ tự động hóa:** `Xac_Nhan_Hoan_Hao/archive_manager.py` tích hợp `VERIFIED_MODULES_CATALOG` và hàm `package_all_verified_modules()`.
- **Danh mục 6 module hoàn chỉnh được đóng gói và cấp `manifest.json`:**
  1. `Module_03_Harvester_Verified`: Thu thập dữ liệu học thuật đa nguồn CrossRef, OpenAlex, ArXiv, Scholar, EuropePMC.
  2. `Module_04_Zotero_Converter_Verified`: Chuyển đổi mã trích dẫn Zotero Word (.docx) In-Place DOM và Bảng Đối Soát 6 Cột.
  3. `Module_05_MathChemPro_Verified`: Chuẩn hóa 109 hợp chất hóa học Unicode, công thức toán OMML và biểu đồ Matplotlib 300 DPI.
  4. `Module_06_BigQuery_AI_Verified`: Dự báo AI.FORECAST, kiểm định dị biệt AI.DETECT_ANOMALIES, phân tích động lực AI.KEY_DRIVERS, NL2SQL.
  5. `Module_07_PDF_OCR_Workspace_Verified`: Studio Document AI OCR PDF, chuyển đổi Markdown/Docx và nạp vào Open-Notebook.
  6. `Module_08_OpenNotebook_RAG_Verified`: Kho tri thức Open-Notebook RAG Vault, tìm kiếm lai Okapi BM25 + Multi-Scale N-Gram.

### 3. Kết Quả Kiểm Toán & Lược Bỏ / Khắc Phục Nút Chức Năng (Milestone M5 - Rà Soát Toàn Diện)
- **Kiểm toán toàn bộ 210+ sự kiện `onclick` và `addEventListener` trên 19 tệp JS và `index.html`:**
  1. **Khắc phục lỗi nút Lưu/Khôi phục Cấu trúc Dàn ý Bước 4 (`pipeline.js`):**
     - *Hiện tượng:* ID thẻ `<textarea>` trong template Step 4 là `pipeline-custom-outline-input`, nhưng hàm `saveCustomOutline()` và `resetDefaultOutline()` trước đó truy vấn ID `pipeline-custom-outline`, dẫn đến nút "💾 Lưu Cấu Trúc Đã Chỉnh Sửa" và "🔄 Khôi Phục Gốc" không nhận được nội dung đã sửa.
     - *Xử lý:* Cập nhật cả 2 hàm và tham số `runStep` hỗ trợ tìm kiếm linh hoạt cả hai ID (`pipeline-custom-outline-input` và fallback `pipeline-custom-outline`), đồng thời cập nhật đúng ID nút chuyển bước (`btn-next-step-4`) và thông báo Toast rõ ràng.
  2. **Lược bỏ nút mở/tải Tệp B không còn tồn tại (`academic-writer.js` & `static/index.html`):**
     - *Hiện tượng:* Sau khi hợp nhất dữ liệu xu hướng OpenAlex vào Tệp A duy nhất (loại bỏ Tệp B theo yêu cầu), giao diện `render2FilesResult()` vẫn cố hiển thị Card Tệp B với các nút "📝 Mở Word" và "📥 Tải về" bị rỗng (`pathB` rỗng).
     - *Xử lý:* Lược bỏ hoàn toàn Card Tệp B trên giao diện kết quả và cập nhật hiển thị tập trung cho Tệp A gồm các nút "📝 Mở Word (.docx)", "📥 Tải về (.docx)", "📥 Tải về (.md)", và tải danh mục trích dẫn đồng hành (.RIS / .BIB).
  3. **Đồng bộ nhãn hiển thị Stepper và Thẻ Trang Chủ (`index.html`):**
     - Đổi nhãn Bước 5 từ "Soạn Thảo Bộ 2 Tệp Chuẩn" sang "Soạn Thảo IMRaD Chuẩn Mực" và cập nhật mô tả tích hợp số liệu OpenAlex API thực tế.
  4. **Kiểm tra trạng thái máy chủ FastAPI (`server.py`):**
     - Xác nhận máy chủ khởi động thành công trên cổng 8080 với đầy đủ 14 feature routers. Mọi nút điều hướng Tab (`App.switchTab`), mở thư mục Workspace (`App.openWindowsExplorer`), nạp Evidence Vault và cấu hình cài đặt (`SettingsUI`) đều phản hồi chính xác 100%.

### 4. Tối Ưu Hóa Hiệu Suất Tải Trang & Core Web Vitals (LCP Optimization)
- **Tối ưu hóa tài nguyên phần cứng & mạng (Resource Hints):**
  - Bổ sung `<link rel="preconnect">` và `<link rel="dns-prefetch">` cho CDN KaTeX (`https://cdn.jsdelivr.net`) và Google Identity Services (`https://accounts.google.com`), rút ngắn thời gian thiết lập kết nối SSL/TLS cho tài nguyên phụ thuộc.
- **Tối ưu hóa Lập lịch & Render trễ (Render Delay < 10%):**
  - Toàn bộ 19 file JavaScript mô-đun được đặt ở cuối thẻ `<body>` và nạp theo chuỗi phân tầng mạch lạc (`auth.js` ➔ `app.js` ➔ Feature Controllers ➔ `onboarding.js`).
  - KaTeX math library được gắn cờ `defer` tránh chặn Main Thread (Zero Render Blocking).
- **Đồng bộ hóa vòng đời Tab Switch ([`app.js`](static/js/app.js)):**
  - Tích hợp hàm làm mới tự động khi chuyển sang thẻ BigQuery ML (`BigQueryMLUI.init()`) và Math-Chem Pro (`MathChemProUI.init()`).
  - Sửa đổi các tham số chuyển tab chuẩn (`workspace-tab`) trong toàn bộ các phân hệ phụ trợ.
- **Thời gian phản hồi API (TTFB):**
  - `/api/health`: ~75ms
  - `/api/agency/agents`: ~19ms
  - `/api/open-notebook/list`: ~83ms
  - Đảm bảo toàn bộ luồng hiển thị giao diện đạt tiêu chuẩn "Good" của Core Web Vitals (< 2,5s).

---

## 🌳 PHẦN V: TỐI ƯU HÓA CẤU TRÚC NHÁNH TRONG THẺ LỚN & GIAO DIỆN TRANG CHỦ (2026-08-28)

### 1. Cấu Trúc Nhánh Phân Cấp Thanh Điều Hướng Sidebar (Hierarchical Branch Navigation)
Thanh Sidebar đã được cấu trúc lại từ danh sách phẳng 14 tab rời rạc thành **5 Nhóm Cụm Chức Năng Lớn** kèm cấu trúc nhánh cây thu gọn/mở rộng (collapsible accordion) và ô tìm kiếm trực tiếp:
- **🔍 Ô Tìm Kiếm Nhanh Chức Năng (`#sidebar-feature-search`):** Gõ ký tự để lọc trực tiếp tên và mô tả các chức năng trong thời gian thực, tự động mở nhóm chứa chức năng khớp.
- **🌟 NHÓM I: TRUNG TÂM & QUY TRÌNH HỌC THUẬT:**
  - 🏠 **Trang Chủ** (Dashboard & Trạng thái tổng quan hệ thống)
  - ⚡ **Quy Trình 7 Bước** (Linear Chained Pipeline từ PICO đến Xuất bản)
  - 🎭 **Đội Ngũ AI Agency** (7 Chuyên gia AI hỗ trợ chuyên sâu)
- **🔬 NHÓM II: NGHIÊN CỨU & KHO TRI THỨC:**
  - 🌐 **1. Thu Thập Dữ Liệu** (Harvester Pro: Scholar, EuropePMC, arXiv, OpenAlex)
  - 🧠 **2. Kho Tri Thức RAG** (Open-Notebook RAG Vault & Ma trận y văn)
  - 📊 **3. BigQuery AI & ML** (Dự báo chuỗi thời gian & Phát hiện dị biệt dữ liệu lớn)
- **✍️ NHÓM III: SOẠN THẢO, TÒA SOẠN & BIÊN TẬP:**
  - 🎓 **4. Viết Học Thuật 2-File** (Bản thảo IMRaD APA 7th & Ma trận dữ liệu)
  - 📰 **5. Tòa Soạn Báo AI** (Mô hình 6 Ban GATE v3.1 & 4 Trạm kiểm duyệt)
  - 📚 **6. Chuyển Đổi Zotero** (Nhúng mã trường CSL Field Codes & Chuẩn hóa APA/MLA/ISO)
- **📐 NHÓM IV: KỸ THUẬT & KIỂM ĐỊNH:**
  - ✨ **7. Khử Dấu Vết AI** (Hạ xác suất AI < 10%, kiểm toán Turnitin 1-Click)
  - 📐 **8. Toán - Hóa - Biểu Đồ** (109 hợp chất Hóa học, công thức Toán OMML, ảnh 300 DPI)
- **📁 NHÓM V: KHÔNG GIAN & QUẢN TRỊ:**
  - 📁 **Không Gian Làm Việc** (Workspace Explorer & DOCX DOM Editor)
  - 🕒 **Lịch Sử Thao Tác** (Audit Log theo phiên & Khôi phục dữ liệu)
  - 👑 **Quản Trị Người Dùng** (Auth Vault, License Keys & Phân quyền)

### 2. Tối Ưu Hóa Trực Quan Giao Diện "Trang Chủ" (Optimized Home Dashboard)
Giao diện `#home-tab` được tái thiết kế toàn diện theo định hướng trực quan hóa cao cấp:
1. **Hero Header & Live Status Strip:**
   - Hiển thị trạng thái kết nối thời gian thực: Mô hình AI Gemini tích cực, Tình trạng lưu trữ Workspace, Cổng Zotero Connector 23119 và Liêm chính học thuật (100% Evidence First).
   - Bộ 4 nút khởi chạy nhanh (Quick Launchers): *Bắt đầu Quy trình 7 Bước*, *Chuẩn hóa Zotero Word*, *Thu thập tài liệu*, *Nâng cấp Toán - Hóa*.
2. **Interactive 7-Step Linear Pipeline Visualizer:**
   - Trình diễn trực quan luồng 7 bước với khả năng nhấp trực tiếp vào bất kỳ bước nào (Bước 1 đến Bước 7) để kích hoạt ngay bước đó trong Quy trình liên kết.
3. **4 Cụm Trụ Cột Kỹ Năng Chuyên Sâu (Master Feature Clusters):**
   - Đóng gói 4 thẻ lớn ứng với 4 nhóm kỹ năng cốt lõi (Nghiên Cứu, Soạn Thảo, Kỹ Thuật, Không Gian & Quản Trị).
   - Mỗi thẻ lớn liệt kê đầy đủ các nhánh con với biểu tượng, mô tả chi tiết, badge chuyên biệt và nút điều hướng 1-click.

### 3. Cơ Chế Mở Nhánh Thông Minh & Tự Động Thu Gọn (Accordion & Auto-Collapse)
- **Mở và Chọn Nhánh (Accordion Navigation):** Khi người dùng nhấp vào tiêu đề của bất kỳ Nhóm Cụm nào, hệ thống sẽ mở danh sách các chức năng con của nhóm đó và **tự động thu gọn các nhóm còn lại**, giúp giao diện luôn gọn gàng và không bị kéo dài màn hình.
- **Tự Động Thu Gọn Khi Không Chọn (Auto-Collapse on Outside Click / Idle):** 
  - Nếu người dùng mở một nhánh để xem nhưng sau đó click ra ngoài thanh sidebar hoặc click vào vùng nội dung chính (`.app-main`) mà **không bấm chọn chức năng con nào**, thanh Sidebar sẽ **tự động thu gọn các nhánh phụ** và chỉ giữ lại duy nhất nhánh chứa tab đang hoạt động (`active tab`).
  - Khi rời chuột (`mouseleave`) khỏi Sidebar, hệ thống duy trì độ trễ tự nhiên (1.2s) rồi tự động đồng bộ thu gọn các nhánh không chọn về trạng thái tối giản.
- **Đồng Bộ Tab Chuyển Đổi:** Khi người dùng chuyển tab từ bất kỳ vị trí nào trên trang (nút bấm Trang chủ, thanh điều hướng nhanh, hoặc tiến trình 7 Bước), hệ thống tự động mở nhánh tương ứng của tab đó và thu gọn các nhánh khác.

### 4. Chế Độ Thu Nhỏ Mini-Dock & Điều Khiển Hiện Đại (Mini-Dock & Modern Controls)
- **Chế Độ Mini-Dock 64px (`.sidebar-compact`):** Nhấp nút `[ ◨ ]` hoặc nhấn phím tắt `Ctrl + B` để thu hẹp thanh Sidebar thành dải Dock đứng siêu gọn (chỉ hiển thị Icon). Khi rê chuột vào Icon, Tooltip chú giải nổi lên mượt mà dạng Glassmorphism.
- **Bộ Phím Tắt Tiện Dụng:**
  - `Ctrl + B`: Bật/Tắt chế độ Mini-Dock thu hẹp Sidebar.
  - `Ctrl + K`: Nhảy nhanh đến ô tìm kiếm tính năng.
  - `Escape`: Xóa tìm kiếm và đóng kết quả lọc.
- **Nút Thu / Mở Nhanh Toàn Bộ Nhánh (`[ ⇱/⇲ ]`):** 1-Click mở toàn bộ hoặc thu gọn toàn bộ các nhánh chức năng.
- **Đường Nối Phân Cấp (Tree Connectors):** Nhánh con được nối bằng các đường kẻ nhánh thanh mảnh, hiện đại thay vì dạng khối hộp nặng nề.



