# 📊 ĐẶC TẢ PHÂN HỆ 11: PHÂN TÍCH DỮ LIỆU LỚN & MÔ HÌNH HÓA (BIGQUERY AI/ML)

## 🎯 VỊ TRÍ & ĐẶC TẢ MODULE
- **Mã Tab trên UI:** `#bigquery-tab` (`static/index.html`)
- **Tên hiển thị:** **📊 BigQuery AI & ML**
- **File JavaScript điều khiển:** `static/js/bigquery-ml.js`
- **File Router Backend:** `modules/bigquery/bigquery_router.py`
- **File Engine cốt lõi:** `modules/bigquery/bigquery_engine.py`
- **Module liên kết:** `modules/shared/pdf_ocr_engine.py` (Purpose-Built Document AI OCR Engine)
- **API Endpoints chính:**
  - `POST /api/bigquery/forecast`: Dự báo chuỗi thời gian học thuật (ARIMA_PLUS / Trend + Seasonality)
  - `POST /api/bigquery/detect-anomalies`: Phát hiện điểm dị biệt & sai số đo đạc thực nghiệm
  - `POST /api/bigquery/key-drivers`: Phân tích nhân tố cốt lõi & tương quan đa biến Pearson
  - `POST /api/bigquery/generate-sql`: Chuyển đổi ngôn ngữ tự nhiên tiếng Việt sang BigQuery SQL (NL2SQL)
  - `POST /api/bigquery/upload-dataset`: Đọc và phân tích cấu trúc tập dữ liệu CSV/JSON
  - `POST /api/bigquery/export-docx`: Xuất bản Báo cáo phân tích định lượng sang file Word (.docx) kèm đồ họa 300 DPI

---

## 🔗 QUY TRÌNH LIÊN KẾT LIÊN THÔNG (INTERLINK PROTOCOL)
- **Đầu vào (Input Tiếp Nhận):**
  - Tiếp nhận dữ liệu số lượng bài báo, trích dẫn hoặc số liệu đo đạc thực nghiệm từ y văn của **Tab 2 (Harvester Pro)** để làm chuỗi thời gian đầu vào.
  - Tiếp nhận bảng số liệu bóc tách từ các tệp PDF qua **PDF Document AI OCR Engine**.
- **Xử lý Phân tích Định lượng:**
  - Thực thi 4 mô hình: Dự báo xu hướng chuỗi thời gian (`AI.FORECAST`), Phát hiện dị biệt kép Z-score + IQR (`AI.DETECT_ANOMALIES`), Phân tích động lực cốt lõi Pearson (`AI.KEY_DRIVERS`), và Chuyển đổi ngôn ngữ tự nhiên sang SQL (`NL2SQL`).
  - Sinh biểu đồ khoa học 300 DPI (Matplotlib) hỗ trợ font tiếng Việt Unicode toàn diện.
- **Đầu ra (Output Bàn Giao Liên Thông):**
  - ➔ **Truyền sang Tab 1 (Pipeline Bước 4):** Bàn giao bảng số liệu dự báo và điểm dị biệt vào phần Kết Quả Nghiên Cứu & Bàn Luận (Results & Discussion).
  - ➔ **Truyền sang Tab 5 (Academic Writer):** Tự động cung cấp ma trận tương quan và phân tích động lực chính vào nội dung File A.
  - ➔ **Truyền sang Tab 8 (Math-Chem Pro):** Nhúng biểu đồ 300 DPI và công thức mô hình hóa vào ấn phẩm Word.
  - ➔ **Truyền sang Workspace & History:** Lưu trữ file Báo cáo (.docx, .md) vào `Tai_Lieu/` và ghi nhật ký kiểm toán.

---

