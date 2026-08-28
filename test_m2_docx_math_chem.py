# test_m2_docx_math_chem.py
"""
Comprehensive Verification Test Suite for Milestone M2:
Word .docx DOM Preservation & Math/Chem Engine Implementation.
"""

import sys
import io
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

import docx
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from modules.shared.docx_styler import DocxStyler, replace_text_in_paragraph_runs
from modules.shared.docx_formula_engine import (
    UNICODE_CHEM_MAP, format_inline_chemical_formulas,
    latex_to_mathml, mathml_to_omml, add_latex_equation
)
from modules.workspace.docx_editor_engine import DocxEditorEngine, docx_editor


def test_vietnamese_decimal_and_thousand_formatting():
    print("\n[TEST 1] Vietnamese Decimal & Thousand Formatting")
    cases = [
        ("Tăng trưởng 15.5% trong năm 2023.", "15,5%"),
        ("Nồng độ đo được là 0.05 mg/L.", "0,05 mg/L"),
        ("Mục 1.2.3 mô tả phương pháp.", "1.2.3"),
        ("Mô hình Gemini 1.5 Pro và Python 3.11.", "Gemini 1.5 Pro và Python 3.11"),
        ("DOI: 10.1016/j.envres.2023.116500", "10.1016/j.envres.2023.116500"),
        ("File báo cáo: data_v3.2.docx", "data_v3.2.docx"),
        ("Chỉ tiêu BOD5 và COD đạt 28.5% so với 1.5 lần.", "28,5% so với 1,5 lần"),
        ("Doanh thu đạt 50,000 USD và 1,000 tấn sản phẩm.", "50.000 USD và 1.000 tấn"),
        ("Quy chuẩn QCVN 40:2011/BTNMT với giới hạn 0.01 mg/L.", "QCVN 40:2011/BTNMT với giới hạn 0,01 mg/L"),
    ]
    for raw, expected in cases:
        res = DocxStyler.convert_decimals_preserve_sections(raw)
        assert expected in res, f"Expected '{expected}' in '{res}'"
        print(f"  [PASS] '{raw}' -> '{res}'")


def test_docx_styler_class_methods():
    print("\n[TEST 2] DocxStyler Class Methods (apply_document_styles, add_heading, add_paragraph, add_styled_table)")
    doc = Document()
    DocxStyler.apply_document_styles(doc)
    
    # Check margins
    sec = doc.sections[0]
    assert abs(sec.top_margin.inches - 0.98) < 0.05
    assert abs(sec.left_margin.inches - 1.18) < 0.05
    
    h1 = DocxStyler.add_heading_1(doc, "Tiêu Đề Cấp 1")
    assert "TIÊU ĐỀ CẤP 1" in h1.text
    assert h1.style.name == "Heading 1"
    
    h2 = DocxStyler.add_heading_2(doc, "Tiêu Đề Cấp 2")
    assert "Tiêu Đề Cấp 2" in h2.text
    assert h2.style.name == "Heading 2"
    
    h3 = DocxStyler.add_heading_3(doc, "Tiêu Đề Cấp 3")
    assert "Tiêu Đề Cấp 3" in h3.text
    assert h3.style.name == "Heading 3"
    
    p = DocxStyler.add_paragraph(doc, "Đoạn văn chứa nồng độ H2SO4 là 15.5% và FeS2 là 28.5%.")
    assert "15,5%" in p.text
    assert "28,5%" in p.text
    
    headers = ["STT", "Chỉ Tiêu", "Giá Trị"]
    data = [["1", "Ca(OH)2", "120.5 mg/L"], ["2", "HNO3", "15.0 mg/L"]]
    DocxStyler.add_styled_table(doc, headers=headers, data=data)
    assert len(doc.tables) == 1
    tbl = doc.tables[0]
    assert len(tbl.rows) == 3
    print("  [PASS] All DocxStyler class methods created expected elements.")


def test_run_level_style_preservation():
    print("\n[TEST 3] Multi-Run Style Preservation in DocxStyler & DocxEditorEngine")
    doc = Document()
    p = doc.add_paragraph()
    r1 = p.add_run("Văn bản in đậm: ")
    r1.bold = True
    r2 = p.add_run("văn bản in nghiêng: ")
    r2.italic = True
    r3 = p.add_run("số liệu 45.5% tăng lên 85.0%.")
    r3.font.color.rgb = RGBColor(0xDC, 0x26, 0x26)
    
    buf = io.BytesIO()
    doc.save(buf)
    
    # 1. Test update_docx_content_preserving_styles
    mod_bytes = DocxStyler.update_docx_content_preserving_styles(buf.getvalue(), {"45.5%": "45,5%"})
    doc_mod = Document(io.BytesIO(mod_bytes))
    p_mod = doc_mod.paragraphs[0]
    assert len(p_mod.runs) == 3
    assert p_mod.runs[0].bold is True
    assert p_mod.runs[0].text == "Văn bản in đậm: "
    assert p_mod.runs[1].italic is True
    assert p_mod.runs[1].text == "văn bản in nghiêng: "
    assert p_mod.runs[2].font.color.rgb == RGBColor(0xDC, 0x26, 0x26)
    assert "45,5%" in p_mod.runs[2].text
    print("  [PASS] DocxStyler.update_docx_content_preserving_styles preserved all 3 run styles.")
    
    # 2. Test cross-run replacement
    doc_cross = Document()
    p_cross = doc_cross.add_paragraph()
    rc1 = p_cross.add_run("Tiền tố ")
    rc1.bold = True
    rc2 = p_cross.add_run("TừKhóa")
    rc2.italic = True
    rc3 = p_cross.add_run(" NốiTiếp hậu tố")
    rc3.font.color.rgb = RGBColor(0x25, 0x63, 0xEB)
    
    # Replace "TừKhóa NốiTiếp" across rc2 and rc3
    c = replace_text_in_paragraph_runs(p_cross, "TừKhóa NốiTiếp", "ĐãThayThế")
    assert c == 1
    assert p_cross.runs[0].text == "Tiền tố "
    assert p_cross.runs[0].bold is True
    assert "ĐãThayThế" in p_cross.runs[1].text
    assert p_cross.runs[1].italic is True
    assert p_cross.runs[2].text == " hậu tố"
    assert p_cross.runs[2].font.color.rgb == RGBColor(0x25, 0x63, 0xEB)
    print("  [PASS] Cross-run replacement preserved distinct styles before and after boundary.")


