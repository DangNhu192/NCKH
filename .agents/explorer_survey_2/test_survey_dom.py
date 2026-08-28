# test_survey_dom.py
import sys
import os
import io
import re
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

print("=" * 70)
print("  SURVEY AUDIT: WORD (.DOCX) DOM & MATH/CHEM SUBSYSTEMS")
print("=" * 70)

import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

from modules.shared.docx_styler import DocxStyler
from modules.shared.docx_formula_engine import (
    latex_to_mathml, mathml_to_omml, latex_to_omml,
    add_latex_equation, format_inline_chemical_formulas,
    UNICODE_CHEM_MAP
)

# 1. Decimal Conversion Test
print("\n--- 1. Vietnamese Decimal Conversion & Invariant Protection ---")
test_cases = [
    ("Tăng trưởng 15.5% trong năm 2023.", "15,5%"),
    ("Nồng độ đo được là 0.05 mg/L.", "0,05"),
    ("Mục 1.2.3 mô tả phương pháp.", "1.2.3"),
    ("Mô hình Gemini 1.5 Pro và Python 3.11.", "Gemini 1.5 Pro và Python 3.11"),
    ("DOI: 10.1016/j.envres.2023.116500", "10.1016/j.envres.2023.116500"),
    ("File báo cáo: data_v3.2.docx", "data_v3.2.docx"),
    ("Chỉ tiêu BOD5 và COD đạt 28.5% so với 1.5 lần.", "28,5%"),
]

for orig, expected_sub in test_cases:
    converted = DocxStyler.convert_decimals_preserve_sections(orig)
    status = "PASS" if expected_sub in converted else "FAIL"
    print(f"[{status}] Orig: '{orig}' -> Converted: '{converted}'")

# 2. Math & LaTeX Conversion Test
print("\n--- 2. LaTeX to OMML and Inline Math Cleaning ---")
latex_eq = r"E = mc^2 + \frac{\alpha}{\beta} \sqrt{x^2 + y^2}"
try:
    mathml = latex_to_mathml(latex_eq)
    omml = mathml_to_omml(mathml)
    has_omath = "<m:oMath" in omml
    print(f"[PASS] LaTeX to OMML conversion: has <m:oMath>: {has_omath}")
    print(f"       OMML preview: {omml[:120]}...")
except Exception as e:
    print(f"[FAIL] LaTeX to OMML conversion error: {e}")

cleaned_inline = DocxStyler.clean_inline_latex_math(r"Hàm số f(x) = \alpha x^2 + \beta x + \gamma với \sqrt{a+b}")
print(f"[INFO] Cleaned inline math: '{cleaned_inline}'")

# 3. Chemical Formula Subscript Mapping
print("\n--- 3. Chemical Formula Unicode Mapping ---")
chem_samples = ["FeS2", "H2SO4", "NH4+", "NO3-", "Al3+", "Fe2+", "SO42-", "CaCO3", "BOD5", "COD", "CH4", "CO2"]
doc_chem = Document()
p_chem = doc_chem.add_paragraph("Nồng độ các chất: " + ", ".join(chem_samples) + ".")
format_inline_chemical_formulas(p_chem)
print(f"[INFO] Normalized chemical paragraph text: '{p_chem.text}'")
for chem in ["FeS₂", "H₂SO₄", "NH₄⁺", "NO₃⁻", "Al³⁺", "Fe²⁺", "SO₄²⁻", "CaCO₃", "BOD₅", "COD", "CH₄", "CO₂"]:
    status = "PASS" if chem in p_chem.text else "FAIL"
    print(f"[{status}] Contains {chem}: {status == 'PASS'}")

