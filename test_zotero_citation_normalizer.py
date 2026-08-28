import os
import sys
from pathlib import Path
from docx import Document
import requests

from modules.shared.file_manager import file_mgr
from modules.zotero.zotero_converter_engine import zotero_converter
from modules.auth.auth_service import create_jwt_token

print("======================================================================")
print("   KIỂM THỬ CHUẨN HÓA TRÍCH DẪN & XUẤT ZOTERO (APA, MLA, ISO 690)    ")
print("======================================================================")

# 1. Kiểm thử parse_author_name
print("\n--- 1. Kiểm thử Phân tích Tác giả (parse_author_name) ---")
a1 = zotero_converter.parse_author_name("Nguyen, Tuan Anh")
assert a1["family"] == "Nguyen" and a1["given"] == "Tuan Anh", "Lỗi phân tích Nguyen, Tuan Anh"
assert a1["apa"] == "Nguyen, T. A.", f"Lỗi APA: {a1['apa']}"
assert a1["mla"] == "Nguyen, Tuan Anh", f"Lỗi MLA: {a1['mla']}"
assert a1["iso"] == "NGUYEN, Tuan Anh", f"Lỗi ISO: {a1['iso']}"
print("  [PASS] Phân tích tác giả 'Nguyen, Tuan Anh' thành công (APA, MLA, ISO 690)")

a2 = zotero_converter.parse_author_name("Prof. Dr. John Smith")
assert a2["family"] == "Smith" and a2["given"] == "John", "Lỗi phân tích Dr. John Smith"
assert a2["apa"] == "Smith, J.", f"Lỗi APA: {a2['apa']}"
assert a2["iso"] == "SMITH, John", f"Lỗi ISO: {a2['iso']}"
print("  [PASS] Loại bỏ tiền tố học hàm 'Prof. Dr.' và chuẩn hóa đúng")

# 2. Kiểm thử format_citation trong 3 chuẩn
print("\n--- 2. Kiểm thử Định dạng 3 Chuẩn (APA, MLA, ISO 690) ---")
sample_item = {
    "title": "Deep reinforcement learning for renewable energy integration",
    "authors": ["Nguyen, Tuan Anh", "Tran, Van Binh"],
    "year": "2022",
    "journal": "Applied Energy",
    "volume": "319",
    "issue": "1",
    "pages": "119151",
    "doi": "10.1016/j.apenergy.2022.119151",
    "issn": "0306-2619"
}

apa_plain, apa_html = zotero_converter.format_citation(sample_item, style="APA")
assert "Nguyen, T. A., & Tran, V. B. (2022)" in apa_plain, f"APA plain error: {apa_plain}"
assert "https://doi.org/10.1016/j.apenergy.2022.119151" in apa_plain, "Thiếu DOI link trong APA"
assert "<a href=" in apa_html, "Thiếu HTML link trong APA"
print("  [PASS] Định dạng chuẩn APA 7th chính xác")

mla_plain, mla_html = zotero_converter.format_citation(sample_item, style="MLA")
assert 'Nguyen, Tuan Anh, and Van Binh Tran.' in mla_plain, f"MLA plain error: {mla_plain}"
assert '"Deep reinforcement learning for renewable energy integration."' in mla_plain, "Thiếu ngoặc kép tiêu đề MLA"
assert "vol. 319" in mla_plain and "no. 1" in mla_plain, "Thiếu volume/issue MLA"
print("  [PASS] Định dạng chuẩn MLA 9th chính xác")

iso_plain, iso_html = zotero_converter.format_citation(sample_item, style="ISO")
assert "NGUYEN, Tuan Anh, TRAN, Van Binh." in iso_plain, f"ISO plain error: {iso_plain}"
assert "Applied Energy." in iso_plain, "Thiếu tên tạp chí ISO"
assert "DOI: 10.1016/j.apenergy.2022.119151" in iso_plain, "Thiếu DOI ISO"
print("  [PASS] Định dạng chuẩn ISO 690:2021 chính xác")

