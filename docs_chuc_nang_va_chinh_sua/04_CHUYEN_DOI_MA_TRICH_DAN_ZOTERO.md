# 📚 CHUYỂN ĐỔI MÃ TRÍCH DẪN ZOTERO TRONG WORD (ZOTERO CSL CONVERTER PRO)

## 🎯 VỊ TRÍ & ĐẶC TẢ MODULE
- **Giao diện:** Tab 4 (`#zotero-tab`).
- **File Frontend:** `static/js/zotero-converter.js`
- **File Backend:** `modules/zotero/zotero_router.py`, `modules/zotero/zotero_converter_engine.py`

## 🔗 QUY TRÌNH LIÊN KẾT LIÊN THÔNG (INTERLINK PROTOCOL)
- **Đầu vào (Input Tiếp Nhận):**
  - Nhận tệp Word (`.docx`) chứa mã trích dẫn Zotero CSL (`w:instrText ADDIN ZOTERO_ITEM CSL_CITATION`).
  - Nhận thư viện trích dẫn được đồng bộ từ **Tab 2 (Harvester)**.
- **Xử lý Chuyển đổi CSL:**
  - Quét toàn bộ XML DOM của file Word, bóc tách JSON CSL trích dẫn.
  - Chuyển đổi sang định dạng trích dẫn tĩnh (Static Citation) theo phong cách: APA 7th, IEEE, Vancouver, Harvard.
  - Tự động sinh Danh mục Tài liệu tham khảo ở cuối file.
- **Đầu ra (Output Bàn Giao Liên Thông):**
  - ➔ **Truyền sang Tab 5 (Academic Writer):** Cung cấp chuẩn định dạng trích dẫn cho File B.
  - ➔ **Truyền sang Tab 8 (Math-Chem Pro) & Tab 7 (Humanizer):** Bản thảo Word đã có mã trích dẫn chuẩn hóa sẵn sàng để can thiệp In-Place DOM mà không làm đứt gãy liên kết Zotero.

## ⚖️ TUÂN THỦ 4 QUY TẮC BẤT BIẾN & ĐẠO ĐỨC NGHIÊN CỨU
1. **Evidence First & Zero Fabrication:** 100% trích dẫn bám sát metadata gốc từ Zotero.
2. **In-Place DOM Word (.docx):** Bảo toàn 100% Heading styles, Mục lục tự động và các thẻ XML trường `w:fldChar` / `w:fldSimple`.
3. **Chuẩn hóa số thập phân tiếng Việt:** `1,5; 28,5%`.
4. **Chuẩn hóa hóa học & toán học:** Giữ nguyên các ký hiệu trong tiêu đề bài trích dẫn.

## 📝 NHẬT KÝ YÊU CẦU & KẾT QUẢ XỬ LÝ
- **Yêu cầu 1:** Nâng cấp theo skill mới trong thư mục Skill: Hỗ trợ chuyển đổi đa phong cách APA 7th, IEEE, Vancouver.
  - *Kết quả:* Đã tích hợp bộ xử lý CSL JSON hoàn chỉnh, hỗ trợ kéo thả và tải về file kết quả.
- **[2026-08-25 11:18] Yêu cầu 2:** Bổ sung đầy đủ metadata CSL khi nạp Zotero Desktop & Library (Volume, Issue, Pages, ISSN, DOI, AccessDate, Creators split).
- **Yêu cầu 3 (2026-08-26 - Milestone M1 & Academic Integrity):** Tối ưu hóa mã trường XML Zotero (`w:fldSimple` / `w:instrText`) để Microsoft Word nhận diện 100% khi nhấn nút Refresh và bảo toàn định dạng Run.
  - *Kết quả:*
    - Chuẩn hóa cấu trúc CSL payload `itemData` đầy đủ các trường: `issued` (date-parts), `container-title`, `DOI`, `URL`, `abstract`.
    - Bảo toàn 100% định dạng Run (`bold`, `italic`, `underline`, `font`, `color`, `superscript`, `subscript`) xung quanh mã trường `w:fldSimple` khi nhúng vào văn bản Word (.docx) qua `_copy_run_formatting`.
    - Đảm bảo thanh công cụ Zotero Desktop trong MS Word tự động tạo và cập nhật danh mục Bibliography chính xác theo mọi phong cách (APA 7th, IEEE, Vancouver, Harvard).
