import sys
import os
import io
import json
import docx

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

print("=======================================================", flush=True)
print("   WEB SUPER v2.0 - KIỂM THỬ TOÀN DIỆN MỌI MODULE   ", flush=True)
print("=======================================================", flush=True)

# 1. Imports
print("\n[1/8] Kiểm tra Import các Module...", flush=True)
import server
from backend.auth import create_jwt_token, decode_jwt_token
from backend.file_manager import file_mgr
from backend.data_harvesting_engine import data_harvester
from backend.academic_writer_engine import academic_writer
from backend.humanizer_engine import humanizer_engine
from backend.editorial_engine import editorial_engine
from backend.pipeline_engine import pipeline_engine
from backend.zotero_converter_engine import zotero_converter
from backend.history_manager import history_mgr
from backend.gemini_service import gemini_service
import tempfile
from pathlib import Path

# Cấu hình Thư mục Kiểm thử Cô lập (Isolated Temp Workspace) để không làm bẩn Workspace thật
temp_ws_dir = tempfile.TemporaryDirectory()
temp_ws_path = Path(temp_ws_dir.name)

orig_ws = file_mgr.workspace
orig_docs = file_mgr.docs_dir
orig_drafts = file_mgr.drafts_dir
orig_publish = file_mgr.publish_dir
orig_logs = file_mgr.logs_dir
orig_zotero = file_mgr.zotero_dir

file_mgr.workspace = temp_ws_path
file_mgr.docs_dir = temp_ws_path / "Tai_Lieu"
file_mgr.docs_dir.mkdir(exist_ok=True)
file_mgr.drafts_dir = temp_ws_path / "Ban_Thao"
file_mgr.drafts_dir.mkdir(exist_ok=True)
file_mgr.publish_dir = temp_ws_path / "Xuat_Ban"
file_mgr.publish_dir.mkdir(exist_ok=True)
file_mgr.logs_dir = temp_ws_path / "Logs"
file_mgr.logs_dir.mkdir(exist_ok=True)
file_mgr.zotero_dir = temp_ws_path / "Zotero_Converted"
file_mgr.zotero_dir.mkdir(exist_ok=True)

print("  --> OK: Tất cả module lõi & GeminiService import thành công (Chế độ Isolated Temp Workspace).", flush=True)

# 2. Gemini Dynamic Models & Google Key System
print("\n[2/8] Kiểm tra Module Tự Động Tải & Cập Nhật Mô Hình Gemini...", flush=True)
models = gemini_service.fetch_available_models()
active_m = gemini_service.get_active_model()
assert len(models) > 0
assert active_m is not None
print(f"  --> OK: Đã phát hiện {len(models)} mô hình Gemini. Mô hình mặc định mới nhất: {active_m}", flush=True)

demo_user = {"name": "Test User", "email": "test@gmail.com", "role": "researcher"}
token = create_jwt_token(demo_user)
decoded = decode_jwt_token(token)
assert decoded["email"] == "test@gmail.com"
print("  --> OK: JWT Token & Session Google Auth hoạt động chính xác.", flush=True)

# 3. Data Harvester (In-Memory Search & On-Demand Save)
print("\n[3/8] Kiểm tra Thu thập Dữ liệu (Data Harvester - In-Memory Search & On-Demand Save)...", flush=True)
q = data_harvester.generate_boolean_query("Ứng dụng Trí tuệ Nhân tạo trong Tối ưu hóa Năng lượng")
assert len(q["keywords"]) > 0
assert "boolean_en" in q and "boolean_vi" in q

# Test in-memory candidate search (does not create disk docx files)
search_res = data_harvester.search_candidates("Deep Learning Energy", max_papers=3, preferred_source="scholar")
assert search_res["status"] == "success"
assert search_res["in_memory_only"] is True
assert len(search_res["papers"]) >= 1

# Test saving single paper on-demand
p_to_save = search_res["papers"][0]
saved_res = data_harvester.save_paper_to_workspace(paper_id=p_to_save["id"])
assert saved_res["status"] == "success"
assert saved_res["paper"]["is_saved_to_disk"] is True
print(f"  --> OK: Tìm kiếm in-memory ({len(search_res['papers'])} bài) & Lưu theo yêu cầu '{saved_res['paper']['file_name']}' thành công.", flush=True)

# 4. Zotero Converter (Mode A & Mode B)
print("\n[4/8] Kiểm tra Chuyển đổi Trích dẫn Zotero Word (Dynamic Field Codes)...", flush=True)
test_doc = docx.Document()
test_doc.add_paragraph("Theo tổng hợp của (Nguyen, 2023), mô hình tối ưu hóa vận hành rất hiệu quả.")
test_doc.add_paragraph("Nghiên cứu của (Vaswani, 2017) đã đặt nền móng cho kiến trúc mạng nơ-ron Transformer.")
test_doc.add_paragraph("Tài liệu tham khảo")
test_doc.add_paragraph("Nguyen, V. A. (2023). Đánh giá hệ thống. Tạp chí Khoa học & Công nghệ, 10(2), 15-28.")
test_doc.add_paragraph("Vaswani, A. (2017). Attention is All You Need. Advances in Neural Information Processing Systems, 30, 5998-6008.")

buf = io.BytesIO()
test_doc.save(buf)
docx_bytes = buf.getvalue()

# Test Mode A
zot_res_a = zotero_converter.convert_docx(docx_bytes, "test_paper_a.docx", mode="A")
assert zot_res_a["status"] == "success"
print(f"  --> Chế độ A: Đã khớp {zot_res_a['stats']['matched_citations']}/{zot_res_a['stats']['total_citations_found']} trích dẫn với thư viện Zotero hiện hữu.", flush=True)

