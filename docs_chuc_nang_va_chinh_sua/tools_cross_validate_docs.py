# tools_cross_validate_docs.py
"""
Công cụ kiểm tra chéo và đối soát tính toàn vẹn giữa các file đặc tả trong docs_chuc_nang_va_chinh_sua/
với cấu trúc mã nguồn và bộ kiểm thử thực tế của dự án WEB SUPER v3.2 / v2.0.
"""

import os
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

DOCS_DIR = Path(__file__).resolve().parent
PROJECT_DIR = DOCS_DIR.parent
STATIC_DIR = PROJECT_DIR / "static"

MANDATORY_DOC_FILES = [
    "00_TONG_QUAN_VA_MUC_LUC.md",
    "00_CAU_TRUC_VA_GIAO_DIEN_WEB_SUPER.md",
    "00_MA_TRAN_QUY_TRINH_LIEN_KET_LIEN_THONG.md",
    "00_QUY_TAC_BAT_BIEN_VA_DAO_DUC_NGHIEN_CUU.md",
    "01_QUY_TRINH_7_BUOC_PIPELINE.md",
    "02_THU_THAP_TAI_LIEU_HARVESTER.md",
    "03_KHO_TRI_THUC_NOTEBOOKLM.md",
    "04_CHUYEN_DOI_MA_TRICH_DAN_ZOTERO.md",
    "05_VIET_HOC_THUAT_2_FILE.md",
    "06_TOA_SOAN_BAO_AI_EDITORIAL_GATE.md",
    "07_KHU_AI_VA_CHONG_DAO_VAN_TURNITIN.md",
    "08_CHUAN_HOA_TOAN_HOA_HOC_MATH_CHEM_PRO.md",
    "09_QUAN_LY_TAI_KHOAN_VA_AUTH_VAULT.md",
    "10_WORKSPACE_VA_LICH_SU_HISTORY.md",
    "11_PHAN_TICH_DU_LIEU_BIGQUERY_AI_ML.md",
]

MANDATORY_SECTIONS = [
    "VỊ TRÍ & ĐẶC TẢ MODULE",
    "QUY TRÌNH LIÊN KẾT LIÊN THÔNG",
    "TUÂN THỦ 4 QUY TẮC BẤT BIẾN",
    "NHẬT KÝ YÊU CẦU & KẾT QUẢ XỬ LÝ"
]

MANDATORY_TEST_FILES = [
    ("test_pdf_ocr_full_flow.py", "Bộ kiểm thử E2E PDF Document AI OCR"),
    ("test_open_notebook_full_flow.py", "Bộ kiểm thử E2E Open-Notebook RAG Vault"),
    ("test_docx_editor_engine.py", "Bộ kiểm thử E2E Word DOM Preservation & Math/Chem"),
    ("test_server_load.py", "Bộ kiểm thử E2E Server Endpoints & Concurrent Load"),
    ("test_worker_m1_verification.py", "Bộ kiểm thử M1 Academic Integrity & Zero-Fabrication"),
    ("test_m2_docx_math_chem.py", "Bộ kiểm thử M2 Word Styler & Math/Chem Engine"),
]

def check_files_existence():
    print("=" * 70)
    print("📁 BƯỚC 1: KIỂM TRA SỰ TỒN TẠI CỦA 15 FILE ĐẶC TẢ BẮT BUỘC")
    print("=" * 70)
    all_exist = True
    for fname in MANDATORY_DOC_FILES:
        fpath = DOCS_DIR / fname
        if fpath.exists():
            size = fpath.stat().st_size
            print(f"  [OK] {fname} ({size:,} bytes)")
        else:
            print(f"  [MISSING] ❌ THIẾU FILE: {fname}")
            all_exist = False
    return all_exist

def check_mandatory_sections():
    print("\n" + "=" * 70)
    print("📋 BƯỚC 2: KIỂM TRA CHÉO CÁC MỤC BẮT BUỘC TRONG TỪNG FILE CHỨC NĂNG")
    print("=" * 70)
    all_sections_ok = True
    feature_files = [f for f in MANDATORY_DOC_FILES if f.startswith(("01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11"))]
    for fname in feature_files:
        fpath = DOCS_DIR / fname
        if not fpath.exists():
            continue
        content = fpath.read_text(encoding="utf-8")
        print(f"\n📄 Kiểm tra: {fname}")
        for sec in MANDATORY_SECTIONS:
            if sec in content:
                print(f"    [OK] Đã có mục: {sec}")
            else:
                print(f"    [MISSING] ❌ THIẾU MỤC: {sec}")
                all_sections_ok = False
    return all_sections_ok

