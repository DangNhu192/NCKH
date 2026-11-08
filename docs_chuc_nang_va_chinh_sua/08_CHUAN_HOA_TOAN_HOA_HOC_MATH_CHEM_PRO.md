# 📐 CHUẨN HÓA CÔNG THỨC TOÁN - HÓA HỌC & ĐỒ HỌA 300 DPI (MATH-CHEM & DOCX PRO)

## 🎯 VỊ TRÍ & ĐẶC TẢ MODULE
- **Giao diện:** Tab 8 (`#math-chem-tab`).
- **File Frontend:** `static/js/math-chem-pro.js`
- **File Backend:** `modules/shared/docx_styler.py`, `modules/shared/docx_formula_engine.py`, `modules/shared/docx_math_chem_styler.py`, `modules/shared/chart_generator.py`

## 🔗 QUY TRÌNH LIÊN KẾT LIÊN THÔNG (INTERLINK PROTOCOL)
- **Đầu vào (Input Tiếp Nhận):**
  - Nhận file Word (.docx) được tạo ra từ **Tab 5 (Academic Writer)** hoặc do người dùng tải lên.
  - Nhận hình ảnh khoa học 300 DPI được thu thập từ **Tab 2 (Harvester)**.
- **Xử lý 3 Chế Độ Nâng Cấp:**
  1. `math_chem_only`: Quét và chuẩn hóa toàn bộ ký hiệu hóa học (`FeS₂`, `H₂SO₄`...), chèn công thức OMML Word Equation.
  2. `images_only`: Nhúng hình ảnh / sơ đồ khoa học 300 DPI căn giữa trang, gắn Caption học thuật chuẩn.
  3. `both`: Thực hiện đồng thời cả hai chế độ trên.
- **Đầu ra (Output Bàn Giao Liên Thông):**
  - ➔ **Truyền sang Tab 7 (Humanizer Pro):** File Word đã chuẩn hóa công thức và đồ họa sẵn sàng để khử AI.
  - ➔ **Truyền sang Workspace:** Lưu file Word nâng cấp vào thư mục làm việc.

## ⚖️ TUÂN THỦ 4 QUY TẮC BẤT BIẾN & ĐẠO ĐỨC NGHIÊN CỨU
1. **Evidence First & Zero Fabrication:** Không bịa đặt công thức toán học hoặc phương trình hóa học.
2. **In-Place DOM Word (.docx):** Bảo toàn 100% Heading styles, Mục lục tự động và Mã trường Zotero XML.
3. **Chuẩn hóa số thập phân tiếng Việt:** `1,5; 28,5%` và `1.000; 50.000`.
4. **Chuẩn hóa hóa học & toán học:** Tự động sửa chỉ số dưới (`FeS₂`, `H₂SO₄`...).

## 📝 NHẬT KÝ YÊU CẦU & KẾT QUẢ XỬ LÝ
- **Yêu cầu 1:** Tách thành 3 lựa chọn riêng biệt theo skill `SKILL_DOCX_MATH_CHEM_CHART_PRO`.
  - *Kết quả:* Đã tích hợp 3 radio button trên UI và tham số `upgrade_mode` trong backend.
- **[2026-08-25 11:18] Yêu cầu 2:** Triệt tiêu 100% ký hiệu LaTeX $ và chuyển đổi toàn bộ công thức toán Hy Lạp, phân số, chỉ số dưới hóa học sang Unicode chuẩn trong Word.
- **Yêu cầu 3 (2026-08-26):** Mở rộng thư viện công thức mẫu sang 5 lĩnh vực chuyên sâu (Môi trường, Hóa sinh, Kinh tế lượng, Thống kê, Khoa học Dữ liệu & AI).
  - *Kết quả:*
    - Cập nhật thư viện `PRESET_EQUATIONS` trong `static/js/math-chem-pro.js` với các công thức tiêu biểu của cả 5 chuyên ngành.
    - Tự động chuyển đổi sang Microsoft Word Equation `<m:oMath>` và hỗ trợ diễn giải 4 yếu tố bắt buộc.
