# ⚡ QUY TRÌNH NGHIÊN CỨU 7 BƯỚC (PIPELINE 7 STEPS IMRaD & GATE)

## 🎯 VỊ TRÍ & ĐẶC TẢ MODULE
- **Giao diện:** Tab 1 (`#pipeline-tab`).
- **File Frontend:** `static/js/pipeline.js`
- **File Backend:** `modules/pipeline/pipeline_router.py`, `modules/pipeline/pipeline_engine.py`

## 🔗 QUY TRÌNH LIÊN KẾT LIÊN THÔNG (INTERLINK PROTOCOL)
- **Đầu vào (Input Tiếp Nhận):**
  - Chủ đề nghiên cứu từ Người dùng.
  - Phân tích PICO Framework (Population, Intervention, Comparison, Outcome) và Domain Perspective.
- **Xử lý & Chuyển giao Nội bộ (Quy trình 7 Bước IMRaD kết hợp RhinoInsight Deep-Research / arXiv:2511.18743):**
  - **Bước 1 (Ý tưởng & PICO):** Sinh cấu trúc PICO, câu hỏi nghiên cứu, thẻ từ khóa Anh/Việt.
  - **Bước 2 (Tổng quan Y văn & Dàn ý Tương tác Phase 1):** Sinh Cây Đề cương (Interactive Outline Tree), mở rộng nhánh (`expand-branch`), thêm chiều phân tích (`add-dimension`), và Cổng phê duyệt chuyên gia (`lock`).
  - **Bước 3 (Phương pháp luận):** Thiết kế mô hình, quy trình thực nghiệm, biến số và khung đo lường.
  - **Bước 4 (Dữ liệu & BigQuery AI/ML):** Nạp dữ liệu, mô hình hóa chuỗi thời gian (`AI.FORECAST`), phát hiện dị biệt kép Z-score + IQR (`AI.DETECT_ANOMALIES`), và phân tích động lực Pearson (`AI.KEY_DRIVERS`).
  - **Bước 5 (Điều tra sâu Phase 2 & Bàn luận):** Soạn thảo sâu từng Node luận điểm dựa trên dữ liệu thực chứng, gán cờ `[uncertain]` khi phát hiện dữ liệu mâu thuẫn/chưa đủ.
  - **Bước 6 (Thẩm định Tòa soạn GATE):** Thẩm định qua Hội đồng 6 Ban, chấm điểm Q1 ISI Rubric (thang điểm 100) và 2-Reviewer Adversarial Peer Review.
  - **Bước 7 (Tổng hợp & Xuất bản 2-File):** Kết xuất trọn gói File A (.docx/.md) và File B (Ma trận Đối soát 6 Cột & APA 7th).
- **Đầu ra (Output Bàn Giao Liên Thông):**
  - ➔ **Truyền sang Tab 2 (Harvester):** Tự động sinh câu truy vấn Boolean (`"Machine Learning" AND "Healthcare"`) và Thẻ Từ khóa học thuật (Anh/Việt) để nạp vào ô tìm kiếm bài báo.
  - ➔ **Truyền sang Tab 5 (Academic Writer):** Cung cấp khung cấu trúc dàn ý IMRaD đã được Approval Gate khóa để sinh Bộ đôi 2-File Word.
  - ➔ **Truyền sang Workspace & History:** Tự động ghi nhật ký phiên làm việc và lưu trữ tệp kết quả.

## ⚖️ TUÂN THỦ 4 QUY TẮC BẤT BIẾN & ĐẠO ĐỨC NGHIÊN CỨU
1. **Evidence First & Zero Fabrication:** Bám sát tuyệt đối số liệu thực nghiệm và tài liệu gốc.
2. **In-Place DOM Word (.docx):** Giữ nguyên cấu trúc đề mục heading và bảng biểu.
3. **Chuẩn hóa số thập phân tiếng Việt:** Dấu phẩy cho số thập phân (`1,5; 28,5%`), dấu chấm cho hàng nghìn (`1.000`).
4. **Chuẩn hóa hóa học & toán học:** Tự động sửa chỉ số dưới (`FeS₂`, `H₂SO₄`, `NH₄⁺`...).

## 📝 NHẬT KÝ YÊU CẦU & KẾT QUẢ XỬ LÝ
- **Yêu cầu 1:** Đồng bộ Khung PICO và Thẻ Từ khóa, loại bỏ trùng lặp 2 thẻ Anh - Việt dư thừa.
  - *Kết quả:* Đã tích hợp nút "Đồng Bộ Sang Thẻ Từ Khóa" và gộp thẻ từ khóa tối ưu.
- **Yêu cầu 2:** Hỗ trợ thực thi Chạy từng bước (Step-by-step) và Chạy chuỗi toàn bộ (Chained 1-Click).
  - *Kết quả:* Đã hoàn thiện 2 endpoint `/api/pipeline/run-step` và `/api/pipeline/run-full`.