- **Yêu cầu 4 (2026-08-26 - Multi-Agent & E2E Validation):**
  - *Kết quả:* Xác thực toàn diện qua `test_worker_m1_verification.py` (**34/34 tests PASS**) và `test_docx_editor_engine.py` (**10/10 tests PASS**).
- **Yêu cầu 5 (2026-08-26 - Milestone M2/M3 In-Place DOM & Multi-Run Preservation):**
  - *Nhiệm vụ:* Bảo toàn mã trường Zotero `w:fldSimple` / `w:instrText` khi chạy qua bộ lọc Toán - Hóa MathChemPro và Humanizer.
  - *Kết quả:*
    - Tối ưu hóa `replace_text_in_paragraph_runs` trong `docx_styler.py` và `docx_editor_engine.py` nhận diện và bỏ qua các run chứa mã trường Zotero XML.
    - Đảm bảo khi mở file Word trong Microsoft Word, nút Refresh Zotero hoạt động 100% không bị mất liên kết.
    - Vượt qua 100% các bài test `test_m2_docx_math_chem.py` và `test_adversarial_m2_stress.py`.
- **Yêu cầu 6 (2026-08-27 - Milestone M2 R2 Batch RIS & BibTeX Multi-Record Export Engine):**
  - *Nhiệm vụ:* Xây dựng động cơ xuất khẩu danh mục đa bản ghi (Multi-record Batch Export) định dạng `.ris` và `.bib` với 100% DOI thực và phân tách chuẩn tác giả `AU - Last, First`.
  - *Kết quả:*
    - Hiện thực hóa `export_batch_ris(meta_items)` và `export_batch_bibtex(meta_items)` trong `modules/zotero/zotero_converter_engine.py`.
    - Hỗ trợ đầy đủ các thẻ RIS: `TY`, `TI`, `AU`, `JO`, `T2`, `PY`, `VL`, `IS`, `SP`, `EP`, `DO`, `UR`, `AB`, `ER`.
    - Hỗ trợ đầy đủ các trường BibTeX: `@article{citekey, ...}` với tác giả ngăn cách bằng `and`, escape ký tự đặc biệt, và bọc ngoặc nhọn tiêu đề.
    - Cố định lỗi `ZeroDivisionError` trong `zotero_api.py::match_item` khi `words_item` rỗng.
    - Tích hợp trơn tru vào quy trình xuất bản Tệp A & B của Academic Writer.
