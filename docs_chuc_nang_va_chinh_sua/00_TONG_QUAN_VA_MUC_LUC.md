# 📚 HỆ THỐNG QUẢN LÝ YÊU CẦU CHỈNH SỬA & ĐẶC TẢ TỪNG CHỨC NĂNG WEB SUPER
> **Mục đích:** Chống sự lãng quên các yêu cầu, duy trì tính nhất quán xuyên suốt quá trình phát triển, nâng cấp và vận hành hệ thống Web Super v3.2 / v2.0 hợp nhất nghiên cứu khoa học chuẩn quốc tế ISI/Scopus/Scimago, Tòa soạn báo AI 6 Ban GATE, và Kho tri thức học thuật Open-Notebook RAG.

---

## 📌 NGUYÊN TẮC BẮT BUỘC KHI PHÁT TRIỂN / CHỈNH SỬA CODE
1. **Đọc trước khi sửa:** Bất kỳ lập trình viên hoặc AI Agent nào trước khi can thiệp vào mã nguồn của một chức năng **BẮT BUỘC PHẢI ĐỌC FILE `.MD` TƯƠNG ỨNG** trong thư mục này.
2. **Tuân thủ quy tắc bất biến:** Không được phép làm mất hoặc suy giảm các tính năng, ràng buộc đạo đức khoa học và cơ chế bảo toàn đã được thiết lập (4 Trụ cột Bất biến: Zero Fabrication, In-Place DOM Word, Chuẩn hóa số thập phân tiếng Việt, Chuẩn hóa Toán - Hóa học OMML).
3. **Cập nhật sau khi sửa:** Sau mỗi lần chỉnh sửa mã nguồn thành công, **BẮT BUỘC PHẢI CẬP NHẬT LẠI FILE `.MD` TƯƠNG ỨNG** với các mục:
   - *Yêu cầu chỉnh sửa mới nhất từ Người dùng.*
   - *Chi tiết các thay đổi kỹ thuật (Files, hàm, thuật toán, REST endpoints).*
   - *Kết quả kiểm thử thực tế và trạng thái hiện tại (100% PASS).*

---

## 🗂️ MỤC LỤC DANH MỤC FILE THEO TỪNG CHỨC NĂNG (15 TỆP ĐẶC TẢ ĐỒNG BỘ 4 LỚP)