- **[2026-08-25 11:18] Yêu cầu 3:** Khắc phục triệt để lỗi kết nối Step 6 (AttributeError evaluate_academic_quality_scorecard). Bổ sung Scope Anchor chống lạc đề và triệt tiêu ký hiệu LaTeX $.
- **Yêu cầu 4 (2026-08-26 - Multi-Agent Milestone M1, M2, M3 & E2E Validation):**
  - *Nhiệm vụ:* Tích hợp phân tích định lượng BigQuery AI/ML (ARIMA_PLUS / Key Drivers) vào Bước 4 & 5; khóa Evidence Vault 100% Zero Fabrication; xuất bản trọn gói Bộ 2-File (.docx & .md) kèm xem trước Biểu đồ 300 DPI.
  - *Kết quả xử lý:*
    1. Nâng cấp `modules/pipeline/pipeline_engine.py` gọi tự động `bigquery_engine` mô hình hóa chuỗi thời gian, phát hiện điểm dị biệt và sinh biểu đồ 300 DPI.
    2. Xây dựng cơ chế `evidence_vault` khóa dữ liệu y văn thực chứng từ Harvester Pro phục vụ chuyển giao 6 Ban GATE.
    3. Cập nhật `static/js/pipeline.js` hiển thị panel phân tích định lượng BigQuery, xem trước ảnh đồ thị 300 DPI và cung cấp nút tải trọn gói Bộ 2-File (.docx & .md).
    4. Kiểm thử toàn diện qua bộ test E2E `test_server_load.py` (8/8 tests PASS) và `test_m3_hardening.py` đạt **100% PASS**.
- **Yêu cầu 8 (2026-08-27 - 4 CẢI TIẾN TRỌNG TÂM: OPENALEX THEO TỪ KHÓA, CHỌN TÀI LIỆU OA, BỎ FILE B & SỬA LỖI BƯỚC 7):**
  - *Nhiệm vụ & Kết quả xử lý:*
    1. **Bước 1 (Xu hướng OpenAlex theo từng từ khóa):** Hiện thực hóa `fetch_per_keyword_trends()` truy vấn OpenAlex API song song theo từng keyword độc lập, tính toán CAGR, tổng số bài báo và phân bố theo năm. Bỏ hoàn toàn fallback sinh dữ liệu giả (100% Zero Fabrication). Hiển thị biểu đồ phân bố cho từng keyword trên giao diện Bước 1.
    2. **Bước 2 (Chọn trước khi tải & Xem file .MD):** Tích hợp cờ `is_open_access`, hiển thị nhãn 🟢 Open Access vs 🔒 Paywall, hyperlink trỏ trực tiếp đến web gốc/landing page của tài liệu, nút tải thủ công cho tài liệu bản quyền và nút "📄 Xem .MD (AI)" để đối soát dữ liệu verbatim mà AI nạp vào.
    3. **Bước 5 (Loại bỏ File B & Tích hợp Xu hướng vào File A):** Bỏ hoàn toàn việc tạo File B (Ma trận 6 cột) nhằm tiết kiệm token tối đa; nội dung xu hướng công bố khoa học thực tế từ OpenAlex được tích hợp tự động vào luận cứ phân tích của File A (Bài báo IMRaD).
    4. **Bước 7 (Sửa lỗi mất nội dung sau khi Khử AI):** Khắc phục lỗi tìm file bản thảo (.md) do không khớp tiền tố (`File_A_*` thay vì `Bao_cao_*`), bổ sung cơ chế fallback quét đa tầng (`Tai_Lieu/`, `Ban_Thao/`) và kiểm tra tính toàn vẹn (integrity guard) trước và sau khi Humanize.
    5. Đạt **100% PASS** trên bộ kiểm thử tự động `test_4_fixes.py`.
- **Yêu cầu 9 (2026-09-06 - Tích Hợp Động Cơ Bóc Tách Thực Chứng & Cơ Sở Dữ Liệu Thực Chứng Vào Bước 2 & Bước 5):**
  - *Nhiệm vụ:* Tích hợp tính năng bóc tách chuyên sâu theo từng tài liệu cung cấp (chuẩn APA 7th, số trang, phân mục, trích đoạn nguyên văn, bản dịch, thống kê định lượng) vào dòng chảy quy trình 7 bước.
  - *Kết quả xử lý:*
    1. **Tích hợp Bước 2 (Evidence Vault to Empirical Database):** Bổ sung hàm `build_empirical_database_from_vault()` trong `PipelineEngine` (`modules/pipeline/pipeline_engine.py`), tự động bóc tách toàn bộ tài liệu đã lưu trong Vault để tạo Cơ sở dữ liệu Thực chứng hoàn chỉnh (`.json`, `.docx`, `.md`, `.ris`, `.bib`).
    2. **Liên thông sang Bước 5:** Tự động chuyển giao `empirical_database` từ Bước 2 sang Bước 5 để đưa trực tiếp các luận cứ và chỉ số đo lường vào Báo cáo IMRaD (Tệp A) và Bảng Ma trận đối soát 6 Cột (Tệp B).
    3. **Kiểm Thử:** Đạt 100% PASS trên toàn bộ 33/33 tests trong bộ kiểm thử `pytest tests`.
