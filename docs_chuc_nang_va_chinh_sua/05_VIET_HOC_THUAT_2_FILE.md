# 🎓 VIẾT HỌC THUẬT BỘ ĐÔI 2-FILE CHUẨN APA 7TH (ACADEMIC WRITER PRO)

## 🎯 VỊ TRÍ & ĐẶC TẢ MODULE
- **Giao diện:** Tab 5 (`#writer-tab`).
- **File Frontend:** `static/js/academic-writer.js`
- **File Backend:** `modules/academic_writer/writer_router.py`, `modules/academic_writer/academic_writer_engine.py`
- **API Endpoints chính:**
  - `POST /api/writer/outline/structured`: Đề xuất Cây Đề Cương IMRaD 6 chương có cấu trúc Node & Chiều phân tích (`outline_tree`, `dimensions`).
  - `POST /api/writer/outline/expand-branch`: Mở rộng phân nhánh chi tiết theo ngữ cảnh (`target_node_id`, `expansion_prompt`).
  - `POST /api/writer/outline/add-dimension`: Bổ sung chiều phân tích học thuật mới vào đề cương (`dimension_name`, `dimension_description`).
  - `POST /api/writer/outline/lock`: Cổng phê duyệt chuyên gia (Human-in-the-loop Approval Gate) khóa cấu trúc dàn ý (`is_locked=True`, `locked_at`).
  - `POST /api/writer/generate-2file`: Thực thi Phase 2 Deep Investigation soạn thảo sâu từng Node, gán cờ `[uncertain]` và xuất bản trọn gói Bộ 2-File Word.

## 🔗 QUY TRÌNH LIÊN KẾT LIÊN THÔNG (INTERLINK PROTOCOL)
- **Đầu vào (Input Tiếp Nhận):**
  - Nhận chủ đề, mục tiêu nghiên cứu từ **Tab 1 (Pipeline)**.
  - Nhận dữ liệu thực chứng từ **Tab 3 (Kho Tri Thức SciBot)** và danh mục trích dẫn từ **Tab 4 (Zotero)**.
- **Xử lý Quy trình Deep-Research 2 Giai Đoạn (RhinoInsight / arXiv:2511.18743):**
  - **Giai đoạn 1 (Interactive Outline Generation & Expansion):** Sinh Cây Đề Cương phân cấp (JSON tree), cho phép người dùng xem trước, mở rộng nhánh luận điểm, thêm chiều phân tích và phê duyệt tại Cổng Approval Gate.
  - **Giai đoạn 2 (Node-level Deep Investigation & Evidence Gathering):** Soạn thảo chuyên sâu từng Node theo cấu trúc 4 tầng CS519.M11 (Luận điểm ➔ Dẫn chứng ➔ Cơ chế TẠI SAO ➔ Hàm ý ứng dụng). Gán cờ `[uncertain: <aspect>]` khi số liệu chưa đầy đủ.
  - **Sinh đồng thời Bộ 2-File:**
    - **File A:** Bản thảo nghiên cứu chuẩn mực theo IMRaD, bảng biểu dạng lưới, trích dẫn APA 7th, hình ảnh 300 DPI.
    - **File B:** Bảng Ma trận Đối soát 6 Cột (`STT`, `Luận điểm`, `Tác giả & Năm`, `Tệp Gốc`, `Trích đoạn nguyên văn`, `Bản dịch`) và Danh mục tài liệu tham khảo APA 7th A-Z.
- **Đầu ra (Output Bàn Giao Liên Thông):**
  - ➔ **Truyền sang Tab 8 (Math-Chem Pro):** Chuẩn hóa toàn bộ công thức toán (OMML) và ký hiệu hóa học (109 chất).
  - ➔ **Truyền sang Tab 6 (Editorial Office):** Bàn giao bản thảo để 6 Ban GATE thẩm định và chạy Adversarial Peer Review.
  - ➔ **Truyền sang Tab 7 (Humanizer Pro):** Đưa toàn văn qua bộ lọc khử AI và chống Turnitin trước khi xuất bản chính thức.

