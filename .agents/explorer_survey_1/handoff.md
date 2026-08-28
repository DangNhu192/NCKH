# 🤝 HANDOFF REPORT — EXPLORER 1 (PIPELINE & PICO REFORM)

**Người thực hiện:** Explorer 1 (Lead Pipeline & PICO Architecture Explorer)  
**Mã nhiệm vụ:** R1 — Comprehensive Reform of 7-Step Pipeline ("Quy Trình Liên Kết")  
**Không gian làm việc:** `H:\My Drive\Ho so ca nhan\b. ThS KHMT\Skill\Web Super\.agents\explorer_survey_1`  
**Ngày bàn giao:** 2026-08-27  

---

## 1. OBSERVATION (Quan sát thực tế & Dẫn chứng cụ thể)

1. **Về Khung PICO & Xu Hướng Nghiên Cứu (Step 1):**
   - Tại `modules/pipeline/pipeline_engine.py` (dòng 90-142) và `modules/harvester/data_harvesting_engine.py` (dòng 126-354):
     - Hàm `generate_boolean_query` và `translate_keywords_multilingual` trích xuất được khung PICO và 6 ngôn ngữ học thuật (en, vi, ru, fr, de, zh).
     - **Quan sát trực tiếp:** Hoàn toàn **chưa có hàm nào truy vấn thống kê tần suất xuất bản theo năm** (Publication Frequencies & Research Trends) từ OpenAlex, EuropePMC hoặc ArXiv.
2. **Về Nạp Tài Liệu Đa Định Dạng vào Evidence Vault (Step 2):**
   - Tại `modules/pipeline/pipeline_engine.py` (dòng 145-202):
     - Bước 2 chỉ nhận `saved_records` sinh ra từ việc cào dữ liệu Harvester.
     - Chưa có API hoặc logic cho phép người dùng nạp trực tiếp file `.docx`, `.md`, `.pdf` từ máy tính hoặc đính kèm các file tài liệu đã có trong thư mục Workspace (`Tai_Lieu/`, `Tri_Thuc/`, `Ban_Thao/`) vào Evidence Vault.
   - Tại `modules/pipeline/pipeline_router.py` (dòng 1-56):
     - Chỉ có 3 endpoint: `/api/pipeline/steps`, `/api/pipeline/run-step`, `/api/pipeline/run-full`. Chưa có endpoint quản lý Vault (`/api/pipeline/vault/*`).
3. **Về Bất Đồng Bộ Cấu Trúc 6 Bước vs. 7 Bước Giữa Frontend và Backend:**
   - Tại `modules/pipeline/pipeline_engine.py` (dòng 28-78):
     - Backend định nghĩa chuẩn **7 Bước**: Step 1 (`scope_and_harvest`), Step 2 (`evidence_vault`), Step 3 (`knowledge_sync`), Step 4 (`structure_and_bigquery`), Step 5 (`academic_drafting`), Step 6 (`zotero_conversion`), Step 7 (`humanize_and_qa`).
   - Tại `static/index.html` (dòng 346-553):
     - Header ghi "⚡ Quy Trình Nghiên Cứu... (6 Bước)", Stepper Navigation chỉ có 6 nodes (`data-step="1"` đến `6`), các Step Cards chỉ có 6 card.
   - Tại `static/js/pipeline.js` (dòng 294):
     - Sử dụng mapping ép bước: `const backendStepMap = { 1: 1, 2: 3, 3: 4, 4: 5, 5: 6, 6: 7 };`, làm Bước 2 của backend (`evidence_vault`) bị bỏ qua khi chạy từng bước, và gây sai lệch giao diện khi chạy tự động 7 bước qua `runFullAuto()`.

---

## 2. LOGIC CHAIN (Chuỗi suy luận logic từ quan sát đến giải pháp)

1. **Từ Quan sát 1 ➔ Giải pháp Bước 1:**
   - Do người dùng cần nhìn thấy bức tranh tổng quan về xu hướng nghiên cứu trước khi thu thập tài liệu, cần bổ sung hàm `data_harvester.fetch_research_trends(topic, query)` gọi API `https://api.openalex.org/works?search=...&group_by=publication_year` và EuropePMC `PUB_YEAR` để tính toán số lượng bài theo năm (2019-2025), tốc độ tăng trưởng CAGR và hiển thị biểu đồ/bảng thống kê trực quan trên giao diện Bước 1.
2. **Từ Quan sát 2 ➔ Giải pháp Nạp Tài Liệu Đa Định Dạng:**
   - Để thỏa mãn yêu cầu nạp tài liệu từ file cá nhân (`.docx`, `.md`, `.pdf`, `.txt`) hoặc Workspace, cần xây dựng hàm `ingest_document_to_vault` và `import_workspace_files_to_vault` trong `pipeline_engine.py`, mở thêm endpoint `POST /api/pipeline/vault/upload` và `POST /api/pipeline/vault/import-workspace` trong `pipeline_router.py`.
3. **Từ Quan sát 3 ➔ Giải pháp Chuẩn Hóa Toàn Diện 7 Bước:**
   - Cần đồng bộ hóa 1:1 cả Frontend (`index.html`, `pipeline.js`) và Backend (`pipeline_engine.py`):
     - Sửa `static/index.html`: Cập nhật tiêu đề thành 7 Bước, tạo đủ 7 Stepper Nodes và 7 Step Cards riêng biệt.
     - Sửa `static/js/pipeline.js`: Cập nhật `stepPercentages` thành 7 mốc (14%, 28%, 42%, 57%, 71%, 85%, 100%), xóa bỏ `backendStepMap` và chạy trực tiếp `backendStepNo = stepNo` (1 đến 7), xây dựng renderer riêng cho từng bước từ 1 đến 7.

---

## 3. CAVEATS (Vùng chưa khảo sát hoặc giả định)

- **API Rate Limits:** OpenAlex và EuropePMC là các API mở miễn phí không yêu cầu API key, nhưng cần thiết lập cơ chế timeout (5-10s) và fallback an toàn nếu mất mạng.
- **Giả định về định dạng file:** File `.docx` tải lên phải hợp lệ theo chuẩn OpenXML, file `.pdf` nếu là dạng ảnh scan không có text sẽ được thông báo yêu cầu OCR hoặc cung cấp file Word/MD.

---

## 4. CONCLUSION (Kết luận & Đề xuất hành động)

Yêu cầu **R1 (Cải tổ Quy trình 7 Bước & PICO)** đã được khảo sát toàn diện, có phương án thiết kế kiến trúc chi tiết, phân chia 4 giai đoạn thực thi rõ ràng tại `.agents/explorer_survey_1/analysis.md`. Các Worker tiếp theo có thể triển khai trực tiếp vào mã nguồn mà không gặp bất kỳ xung đột cấu trúc nào.

---

## 5. VERIFICATION METHOD (Phương pháp kiểm chứng độc lập)

1. **Kiểm tra file báo cáo phân tích:**
   - Xem chi tiết tại: `H:\My Drive\Ho so ca nhan\b. ThS KHMT\Skill\Web Super\.agents\explorer_survey_1\analysis.md`
2. **Kiểm thử các API hiện tại:**
   - Chạy lệnh kiểm thử: `python test_suite.py` hoặc `python test_server_load.py`
3. **Điều kiện vô hiệu hóa (Invalidation conditions):**
   - Nếu sau khi Worker thực hiện sửa đổi, `static/index.html` hoặc `static/js/pipeline.js` vẫn còn chứa 6 bước hoặc còn tồn tại `backendStepMap = { 1: 1, 2: 3, ... }` thì xem như việc chuẩn hóa 7 bước chưa hoàn tất.
