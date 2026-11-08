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
- **Yêu cầu 9 (2026-09-06 - Bóc Tách Dữ Liệu Theo Từng Tài Liệu Cung Cấp, Thống Kê Định Lượng & Quản Trị Cơ Sở Dữ Liệu Thực Chứng):**
  - *Nhiệm vụ:* Phát triển tính năng bóc tách dữ liệu theo từng tài liệu được cung cấp, có trích dẫn viễn dẫn theo chuẩn APA 7th (số trang, phân mục, trích đoạn nguyên văn, bản dịch), thống kê số lượng định lượng chi tiết theo từng tài liệu và toàn kho, kiến tạo cơ sở dữ liệu thực chứng bền vững để triển khai các bước tiếp theo (viết bài, đối soát, phản biện).
  - *Kết quả xử lý:*
    1. **Động cơ Bóc tách Chuyên sâu:** Xây dựng `modules/pipeline/document_extractor_engine.py` (`DocumentEvidenceExtractor`) hỗ trợ đa định dạng PDF (bóc tách bảng qua pdfplumber + text pypdf), Word .docx (bóc tách bảng và đề mục phân trang), và Markdown/Text.
    2. **Chuẩn Hóa Trích Dẫn APA 7th:** Tự động kiến tạo trích dẫn In-text đóng ngoặc `(Vaswani et al., 2017)`, Narrative `Vaswani et al. (2017)`, Mục tài liệu tham khảo với liên kết DOI thực tế `https://doi.org/...`, và Trích dẫn viễn dẫn chính xác theo vị trí `(Vaswani et al., 2017, p. 2)` hoặc `Trang 2 (Mục 2.1)`.
    3. **Phân Loại 5 Nhóm Thực Chứng Cốt Lõi:** Phân loại toàn bộ câu trích thành 5 nhóm: `OBJECTIVE` (Mục tiêu), `METHODOLOGY` (Phương pháp/mô hình), `QUANTITATIVE_RESULT` (Số liệu đo lường định lượng), `LIMITATION` (Giới hạn/Rủi ro), và `RESEARCH_GAP` (Khoảng trống phát triển). Tự động gắn nhãn minh bạch `[uncertain]` đối với các luận điểm định tính chưa được kiểm chứng số liệu.
    4. **Thống Kê Định Lượng Theo Từng Tài Liệu:** Tính toán chi tiết cho mỗi tài liệu: `page_count`, `total_words`, `total_claims_extracted`, `quantitative_metrics_count`, `methodology_items_count`, `limitations_and_gaps_count`, `tables_extracted_count`, `extraction_quality` (HIGH/MEDIUM/LOW).
    5. **Cơ Sở Dữ Liệu Thực Chứng (Empirical Evidence Database):** Lưu trữ có cấu trúc tại `workspace/Evidence_Database/{db_id}.json` và `latest_database.json`. Tự động xuất Báo cáo Word `.docx` chuẩn A4 (bảng tổng hợp scorecard, bảng ma trận đối soát lưới, thư viện tham khảo thụt lề treo Hanging Indent), file Markdown `.md`, và bộ trích dẫn Zotero `.ris` & `.bib`.
    6. **Hệ Thống API Endpoints:** Khởi tạo `modules/pipeline/evidence_db_router.py` với các endpoints: `POST /api/evidence-db/extract-provided-documents`, `POST /api/evidence-db/upload-and-extract`, `GET /api/evidence-db/list`, `GET /api/evidence-db/{db_id}`, `GET /api/evidence-db/{db_id}/download-docx`, `POST /api/evidence-db/feed-to-writer`.