- **Yêu cầu 4 (2026-08-26 - Milestone M2 DOM Preservation & Math/Chem):** Khắc phục toàn diện chuẩn hóa số thập phân tiếng Việt, mở rộng bảng ánh xạ hóa học `UNICODE_CHEM_MAP` và bảo toàn 100% In-Place Run-level DOM.
  - *Kết quả:*
    - Sửa chuỗi thay thế regex trong `DocxStyler.convert_decimals_preserve_sections` (`r' , '` -> `r'\1,\2'`), hỗ trợ chuẩn hóa dấu phẩy thập phân (`1,5; 28,5%; 0,05`) và dấu chấm phân cách hàng nghìn (`1.000; 50.000`).
    - Bổ sung 77 hợp chất và ion môi trường vào `UNICODE_CHEM_MAP` trong `modules/shared/docx_formula_engine.py` (đạt 109 hợp chất bao gồm `Ca(OH)₂`, `HNO₃`, `H₃PO₄`, `Cu²⁺`, `Pb²⁺`, `Cd²⁺`, `Cr⁶⁺`, `As³⁺`, `PM₂.₅`, `PM₁₀`...).
    - Khởi tạo thuật toán thay thế không làm phẳng Run `replace_text_in_paragraph_runs`, bảo toàn màu sắc, chữ đậm, chữ nghiêng riêng biệt trên từng Run trong Word .docx.
- **Yêu cầu 5 (2026-08-26 - Multi-Agent & E2E Validation):**
  - *Kết quả:* Vượt qua 100% các kịch bản kiểm thử `test_survey_dom.py`, `test_dom_preservation_edge_cases.py`, `test_m2_docx_math_chem.py` (**5/5 PASS**) và `test_docx_editor_engine.py` (**10/10 tests PASS**).
- **Yêu cầu 6 (2026-08-27 - Khắc Phục Lỗi Đóng Gói `word/media` & Nâng Cấp Giao Diện Tab 8):**
  - *Vấn đề:* Các tệp Word học thuật tải về từ OJS/Pandoc/Google Docs có các tệp ảnh trong `word/media/` với đuôi bất thường như `.undefined` hoặc thiếu khai báo MIME trong `[Content_Types].xml`, làm `python-docx` (`Document()`) ném lỗi `KeyError: "no content type for partname '/word/media/bc7e...undefined' in [Content_Types].xml"`. Giao diện Tab 8 có thanh cuộn công thức chưa tối ưu, thiếu bộ lọc chuyên ngành và nút nâng cấp 1-click chưa hỗ trợ chọn trực tiếp từ Workspace.
  - *Kết quả xử lý:*
    1. **Hàm Universal `sanitize_and_repair_docx` (`modules/shared/docx_styler.py`):** Phân tích magic bytes của mọi tệp trong `word/media/` (JPEG, PNG, GIF, BMP, EMF, WMF, TIFF, SVG), tự động tạo các thẻ `<Default Extension="...">` và `<Override PartName="...">` hợp lệ trong `[Content_Types].xml`, đồng bộ `word/_rels/document.xml.rels`, loại bỏ directory entries rỗng. Đã giải cứu thành công **100% (26/26 tệp)** bị lỗi.
    2. **Bảo Vệ Đa Tầng Mở File Word:** Tích hợp `sanitize_and_repair_docx` vào toàn bộ các module xử lý DOCX: `modules/math_chem_pro/math_chem_router.py`, `modules/workspace/docx_editor_engine.py`, `modules/workspace/workspace_router.py`, `modules/humanizer/humanizer_router.py`, `modules/zotero/zotero_converter_engine.py`.
    3. **Tái Thiết Kế Giao Diện Tab 8:**
       - **Subtab 1 (Toán & Hóa):** Thêm thanh Pills 5 chuyên ngành (`Tất cả`, `Môi trường`, `Hóa sinh`, `Kinh tế lượng`, `Thống kê`, `AI & Dữ liệu`), ô tìm kiếm công thức, danh sách có thanh cuộn tối đa 280px; nút Sao chép OMML XML và nút "⚡ Đưa sang Nâng Cấp Word".
       - **Subtab 2 & 3 (Biểu đồ & Sơ đồ):** Sửa lỗi hiển thị, bổ sung nút liên thông "⚡ Nhúng Vào File Word" gán trực tiếp tên tệp ảnh 300 DPI sang Subtab 5.
       - **Subtab 4 (Wikimedia):** Thêm gợi ý từ khóa Quick Search Chips (Mekong Delta, Acid sulfate soil, Bioreactor, Mangrove, Biochar, Salinity).
       - **Subtab 5 (Nâng Cấp Word 1-Click):** Bổ sung bộ chọn nguồn tệp kép (Tab Chọn từ Workspace / Tab Tải từ máy tính), hỗ trợ quét chuẩn hóa ký hiệu hóa học trong cả văn bản và bảng biểu, chuyển đổi LaTeX `$$...$$` thành Word Equation OMML, áp dụng chuẩn số thập phân tiếng Việt (`1,5; 28,5%`), và nút mở ngay trong Trình Biên Tập Số Liệu sau khi xử lý.
    4. **Kiểm thử tự động:** Vượt qua 100% test suite `test_math_chem_pro_full.py` và `test_batch_25_enhance.py` (26/26 tệp PASS).
