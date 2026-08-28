# test_docx_editor_engine.py
"""
WEB SUPER v3.2 / v2.0 - Comprehensive E2E Test Suite for Word .docx DOM Engine & Math/Chem Subsystem.
Covers:
1. DocxStyler Core Class Methods (apply_document_styles, add_heading_1/2/3, add_paragraph, add_styled_table).
2. Vietnamese Number & Typography Conversion (convert_decimals_preserve_sections with strict protection of DOIs, URLs, sections, versions).
3. Math/Chem Formula & Symbol Standardization (clean_inline_latex_math, Greek alphabet, UNICODE_CHEM_MAP compounds).
4. DocxEditorEngine DOM Parsing (parse_docx: Headings, Paragraphs, Tables, Extracted Numerical Data Points).
5. In-Place Word File Generation & Storage (save_edited_docx with structured paragraphs & tables).
6. Multi-Target Batch Search & Replace in Word (batch_replace_in_docx across paragraphs and tables).
7. DOM In-Place Preservation & Multi-Run Formatting Safety (update_docx_content_preserving_styles).
8. Table Grid Styling, Borders, Cell Margins, and Zebra Backgrounds.
"""

import os
import io
import sys
import json
import time
import shutil
import tempfile
import unittest
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

from modules.shared.file_manager import file_mgr
from modules.shared.docx_styler import (
    DocxStyler,
    COLOR_PRIMARY,
    COLOR_SECONDARY,
    COLOR_BODY,
    HEX_HEADER_BG,
    HEX_BORDER,
    set_cell_background,
    set_cell_margins,
    set_table_borders,
    sanitize_xml_text
)
from modules.shared.docx_formula_engine import UNICODE_CHEM_MAP
from modules.workspace.docx_editor_engine import DocxEditorEngine, docx_editor