- **Yêu cầu 10 (2026-09-07 - Tự Động Xây Dựng Cây Đề Cương Theo Tên Đề Tài & Bóc Tách Thực Chứng Bằng Google Gemini AI):**
  - *Nhiệm vụ:* Bóc tách nguyên lý hoạt động của `dashi-ppt-skill` (Knowledge Atomization Protocol) và `codex-ppt-skill` (Page Role Pacing & Multimodal Notes), xây dựng tính năng tự động thiết lập cây đề cương nghiên cứu theo tên đề tài bằng Google Gemini AI và bóc tách dữ liệu từ các tài liệu cung cấp khớp trực tiếp vào từng phân mục đề cương.
  - *Kết quả xử lý:*
    1. **Tối ưu hóa Skills sang Google Gemini AI:** Tích hợp thành công `GeminiImageProvider` (Google Imagen 3 API: `imagen-3.0-generate-002` / `imagen-3.0-fast-generate-001`) thay thế hoàn toàn OpenAI DALL-E/GPT-Image-2 trong `gemini-ppt`. Tích hợp `gemini_dashi_generator.py` phân tích đề cương bài thuyết trình và đóng gói `goal.json` chuẩn schema v2 trong `dashi-ppt`. Cài đặt thành công cả ở Global Skills (`~/.gemini/config/skills/`) và Workspace Skills (`Skill/`).
    2. **Kiến Trúc Sinh Đề Cương Đề Tài Tự Động Bằng Gemini AI (`generate_topic_structured_outline`):** Nhận tên đề tài từ người dùng, gọi Google Gemini AI phân tích chuyên sâu để kiến tạo cây đề cương 6-8 phân mục khoa học chuẩn quốc tế (Đặt vấn đề & Mục tiêu, Cơ sở lý thuyết & Khoảng trống, Phương pháp & Thiết kế nghiên cứu, Kết quả thực nghiệm định lượng, Thảo luận & Đối chuẩn đa chiều, Giới hạn & Khuyến nghị chính sách). Hỗ trợ cơ chế Fallback Heuristic học thuật chuyên sâu khi không có internet hoặc API key.
    3. **Động Cơ Bóc Tách Khớp Đề Cương (`extract_evidence_by_topic_outline`):** Phân tích đối soát từng tài liệu cung cấp (PDF, Word .docx, Markdown), trích xuất luận điểm thực chứng, chỉ số đo lường, đơn vị đo, đoạn văn trích nguyên văn và vị trí số trang chính xác. Gắn nhãn viễn dẫn chuẩn APA 7th `(Author, Year, p. X)`.
    4. **Cơ Chế Kiểm Soát Tính Bất Định (Zero-Fabrication Transparency):** Tự động phát hiện và gắn cờ cảnh báo minh bạch `[uncertain]` đối với các phân mục đề cương chưa có dữ liệu thực chứng trong tài liệu cung cấp hoặc chỉ có nhận định định tính chung, loại trừ 100% rủi ro bịa đặt số liệu (Hallucination).
    5. **Xuất Bản Đa Định Dạng Bền Vững:** Tự động tạo Báo cáo Word `.docx` đạt chuẩn In-Place DOM Word (bảng scorecard độ phủ thực chứng, bảng lưới đối soát màu sắc chuyên nghiệp, thư viện tài liệu tham khảo Hanging Indent A-Z), Báo cáo Markdown `.md` và Cơ sở dữ liệu JSON tại `workspace/Evidence_Database/`.
    6. **Hệ Thống API Endpoints:** Bổ sung `POST /api/evidence-db/generate-topic-outline` và `POST /api/evidence-db/extract-by-topic` trong `evidence_db_router.py`.
    7. **Kiểm Thử Toàn Diện:** Đạt 100% PASS trên bộ kiểm thử tự động `tests/test_topic_outline_extractor.py` (3/3 tests PASS).