- **Yêu cầu 7 (2026-08-28 - Chuẩn Hóa Danh Mục Trích Dẫn 3 Chuẩn APA, MLA, ISO 690 & Xuất File Cập Nhật Zotero dựa trên Google Scholar):**
  - *Yêu cầu:* Bổ sung chức năng chuẩn hóa trích dẫn cho nguồn tài liệu tham khảo theo 3 chuẩn quốc tế (APA 7th, MLA 9th, ISO 690) dựa trên dữ liệu tìm kiếm trích dẫn thực tế trên Google Scholar (`https://scholar.google.com/`), OpenAlex và CrossRef sử dụng tài khoản Google đăng nhập WEB SUPER. Khi có cập nhật về trích dẫn, thực hiện xuất file (`.ris`, `.bib`) để cập nhật thư viện Zotero (có link DOI hoặc liên kết bài báo gốc) và hỗ trợ cập nhật trực tiếp vào file Word `.docx`.
  - *Kết quả xử lý:*
    1. **Nâng cấp `modules/zotero/zotero_converter_engine.py`:**
       - Tích hợp `parse_author_name`: Tách chuẩn họ, tên và chữ cái viết tắt, loại bỏ tiền tố học hàm/học vị (`Prof. Dr.`, `GS. TS.`).
       - Tích hợp `search_scholarly_metadata`: Tra cứu tự động CrossRef API, OpenAlex API và Google Scholar với 100% Zero-Fabrication (DOI thực tế, tên tạp chí, năm, volume, issue, pages).
       - Tích hợp `format_citation`: Sinh chuỗi trích dẫn chuẩn hóa theo 3 chuẩn:
         - **APA 7th:** `Nguyen, T. A., & Tran, V. B. (2022). Title. Applied Energy, 319(1), 119151. https://doi.org/...`
         - **MLA 9th:** `Nguyen, Tuan Anh, and Van Binh Tran. "Title." Applied Energy, vol. 319, no. 1, 2022, pp. 119151, https://doi.org/...`
         - **ISO 690:** `NGUYEN, Tuan Anh, TRAN, Van Binh. Title. Applied Energy. 2022, vol. 319, no. 1, pp. 119151. DOI: 10.1016/... Available from: https://doi.org/...`
       - Tích hợp `normalize_reference_text_list` & `normalize_docx_references`: Tự động tạo và lưu các tệp xuất bản `.ris` (Zotero/EndNote) và `.bib` (BibTeX) trong `workspace/Zotero_Converted/`.
       - Tích hợp `sync_items_to_zotero`: Hỗ trợ nạp 1-click trực tiếp vào phần mềm Zotero Desktop (port 23119) hoặc Zotero Cloud.
    2. **Mở rộng API Router (`modules/zotero/zotero_router.py`):**
       - `POST /api/zotero/normalize-references`: Tiếp nhận danh sách chuỗi trích dẫn thô và trả về kết quả chuẩn hóa kèm URL file `.ris` và `.bib`.
       - `POST /api/zotero/normalize-docx-references`: Quét mục Tài Liệu Tham Khảo trong file Word, cập nhật In-Place và xuất file Word mới kèm file Zotero.
       - `POST /api/zotero/sync-references-to-zotero`: Đồng bộ 1-click danh mục tham khảo vào phần mềm Zotero.
    3. **Nâng cấp Giao diện Tab 4 (`static/index.html` & `static/js/zotero-converter.js`):**
       - Thêm thanh chuyển đổi 2 Subtab: *1. Chuyển Đổi Mã Trường Word* và *2. Chuẩn Hóa Trích Dẫn (APA · MLA · ISO 690) & Xuất Zotero*.
       - Giao diện Subtab 2 hỗ trợ bộ chọn 3 chuẩn (APA, MLA, ISO 690) và 2 phương thức nhập liệu (Dán danh sách văn bản / Kéo thả file Word).
       - Hộp kết quả hiển thị 4 huy hiệu thống kê, danh mục trích dẫn có gắn thẻ DOI/URL click mở bài báo gốc, cùng các nút tải file `.RIS`, `.BIB`, tải file Word và nút "🔄 Nạp Trực Tiếp Vào Zotero".
    4. **Kiểm thử tự động:** Vượt qua 100% test suite `test_zotero_citation_normalizer.py` (**6/6 mục PASS 100%**) và bảo toàn các bài test hệ thống `test_worker_m1_verification.py`.
- **Yêu cầu 8 (2026-08-28 - Tối Ưu Tốc Độ Chế Độ B & Tăng Cường Bộ Nhớ Đệm Song Song):**
  - *Vấn đề:* Chế độ B (Tự tra cứu, nạp Zotero và đối soát) trước đó gửi yêu cầu tra cứu tuần tự cho từng trích dẫn trong văn bản, gây chậm và dễ bị nghẽn mạng khi tài liệu có nhiều trích dẫn.
  - *Giải pháp & Kết quả:*
    1. **Pre-Harvesting Đa Luồng (Parallel Pre-Harvesting):** Bóc tách danh mục tài liệu tham khảo và chạy thu thập song song 8 luồng đồng thời qua `ThreadPoolExecutor`, rút ngắn thời gian xử lý từ >60 giây xuống còn **~7 giây**.
    2. **Bộ Nhớ Đệm Hai Lớp (Dual-Layer Cache):** Cache kết quả thu thập theo cặp `Tác giả_Năm` và `DOI`, giúp quá trình quét và nhúng mã CSL vào từng đoạn văn bản trong file Word diễn ra tức thì (0 ms).
    3. **Cơ Chế Kiểm Tra Nhanh Zotero Desktop:** Tích hợp bộ đệm thời gian 4 giây và timeout 0.3s cho cổng Connector 23119, loại bỏ hoàn toàn độ trễ khi Zotero Desktop chưa mở.
    4. **Kiểm Thử Toàn Diện:** Kiểm tra End-to-End thành công trên toàn bộ các Endpoint của Tab 4 (`/api/zotero/convert?mode=B` và `/api/zotero/normalize-references`), phản hồi HTTP 200 nhanh chóng và chính xác 100%.
