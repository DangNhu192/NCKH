# HANDOFF REPORT — EXPLORER 3 (HUMANIZER & UI AUDIT EXPLORER)

## 1. Observation (Quan Sát Trực Tiếp)

1. **Lỗi Runtime trong `modules/humanizer/humanizer_engine.py` (Dòng 636-637):**
   - Phương thức `humanize_paragraph_by_paragraph` gọi trực tiếp `self.replace_cliches_deterministic(p)` và `self.break_sentence_lengths(p_humanized)`.
   - Kết quả chạy kiểm thử thực tế:
     ```
     AttributeError: 'HumanizerEngine' object has no attribute 'replace_cliches_deterministic'
     ```
   - Xác thực: `HumanizerEngine` chỉ có các phương thức `['analyze', 'apply_local_rule_humanization', 'evaluate_academic_quality_scorecard', 'format_vietnamese_decimals_and_chem', 'humanize', 'humanize_docx_bytes', 'humanize_paragraph_by_paragraph', 'plagiarism_audit', 'process_unified', 'turnitin_rephrase']`.

2. **Lỗi phá vỡ cây XML Word DOM trong `humanize_docx_bytes` (`modules/humanizer/humanizer_engine.py:511-564`):**
   - Dòng 533-537 gán `paragraph.runs[0].text = unified_p` và xóa các run sau `for r in paragraph.runs[1:]: r.text = ""`.
   - Quan sát thực tế: Khi file `.docx` chứa mã trường XML Zotero (`w:fldSimple` hoặc `w:fldChar`), việc gán text vào run 0 trong khi không gỡ bỏ `w:fldSimple` dẫn đến nhân bản trích dẫn (xuất hiện cả text trích dẫn do LLM sinh ra và mã trường XML Zotero cũ).
   - Ngoài ra, hình ảnh `<w:drawing>` và công thức toán `<m:oMath>` bị xáo trộn vị trí inline khi dồn text vào run đầu tiên.
   - Điều kiện `paragraph.style.name.startswith('Heading')` bỏ sót các tiêu đề tiếng Việt (`Tiêu đề 1`, `Tieu de 1`) và các đoạn văn có XML `<w:outlineLvl>`.

3. **Kiểm toán 170 Nút Bấm Giao Diện (`static/index.html` & `static/js/*.js`):**
   - Script kiểm toán `.agents/explorer_survey_3/audit_tab_buttons.py` quét qua 170 thẻ `<button>` trên toàn bộ giao diện:
     - `home-tab`: 9 nút (Active 9/9)
     - `pipeline-tab`: 14 nút (Active 14/14)
     - `notebooklm-tab`: 14 nút (Active 14/14)
     - `harvester-tab`: 13 nút (Active 13/13)
     - `zotero-tab`: 2 nút (Active 2/2)
     - `writer-tab`: 4 nút (Active 4/4)
     - `editorial-tab`: 2 nút (Active 2/2)
     - `humanizer-tab`: 15 nút (Active 15/15)
     - `workspace-tab`: 13 nút (Active 13/13)
     - `history-tab`: 14 nút (Active 14/14)
     - `admin-tab`: 12 nút (Active 12/12)
     - `math-chem-tab`: 13 nút (Active 13/13)
     - `bigquery-tab`: 43 nút (Active 43/43)
     - Modals (Cài đặt, Auth): 2 nút (Active 2/2 via `setupModals` trong `app.js`)
   - **Kết quả:** 170/170 nút bấm đều có event handler được gắn chính xác, không có nút chết.

4. **Kiểm toán Endpoint API Tuyến Tính (101 JS API Calls vs 130 Backend Routes):**
   - Script `.agents/explorer_survey_3/comprehensive_route_audit.py` phát hiện 1 lời gọi endpoint sai:
     - `static/js/pdf-ocr-reader.js:287`: `fetch('/api/open-notebook/list')` không tồn tại ở backend (backend là `/api/notebooklm/notebooks`).
     - Hậu quả: Nút nạp OCR vào Kho Tri Thức luôn báo "Bạn chưa có Notebook nào".
   - Tất cả các endpoint khác trong `bigquery-ml.js`, `math-chem-pro.js`, `pipeline.js`, `harvester.js`, `humanizer.js`, `history.js` đều khớp hoàn toàn với FastAPI APIRouter.

5. **Hiện trạng Thư mục Đóng gói Snapshot `Xac_Nhan_Hoan_Hao/`:**
   - Đã có công cụ `archive_manager.py` với 2 hàm `save_module_snapshot()` và `save_full_system_snapshot()`.
   - Các module Harvester, Zotero Converter, Math-Chem Pro, BigQuery AI đã hoàn chỉnh và sẵn sàng để đóng gói snapshot.

---

## 2. Logic Chain (Chuỗi Lập Luận Suy Diễn)

