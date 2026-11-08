# 🧠 KHO TRI THỨC HỌC THUẬT & TRỢ LÝ NOTEBOOKLM RAG

## 🎯 VỊ TRÍ & ĐẶC TẢ MODULE
- **Giao diện:** Tab 3 (`#notebooklm-tab`).
- **File Frontend:** `static/js/notebooklm.js`
- **File Backend:** `modules/notebooklm/notebooklm_router.py`, `modules/notebooklm/notebooklm_engine.py`

## 🔗 QUY TRÌNH LIÊN KẾT LIÊN THÔNG (INTERLINK PROTOCOL)
- **Đầu vào (Input Tiếp Nhận):**
  - Nhận toàn bộ tài liệu PDF, DOCX, TXT được thu thập từ **Tab 2 (Harvester)** hoặc người dùng tải lên.
- **Xử lý Tri thức Ngữ nghĩa:**
  - Trích xuất văn bản đa tầng, phân đoạn văn bản (Text Chunking), đánh chỉ mục ngữ nghĩa (BM25 + Semantic Cosine).
  - Tổng hợp ma trận so sánh các trường phái nghiên cứu (7-Column Literature Review Matrix).
- **Đầu ra (Output Bàn Giao Liên Thông):**
  - ➔ **Truyền sang Tab 5 (Academic Writer):** Cung cấp các đoạn trích dẫn thực chứng (Grounding Citations) kèm số trang/vị trí chính xác `[filename, Trang X]` để làm luận cứ viết bài.
  - ➔ **Truyền sang Tab 6 (Editorial Office):** Cung cấp Content Brief và dữ liệu đối soát thực tế cho Trạm 1 (GATE 1).

## ⚖️ TUÂN THỦ 4 QUY TẮC BẤT BIẾN & ĐẠO ĐỨC NGHIÊN CỨU
1. **Evidence First & Zero Fabrication:** Mọi câu trả lời của trợ lý AI đều bắt buộc phải trích dẫn số trang/vị trí cụ thể trong tài liệu gốc.
2. **In-Place DOM Word (.docx):** Bảo toàn cấu trúc khi trích xuất tài liệu.
3. **Chuẩn hóa số thập phân tiếng Việt:** `1,5; 28,5%`.
4. **Chuẩn hóa hóa học & toán học:** Giữ nguyên các phương trình toán/hóa trong tài liệu nguồn.

## 📝 NHẬT KÝ YÊU CẦU & KẾT QUẢ XỬ LÝ
- **Yêu cầu 1:** Trả lời truy vấn RAG phải có trích dẫn nguồn trang rõ ràng.
  - *Kết quả:* Đã tích hợp cơ chế trích xuất Citation Footnotes trong câu trả lời.
- **Yêu cầu 2:** Bổ sung mô hình Open-Notebook (dựa trên kiến trúc mã nguồn mở `lfnovo/open-notebook`) để quản lý và truy xuất tài liệu đa phương thức, hỗ trợ tìm kiếm lai (BM25 + Semantic Cosine), trò chuyện đối soát nguồn (Grounded Chat) và sinh tạo sản phẩm nghiên cứu (Audio Podcast Script, Study Guide, FAQ & Phản biện luận văn, Synthesis Matrix).
  - *Kết quả:*
    - Xây dựng lớp `OpenNotebookEngine` hoàn chỉnh trong `modules/notebooklm/notebooklm_engine.py` hỗ trợ quản lý Notebooks, nạp tài liệu PDF/Word/TXT/MD, phân đoạn ngữ nghĩa (Chunking), tìm kiếm lai BM25 + Semantic Cosine, và Grounded Q&A Chat kèm chú thích trích dẫn `[Tác giả, Năm]`.
    - Phát triển Xưởng Biến Đổi Tri Thức (Transformations Studio) với 5 sản phẩm cốt lõi: Audio Podcast Overview, Academic Study Guide, FAQ & Defense Guide, Cross-Paper Synthesis Matrix, và Research Gaps Analysis.
    - Bổ sung toàn bộ REST APIs trong `modules/notebooklm/notebooklm_router.py`.
    - Thiết kế giao diện Open-Notebook 3 cột hiện đại trong `static/js/notebooklm.js` và tích hợp vào Sidebar `index.html`.
- **Yêu cầu 3 (2026-08-26):** Hoàn thiện tính năng lập Ma Trận Tổng Thuật Y Văn (Literature Review Matrix) và Trợ lý Chat trích dẫn nguồn mở chi tiết từng số trang và đoạn văn gốc.
  - *Kết quả:*
    - Bổ sung hàm `generate_literature_matrix()` trong `modules/notebooklm/notebooklm_engine.py` trích xuất 7 cột học thuật chuẩn mực (Tác giả, Tiêu đề, Mục tiêu, Phương pháp, Kết quả cốt lõi, Lỗ hổng, Đóng góp).
    - Mở rộng API `POST /api/notebooklm/notebooks/{notebook_id}/literature-matrix`.
    - Tích hợp trích dẫn số trang và đoạn trích thực tế cho AI Chatbot.