def check_codebase_mapping():
    print("\n" + "=" * 70)
    print("⚡ BƯỚC 3: KIỂM TRA TÍNH KHỚP NỐI VỚI MÃ NGUỒN THỰC TẾ (CODEBASE MAPPING)")
    print("=" * 70)
    index_html = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
    tabs_to_check = [
        ("home-tab", "Trang chủ & Hệ sinh thái"),
        ("pipeline-tab", "Tab 1: Quy trình 7 bước"),
        ("harvester-tab", "Tab 2: Thu thập tài liệu"),
        ("zotero-tab", "Tab 3: Chuyển đổi Zotero"),
        ("writer-tab", "Tab 4: Viết 2-File"),
        ("editorial-tab", "Tab 5: Tòa soạn Báo GATE"),
        ("humanizer-tab", "Tab 6: Khử AI & Turnitin"),
        ("math-chem-tab", "Tab 7: Toán - Hóa Pro"),
        ("admin-tab", "Tab 8: Quản trị viên"),
        ("workspace-tab", "Tab Workspace"),
        ("history-tab", "Tab Lịch sử"),
        ("bigquery-tab", "Tab BigQuery AI & ML"),
    ]
    all_tabs_ok = True
    for tab_id, tab_label in tabs_to_check:
        if f'id="{tab_id}"' in index_html:
            print(f"  [OK] Giao diện HTML chứa: #{tab_id} ({tab_label})")
        else:
            print(f"  [MISSING] HTML thiếu thẻ: #{tab_id} ({tab_label})")
            all_tabs_ok = False
    return all_tabs_ok