def test_docx_editor_engine_save_and_batch_replace():
    print("\n[TEST 4] DocxEditorEngine save_edited_docx & batch_replace_in_docx")
    engine = DocxEditorEngine()
    
    # 1. Test save_edited_docx
    res_save = engine.save_edited_docx(
        rel_path="Tai_Lieu/m2_test_save.docx",
        paragraphs=[
            {"text": "BÁO CÁO M2", "heading_level": 1},
            {"text": "1. Tổng Quan Môi Trường", "heading_level": 2},
            {"text": "Nồng độ Ca(OH)2 và HNO3 đo được là 25.5 mg/L tại 1.000 điểm đo.", "heading_level": 0}
        ],
        tables=[
            {
                "title": "Bảng Chỉ Số Kim Loại Nặng",
                "rows": [
                    ["STT", "Kim Loại", "Nồng Độ", "Hiệu Suất"],
                    ["1", "Cu2+", "15.5 mg/L", "92.5%"],
                    ["2", "Pb2+", "0.05 mg/L", "99.0%"]
                ]
            }
        ]
    )
    assert res_save["success"] is True
    saved_file = Path(res_save["abs_path"])
    assert saved_file.exists()
    
    doc_check = Document(saved_file)
    assert len(doc_check.paragraphs) >= 3
    assert len(doc_check.tables) == 1
    print("  [PASS] save_edited_docx succeeded without AttributeError.")
    
    # 2. Test batch_replace_in_docx
    res_rep = engine.batch_replace_in_docx(
        rel_path="Tai_Lieu/m2_test_save.docx",
        replacements=[
            {"find": "25,5 mg/L", "replace": "28,5 mg/L"},
            {"find": "15,5 mg/L", "replace": "18,5 mg/L"}
        ],
        output_rel_path="Tai_Lieu/m2_test_replaced.docx"
    )
    assert res_rep["success"] is True
    assert res_rep["total_replacements"] >= 2
    
    doc_rep = Document(Path(res_rep["abs_path"]))
    full_text = " ".join(p.text for p in doc_rep.paragraphs)
    assert "28,5 mg/L" in full_text
    tbl_text = " ".join(c.text for row in doc_rep.tables[0].rows for c in row.cells)
    assert "18,5 mg/L" in tbl_text
    print("  [PASS] batch_replace_in_docx succeeded across paragraphs and table cells.")


def test_chemical_formula_coverage():
    print("\n[TEST 5] Chemical Formula Map & Format Inline Coverage")
    required_chemicals = [
        ("Ca(OH)2", "Ca(OH)₂"),
        ("HNO3", "HNO₃"),
        ("H3PO4", "H₃PO₄"),
        ("Na2CO3", "Na₂CO₃"),
        ("NaHCO3", "NaHCO₃"),
        ("KMnO4", "KMnO₄"),
        ("Cu2+", "Cu²⁺"),
        ("Pb2+", "Pb²⁺"),
        ("Cd2+", "Cd²⁺"),
        ("Cr6+", "Cr⁶⁺"),
        ("As3+", "As³⁺"),
        ("PM2.5", "PM₂.₅"),
        ("PM10", "PM₁₀"),
        ("FeS2", "FeS₂"),
        ("H2SO4", "H₂SO₄"),
        ("NH4+", "NH₄⁺"),
        ("NO3-", "NO₃⁻"),
        ("Al3+", "Al³⁺"),
        ("BOD5", "BOD₅"),
        ("COD", "COD")
    ]
    
    for raw, expected in required_chemicals:
        assert raw in UNICODE_CHEM_MAP, f"Missing {raw} in UNICODE_CHEM_MAP"
        assert UNICODE_CHEM_MAP[raw] == expected, f"Expected {expected}, got {UNICODE_CHEM_MAP[raw]}"
    
    doc = Document()
    p = doc.add_paragraph("Mẫu chứa Ca(OH)2, HNO3, Cu2+, Pb2+, PM2.5 và PM10.")
    format_inline_chemical_formulas(p)
    assert "Ca(OH)₂" in p.text
    assert "HNO₃" in p.text
    assert "Cu²⁺" in p.text
    assert "Pb²⁺" in p.text
    assert "PM₂.₅" in p.text
    assert "PM₁₀" in p.text
    print("  [PASS] All 20 key chemical formulas and ions normalized correctly.")


if __name__ == "__main__":
    print("=" * 70)
    print("  RUNNING M2 MASTER VERIFICATION TEST SUITE")
    print("=" * 70)
    test_vietnamese_decimal_and_thousand_formatting()
    test_docx_styler_class_methods()
    test_run_level_style_preservation()
    test_docx_editor_engine_save_and_batch_replace()
    test_chemical_formula_coverage()
    print("\n" + "=" * 70)
    print("  ALL M2 VERIFICATION TESTS PASSED PERFECTLY (5/5)")
    print("=" * 70)