- **Yêu cầu 4 (2026-08-26):** Khắc phục toàn diện các lỗi vận hành giao diện Open-Notebook (Headers JWT, `App.toast`, endpoint `/api/files`, `NotebookLMUI.init()`, alias `generateTransform`).
- **Yêu cầu 5 (2026-08-26):** Tích hợp Purpose-Built AI OCR cho việc đọc file PDF (`abbyy/JFK-OCR` model):
  - *Kết quả:* Nạp 1-click trực tiếp các tệp PDF đã OCR kèm phân đoạn ngữ nghĩa và trích dẫn số trang chính xác (`[Tên_tệp.pdf, Trang X]`) vào bất kỳ Notebook nào trong Kho Tri Thức qua `ingest_to_open_notebook()`.
  - Bổ sung nút bấm **"📄 Đọc & OCR File PDF (ABBYY AI)"** trực tiếp trên panel Nguồn tài liệu của Kho Tri Thức.
- **Yêu cầu 6 (2026-08-26 - Multi-Agent & E2E Test Suite Validation):**
  - *Kết quả:* Kiểm thử độc lập đạt **100% PASS** qua bộ test E2E `test_open_notebook_full_flow.py` (10/10 tests PASS, 1.33s), xác thực trọn vẹn quy trình tạo Notebook, nạp đa nguồn, BM25 Indexing, Grounded Chat và xuất bản Ma trận Y văn 7 Cột.
- **Yêu cầu 8 (2026-08-27 - TẦNG 2 & TẦNG 3 TRACEABLE EVIDENCE SYSTEM):**
  - *Nhiệm vụ:* Hiện thực hóa kiến trúc bóc tách thực chứng có cấu trúc 17 trường, đối soát chéo đa nguồn, phát hiện sự đánh đổi (Trade-offs) và ma trận bao phủ (Coverage Control Matrix).
  - *Kết quả xử lý:*
    1. **TẦNG 2 (EXTRACTION):** Hiện thực hóa `extract_structured_evidence()` chuẩn hóa 17 trường (`evidence_id`, `document_id`, `research_dimension`, `claim`, `variable`, `value`, `unit`, `population_or_unit`, `geography`, `time_period`, `method`, `comparison_group`, `effect_direction`, `effect_size`, `confidence_or_uncertainty`, `source_location`, `supporting_excerpt_or_summary`).
    2. **TẦNG 3 (VALIDATION):** Xây dựng `validate_cross_document_evidence()` (phân tích agreement, partial agreement, disagreement với giải thích nguyên nhân), `detect_tradeoffs_and_contradictions()` (phát hiện trade-offs lợi ích vs chi phí, ngắn hạn vs dài hạn, tự động hóa vs bảo mật), `extract_trends_and_geographic_comparisons()`, và `evaluate_coverage_matrix()` (đánh giá tỷ lệ bao phủ theo 13 chiều A-M và quy tắc dừng stopping rule).
    3. Xây dựng `build_traceable_evidence_system()` liên kết 4 bộ dữ liệu: `DOCUMENTS` ➔ `EVIDENCE` ➔ `CLAIMS` ➔ `SYNTHESIS`.
    4. Đạt 100% PASS trên bộ kiểm thử `test_4tier_evidence_system.py`.
- **Yêu cầu 9 (2026-09-06 - Khắc Phục Tương Tác Nút Bấm & Huy Hiệu Header Open-Notebook):**
  - *Nhiệm vụ:* Sửa lỗi nút bấm chuyển thẻ không phản hồi (Grounded Chat, Hybrid Retrieval, Transformations Studio) và kích hoạt hiển thị số lượng nguồn, số đoạn trích trên thanh tiêu đề.
  - *Kết quả xử lý:*
    1. Đồng bộ định danh DOM giữa `static/js/notebooklm.js` và `static/index.html`: `switchViewTab()` nay hỗ trợ cả `open-nb-*-pane` và `open-nb-pane-*`, đảm bảo khi bấm chuyển tab thì nội dung phản hồi tức thì và nút tab được làm nổi bật với màu `#3b82f6`.
    2. Bổ sung `id="open-notebook-active-title"` và loại bỏ điều kiện ngắt sớm trong `renderNotebookHeader()`, giúp các huy hiệu `open-notebook-active-meta` (số Nguồn, số Đoạn trích, thời gian cập nhật) luôn hiển thị chính xác.