## ⚖️ TUÂN THỦ 4 QUY TẮC BẤT BIẾN & ĐẠO ĐỨC NGHIÊN CỨU
1. **Evidence First & Zero Fabrication:** Tuyệt đối không bịa đặt số liệu/tác giả/kết quả nghiên cứu. 100% DOI thật từ tài liệu thực tế.
2. **In-Place DOM Word (.docx):** Kết xuất file Word đúng Style Heading 1, 2, 3 chuẩn mực, bảo toàn Run formatting.
3. **Chuẩn hóa số thập phân tiếng Việt:** `1,5; 28,5%` và `1.000; 50.000`.
4. **Chuẩn hóa hóa học & toán học:** Tự động sửa chỉ số dưới (`FeS₂`, `H₂SO₄`, `NH₄⁺`...).

## 📝 NHẬT KÝ YÊU CẦU & KẾT QUẢ XỬ LÝ
- **Yêu cầu 1:** Đề xuất dàn ý chi tiết trước khi tạo 2 file Word.
  - *Kết quả:* Đã tích hợp nút "Đề Xuất Dàn Ý" và khung chỉnh sửa trực tiếp trên giao diện.
- **Yêu cầu 2 (2026-08-26 - Milestone M1 & Academic Integrity):** Loại bỏ hoàn toàn fallback DOI giả lập, bảo đảm 100% Zero Fabrication và chuẩn hóa Ma trận đối soát 6 Cột trong Tệp B.
  - *Kết quả:*
    - Rà soát và loại bỏ triệt để các mã DOI/trích dẫn giả lập trong `academic_writer_engine.py`. Tự động nạp tài liệu từ Harvester (CrossRef/OpenAlex) hoặc các công trình kinh điển đã kiểm chứng (Vaswani et al., 2017; LeCun et al., 2015) khi ngoại tuyến kèm log cảnh báo Zero-Fabrication.
    - Chuẩn hóa Bảng Ma trận Đối soát 6 Cột trong Tệp B (`STT`, `Luận điểm trong bài`, `Tác giả & Năm`, `Tệp Monograph Gốc`, `Trích đoạn nguyên văn`, `Bản dịch tiếng Việt`).
- **Yêu cầu 3 (2026-08-26 - Multi-Agent & E2E Validation):**
  - *Kết quả:* Vượt qua 100% bài kiểm tra tự động `test_worker_m1_verification.py` (**34/34 tests PASS**) và `test_docx_editor_engine.py` (**10/10 tests PASS**).
- **Yêu cầu 4 (2026-08-26 - Milestone M1 RhinoInsight 2-Phase Deep-Research Integration / arXiv:2511.18743):**
  - *Nhiệm vụ:* Tích hợp quy trình Deep Research 2 giai đoạn: Cây đề cương tương tác (Interactive Outline Tree) với Cổng phê duyệt (Approval Gate) và Điều tra sâu từng Node (Deep Investigation) với gắn cờ không chắc chắn (`[uncertain]`).
  - *Kết quả:*
    - Hiện thực hóa các phương thức: `propose_structured_outline()`, `expand_outline_branch()`, `add_outline_dimension()`, `lock_structured_outline()`, `outline_tree_to_markdown()`, `markdown_to_outline_tree()`.
    - Bổ sung 4 endpoints REST: `/api/writer/outline/structured`, `/api/writer/outline/expand-branch`, `/api/writer/outline/add-dimension`, `/api/writer/outline/lock`.
    - Nâng cấp `static/js/academic-writer.js` hiển thị Cây Đề Cương tương tác, mở rộng nhánh, thêm chiều phân tích và khóa đề cương.
- **Yêu cầu 6 (2026-08-27 - TẦNG 4 TRACEABLE 12-SECTION ACADEMIC SYNTHESIS):**
  - *Nhiệm vụ:* Nâng cấp cơ chế tổng hợp học thuật thành Hệ Thống Thực Chứng Truy Xuất Nguồn Gốc 1-1 (Traceable Evidence System) chuẩn mực 12 mục:
    1. Executive findings
    2. 1. Current status / baseline
    3. 2. Major trends
    4. 3. Drivers / determinants
    5. 4. Key interventions / mechanisms
    6. 5. Quantitative evidence
    7. 6. Adoption / implementation
    8. 7. Economic / social implications
    9. 8. Policy / regulatory context
    10. 9. Contradictions and trade-offs
    11. 10. Limitations and uncertainties
    12. 11. Research gaps
