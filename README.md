# 🚀 WEB SUPER v3.2 / v2.0 — Academic AI Research Platform

**Hệ Thống Tích Hợp Nghiên Cứu Khoa Học Chuẩn Quốc Tế ISI/Scopus/Scimago, Tòa Soạn Báo AI 6 Ban GATE & Kho Tri Thức Học Thuật Open-Notebook**

---

## 🌟 Tính Năng Cốt Lõi (Core Features)

1. **🎯 Quy Trình Nghiên Cứu 7 Bước (7-Step Linear Chained Pipeline):**
   - Phân tích ngữ nghĩa PICO, bóc tách thẻ từ khóa đa tầng tiếng Anh/Việt.
   - Thống kê tần suất và xu hướng công bố khoa học quốc tế qua OpenAlex & EuropePMC.
   - Khóa kho thực chứng **Evidence Vault (Zero Fabrication)** nạp tệp đa định dạng (.docx, .md, .pdf).

2. **📝 Viết Học Thuật 2-File & Đồng Bộ Zotero Hai Chiều (Academic Writer & Zotero Pro):**
   - Soạn thảo chuyên sâu chuẩn IMRaD (File A) và Ma Trận Đối Soát 6 Cột (File B).
   - Nhúng mã trường Zotero CSL XML (`w:fldSimple` / `w:instrText` `ADDIN ZOTERO_ITEM`) chuẩn APA 7th, IEEE, Vancouver, Harvard.
   - **Kích hoạt Interactive Word Hyperlinks (Hỗ trợ Ctrl + Click)**: Chuyển đổi 100% URL/DOI thành đối tượng `<w:hyperlink>` chuẩn Word (Times New Roman 11pt, màu `#0563C1`, gạch chân đơn), kèm kiểm soát trần số trang nghiêm ngặt ($\le 15$ trang theo mẫu tạp chí DTHU).
   - **Đồng bộ Zotero Web API Hai Chiều**: Chuẩn hóa họ tên tác giả tiếng Việt thành Hai ô (Two-Field Mode: `lastName: Họ`, `firstName: Tên đệm & Tên`) theo chuẩn APA 7th ĐH Đồng Tháp (Thông báo 5343/TB-ĐHĐT), phân loại có hệ thống vào các Bộ sưu tập Chuyên đề (Subcollections).
   - **Tối ưu hóa Dung lượng Zotero (Zero-Risk Storage Optimizer)**: Nén sao lưu zip tự động (`Backup_Zotero_PDFs_PreDelete.zip`) trước khi xóa tệp PDF đã có link trực tuyến để giải phóng quota 300MB Zotero Cloud, bảo vệ 100% tài liệu không có link.
   - Xuất kèm danh mục tài liệu tham khảo thực tế định dạng `.ris` và `.bib` có DOI thực 100%.

3. **🤖 Khử Dấu Vết AI & Chống Đạo Văn (Humanizer & Turnitin Rephrase Pro):**
   - Phân tích Perplexity & Burstiness, triệt tiêu 100% mẫu câu sáo rỗng AI.
   - Bảo toàn 100% DOM Word (`.docx`): Heading styles, Mục lục tự động, Bảng biểu, Hình ảnh 300 DPI và Mã trường Zotero.

4. **📐 Toán - Hóa - Biểu Đồ Khoa Học Pro (Math-Chem-Chart Pro):**
   - Chuẩn hóa 109 hợp chất hóa học và ion (`FeS₂`, `H₂SO₄`, `NH₄⁺`, `NO₃⁻`...).
   - Chuyển đổi công thức LaTeX sang Microsoft Word Equation (`<m:oMath>`) kèm quy tắc diễn giải 4 yếu tố.
   - Tạo biểu đồ, sơ đồ quy trình 300 DPI và tự động sửa lỗi đóng gói `word/media`.

5. **🧠 Kho Tri Thức Open-Notebook RAG Studio:**
   - Tra cứu lai (Hybrid Search: Okapi BM25 + Multi-Scale N-Gram) với trích dẫn số trang chính xác.

6. **📰 Tòa Soạn Báo AI Mô Hình 6 Ban GATE (Editorial Office):**
   - Quy trình xuất bản học thuật 4 trạm GATE và chấm điểm bài báo theo Rubric ISI/Scopus Q1 (100 điểm).

7. **📊 Phân Tích Dữ Liệu Lớn BigQuery AI/ML:**
   - Dự báo chuỗi thời gian ARIMA_PLUS, phát hiện dị thường và tìm nhân tố tác động chính (Key Drivers).

---

## 🛠️ Cài Đặt & Khởi Chạy (Installation & Setup)

### 1. Yêu cầu hệ thống:
- Python 3.10+ (Khuyến nghị Python 3.11)
- Git

### 2. Cài đặt môi trường:
```bash
# 1. Clone repository về máy tính
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>

# 2. Tạo và kích hoạt môi trường ảo
python -m venv .venv
# Trên Windows:
.venv\Scripts\activate
# Trên Linux/macOS:
source .venv/bin/activate

# 3. Cài đặt các gói thư viện phụ thuộc
pip install -r requirements.txt
```

### 3. Cấu hình hệ thống:
Sao chép tệp mẫu `config.example.json` thành `config.json` và điền các API Key của bạn:
```bash
cp config.example.json config.json
```

Cấu hình mẫu trong `config.json`:
```json
{
  "google_client_id": "",
  "gemini_api_key": "YOUR_GEMINI_API_KEY",
  "openai_api_key": "YOUR_OPENAI_API_KEY",
  "zotero_user_id": "",
  "zotero_api_key": "",
  "zotero_library_type": "user",
  "selected_gemini_model": "gemini-3.6-flash",
  "custom_storage_dir": ""
}
```

### 4. Khởi chạy ứng dụng:
```bash
# Chạy trực tiếp qua Uvicorn / FastAPI
python server.py
```
Truy cập giao diện Web Super tại trình duyệt: **`http://localhost:8000`**

---

## ⚖️ 4 Nguyên Tắc Bất Biến & Đạo Đức Nghiên Cứu
1. **Evidence First & Zero Fabrication:** 100% số liệu, tác giả, DOI trích xuất từ tài liệu thực tế.
2. **In-Place DOM Word (.docx) Preservation:** Giữ nguyên 100% định dạng, Heading Styles, Mục lục và Zotero XML.
3. **Chuẩn Hóa Số Thập Phân Tiếng Việt:** Dấu phẩy cho số thập phân (`1,5; 28,5%`) và dấu chấm cho hàng nghìn (`1.000; 50.000`).
4. **Chuẩn Hóa Ký Hiệu Hóa Học & Toán Học:** Tự động nhận diện chỉ số dưới (`FeS₂`, `H₂SO₄`...) và công thức Word OMML sắc nét.

---

## 📜 Giấy Phép (License)
Dự án được bảo hộ quyền tác giả cho mục đích nghiên cứu học thuật và chuyển giao công nghệ.