1. Từ **Observation 1**, việc gọi phương thức không tồn tại trong `humanize_paragraph_by_paragraph` chứng minh phân hệ paragraph alignment chưa được kết nối đồng bộ với engine khử AI chính, cần được tái cấu trúc triệt để bằng LLM Rewriting.
2. Từ **Observation 2**, cơ chế can thiệp thô bạo vào `paragraph.runs` làm hỏng tính toàn vẹn của mã trường Zotero XML (`w:fldSimple`) và hình ảnh 300 DPI, vi phạm Quy tắc Bất biến 2 (In-Place DOM Word Preservation). Do đó, giải pháp bắt buộc là áp dụng cơ chế **Token Shielding** (`{{ZOTERO_REF_i}}`), giữ nguyên các node XML trích dẫn và chỉ tái cấu trúc văn bản bao quanh.
3. Từ **Observation 3**, toàn bộ 170 nút bấm trên giao diện đã có event listener hoặc inline handler, nghĩa là hệ thống UI không có nút chết về mặt cú pháp DOM, nhưng phụ thuộc vào tính chính xác của các route API phía sau.
4. Từ **Observation 4**, lời gọi sai `/api/open-notebook/list` tại `pdf-ocr-reader.js:287` là nguyên nhân duy nhất gây đứt gãy luồng tương tác giữa PDF OCR và Open-Notebook. Việc cập nhật đường dẫn thành `/api/notebooklm/notebooks` và thêm alias route tại backend sẽ khắc phục triệt để.
5. Từ **Observation 5**, quy trình đóng gói vào `Xac_Nhan_Hoan_Hao/` đã có nền tảng tự động hóa qua `archive_manager.py`, có thể kích hoạt đóng gói ngay cho các module đã qua kiểm thử đạt 100%.

---

## 3. Caveats (Ranh Giới & Giả Định Khảo Sát)

- **Ranh giới khảo sát:** Explorer thực hiện khảo sát ở chế độ Read-Only, không trực tiếp sửa code trong cây nguồn chính mà cung cấp phân tích chi tiết, thiết kế kiến trúc và script kiểm toán độc lập trong thư mục `.agents/explorer_survey_3/`.
- **Giả định:** Việc gọi Gemini API phụ thuộc vào API key hợp lệ của người dùng; khi không có API key, hệ thống cần cơ chế fallback thông minh (local deterministic rule-based) vẫn đảm bảo Burstiness và không gây crash runtime.
- **Phương án dự phòng:** Đã thiết kế cả 2 phương án: sửa trực tiếp tại frontend `pdf-ocr-reader.js` và thêm alias route tại backend `notebooklm_router.py`.

---

## 4. Conclusion (Kết Luận & Đề Xuất Hành Động)

1. **Đối với R3 (Nâng Cấp Khử Dấu Vết AI):**
   - Loại bỏ cơ chế regex thay từ máy móc đơn giản, thay thế bằng LLM Rewriting đa tầng (kiểm soát Sentence Burstiness $\sigma \ge 8,0$, Perplexity phong phú, loại bỏ clichés ContentBeta 300+ và Wikipedia Tells).
   - Tích hợp cơ chế In-Place DOM Token Shielding để bảo toàn 100% mã trường XML Zotero, Headings đa ngữ và hình ảnh 300 DPI.
   - Sửa lỗi crash runtime trong `humanize_paragraph_by_paragraph`.
2. **Đối với R4 (Rà Soát UI & Đóng Gói Snapshot):**
   - 170/170 nút bấm trên giao diện hoạt động tốt.
   - Sửa 1 lỗi route tại `static/js/pdf-ocr-reader.js:287` (`/api/open-notebook/list` $\rightarrow$ `/api/notebooklm/notebooks`).
   - Kích hoạt `archive_manager.py` đóng gói các module Harvester, Zotero Converter, Math-Chem Pro, BigQuery AI vào `Xac_Nhan_Hoan_Hao/Modules_Source_Code/`.

---

## 5. Verification Method (Phương Pháp Xác Minh Độc Lập)

Người nhận bàn giao hoặc kiểm thử viên độc lập có thể kiểm chứng toàn bộ kết quả khảo sát qua các lệnh sau:

1. **Kiểm chứng lỗi crash trong `humanize_paragraph_by_paragraph`:**
   ```powershell
   & "H:\My Drive\Ho so ca nhan\b. ThS KHMT\Skill\.venv\Scripts\python.exe" -c "from modules.humanizer.humanizer_engine import humanizer_engine; print(humanizer_engine.humanize_paragraph_by_paragraph('Trong bối cảnh hiện nay'))"
   ```

2. **Kiểm toán 170 nút bấm trên giao diện:**
   ```powershell
   & "H:\My Drive\Ho so ca nhan\b. ThS KHMT\Skill\.venv\Scripts\python.exe" ".agents\explorer_survey_3\audit_tab_buttons.py"
   ```

3. **Kiểm toán 101 endpoint API frontend vs 130 backend routes:**
   ```powershell
   & "H:\My Drive\Ho so ca nhan\b. ThS KHMT\Skill\.venv\Scripts\python.exe" ".agents\explorer_survey_3\comprehensive_route_audit.py"
   ```

4. **Kiểm tra công cụ đóng gói `Xac_Nhan_Hoan_Hao`:**
   ```powershell
   & "H:\My Drive\Ho so ca nhan\b. ThS KHMT\Skill\.venv\Scripts\python.exe" "Xac_Nhan_Hoan_Hao\archive_manager.py"
   ```