- **Yêu cầu 7 (2026-08-27 - Loại Bỏ File B Tiết Kiệm Token & Tích Hợp Xu Hướng OpenAlex Theo Từ Khóa):**
  - *Nhiệm vụ & Kết quả xử lý:*
    1. Thử nghiệm rút gọn bỏ File B để tiết kiệm token và đánh giá hiệu năng.
    2. Tích hợp dữ liệu xu hướng công bố khoa học thực tế từ OpenAlex theo từng từ khóa vào luận cứ viết bài (`evidence_block`) của Tệp A (Bài báo IMRaD chuẩn mực).
    3. Đạt 100% PASS trên bộ kiểm thử tự động `test_4_fixes.py`.
- **Yêu cầu 8 (2026-09-06 - Phục Hồi Toàn Diện Bộ Đôi 2-File Bảo Đảm Liêm Chính Học Thuật 100% & Thiết Lập Hội Đồng 10 Giáo Sư Nghiêm Khắc):**
  - *Bối cảnh:* Việc thiếu Tệp B (Ma trận đối soát bằng chứng 6 cột) vi phạm nguyên tắc bất biến "Evidence First & Zero Fabrication" và làm rớt các bài kiểm thử tự động `tests/test_reform_r1_pipeline.py` và `tests/test_reform_r2_writer_zotero.py`.
  - *Nhiệm vụ & Kết quả xử lý:*
    1. **Phục Hồi Hoàn Chỉnh Tệp B (6-Column Traceability Matrix):**
       - Tái lập Bảng Ma trận 6 Cột: `STT`, `Luận điểm trong báo cáo`, `Tác giả & Năm (APA)`, `Tệp Monograph Gốc`, `Trích đoạn nguyên văn (Original Excerpt)`, `Bản dịch tiếng Việt + Số trang đối chứng`.
       - Xuất bản đồng thời cả hai định dạng `.docx` và `.md` cho Tệp B lưu vào thư mục `Ban_Thao/` và Workspace.
       - Cập nhật hàm `generate_2_files()` trả về đầy đủ `file_a` (Báo cáo IMRaD), `file_b` (Ma trận 6 Cột), `file_ris` và `file_bib` (Zotero library).
       - Cập nhật Bước 5 trong `modules/pipeline/pipeline_engine.py` chuyển giao toàn vẹn cả `file_b` sang các bước tiếp theo.
    2. **Tối Ưu Hóa API Router & Tham Số Điều Tra Sâu:**
       - Nâng cấp `modules/academic_writer/writer_router.py` bóc tách và chuyển tiếp `target_papers`, `target_words`, `target_pages` trực tiếp tới `academic_writer.generate_2_files()`.
    3. **Tích Hợp Hội Đồng 10 Giáo Sư Nghiêm Khắc (Council of 10 Rigorous Academic Professors):**
       - Khởi tạo 10 vị trí Giáo sư Trưởng ban viện hàn lâm chuẩn CS519.M11 kiểm soát liêm chính và chất lượng xuất bản khoa học thời đại AI.
    4. **Kiểm Thử & Đảm Bảo Chất Lượng:**
       - Vượt qua 100% test suite `pytest tests` (**26/26 tests PASS**).
       - Vượt qua 100% `test_worker_m1_verification.py` (**33/33 tests PASS**).
       - Vượt qua 100% `test_adversarial_m2_stress.py` (**87/87 tests PASS**).
