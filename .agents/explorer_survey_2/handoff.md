# 🤝 BÁO CÁO BÀN GIAO ĐIỀU TRA HỌC THUẬT & ZOTERO DOM (HANDOFF REPORT - R2)

**Người thực hiện:** Explorer 2 (Academic Writer & Zotero Explorer)  
**Thời gian hoàn thành:** 2026-08-27T07:56:30+07:00  
**Không gian làm việc:** `H:\My Drive\Ho so ca nhan\b. ThS KHMT\Skill\Web Super\.agents\explorer_survey_2\`  
**Nhiệm vụ:** Điều tra chuyên sâu & Thiết kế giải pháp cho Yêu cầu R2: Nâng cấp Viết Học Thuật 2-File (Pure LLM drafting, Zotero XML DOM injection, and RIS/BIB bibliography generation)  

---

## 1. Observation (Quan Sát Trực Tiếp)

1. **Mad-Libs Templates trong Academic Writer:**
   - Tại `modules/academic_writer/academic_writer_engine.py:818-970`, hàm `_synthesize_grounded_academic_section()` chứa các đoạn văn mẫu gán cứng:
     * Dòng 846: `"$$\\dot{\\mathbf{x}}(t) = \\mathbf{A}\\mathbf{x}(t) + \\mathbf{B}\\mathbf{u}(t) + \\mathbf{f}(\\mathbf{x}(t), \\mathbf{w}(t))$$"`
     * Dòng 889: `"$$\\min_{\\mathbf{u}(t) \\in \\mathcal{U}} \\mathcal{J} = \\sum_{t=1}^{T} \\Big[ \\alpha \\cdot P_{\\text{loss}}(\\mathbf{x}(t), \\mathbf{u}(t)) + \\dots \\Big]$$"`
     * Dòng 903: `"| **Tổng quy mô mẫu quan sát** | $N_{\\text{total}}$ | 18.500 | Bản ghi chuỗi thời gian |"`
     * Dòng 919: `"| **4. Mô hình Tối ưu Đa tác tử (Đề xuất)** | **8,65 MW (-41,6%)** | **2,15%** | **1,45 giây (-92,1%)** |"`
   - Tại `academic_writer_engine.py:1134-1142`, `evidence_block` truyền vào cho LLM chỉ nối `abstract` của 6 bài báo đầu tiên, chưa khai thác phân đoạn mục tiêu (Introduction/Method/Results) từ `open_notebook_engine`.

2. **Tách Rời Mã Trường Zotero CSL XML trong File A:**
   - Tại `academic_writer_engine.py:1265-1274`, `generate_2_files()` xuất bản Tệp A thông qua `DocxStyler.render_markdown_body()`, chỉ tạo các Run văn bản tĩnh (ví dụ: `(Vaswani et al., 2017)`), hoàn toàn KHÔNG chứa mã trường `w:fldSimple` Zotero CSL.
   - Tại `modules/zotero/zotero_converter_engine.py:1235-1317`, hàm `build_csl_field_xml()` đã có sẵn cấu trúc chuẩn `w:fldSimple` với payload JSON CSL `itemData` và `_copy_run_formatting()`, nhưng chỉ được gọi khi người dùng thao tác riêng tại Tab 4 hoặc Pipeline Bước 6.

3. **Thiếu Bộ Xuất Thư Mục Đồng Hành .ris và .bib:**
   - Tại `modules/zotero/zotero_converter_engine.py:279-303`, hàm `generate_ris()` chỉ xuất 1 bài báo đơn lẻ. Chưa có hàm xuất danh mục multi-record RIS.
   - Toàn bộ codebase không có bộ xuất định dạng BibTeX (`.bib`).
   - Tại `academic_writer_engine.py:1333-1378`, kết quả trả về chỉ gồm `file_a` và `file_b`, thiếu tệp `.ris` và `.bib` đồng hành.
   - Tại `static/js/academic-writer.js:359-380`, giao diện chỉ hiển thị 2 nút mở/tải cho Tệp A và Tệp B.

---

## 2. Logic Chain (Chuỗi Lập Luận Suy Luận)

1. Từ **Quan sát 1**, việc giữ các chuỗi số liệu mẫu cố định trong `_synthesize_grounded_academic_section()` khiến hệ thống bị phụ thuộc vào khuôn mẫu khi LLM gặp sự cố, dẫn đến nguy cơ sai lệch số liệu và sinh nội dung lạc đề đối với các chuyên ngành khác (Y học, Kinh tế, Luật...). Do đó, cần thay thế hoàn toàn bằng cơ chế soạn thảo LLM đa tầng có ngữ cảnh phân đoạn từ Evidence Vault/Open-Notebook.
2. Từ **Quan sát 2**, việc Tệp A không có mã trường Zotero XML trực tiếp làm gián đoạn trải nghiệm người dùng, vi phạm tiêu chí "Viết Học Thuật 2-File xuất bản chuẩn Zotero 1-Click". Do `zotero_converter_engine.py` đã có sẵn bộ sinh XML `w:fldSimple` hoàn hảo, việc kích hoạt tự động `convert_docx` ngay sau khi tạo Tệp A sẽ nhúng trực tiếp mã trường Zotero vào cây DOM Word mà không cần người dùng thao tác thêm.
3. Từ **Quan sát 3**, người dùng Zotero và LaTeX/Overleaf cần nạp danh mục tài liệu vào phần mềm quản lý thư viện của họ. Việc tạo thêm 2 tệp đồng hành `File_References_{topic}.ris` và `File_References_{topic}.bib` với 100% DOI thật và siêu dữ liệu thực tế từ Evidence Vault sẽ giải quyết trọn vẹn yêu cầu xuất bản Zotero Bibliography.

---

## 3. Caveats (Các Điểm Lưu Ý & Ranh Giới)

1. **Phụ thuộc API / Offline Mode:** Khi offline hoặc không có API Key, hệ thống cần dựa vào tài liệu nền tảng học thuật quốc tế đã kiểm chứng (như Vaswani et al., 2017; LeCun et al., 2015) hoặc các tệp bài báo sẵn có trong `Tai_Lieu/`, tuyệt đối không sinh DOI giả mạo.
2. **Khả năng tương thích MS Word:** Mã trường Zotero `w:fldSimple` khi mở trong MS Word yêu cầu người dùng bấm nút **Refresh** trên tab Zotero để hiển thị đúng định dạng CSL mong muốn (APA 7th, IEEE...).
3. **Độ dài tệp RIS/BIB:** Cần đảm bảo các ký tự đặc biệt trong tiêu đề/tác giả được escape chuẩn (nhất là dấu ngoặc nhọn `{}` trong BibTeX).

---

## 4. Conclusion (Kết Luận & Định Hướng Triển Khai)

Kiến trúc nâng cấp R2 đã được khảo sát toàn diện và hoàn thiện thiết kế kỹ thuật:
1. **Academic Writer Engine:** Tích hợp Section-Aware Context Retrieval từ Evidence Vault / Open-Notebook; loại bỏ mad-libs gán cứng; tự động chạy `zotero_converter.convert_docx()` trên Tệp A để nhúng mã trường `w:fldSimple` trực tiếp vào DOM Word.
2. **Bibliography Exporter:** Bổ sung `export_batch_ris()` và `export_batch_bibtex()`, xuất bản tự động 2 tệp `File_References_{topic}.ris` và `File_References_{topic}.bib` với 100% DOI thật.
3. **API & UI:** Trả về đường dẫn `.ris` và `.bib` trong response `/api/writer/generate-2file` và thêm nút tải 1-click trên giao diện `#writer-tab`.