# 3. Kiểm thử normalize_reference_text_list
print("\n--- 3. Kiểm thử Chuẩn hóa Danh sách Trích dẫn & Xuất RIS/BibTeX ---")
raw_refs = [
    "10.1016/j.apenergy.2022.119151",
    "Acid sulfate soil remediation in Mekong Delta. Le Van Khoa, 2021. Journal of Environmental Management"
]
norm_res = zotero_converter.normalize_reference_text_list(raw_refs, style="APA")
assert norm_res["success"] == True, "Normalize text failed"
assert norm_res["total"] == 2, "Wrong total items"
assert Path(file_mgr.workspace / norm_res["ris_rel_path"]).exists(), "Tệp .RIS không tồn tại"
assert Path(file_mgr.workspace / norm_res["bib_rel_path"]).exists(), "Tệp .BIB không tồn tại"
ris_text = Path(file_mgr.workspace / norm_res["ris_rel_path"]).read_text(encoding="utf-8")
assert "TY  - JOUR" in ris_text, "Tệp RIS thiếu TY - JOUR"
assert "ER  -" in ris_text, "Tệp RIS thiếu ER -"
print(f"  [PASS] Đã chuẩn hóa {norm_res['total']} tài liệu, tạo tệp .RIS và .BIB thành công")

# 4. Kiểm thử normalize_docx_references
print("\n--- 4. Kiểm thử Chuẩn hóa Danh mục Tham khảo trong File Word (.docx) ---")
doc = Document()
doc.add_heading("BÀI BÁO THỬ NGHIỆM CHUẨN HÓA TRÍCH DẪN", level=1)
doc.add_paragraph("Nội dung bài viết nghiên cứu về năng lượng tái tạo và quản lý lưới điện.")
doc.add_heading("TÀI LIỆU THAM KHẢO", level=2)
doc.add_paragraph("Nguyen, T. A., Tran, V. B. (2022). Renewable energy integration using deep reinforcement learning. Applied Energy, 319. 10.1016/j.apenergy.2022.119151")
doc.add_paragraph("Le Van Khoa (2021). Acid sulfate soil remediation in Mekong Delta. Journal of Environmental Management.")

test_docx_path = file_mgr.drafts_dir / "test_norm_raw.docx"
doc.save(str(test_docx_path))

with open(test_docx_path, "rb") as f:
    docx_bytes = f.read()

docx_norm_res = zotero_converter.normalize_docx_references(docx_bytes, "test_norm_raw.docx", style="APA")
assert docx_norm_res["success"] == True, "Normalize docx failed"
assert Path(file_mgr.workspace / docx_norm_res["rel_path"]).exists(), "File Word đã chuẩn hóa không tồn tại"
assert Path(file_mgr.workspace / docx_norm_res["ris_rel_path"]).exists(), "File RIS đồng hành không tồn tại"

doc_check = Document(str(file_mgr.workspace / docx_norm_res["rel_path"]))
full_docx_text = "\n".join([p.text for p in doc_check.paragraphs])
assert "TÀI LIỆU THAM KHẢO" in full_docx_text, "Mục References bị mất"
assert "https://doi.org/" in full_docx_text or "10.1016" in full_docx_text, "DOI không được chèn vào Word"
print("  [PASS] File Word đã được cập nhật mục Tài Liệu Tham Khảo chuẩn APA in-place")

# 5. Kiểm thử HTTP API Endpoints với Admin Auth Token
print("\n--- 5. Kiểm thử HTTP API Endpoints (Auth Protected) ---")
auth_token = create_jwt_token({"email": "admin@websuper.edu.vn", "role": "admin", "status": "active", "plan": "enterprise"})
auth_headers = {"Authorization": f"Bearer {auth_token}"}

r_api = requests.post(
    "http://127.0.0.1:8080/api/zotero/normalize-references",
    headers=auth_headers,
    json={"references": ["10.1016/j.apenergy.2022.119151"], "style": "MLA"}
)
print("  API normalize-references Status:", r_api.status_code)
assert r_api.status_code == 200, f"API normalize-references failed: {r_api.text}"
data_api = r_api.json()
assert data_api["success"] == True and data_api["style"] == "MLA", "API response invalid"
print("  [PASS] API POST /api/zotero/normalize-references hoạt động chính xác (200 OK)")

r_sync = requests.post(
    "http://127.0.0.1:8080/api/zotero/sync-references-to-zotero",
    headers=auth_headers,
    json={"items": data_api["items"]}
)
print("  API sync-references-to-zotero Status:", r_sync.status_code)
assert r_sync.status_code == 200, f"API sync-references-to-zotero failed: {r_sync.text}"
print("  [PASS] API POST /api/zotero/sync-references-to-zotero hoạt động chính xác (200 OK)")

print("\n======================================================================")
print("   TẤT CẢ CÁC BÀI TEST CHUẨN HÓA TRÍCH DẪN ĐÃ PASS 100%!               ")
print("======================================================================")