| STT | Tên Tệp Tài Liệu | Chức Năng Tương Ứng & Kiến Trúc Tích Hợp | File Mã Nguồn Trọng Tâm |
| :---: | :--- | :--- | :--- |
| **00** | [`00_CAU_TRUC_VA_GIAO_DIEN_WEB_SUPER.md`](./00_CAU_TRUC_VA_GIAO_DIEN_WEB_SUPER.md) | **Cấu Trúc Hệ Thống & Thiết Kế Giao Diện UI/UX 12 Tab** | `server.py`, `static/index.html`, `static/js/`, `static/css/` |
| **00b**| [`00_QUY_TAC_BAT_BIEN_VA_DAO_DUC_NGHIEN_CUU.md`](./00_QUY_TAC_BAT_BIEN_VA_DAO_DUC_NGHIEN_CUU.md) | **Khung Đạo Đức & 4 Quy Chuẩn Bất Biến & Tư Duy Phản Biện** | `modules/shared/skill_prompts.py`, `docx_styler.py` |
| **00c**| [`00_MA_TRAN_QUY_TRINH_LIEN_KET_LIEN_THONG.md`](./00_MA_TRAN_QUY_TRINH_LIEN_KET_LIEN_THONG.md) | **Ma Trận Quy Trình Nghiên Cứu Liên Kết Liên Thông 7 Chặng** | `modules/pipeline/`, `modules/shared/` |
| **01** | [`01_QUY_TRINH_7_BUOC_PIPELINE.md`](./01_QUY_TRINH_7_BUOC_PIPELINE.md) | **Quy Trình Nghiên Cứu 7 Bước IMRaD & RhinoInsight Deep-Research** | `modules/pipeline/pipeline_engine.py`, `pipeline_router.py` |
| **02** | [`02_THU_THAP_TAI_LIEU_HARVESTER.md`](./02_THU_THAP_TAI_LIEU_HARVESTER.md) | **Thu Thập Đa Nguồn, PMC XML, Ảnh 300 DPI & SciBot Ingestion** | `modules/harvester/data_harvesting_engine.py`, `harvester_router.py` |
| **03** | [`03_KHO_TRI_THUC_NOTEBOOKLM.md`](./03_KHO_TRI_THUC_NOTEBOOKLM.md) | **Kho Tri Thức Học Thuật, SciBot Okapi BM25 & Grounded RAG** | `modules/notebooklm/notebooklm_engine.py`, `notebooklm_router.py` |
| **04** | [`04_CHUYEN_DOI_MA_TRICH_DAN_ZOTERO.md`](./04_CHUYEN_DOI_MA_TRICH_DAN_ZOTERO.md) | **Chuyển Đổi Zotero CSL Sang Word Docx (In-Place DOM)** | `modules/zotero/zotero_converter_engine.py`, `zotero_router.py` |
| **05** | [`05_VIET_HOC_THUAT_2_FILE.md`](./05_VIET_HOC_THUAT_2_FILE.md) | **Viết Học Thuật 2-File (RhinoInsight Phase 1 Tree & Phase 2 Deep)** | `modules/academic_writer/academic_writer_engine.py`, `writer_router.py` |
| **06** | [`06_TOA_SOAN_BAO_AI_EDITORIAL_GATE.md`](./06_TOA_SOAN_BAO_AI_EDITORIAL_GATE.md) | **Tòa Soạn Báo AI 6 Ban, Q1 ISI Rubric & Adversarial Peer-Review** | `modules/editorial_office/editorial_engine.py`, `editorial_router.py` |
| **07** | [`07_KHU_AI_VA_CHONG_DAO_VAN_TURNITIN.md`](./07_KHU_AI_VA_CHONG_DAO_VAN_TURNITIN.md) | **Khử Dấu Vết AI & Chống Đạo Văn Turnitin 1-Click Master** | `modules/humanizer/humanizer_engine.py`, `humanizer_router.py` |
| **08** | [`08_CHUAN_HOA_TOAN_HOA_HOC_MATH_CHEM_PRO.md`](./08_CHUAN_HOA_TOAN_HOA_HOC_MATH_CHEM_PRO.md) | **Chuẩn Hóa 109 Ký Hiệu Hóa Học, OMML Math & Đồ Họa 300 DPI** | `modules/shared/docx_styler.py`, `docx_formula_engine.py` |
| **09** | [`09_QUAN_LY_TAI_KHOAN_VA_AUTH_VAULT.md`](./09_QUAN_LY_TAI_KHOAN_VA_AUTH_VAULT.md) | **Bảo Mật Auth Vault (AES-256/PBKDF2) & Phân Quyền Admin** | `modules/auth/`, `auth_vault/` |
| **10** | [`10_WORKSPACE_VA_LICH_SU_HISTORY.md`](./10_WORKSPACE_VA_LICH_SU_HISTORY.md) | **Không Gian Workspace, Soạn Thảo In-Place DOM & Lịch Sử Phiên** | `modules/workspace/docx_editor_engine.py`, `modules/history/` |
| **11** | [`11_PHAN_TICH_DU_LIEU_BIGQUERY_AI_ML.md`](./11_PHAN_TICH_DU_LIEU_BIGQUERY_AI_ML.md) | **Phân Tích Dữ Liệu Lớn BigQuery AI/ML & PDF Document AI OCR** | `modules/bigquery/bigquery_engine.py`, `modules/shared/pdf_ocr_engine.py` |
| **12** | [`12_DOI_SOAT_SONG_SONG_DUAL_PANE_INSPECTOR.md`](./12_DOI_SOAT_SONG_SONG_DUAL_PANE_INSPECTOR.md) | **Đối Soát Song Song Dual-Pane v4.2 & Cổng Kiểm Duyệt 4 Tầng** | `modules/inspector/`, `static/js/inspector.js` |

---

## 🧪 BỘ CÔNG CỤ TỰ ĐỘNG HÓA KIỂM ĐỊNH (CROSS-VALIDATION PROTOCOL)
Để đảm bảo tính toàn vẹn 100% không bị phân rã theo thời gian:
1. **Kiểm tra chéo tài liệu đặc tả 4 lớp:**
   ```powershell
   uv run python docs_chuc_nang_va_chinh_sua/tools_cross_validate_docs.py
   ```
2. **Bộ kiểm thử tự động toàn diện (Master E2E & Stress Test Suites):**
   - `test_worker_m1_verification.py` (M1 Academic Integrity & Zero-Fabrication - 34 tests PASS)
   - `.agents/worker_m1/test_rhinoinsight_m1.py` (M1 RhinoInsight 2-Phase Outline & Deep-Investigation - 28 tests PASS)
   - `test_open_notebook_full_flow.py` (M2 SciBot Scientific Sectioning & Okapi BM25 - 14 tests PASS)
   - `test_pdf_ocr_full_flow.py` (PDF Document AI OCR Engine - 11 tests PASS)
   - `test_docx_editor_engine.py` (Word DOM Preservation & In-Place Replacement - 10 tests PASS)
   - `test_m2_docx_math_chem.py` (Word In-Place DOM & Math/Chem Engine - 5 tests PASS)
   - `test_adversarial_m2_stress.py` (Adversarial DOM & Decimal Extreme Stress Tests - 87 tests PASS)
   - `test_server_load.py` (Server Endpoints & Concurrent Load - 8 tests PASS)
   - `tests/test_looped_flows_engine.py` (Looped Flows Reasoning & Verification - 10 tests PASS)
   - `tests/test_data_autocleaning.py` (Data Autocleaning, Profiling & Outlier Sanitation - 6 tests PASS)
   - `tests/test_reactome_service.py` (Reactome Database Bio-Pathways & Reaction Service - 5 tests PASS)
   - `tests/test_evidence_inspector_gate.py` (Dual-Pane Evidence Inspector & 4-Layer Gate - 9 tests PASS)
