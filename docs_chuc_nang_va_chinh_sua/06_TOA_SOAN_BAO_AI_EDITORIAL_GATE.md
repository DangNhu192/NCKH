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
- **Yêu cầu 5 (2026-09-06 - Hợp Nhất Hội Đồng 10 Giáo Sư Nghiêm Khắc & Ban Phản Biện Đối Kháng Red-Teaming):**
  - *Nhiệm vụ & Kết quả xử lý:*
    1. **Tích Hợp Trưởng Ban Phản Biện Độc Lập:** Bổ sung vị trí GS. Adversarius Grimm (*Adversarial Red-Teaming & Blind Peer-Review Chair*) đóng vai Reviewer 2 khó tính, thách thức các giả định nền tảng, bóc trần tương quan giả và thiết lập bộ 10 câu hỏi phản biện gắt gao.
    2. **Đồng Bộ Hóa Quy Trình 4 Trạm GATE:** Phối hợp chặt chẽ giữa Ban Soạn thảo (GS. Scholaris Thorne), Ban Liêm chính (GS. Veritas Proctor), Ban Phân tích Định lượng (GS. Quantus Maxwell) và Tổng Biên Tập (GS. Victor Aurelius).
    3. **Nâng Cấp API Agency Roster:** Cập nhật endpoint `GET /api/agency/agents` trả về đầy đủ thông tin Hội đồng 10 Giáo sư viện hàn lâm.
- **Yêu cầu 6 (2026-09-07 - Thẩm Định Chặt Chẽ Văn Phong Khoa Học & Khắc Phục Over-Claiming Trong Rubric Q1 & Adversarial Review):**
  - *Nhiệm vụ:* Nâng cấp bộ máy thẩm định Tòa soạn Báo AI (GATE 3) và Hội đồng Phản biện Đối kháng (Adversarial Review) để phát hiện và trừ điểm các lỗi phóng đại, khẳng định quá mức (over-claiming), thiếu tiết chế học thuật (lack of epistemic hedging) và văn phong hoa mỹ phi khoa học.
  - *Kết quả xử lý:*
    1. **Nâng cấp Rubric Q1 (`evaluate_manuscript_q1_rubric`):** Bổ sung tiêu chí rà soát over-claiming vào đánh giá chất lượng; áp dụng mức phạt điểm trực tiếp nếu bản thảo mắc lỗi khẳng định quá mức hoặc sử dụng ngôn từ phi khoa học, đồng thời đưa ra khuyến nghị sửa chữa cụ thể.
    2. **Tăng Cường Phản Biện Đối Kháng (`conduct_adversarial_peer_review`):** Thiết lập Reviewer 1 và Reviewer 2 tập trung chất vấn tính chính xác của các tuyên bố quả quyết, buộc tác giả giải trình và đưa ra bằng chứng thực nghiệm lượng hóa.
    3. **Chuẩn Hóa Dữ Liệu Mẫu GATE:** Loại bỏ hoàn toàn các cụm từ sáo rỗng "Trong bối cảnh..." khỏi nội dung fallback của quy trình GATE.
    4. **Kiểm Thử:** Vượt qua 100% kịch bản kiểm thử trong `tests/test_scientific_hedging_and_tone.py` và `test_server_load.py`.
