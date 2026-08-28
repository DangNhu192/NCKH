# Original User Request

## 2026-08-26T09:09:32Z

Requested team: Đội ngũ Đa Tác Nhân Phản Biện Chéo & Hoàn Thiện Toàn Diện WEB SUPER & Hệ Thống Skill

Điều phối đội ngũ Đa Tác Nhân AI (Multi-Agent Teamwork) phân vai chuyên biệt theo mô hình Tòa soạn 6 Ban & The Academic Agency để phản biện chéo đối kháng (Adversarial Peer Review), kiểm toán kỹ thuật toàn diện và chỉnh sửa hoàn thiện toàn bộ các Skill (00-06) cùng 8 phân hệ chức năng cốt lõi của nền tảng WEB SUPER.

Working directory: H:\My Drive\Ho so ca nhan\b. ThS KHMT\Skill\Web Super
Integrity mode: development

## Requirements

### R1. Phản Biện Chéo & Kiểm Toán Tính Liêm Chính Học Thuật (Zero Fabrication & Academic Integrity)
Thiết lập hội đồng phản biện học thuật độc lập (Peer-Review Board) rà soát toàn bộ các Skill (`01_BO_NAO_AI_RESEARCHER`, `02_THU_THAP_PDF_VA_ZOTERO`, `03_VIET_CHUYEN_NGHIEP_V3.1`, `SKILL.md`) và các module backend/frontend: đảm bảo 100% số liệu đo đạc, DOI, tên tác giả, năm xuất bản và mã trích dẫn Zotero CSL XML (`w:fldSimple`, `w:instrText`), Harvester Pro và Kho Tri Thức (Open-Notebook RAG) có căn cứ thực chứng xác thực, tuyệt đối không bịa đặt (Zero Fabrication).

### R2. Kiểm Thử & Bảo Toàn Cấu Trúc Word (.docx) In-Place DOM & Chuẩn Hóa Toán - Hóa Học
Kiểm thử và tối ưu hóa bộ công cụ xử lý tệp Word và hiển thị ký hiệu khoa học (`modules/shared/docx_styler.py`, `modules/workspace/docx_editor_engine.py`, `modules/math_chem/math_chem_engine.py`): bảo toàn 100% Heading Styles (1/2/3), bảng mục lục động, bảng số liệu dạng lưới, biểu đồ/sơ đồ quy trình 300 DPI, công thức toán khối $\LaTeX$ / OMML và chỉ số dưới/trên cho các hợp chất hóa học (`FeS₂`, `H₂SO₄`, `NH₄⁺`, `NO₃⁻`, `Ca(OH)₂`, `BOD₅`, `COD`...).

### R3. Tối Ưu Hóa Hiệu Năng Phân Hệ PDF AI OCR & BigQuery AI/ML Analytics
Tối ưu hóa và kiểm thử chuyên sâu hệ thống đọc PDF quang học Purpose-Built Document AI (`modules/shared/pdf_ocr_engine.py` theo mô hình `abbyy/JFK-OCR` + Gemini Multimodal Vision AI) và phân hệ phân tích dữ liệu lớn (`modules/bigquery/bigquery_engine.py`): đảm bảo khả năng phục hồi lớp chữ tìm kiếm, bóc tách bảng số liệu dạng lưới, tạo RAG Semantic Chunks có trích dẫn số trang chính xác (`[Tên_tệp.pdf, Trang X]`) và các mô hình BigQuery AI (`AI.FORECAST`, `AI.DETECT_ANOMALIES`, `AI.KEY_DRIVERS`, NL2SQL).

### R4. Đồng Bộ Hóa Toàn Bộ Tài Liệu Đặc Tả & Tự Động Hóa Kiểm Định 4 Lớp
Cập nhật đầy đủ và đồng bộ tất cả các tệp tài liệu đặc tả chức năng trong thư mục `docs_chuc_nang_va_chinh_sua/` theo đúng Quy trình 3 Bước (Đọc trước -> Thực thi & kiểm thử -> Cập nhật nhật ký), đảm bảo công cụ kiểm tra chéo tự động `tools_cross_validate_docs.py` và tất cả các test suites đạt chuẩn 100% PASS.

## Acceptance Criteria

### Tính Xác Thực & Liêm Chính Học Thuật (Integrity & Citations)
- [ ] 100% trích dẫn trong Tệp A (Báo cáo chính thức APA 7th) và Bảng Ma trận Đối soát 6 Cột trong Tệp B có đối chứng DOI và tệp PDF thực tế trong `Tai_Lieu/`.
- [ ] Mã trường XML Zotero (`w:fldSimple` / `w:instrText`) mở trong Microsoft Word ấn nút Refresh nhận diện tự động và trích xuất danh mục tài liệu tham khảo chính xác.

### Bảo Toàn DOM Word (.docx) & Chuẩn Hóa Định Dạng Tiếng Việt
- [ ] Quá trình đọc, chỉnh sửa và lưu tệp Word (.docx) bảo toàn nguyên vẹn 100% hình ảnh 300 DPI, bảng biểu dạng lưới và cấu trúc phân cấp Heading 1/2/3.
- [ ] Ký hiệu hóa học hiển thị chính xác chỉ số dưới/trên; công thức toán khối hiển thị chuẩn xác dạng OMML/LaTeX.
- [ ] Toàn bộ số thập phân tiếng Việt được chuẩn hóa sử dụng dấu phẩy (`1,5; 28,5%; 0,05`) và dấu chấm cho hàng nghìn (`1.000; 50.000`).