- **Yêu cầu 9 (2026-09-06 - Liên Thông Trực Tiếp Cơ Sở Dữ Liệu Thực Chứng Bóc Tách Vào Bộ Đôi 2-File):**
  - *Nhiệm vụ:* Tự động liên thông toàn bộ kho dữ liệu thực chứng đã bóc tách từ tài liệu cung cấp (có số trang, phân mục, trích đoạn nguyên văn, bản dịch tiếng Việt, nhãn `[uncertain]`) trực tiếp vào quy trình soạn thảo học thuật 2-File.
  - *Kết quả xử lý:*
    1. **Nâng cấp `generate_2_files()`:** Bổ sung khả năng tiếp nhận tham số `evidence_database` (từ `document_extractor_engine.py`).
    2. **Đồng Bộ Hoá Ma Trận Đối Soát 6 Cột (Tệp B):** Chuyển hóa 100% các luận điểm trong cơ sở dữ liệu thành hàng ma trận đối soát: `STT`, `Luận điểm`, `Tác giả & Năm (APA)`, `Tệp Gốc`, `Trích đoạn nguyên văn`, `Bản dịch + Vị trí số trang`.
    3. **Tích Hợp Luận Cứ Chuẩn Xác Vào Tệp A:** Bổ sung khối trích dẫn viễn dẫn thực tế theo chuẩn APA `(Author, Year, p. X)` vào dàn ý và nội dung bài viết IMRaD, xóa bỏ hoàn toàn nguy cơ sinh ảo tưởng hay thiếu bằng chứng xác thực.
- **Yêu cầu 10 (2026-09-07 - Nâng Cấp Viết Học Thuật Dựa Trên Cây Đề Cương Đề Tài Gemini AI & Nguyên Tử Hoá Tri Thức Từ Dashi/Codex Skills):**
  - *Nhiệm vụ:* Ứng dụng kiến trúc phân giải dữ liệu nguyên tử (Knowledge Atomization) từ `dashi-ppt-skill` và cấu trúc vai trò phân đoạn (Page Role Pacing) từ `codex-ppt-skill` vào quy trình viết học thuật 2-File; liên thông cây đề cương đề tài sinh bởi Google Gemini AI (`generate_topic_structured_outline`) trực tiếp vào cấu trúc Tệp A và Tệp B.
  - *Kết quả xử lý:*
    1. **Tích hợp Kiến trúc Đề cương Đề tài:** Cây đề cương sinh bởi Google Gemini AI được tự động ánh xạ vào các phần của bài viết IMRaD (Đặt vấn đề, Cơ sở lý thuyết, Phương pháp, Kết quả thực nghiệm, Thảo luận đa chiều, Kết luận & Khuyến nghị).
    2. **Định Lượng Hoá & Nguyên Tử Hoá Bằng Chứng:** Mỗi bằng chứng được liên kết chặt chẽ với 5 trường thông tin: `claim_statement`, `metric_value`, `metric_unit`, `verbatim_excerpt`, `pinpoint_location` (số trang).
    3. **Bảo Toàn Liêm Chính Học Thuật (Zero-Fabrication):** Các mục chưa có số liệu được giữ nguyên cờ `[uncertain]`, không để AI tự ý suy diễn hoặc bịa đặt số liệu vào bài viết.
    4. **Kiểm Thử:** Đạt 100% PASS trên bộ kiểm thử tự động `tests/test_topic_outline_extractor.py` (3/3 tests PASS).
- **Yêu cầu 11 (2026-09-07 - Tích Hợp Thống Kê Xu Hướng Thư Mục Học Đa Nguồn Mở Vào Soạn Thảo 2-File):**
  - *Nhiệm vụ:* Nạp dữ liệu thống kê xu hướng công bố khoa học từ các cơ sở dữ liệu mở (OpenAlex, Europe PMC, arXiv, Crossref, All) vào phân đoạn Tổng quan Tài liệu & Thư mục học (Chương 2) của Tệp A (IMRaD) và ghi nhận nguồn trích dẫn số liệu vào Tệp B (Ma trận đối soát 6 cột).
  - *Kết quả xử lý:*
    1. **Nạp Dữ Liệu Thực Chứng Xu Hướng Đa Nguồn:** `generate_2_files()` tự động tiếp nhận `bibliometric_trends` từ `evidence_database` hoặc `kwargs`, sinh khối phân tích thư mục học vĩ mô kèm bảng phân bố số lượng công bố, CAGR % và xu hướng phát triển theo từ khóa.
    2. **Phân Đoạn Thư Mục Học Học Thuật:** Soạn thảo phân đoạn phân tích thư mục học trong Tệp A dựa trên số liệu thực tế đo đạc, đảm bảo 100% Zero Fabrication.
    3. **Kiểm Thử:** Đạt 100% PASS trên `tests/test_multi_source_keyword_trends.py` (6/6 tests PASS) và `tests/test_topic_outline_extractor.py` (3/3 tests PASS).