class TestDocxEditorAndDOMEngine(unittest.TestCase):
    """Hermetic, Isolated End-to-End Test Suite for Word .docx DOM & Math/Chem Engine."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_workspace = Path(self.temp_dir.name)

        # Redirect file_mgr workspace
        self.orig_workspace = file_mgr.workspace
        file_mgr.workspace = self.temp_workspace
        file_mgr.docs_dir = self.temp_workspace / "Tai_Lieu"
        file_mgr.drafts_dir = self.temp_workspace / "Ban_Thao"
        file_mgr.publish_dir = self.temp_workspace / "Xuat_Ban"
        file_mgr.docs_dir.mkdir(parents=True, exist_ok=True)
        file_mgr.drafts_dir.mkdir(parents=True, exist_ok=True)
        file_mgr.publish_dir.mkdir(parents=True, exist_ok=True)

        self.editor = DocxEditorEngine()
        self.editor.workspace = self.temp_workspace

    def tearDown(self):
        file_mgr.workspace = self.orig_workspace
        file_mgr.docs_dir = self.orig_workspace / "Tai_Lieu"
        file_mgr.drafts_dir = self.orig_workspace / "Ban_Thao"
        file_mgr.publish_dir = self.orig_workspace / "Xuat_Ban"
        self.temp_dir.cleanup()

    # ── TEST 1: VIETNAMESE DECIMAL & NUMBER TYPOGRAPHY ───────────────────────

    def test_01_vietnamese_decimal_conversion_accuracy(self):
        """Verify convert_decimals_preserve_sections transforms decimal numbers while preserving protected tokens."""
        # 1. Real decimal measurements with units
        input_text = "Nồng độ FeS₂ đạt 28.5% và lượng axit H₂SO₄ tiêu hao là 1.5 mg/L với sai số 0.05 ppm."
        result = DocxStyler.convert_decimals_preserve_sections(input_text)
        self.assertIn("28,5%", result)
        self.assertIn("1,5 mg/L", result)
        self.assertIn("0,05", result)

        # 2. Strict Protection of DOIs
        doi_text = "Nghiên cứu theo DOI: 10.1038/s41598-021-04362-w và https://doi.org/10.1016/j.envres.2023.115890."
        res_doi = DocxStyler.convert_decimals_preserve_sections(doi_text)
        self.assertIn("10.1038/s41598-021-04362-w", res_doi)
        self.assertIn("10.1016/j.envres.2023.115890", res_doi)
        self.assertNotIn("10,1038", res_doi)

        # 3. Strict Protection of Section Headings & Versions
        sec_text = "Mục 1.2 và Điều 2.3.4 trong phiên bản v3.1 sử dụng Python 3.11 và Gemini 1.5 Pro."
        res_sec = DocxStyler.convert_decimals_preserve_sections(sec_text)
        self.assertIn("Mục 1.2", res_sec)
        self.assertIn("Điều 2.3.4", res_sec)
        self.assertIn("v3.1", res_sec)
        self.assertIn("Python 3.11", res_sec)
        self.assertIn("Gemini 1.5", res_sec)

        # 4. Strict Protection of File Names & Emails
        file_text = "Tệp dữ liệu data_v2.0.csv và metadata.json gửi tới contact.research@univ.edu.vn."
        res_file = DocxStyler.convert_decimals_preserve_sections(file_text)
        self.assertIn("data_v2.0.csv", res_file)
        self.assertIn("metadata.json", res_file)
        self.assertIn("contact.research@univ.edu.vn", res_file)

    # ── TEST 2: MATH & CHEMICAL FORMULA CONVERSION ───────────────────────────

    def test_02_math_chem_symbols_and_latex_cleaning(self):
        """Verify clean_inline_latex_math converts LaTeX symbols, Greek alphabet, and chemical formulas."""
        # 1. Greek letters & mathematical operators
        latex_str = r"Giả thuyết $H_0$: \alpha = 0.05, hệ số \beta = 1.25, độ lệch \Delta = 0.15 \pm 0.02 \approx \gamma."
        cleaned = DocxStyler.clean_inline_latex_math(latex_str)
        self.assertIn("α", cleaned)
        self.assertIn("β", cleaned)
        self.assertIn("Δ", cleaned)
        self.assertIn("±", cleaned)
        self.assertIn("≈", cleaned)
        self.assertIn("γ", cleaned)

        # 2. Fractions and Square roots
        math_expr = r"Tính toán \sqrt{x^2 + y^2} và phân số \frac{A}{B}."
        res_math = DocxStyler.clean_inline_latex_math(math_expr)
        self.assertIn("√(x² + y²)", res_math)
        self.assertIn("(A/B)", res_math)

        # 3. Chemical compound notation from UNICODE_CHEM_MAP
        chem_text = "Các chất FeS2, H2SO4, NH4+, NO3-, Al3+, BOD5, CaCO3, SO2, NO2."
        res_chem = DocxStyler.clean_inline_latex_math(chem_text)
        self.assertIn("FeS₂", res_chem)
        self.assertIn("H₂SO₄", res_chem)
        self.assertIn("NH₄⁺", res_chem)
        self.assertIn("NO₃⁻", res_chem)
        self.assertIn("Al³⁺", res_chem)
        self.assertIn("BOD₅", res_chem)
        self.assertIn("CaCO₃", res_chem)
        self.assertIn("SO₂", res_chem)
        self.assertIn("NO₂", res_chem)

    def test_03_unicode_chem_map_completeness(self):
        """Verify UNICODE_CHEM_MAP covers core environmental and chemical substances."""
        self.assertGreaterEqual(len(UNICODE_CHEM_MAP), 30)
        expected_compounds = ["FeS2", "H2SO4", "NH4+", "NO3-", "Al3+", "BOD5", "CO2", "CaCO3"]
        for comp in expected_compounds:
            self.assertIn(comp, UNICODE_CHEM_MAP)
            # Verify mapped value has proper subscript/superscript
            self.assertNotEqual(UNICODE_CHEM_MAP[comp], comp)

    # ── TEST 3: DOCX STYLER CLASS METHODS & HEADINGS ─────────────────────────

    def test_04_docx_styler_class_methods(self):
        """Verify DocxStyler class methods: apply_document_styles, headings, paragraphs, and tables."""
        doc = Document()
        
        # 1. Apply document styles
        DocxStyler.apply_document_styles(doc)
        
        # 2. Add Headings (H1, H2, H3)
        h1 = DocxStyler.add_heading_1(doc, "1. TỔNG QUAN NGHIÊN CỨU")
        h2 = DocxStyler.add_heading_2(doc, "1.1. Cơ Sở Lý Thuyết")
        h3 = DocxStyler.add_heading_3(doc, "1.1.1. Khung Phân Tích")
        p = DocxStyler.add_paragraph(doc, "Nội dung đoạn văn học thuật với chuẩn phông Times New Roman 14pt.")

        self.assertEqual(h1.text, "1. TỔNG QUAN NGHIÊN CỨU")
        self.assertEqual(h2.text, "1.1. Cơ Sở Lý Thuyết")
        self.assertEqual(h3.text, "1.1.1. Khung Phân Tích")
        self.assertEqual(p.text, "Nội dung đoạn văn học thuật với chuẩn phông Times New Roman 14pt.")

        # 3. Add styled table
        headers = ["STT", "Thông Số", "Giá Trị", "Đơn Vị"]
        data = [
            ["1", "FeS₂", "28,5", "%"],
            ["2", "H₂SO₄", "1,5", "mg/L"],
            ["3", "pH", "7,2", "-"]
        ]
        DocxStyler.add_styled_table(doc, headers=headers, data=data)
        self.assertGreaterEqual(len(doc.tables), 1)
        tbl = doc.tables[-1]
        self.assertEqual(len(tbl.rows), 4)
        self.assertEqual(len(tbl.columns), 4)

        # Save and verify
        test_docx_path = self.temp_workspace / "Ban_Thao" / "styler_test.docx"
        doc.save(str(test_docx_path))
        self.assertTrue(test_docx_path.exists())
        self.assertGreater(test_docx_path.stat().st_size, 1000)

    # ── TEST 4: DOCX EDITOR ENGINE PARSE & DATA EXTRACTION ───────────────────

    def test_05_parse_docx_headings_and_data_points(self):
        """Verify DocxEditorEngine.parse_docx correctly extracts paragraphs, headings, tables, and metrics."""
        # 1. Create a structured sample .docx
        sample_docx_path = self.temp_workspace / "Ban_Thao" / "sample_experiment.docx"
        doc = Document()
        DocxStyler.apply_document_styles(doc)
        DocxStyler.add_heading_1(doc, "BÁO CÁO THỰC NGHIỆM HÓA HỌC")
        DocxStyler.add_paragraph(doc, "Tỷ lệ tăng trưởng đạt 24.5% trong điều kiện nhiệt độ 25°C và nồng độ 1.5 mg/L.")
        DocxStyler.add_heading_2(doc, "KẾT QUẢ ĐO ĐẠC")
        
        headers = ["Chỉ Số", "Đo Đạc", "Chuẩn"]
        data = [
            ["FeS₂", "28.5%", "< 30%"],
            ["COD", "120.5 mg/L", "< 150 mg/L"]
        ]
        DocxStyler.add_styled_table(doc, headers=headers, data=data)
        doc.save(str(sample_docx_path))

        # 2. Parse using DocxEditorEngine
        parsed = self.editor.parse_docx(sample_docx_path, filename="sample_experiment.docx")
        self.assertTrue(parsed["success"])
        self.assertEqual(parsed["filename"], "sample_experiment.docx")
        
        # Verify paragraphs
        self.assertGreaterEqual(len(parsed["paragraphs"]), 2)
        h1_paras = [p for p in parsed["paragraphs"] if p["heading_level"] == 1]
        self.assertEqual(len(h1_paras), 1)
        self.assertEqual(h1_paras[0]["text"], "BÁO CÁO THỰC NGHIỆM HÓA HỌC")

        # Verify tables
        self.assertEqual(len(parsed["tables"]), 1)
        tbl_data = parsed["tables"][0]
        self.assertEqual(tbl_data["row_count"], 3)
        self.assertEqual(tbl_data["col_count"], 3)

        # Verify extracted numerical data points (DocxStyler automatically converted 24.5% to 24,5%)
        extracted_pts = parsed["extracted_data_points"]
        self.assertGreaterEqual(len(extracted_pts), 2)
        pt_values = [pt["value"] for pt in extracted_pts]
        self.assertTrue(any("24,5%" in v or "24.5%" in v for v in pt_values))
        self.assertTrue(any("1,5 mg/L" in v or "1.5 mg/L" in v for v in pt_values))

    # ── TEST 5: SAVE EDITED DOCX IN-PLACE ────────────────────────────────────

    def test_06_save_edited_docx_flow(self):
        """Verify save_edited_docx saves edited content and tables into a clean .docx file."""
        content_text = (
            "# BÁO CÁO TỔNG KẾT DỰ ÁN\n"
            "## 1. Giới Thiệu Chung\n"
            "Dự án đạt hiệu suất 98.5% và tiết kiệm 35.0% chi phí vận hành.\n"
            "### 1.1. Chi Tiết Phương Pháp\n"
            "Áp dụng mô hình AI.FORECAST dải tin cậy 95%."
        )
        tables = [
            {
                "title": "Bảng Tổng Hợp Chi Phí",
                "rows": [
                    ["Hạng Mục", "Chi Phí (VNĐ)", "Tỷ Lệ (%)"],
                    ["Phần Cứng", "50.000.000", "45,0%"],
                    ["Nhân Lực", "60.000.000", "55,0%"]
                ]
            }
        ]

        save_res = self.editor.save_edited_docx(
            rel_path="Ban_Thao/Bao_Cao_Tong_Ket.docx",
            content_text=content_text,
            tables=tables,
            topic="Tổng Kết Dự Án"
        )

        self.assertTrue(save_res["success"])
        self.assertEqual(save_res["filename"], "Bao_Cao_Tong_Ket.docx")
        
        target_file = self.temp_workspace / "Ban_Thao" / "Bao_Cao_Tong_Ket.docx"
        self.assertTrue(target_file.exists())
        self.assertGreater(target_file.stat().st_size, 1000)

        # Re-parse to verify structure
        re_parsed = self.editor.parse_docx(target_file)
        self.assertEqual(len(re_parsed["tables"]), 1)
        self.assertEqual(re_parsed["tables"][0]["row_count"], 3)

    # ── TEST 6: BATCH SEARCH & REPLACE IN WORD ────────────────────────────────

    def test_07_batch_replace_in_docx_paragraphs_and_tables(self):
        """Verify batch_replace_in_docx replaces terms and numbers across paragraphs and table cells."""
        # 1. Create source document
        src_path = self.temp_workspace / "Ban_Thao" / "report_to_replace.docx"
        doc = Document()
        DocxStyler.apply_document_styles(doc)
        DocxStyler.add_heading_1(doc, "BÁO CÁO NĂNG LƯỢNG 2025")
        DocxStyler.add_paragraph(doc, "Tổng sản lượng đạt 15.5 MWh với hiệu suất 85.0%.")
        
        # Add table with target phrases
        tbl = doc.add_table(rows=3, cols=3)
        tbl.cell(0, 0).text = "Nguồn"
        tbl.cell(0, 1).text = "Sản Lượng"
        tbl.cell(0, 2).text = "Hiệu Suất"
        tbl.cell(1, 0).text = "Mặt Trời"
        tbl.cell(1, 1).text = "15.5 MWh"
        tbl.cell(1, 2).text = "85.0%"
        tbl.cell(2, 0).text = "Gió"
        tbl.cell(2, 1).text = "20.0 MWh"
        tbl.cell(2, 2).text = "90.0%"
        doc.save(str(src_path))

        # 2. Execute batch replacement
        replacements = [
            {"find": "15.5 MWh", "replace": "18,2 MWh"},
            {"find": "85.0%", "replace": "88,5%"},
            {"find": "2025", "replace": "2026"}
        ]
        rep_res = self.editor.batch_replace_in_docx(
            rel_path="Ban_Thao/report_to_replace.docx",
            replacements=replacements
        )

        self.assertTrue(rep_res["success"])
        self.assertGreaterEqual(rep_res["total_replacements"], 3)

        # 3. Read back and verify replacements took effect
        re_doc = Document(str(src_path))
        re_full_text = " ".join([p.text for p in re_doc.paragraphs])
        for tbl in re_doc.tables:
            for row in tbl.rows:
                re_full_text += " " + " ".join([c.text for c in row.cells])

        self.assertIn("18,2 MWh", re_full_text)
        self.assertIn("88,5%", re_full_text)
        self.assertIn("2026", re_full_text)
        self.assertNotIn("15.5 MWh", re_full_text)

    # ── TEST 7: MULTI-RUN DOM PRESERVATION ───────────────────────────────────

    def test_08_multi_run_preservation_in_paragraph(self):
        """Verify update_docx_content_preserving_styles updates content while preserving styles."""
        doc = Document()
        p = doc.add_paragraph()
        
        # Add styled runs
        run1 = p.add_run("Phát hiện quan trọng: ")
        run1.bold = True
        
        run2 = p.add_run("Nồng độ ion FeS₂ đạt 28.5% ")
        run2.italic = True
        
        run3 = p.add_run("trong môi trường kiểm nghiệm.")
        run3.font.color.rgb = RGBColor(30, 58, 138)

        # Save to buffer
        buf = io.BytesIO()
        doc.save(buf)
        doc_bytes = buf.getvalue()

        # Update preserving styles
        updated_bytes = DocxStyler.update_docx_content_preserving_styles(
            input_bytes=doc_bytes,
            replacements={"28.5%": "28,5%"}
        )

        # Load updated document
        updated_doc = Document(io.BytesIO(updated_bytes))
        p_updated = updated_doc.paragraphs[0]
        self.assertIn("28,5%", p_updated.text)
        self.assertTrue(p_updated.runs[0].bold)

    # ── TEST 8: TABLE STYLING, BORDERS, & CELL BACKGROUNDS ───────────────────

    def test_09_table_grid_styling_helpers(self):
        """Verify XML styling helpers: set_cell_background, set_cell_margins, set_table_borders."""
        doc = Document()
        tbl = doc.add_table(rows=2, cols=2)
        
        # Apply table styling functions
        set_table_borders(tbl, hex_color=HEX_BORDER)
        cell = tbl.cell(0, 0)
        set_cell_background(cell, hex_color=HEX_HEADER_BG)
        set_cell_margins(cell, top=120, bottom=120, left=180, right=180)

        # Verify XML structure
        tc_xml = cell._tc.xml
        self.assertIn(HEX_HEADER_BG, tc_xml)
        self.assertIn("w:tcMar", tc_xml)

        tbl_xml = tbl._tbl.xml
        self.assertIn("w:tblBorders", tbl_xml)

    # ── TEST 9: XML SANITIZATION & ADVERSARIAL CONTROL CHARACTERS ────────────

    def test_10_sanitize_xml_text_control_characters(self):
        """Verify sanitize_xml_text strips invalid XML control characters while preserving valid text."""
        dirty_text = "Tiêu đề nghiên cứu\x00\x08\x0b\x0c\x1f có ký tự lỗi \x7f nhưng giữ lại \n\t dấu cách."
        clean = sanitize_xml_text(dirty_text)
        self.assertNotIn("\x00", clean)
        self.assertNotIn("\x08", clean)
        self.assertNotIn("\x0b", clean)
        self.assertNotIn("\x1f", clean)
        self.assertIn("Tiêu đề nghiên cứu", clean)
        self.assertIn("\n\t", clean)


def run_tests():
    """Test runner with formatted console output."""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDocxEditorAndDOMEngine)
    runner = unittest.TextTestRunner(verbosity=2)
    start_time = time.time()
    result = runner.run(suite)
    elapsed = round(time.time() - start_time, 2)

    print("\n" + "=" * 70)
    print(f"📊 DOCX DOM EDITOR & MATH/CHEM TEST SUITE SUMMARY:")
    print(f"   Total Tests Run: {result.testsRun}")
    print(f"   Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    print(f"   Execution Time: {elapsed}s")
    print("=" * 70)

    return len(result.failures) == 0 and len(result.errors) == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
