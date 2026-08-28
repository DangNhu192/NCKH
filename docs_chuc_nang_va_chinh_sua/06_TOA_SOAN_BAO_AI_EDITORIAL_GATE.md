# 🏢 TÒA SOẠN BÁO AI V3.1 & CHU TRÌNH 4 TRẠM GATE (EDITORIAL OFFICE PRO)

## 🎯 VỊ TRÍ & ĐẶC TẢ MODULE
- **Giao diện:** Tab 6 (`#editorial-tab`).
- **File Frontend:** `static/js/editorial-office.js`
- **File Backend:** `modules/editorial_office/editorial_router.py`, `modules/editorial_office/editorial_engine.py`
- **API Endpoints chính:**
  - `POST /api/editorial/analyze`: Phân tích sơ bộ bản thảo và đề xuất tuyến bài.
  - `POST /api/editorial/execute-gate`: Thực thi quy trình từng trạm GATE (GATE 1 ➔ GATE 4).
  - `POST /api/editorial/evaluate-q1`: Thẩm định chất lượng học thuật theo Rubric Q1 ISI/Scopus (thang điểm 100).
  - `POST /api/editorial/adversarial-review`: Thiết lập Hội đồng Phản biện Đối kháng 2 Reviewer và soạn thảo Thư Giải trình (Rebuttal Letter).

## 🔗 QUY TRÌNH LIÊN KẾT LIÊN THÔNG (INTERLINK PROTOCOL)
- **Đầu vào (Input Tiếp Nhận):**
  - Nhận bản thảo từ **Tab 5 (Academic Writer)** hoặc tệp Word tư liệu kéo thả vào Drop-Zone.
  - Nhận dữ liệu thực tế từ **Tab 2 (Harvester)** và **Tab 3 (Kho tri thức SciBot)**.
- **Xử lý Qua Hội Đồng 6 Ban & 4 Trạm GATE Khép Kín:**
  - **Hội đồng 6 Ban Chuyên Trách:**
    1. *Ban Nghiên cứu & Dữ liệu (Research & Fact-Checking Board)*
    2. *Ban Thư ký & Biên tập (Editorial & Structuring Board)*
    3. *Ban Thẩm định & Phản biện (Peer-Review & Quality Assurance Board)*
    4. *Ban Chế bản & Xuất bản (Publishing & Formatting Board)*
    5. *Ban Lưu trữ & Tư liệu (Archive & Evidence Vault Board)*
    6. *Ban Phát triển & Công nghệ (Development & AI Engineering Board)*
  - **Chu trình 4 Trạm GATE:**
    - `GATE 1 (Research Board):` Lập Content Brief & Dữ liệu thực chứng.
    - `GATE 2 (Editorial Board):` Soạn thảo bản thảo báo chí chuyên sâu đa góc nhìn.
    - `GATE 3 (Review Board):` Lập biên bản kiểm duyệt chất lượng, fact-check, đạo đức báo chí, Q1 Rubric Scoring (5 tiêu chí, 100đ).
    - `GATE 4 (Publishing Board):` Định dạng xuất bản hoàn tất (DOCX/Markdown In-Place DOM).
  - **Hội Đồng Phản Biện Đối Kháng 2 Reviewer (Adversarial Peer-Review):**
    - *Reviewer 1:* Phản biện lý thuyết, tính mới và phương pháp luận.
    - *Reviewer 2:* Chất vấn tính vững chắc thực nghiệm, dữ liệu và ứng dụng thực tiễn.
    - *Rebuttal Letter:* Tự động soạn thư giải trình và kế hoạch tiếp thu chỉnh sửa.
- **Đầu ra (Output Bàn Giao Liên Thông):**
  - ➔ **Truyền sang Tab 7 (Humanizer Pro):** Thẩm định nguy cơ trùng lặp và làm mượt giọng văn tự nhiên như nhà báo chuyên nghiệp.
  - ➔ **Truyền sang Workspace & History:** Lưu trữ bản thảo xuất bản.

## ⚖️ TUÂN THỦ 4 QUY TẮC BẤT BIẾN & ĐẠO ĐỨC NGHIÊN CỨU
1. **Evidence First & Zero Fabrication:** Fact-check 100% số liệu thực tế tại Trạm GATE 1 & GATE 3.
2. **In-Place DOM Word (.docx):** Bảo toàn cấu trúc bài viết khi xuất bản Word.
3. **Chuẩn hóa số thập phân tiếng Việt:** `1,5; 28,5%`.
4. **Chuẩn hóa hóa học & toán học:** Tự động sửa ký hiệu kỹ thuật (`FeS₂`, `H₂SO₄`, `NH₄⁺`...).

## 📝 NHẬT KÝ YÊU CẦU & KẾT QUẢ XỬ LÝ
- **Yêu cầu 1:** Kéo thả tệp Word (.docx) trực tiếp vào Drop-Zone của Tòa soạn để tự động trích xuất.
  - *Kết quả:* Đã tích hợp bộ lắng nghe sự kiện kéo thả file Word trên `#editorial-drop-zone`.
- **Yêu cầu 2 (2026-08-26):** Bổ sung quy trình Phản biện 2 Vòng chuẩn Rubric Q1 ISI/Scopus và Chế độ Tranh luận Học thuật AI (Adversarial Peer-Review).
  - *Kết quả:*
    - Tích hợp hàm `evaluate_manuscript_q1_rubric()` chấm điểm 5 tiêu chí chuẩn quốc tế (Tính mới 25đ, Phương pháp 25đ, Số liệu 20đ, Trích dẫn APA 7th 15đ, Ý nghĩa thực tiễn 15đ). Ngưỡng quyết định: Accept ($\ge 85$), Minor Revision ($70-84$), Major Revision ($< 70$).
    - Tích hợp hàm `conduct_adversarial_peer_review()` giả lập 2 Reviewer ẩn danh (Phương pháp vs. Thực nghiệm) và tự động soạn thảo Thư Giải trình Phản biện (Rebuttal Letter).
    - Bổ sung các REST endpoints `POST /api/editorial/evaluate-q1` và `POST /api/editorial/adversarial-review`.
- **Yêu cầu 3 (2026-08-26 - Multi-Agent & E2E Validation):**
  - *Kết quả:* Xác thực toàn diện qua `test_server_load.py` (8/8 tests PASS) và kiểm toán chéo `tools_cross_validate_docs.py` đạt **100% PASS**.
- **Yêu cầu 4 (2026-08-26 - Milestone M3 Editorial Office & Invariants Hardening):**
  - *Nhiệm vụ:* Gia cố xử lý phòng thủ cho `editorial_engine.py` (xử lý an toàn chuỗi rỗng/None), đảm bảo tính bền vững của Tòa soạn 6 Ban và Q1 Rubric.
  - *Kết quả:*
    - Ép kiểu an toàn `content_str = str(content or "")` và `topic_str = str(topic or "Bài Báo Khoa Học")`.
    - Vượt qua 100% các kịch bản kiểm thử tải cực đoan và phản biện đối kháng với 0 lỗi.