- **Yêu cầu 7 (2026-08-28 - Tự Động Quét & Chuyển Đổi Công Thức Toán - Hóa Đẹp Chuẩn trong File Word .docx):**
  - *Vấn đề:* Người dùng nhập file Word `.docx` chứa các công thức toán LaTeX (`$$...$$`, `$math$`), phương trình hóa học và ion chưa chuẩn hóa khiến văn bản hiển thị vỡ, tràn dòng và thô như văn bản thô (raw text).
  - *Kết quả xử lý:*
    1. **Nâng cấp `modules/shared/docx_formula_engine.py`:**
       - Tích hợp `scan_and_enhance_document_formulas`: Tự động quét toàn diện 100% các đoạn văn bản (paragraphs) và tất cả ô trong bảng biểu (tables).
       - Khối công thức Block LaTeX (`$$...$$` hoặc `\[...\]`): Chuyển đổi sang thẻ chuẩn Microsoft Word Equation `<m:oMathPara><m:oMath>...</m:oMath></m:oMathPara>` căn giữa, cách lề chuẩn 6pt, tách biệt số thứ tự phương trình `(1.1)`.
       - Công thức toán nội dòng Inline LaTeX (`$...$` hoặc `\(...\)`): Tách chuỗi và nhúng trực tiếp đối tượng `<m:oMath>` nội dòng, hiển thị đồng nhất trên dòng chữ với font Cambria Math sắc nét, không bị ngắt dòng hay vỡ layout.
       - Chuẩn hóa ký hiệu hóa học & phản ứng: Bổ sung hàm `format_chemical_text` tự động chuyển đổi 109+ hợp chất hóa học, ion (`Fe³⁺`, `SO₄²⁻`, `NH₄⁺`, `NO₃⁻`, `Al³⁺`, `BOD₅`, `PM₂.₅`...), phân tử ngậm nước (`CuSO₄·5H₂O`) và các mũi tên phản ứng (`→`, `⇌`, `⟶`).
       - Chuẩn hóa số thập phân tiếng Việt (`1,5; 28,5%`) và phân cách hàng nghìn (`10.000; 50.000`) mà không gây ảnh hưởng đến định danh DOI.
    2. **Tối ưu hóa Giao diện Subtab 5 (`static/index.html` & `static/js/math-chem-pro.js`):**
       - Thêm vùng Kéo thả & Duyệt tệp Word (.docx) chuyên dụng (`mathchem-drop-zone`).
       - Thêm nhãn trạng thái tệp đã chọn và nút thực thi lớn: `🚀 Quét & Nâng Cấp Công Thức Toán - Hóa Toàn Diện (.docx)`.
       - Hộp kết quả hiển thị 4 huy hiệu thống kê chi tiết (Số vị trí hóa học, số công thức OMML, số vị trí số thập phân, số bảng biểu) cùng đầy đủ 4 nút hành động: *📝 Mở Trực Tiếp Trên Word (.docx)*, *⬇️ Tải Về (.docx)*, *📊 Mở Trong Trình Biên Tập Số Liệu*, và *📂 Mở Folder Workspace*.
    3. **Kiểm thử tự động:** Vượt qua 100% test suite `test_math_chem_docx_enhancer.py` (**16/16 assertions PASS**) và endpoint API kiểm thử trực tiếp.
