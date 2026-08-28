import unittest
import os
import sys
import json
import zipfile
import re
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from modules.zotero.zotero_converter_engine import zotero_converter, export_batch_ris, export_batch_bibtex
from modules.academic_writer.academic_writer_engine import academic_writer, AcademicWriterEngine


class TestWorkerM2Verification(unittest.TestCase):
    def setUp(self):
        self.sample_meta_items = [
            {
                "author": "Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., Kaiser, Ł., & Polosukhin, I.",
                "year": "2017",
                "title": "Attention Is All You Need",
                "journal": "Advances in Neural Information Processing Systems",
                "volume": "30",
                "pages": "5998-6008",
                "doi": "10.48550/arXiv.1706.03762",
                "source_url": "https://doi.org/10.48550/arXiv.1706.03762",
                "abstract": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks."
            },
            {
                "author": "LeCun, Y., Bengio, Y., & Hinton, G.",
                "year": "2015",
                "title": "Deep learning",
                "journal": "Nature",
                "volume": "521",
                "issue": "7553",
                "pages": "436-444",
                "doi": "10.1038/nature14539",
                "source_url": "https://doi.org/10.1038/nature14539",
                "abstract": "Deep learning allows computational models that are composed of multiple processing layers to learn representations of data."
            }
        ]

    def test_r2_1_no_hardcoded_madlibs_formulas_in_synthesizer(self):
        """Test R2.1: Verify synthesizer does not output fixed mad-libs numbers/formulas."""
        topic = "Quan trắc Môi trường Nước bằng IoT"
        engine = AcademicWriterEngine()
        
        # Test Theory Section
        theory_sec = engine._synthesize_grounded_academic_section(
            section_idx=2,
            section_title="Cơ sở lý thuyết & Khung phân tích",
            section_subsections=["Khung lý thuyết", "Tổng quan"],
            topic=topic,
            paper_type="Báo cáo khoa học",
            evidence_block="Tóm tắt thực chứng: Nghiên cứu quan trắc nước bằng cảm biến quang học.",
            allowed_citation_keys=["Vaswani et al., 2017", "LeCun et al., 2015"]
        )
        # Verify hardcoded static formula is gone
        self.assertNotIn(r"\dot{\mathbf{x}}(t) = \mathbf{A}\mathbf{x}(t)", theory_sec)
        # Verify topic presence
        self.assertIn(topic, theory_sec)
        # Verify [uncertain] tag presence for unmeasured parameters
        self.assertIn("[uncertain", theory_sec)

        # Test Results Section
        results_sec = engine._synthesize_grounded_academic_section(
            section_idx=4,
            section_title="Kết quả nghiên cứu và Phân tích thực nghiệm",
            section_subsections=["Kết quả", "Kiểm định"],
            topic=topic,
            paper_type="Báo cáo khoa học",
            evidence_block="Tóm tắt thực chứng: Kết quả đo đạc BOD5 và COD qua mạng LoRaWAN.",
            allowed_citation_keys=["Vaswani et al., 2017", "LeCun et al., 2015"]
        )
        # Verify hardcoded numbers are gone
        self.assertNotIn("18.500", results_sec)
        self.assertNotIn("-41,6%", results_sec)
        self.assertNotIn("t = 8,92, p = 0,0001", results_sec)
        # Verify 4-layer argumentation
        self.assertIn("Tầng 1", results_sec)
        self.assertIn("Tầng 2", results_sec)
        self.assertIn("Tầng 3", results_sec)
        self.assertIn("Tầng 4", results_sec)

    def test_r2_1_section_aware_evidence_retrieval(self):
        """Test R2.1: Section-aware evidence retrieval adapts to section type."""
        engine = AcademicWriterEngine()
        topic = "Trí tuệ Nhân tạo trong Y tế"
        
        intro_evidence = engine._retrieve_section_evidence(
            topic=topic,
            section_title="1. MỞ ĐẦU & TÍNH CẤP THIẾT",
            section_subsections=["Bối cảnh", "Mục tiêu"],
            meta_items=self.sample_meta_items
        )
        self.assertIn("INTRODUCTION", intro_evidence)
        self.assertIn("Vaswani", intro_evidence)

        method_evidence = engine._retrieve_section_evidence(
            topic=topic,
            section_title="3. PHƯƠNG PHÁP NGHIÊN CỨU & MÔ HÌNH",
            section_subsections=["Thuật toán", "Dữ liệu"],
            meta_items=self.sample_meta_items
        )
        self.assertIn("METHODOLOGY", method_evidence)

    def test_r2_2_export_batch_ris_format_and_real_dois(self):
        """Test R2.3: RIS multi-record batch export with 100% verified real DOIs."""
        ris_text = export_batch_ris(self.sample_meta_items)
        
        # Verify RIS structure tags
        self.assertIn("TY  - JOUR", ris_text)
        self.assertIn("TI  - Attention Is All You Need", ris_text)
        self.assertIn("DO  - 10.48550/arXiv.1706.03762", ris_text)
        self.assertIn("TI  - Deep learning", ris_text)
        self.assertIn("DO  - 10.1038/nature14539", ris_text)
        self.assertIn("PY  - 2017", ris_text)
        self.assertIn("PY  - 2015", ris_text)
        self.assertIn("ER  -", ris_text)
        # Should have 2 ER tags for 2 records
        self.assertEqual(ris_text.count("ER  -"), 2)

    def test_r2_2_export_batch_bibtex_format_and_real_dois(self):
        """Test R2.3: BibTeX multi-record batch export with valid citekeys and real DOIs."""
        bib_text = export_batch_bibtex(self.sample_meta_items)
        
        # Verify BibTeX structure
        self.assertIn("@article{", bib_text)
        self.assertIn("Attention Is All You Need", bib_text)
        self.assertIn("doi = {10.48550/arXiv.1706.03762}", bib_text)
        self.assertIn("Deep learning", bib_text)
        self.assertIn("doi = {10.1038/nature14539}", bib_text)
        self.assertEqual(bib_text.count("@article{"), 2)

    def test_r2_3_generate_2_files_and_zotero_dom_embedding(self):
        """Test R2.2 & R2.3: generate_2_files auto-embeds Zotero XML DOM and produces RIS & BIB."""
        topic = "Test Tự Động Hóa AI M2"
        res = academic_writer.generate_2_files(
            topic=topic,
            author_name="Kỹ Sư Kiểm Thử M2",
            paper_type="Báo cáo khoa học"
        )
        
        self.assertEqual(res.get("status"), "success")
        
        # Check File A (.docx & .md)
        file_a_path = res.get("file_a_path")
        self.assertTrue(os.path.exists(file_a_path))
        
        # Inspect File A docx XML DOM for Zotero CSL field codes
        has_zotero_field_code = False
        with zipfile.ZipFile(file_a_path, "r") as docx_zip:
            if "word/document.xml" in docx_zip.namelist():
                doc_xml = docx_zip.read("word/document.xml").decode("utf-8")
                if "w:fldSimple" in doc_xml or "ADDIN ZOTERO_ITEM" in doc_xml:
                    has_zotero_field_code = True
        
        self.assertTrue(has_zotero_field_code, "File A docx MUST contain Zotero CSL XML field codes (w:fldSimple)")

        # Check File B (.docx)
        file_b_path = res.get("file_b_path")
        self.assertTrue(os.path.exists(file_b_path))

        # Check Companion RIS & BIB files
        file_ris_path = res.get("file_ris_path")
        file_bib_path = res.get("file_bib_path")
        self.assertTrue(file_ris_path and os.path.exists(file_ris_path), "Companion .ris file MUST exist")
        self.assertTrue(file_bib_path and os.path.exists(file_bib_path), "Companion .bib file MUST exist")

        with open(file_ris_path, "r", encoding="utf-8") as f:
            ris_content = f.read()
            self.assertIn("TY  - JOUR", ris_content)
            self.assertIn("ER  -", ris_content)

        with open(file_bib_path, "r", encoding="utf-8") as f:
            bib_content = f.read()
            self.assertIn("@article{", bib_content)

        # Check response dictionary
        self.assertGreaterEqual(res["file_ris"]["records_count"], 1)
        self.assertEqual(res["file_ris"]["records_count"], res["file_bib"]["records_count"])

    def test_r2_4_frontend_js_contains_ris_bib_handlers(self):
        """Test R2.3: Check academic-writer.js contains download handlers for .ris and .bib."""
        js_path = PROJECT_ROOT / "static" / "js" / "academic-writer.js"
        self.assertTrue(js_path.exists())
        
        with open(js_path, "r", encoding="utf-8") as f:
            js_code = f.read()
        
        self.assertIn("fileRis", js_code)
        self.assertIn("fileBib", js_code)
        self.assertIn("Tải Tệp .RIS (Zotero 1-Click)", js_code)
        self.assertIn("Tải Tệp .BIB (BibTeX)", js_code)


if __name__ == "__main__":
    unittest.main()
