# test_worker_m1_verification.py
"""
Comprehensive Unit & Integration Test Suite for worker_m1:
1. Academic Integrity & Zero Fabrication in Academic Writer
2. Decimal Conversion vs DOI Regex in Humanizer
3. Run Formatting Preservation in Zotero CSL XML Docx Converter & Zotero Engine
4. 6-Column Matrix Verification in SKILL.md
"""

import sys
import os
import re
import io
import docx
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

print("======================================================================")
print("   WORKER_M1 VERIFICATION TEST SUITE (ACADEMIC INTEGRITY & DOCX DOM)   ")
print("======================================================================")

passed = 0
total = 0

def test(name, condition, details=""):
    global passed, total
    total += 1
    if condition:
        passed += 1
        print(f"  [PASS] {name}")
    else:
        print(f"  [FAIL] {name} - Details: {details}")
        assert False, f"Test failed: {name} - {details}"

# ── TEST 1: Academic Writer Fallback Zero Fabrication ──────────────────────────
print("\n--- 1. Kiểm thử Tính Liêm chính Học thuật & Zero Fabrication (Academic Writer) ---")
from modules.academic_writer.academic_writer_engine import AcademicWriterEngine, academic_writer
import tempfile
from modules.shared.file_manager import file_mgr

# Setup temporary test workspace
temp_ws = tempfile.TemporaryDirectory()
temp_p = Path(temp_ws.name)
file_mgr.workspace = temp_p
file_mgr.docs_dir = temp_p / "Tai_Lieu"
file_mgr.docs_dir.mkdir(parents=True, exist_ok=True)
file_mgr.drafts_dir = temp_p / "Ban_Thao"
file_mgr.drafts_dir.mkdir(parents=True, exist_ok=True)

# Generate report with no local documents and mock topic
res_writer = academic_writer.generate_2_files(
    topic="Tối ưu hóa Hệ thống Năng lượng Tái tạo",
    author_name="ThS. Nguyễn Văn A",
    paper_type="Báo cáo khoa học",
    target_papers=[]
)

test("Trạng thái sinh báo cáo thành công", res_writer.get("status") == "success")
test("Tệp A docx tồn tại trên đĩa", Path(res_writer["file_a"]["abs_path"]).exists())
test("Tệp A md tồn tại trên đĩa", Path(str(res_writer["file_a"]["abs_path"]).replace(".docx", ".md")).exists())

doc_a_read = docx.Document(res_writer["file_a"]["abs_path"])
text_a_all = "\n".join(p.text for p in doc_a_read.paragraphs)

test("Không chứa DOI giả 10.1016/j.artint.2022.103450", "10.1016/j.artint.2022.103450" not in text_a_all)
test("Không chứa DOI giả 10.1016/j.eswa.2023.119850", "10.1016/j.eswa.2023.119850" not in text_a_all)
test("Tệp A có nội dung học thuật hợp lệ", len(text_a_all.strip()) > 100)

# ── TEST 2: Humanizer Decimal & DOI Disambiguation ────────────────────────────
print("\n--- 2. Kiểm thử Chuẩn hóa Số Thập phân & Phân lập DOI (Humanizer Engine) ---")
from modules.humanizer.humanizer_engine import humanizer_engine

decimal_cases = [
    ("Hiệu suất đạt 10.5% trong điều kiện chuẩn.", ["10,5%"]),
    ("Nồng độ đạt 10.25 mg/L và 10.0 mg/L.", ["10,25 mg/L", "10,0 mg/L"]),
    ("Chỉ số đo đạc 10.999 kg.", ["10,999 kg"]),
    ("Độ chính xác 0.05 và 28.5%.", ["0,05", "28,5%"]),
    ("Bài báo có DOI: 10.1038/s41598-021-04362-w được trích dẫn.", ["10.1038/s41598-021-04362-w"]),
    ("Tham khảo tại https://doi.org/10.1016/j.eswa.2023.119850 trực tuyến.", ["https://doi.org/10.1016/j.eswa.2023.119850"]),
    ("Công bố theo doi: 10.1109/TPWRS.2018.2868958 gần đây.", ["doi: 10.1109/TPWRS.2018.2868958"]),
    ("Quy mô mẫu gồm 10,000 đối tượng.", ["10.000"]),
    ("Hợp chất H2SO4 phản ứng với FeS2 sinh ra SO4 2-.", ["H₂SO₄", "FeS₂", "SO₄²⁻"]),
]

for raw_in, expected_substrs in decimal_cases:
    res = humanizer_engine.format_vietnamese_decimals_and_chem(raw_in)
    for exp in expected_substrs:
        test(f"Định dạng đúng '{exp}' từ '{raw_in[:35]}...'", exp in res, f"Expected '{exp}' in '{res}'")