- **Yêu cầu 8 (2026-09-16 - Tích hợp PubChem Database & Phân Giải Cấu Trúc Hóa Học 2D):**
  - *Mục tiêu:* Bổ sung kho dữ liệu hóa học chuẩn quốc tế NIH PubChem, phục vụ tra cứu phân tử, tính chất lý hóa, danh pháp IUPAC, khối lượng mol và cấu trúc 2D.
  - *Kết quả xử lý:*
    1. **Backend Engine (`modules/shared/pubchem_service.py`):** Lớp `PubChemService` tích hợp PUG-REST API và Local Curated Cache cho các chất/ion môi trường (`FeS₂`, `H₂SO₄`, `NH₄⁺`, `Glyphosate`, `Chitosan`, `Urea`...).
    2. **API Endpoints (`modules/math_chem_pro/math_chem_router.py`):** Cung cấp `POST /api/math-chem/pubchem-resolve` và `GET /api/math-chem/pubchem-image/{cid}`.
    3. **Giao diện Subtab 6 (`static/index.html` & `static/js/math-chem-pro.js`):** Thêm Subtab 6 "🧪 Tra Cứu PubChem Database" với Quick Chips, thẻ ảnh cấu trúc 2D, bảng thông số SMILES/InChIKey, nút nạp trực tiếp vào OMML Word Equation và nút sao chép trích dẫn chuẩn APA 7th.
    4. **Kiểm thử:** 100% test case trong `test_pubchem_service.py` đạt trạng thái PASS.
- **Yêu cầu 9 (2026-09-25 - Đồng Bộ Hóa Toàn Diện Chuẩn Toán - Hóa & Quy Tắc Diễn Giải 4 Thành Phần Vào Hệ Thống Kỹ Năng Viết):**
  - *Mục tiêu:* Thiết lập chuẩn mực thể hiện công thức toán học và ký hiệu hóa học thống nhất giữa module Tab 8 Math-Chem Pro với toàn bộ hệ thống kỹ năng viết học thuật (`academic-evidence-writer`, `vietnamese-academic-researcher`, `zotero-academic-writer`, `research-paper-writing`, `viet-chuyen-nghiep`).
  - *Kết quả xử lý:*
    1. **Tích hợp Quy tắc Diễn giải 4 Thành phần Bắt buộc:** Chống công thức mồ côi; mọi công thức/phương trình sinh ra trong văn bản BẮT BUỘC có 4 yếu tố: (1) Tên gọi, nguồn gốc APA 7th & mục đích, (2) Định nghĩa rõ từng biến số, (3) Đơn vị đo lường chuẩn khoa học, và (4) Ý nghĩa môi trường/kinh tế thực chứng.
    2. **Đồng bộ hóa Ký hiệu Hóa học Run-level DOM:** Bảo toàn 100% mã trường Zotero XML khi định dạng Subscript/Superscript cho 109+ hợp chất và ion môi trường.
    3. **Chuẩn hóa số thập phân tiếng Việt:** Bắt buộc dùng dấu phẩy cho số thập phân (`1,5; 28,5%`), dấu chấm cho hàng nghìn (`1.000; 50.000`), giữ nguyên dấu chấm cho số thứ tự mục (`1.1.`, `2.1.`).