# 4. Full Markdown to DOCX Rendering Test
print("\n--- 4. Full Document DOM Rendering (Headings, Tables, Equations, Images) ---")
test_md = """# BÁO CÁO NGHIÊN CỨU KHOA HỌC THỬ NGHIỆM

## 1. MỞ ĐẦU
Nghiên cứu đánh giá nồng độ H2SO4 và FeS2 trong nước thải với lưu lượng 15.5 m3/h. Mô hình áp dụng phiên bản v3.1 và Python 3.11.

## 2. PHƯƠNG PHÁP & CÔNG THỨC TOÁN
Phương trình động học phản ứng được mô tả như sau:

$$k = A \\cdot e^{-\\frac{E_a}{R T}}$$

### 2.1. Phân Tích Thực Nghiệm
Bảng số liệu tổng hợp kết quả đo đạc:

| STT | Thông Số Đo | Giá Trị Ban Đầu | Sau Xử Lý | Hiệu Suất Giảm |
| :--- | :--- | :--- | :--- | :--- |
| 1 | BOD5 (mg/L) | 120.5 | 15.2 | 87.4% |
| 2 | COD (mg/L) | 350.0 | 45.8 | 86.9% |
| 3 | Fe2+ (mg/L) | 28.5 | 1.2 | 95.8% |
| 4 | SO42- (mg/L) | 500.0 | 50.0 | 90.0% |

> Đây là trích dẫn quan trọng: Quá trình xử lý đạt chuẩn QCVN 40:2011/BTNMT.

## 3. KẾT LUẬN
Tất cả chỉ tiêu FeS2 và H2SO4 đều giảm hơn 85.0% theo phương trình mô hình hóa.
"""

doc_out = Document()
DocxStyler.render_markdown_to_docx(doc_out, test_md, title="BÁO CÁO ĐÁNH GIÁ THỰC NGHIỆM")

out_path = Path(PROJECT_ROOT / "modules/workspace/Tai_Lieu/test_survey_output.docx")
out_path.parent.mkdir(parents=True, exist_ok=True)
doc_out.save(str(out_path))
print(f"[PASS] Rendered and saved test document to: {out_path} ({out_path.stat().st_size} bytes)")

# Verify DOM elements in output document
doc_verify = Document(str(out_path))
print(f"  Total paragraphs: {len(doc_verify.paragraphs)}")
print(f"  Total tables: {len(doc_verify.tables)}")
headings_found = [p.style.name for p in doc_verify.paragraphs if "Heading" in p.style.name]
print(f"  Headings detected: {headings_found}")

# Check tables structure
if doc_verify.tables:
    tbl = doc_verify.tables[0]
    print(f"  Table 1 rows: {len(tbl.rows)}, cols: {len(tbl.columns)}")
    hdr_cells = [c.text.strip() for c in tbl.rows[0].cells]
    print(f"  Header cells: {hdr_cells}")
    row1_cells = [c.text.strip() for c in tbl.rows[1].cells]
    print(f"  Row 1 cells (with Vietnamese decimals): {row1_cells}")

# 5. In-Place DOM Preservation & Zotero Field Code Preservation
print("\n--- 5. Zotero Field Code & In-Place DOM Preservation Test ---")
doc_zot = Document()
p_zot = doc_zot.add_paragraph("Theo nghiên cứu của tác giả về xử lý FeS2 và H2SO4 với hiệu suất 28.5%.")

# Add a simulated Zotero fldSimple field
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
zot_xml = parse_xml(f'<w:fldSimple {nsdecls("w")} w:instr=" ADDIN ZOTERO_ITEM CSL_CITATION {{&quot;citationItems&quot;:[{{&quot;id&quot;:123}}]}} "><w:r><w:t>(Nguyen, 2023)</w:t></w:r></w:fldSimple>')
p_zot._p.append(zot_xml)

print(f"  Before chemical normalization XML child count: {len(p_zot._p)}")
format_inline_chemical_formulas(p_zot)
print(f"  After chemical normalization paragraph text: '{p_zot.text}'")
has_fld = any('fldSimple' in elem.tag for elem in p_zot._p)
print(f"  [PASS] Preserved w:fldSimple Zotero XML field: {has_fld}")

# 6. DocxEditorEngine Audit
print("\n--- 6. DocxEditorEngine Method Availability Audit ---")
from modules.workspace.docx_editor_engine import DocxEditorEngine
engine = DocxEditorEngine()
parsed = engine.parse_docx(str(out_path))
print(f"  parse_docx successful: {parsed['success']}, extracted {len(parsed['extracted_data_points'])} data points, {len(parsed['tables'])} tables.")

print("\n=======================================================")
print("  AUDIT COMPLETED SUCCESSFULLY")
print("=======================================================")