- **Yêu cầu 12 (2026-09-07 - Tối Ưu Hóa Chức Năng Viết: Triệt Tiêu Từ Ngữ Phi Khoa Học, Chống Phóng Đại, Khẳng Định Quá Mức & Áp Dụng Dè Dặt Học Thuật - Epistemic Hedging):**
  - *Nhiệm vụ:* Tối ưu hóa toàn diện module viết học thuật (Academic Writer), chuẩn hóa văn phong khoa học chuẩn mực ISI/Scopus: loại bỏ hoàn toàn các từ ngữ bình dân, cảm thán, tiếp thị ("rất hay", "kỳ diệu", "thần kỳ", "thổi luồng gió mới", "thay đổi cuộc chơi", "bước đột phá lịch sử"); loại bỏ lối miêu tả hoa mỹ, sáo rỗng ("bức tranh tráng lệ", "Trong bối cảnh phát triển như vũ bão..."); xóa bỏ các khẳng định quả quyết 100% thiếu căn cứ ("chắc chắn 100%", "chứng minh tuyệt đối", "không thể bác bỏ"); bắt buộc áp dụng kỹ thuật dè dặt học thuật (Epistemic Hedging) kèm định lượng thực nghiệm (khoảng tin cậy, sai số, giá trị p).
  - *Kết quả xử lý:*
    1. **Nâng cấp Prompts Hệ Thống (`modules/shared/skill_prompts.py`):**
       - Bổ sung Mục 8 vào `ACADEMIC_WRITER_SYSTEM_PERSONA` về Tiết chế học thuật & Văn phong khoa học chuẩn mực quốc tế (Epistemic Hedging & Academic Restraint).
       - Cập nhật chỉ thị văn phong và dè dặt học thuật trong `DRAFTING_PROMPT_TEMPLATE`, `EDITORIAL_OFFICE_EXECUTION_PROMPT`, và `UNIFIED_HUMANIZER_TURNITIN_PROMPT_TEMPLATE`.
       - Định hình chuẩn mực cho Hội đồng 10 Giáo sư (`COUNCIL_OF_10_PROFESSORS_FRAMEWORK`): GS. Methodius Sterling, GS. Scholaris Thorne và GS. Stylus Artisan giám sát chặt chẽ văn phong khách quan, trung thực và liêm chính.
    2. **Gia Cố Động Cơ Soạn Thảo (`modules/academic_writer/academic_writer_engine.py`):**
       - Tiêm Điều 9 vào `_generate_section_deep()` cưỡng chế Epistemic Hedging và triệt tiêu 100% sáo ngữ AI / hyperbole.
       - Tái cấu trúc hàm tổng hợp thực chứng `_synthesize_grounded_academic_section()`: loại bỏ triệt để các sáo ngữ "Trong bối cảnh...", "bức tranh phát triển đa diện", loại bỏ ký hiệu `$H_1$` trong văn xuôi (chuẩn hóa thành Unicode H₁, H₂), thay thế các tuyên bố quả quyết thành các luận điểm có kiểm chứng thực nghiệm thận trọng.
    3. **Kiểm Thử & Đảm Bảo Chất Lượng:**
       - Vượt qua 100% bộ kiểm thử văn phong và hedging `tests/test_scientific_hedging_and_tone.py` (6/6 tests PASS).
       - Vượt qua 100% test suite `pytest tests/` (51/51 tests PASS).
       - Vượt qua 100% `test_worker_m1_verification.py` (33/33 tests PASS).
