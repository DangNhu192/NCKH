# 🌐 THU THẬP TÀI LIỆU ĐA NGUỒN & HÌNH ẢNH 300 DPI (HARVESTER PRO)

## 🎯 VỊ TRÍ & ĐẶC TẢ MODULE
- **Giao diện:** Tab 2 (`#harvester-tab`).
- **File Frontend:** `static/js/harvester.js`
- **File Backend:** `modules/harvester/harvester_router.py`, `modules/harvester/data_harvesting_engine.py`
- **Module liên kết:** `modules/zotero/zotero_converter_engine.py` (đính kèm attachment), `modules/shared/docx_styler.py` (xuất .docx), `modules/shared/pdf_ocr_engine.py` (Purpose-Built Document AI)

## 🔗 QUY TRÌNH LIÊN KẾT LIÊN THÔNG (INTERLINK PROTOCOL)
- **Đầu vào (Input Tiếp Nhận):**
  - Nhận câu truy vấn tìm kiếm và danh sách từ khóa được chuyển tiếp tự động từ **Tab 1 (Pipeline Bước 1)** hoặc do người dùng nhập tùy chỉnh.
  - Người dùng có thể upload trực tiếp file PDF/DOCX từ máy tính.
- **Xử lý Thu Thập Đa Nguồn:**
  - Quét đồng thời 5 cơ sở dữ liệu học thuật toàn cầu: Google Scholar, EuropePMC, arXiv, OpenAlex, CrossRef.
  - Tích hợp Wikimedia Commons API để tìm kiếm hình ảnh thực địa, bản đồ khoa học thực tế và chuyển đổi sang chuẩn in ấn RGB 300 DPI.
  - **Bóc tách toàn văn theo 4 tầng ưu tiên:**
    1. PMC XML (EuropePMC) — giàu cấu trúc nhất: bảng biểu, hình ảnh, danh sách tài liệu tham khảo.
    2. PDF Full Text qua pdfplumber + pypdf (bảng số liệu + hình ảnh 300 DPI).
    3. Web HTML trang nguồn (article, main content).
    4. Abstract nguyên bản + Metadata từ CrossRef/OpenAlex (khi không có toàn văn).
  - **Giải mã URL PDF đa tầng:** OpenAlex → Unpaywall → Semantic Scholar → Deep Web Crawler.
  - **Lấy danh mục tài liệu tham khảo thực tế** từ CrossRef API theo DOI.
- **Đầu ra (Output Bàn Giao Liên Thông):**
  - ➔ **Lưu Workspace:** File `.docx` + `.md` học thuật tại `Tai_Lieu/`, file PDF gốc tại `Tai_Lieu/PDFs/`.
  - ➔ **Truyền sang Tab 3 (NotebookLM):** Nội dung đã bóc tách (verbatim) phục vụ AI đọc qua `/api/harvest/read-for-ai`.
  - ➔ **Truyền sang Tab 4 (Zotero Converter):** Đẩy Metadata + đính kèm link PDF vào Zotero item qua `attach_pdf_link_to_item()`.
  - ➔ **Truyền sang Tab 8 (Math-Chem Pro):** Hình ảnh khoa học 300 DPI tại `workspace/charts/`.

## ⚖️ TUÂN THỦ 4 QUY TẮC BẤT BIẾN & ĐẠO ĐỨC NGHIÊN CỨU
1. **Evidence First & Zero Fabrication:** 100% tài liệu thu thập có DOI thực tế, tác giả và nguồn xuất bản xác thực (không bịa đặt). Hệ thống cảnh báo rõ khi không thể truy cập toàn văn — **TUYỆT ĐỐI không diễn giải, thêm hoặc sửa nội dung gốc.**
2. **In-Place DOM Word (.docx):** Bảo toàn mã trích dẫn liên kết khi lưu trữ. Hình ảnh nhúng vào .docx đúng vị trí với Caption học thuật chuẩn APA.
3. **Chuẩn hóa số thập phân tiếng Việt:** `1,5; 28,5%`.
4. **Chuẩn hóa hóa học & toán học:** Nhận diện đúng ký hiệu trong tiêu đề và tóm tắt bài báo.

