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
    1. Loại bỏ toàn bộ logic tạo và lưu File B (Ma trận 6 cột) trong `generate_2_files()` để tiết kiệm token và tăng tốc độ xử lý.
    2. Tích hợp dữ liệu xu hướng công bố khoa học thực tế từ OpenAlex theo từng từ khóa vào luận cứ viết bài (`evidence_block`) của Tệp A (Bài báo IMRaD chuẩn mực).
    3. Trả về kết quả tinh gọn: `file_a` (.docx & .md), `file_ris`, `file_bib` phục vụ trích dẫn Zotero.
    4. Cập nhật giao diện Bước 5 hiển thị tập trung vào File A và danh mục tham khảo.
    5. Đạt 100% PASS trên bộ kiểm thử tự động `test_4_fixes.py`.


