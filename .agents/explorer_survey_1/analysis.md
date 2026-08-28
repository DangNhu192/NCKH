# 📊 BÁO CÁO KHẢO SÁT & THIẾT KẾ KIẾN TRÚC TOÀN DIỆN: CẢI TỔ QUY TRÌNH 7 BƯỚC (R1 PIPELINE & PICO REFORM)

**Người thực hiện:** Explorer 1 (Lead Pipeline & PICO Architecture Explorer)  
**Mã nhiệm vụ:** R1 — Comprehensive Reform of 7-Step Pipeline ("Quy Trình Liên Kết")  
**Không gian làm việc:** `Web Super/`  
**Ngày hoàn thành khảo sát:** 2026-08-27  

---

## 🎯 1. TỔNG QUAN YÊU CẦU & BỐI CẢNH DỰ ÁN

Theo đặc tả `ORIGINAL_REQUEST.md`, `PROJECT.md` và `docs_chuc_nang_va_chinh_sua/01_QUY_TRINH_7_BUOC_PIPELINE.md`, mục tiêu cốt lõi của R1 là tiến hành **cải tổ toàn diện thẻ "Quy Trình Liên Kết" (7-Step IMRaD & GATE Chained Pipeline)** nhằm đảm bảo:

1. **Bước 1 (Scope & PICO Reform):**
   - Ứng dụng Gemini AI bóc tách ngữ nghĩa PICO chuyên sâu (Population/Problem, Intervention/Technology, Context/Setting, Outcome/Impact) kết hợp câu hỏi nghiên cứu định hướng (Core Research Question & Sub-questions).
   - Chuẩn hóa bộ từ khóa học thuật đa ngữ (English, Vietnamese, Russian, French, German, Chinese) không chia cắt từ ngữ vật lý thô thiển.
   - **Tích hợp thống kê tần suất & xu hướng công bố khoa học thực tế từ EuropePMC / OpenAlex / ArXiv** (số lượng bài theo năm, tốc độ tăng trưởng CAGR, biểu đồ xu hướng, cơ cấu chuyên ngành).
2. **Nạp tài liệu đa định dạng vào Kho Dữ Liệu Thực Chứng (Evidence Vault):**
   - Hỗ trợ người dùng đính kèm hoặc tải lên trực tiếp tài liệu từ các định dạng `.docx`, `.md`, `.pdf`, `.txt`.
   - Cho phép nạp và liên kết các tệp sẵn có trong không gian làm việc Workspace (`Tai_Lieu/`, `Tri_Thuc/`, `Ban_Thao/`) vào Evidence Vault.
   - Khóa dữ liệu 100% Zero Fabrication, tự động bóc tách trích dẫn nguyên văn (Verbatim Sections), đối soát DOI và danh mục tác giả.