def check_backend_modules_and_endpoints():
    print("\n" + "=" * 70)
    print("🔬 BƯỚC 4: KIỂM TRA MODULE BACKEND & API ENDPOINTS (CODEBASE INTEGRITY)")
    print("=" * 70)
    all_ok = True
    modules_to_check = [
        ("modules/harvester/data_harvesting_engine.py", "Harvester Engine"),
        ("modules/harvester/harvester_router.py", "Harvester Router"),
        ("modules/zotero/zotero_converter_engine.py", "Zotero Engine"),
        ("modules/zotero/zotero_router.py", "Zotero Router"),
        ("modules/humanizer/humanizer_engine.py", "Humanizer Engine"),
        ("modules/auth/auth_service.py", "Auth Service"),
        ("modules/bigquery/bigquery_engine.py", "BigQuery Engine"),
        ("modules/bigquery/bigquery_router.py", "BigQuery Router"),
        ("modules/shared/pdf_ocr_engine.py", "PDF Document AI OCR Engine"),
        ("modules/workspace/docx_editor_engine.py", "Docx Editor Engine"),
        ("modules/notebooklm/notebooklm_engine.py", "NotebookLM / OpenNotebook Engine"),
        ("modules/shared/docx_formula_engine.py", "Docx Formula Engine"),
        ("static/js/bigquery-ml.js", "BigQuery JS"),
        ("static/js/pdf-ocr-reader.js", "PDF OCR Reader JS"),
        ("modules/auth/user_config_manager.py", "User Config Manager"),
        ("modules/history/history_manager.py", "History Manager"),
        ("modules/shared/docx_styler.py", "DocX Styler"),
        ("modules/shared/skill_prompts.py", "Skill Prompts"),
        ("auth_vault/users_registry.vault.json", "Users Registry Vault"),
        ("static/index.html", "Frontend HTML"),
        ("static/js/harvester.js", "Harvester JS"),
        ("static/js/auth.js", "Auth JS"),
    ]
    for rel_path, label in modules_to_check:
        fpath = PROJECT_DIR / rel_path
        if fpath.exists():
            print(f"  [OK] Module tồn tại: {label} ({rel_path})")
        else:
            print(f"  [MISSING] Thiếu module: {label} ({rel_path})")
            all_ok = False

    print("\n--- Kiểm tra sự hiện diện của Master Test Suites ---")
    for tfile, tdesc in MANDATORY_TEST_FILES:
        tfpath = PROJECT_DIR / tfile
        if tfpath.exists():
            print(f"  [OK] Test Suite tồn tại: {tfile} — {tdesc}")
        else:
            print(f"  [MISSING] Thiếu Test Suite: {tfile} — {tdesc}")
            all_ok = False

    print("\n--- Kiểm tra các hàm nghiệp vụ cốt lõi ---")
    h_engine = PROJECT_DIR / "modules/harvester/data_harvesting_engine.py"
    if h_engine.exists():
        h_src = h_engine.read_text(encoding="utf-8")
        funcs_h = [
            ("resolve_authentic_pdf_url", "Giải mã URL PDF đa tầng"),
            ("extract_full_text", "Bóc tách toàn văn (PMC XML / PDF / HTML)"),
            ("save_paper_to_zotero", "Lưu bài báo vào Zotero + tạo .docx"),
            ("download_pdf_to_disk", "Tải PDF về đĩa cục bộ"),
            ("audit_extraction_integrity", "Kiểm tra tính toàn vẹn bóc tách"),
            ("get_readable_content_for_ai", "Phục vụ AI đọc nội dung"),
            ("process_user_uploaded_paper_file", "Xử lý file PDF upload của người dùng"),
            ("fetch_real_references_from_crossref", "Lấy tài liệu tham khảo thực tế từ CrossRef"),
        ]
        for func_name, desc in funcs_h:
            if f"def {func_name}" in h_src:
                print(f"  [OK] Hàm tồn tại (Harvester): {func_name}() — {desc}")
            else:
                print(f"  [MISSING] Thiếu hàm (Harvester): {func_name}() — {desc}")
                all_ok = False

    bq_engine = PROJECT_DIR / "modules/bigquery/bigquery_engine.py"
    if bq_engine.exists():
        bq_src = bq_engine.read_text(encoding="utf-8")
        funcs_bq = [
            ("forecast_timeseries", "Dự báo chuỗi thời gian BigQuery AI.FORECAST"),
            ("detect_anomalies", "Kiểm định dị biệt BigQuery AI.DETECT_ANOMALIES"),
            ("analyze_key_drivers", "Phân tích động lực BigQuery AI.KEY_DRIVERS"),
            ("generate_bigquery_sql", "Sinh BigQuery SQL NL2SQL"),
            ("export_analysis_report_docx", "Xuất bản báo cáo Word .docx 300 DPI")
        ]
        for func_name, desc in funcs_bq:
            if f"def {func_name}" in bq_src:
                print(f"  [OK] Hàm tồn tại (BigQuery): {func_name}() — {desc}")
            else:
                print(f"  [MISSING] Thiếu hàm (BigQuery): {func_name}() — {desc}")
                all_ok = False

    pdf_engine = PROJECT_DIR / "modules/shared/pdf_ocr_engine.py"
    if pdf_engine.exists():
        pdf_src = pdf_engine.read_text(encoding="utf-8")
        funcs_pdf = [
            ("inspect_pdf", "Đánh giá mật độ chữ và phân loại PDF Digital vs Scan"),
            ("extract_pdf_page_image", "Trích xuất ảnh PDF 200-300 DPI đa tầng"),
            ("ocr_page_with_vision_ai", "OCR Vision AI tuân thủ 5 quy tắc bất biến"),
            ("process_pdf_document", "Xử lý PDF tạo RAG Chunks [filename, Trang X]"),
            ("export_searchable_docx", "Xuất bản Word .docx In-Place DOM 300 DPI"),
            ("ingest_to_open_notebook", "Nạp 1-click toàn văn OCR vào Open-Notebook")
        ]
        for func_name, desc in funcs_pdf:
            if f"def {func_name}" in pdf_src:
                print(f"  [OK] Hàm tồn tại (PDF OCR): {func_name}() — {desc}")
            else:
                print(f"  [MISSING] Thiếu hàm (PDF OCR): {func_name}() — {desc}")
                all_ok = False

    docx_engine = PROJECT_DIR / "modules/workspace/docx_editor_engine.py"
    if docx_engine.exists():
        docx_src = docx_engine.read_text(encoding="utf-8")
        funcs_docx = [
            ("parse_docx", "Bóc tách cấu trúc đoạn văn và bảng biểu Word"),
            ("save_edited_docx", "Lưu nội dung chỉnh sửa chuẩn In-Place DOM"),
            ("batch_replace_in_docx", "Tìm & thay thế Run-level không làm phẳng style")
        ]
        for func_name, desc in funcs_docx:
            if f"def {func_name}" in docx_src:
                print(f"  [OK] Hàm tồn tại (Docx Editor): {func_name}() — {desc}")
            else:
                print(f"  [MISSING] Thiếu hàm (Docx Editor): {func_name}() — {desc}")
                all_ok = False

    print("\n--- Kiểm tra các REST API Endpoints ---")
    h_router = PROJECT_DIR / "modules/harvester/harvester_router.py"
    if h_router.exists():
        hr_src = h_router.read_text(encoding="utf-8")
        endpoints_h = [
            ("/api/harvest/run", "Tìm kiếm & thu thập bài báo"),
            ("/api/harvest/save-to-zotero", "Lưu bài báo vào Zotero"),
            ("/api/harvest/batch-save-to-zotero", "Lưu hàng loạt vào Zotero"),
            ("/api/harvest/upload-paper-file", "Upload PDF người dùng"),
            ("/api/harvest/download-pdf", "Tải PDF gốc về máy tính"),
            ("/api/harvest/integrity-check", "Kiểm tra tính toàn vẹn bóc tách"),
            ("/api/harvest/read-for-ai", "Phục vụ AI đọc nội dung"),
        ]
        for ep, desc in endpoints_h:
            if ep in hr_src:
                print(f"  [OK] Endpoint (Harvester): {ep} — {desc}")
            else:
                print(f"  [MISSING] Thiếu endpoint (Harvester): {ep} — {desc}")
                all_ok = False

    bq_router = PROJECT_DIR / "modules/bigquery/bigquery_router.py"
    if bq_router.exists():
        bqr_src = bq_router.read_text(encoding="utf-8")
        endpoints_bq = [
            ("/forecast", "API Dự báo chuỗi thời gian (/api/bigquery/forecast)"),
            ("/detect-anomalies", "API Kiểm định dị biệt (/api/bigquery/detect-anomalies)"),
            ("/key-drivers", "API Phân tích động lực (/api/bigquery/key-drivers)"),
            ("/generate-sql", "API Sinh BigQuery SQL (/api/bigquery/generate-sql)"),
            ("/upload-dataset", "API Nạp tập dữ liệu (/api/bigquery/upload-dataset)"),
            ("/export-docx", "API Xuất bản Word .docx (/api/bigquery/export-docx)")
        ]
        for ep, desc in endpoints_bq:
            if f'"{ep}"' in bqr_src or f"'{ep}'" in bqr_src:
                print(f"  [OK] Endpoint (BigQuery): /api/bigquery{ep} — {desc}")
            else:
                print(f"  [MISSING] Thiếu endpoint (BigQuery): /api/bigquery{ep} — {desc}")
                all_ok = False

    return all_ok

def main():
    ok1 = check_files_existence()
    ok2 = check_mandatory_sections()
    ok3 = check_codebase_mapping()
    ok4 = check_backend_modules_and_endpoints()
    
    print("\n" + "=" * 70)
    if ok1 and ok2 and ok3 and ok4:
        print("🎉 TẤT CẢ 15 FILE ĐẶC TẢ TRONG docs_chuc_nang_va_chinh_sua/ ĐỒNG BỘ 100%!")
        print("✅ TOÀN BỘ MODULE BACKEND, TEST SUITES VÀ ENDPOINTS XÁC THỰC CHUẨN!")
    else:
        print("⚠️ CẦN BỔ SUNG CÁC CẤU PHẦN CHƯA HOÀN TOÀN ĐỒNG BỘ THEO DANH SÁCH TRÊN.")
    print("=" * 70)

if __name__ == "__main__":
    main()