## ⚖️ TUÂN THỦ 4 QUY TẮC BẤT BIẾN & ĐẠO ĐỨC NGHIÊN CỨU
1. **Evidence First & Zero Fabrication:** 100% số liệu tính toán dựa trên chuỗi dữ liệu thực tế được cung cấp; công khai rõ ràng khoảng tin cậy 95% và phương pháp thống kê, không bịa đặt số liệu.
2. **In-Place DOM Word (.docx):** Báo cáo kết xuất bảo toàn cấu trúc Heading 1/2/3, bảng số liệu dạng lưới và nhúng biểu đồ độ phân giải cao 300 DPI.
3. **Chuẩn hóa số thập phân tiếng Việt:** Sử dụng dấu phẩy cho số thập phân (`1,5; 28,5%`) và dấu chấm cho hàng nghìn (`1.000; 50.000`).
4. **Chuẩn hóa hóa học & toán học:** Các ký hiệu biến số toán học và hóa học được định dạng chuẩn mực trong văn bản phân tích.

---

## 📝 NHẬT KÝ YÊU CẦU & KẾT QUẢ XỬ LÝ
- **Yêu cầu 1 (2026-08-26):** Tích hợp kỹ năng BigQuery AI & ML vào WEB SUPER theo skill `bigquery-ai-ml`.
  - *Kết quả:*
    - Xây dựng `BigQueryAIEngine` trong `modules/bigquery/bigquery_engine.py` hỗ trợ 4 trụ cột: Dự báo chuỗi thời gian (`AI.FORECAST`), Phát hiện dị biệt (`AI.DETECT_ANOMALIES`), Động lực cốt lõi (`AI.KEY_DRIVERS`), và Trợ lý NL2SQL (`AI.GENERATE`).
    - Bổ sung toàn bộ REST APIs trong `modules/bigquery/bigquery_router.py` và mount vào `server.py`.
    - Phát triển giao diện `static/js/bigquery-ml.js` với 4 subtab chuyên sâu, hỗ trợ upload CSV và nạp nhanh 3 bộ dữ liệu mẫu khoa học.
    - Tích hợp xuất bản file Word `.docx` kèm biểu đồ 300 DPI tự động lưu vào Workspace `Tai_Lieu/`.
    - Đã chạy kiểm thử tự động toàn diện đạt 100%.

- **Yêu cầu 2 (2026-08-26 - Worker M3 Hardening):** Tôi luyện và gia cố kỹ thuật toàn diện Phân hệ BigQuery AI/ML và PDF AI OCR.
  - *Kết quả:*
    - Gia cố `modules/shared/pdf_ocr_engine.py`: Đóng gói quy trình 4 tầng Purpose-Built Document AI, xử lý ngoại lệ tệp rỗng/mã hóa, bảo toàn trích dẫn RAG Semantic Chunks `[filename, Trang X]`, xuất bản Word In-Place DOM 300 DPI và nạp 1-click vào Open-Notebook.
    - Gia cố `modules/bigquery/bigquery_engine.py`: Tối ưu hóa cấu trúc IMRaD, nhúng đồ thị 300 DPI Matplotlib hỗ trợ font tiếng Việt Unicode toàn diện (`DejaVu Sans`, `Arial`, `Segoe UI`), chuẩn hóa dấu phẩy số thập phân (`1,5; 28,5%`), kiểm soát khoảng tin cậy 95% và phân loại dị biệt kép (Z-score + IQR).
    - Gia cố `modules/bigquery/bigquery_router.py`: Tự động nhận diện dấu phân cách CSV (phẩy, chấm phẩy, tab), xác thực đầu vào và ghi vết lịch sử hoạt động.
    - Chạy bộ kiểm thử chuyên sâu `test_m3_hardening.py` và `test_survey_engines.py` đạt **100% PASS**.

- **Yêu cầu 3 (2026-08-26 - Multi-Agent & E2E Validation):**
  - *Kết quả:* Xác thực toàn diện qua `test_server_load.py` (8/8 tests PASS) và `test_pdf_ocr_full_flow.py` (11/11 tests PASS), bảo đảm 100% tính sẵn sàng và độ tin cậy của phân hệ phân tích dữ liệu lớn.