3. **Kích hoạt luồng liên thông tuần tự 7 bước (End-to-End 7-Step Execution):**
   - Thống nhất triệt để giữa Backend (`modules/pipeline/pipeline_engine.py`) và Frontend (`static/index.html` #pipeline-tab, `static/js/pipeline.js`).
   - Xóa bỏ tình trạng phân rã bước (trước đây Frontend hiển thị 6 bước lệch pha với 7 bước Backend).
   - Đảm bảo toàn bộ 7 bước (PICO ➔ Evidence Vault ➔ Knowledge Base & Matrix ➔ Structure & BigQuery AI/ML ➔ 2-File Drafting ➔ Dynamic Zotero XML ➔ Turnitin Humanizer & Publishing) vận hành mượt mà, chuyển giao artifact khép kín.

---

## 🔍 2. KHẢO SÁT HIỆN TRẠNG & PHÂN TÍCH KHE HỞ (GAP ANALYSIS)

Qua rà soát chuyên sâu từng dòng mã nguồn, chúng tôi ghi nhận hiện trạng và các điểm khiếm khuyết sau:

### 2.1. Khe hở tại Bước 1 (Scope & PICO + Trends)
- **Tập tin liên quan:** `modules/pipeline/pipeline_engine.py` (dòng 90-142), `modules/harvester/data_harvesting_engine.py` (dòng 126-354), `static/js/pipeline.js` (dòng 409-580).
- **Hiện trạng:**
  - `data_harvester.generate_boolean_query(topic, api_key)` đã có logic gọi Gemini AI trích xuất PICO và dịch sang 6 thứ tiếng.
  - Tuy nhiên, **hoàn toàn chưa có cơ chế truy vấn dữ liệu thống kê tần suất & xu hướng công bố thực tế (Publication Trends & Frequency)** từ các API mở OpenAlex, EuropePMC và ArXiv.
  - Người dùng chỉ thấy khung PICO và các thẻ từ khóa, thiếu biểu đồ xu hướng công bố theo dòng thời gian (2018 - 2025) để thẩm định độ "hot" và mật độ nghiên cứu của đề tài trước khi thu thập tài liệu.

### 2.2. Khe hở trong việc nạp tài liệu đa định dạng vào Evidence Vault
- **Tập tin liên quan:** `modules/pipeline/pipeline_engine.py` (dòng 145-202), `modules/pipeline/pipeline_router.py` (dòng 1-56), `modules/shared/file_manager.py`.
- **Hiện trạng:**
  - Bước 2 (`evidence_vault`) trong backend chỉ tự động lấy từ danh sách bài báo tải về qua Harvester (`data_harvester.save_all_papers` / `harvest_papers`).
  - Chưa có endpoint hoặc hàm chuyên dụng cho phép:
    - Nạp trực tiếp tệp `.md` hoặc `.docx` từ máy người dùng vào Evidence Vault.
    - Duyệt và chọn các tài liệu có sẵn trong thư mục Workspace (`Tai_Lieu/`, `Tri_Thuc/`, `Ban_Thao/`) để gắn vào phiên làm việc hiện tại của Pipeline.
  - Thiếu panel quản lý Evidence Vault trực quan trên giao diện để người dùng kiểm tra danh sách bài báo đã khóa bằng chứng, kiểm toán DOI và đoạn trích dẫn.

### 2.3. Bất đồng bộ nghiêm trọng về cấu trúc 6 bước vs. 7 bước giữa Frontend và Backend
- **Tập tin liên quan:** `static/index.html` (dòng 346, 354, 377-553), `static/js/pipeline.js` (dòng 1-14, dòng 294: `backendStepMap = { 1: 1, 2: 3, 3: 4, 4: 5, 5: 6, 6: 7 }`).
- **Hiện trạng:**
  - `modules/pipeline/pipeline_engine.py` định nghĩa **7 Bước**:
    - Bước 1: Scope & PICO
    - Bước 2: Evidence Harvest & Evidence Vault Lock
    - Bước 3: Knowledge Base & Literature Matrix (Open-Notebook)
    - Bước 4: Structure Lock & BigQuery AI/ML (300 DPI Charts)
    - Bước 5: 2-File Drafting (File A IMRaD + File B 6-Col Matrix)
    - Bước 6: Dynamic Zotero CSL XML Embedding
    - Bước 7: Turnitin AI Humanizer & Publishing
  - Trong khi đó, `static/index.html` lại viết tiêu đề "Quy Trình Nghiên Cứu 6 Bước", tạo 6 Stepper Nodes và 6 Card!
  - Trong `static/js/pipeline.js`, lập trình viên cũ đã gộp gượng ép Bước 1 (PICO) và Bước 2 (Thu thập bài báo) vào 1 Card giao diện, sau đó dùng `backendStepMap` để nhảy cóc Bước 2 của backend.
  - Hậu quả:
    - Nút "Chạy Toàn Bộ Tự Động (1-Click)" gọi `/api/pipeline/run-full` sinh ra 7 kết quả (`step_1`..`step_7`), nhưng frontend chỉ render 6 bước, gây lỗi hiển thị hoặc mất kết nối trạng thái.
    - Không thể quản lý riêng biệt trạm kiểm duyệt GATE 1 (PICO & Trends) và GATE 2 (Evidence Vault Lock).

---

## 🏗️ 3. THIẾT KẾ KIẾN TRÚC MỚI CHO QUY TRÌNH 7 BƯỚC (CHUẨN HÓA ĐỒNG BỘ 1:1)

### 3.1. Ma trận 7 Bước Tuyến Tính (End-to-End Pipeline Matrix)

| Bước | Mã Định Danh | Tên Bước & Trạm Kiểm Duyệt GATE | Đầu Vào (Input) | Xử Lý & Công Nghệ Cốt Lõi | Đầu Ra (Output Artifacts) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | `scope_pico_trends` | **Bước 1: Xác Định Phạm Vi & PICO Lock (Scope & Research Trends)**<br>`⛔ GATE 1` | Đề tài nghiên cứu từ người dùng | • Gemini AI bóc tách PICO & 4 Câu hỏi nghiên cứu.<br>• Sinh 6 bộ từ khóa đa ngữ (en, vi, ru, fr, de, zh).<br>• Gọi API OpenAlex (`group_by=publication_year`) & EuropePMC (`PUB_YEAR`) trích xuất tần suất & xu hướng tăng trưởng (2018-2025). | • Khung PICO & Tóm tắt định hướng.<br>• Thẻ từ khóa đa tầng & Chuỗi Boolean Query.<br>• Thống kê tần suất công bố (Publication Frequencies & CAGR). |
| **2** | `evidence_vault` | **Bước 2: Thu Thập & Khóa Kho Dữ Liệu Thực Chứng (Evidence Vault Lock)**<br>`⛔ GATE 2` | • Chuỗi Boolean từ Bước 1<br>• Tệp nạp lên (.docx, .md, .pdf)<br>• Tệp từ Workspace | • Quét 5 kho y văn (EuropePMC, arXiv, OpenAlex, CrossRef, Scholar).<br>• Ingestion Engine bóc tách toàn văn/tóm tắt từ .docx, .md, .pdf.<br>• Khóa Evidence Vault 100% Zero Fabrication (DOI, Tác giả, Năm, Verbatim). | • Danh sách bài báo đã khóa vào Vault.<br>• Tệp `.docx` & `.md` lưu tại `Tai_Lieu/`.<br>• Trạng thái kiểm toán trích dẫn thực chứng. |
| **3** | `knowledge_sync` | **Bước 3: Đồng Bộ Kho Tri Thức & Ma Trận Y Văn (Open-Notebook Matrix)**<br>`⛔ GATE 3` | Evidence Vault từ Bước 2 | • Đồng bộ vào Open-Notebook (`nb_default`).<br>• Bóc tách đoạn văn IMRaD SciBot.<br>• Sinh Ma trận Tổng thuật Y văn 7 cột (Literature Matrix). | • Báo cáo tổng hợp tri thức (`Tri_Thuc/`).<br>• Ma trận Y văn đa chiều kèm số trang trích dẫn. |
| **4** | `structure_bigquery` | **Bước 4: Khóa Cấu Trúc IMRaD & Phân Tích Định Lượng (BigQuery AI/ML Analytics)**<br>`⛔ GATE 4` | Đề tài + Loại bài báo + Chuỗi số liệu | • Thiết lập khung cấu trúc IMRaD phân tầng.<br>• Chạy mô hình BigQuery `AI.FORECAST` (ARIMA_PLUS), Dị biệt Z-score/IQR, Key Drivers.<br>• Xuất biểu đồ phân giải cao 300 DPI (`matplotlib/seaborn`). | • Dàn ý phân tầng cho phép chỉnh sửa trực tiếp.<br>• Kết quả dự báo định lượng + URL đồ thị 300 DPI (`Ban_Thao/chart_*.png`). |
| **5** | `academic_drafting` | **Bước 5: Soạn Thảo Bộ Đôi 2-File Học Thuật (Drafting 2-Files)**<br>`⛔ GATE 5` | • Cấu trúc Bước 4<br>• Dữ liệu Evidence Vault Bước 2<br>• Đồ thị 300 DPI Bước 4 | • Senior Academic AI Scientist chắp bút bài báo.<br>• Chèn số liệu thực chứng, bảng số liệu dạng lưới và đồ thị 300 DPI.<br>• Sinh Tệp A (Bài báo IMRaD) & Tệp B (Ma trận Đối soát 6 Cột). | • **Tệp A:** `Ban_Thao/Bao_cao_...docx` & `.md`<br>• **Tệp B:** `Ban_Thao/File_B_Danh_Muc_...docx` |
| **6** | `zotero_conversion` | **Bước 6: Nhúng Mã Trường Động Zotero (Dynamic CSL XML Codes)**<br>`⛔ GATE 6` | Tệp A Word (.docx) từ Bước 5 | • Quét các trích dẫn in-text `(Author, Year)`.<br>• Tra cứu DOI/Crossref và nhúng mã trường XML Zotero (`w:fldSimple` / `w:instrText`).<br>• Tự động tạo mục Bibliography sẵn sàng 1-Click Refresh trên Word. | • Tệp Word đã nhúng mã Zotero (`Zotero_Converted/...docx`). |
| **7** | `humanize_publishing` | **Bước 7: Khử Dấu Vết AI Turnitin & Xuất Bản Trọn Gói (Final QA & Publishing)**<br>`⛔ GATE 7` | Tệp A & B sau khi nhúng Zotero | • Tái cấu trúc câu học thuật tự nhiên (Human Score >= 90%, AI Detection < 10%).<br>• Tối ưu độ biến thiên nhịp điệu câu (Burstiness).<br>• Đóng gói xuất bản trọn gói Bộ 2-File Word & Markdown vào `Xuat_Ban/`. | • `Xuat_Ban/Bao_Cao_Hoan_Tat_...docx`<br>• `Xuat_Ban/Bao_Cao_Hoan_Tat_...md`<br>• Phiếu kiểm toán chất lượng GATE QA (100/100). |

---

## 🛠️ 4. ĐẶC TẢ KỸ THUẬT & THUẬT TOÁN CHI TIẾT CHO R1

### 4.1. Thuật toán Thống kê Tần suất & Xu hướng Nghiên cứu (Research Trends Engine)

Tạo hàm mới `data_harvester.fetch_research_trends(topic: str, query: str = "") -> dict`:
- **Nguồn 1: OpenAlex API Works Group By Year**
  - Endpoint: `https://api.openalex.org/works?search={urllib.parse.quote(query_en)}&group_by=publication_year`
  - Trả về danh sách `{key: "2024", count: 2450}, {key: "2023", count: 1890}...`
- **Nguồn 2: EuropePMC API Year Counts**
  - Endpoint: `https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=OPEN_ACCESS:Y%20AND%20({urllib.parse.quote(query_en)})%20AND%20(PUB_YEAR:{year})&format=json&pageSize=0`
  - Đếm `hitCount` cho từng năm từ 2019 đến 2025.
- **Nguồn 3: arXiv Preprints Frequency**
  - Endpoint: `http://export.arxiv.org/api/query?search_query=all:{urllib.parse.quote(query_en)}&start=0&max_results=50`
  - Gom nhóm theo năm xuất bản của các preprints.
- **Xử lý số liệu & Chỉ số Tăng trưởng (CAGR & Momentum):**
  - Tính tổng số bài báo theo từng năm: $Total(t) = OpenAlex(t) + EuropePMC(t) + arXiv(t)$.
  - Tốc độ tăng trưởng hàng năm kép: $CAGR = \left(\frac{Total_{2024}}{Total_{2019}}\right)^{\frac{1}{5}} - 1$.
  - Đánh giá xu hướng:
    - $CAGR > 20\%$: "Bùng nổ nghiên cứu (Explosive Growth / High Momentum)"
    - $10\% \le CAGR \le 20\%$: "Tăng trưởng ổn định (Steady Growth)"
    - $0\% \le CAGR < 10\%$: "Giai đoạn bão hòa / Trưởng thành (Mature Domain)"

#### Schema Dữ liệu Đầu ra của `research_trends`:
```json
{
  "status": "success",
  "topic": "Ứng dụng Trí tuệ Nhân tạo trong Chẩn đoán Ung thư Phổi",
  "query_used": "(\"Artificial Intelligence\" OR \"Deep Learning\") AND (\"Lung Cancer\" OR \"Pulmonary Nodules\")",
  "yearly_frequencies": [
    {"year": "2019", "openalex": 520, "europepmc": 240, "arxiv": 110, "total": 870},
    {"year": "2020", "openalex": 780, "europepmc": 390, "arxiv": 180, "total": 1350},
    {"year": "2021", "openalex": 1120, "europepmc": 560, "arxiv": 260, "total": 1940},
    {"year": "2022", "openalex": 1640, "europepmc": 820, "arxiv": 390, "total": 2850},
    {"year": "2023", "openalex": 2310, "europepmc": 1150, "arxiv": 540, "total": 4000},
    {"year": "2024", "openalex": 3120, "europepmc": 1540, "arxiv": 720, "total": 5380},
    {"year": "2025", "openalex": 3890, "europepmc": 1910, "arxiv": 890, "total": 6690}
  ],
  "growth_metrics": {
    "cagr_percent": 33.7,
    "total_indexed_papers": 23080,
    "momentum": "Bùng nổ nghiên cứu mạnh mẽ (High Momentum)",
    "peak_year": "2025"
  },
  "top_subfields": ["Deep Learning", "Convolutional Neural Networks", "Computer-Aided Diagnosis (CAD)", "Thoracic Oncology", "Computed Tomography"],
  "data_sources": ["OpenAlex Knowledge Graph", "EuropePMC Open Access", "arXiv Preprints"]
}
```

---

### 4.2. Thiết Kế Module Nạp Tài Liệu Đa Định Dạng (Multi-Format Document Ingestion Engine)

Tích hợp trực tiếp vào `modules/pipeline/pipeline_engine.py` và `modules/pipeline/pipeline_router.py`:

1. **Endpoint `POST /api/pipeline/vault/upload-document`:**
   - Tiếp nhận tệp tải lên (`UploadFile`): `.docx`, `.doc`, `.md`, `.pdf`, `.txt`.
   - Sử dụng `python-docx` đọc văn bản & bảng biểu cho `.docx`.
   - Sử dụng `pdfplumber` / `pypdf` trích xuất văn bản có cấu trúc cho `.pdf`.
   - Đọc UTF-8 cho `.md` và `.txt`.
   - Trích xuất tự động Metadata:
     - Tên tác giả (Author cleaning theo APA 7th).
     - Năm xuất bản (Regex nhận diện năm 4 chữ số trong văn bản/tiêu đề).
     - Mã định danh DOI (Regex `10.\d{4,9}/[-._;()/:A-Za-z0-9]+`).
     - Tóm tắt hoặc đoạn văn mở đầu (Verbatim text excerpt).
   - Lưu trữ bản sao vào `Tai_Lieu/` và đăng ký vào danh sách `evidence_vault`.

2. **Endpoint `POST /api/pipeline/vault/import-workspace-files`:**
   - Tiếp nhận danh sách đường dẫn tương đối trong Workspace: `{"rel_paths": ["Tai_Lieu/paper1.docx", "Tri_Thuc/summary.md"]}`.
   - Đọc nội dung tệp qua `file_mgr.read_file(rel_path)`.
   - Trích xuất metadata và khóa vào `evidence_vault`.

3. **Endpoint `GET /api/pipeline/vault/list` & `DELETE /api/pipeline/vault/item/{item_id}`:**
   - Quản lý trạng thái danh mục tài liệu thực chứng trong phiên làm việc.

---

### 4.3. Thiết Kế Lại Giao Diện UI & Luồng Trạng Thái (Frontend Reform in `static/index.html` & `static/js/pipeline.js`)

1. **Sửa Đổi `#pipeline-tab` trong `static/index.html`:**
   - Cập nhật tiêu đề: `⚡ Quy Trình Nghiên Cứu & Biên Soạn Liên Kết Toàn Diện (7 Bước IMRaD & GATE)`.
   - Nút chạy 1-Click: `⚡ Chạy Toàn Bộ 7 Bước Tự Động (1-Click)`.
   - Stepper Navigation gồm đúng **7 Bước**:
     1. `Mục Tiêu (PICO) & Xu Hướng` (Icon 🎯)
     2. `Kho Dữ Liệu Thực Chứng (Evidence Vault)` (Icon 🌐)
     3. `Đồng Bộ Tri Thức & Ma Trận Y Văn` (Icon 🧠)
     4. `Cấu Trúc & Phân Tích Định Lượng BigQuery` (Icon 📊)
     5. `Soạn Thảo Bộ Đôi 2-File Học Thuật` (Icon 🎓)
     6. `Nhúng Mã Trường Động Zotero` (Icon 📚)
     7. `Khử Dấu Vết AI & Xuất Bản Trọn Gói` (Icon ✨)
   - Thiết lập đúng 7 Card tương ứng: `data-step="1"` đến `data-step="7"`.

2. **Tái Cấu Trúc `static/js/pipeline.js`:**
   - Định nghĩa `stepPercentages`:
     ```javascript
     stepPercentages: {
       1: 14,
       2: 28,
       3: 42,
       4: 57,
       5: 71,
       6: 85,
       7: 100
     }
     ```
   - Xóa bỏ `backendStepMap` lệch lạc; thực hiện ánh xạ trực tiếp `1:1`:
     `const backendStepNo = stepNo; // 1 -> 1, 2 -> 2, ..., 7 -> 7`.
   - Xây dựng `renderStepResult(stepNo, data)` độc lập cho từng bước 1 đến 7:
     - **Bước 1 UI:** Hiển thị PICO Form (cho phép sửa & lưu), Thẻ Từ khóa đa ngữ Anh/Việt/Quốc tế, Khung chuỗi Boolean Query và **Biểu Đồ & Thống Kê Xu Hướng Nghiên Cứu (OpenAlex / EuropePMC / ArXiv Trends Bar)**.
     - **Bước 2 UI:** Hiển thị Bảng Điều Khiển Evidence Vault: Nút tải bài báo từ Harvester, Nút nạp tệp `.docx` / `.md` / `.pdf`, Nút chọn từ Workspace, Bảng kiểm toán danh mục bài báo đã khóa (Zero Fabrication Audit Badge).
     - **Bước 3 UI:** Hiển thị Bảng Ma trận Y văn 7 cột (Literature Matrix), danh mục tài liệu đã nạp, liên kết xem báo cáo tri thức.
     - **Bước 4 UI:** Hiển thị Khung Dàn ý IMRaD (cho phép chỉnh sửa trực tiếp), Panel phân tích BigQuery AI.FORECAST và ảnh đồ thị 300 DPI xem trước sắc nét.
     - **Bước 5 UI:** Hiển thị nút mở / tải Bộ đôi 2-File: Tệp A (Báo cáo IMRaD) & Tệp B (Ma trận Đối soát 6 Cột).
     - **Bước 6 UI:** Hiển thị trạng thái chuyển đổi mã trường XML Zotero (`w:fldSimple`), nút mở và tải file Word CSL.
     - **Bước 7 UI:** Hiển thị Phiếu chấm điểm GATE QA Rubric (100/100), Điểm tự nhiên ngôn ngữ (>90%), Điểm Burstiness, và Khung tải trọn gói xuất bản `Xuat_Ban/`.

---

## 🗺️ 5. LỘ TRÌNH THỰC THI CHO CÁC WORKER TIẾP THEO (IMPLEMENTATION ROADMAP)

Để hiện thực hóa trọn vẹn R1 mà không làm gián đoạn các tính năng khác, các Worker tiếp theo nên thực thi theo 4 giai đoạn sau:

```
┌──────────────────────────────────────────────────────────────────────────┐
│ GIAI ĐOẠN 1: NÂNG CẤP BACKEND HARVESTER & RESEARCH TRENDS ENGINE         │
│ • Bổ sung data_harvester.fetch_research_trends() (OpenAlex/EuropePMC)    │
│ • Thêm endpoint POST /api/harvest/research-trends                        │
│ • Tích hợp Gemini PICO prompt chuẩn sâu và trả về Research Trends        │
└────────────────────────────────────┬─────────────────────────────────────┘
                                     │
                                     ▼
┌──────────────────────────────────────────────────────────────────────────┐
│ GIAI ĐOẠN 2: NÂNG CẤP EVIDENCE VAULT & MULTI-FORMAT INGESTION            │
│ • Viết hàm ingest_document_to_vault() (.docx, .md, .pdf) trong engine    │
│ • Viết hàm import_workspace_files_to_vault()                             │
│ • Bổ sung các endpoint /api/pipeline/vault/* trong pipeline_router.py    │
└────────────────────────────────────┬─────────────────────────────────────┘
                                     │
                                     ▼
┌──────────────────────────────────────────────────────────────────────────┐
│ GIAI ĐOẠN 3: ĐỒNG BỘ 7 BƯỚC TUYẾN TÍNH TRONG PIPELINE ENGINE             │
│ • Chuẩn hóa step_no 1 đến 7 trong pipeline_engine.py & pipeline_router.py│
│ • Hoàn thiện luồng artifact chuyển giao giữa Step 1 -> 2 -> ... -> 7     │
└────────────────────────────────────┬─────────────────────────────────────┘
                                     │
                                     ▼
┌──────────────────────────────────────────────────────────────────────────┐
│ GIAI ĐOẠN 4: NÂNG CẤP TOÀN BỘ GIAO DIỆN FRONTEND (HTML & JS)             │
│ • Cập nhật static/index.html (#pipeline-tab): 7 Bước & 7 Cards           │
│ • Cập nhật static/js/pipeline.js: 7 Steps 1:1, UI Trends, Vault Manager  │
│ • Chạy bộ test tự động E2E xác nhận 100% PASS                            │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 🏁 6. KẾT LUẬN KHẢO SÁT

Kiến trúc hiện tại của WEB SUPER đã có nền tảng rất mạnh về Harvester, Zotero Converter, BigQuery AI/ML và Open-Notebook. Việc thực hiện cải tổ R1 sẽ giải quyết triệt để sự lệch pha giữa giao diện và backend, trang bị tính năng phân tích xu hướng nghiên cứu toàn cầu (OpenAlex / EuropePMC / ArXiv), và mở rộng khả năng nạp tài liệu thực chứng đa định dạng (.docx, .md, workspace) đạt chuẩn 100% Zero Fabrication.