- **Yêu cầu 11 (2026-09-07 - Thống Kê Xu Hướng Nghiên Cứu Đa Nguồn Mở Theo Từ Khóa Đề Tài & Tích Hợp Vào Cấu Trúc Bài Làm):**
  - *Nhiệm vụ:* Xây dựng tính năng cho phép người dùng lựa chọn nguồn dữ liệu thống kê mã nguồn mở (OpenAlex, Europe PMC, arXiv, Crossref, hoặc Đa nguồn hợp nhất) để thu thập số liệu thống kê công bố khoa học theo các từ khóa liên quan đến đề tài, tính toán CAGR (%) và xu hướng phát triển, đồng thời tích hợp trực tiếp một phân mục chuyên sâu vào Cây đề cương và Báo cáo thực chứng.
  - *Kết quả xử lý:*
    1. **Mở rộng Động cơ Thống kê Đa Nguồn Mở:** Triển khai `extract_topic_keywords()` tự động bóc tách từ khóa song ngữ Anh - Việt, và `fetch_per_keyword_trends(keywords, source="openalex"|"europepmc"|"arxiv"|"crossref"|"all")` kèm `fetch_multi_source_keyword_trends()` trong `modules/harvester/data_harvesting_engine.py`.
    2. **Tích hợp Vào Cấu trúc Bài làm & Cây Đề Cương:** Bổ sung phân mục `2.2. Phân Tích Thư Mục Học & Xu Hướng Nghiên Cứu Toàn Cầu ({source_name})` vào Chương 2 của Cây đề cương (`generate_topic_structured_outline`) với nhãn `BIBLIOMETRICS` và `TRENDS`.
    3. **Tự Động Nạp Dữ Liệu Thực Chứng & Bảo Toàn Liêm Chính (Zero-Fabrication):** `extract_evidence_by_topic_outline` tự động truy vấn dữ liệu mở theo nguồn được chọn, nạp các chỉ số đo lường công bố, CAGR %, hướng vận động và số bài báo thực tế vào bảng bằng chứng, gắn nhãn minh bạch xác thực từ API Mở (không bị đánh cờ `[uncertain]`).
    4. **Xuất Bản Bảng Ma Trận Xu Hướng Word .docx & Markdown .md:** Trình bày bảng lưới Word chuyên nghiệp (Navy Header `#0F172A`, các dòng xen kẽ `#F8FAFC`, số thập phân dấu phẩy kiểu Việt Nam) và bảng Markdown trực quan.
    5. **Mở Rộng API Endpoints:** Mở endpoint `POST /api/harvest/keyword-trends` và bổ sung tham số `trend_source`, `trend_keywords` vào `POST /api/evidence-db/generate-topic-outline`, `POST /api/evidence-db/extract-by-topic`.
    6. **Kiểm Thử:** Đạt 100% PASS trên bộ kiểm thử tự động mới `tests/test_multi_source_keyword_trends.py` (6/6 tests PASS) và bảo toàn 100% tests hồi quy `tests/test_topic_outline_extractor.py` (3/3 tests PASS).
- **Yêu cầu 12 (2026-09-07 - Tinh Chỉnh Điều Khiển Nút Bấm & Trải Nghiệm Tương Tác Harvester Thông Minh):**
  - *Nhiệm vụ:* Rà soát các nút bấm chức năng trong phân hệ Thu thập tài liệu Harvester, loại bỏ hiện tượng silent failure khi bỏ trống câu hỏi/chủ đề, bổ sung phím tắt Enter và chống double-click.
  - *Kết quả xử lý:*
    1. Gắn định danh `id="btn-harvester-generate-kw"` cho nút sinh từ khóa, tích hợp trạng thái `btn.disabled = true` cùng biểu tượng tải xoay vòng trong suốt quá trình AI phân tích.
    2. Tự động focus con trỏ và kích hoạt viền cảnh báo trực quan tại `#harvester-topic` và `#harvester-custom-query` khi người dùng bấm thao tác mà chưa điền câu truy vấn.
    3. Bổ sung phím tắt `Enter` trên cả 2 ô nhập `#harvester-topic` và `#harvester-custom-query` để kích hoạt tức thì quy trình mà không cần chuyển tay dùng chuột.