### Hiệu Năng & Ổn Định Của PDF AI OCR & BigQuery AI
- [ ] Engine `pdf_ocr_engine.py` nhận diện chính xác lớp chữ (Digital vs Scan thuần ảnh), xuất file Word `.docx` 300 DPI và nạp 1-click vào Open-Notebook với đầy đủ RAG Chunks.
- [ ] Module BigQuery AI sinh câu lệnh SQL chuẩn xác cho dự báo/dị biệt/key drivers và xuất bản báo cáo phân tích định lượng `.docx` hoàn chỉnh.

### Kiểm Thử Tự Động & Đồng Bộ Toàn Diện (Automated Verification)
- [ ] Script `tools_cross_validate_docs.py` chạy thành công đạt 100% PASS trên tất cả 4 lớp kiểm định (Vị trí, Liên thông, 4 Quy tắc, Codebase Mapping & Endpoints).
- [ ] Các bộ kiểm thử tự động (`test_pdf_ocr_full_flow.py`, `test_open_notebook_full_flow.py`, `test_docx_editor_engine.py`, `test_server_load.py`) đạt 100% PASS.

## 2026-08-26T10:21:50Z

Requested team: Đội ngũ Đa Tác Nhân Tích Hợp Deep-Research-Skills, SciBot & Hoàn Thiện Toàn Diện WEB SUPER

Tích hợp kiến trúc Deep Research 2 giai đoạn (từ `deep-research-skills` / RhinoInsight) và Chatbot Khoa Học chuyên sâu dựa trên Embeddings / Cấu trúc tài liệu (từ `SciBot`), đồng thời phân vai AI phản biện chéo đối kháng để hoàn thiện toàn bộ các Skill và phân hệ nghiên cứu của WEB SUPER.

Working directory: H:\My Drive\Ho so ca nhan\b. ThS KHMT\Skill\Web Super
Integrity mode: development

## Requirements

### R1. Tích Hợp Workflow 2 Giai Đoạn Từ Deep-Research-Skills
Tích hợp phương pháp luận Deep Research (RhinoInsight / arXiv:2511.18743) vào `01_BO_NAO_AI_RESEARCHER` và phân hệ Academic Writer / Quy trình 7 bước:
- **Giai đoạn 1 (Interactive Outline Generation & Expansion):** Cho phép người dùng xem trước, bổ sung nhánh luận điểm và duyệt đề cương chi tiết trước khi tiến hành viết sâu.
- **Giai đoạn 2 (Deep Investigation & Evidence Gathering):** Soạn thảo chi tiết từng phần dựa trên dữ liệu thực chứng đa nguồn, trích xuất số liệu định lượng và gán trích dẫn chuẩn mực APA 7th.

### R2. Tích Hợp Kiến Trúc Scientific Domain-Specific Chatbot & Embeddings Từ SciBot
Nâng cấp phân hệ Kho Tri Thức (Open-Notebook) và Harvester Pro với các kỹ thuật từ `SciBot` (Digital Discovery / DOI:10.1039/D3DD00112A):
- Bóc tách cấu trúc khoa học sâu cho tệp PDF/Docx học thuật (Tiêu đề, Tác giả, Abstract, Phương pháp luận, Kết quả, Công thức toán, Danh mục tài liệu tham khảo).
- Tối ưu hóa Vector Embedding khoa học và thuật toán xếp hạng hybrid (BM25 + N-gram Cosine Similarity) cho Grounded Chat và Ma Trận Y Văn 7 Cột.

### R3. Phân Vai Phản Biện Chéo Đối Kháng & Kiểm Toán Liêm Chính (Adversarial Peer-Review)
Thiết lập hội đồng đặc vụ chuyên trách theo mô hình 6 Ban GATE & Agency-Agents để kiểm toán 4 nguyên tắc bất biến: Zero-Fabrication (100% DOI thật), bảo toàn Word (.docx) In-Place DOM, chuẩn hóa số thập phân tiếng Việt (`1,5; 28,5%`) và ký hiệu Toán - Hóa học (`FeS₂`, `H₂SO₄`, `NH₄⁺`, $\LaTeX$/OMML).

### R4. Tự Động Hóa Kiểm Thử E2E & Đồng Bộ Đặc Tả 4 Lớp
Mở rộng bộ kiểm thử E2E tự động bao phủ các tính năng mới và đồng bộ 100% tài liệu trong `docs_chuc_nang_va_chinh_sua/` qua `tools_cross_validate_docs.py`.

## Acceptance Criteria

### Tính Năng Deep Research & SciBot Ingestion
- [ ] Giao diện và API Academic Writer hỗ trợ quy trình 2 giai đoạn: xem trước/hiệu chỉnh đề cương phân nhánh và điều tra sâu từng phần độc lập.
- [ ] Kho Tri Thức hỗ trợ đọc và bóc tách tài liệu khoa học cấu trúc cao theo mô hình SciBot, sinh Ma Trận Y Văn và Grounded Chat kèm trích dẫn chính xác.

### Liêm Chính Học Thuật & Bảo Toàn Cấu Trúc Word
- [ ] 100% trích dẫn trong bài báo (Tệp A) và Bảng Ma trận Đối soát 6 Cột (Tệp B) có DOI thật và tệp PDF thực tế trong `Tai_Lieu/`.
- [ ] Xuất bản tệp Word .docx bảo toàn 100% Runs formatting, bảng số liệu dạng lưới, biểu đồ 300 DPI và mã trường XML Zotero (`w:fldSimple`).

### Kiểm Thử Tự Động & Đồng Bộ Toàn Diện
- [ ] Toàn bộ các bộ kiểm thử E2E (`test_pdf_ocr_full_flow.py`, `test_open_notebook_full_flow.py`, `test_docx_editor_engine.py`, `test_server_load.py`) và `tools_cross_validate_docs.py` đạt **100% PASS**.
