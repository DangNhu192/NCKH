# 🔗 MA TRẬN QUY TRÌNH NGHIÊN CỨU LIÊN KẾT LIÊN THÔNG TOÀN DIỆN (END-TO-END INTERLINKED PIPELINE)

> **Mục tiêu:** Định nghĩa luồng dữ liệu liên tục (Data Stream) và cơ chế chuyển giao trạng thái (Context Passing) giữa toàn bộ các phân hệ của WEB SUPER v3.2 / v2.0.
> Đảm bảo không có chức năng nào hoạt động cô lập; kết quả đầu ra của phân hệ trước là đầu vào chuẩn hóa của phân hệ sau.

---

## 🗺️ SƠ ĐỒ LUỒNG DỮ LIỆU LIÊN KẾT XUYÊN SUỐT 7 CHẶNG (END-TO-END RESEARCH LIFECYCLE)

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ CHẶNG 1: XÁC ĐỊNH ĐỀ TÀI, KHUNG PICO & DÀN Ý TƯƠNG TÁC (RHINOINSIGHT PHASE 1)          │
│ [Tab 1: Pipeline & Tab 5: Writer] ➔ Sinh PICO, Câu hỏi NC, Thẻ từ khóa Anh/Việt        │
│ ➔ Sinh Cây Đề Cương Tương Tác (Outline Tree Node), Mở rộng nhánh, Chiều phân tích     │
│ ➔ Cổng phê duyệt của chuyên gia (Approval Gate) khóa cấu trúc dàn ý                    │
└──────────────────────────────────────────┬─────────────────────────────────────────────┘
                                           │ Truyền Query / Keywords / PICO / Outline Tree
                                           ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ CHẶNG 2: THU THẬP TÀI LIỆU ĐA NGUỒN, AI OCR & HÌNH ẢNH KHOA HỌC THỰC TẾ 300 DPI         │
│ [Tab 2: Harvester Pro & PDF AI OCR] ➔ Quét Scholar, EuropePMC, arXiv, OpenAlex, CrossRef│
│ ➔ Tải PDF gốc, Trích xuất PMC XML, AI OCR quang học phục hồi lớp chữ Searchable Text    │
│ ➔ Trích xuất Bảng số liệu dạng lưới, RAG Chunks [filename, Trang X], Hình ảnh 300 DPI  │
└──────────────────────────────────────────┬─────────────────────────────────────────────┘
                                           │ Lưu tài liệu, RAG Chunks & Metadata
                                           ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ CHẶNG 3: ĐỒNG BỘ THƯ VIỆN ZOTERO & KHO TRI THỨC NGỮ NGHĨA (SCIBOT OPEN-NOTEBOOK RAG)   │
│ [Tab 3: NotebookLM] ➔ ScientificSectioner IMRaD, Okapi BM25 + Multi-Scale N-Gram      │
│ ➔ Section-Aware Query Routing Boost (+30-40%), Ma trận Y văn 7 Cột, Grounded Chat      │
│ [Tab 4: Zotero CSL] ➔ Đồng bộ thư viện Zotero, mã hóa CSL Citation JSON In-Place DOM   │
└──────────────────────────────────────────┬─────────────────────────────────────────────┘
                                           │ Cung cấp Context + Ma trận Y văn + Trích dẫn
                                           ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ CHẶNG 4: ĐIỀU TRA SÂU (RHINOINSIGHT PHASE 2), BIGQUERY AI/ML & ĐIỀU PHỐI TÒA SOẠN GATE │
│ [Tab 11: BigQuery AI/ML] ➔ Dự báo chuỗi thời gian, Dị biệt IQR/Z-score, Key Drivers     │
│ [Tab 5: Academic Writer] ➔ Soạn thảo sâu từng Node, gán cờ [uncertain], sinh Bộ đôi    │
│                           2-File (File A IMRaD chuẩn + File B Ma trận Đối soát 6 Cột)   │
│ [Tab 6: Editorial Office] ➔ 6 Ban Biên Tập, 4 Trạm GATE, Q1 ISI Rubric (100đ) &        │
│                           Hội đồng Phản biện Đối kháng 2 Reviewer + Rebuttal Letter     │
└──────────────────────────────────────────┬─────────────────────────────────────────────┘
                                           │ Kết xuất file Word (.docx) bản thảo
                                           ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ CHẶNG 5: CHUẨN HÓA CÔNG THỨC TOÁN - HÓA HỌC & ĐỒ HỌA 300 DPI                           │