## 🛡️ CƠ CHẾ KIỂM TRA TÍNH TOÀN VẸN (Integrity Audit)
- `audit_extraction_integrity()` so sánh số từ bóc tách với tổng trang PDF.
- Phân loại chất lượng: `HIGH` / `MEDIUM` / `LOW` / `ABSTRACT_ONLY` / `NO_CONTENT`.
- Cảnh báo rõ ràng khi tài liệu bị paywall: trả về link trang nguồn để người dùng tự tải.
- **Ràng buộc:** Chỉ tải PDF từ nguồn Open Access xác thực (OpenAlex, Unpaywall, PMC, arXiv).

## 📡 API ENDPOINTS
| Endpoint | Mô tả |
|---|---|
| `POST /api/harvest/run` | Tìm kiếm & thu thập bài báo |
| `POST /api/harvest/save-to-zotero` | Lưu 1 bài báo vào Zotero + tạo .docx |
| `POST /api/harvest/batch-save-to-zotero` | Lưu hàng loạt vào Zotero |
| `POST /api/harvest/upload-paper-file` | Upload PDF/DOCX từ người dùng → chuyển .docx + .md |
| `GET/POST /api/harvest/download-pdf` | Tải file PDF gốc về Workspace (`Tai_Lieu/PDFs/`) |
| `POST /api/harvest/integrity-check` | Kiểm tra tính toàn vẹn bóc tách |
| `POST /api/harvest/read-for-ai` | Trả về nội dung verbatim để AI đọc (NotebookLM/RAG) |
| `POST /api/pdf-ocr/inspect` | Phân tích lớp chữ PDF (Digital vs Scan thuần ảnh) |
| `POST /api/pdf-ocr/upload-and-process` | Upload và thực hiện AI OCR + RAG Chunks |
| `POST /api/pdf-ocr/process` | Xử lý OCR trên file PDF trong Workspace |
| `POST /api/pdf-ocr/export-docx` | Xuất kết quả OCR sang Word .docx 300 DPI |
| `POST /api/pdf-ocr/ingest-to-notebook` | Nạp 1-click toàn văn OCR vào Open-Notebook |

## 📝 NHẬT KÝ YÊU CẦU & KẾT QUẢ XỬ LÝ
- **Yêu cầu 1:** Bổ sung Quick Chips (5, 15, 50, 100, 200) để chọn nhanh số lượng bài cần quét.
  - *Kết quả:* Đã triển khai trên giao diện tại `#harvester-max-papers`.
- **Yêu cầu 2:** Tải ảnh thực địa khoa học chuẩn in ấn 300 DPI từ Wikimedia Commons.
  - *Kết quả:* Đã tích hợp thư viện Pillow chuyển đổi RGB 300 DPI tự động.
- **Yêu cầu 4 (2026-08-27 - 4-Tier Traceable Research Retrieval & Evidence System):**
  - *Nhiệm vụ:* Nâng cấp Harvester thành Chuyên gia Truy xuất & Bóc tách Thực chứng Cấu trúc (Research Retrieval & Evidence Extraction Specialist) theo mô hình 4 tầng.
  - *Kết quả xử lý:*
    1. **TẦNG 1 (RETRIEVAL):** Hiện thực hóa `parse_research_intent()` (phân định yêu cầu tường minh, suy luận, thông số chưa biết), `decompose_topic()` (phân rã 13 chiều nghiên cứu A-M), `expand_research_queries()` (sinh đa dạng 6 loại truy vấn: broad, technical, review/meta-analysis, implementation, measurement, policy), và `deduplicate_candidates()` (khử trùng theo DOI, normalized title, author/year).
    2. **TẦNG 2 (SCREENING & EXTRACTION):** `screen_candidates_relevance()` (chấm điểm 0-100 theo 6 tiêu chí kèm phân loại và lý do), `assess_source_quality()` (xếp hạng 4 tầng phân cấp chất lượng nguồn).
    3. Đạt 100% PASS trên bài kiểm tra E2E `test_4tier_evidence_system.py`.
    4. Nâng cấp `saved_record` với `zotero_web_url`, `zotero_attachment_url`, `integrity_audit` — tạo liên kết 3 chiều (file .docx ↔ Zotero item ↔ PDF URL).
    - Thêm `download_pdf_to_disk()` — tải PDF gốc về `Tai_Lieu/PDFs/`, kiểm tra magic bytes `%PDF` và kích thước, endpoint `/api/harvest/download-pdf`.
    - Thêm `audit_extraction_integrity()` — phân loại chất lượng bóc tách (HIGH/MEDIUM/LOW/ABSTRACT_ONLY), cảnh báo paywall, không bao giờ thêm nội dung giả.
    - Thêm `get_readable_content_for_ai()` + endpoint `/api/harvest/read-for-ai` — trả về nội dung verbatim để AI/NotebookLM đọc trực tiếp mà không cần xử lý lại PDF.
    - Thêm `attach_pdf_link_to_item()` vào `zotero_converter_engine.py` — đính kèm link URL PDF (linked_url) vào Zotero item sau khi nạp metadata.