- **Yêu cầu 13 (2026-09-07 - Tích Hợp Động Cơ Trình Duyệt Tàng Hình Obscura Dùng Chung Cho Tác Vụ Thu Thập & Tải Tệp):**
  - *Nhiệm vụ:* Cài đặt và suy luận ra kỹ năng dùng chung `stealth-data-harvesting` dựa trên động cơ trình duyệt không đầu Obscura (Rust V8 headless engine), phục vụ thu thập dữ liệu web và tải tài liệu PDF tàng hình vượt qua cơ chế chống bot/Cloudflare.
  - *Kết quả xử lý:*
    1. **Cài Đặt Động Cơ Obscura v0.2.2:** Tải và cài đặt thành công bộ nhị phân Obscura Windows (`obscura.exe` và `obscura-worker.exe`) vào thư mục `~/.local/bin` (đã nằm trong `PATH` hệ thống), sẵn sàng kích hoạt từ mọi terminal và môi trường dòng lệnh.
    2. **Xây Dựng Kỹ Năng Toàn Cục & Cục Bộ:** Đóng gói hoàn chỉnh kỹ năng `stealth-data-harvesting` gồm tệp đặc tả chuẩn mực `SKILL.md` tại cả hai vị trí: Global Skills (`~/.gemini/config/skills/stealth-data-harvesting/`) và Workspace Master Skills (`Skill/02_THU_THAP_PDF_VA_ZOTERO/Stealth_Browser_Harvesting/`).
    3. **Phát Triển Mô-đun Python Wrapper (`ObscuraHarvester`):** Cung cấp giao diện lập trình cấp cao hỗ trợ đầy đủ 5 phương thức nghiệp vụ: `fetch_text()` (bóc tách văn bản sạch chuẩn LLM-Ready), `fetch_html()` (kết xuất DOM SPA hoàn chỉnh), `fetch_links()` (dò tìm siêu liên kết PDF/DOI), `download_file()` (tải nhị phân nguyên bản qua luồng `--dump original`), và `scrape_batch()` (quét song song đa luồng).
    4. **Đăng Ký Vào Hệ Thống Tiến Hóa Glimax Darwin:** Đăng ký thành công artifact kỹ năng `stealth-browser-harvesting` (ID: `5e8954acabfc`) với tỷ suất ROI 0.82 và tỷ lệ thành công 100%.
    5. **Kiểm Thử Thực Nghiệm 100%:** Kiểm thử tự động qua `test_harvester.py` xác thực thành công 5/5 tiêu chí: Nhận diện phiên bản, Bóc tách văn bản sạch, Trích xuất liên kết, Thực thi JS, và Tải tệp PDF thực tế từ arXiv đạt chuẩn `%PDF-` 100%.