# ── TEST 3: DOCX Multi-Run Formatting Preservation in Zotero XML ──────────────
print("\n--- 3. Kiểm thử Bảo toàn Định dạng Multi-Run khi Nhúng Zotero XML ---")
from modules.zotero.zotero_converter_engine import zotero_converter
from docx import Document

# Test 3a: Direct paragraph processing with ZoteroConverterEngine
doc_direct = Document()
p_dir = doc_direct.add_paragraph()
r_d1 = p_dir.add_run("Đoạn mở đầu in đậm: ")
r_d1.bold = True
r_d2 = p_dir.add_run("(Vaswani, 2017)")
r_d3 = p_dir.add_run(" và đoạn kết in nghiêng.")
r_d3.italic = True

stats_mock = {"matched_citations": 0, "total_citations_found": 0, "unmatched": 0, "auto_enriched": 0, "details": []}
ref_lookup_mock = {
    "vaswani_2017": {"primary_author": "Vaswani", "year": "2017", "title": "Attention Is All You Need", "doi": "10.48550/arXiv.1706.03762"}
}
ref_items_mock = [ref_lookup_mock["vaswani_2017"]]

zotero_converter._process_single_paragraph(
    p_dir,
    ref_lookup_mock,
    mode="B",
    stats=stats_mock,
    ref_items=ref_items_mock
)

test("Paragraph chứa trường XML w:fldSimple", "<w:fldSimple" in p_dir._p.xml)
bold_found = any(r.bold is True for r in p_dir.runs)
italic_found = any(r.italic is True for r in p_dir.runs)
test("ZoteroConverterEngine bảo toàn Run in đậm (bold=True)", bold_found)
test("ZoteroConverterEngine bảo toàn Run in nghiêng (italic=True)", italic_found)

# Test 3b: Test 02_THU_THAP_PDF_VA_ZOTERO/Zotero_Citation_Converter/scripts/docx_converter.py
sys.path.insert(0, str(Path(r"H:\My Drive\Ho so ca nhan\b. ThS KHMT\Skill\02_THU_THAP_PDF_VA_ZOTERO\Zotero_Citation_Converter\scripts").resolve()))
from docx_converter import DocxZoteroConverter
from zotero_api import ZoteroManager

z_mgr_mock = ZoteroManager(local_sqlite_path=None)
conv_script = DocxZoteroConverter(zotero_mgr=z_mgr_mock, mode="B")
test_p_copy = Document()
p_copy = test_p_copy.add_paragraph()
r_b = p_copy.add_run("Đoạn in đậm: ")
r_b.bold = True
r_c = p_copy.add_run("(Nguyen, 2023)")
r_i = p_copy.add_run(" và đoạn in nghiêng.")
r_i.italic = True

ref_lookup_mock2 = {
    "nguyen_2023": {"primary_author": "Nguyen", "year": "2023", "title": "Test Title"}
}
conv_script._process_single_paragraph(p_copy, ref_lookup_mock2)
test("DocxZoteroConverter chèn trường w:fldSimple", "<w:fldSimple" in p_copy._p.xml)
test("DocxZoteroConverter bảo toàn Run in đậm", any(r.bold is True for r in p_copy.runs))
test("DocxZoteroConverter bảo toàn Run in nghiêng", any(r.italic is True for r in p_copy.runs))

# ── TEST 4: SKILL.md 6-Column Matrix Definition ───────────────────────────────
print("\n--- 4. Kiểm thử Đặc tả SKILL.md 6-Column Evidence Audit Matrix ---")
skill_01_path = Path(r"H:\My Drive\Ho so ca nhan\b. ThS KHMT\Skill\01_BO_NAO_AI_RESEARCHER\SKILL.md")
test("SKILL.md tồn tại", skill_01_path.exists())

with open(skill_01_path, "r", encoding="utf-8") as f_sk:
    skill_content = f_sk.read()

test("SKILL.md đặc tả 6 Cột chuẩn mực (6-Column Evidence Audit Matrix)", "6 Cột chức năng chuẩn mực" in skill_content)
test("SKILL.md liệt kê STT", "1. `STT`" in skill_content)
test("SKILL.md liệt kê Luận điểm", "2. `Luận điểm trong bài" in skill_content)
test("SKILL.md liệt kê Tác giả & Năm", "3. `Tác giả & Năm" in skill_content)
test("SKILL.md liệt kê Tệp Monograph Gốc", "4. `Tệp Monograph Gốc" in skill_content)
test("SKILL.md liệt kê Trích đoạn nguyên văn", "5. `Trích đoạn nguyên văn" in skill_content)
test("SKILL.md liệt kê Bản dịch tiếng Việt", "6. `Bản dịch tiếng Việt" in skill_content)

print(f"\n======================================================================")
print(f"   KẾT QUẢ KIỂM THỬ: {passed}/{total} TESTS PASS (100% THÀNH CÔNG)   ")
print(f"======================================================================")