- **[2026-08-26 11:40] Yêu cầu 5:** Tích hợp Purpose-Built AI OCR cho việc đọc file PDF theo mô hình `abbyy/JFK-OCR` (mở rộng khả năng đọc PDF scan thuần ảnh, phục hồi lớp chữ Searchable Text Layer, trích xuất bảng số liệu dạng lưới và phân đoạn RAG Semantic Chunks).
  - *Kết quả:*
    - Xây dựng `modules/shared/pdf_ocr_engine.py` với kiến trúc 4 tầng: `inspect_pdf()`, `ocr_page_with_vision_ai()` (Gemini Vision AI / ABBYY Vantage), `export_searchable_docx()` (In-Place DOM Word) và `ingest_to_open_notebook()`.
    - Bổ sung các endpoints `/api/pdf-ocr/inspect`, `/api/pdf-ocr/upload-and-process`, `/api/pdf-ocr/process`, `/api/pdf-ocr/export-docx`, `/api/pdf-ocr/ingest-to-notebook` trong `modules/workspace/workspace_router.py`.
    - Xây dựng giao diện Studio `static/js/pdf-ocr-reader.js` và Modal `#modal-pdf-ocr` trong `static/index.html`.
- **Yêu cầu 6 (2026-08-26 - Multi-Agent & E2E Validation):** Hoàn thiện kiểm thử đa tác nhân M1, M2, M3 và bộ kiểm thử tự động E2E.
  - *Kết quả:*
    - Xác thực 100% Zero-Fabrication qua `test_worker_m1_verification.py` (34/34 tests PASS).
    - Xác thực trọn vẹn luồng đọc và bóc tách PDF AI OCR qua `test_pdf_ocr_full_flow.py` (11/11 tests PASS, 1.11s).
    - Đạt 100% PASS trên tất cả 4 lớp kiểm định của `tools_cross_validate_docs.py`.
- **Yêu cầu 8 (2026-08-27 - Khắc Phục Triệt Để Lỗi Error 500 Khi Sinh Từ Khóa & Tối Ưu Hóa Dịch Thuật Đa Tầng):**
  - *Nguyên nhân gốc rễ:* Thư viện `deep_translator` scraping Google Translate bị Google trả về mã lỗi HTML `Error 500 (Server Error)!!1500.That's an error...`. Do trước đây hàm dịch chỉ kiểm tra ký tự tiếng Việt (`_has_vietnamese_characters`) nên chuỗi lỗi này đã bị chấp nhận và đưa vào Boolean Query `("Error 500...") AND ("Scopus")`.
  - *Giải pháp & Kết quả:*
    1. Loại bỏ `deep_translator`, bổ sung hàm kiểm định nghiêm ngặt `_is_valid_translation()` sàng lọc 100% các chuỗi lỗi máy chủ, HTML, Exception, 404, 500, 429.
    2. Tích hợp cổng dịch thuật MyMemory REST API kết hợp Từ điển Thuật ngữ Học thuật Song ngữ chuyên sâu và bộ nhớ đệm `_translation_cache`.
    3. Cập nhật `gemini_service.py` ưu tiên `gemini-3.6-flash`, tự động ghi nhận cooldown 60s trên mã 429 và failover mô hình dự phòng.
    4. Xác thực qua `test_query_fix.py` và `test_all_features_e2e.py` đạt 100% PASS, sinh câu truy vấn và từ khóa chuẩn xác cho mọi chủ đề.