- **Yêu cầu 7 (2026-09-14 - Tích Hợp Looped Flows Empirical Verification & Spurious Attractor Audit Vào Rubric Q1 & Adversarial Review):**
  - *Nhiệm vụ:* Nâng cấp Tòa soạn Báo AI ứng dụng giao thức suy luận luồng lặp Looped Flows (arXiv:2609.11801) để tự động kiểm toán điểm bão hòa kiểm chứng ACT $q(z)$, trừ điểm các trường hợp rơi vào điểm hấp dẫn giả (Spurious Attractor), và vũ khí hóa Reviewer 2 phản biện đối kháng với chỉ báo bão hòa thực chứng.
  - *Kết quả xử lý:*
    1. **Nâng Cấp Rubric Q1 (`evaluate_manuscript_q1_rubric`):** Tự động chạy `audit_text_with_looped_flows()`, tính toán ACT $q(z)$, phạt điểm khi phát hiện Spurious Attractor, và trả về đối tượng `looped_flows_audit` hoàn chỉnh.
    2. **Phản Biện Đối Kháng Sắc Bén (`conduct_adversarial_peer_review`):** Reviewer 2 (GS. Adversarius Grimm) tự động phát hiện các ca ngụy biện tự tin (overconfident assumptions) và đưa ra chất vấn đích danh kèm khuyến nghị kích hoạt Stochastic Backtracking.
    3. **Mở Rộng API Endpoints:** Cung cấp 2 endpoints mới: `POST /api/editorial/looped-flows-audit` (kiểm toán độc lập văn bản) và `GET /api/reasoning/looped-flows/status` (thông số cấu hình engine).
    4. **Kiểm Thử:** Đạt 100% PASS trên `tests/test_looped_flows_engine.py` (Test 8 & 10).
- **Yêu cầu 8 (2026-09-14 - Tích Hợp Data Autocleaning, Data Profiling & Chuẩn Hóa Số Liệu Khoa Học Vào GATE 2 & File B):**
  - *Nhiệm vụ:* Nâng cấp hệ thống kiểm duyệt khoa học của Tòa soạn AI (GATE 2) và quy trình xuất bản File B bằng cách tích hợp module làm sạch và thẩm định dữ liệu tự động (`/data-autocleaning`).
  - *Kết quả xử lý:*
    1. **Khởi Tạo `ScientificDataCleaner` (`modules/shared/data_autocleaning.py`):** Phát hiện số liệu ngoại lai (outliers), kiểm tra biên vật lý (pH, %, $q_{\max}$, COD, BOD, CEC), chuẩn hóa đơn vị đo lường khoa học (mg/g, $\text{m}^2/\text{g}$, mg/L, tấn CO₂e) và tự động chuẩn hóa số thập phân tiếng Việt (dấu phẩy `1,5; 28,5%`).
    2. **Làm Sạch Bảng Ma Trận Đối Soát 6 Cột:** File B của Academic Writer tự động lọc qua `clean_evidence_matrix_rows()` trước khi xuất bản Word .docx.
    3. **Mở Rộng API Endpoints:** Mở endpoint `POST /api/evidence-db/autoclean` hỗ trợ profiling bộ dữ liệu và làm sạch tự động.
    4. **Kiểm Thử:** Đạt 100% PASS trên `tests/test_data_autocleaning.py` (6/6 tests PASS).
- **Yêu cầu 9 (2026-09-16 - Hoàn Thiện Giao Diện Thẩm Định Dấu Chân Số Liệu & DOI Độc Lập):**
  - *Nhiệm vụ:* Cung cấp nút bấm và giao diện thẩm định thời gian thực cho Academic Fact-Checker trên Dashboard Tòa Soạn Báo AI.
  - *Kết quả xử lý:*
    1. **Nút Thẩm Định Độc Lập:** Bổ sung `🛡️ Thẩm Định Dấu Chân Số Liệu & DOI Độc Lập (Fact-Checker)` trên giao diện Tòa Soạn Báo AI (`static/index.html`).
    2. **Scorecard Thẩm Định Thực Chứng:** Render thẻ kết quả với: Số lượng khẳng định định lượng bóc tách được, số mã DOI tra cứu với trạng thái `HTTP 200 OK`, số dị biệt/cảnh báo, và danh sách trích đoạn câu văn kèm dấu chân số liệu chi tiết.
    3. **Bảo Đảm Liêm Chính Tuyệt Đối:** Tuân thủ Quy tắc Bất biến 1 (Evidence First & Zero Fabrication) và quy chuẩn trích dẫn APA 7th ĐH Đồng Tháp.
    4. **Kiểm Thử:** Đạt 100% PASS trên toàn bộ test suite `test_academic_fact_checker.py`.