│ [Tab 8: Math-Chem Pro] ➔ Tự động sửa 109 chất (FeS₂, H₂SO₄, NH₄⁺...), chèn OMML Eq      │
│ ➔ Nhúng hình ảnh/sơ đồ khoa học 300 DPI căn giữa trang, gắn Caption học thuật chuẩn    │
│ ➔ Bảo toàn 100% In-Place DOM Word (.docx) và Mã trường Zotero XML (w:fldSimple)         │
└──────────────────────────────────────────┬─────────────────────────────────────────────┘
                                           │ Bản thảo đã chuẩn hóa Toán - Hóa
                                           ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ CHẶNG 6: KHỬ DẤU VẾT AI & CHỐNG ĐẠO VĂN TURNITIN (1-CLICK UNIFIED MASTER)              │
│ [Tab 7: Humanizer & Turnitin Pro]                                                      │
│ ➔ Phân tích Sentence Burstiness sóng 3 tầng, Triệt tiêu 100% Wikipedia & ContentBeta  │
│ ➔ Áp dụng 5 Kỹ thuật Turnitin Rephrase, đưa Similarity < 8% & Human Score > 95%        │
│ ➔ Bảo toàn phân cách số thập phân tiếng Việt và bảo vệ chuỗi DOI tuyệt đối              │
│ ➔ Xuất bản File Word Hoàn Thiện (.docx In-Place DOM)                                   │
└──────────────────────────────────────────┬─────────────────────────────────────────────┘
                                           │ Lưu trữ & Sao lưu bảo mật
                                           ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ CHẶNG 7: LƯU TRỮ WORKSPACE, GHI NHẬT KÝ LỊCH SỬ & BẢO MẬT AUTH VAULT                   │
│ [Tab Workspace & History] ➔ Soạn thảo In-Place DOM, Audit Log lịch sử, khôi phục phiên │
│ [Auth Vault] ➔ Mã hóa AES-256 cho toàn bộ API Keys, bảo mật danh bạ người dùng         │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 MA TRẬN ÁNH XẠ ĐẦU VÀO / ĐẦU RA (INPUT/OUTPUT CONTRACT MATRIX)

| Phân Hệ Nguồn | Dữ Liệu Đầu Ra (Output) | Phân Hệ Đích Tiếp Nhận | Mục Đích Sử Dụng |
| :--- | :--- | :--- | :--- |
| **Tab 1: Pipeline** | Chủ đề, PICO, Boolean Query, Từ khóa, Outline Tree | **Tab 2: Harvester & Tab 5: Writer** | Tìm kiếm bài báo đa nguồn & khởi tạo dàn ý RhinoInsight |
| **Tab 2: Harvester & PDF OCR** | Danh sách bài báo, Abstract, DOI, File PDF, RAG Chunks, Ảnh 300 DPI | **Tab 3: NotebookLM & Tab 4: Zotero** | Nạp vào Kho tri thức SciBot để RAG và lưu vào thư viện Zotero |
| **Tab 3 & 4: NotebookLM/Zotero** | Ma trận tổng quan y văn 7 Cột, Trích dẫn chuẩn CSL In-Place DOM | **Tab 5: Academic Writer & Tab 6: Editorial** | Cung cấp luận cứ thực chứng và định dạng trích dẫn chuẩn |
| **Tab 11: BigQuery AI/ML** | Bảng số liệu dự báo, dị biệt, Key Drivers, Biểu đồ 300 DPI | **Tab 1 (Pipeline) & Tab 5 (Writer)** | Cung cấp dữ liệu định lượng cho phần Kết Quả & Bàn Luận |
| **Tab 5: Academic Writer** | Bộ 2-File Word (File A + File B Ma trận 6 Cột & Uncertainty Flags) | **Tab 8: Math-Chem Pro & Tab 6: Editorial** | Chuẩn hóa công thức Toán (OMML)/Hóa học và thẩm định tòa soạn |
| **Tab 6: Editorial Office** | Ấn phẩm bản thảo qua 4 trạm GATE, Q1 Rubric & Rebuttal Letter | **Tab 7: Humanizer** | Kiểm định đạo văn và khử dấu vết AI |
| **Tab 8: Math-Chem Pro** | File Word (.docx) đã chuẩn hóa công thức/ảnh 300 DPI | **Tab 7: Humanizer** | Khử AI trực tiếp trong file Word qua In-Place DOM |
| **Tab 7: Humanizer Pro** | File Word (.docx) hoàn thiện cuối cùng (< 8% Similarity) | **Workspace & History** | Lưu vào kho tệp nghiên cứu và ghi nhận Audit Log |
| **Tất cả các Tab** | Lệnh gọi AI Gemini / ChatGPT | **Auth Vault (modules/auth)** | Tự động giải mã AES-256 API Key trong RAM để thực thi |