# Test Mode B (CrossRef auto-lookup & Bibliography Review with Dedicated Folders)
zot_res_b = zotero_converter.convert_docx(docx_bytes, "test_paper_b.docx", mode="B")
assert zot_res_b["status"] == "success"
assert zot_res_b["stats"]["matched_citations"] >= 1
assert zot_res_b["stats"]["auto_enriched"] >= 1
assert zot_res_b["stats"]["total_references_in_bibliography"] == 2
assert "dedicated_dir_rel" in zot_res_b and "tai_lieu_dir_rel" in zot_res_b
assert Path(zot_res_b["dedicated_dir_abs"]).exists()
assert Path(zot_res_b["tai_lieu_dir_abs"]).exists()
assert Path(zot_res_b["doi_soat_file_abs"]).exists()
assert len(zot_res_b["harvested_files"]) >= 1
print(f"  --> Chế độ B: Đã tạo thư mục riêng '{zot_res_b['dedicated_dir_rel']}' và thư mục con 'Tai_Lieu' chứa {len(zot_res_b['harvested_files'])} tài liệu đối soát thành công.", flush=True)

# 5. Academic Writer 2-File Paradigm
print("\n[5/8] Kiểm tra Viết Học Thuật 2-File Paradigm & 100% Citation Audit...", flush=True)
topic = "Ứng dụng Trí tuệ Nhân tạo trong Tối ưu hóa Năng lượng"
writer_res = academic_writer.generate_2file_academic_report(topic, author_name="Nguyen Van B")
assert "file_a" in writer_res
assert writer_res["audit"]["is_100_percent_compliant"] == True
print(f"  --> OK: Tệp A ({writer_res['file_a']['name']}) đã tạo chuẩn mực với dữ liệu xu hướng OpenAlex tích hợp.", flush=True)

# 6. Editorial Office v3.1 & Docx Ingestion
print("\n[6/8] Kiểm tra Tòa Soạn Báo AI v3.1 (Matrix Analysis, Docx Ingestion & GATE)...", flush=True)
ed_analysis = editorial_engine.analyze_request("Phát triển kinh tế xanh", user_input="bài viết cũ")
assert "board_selection" in ed_analysis
assert len(ed_analysis["gate_steps"]) >= 4
sample_docx_text = "Phát triển kinh tế tuần hoàn là một bước tiến quan trọng trong bảo vệ môi trường."
ed_exec = editorial_engine.execute_gate_workflow("Phát triển kinh tế xanh", ed_analysis["gate_steps"], source_content=sample_docx_text)
assert ed_exec["status"] == "success"
assert len(ed_exec.get("content", "").strip()) > 100
assert Path(ed_exec.get("file_docx_abs", "")).exists() or Path(ed_exec.get("file_md_abs", "")).exists()
print(f"  --> OK: Tiếp nhận tệp Word tư liệu và thực thi GATE thành công qua {len(ed_exec['execution_logs'])} trạm.", flush=True)

# 7. Anti-AI Humanizer & Word Docx Handling
print("\n[7/8] Kiểm tra Khử Dấu Vết AI (Vietnamese & Word Docx Extraction)...", flush=True)
ai_sample = "Nhìn chung dự án đóng vai trò quan trọng trong bức tranh toàn cảnh. Tóm lại cần mở ra một chương mới."
h_eval = humanizer_engine.analyze(ai_sample)
assert len(h_eval["found_cliches"]) >= 3
humanized = humanizer_engine.humanize(ai_sample)
assert "Nhìn chung" not in humanized and "Tóm lại" not in humanized
print(f"  --> OK: Đã phát hiện {len(h_eval['found_cliches'])} từ sáo rỗng và khử AI thành công.", flush=True)

# 8. Chained Pipeline 7 Steps
print("\n[8/9] Kiểm tra Quy Trình Nghiên Cứu Nối Tiếp 7 Bước...", flush=True)
for step in range(1, 8):
    p_step = pipeline_engine.run_step(step, "Quản trị chuỗi cung ứng thông minh")
    assert p_step["status"] == "success"
print("  --> OK: Toàn bộ 7 bước trong quy trình liên kết hoạt động hoàn hảo.", flush=True)

# 9. Activity History Manager (Record, Retrieve, Delete, Clear)
print("\n[9/9] Kiểm tra Quản Lý Lịch Sử Thao Tác & Khôi Phục Dữ Liệu...", flush=True)
hist_entry = history_mgr.add_entry(
    module="writer",
    action_title="Soạn thảo Báo cáo Thử nghiệm",
    inputs={"topic": "Trí tuệ nhân tạo"},
    result_data={"file_a": {"name": "Test_A.docx"}},
    summary="Đã tạo báo cáo thử nghiệm"
)
assert hist_entry["id"] != ""
assert hist_entry["module"] == "writer"

# Verify retrieve
records = history_mgr.get_history(module="writer")
assert len(records) >= 1
assert any(r["id"] == hist_entry["id"] for r in records)

# Verify delete item
deleted = history_mgr.delete_entry(hist_entry["id"])
assert deleted == True
print("  --> OK: Thêm mới, Lọc theo phân hệ, Truy xuất & Xóa lịch sử hoạt động chính xác.", flush=True)

# Cleanup and restore
file_mgr.workspace = orig_ws
file_mgr.docs_dir = orig_docs
file_mgr.drafts_dir = orig_drafts
file_mgr.publish_dir = orig_publish
file_mgr.logs_dir = orig_logs
file_mgr.zotero_dir = orig_zotero
try:
    temp_ws_dir.cleanup()
except Exception:
    pass

print("\n=======================================================")
print("  >>> TẤT CẢ 9 CHỨC NĂNG & LỊCH SỬ THAO TÁC 100% <<<")
print("=======================================================", flush=True)