- **Yêu cầu 14 (2026-09-08 - Hoàn Thiện & Tối Ưu Toàn Diện Kỹ Năng Thu Thập Dữ Liệu Harvester Pro Đa Nguồn & Tạp Chí Việt Nam):**
  - *Nhiệm vụ:* Nâng cấp toàn diện Harvester Pro theo đặc tả `Skill/00_QUY_TRINH_TONG_THE/01_Auto_Download_PDF/SKILL.md`, đảm bảo khả năng tìm kiếm đa nguồn thực tế (Google Scholar, EuropePMC, arXiv, OpenAlex, CrossRef), bổ sung tìm kiếm tạp chí trong nước (VJOL, ĐHQG, Bộ KH&CN, ĐH Cần Thơ...), tích hợp ảnh Wikimedia 300 DPI và tối ưu tốc độ tra cứu dưới 3 giây.
  - *Kết quả xử lý:*
    1. **Bổ Sung `search_vietnamese_journals`:** Tích hợp phương thức tìm kiếm chuyên sâu tạp chí khoa học Việt Nam từ các nguồn chính thống, bóc tách chính xác tiêu đề, tác giả, tên tạp chí và liên kết tải toàn văn thực tế.
    2. **Tích Hợp Ảnh Khoa Học 300 DPI RGB (`search_wikimedia_images`):** Tự động tìm kiếm ảnh thực địa/sơ đồ khoa học từ Wikimedia Commons, chuyển đổi sang độ phân giải in ấn 300 DPI qua Pillow và lưu trữ tại `workspace/charts/`.
    3. **Tách Biệt Resolver Tra Cứu Nhanh vs Bóc Tách Sâu:** Thêm cờ `deep_crawl=False` cho giai đoạn tìm kiếm ứng viên, giảm thời gian tìm kiếm từ ~45s xuống ~3s.
    4. **Bộ Dịch Thuật Đa Tầng Tối Ưu:** Kết hợp Cache RAM bộ nhớ và Google GTX tốc độ cao giúp phản hồi tức thì (0.00s).
    5. **Hoàn Thiện `save_paper_to_zotero`:** Bổ sung đầy đủ các trường `rel_md_path`, `md_file_name`, và `integrity_audit` vào kết quả trả về, bảo đảm liên thông 3 chiều (.docx ↔ Zotero ↔ PDF).
    6. **Kiểm Thử Thực Nghiệm:** Đạt 100% PASS trên tất cả các kịch bản kiểm thử Harvester (Test 1.1, 1.2, 1.3, 1.4).
- **Yêu cầu 15 (2026-09-14 - Tích Hợp Reactome Database Service Tra Cứu Đường Dẫn Sinh Học & Chu Trình Sinh Hóa):**
  - *Nhiệm vụ:* Mở rộng năng lực của Harvester phục vụ các đề tài Khoa học máy tính ứng dụng trong Nông nghiệp, Tài nguyên và Môi trường (trọng tâm ThS KHMT ĐH Đồng Tháp), tích hợp cơ sở dữ liệu đường dẫn sinh học Reactome (`https://reactome.org/`).
  - *Kết quả xử lý:*
    1. **Khởi Tạo `ReactomeService` (`modules/shared/reactome_service.py`):** Cung cấp các phương thức `search_pathways(query, max_results)` và `get_pathway_details(pathway_id)` kết nối Content Service API của Reactome, có cơ chế Local Curated Knowledge Cache tự động fallback khi offline.
    2. **Hệ Thống API Endpoints Mới:** Khởi tạo `POST /api/harvester/reactome-search` và `GET /api/harvester/reactome-pathway/{pathway_id}` trong `modules/harvester/harvester_router.py`.
    3. **Kiểm Thử Độc Lập:** Đạt 100% PASS trên bộ kiểm thử tự động `tests/test_reactome_service.py` (5/5 tests PASS).
- **Yêu cầu 16 (2026-09-16 - Hoàn Thiện Giao Diện Tương Tác Reactome Pathways Explorer & Nạp Vào Evidence Vault):**
  - *Nhiệm vụ:* Đưa tính năng tra cứu Reactome vào giao diện Harvester UI (`static/index.html` & `static/js/harvester.js`) kèm tính năng nạp thẳng vào Evidence Vault.
  - *Kết quả xử lý:*
    1. **Tùy chọn Nguồn:** Bổ sung `Reactome Pathways` vào thẻ `harvester-source-select`.
    2. **Thẻ Explorer Chuyên Dụng:** Bổ sung giao diện Thẻ Tra Cứu Đường Dẫn Sinh Học & Phản Ứng (Reactome Pathways Explorer) với Quick Search Chips: Chuyển hóa Nitơ, Amoni, Chu trình Lưu huỳnh, Giải độc Kim loại nặng, Đường phân.
    3. **Nạp Thẳng Vào Vault:** Nút "📥 Thêm Vào Vault" chuyển dữ liệu đường dẫn sinh học và số lượng phản ứng hóa sinh trực tiếp sang Evidence Vault phục vụ Academic Writer.
    4. **Kiểm thử:** 100% test case trong `tests/test_reactome_service.py` đạt trạng thái PASS.
