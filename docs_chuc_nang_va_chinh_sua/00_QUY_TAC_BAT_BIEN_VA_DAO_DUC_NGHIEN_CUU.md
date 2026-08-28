# ⚖️ QUY TẮC BẤT BIẾN & ĐẠO ĐỨC NGHIÊN CỨU KHOA HỌC (RESEARCH ETHICS)

## 📌 4 TRỤ CỘT BẤT BIẾN (IMMUTABLE INVARIANTS)
Mọi chức năng trong Web Super khi sinh nội dung, khử AI, viết lại văn bản hoặc xử lý file Word (.docx) bắt buộc phải tuân thủ 100%:

### 1. 🔬 Evidence First & Zero Fabrication (Tuyệt Đối Không Bịa Đặt)
- Mọi số liệu thực nghiệm, chỉ số đo lường, công thức toán/hóa, tên tác giả, năm công bố, DOI và kết quả nghiên cứu **bắt buộc phải bám sát tài liệu gốc và có nguồn đối chứng thực tế**.
- Tuyệt đối KHÔNG tự ý sáng tác (hallucinate) số liệu giả, tài liệu tham khảo giả hay kết quả khống.
- 100% DOI phải có đối chứng thực tế từ CrossRef, OpenAlex, PubMed, arXiv hoặc các công trình chuẩn mực đã xác thực (Vaswani et al., 2017; LeCun et al., 2015).

### 2. 📑 Bảo Toàn Cấu Trúc In-Place DOM File Word (.docx)
- Khi khử AI, chỉnh sửa hoặc viết lại file Word, hệ thống phải can thiệp trực tiếp vào từng XML Run/Paragraph mà không làm hỏng hoặc làm phẳng (flatten) cấu trúc tệp.
- **Bảo toàn 100%**:
  - Cấu trúc đề mục (Heading 1, Heading 2, Heading 3...) theo Style chuẩn của tài liệu.
  - Mục lục tự động (Table of Contents) và phân cấp tài liệu.
  - Hình ảnh, sơ đồ quy trình 300 DPI, bảng biểu dạng lưới viền `#CBD5E1` và chú thích (Caption).
  - Công thức toán học gốc (OMML Word Equation `<m:oMathPara>` / MathML).
  - Mã trường trích dẫn Zotero CSL (`w:fldSimple`, `w:fldChar`, `w:instrText`).

### 3. 🔢 Chuẩn Hóa Số Thập Phân & Dấu Ngăn Tiếng Việt
- Dùng **dấu phẩy** cho số thập phân: ví dụ `1,5`; `28,5%`; `0,05`; `10,25 mg/L`.
- Dùng **dấu chấm** cho phân cách hàng nghìn: ví dụ `1.000`; `50.000`; `1.000.000`; `12.500.000.000 VNĐ`.
- Phân lập tuyệt đối số thập phân với định danh DOI (`10.1016/...`, `10.1039/...`) qua regex `^10\.\d{4,9}/`.

### 4. 🧪 Chuẩn Hóa Ký Hiệu Hóa Học & Công Thức Toán Học Chuẩn Quốc Tế
- Tự động phát hiện và chuyển đổi đúng chỉ số dưới/trên cho 109 hợp chất, ion và chỉ số môi trường trong `UNICODE_CHEM_MAP`: `FeS₂`, `H₂SO₄`, `Fe²⁺`, `SO₄²⁻`, `NH₄⁺`, `NO₃⁻`, `CO₂`, `CH₄`, `PO₄³⁻`, `CaCO₃`, `Ca(OH)₂`, `HNO₃`, `H₃PO₄`, `Al³⁺`, `Cr⁶⁺`, `As³⁺`, `PM₂.₅`, `PM₁₀`, `BOD₅`, `COD`, `DO`...
- Tự động chuẩn hóa mà không cần nhắc nhở, nhưng TUYỆT ĐỐI KHÔNG làm biến dạng hay bịa đặt phương trình hóa học.
- Công thức toán khối định dạng LaTeX `$$...$$` hoặc XML OMML sắc nét.

### 5. 🧠 Khung Tư Duy Phản Biện & Hỗ Trợ CS519.M11
- Luôn đào sâu cơ chế giải thích sâu **TẠI SAO** một hiện tượng/giải pháp diễn ra.
- Nhận diện rõ **Khoảng trống tri thức (Research Gap)** và **Đe dọa tính hợp lệ (Threats to Validity)**.
- Chuỗi lập luận 4 bước: `[Luận điểm] ➔ [Dẫn chứng thực chứng] ➔ [Cơ chế giải thích sâu] ➔ [Hàm ý ứng dụng]`.

