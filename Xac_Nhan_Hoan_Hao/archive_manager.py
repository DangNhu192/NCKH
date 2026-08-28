# H:\My Drive\Ho so ca nhan\b. ThS KHMT\Skill\Web Super\Xac_Nhan_Hoan_Hao\archive_manager.py
"""
Công cụ tự động đóng gói & lưu trữ các bản phát hành được xác nhận hoàn hảo.
"""

import os
import sys
import shutil
import json
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = Path(__file__).resolve().parent.parent
ARCHIVE_DIR = Path(__file__).resolve().parent

def save_module_snapshot(module_name: str, description: str, files_list: list = None):
    now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    target_folder = ARCHIVE_DIR / "Modules_Source_Code" / f"{module_name}_{now_str}"
    target_folder.mkdir(parents=True, exist_ok=True)

    manifest = {
        "module": module_name,
        "archived_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "description": description,
        "files": []
    }

    if files_list:
        for rel_f in files_list:
            src_f = ROOT_DIR / rel_f
            if src_f.exists():
                dst_f = target_folder / rel_f
                dst_f.parent.mkdir(parents=True, exist_ok=True)
                if src_f.is_file():
                    shutil.copy2(src_f, dst_f)
                    manifest["files"].append(str(rel_f))
                elif src_f.is_dir():
                    shutil.copytree(src_f, dst_f, dirs_exist_ok=True)
                    manifest["files"].append(str(rel_f) + " (folder)")

    with open(target_folder / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print(f"✅ Đã lưu trữ thành công module '{module_name}' vào: {target_folder}")
    return target_folder

def save_full_system_snapshot(version_tag: str, note: str):
    now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    target_folder = ARCHIVE_DIR / "Full_System_Snapshots" / f"Release_{version_tag}_{now_str}"
    target_folder.mkdir(parents=True, exist_ok=True)

    # Sao chép toàn bộ modules, static, server.py, config.json, v.v.
    items_to_copy = ["modules", "static", "server.py", "config.json", "requirements.txt", "README.md"]
    copied_items = []

    for item in items_to_copy:
        src = ROOT_DIR / item
        dst = target_folder / item
        if src.exists():
            if src.is_file():
                shutil.copy2(src, dst)
            elif src.is_dir():
                shutil.copytree(src, dst, dirs_exist_ok=True)
            copied_items.append(item)

    manifest = {
        "version_tag": version_tag,
        "archived_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "note": note,
        "copied_items": copied_items
    }

    with open(target_folder / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print(f"🎉 ĐÃ ĐÓNG GÓI TOÀN BỘ HỆ THỐNG '{version_tag}' VÀO: {target_folder}")
    return target_folder

VERIFIED_MODULES_CATALOG = {
    "Module_01_Pipeline_7Steps_Verified": {
        "description": "Quy trình nghiên cứu 7 bước IMRaD & GATE, phân tích PICO AI, xu hướng OpenAlex & EuropePMC, và khóa Evidence Vault đa định dạng.",
        "files": [
            "modules/pipeline",
            "static/js/pipeline.js",
            "docs_chuc_nang_va_chinh_sua/01_QUY_TRINH_7_BUOC_PIPELINE.md"
        ]
    },
    "Module_02_AcademicWriter_Verified": {
        "description": "Viết học thuật 2-File chuyên sâu chuẩn APA 7th (Tệp A Báo cáo & Tệp B Ma trận 6 cột), nhúng Zotero XML DOM và xuất kèm file tham khảo .ris / .bib.",
        "files": [
            "modules/academic_writer",
            "static/js/academic-writer.js",
            "docs_chuc_nang_va_chinh_sua/05_VIET_HOC_THUAT_2_FILE.md"
        ]
    },
    "Module_03_Harvester_Verified": {
        "description": "Phân hệ Thu thập tài liệu học thuật đa nguồn (CrossRef, OpenAlex, ArXiv, Scholar, EuropePMC, Wikimedia) và quản lý thư viện số.",
        "files": [
            "modules/harvester",
            "static/js/harvester.js",
            "docs_chuc_nang_va_chinh_sua/02_THU_THAP_TAI_LIEU_HARVESTER.md"
        ]
    },
    "Module_04_Zotero_Converter_Verified": {
        "description": "Phân hệ Chuyển đổi mã trích dẫn Zotero Word (.docx) In-Place DOM chuẩn APA 7th, IEEE, Vancouver, Harvard và Bảng Đối Soát 6 Cột.",
        "files": [
            "modules/zotero",
            "static/js/zotero-converter.js",
            "docs_chuc_nang_va_chinh_sua/04_CHUYEN_DOI_MA_TRICH_DAN_ZOTERO.md"
        ]
    },
    "Module_05_MathChemPro_Verified": {
        "description": "Phân hệ Chuẩn hóa Công thức Toán - Hóa Học (109 hợp chất Unicode, OMML LaTeX, Biểu đồ Matplotlib 300 DPI, Sơ đồ Mermaid) & Sửa Lỗi Đóng Gói Word Media In-Place DOM.",
        "files": [
            "modules/math_chem_pro",
            "static/js/math-chem-pro.js",
            "modules/shared/docx_formula_engine.py",
            "modules/shared/docx_styler.py",
            "modules/shared/docx_math_chem_styler.py",
            "docs_chuc_nang_va_chinh_sua/08_CHUAN_HOA_TOAN_HOA_HOC_MATH_CHEM_PRO.md"
        ]
    },
    "Module_06_BigQuery_AI_Verified": {
        "description": "Phân hệ Phân tích dữ liệu lớn & Trí tuệ nhân tạo BigQuery AI/ML (AI.FORECAST, AI.DETECT_ANOMALIES, AI.KEY_DRIVERS, NL2SQL).",
        "files": [
            "modules/bigquery",
            "static/js/bigquery-ml.js",
            "docs_chuc_nang_va_chinh_sua/11_PHAN_TICH_DU_LIEU_BIGQUERY_AI_ML.md"
        ]
    },
    "Module_07_PDF_OCR_Workspace_Verified": {
        "description": "Phân hệ Document AI PDF OCR Studio & Soạn thảo Word In-Place DOM Workspace (Abbyy Vantage, Hybrid RAG, Open-Notebook Ingestion).",
        "files": [
            "modules/workspace",
            "static/js/document-editor.js",
            "static/js/pdf-ocr-reader.js",
            "modules/shared/pdf_ocr_engine.py",
            "docs_chuc_nang_va_chinh_sua/10_WORKSPACE_VA_LICH_SU_HISTORY.md"
        ]
    },
    "Module_08_OpenNotebook_RAG_Verified": {
        "description": "Phân hệ Kho tri thức học thuật Open-Notebook RAG Vault (Okapi BM25, Multi-Scale N-Gram, Grounded Chat & Transformation Studio).",
        "files": [
            "modules/notebooklm",
            "static/js/notebooklm.js",
            "docs_chuc_nang_va_chinh_sua/03_KHO_TRI_THUC_NOTEBOOKLM.md"
        ]
    },
    "Module_09_Humanizer_Turnitin_Verified": {
        "description": "Khử dấu vết AI & Chống đạo văn Turnitin Rephrase Pro, biến thiên nhịp điệu Burstiness và triệt tiêu 100% Wikipedia Tells & ContentBeta 300+.",
        "files": [
            "modules/humanizer",
            "static/js/humanizer.js",
            "docs_chuc_nang_va_chinh_sua/07_KHU_AI_VA_CHONG_DAO_VAN_TURNITIN.md"
        ]
    }
}

def package_all_verified_modules():
    """Đóng gói toàn bộ các module đã qua xác nhận hoàn hảo vào Modules_Source_Code."""
    print("📦 BẮT ĐẦU ĐÓNG GÓI CÁC MODULE ĐÃ XÁC NHẬN HOÀN HẢO...")
    results = {}
    for mod_name, mod_info in VERIFIED_MODULES_CATALOG.items():
        folder = save_module_snapshot(
            module_name=mod_name,
            description=mod_info["description"],
            files_list=mod_info["files"]
        )
        results[mod_name] = str(folder)
    print(f"🎉 ĐÃ HOÀN TẤT ĐÓNG GÓI {len(results)} MODULES VÀO: {ARCHIVE_DIR / 'Modules_Source_Code'}")
    return results

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "full":
            tag = sys.argv[2] if len(sys.argv) > 2 else "v2.0_Golden"
            note = sys.argv[3] if len(sys.argv) > 3 else "Bản hoàn hảo được người dùng xác nhận."
            save_full_system_snapshot(tag, note)
        elif cmd in ["modules", "all_modules", "package_modules"]:
            package_all_verified_modules()
        elif cmd in VERIFIED_MODULES_CATALOG:
            mod_info = VERIFIED_MODULES_CATALOG[cmd]
            save_module_snapshot(cmd, mod_info["description"], mod_info["files"])
    else:
        package_all_verified_modules()