- **Yêu cầu 10 (2026-09-14 - Tích Hợp Giao Thức Suy Luận Luồng Lặp Looped Flows Reasoning / arXiv:2609.11801 Vào Bước 1 & Bước 5):**
  - *Nhiệm vụ:* Nâng cấp Quy trình 7 Bước ứng dụng giao thức suy luận lặp chính xác cao: khử nhiễu đa tầng ($t_0 \to t_k$), tự động kiểm toán tính bão hòa ACT $q(z) \ge 0,95$ và chống bẫy ngụy biện tự tin (Spurious Attractors).
  - *Kết quả xử lý:*
    1. **Bước 1 (Scope & PICO):** Tự động kích hoạt `looped_flows_engine.audit_text_with_looped_flows()` để rà soát tính nhất quán nội tại giữa câu hỏi nghiên cứu PICO, mệnh đề can thiệp và từ khóa Boolean, loại bỏ sớm các giả thuyết mâu thuẫn.
    2. **Bước 5 (2-File Academic Drafting):** Nhận trực tiếp biên bản kiểm định Looped Flows từ Academic Writer (ACT Score, Residual $R_i$, Spurious Attractor Guard) và chuyển giao sang các bước xuất bản tiếp theo.
    3. **Kiểm Thử:** Đạt 100% PASS trên bài kiểm tra `test_09_integration_with_pipeline_step1`.
- **Yêu cầu 11 (2026-09-16 - Tích Hợp Data Autocleaning & Lọc Dị Biệt Số Liệu Vào Bước 2 Evidence Vault):**
  - *Nhiệm vụ:* Tích hợp cơ chế tự động làm sạch số liệu (`ScientificDataCleaner`) trực tiếp trên giao diện và backend của Bước 2.
  - *Kết quả xử lý:*
    1. **Backend Router (`modules/pipeline/evidence_db_router.py`):** Mở endpoint `POST /api/evidence-db/autoclean` phân tích và làm sạch toàn bộ bản ghi thực chứng trong Vault.
    2. **Xử lý số liệu:** Tự động phát hiện outliers (pH ngoài $[0, 14]$, phần trăm $>100\%$, giá trị âm bất thường), chuẩn hóa đơn vị đo lường theo hệ SI (`mg/g`, `mg/L`, `tấn CO₂e`), và định dạng số thập phân tiếng Việt (`1,5; 28,5%`).
    3. **Giao diện Bước 2 (`static/index.html` & `static/js/pipeline.js`):** Bổ sung nút bấm `🧹 Làm Sạch Số Liệu` cạnh cụm nút Vault, hiển thị thông báo kết quả làm sạch thời gian thực.
    4. **Kiểm thử:** Đạt 100% PASS trên bộ kiểm thử `test_data_autocleaning.py`.
- **Yêu cầu 12 (2026-09-23 - Nâng Cấp Dual-Pane Evidence Inspector v4.2 & Cổng Kiểm Duyệt 4 Tầng Vào Bước 7):**
  - *Nhiệm vụ:* Nâng cấp Bước 7 tự động kích hoạt Cổng Kiểm Duyệt 4 Tầng (Match Ratio $\ge 0,60$, Anti-Topic Fraud, DOCX sync, Zero-Hallucination Circuit Breaker) và tự động xuất bản Bảng Ma Trận A4 Landscape kèm trọn bộ gói đối soát độc lập.
  - *Kết quả xử lý:*
    1. **Pipeline Engine (`modules/pipeline/pipeline_engine.py`):** Bước 7 sau khi lưu bản thảo hoàn tất sẽ tự động gọi `evidence_inspector_engine.package_standalone_bundle()` và `run_4_layer_verification_gate()` trả về `inspector_verification`.
    2. **Đầu ra đối soát chuẩn mực:** Tự động sinh `multi_evidence_catalog.json` (10 trường), `Bang_Truy_Xuat_Nguon_Goc_Tai_Lieu.docx` (Khổ ngang Landscape 7 cột), và `doi_soat.html`.
    3. **Kiểm thử:** Đạt 100% PASS trên bộ kiểm thử `tests/test_evidence_inspector_gate.py`.
- **Yêu cầu 13 (2026-11-08 - Đồng Bộ Hóa 8 Bước Pipeline & Tối Ưu Hệ Thống Kiểm Thử Tự Động):**
  - *Nhiệm vụ:* Khắc phục lỗi kiểm thử do bổ sung Bước 8 (Dual-Pane Evidence Scanner), đảm bảo tính nhất quán giữa pipeline definition và test suite.
  - *Kết quả xử lý:*
    1. **Đồng bộ hóa kiểm thử (`tests/test_reform_r1_pipeline.py`):** Cập nhật assertion khớp chính xác với cấu trúc 8 bước hoàn chỉnh của hệ thống.
    2. **Cấu hình môi trường pytest (`pytest.ini`):** Bổ sung `pythonpath = .` đảm bảo việc nhận diện các package nội bộ `modules/` đồng bộ trong mọi môi trường chạy tự động.
    3. **Kiểm thử toàn diện:** Bộ test suite 13/13 tests của pipeline và 91/91 tests toàn hệ thống đều đạt **100% PASS**.




