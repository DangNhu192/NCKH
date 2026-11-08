# ✨ KHỬ DẤU VẾT AI & CHỐNG ĐẠO VĂN TURNITIN HỌC THUẬT (HUMANIZER & TURNITIN PRO)

## 🎯 VỊ TRÍ & ĐẶC TẢ MODULE
- **Giao diện:** Tab 7 (`#humanizer-tab`).
- **File Frontend:** `static/js/humanizer.js`
- **File Backend:** `modules/humanizer/humanizer_router.py`, `modules/humanizer/humanizer_engine.py`, `modules/shared/skill_prompts.py`

## 🔗 QUY TRÌNH LIÊN KẾT LIÊN THÔNG (INTERLINK PROTOCOL)
- **Đầu vào (Input Tiếp Nhận):**
  - Nhận văn bản hoặc file Word (.docx) được tạo ra từ **Tab 5 (Academic Writer)** hoặc **Tab 6 (Editorial Office)** hoặc do người dùng dán vào.
- **Xử lý Đồng Bộ Hợp Nhất 1-Click (`POST /api/humanize/unified-process`):**
  - **Nhiệm vụ 1 (Khử AI):** Biến thiên nhịp câu sóng 3 tầng (Burstiness $\sigma$), triệt tiêu 100% Wikipedia Tells & ContentBeta 300+ buzzwords.
  - **Nhiệm vụ 2 (Chống Turnitin):** 5 Kỹ thuật Rephrase phá vỡ chuỗi n-gram 8–16 từ.
  - **Bảo toàn In-Place DOM Word (.docx):** Xử lý trực tiếp từng XML Paragraph/Run trong file Word.
- **Đầu ra (Output Bàn Giao Liên Thông):**
  - ➔ **Bàn giao Thành phẩm Cuối cùng:** File Word (.docx) hoàn hảo đạt **Turnitin Similarity < 8%** và **Human Score > 95%**.
  - ➔ **Truyền sang Workspace & History:** Lưu trữ file sạch và ghi nhận Audit Log.

## ⚖️ TUÂN THỦ 4 QUY TẮC BẤT BIẾN & ĐẠO ĐỨC NGHIÊN CỨU
1. **Evidence First & Zero Fabrication:** Giữ nguyên vẹn 100% số liệu thực nghiệm, tác giả, DOI và kết quả gốc.
2. **In-Place DOM Word (.docx):** Bảo toàn 100% Heading styles, Mục lục tự động, Bảng biểu, Hình ảnh, Công thức OMML và Mã trường Zotero XML (`w:fldChar` / `w:fldSimple`).
3. **Chuẩn hóa số thập phân tiếng Việt:** `1,5; 28,5%` và `1.000; 50.000`.
4. **Chuẩn hóa hóa học & toán học:** Tự động sửa `FeS₂`, `H₂SO₄`, `NH₄⁺`, `NO₃⁻`, `CO₂`, `CH₄`...

## 📝 NHẬT KÝ YÊU CẦU & KẾT QUẢ XỬ LÝ
- **Yêu cầu 1:** Sửa lỗi hiển thị `undefined%` và `None` ở Báo cáo Plagiarism Audit.
  - *Kết quả:* Đã xử lý ép kiểu an toàn, tích hợp Bộ phân tích tất định cục bộ và Markdown Renderer.
- **Yêu cầu 2:** Gộp 2 nút "Khử Lỗi AI & Làm Mượt" và "Chống Đạo Văn Turnitin" làm 1 nút duy nhất đáp ứng 4 Quy tắc Bất biến.
  - *Kết quả:* Đã tạo nút `btn-humanize-unified`, viết prompt `UNIFIED_HUMANIZER_TURNITIN_PROMPT_TEMPLATE`, cập nhật engine và router, kiểm thử live đạt 100%.
- **[2026-08-25 11:18] Yêu cầu 3:** Hoàn thiện evaluate_academic_quality_scorecard trong HumanizerEngine, trả về bảng đánh giá 4 vai trò Hội đồng và chỉ số Turnitin < 8%.
- **Yêu cầu 4 (2026-08-26 - Milestone M1 & Academic Integrity):** Khắc phục triệt để logic kiểm tra phân lập DOI trong chuẩn hóa số thập phân tiếng Việt.
  - *Kết quả:*
    - Thay thế điều kiện `val.startswith("10.")` bằng regex phân lập DOI nghiêm ngặt `re.match(r'^10\.\d{4,9}/', val)`.
    - Bảo đảm 100% các số thực từ `10.0` đến `10.999` (ví dụ `10,5%`, `10,25 mg/L`, `10,0`, `10,999 kg`) được chuyển đổi chính xác sang dấu phẩy tiếng Việt mà không làm sai lệch mã DOI.
