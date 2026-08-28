# Original User Request

## 2026-08-27T00:50:47Z

Requested team: Đội ngũ Đa Tác Nhân Cải Tổ Toàn Diện UI/UX, Pipeline 7 Bước, Viết Học Thuật AI & Khử Dấu Vết AI

Tiến hành cải tổ toàn diện nền tảng WEB SUPER, rà soát từng thẻ giao diện, sửa chữa các nút bấm không phản hồi, thay thế các logic 'điền vào chỗ trống / regex máy móc' bằng AI thực thụ cho Viết học thuật 2-File và Khử dấu vết AI, nâng cấp Bước 1 Pipeline với bóc tách từ khóa học thuật AI kết hợp EuropePMC/OpenAlex, và đóng gói các module hoàn hảo vào `Xac_Nhan_Hoan_Hao`.

Working directory: H:\My Drive\Ho so ca nhan\b. ThS KHMT\Skill\Web Super
Integrity mode: development

## Requirements

### R1. Cải Tổ Thẻ "Quy Trình Liên Kết" (Pipeline 7 Bước)
- **Bước 1 (Xác định phạm vi & PICO):** Dùng AI Gemini bóc tách ngữ nghĩa PICO và từ khóa học thuật đa ngữ (không chia cắt từ vật lý thô thiển). Tích hợp thống kê tần suất và xu hướng nghiên cứu từ EuropePMC / OpenAlex / ArXiv.
- **Nạp tài liệu đa định dạng:** Hỗ trợ nạp và đính kèm tài liệu từ file `.md`, `.docx`, hoặc tài liệu sẵn có trong Workspace vào kho dữ liệu thực chứng của quy trình.
- **Kích hoạt luồng liên thông:** Đảm bảo toàn bộ 7 bước vận hành thông suốt, kết xuất dữ liệu thực tế và cho phép chuyển tiếp liền mạch giữa các bước.

### R2. Nâng Cấp Thẻ "Viết Học Thuật 2-File" (Academic Writer Thực Thụ)
- **Viết bài bằng AI thực thụ:** Loại bỏ tư duy điền vào chỗ trống (mad-libs template); gọi AI LLM chắp bút từng phần dựa trên tài liệu thực chứng trong Evidence Vault / NotebookLM / file tải lên.
- **Tự động chèn mã trích dẫn Zotero:** Tự động chèn mã trường XML Zotero CSL (`w:fldSimple`) và in-text citations trực tiếp vào cây DOM của file Word (.docx).
- **Xuất bản tệp Zotero Bibliography:** Sinh thêm tệp danh mục tài liệu tham khảo chính xác (`.ris` / `.bib` / Zotero format) 100% DOI thật để người dùng nạp 1-click vào thư viện Zotero.

### R3. Nâng Cấp Thẻ "Khử Dấu Vết AI" (AI Humanizer Chuyên Sâu)
- Thay thế cơ chế regex thay từ máy móc bằng LLM AI chuyên biệt để tái cấu trúc câu văn, điều chỉnh nhịp điệu (Burstiness & Perplexity) và văn phong học thuật tự nhiên người thật.
- Bảo toàn 100% định dạng Word In-Place DOM (Heading, bảng biểu, ảnh 300 DPI, mã trường Zotero).

### R4. Rà Soát Toàn Bộ Giao Diện UI/UX & Ghi Nhận "Xác Nhận Hoàn Hảo"
- Kiểm tra từng nút bấm trên giao diện `static/index.html` và các file JavaScript: loại bỏ hoặc sửa toàn bộ các nút không có tác dụng hoặc không phản hồi.
- Ghi nhận và đóng gói các module chạy tốt (Thu thập dữ liệu Harvester, Chuyển đổi Zotero Word) vào thư mục `Xac_Nhan_Hoan_Hao`.

## Acceptance Criteria

### Giao Diện & Pipeline 7 Bước
- [ ] 100% nút bấm trên giao diện phản hồi chính xác, không có nút chết hoặc lỗi console.
- [ ] Bước 1 Pipeline sinh từ khóa chính xác bằng AI, hiển thị xu hướng từ EuropePMC/OpenAlex, và cho phép nạp tài liệu từ file `.md` / `.docx`.
- [ ] Chạy trọn vẹn 7 bước Pipeline xuất bản đầy đủ tệp kết quả.

### Academic Writer & Zotero Export
- [ ] Tệp A bài báo được AI viết sâu sắc theo đúng đề tài, có dẫn chứng thực tế và mã trích dẫn Zotero XML.
- [ ] Tệp B chứa Bảng Ma trận Đối soát 6 Cột và xuất kèm tệp `.ris` / `.bib` nạp trực tiếp vào Zotero không có DOI giả.

### AI Humanizer
- [ ] Khử dấu vết AI bằng LLM tạo văn phong tự nhiên, đạt Human Score >= 90% và bảo toàn nguyên vẹn cây XML Word .docx.

### Lưu Trữ Hoàn Hảo
- [ ] Đóng gói và lưu trữ snapshot của các module đạt chuẩn vào `Xac_Nhan_Hoan_Hao/`.