---

## 5. Verification Method (Phương Pháp Kiểm Tra & Xác Thực)

1. **Kiểm tra cú pháp Word DOM & Zotero XML:**
   - Mở Tệp A sinh ra bằng `python-docx`, kiểm tra XML của các paragraph:
     ```python
     doc = Document("workspace/Tai_Lieu/File_A_Topic.docx")
     xml_all = "\n".join(p._p.xml for p in doc.paragraphs)
     assert "<w:fldSimple" in xml_all
     assert "ADDIN ZOTERO_ITEM CSL_CITATION" in xml_all
     ```
2. **Kiểm tra tệp .ris và .bib:**
   - Kiểm tra tệp `.ris` chứa đầy đủ các thẻ: `TY  - JOUR`, `TI  - `, `AU  - `, `DO  - `, `ER  - `.
   - Kiểm tra tệp `.bib` chứa cú pháp BibTeX hợp lệ: `@article{...}`.
3. **Kiểm tra Zero-Fabrication:**
   - Khẳng định 100% DOI trong Tệp A, Tệp B, file `.ris`, file `.bib` đều là DOI thực tế, không có DOI giả lập (`10.1016/j.artint.2022.103450`...).
4. **Lệnh chạy kiểm thử dự án:**
   ```bash
   uv run python test_worker_m1_verification.py
   ```
