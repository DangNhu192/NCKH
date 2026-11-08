# 🛡️ ĐẶC TẢ CHỨC NĂNG 12: ĐỐI SOÁT SONG SONG & CỔNG KIỂM DUYỆT 4 TẦNG (DUAL-PANE EVIDENCE INSPECTOR v4.2)

> **Trạng thái:** ✅ Sẵn sàng & Tích hợp 100% vào Web Super v3.2 / v2.0  
> **Phiên bản:** v4.2 Pro (Hợp nhất theo Bộ Kỹ Năng Trung Tâm & Quy Trình Xuất Bản Kèm Đối Soát)  
> **Kiến trúc:** Dual-Pane IMRaD 🔁 PDF.js Canvas + 4-Layer Pre-Commit Verification Gate + Standalone Bundle Streaming (Port 8765)

---

## 📌 1. BỐI CẢNH & MỤC TIÊU PHÁT TRIỂN
Trong nghiên cứu học thuật cấp cao và luận văn Thạc sĩ/Tiến sĩ chuẩn ISI/Scopus, việc chỉ có văn bản tổng thuật là chưa đủ. Hội đồng nghiệm thu và các nhà bình duyệt quốc tế luôn đòi hỏi **bằng chứng thực chứng trực quan (Ground-Truth Evidence)** bám sát từng câu chữ, con số trong bài viết khoa học.

Hệ thống **Dual-Pane Evidence Inspector v4.2** ra đời nhằm giải quyết triệt để vấn đề:
1. **Đối soát song song trực tiếp (Dual-Pane View):** Màn hình chia đôi độc lập, cột trái là bản thảo IMRaD với các nút trích dẫn tương tác `cite-btn`; cột phải là Thẻ Tiêu Điểm (Spotlight Card) cùng trình đọc PDF.js Canvas tô sáng vị trí dữ liệu gốc.
2. **Cổng kiểm duyệt 4 tầng tự động (4-Layer Pre-Commit Verification Gate):** Ngắt mạch liêm chính (Zero-Hallucination Circuit Breaker) nếu phát hiện bất kỳ sai lệch nào giữa bài viết và tài liệu gốc.
3. **Bộ đầu ra đối soát 4 thành phần (Nguyên tắc Bất biến 1:1:1:1):** Đảm bảo $N\ \text{PDF} = N\ \text{MD} = N\ \text{DOCX} = N\ \text{RIS} = N\ \text{HTML}$.

---

## ⚖️ 2. BỐN (4) TẦNG KIỂM ĐỊNH LIÊM CHÍNH HỌC THUẬT (4-LAYER GATE)

### Tầng 1: Kiểm toán Trùng khớp Mặt chữ Thô PDF (Raw PDF Text Matching)
- **Tiêu chuẩn:** Tỷ lệ trùng khớp từ vựng $\ge 0,60$ (60%) giữa trích đoạn trong bài báo và văn bản bóc tách thô từ trang PDF chỉ định.
- **Hành vi:** Quét từng trang PDF bằng `pypdf`, chuẩn hóa từ vựng tiếng Anh/Việt, đối chiếu chuỗi từ thực nghiệm.

### Tầng 2: Kiểm toán Nút bấm & Chống Gian Lận Chủ Đề (Interactive Buttons & Anti-Topic Fraud)
- **Tiêu chuẩn 1:** $100\%$ nút bấm trích dẫn `cite-btn` trong HTML phải liên kết chính xác với một mục vi luận điểm trong `multi_evidence_catalog.json` (Không có nút mồ côi `orphaned`).
- **Tiêu chuẩn 2:** Kiểm toán chống gian lận chủ đề (Anti-Topic Fraud) - xác định tỷ lệ trùng khớp từ khóa chuyên môn của chủ đề nghiên cứu (Nông nghiệp, môi trường, vật liệu, v.v.) $\ge 40\%$.

### Tầng 3: Đồng bộ hóa Word DOCX & Khóa Thông Số Định Lượng (DOCX Synchronization & Metric Locking)
- **Tiêu chuẩn:** $100\%$ thông số đo đạc cốt lõi (ví dụ: $7,258\ \text{tấn CO}_2\text{e/ha/năm}$, $q_{\max} = 45,8\ \text{mg/g}$, $S_{BET} = 120,5\ \text{m}^2/\text{g}$, $\text{pH} = 6,5$) xuất hiện trong `multi_evidence_catalog.json` bắt buộc phải hiện diện nguyên vẹn trong tệp Word `.docx` và bản thảo Web HTML.