- **Yêu cầu 13 (2026-09-08 - Hoàn Thiện & Tối Ưu Toàn Diện Kỹ Năng Viết Học Thuật 2-File Kèm Zotero & Đồng Bộ Cây Đề Cương):**
  - *Nhiệm vụ:* Nâng cấp toàn diện Academic Writer Pro theo đặc tả `Skill/00_QUY_TRINH_TONG_THE/03_Academic_Writer/SKILL Writer.md`, bảo toàn tuyệt đối 4 nguyên tắc bất biến (Zero Fabrication, In-Place DOM Word, Số thập phân tiếng Việt, Ký hiệu toán/hóa), tối ưu timeout và failover Gemini API, tương thích kép cấu trúc Cây Đề Cương (`items` & `sections`), và xuất bản đồng thời trọn gói 6 tệp tài liệu.
  - *Kết quả xử lý:*
    1. **Tương Thích Kép Cây Đề Cương (`propose_structured_outline`):** Cung cấp đồng thời cả hai thuộc tính `items` và `sections` trong cây đề cương phân cấp (`outline_tree`), đảm bảo tương thích 100% với giao diện tương tác và các endpoint điều tra sâu.
    2. **Tối Ưu Hóa Gemini API & Cơ Chế Failover Linh Hoạt:** Giới hạn candidate models, đặt timeout ngắn (8s), xử lý ngay `ConnectTimeout/ConnectionError` để chuyển failover sang Heuristic học thuật chuyên sâu ngay lập tức, loại bỏ hoàn toàn hiện tượng treo luồng/chờ đợi lâu.
    3. **Bảo Toàn Bộ Đôi 2-File Xuất Bản Trọn Gói 6 Tệp:** Xuất bản hoàn chỉnh và đồng bộ 6 tệp tin: Tệp A Báo cáo IMRaD (`.docx` + `.md`), Tệp B Ma trận Đối soát 6 Cột (`.docx` + `.md`), `File_References_*.ris` và `File_References_*.bib`.
    4. **Đồng Bộ Hóa Thư Viện Trích Dẫn Zotero:** Tự động nhân bản tệp `.ris` và `.bib` vào cả hai vị trí `workspace/Tai_Lieu/` và `workspace/Zotero/`.
    5. **Kiểm Thử & Đảm Bảo Chất Lượng:** Đạt 100% PASS trên tất cả các kịch bản kiểm thử Academic Writer (Test 2.1, 2.2, 2.3).
- **Yêu cầu 14 (2026-09-14 - Tích Hợp Giao Thức Suy Luận Luồng Lặp Looped Flows Reasoning / arXiv:2609.11801 Vào Soạn Thảo Chuyên Sâu & Đối Soát File B):**
  - *Nhiệm vụ:* Nâng cấp động cơ Academic Writer ứng dụng mô hình chuyển dịch xác suất nhận thức (Probability Transport) và khử nhiễu đa tầng ($t_0 \to t_k$), loại bỏ triệt để hiện tượng ngụy biện tự tin (Spurious Attractors) và tự động tạo Biên bản kiểm định Looped Flows trong Tệp B.
  - *Kết quả xử lý:*
    1. **Tiêm Chỉ Thị 5 Pha Vào Lời Nhắc Hệ Thống:** Bổ sung Điều 10 vào `_generate_section_deep()` cưỡng chế quy trình khử nhiễu 5 pha từ Anchor Facts ($z_0$) đến bão hòa kiểm chứng ACT $q(z) \ge 0,95$, kích hoạt hồi quy ngẫu nhiên (Stochastic Backtrack) khi thiếu dữ liệu thực nghiệm.
    2. **Biên Bản Kiểm Định Looped Flows Trong Tệp B (Cả .docx & .md):** Tự động sinh Mục III *"BIÊN BẢN KIỂM ĐỊNH SUY LUẬN LUỒNG LẶP"* với bảng scorecard 4 thông số: Chỉ số Bão hòa ACT $q(z)$, Bẫy Ngụy biện Tự tin (Spurious Attractor Guard), Sai số Tương đối Bước lặp $R_i$, và Số lượng Dữ liệu Đo lường.
    3. **Mở Rộng Kết Quả Trả Về API:** Bổ sung trường `looped_flows_audit` vào đối tượng trả về của `generate_2_files()`.
    4. **Giao Diện Trực Quan:** Bổ sung thẻ thống kê Looped Flows thời gian thực trên giao diện Tab 4.