- **Yêu cầu 5 (2026-08-26 - Multi-Agent & E2E Validation):**
  - *Kết quả:* Xác thực toàn diện qua `test_worker_m1_verification.py` (**34/34 tests PASS**) và `test_docx_editor_engine.py` (**10/10 tests PASS**).
- **Yêu cầu 7 (2026-08-27 - Khắc Phục Lỗi Mất Nội Dung Sau Khi Khử AI Ở Bước 7):**
  - *Nhiệm vụ:* Sửa lỗi Bước 7 chạy xong chỉ còn tên đề tài mà mất toàn bộ nội dung bài báo.
  - *Nguyên nhân:* Logic quét file tại Bước 7 sử dụng tiền tố cũ `Bao_cao_*.md` trong thư mục `drafts`, trong khi Academic Writer lưu file với tên `File_A_{topic}.md` trong `Tai_Lieu/` → `raw_text` rỗng → Humanizer trả về rỗng.
  - *Kết quả xử lý:*
    1. Thiết kế cơ chế quét file 4 tầng: `file_a_rel` parameter → `Tai_Lieu/File_A_*.md` → `Tai_Lieu/Bao_cao_*.md` → `Ban_Thao/`.
    2. Bổ sung kiểm tra an toàn (Integrity Guard) trước khi xử lý, cảnh báo rõ nếu không tìm thấy bản thảo thay vì lưu file rỗng.
    3. Kiểm tra độ dài văn bản sau khi Humanize: nếu kết quả trả về quá ngắn (< 20% bản gốc) do lỗi mạng/API, tự động bảo toàn bản gốc để không bao giờ làm mất nội dung người dùng.
    4. Xuất bản đồng bộ `.docx` và `.md` hoàn thiện vào `Xuat_Ban/` và hiển thị đầy đủ trên giao diện.
    5. Đạt 100% PASS trên bộ kiểm thử tự động `test_4_fixes.py`.
- **Yêu cầu 8 (2026-09-07 - Tích Hợp Kiểm Toán Văn Phong Khoa Học & Triệt Tiêu Sáo Ngữ Khẳng Định Quá Mức / Miêu Tả Hoa Mỹ):**
  - *Nhiệm vụ:* Mở rộng từ điển sáo ngữ và bổ sung bộ kiểm toán chuyên sâu về tiết chế học thuật (Scientific Hedging Audit) nhằm phát hiện, tính điểm và tự động thay thế các cụm từ khẳng định quá mức, phóng đại giật gân, miêu tả hoa mỹ và từ ngữ phi khoa học.
  - *Kết quả xử lý:*
    1. **Mở Rộng Từ Điển Thay Thế Tự Động (`CONTENTBETA_VIETNAMESE_CLICHES` & `LOCAL_REPLACEMENT_MAP`):** Bổ sung hơn 20 cặp từ ngữ thay thế các biểu đạt sáo rỗng ("bước đột phá lịch sử" ➔ "tiến bộ kỹ thuật ghi nhận được", "thay đổi cuộc chơi" ➔ "tạo ra phương thức tiếp cận mới", "khẳng định chắc chắn" ➔ "kết quả bước đầu cho thấy", "vô cùng hoàn hảo" ➔ "đáp ứng tốt tiêu chuẩn thiết kế", "bức tranh tráng lệ" ➔ "tổng quan tình hình").
    2. **Thiết Lập Bộ Quy Tắc Nhận Diện Vi Phạm (`SCIENTIFIC_HEDGING_VIOLATIONS`):** Phân loại 4 nhóm vi phạm: `over_assertion` (khẳng định quá mức), `over_emphasis` (nhấn mạnh quá đà), `purple_prose` (miêu tả hoa mỹ), `non_academic` (từ ngữ phi khoa học).
    3. **Hàm Kiểm Toán Dè Dặt Học Thuật (`audit_scientific_hedging`):** Tính điểm chuẩn mực học thuật từ 0 đến 100, liệt kê chi tiết các vi phạm theo từng phân nhóm và trả về gợi ý cải thiện văn phong. Tích hợp trực tiếp vào quy trình phân tích văn bản `analyze()`.
    4. **Kiểm Thử:** Đạt 100% PASS trên `tests/test_scientific_hedging_and_tone.py` và toàn bộ test suite dự án.