### Tầng 4: Ngắt Mạch Liêm Chính (Zero-Hallucination Circuit Breaker)
- **Quy tắc:** Nếu $\sum \text{Errors} = 0 \to \text{EXIT CODE 0}$ (Phê duyệt xuất bản). Nếu phát hiện bất kỳ số liệu bịa đặt hoặc thiếu tài liệu gốc $\to \text{EXIT CODE 1}$ (Ngắt mạch, chặn xuất bản và hiển thị báo động đỏ).

---

## 🛠️ 3. QUY CHUẨN TRUY CẬP DOI & SCI-HUB DUY NHẤT TRÊN 1 DÒNG (SINGLE-ROW CLEAN ACCESS)
Nhằm giữ cho bản thảo học thuật IMRaD và danh mục tài liệu tham khảo APA 7th hoàn toàn thanh thoát và chuẩn mực, cặp nút truy cập nguồn:
- `[🌐 DOI NXB]` (Dẫn trực tiếp tới nhà xuất bản: Elsevier, Springer, Wiley, IEEE, MDPI...)
- `[⚡ Sci-Hub VN]` (Dẫn tới cổng truy cập mở Sci-Hub giải phóng tri thức)
**CHỈ ĐƯỢC PHÉP XUẤT HIỆN DUY NHẤT TRÊN DÒNG "MÃ ĐỊNH DANH DOI" CỦA THẺ TIÊU ĐIỂM (SPOTLIGHT CARD)** ở cột phải của màn hình đối soát. Tuyệt đối không đặt trên header, không đặt trên toolbar PDF và không chèn vào cột IMRaD.

---

## 📊 4. BẢNG MA TRẬN TRUY XUẤT NGUỒN GỐC A4 KHỔ NGANG (LANDSCAPE .DOCX)
- **Khổ giấy:** A4 Landscape ($11,69 \times 8,27\ \text{inches}$), căn lề $0,6\ \text{inches}$, bề rộng khả dụng $10,49\ \text{inches}$.
- **Cấu trúc 7 Cột:**
  1. STT
  2. Vi luận điểm khoa học (Scientific Claim)
  3. Tác giả & Năm công bố (APA 7th)
  4. Tệp PDF & Số trang gốc
  5. Trích đoạn nguyên văn (Original Verbatim Quote)
  6. Bản dịch tiếng Việt & Vị trí tọa độ
  7. Thông số đo đạc cốt lõi (Locked Metrics)

---

## 🔌 5. DANH SÁCH REST API ENDPOINTS
- `GET /api/inspector/catalog`: Lấy danh mục vi luận điểm thực chứng (`multi_evidence_catalog.json`).
- `POST /api/inspector/generate-bundle`: Đóng gói trọn bộ đối soát độc lập (HTML, JS, BAT, DOCX, JSON).
- `POST /api/inspector/verify-gate`: Chạy quy trình kiểm toán 4 tầng tự động và trả về Scorecard chi tiết.
- `POST /api/inspector/generate-matrix`: Xuất bản Bảng Ma Trận A4 Landscape `.docx` và `.md`.
- `GET /api/inspector/view-html`: Trả về giao diện Web đối soát song song trực tiếp.
- `GET /api/inspector/stream-pdf/{filename}`: Hỗ trợ phát luồng dữ liệu PDF chuẩn HTTP 206 Partial Content cho PDF.js Canvas.

---

## 🧪 6. KIỂM THỬ TỰ ĐỘNG
- Bộ kiểm thử: `tests/test_evidence_inspector_gate.py` (9/9 bài test PASS).
- Bao quát: Schema catalog, Clean DOI, Layer 1, Layer 2, Layer 3, Layer 4, Word Landscape, Standalone bundle, REST API endpoints.

---

## 📝 7. NHẬT KÝ BẢO TRÌ & NÂNG CẤP ĐỊNH KỲ
- **Ngày 08/11/2026 (Refactor & Bugfix Test Suite):**
  - **Sửa lỗi ngắt mạch Layer 4:** Điều chỉnh kiểm tra `if catalog is None` thay cho `if not catalog` để khi truyền catalog rỗng `{}` kiểm thử tầng 4 độc lập, hệ thống không bị kích hoạt fallback nạp tệp đĩa ngoài ý muốn.
  - **Khắc phục tạo file khởi chạy:** Bổ sung lệnh ghi tệp `Khoi_Chay_Doi_Soat.bat` trong hàm `package_standalone_bundle()`.
  - **Chuẩn hóa đối tượng trả về:** Xây dựng lớp `BundleResult(dict)` vừa hoạt động trọn vẹn như một dictionary (phục vụ `pipeline_engine`), vừa hỗ trợ phương thức `.exists()` khi kiểm tra đường dẫn thư mục gói đóng gói.
  - **Kết quả kiểm thử:** Toàn bộ 9/9 tests của module đạt 100% PASS.