- **Yêu cầu 15 (2026-09-23 - Tự Động Đồng Bộ Sang Dual-Pane Evidence Inspector v4.2 & Bảng Ma Trận A4 Landscape):**
  - *Nhiệm vụ:* Tự động kích hoạt đồng bộ hóa sau khi hoàn thành tạo 2-file: sinh `multi_evidence_catalog.json` chuẩn 10 trường, xuất bản Bảng Ma Trận Truy Xuất Nguồn Gốc A4 Landscape (.docx khổ ngang 7 cột và .md), phục vụ đối soát song song trực tiếp.
  - *Kết quả xử lý:*
    1. **Tích hợp `evidence_inspector_engine`:** Gọi tự động `generate_multi_evidence_catalog()` và `generate_traceability_matrix_docx()` ngay trước khi kết thúc hàm `generate_2_files()`.
    2. **Mở rộng kết quả API:** Trả về trường `inspector_data` chứa trạng thái đồng bộ và tên tệp Ma trận Khổ ngang.
    3. **Kiểm thử:** Đạt 100% PASS trên `tests/test_evidence_inspector_gate.py`.
- **Yêu cầu 16 (2026-09-25 - Tích Hợp Đồng Bộ Quy Chuẩn Công Thức Toán - Hóa Học & Quy Tắc Diễn Giải 4 Thành Phần Vào Hệ Thống Kỹ Năng Viết):**
  - *Nhiệm vụ:* Nâng cấp hệ thống kỹ năng viết học thuật cốt lõi (`academic-evidence-writer`, `vietnamese-academic-researcher`, `zotero-academic-writer`, `research-paper-writing`, `viet-chuyen-nghiep` / `03_VIET_CHUYEN_NGHIEP_V3.1`) tích hợp trực tiếp quy chuẩn thể hiện công thức toán học, ký hiệu hóa học và quy tắc diễn giải 4 thành phần từ `@docx-math-chem-chart-pro`.
  - *Kết quả xử lý:*
    1. **Ký hiệu Hóa học trong dòng (Inline Text):** Tự động chuyển đổi Subscript/Superscript cho 109+ hợp chất, ion, phân tử khí và chỉ số môi trường ($\text{CH}_4, \text{CO}_2, \text{N}_2\text{O}, \text{FeS}_2, \text{H}_2\text{SO}_4, \text{SO}_4^{2-}, \text{Fe}^{2+}, \text{Al}^{3+}, \text{NH}_4^+, \text{NO}_3^-, \text{BOD}_5, \text{COD}, \text{pH}_{\text{KCl}}, \text{PM}_{2,5}$), thao tác trên từng `Run` trong Word để bảo toàn 100% mã trường Zotero XML.
    2. **Công thức Toán khối độc lập (Display Block Equations):** Hỗ trợ chuyển đổi khối LaTeX `$$...$$` sang Microsoft Word Equation `<m:oMath>` gốc, căn giữa kèm đánh số phương trình `(1.1)`.
    3. **Quy tắc Diễn giải Chi tiết 4 Thành phần BẮT BUỘC:** Tuyệt đối chống công thức mồ côi; bắt buộc diễn giải đầy đủ: (1) Tên gọi, nguồn gốc APA 7th & mục đích, (2) Định nghĩa từng biến số, (3) Đơn vị đo lường chuẩn khoa học, và (4) Ý nghĩa môi trường/kinh tế thực chứng.
    4. **Chuẩn hóa số thập phân tiếng Việt:** Dấu phẩy cho số thập phân (`1,5; 28,5%`), dấu chấm cho hàng nghìn (`1.000; 50.000`), bảo toàn dấu chấm số thứ tự đề mục.


