# test_pdf_ocr_full_flow.py
"""
WEB SUPER v3.2 / v2.0 - Comprehensive E2E Test Suite for PDF Document AI OCR Engine.
Covers:
1. Document Inspection & Triage (Digital Searchable, Scanned-Only, Hybrid-Degraded).
2. Image Extraction & Fallback Pipeline.
3. Purpose-Built ABBYY OCR System Prompt & Table Parser Verification.
4. Document Processing & Semantic RAG Chunking with Page Citation Anchors ([file, Trang X]).
5. In-Place DOM Word (.docx) Export & Markdown Full-Text Persistence.
6. 1-Click Open-Notebook Ingestion & Knowledge Vault Synchronization.
7. Fault Tolerance & Adversarial Edge Cases (Corrupt PDFs, Empty Files, Unicode Filenames).
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

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import pypdf
import docx

from modules.shared.file_manager import file_mgr
from modules.shared.pdf_ocr_engine import PDFDocumentAIOcrEngine, ABBYY_OCR_SYSTEM_PROMPT
from modules.notebooklm.notebooklm_engine import open_notebook_engine


class TestPDFDocumentAIOcrEngine(unittest.TestCase):
    """Hermetic, Isolated End-to-End Test Suite for PDF OCR Subsystem."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_workspace = Path(self.temp_dir.name)
        
        # Save original workspace and redirect file_mgr to isolated temp directory
        self.orig_workspace = file_mgr.workspace
        file_mgr.workspace = self.temp_workspace
        file_mgr.docs_dir = self.temp_workspace / "Tai_Lieu"
        file_mgr.drafts_dir = self.temp_workspace / "Ban_Thao"
        file_mgr.publish_dir = self.temp_workspace / "Xuat_Ban"
        file_mgr.docs_dir.mkdir(parents=True, exist_ok=True)
        file_mgr.drafts_dir.mkdir(parents=True, exist_ok=True)
        file_mgr.publish_dir.mkdir(parents=True, exist_ok=True)

        self.ocr_engine = PDFDocumentAIOcrEngine()
        (self.temp_workspace / "Tai_Lieu" / "PDF_OCR_Cache").mkdir(parents=True, exist_ok=True)

        # Redirect open_notebook_engine directory
        self.orig_nb_dir = open_notebook_engine.notebooks_dir
        open_notebook_engine.notebooks_dir = self.temp_workspace / "notebooks"
        open_notebook_engine.notebooks_dir.mkdir(parents=True, exist_ok=True)
        open_notebook_engine._ensure_default_notebook()

    def tearDown(self):
        # Restore original paths
        file_mgr.workspace = self.orig_workspace
        file_mgr.docs_dir = self.orig_workspace / "Tai_Lieu"
        file_mgr.drafts_dir = self.orig_workspace / "Ban_Thao"
        file_mgr.publish_dir = self.orig_workspace / "Xuat_Ban"

        open_notebook_engine.notebooks_dir = self.orig_nb_dir
        
        self.temp_dir.cleanup()

    def _create_digital_pdf(self, path: Path, pages: int = 2) -> Path:
        """Helper to create a genuine digital PDF with rich searchable text and markdown tables."""
        c = canvas.Canvas(str(path), pagesize=letter)
        for p in range(1, pages + 1):
            c.setFont("Helvetica-Bold", 16)
            c.drawString(72, 750, f"# NGHIEP VU NGHIEN CUU KHOA HOC - TRANG {p}")
            c.setFont("Helvetica", 12)
            c.drawString(72, 720, f"## 1. Tong quan nghien cuu ve ky thuat OCR va phan tich du lieu")
            c.drawString(72, 700, f"Nong do FeS2 va H2SO4 trong mau do dat 28.5% so voi nguong cho phep la 1.5 mg/L.")
            c.drawString(72, 680, f"Theo tieu chuan DOI 10.1038/s41598-021-04362-w, chi tieu BOD5 dat 45.0 mg/L va COD dat 120.5 mg/L.")
            c.drawString(72, 660, f"| Chi So | Gia Tri Do | Don Vi |")
            c.drawString(72, 640, f"|---|---|---|")
            c.drawString(72, 620, f"| FeS2 | 28.5 | % |")
            c.drawString(72, 600, f"| H2SO4 | 1.5 | mg/L |")
            c.drawString(72, 580, f"| BOD5 | 45.0 | mg/L |")
            c.drawString(72, 550, f"Mo hinh du bao chuoi thoi gian dat do chinh xac cao voi R2 = 0.95 va MAPE = 2.85%.")
            c.showPage()
        c.save()
        return path

    def _create_scanned_pdf(self, path: Path, pages: int = 2) -> Path:
        """Helper to create a scanned-style PDF with near-zero extractable text."""
        c = canvas.Canvas(str(path), pagesize=letter)
        for _ in range(pages):
            # Draw geometrical shapes simulating a scanned page
            c.rect(50, 50, 500, 700, stroke=1, fill=0)
            c.line(50, 400, 550, 400)
            c.circle(300, 600, 50, stroke=1, fill=0)
            c.showPage()
        c.save()
        return path

    def _create_hybrid_pdf(self, path: Path) -> Path:
        """Helper to create a hybrid PDF (Page 1 has rich text, Page 2 is scanned)."""
        c = canvas.Canvas(str(path), pagesize=letter)
        # Page 1: Digital text
        c.setFont("Helvetica-Bold", 14)
        c.drawString(72, 750, "Bao cao moi truong toan dien - Trang ky thuat so 1")
        c.setFont("Helvetica", 11)
        c.drawString(72, 720, "Dac ta cac thong so hoa hoc va moi truong nuoc thai cong nghiep chi tiet.")
        c.drawString(72, 700, "Ket qua phan tich cho thay nong do ion NH4+ dat 15.8 mg/L va NO3- dat 5.2 mg/L.")
        c.drawString(72, 680, "He so tuong quan Pearson r = 0.89 dat do tin cay thong ke p < 0.001.")
        c.showPage()
        # Page 2: Scanned graphics only
        c.rect(100, 100, 400, 600)
        c.showPage()
        c.save()
        return path

    # ── TEST 1: PDF INSPECTION & TRIAGE ──────────────────────────────────────

    def test_01_inspect_digital_searchable_pdf(self):
        """Verify that digital searchable PDFs are correctly identified with fast_native recommendation."""
        pdf_path = self.temp_workspace / "Tai_Lieu" / "digital_sample.pdf"
        self._create_digital_pdf(pdf_path, pages=3)

        info = self.ocr_engine.inspect_pdf(pdf_path)
        self.assertEqual(info["status"], "success")
        self.assertEqual(info["filename"], "digital_sample.pdf")
        self.assertEqual(info["total_pages"], 3)
        self.assertEqual(info["doc_type"], "DIGITAL_SEARCHABLE")
        self.assertEqual(info["recommended_mode"], "fast_native")
        self.assertGreater(info["avg_chars_per_page"], 100)
        self.assertEqual(info["scanned_pages_count"], 0)
        self.assertEqual(info["digital_pages_count"], 3)

    def test_02_inspect_scanned_pdf(self):
        """Verify that pure scanned PDFs (<40 chars/page) are flagged for Vision AI OCR."""
        pdf_path = self.temp_workspace / "Tai_Lieu" / "scanned_sample.pdf"
        self._create_scanned_pdf(pdf_path, pages=2)

        info = self.ocr_engine.inspect_pdf(pdf_path)
        self.assertEqual(info["status"], "success")
        self.assertEqual(info["total_pages"], 2)
        self.assertEqual(info["doc_type"], "SCANNED_IMAGE_ONLY")
        self.assertEqual(info["recommended_mode"], "vision_ai")
        self.assertEqual(info["scanned_pages_count"], 2)
        self.assertEqual(info["digital_pages_count"], 0)

    def test_03_inspect_hybrid_pdf(self):
        """Verify that mixed digital/scanned PDFs trigger the HYBRID_DEGRADED auto mode."""
        pdf_path = self.temp_workspace / "Tai_Lieu" / "hybrid_sample.pdf"
        self._create_hybrid_pdf(pdf_path)

        info = self.ocr_engine.inspect_pdf(pdf_path)
        self.assertEqual(info["status"], "success")
        self.assertEqual(info["total_pages"], 2)
        self.assertEqual(info["doc_type"], "HYBRID_DEGRADED")
        self.assertEqual(info["recommended_mode"], "auto")
        self.assertEqual(info["scanned_pages_count"], 1)
        self.assertEqual(info["digital_pages_count"], 1)

    # ── TEST 2: PROMPT FORMATTING & TABLE EXTRACTION ─────────────────────────

    def test_04_system_prompt_compliance(self):
        """Verify ABBYY_OCR_SYSTEM_PROMPT contains all 5 mandatory invariant rules."""
        self.assertIn("EVIDENCE FIRST & ZERO FABRICATION", ABBYY_OCR_SYSTEM_PROMPT)
        self.assertIn("BẢO TOÀN CẤU TRÚC BẢNG BIỂU DẠNG LƯỚI", ABBYY_OCR_SYSTEM_PROMPT)
        self.assertIn("BẢO TOÀN CÔNG THỨC TOÁN & HÓA HỌC", ABBYY_OCR_SYSTEM_PROMPT)
        self.assertIn("CHUẨN HÓA SỐ THẬP PHÂN TIẾNG VIỆT", ABBYY_OCR_SYSTEM_PROMPT)
        self.assertIn("PHÂN CẤP TIÊU ĐỀ & ĐOẠN VĂN", ABBYY_OCR_SYSTEM_PROMPT)

    def test_05_markdown_table_parsing(self):
        """Verify markdown table parser correctly extracts structured headers and rows."""
        sample_md = (
            "# Báo Cáo Phân Tích\n\n"
            "Dưới đây là bảng số liệu thực nghiệm đo đạc:\n\n"
            "| Chỉ Số | Đơn Vị | Giá Trị Thực | Ngưỡng Tiêu Chuẩn |\n"
            "|---|---|---|---|\n"
            "| FeS₂ | % | 28,5 | < 30,0 |\n"
            "| H₂SO₄ | mg/L | 1,5 | < 2,0 |\n"
            "| NH₄⁺ | mg/L | 15,8 | < 20,0 |\n"
            "| pH | - | 7,2 | 6,5 - 8,5 |\n\n"
            "Đoạn văn tiếp theo..."
        )
        tables = self.ocr_engine._extract_tables_from_markdown(sample_md)
        self.assertEqual(len(tables), 1)
        table = tables[0]
        self.assertEqual(table["headers"], ["Chỉ Số", "Đơn Vị", "Giá Trị Thực", "Ngưỡng Tiêu Chuẩn"])
        self.assertEqual(len(table["rows"]), 4)
        self.assertEqual(table["rows"][0][0], "FeS₂")
        self.assertEqual(table["rows"][0][2], "28,5")
        self.assertEqual(table["rows"][1][0], "H₂SO₄")
        self.assertEqual(table["rows"][2][0], "NH₄⁺")

    # ── TEST 3: FULL PROCESSING PIPELINE & RAG CHUNKS ────────────────────────

    def test_06_process_pdf_document_digital_flow(self):
        """Verify full OCR and RAG chunking pipeline on a digital document."""
        pdf_path = self.temp_workspace / "Tai_Lieu" / "Nghien_Cuu_Moi_Truong_2026.pdf"
        self._create_digital_pdf(pdf_path, pages=2)

        res = self.ocr_engine.process_pdf_document(
            pdf_source=pdf_path,
            mode="auto",
            max_pages=10
        )

        self.assertEqual(res["status"], "success")
        self.assertEqual(res["filename"], "Nghien_Cuu_Moi_Truong_2026.pdf")
        self.assertEqual(res["total_pages"], 2)
        self.assertGreater(res["total_words"], 50)
        self.assertGreater(res["rag_chunks_count"], 0)

        # Verify page break markers in full markdown
        full_md = res["full_markdown"]
        self.assertIn("<!-- PAGE_BREAK: 1 -->", full_md)
        self.assertIn("<!-- PAGE_BREAK: 2 -->", full_md)
        self.assertIn("## [Trang 1]", full_md)
        self.assertIn("## [Trang 2]", full_md)

        # Verify RAG chunks structure and citation anchors
        rag_chunks = res["rag_chunks"]
        for chunk in rag_chunks:
            self.assertIn("id", chunk)
            self.assertIn("page_number", chunk)
            self.assertIn("section_heading", chunk)
            self.assertIn("content", chunk)
            self.assertIn("token_count_est", chunk)
            self.assertIn("citation_anchor", chunk)
            page_num = chunk["page_number"]
            # Citation anchor must strictly match format: [Filename, Trang X]
            self.assertEqual(chunk["citation_anchor"], f"[Nghien_Cuu_Moi_Truong_2026.pdf, Trang {page_num}]")

        # Verify persistent artifacts generated in Tai_Lieu/
        md_file = self.temp_workspace / res["md_file_path"]
        json_file = self.temp_workspace / res["json_chunks_path"]
        self.assertTrue(md_file.exists())
        self.assertTrue(json_file.exists())

        loaded_chunks = json.loads(json_file.read_text(encoding="utf-8"))
        self.assertEqual(len(loaded_chunks), len(rag_chunks))

    # ── TEST 4: SEARCHABLE WORD DOCX EXPORT ──────────────────────────────────

    def test_07_export_searchable_docx(self):
        """Verify export_searchable_docx generates a high-fidelity In-Place DOM Word file."""
        pdf_path = self.temp_workspace / "Tai_Lieu" / "Academic_Report.pdf"
        self._create_digital_pdf(pdf_path, pages=2)

        res = self.ocr_engine.process_pdf_document(pdf_source=pdf_path)
        export_res = self.ocr_engine.export_searchable_docx(res)

        self.assertEqual(export_res["status"], "success")
        docx_path = Path(export_res["full_path"])
        self.assertTrue(docx_path.exists())
        self.assertGreater(docx_path.stat().st_size, 1000)

        # Validate that the generated docx can be parsed by python-docx
        doc = docx.Document(str(docx_path))
        self.assertGreater(len(doc.paragraphs), 0)
        full_doc_text = " ".join(p.text for p in doc.paragraphs)
        self.assertIn("ACADEMIC_REPORT", full_doc_text.upper())

    # ── TEST 5: 1-CLICK OPEN-NOTEBOOK INGESTION ──────────────────────────────

    def test_08_ingest_to_open_notebook(self):
        """Verify 1-click ingestion registers the OCR full-text and chunks into Open-Notebook."""
        # Create a target notebook
        nb = open_notebook_engine.create_notebook(name="Notebook Quan Trac Moi Truong", topic="Môi Trường & Hóa Học")
        nb_id = nb["id"]

        pdf_path = self.temp_workspace / "Tai_Lieu" / "Bao_Cao_Mau_Nuoc.pdf"
        self._create_digital_pdf(pdf_path, pages=2)
        ocr_res = self.ocr_engine.process_pdf_document(pdf_source=pdf_path)

        ingest_res = self.ocr_engine.ingest_to_open_notebook(ocr_res, notebook_id=nb_id)
        self.assertEqual(ingest_res["status"], "success")
        self.assertGreater(ingest_res["chunks_added"], 0)

        # Check notebook sources and chunks in storage
        nb_details = open_notebook_engine.get_notebook_details(nb_id)
        self.assertEqual(len(nb_details["sources"]), 1)
        self.assertIn("Bao_Cao_Mau_Nuoc", nb_details["sources"][0]["title"])
        self.assertGreater(nb_details["chunks_count"], 0)

    # ── TEST 6: FAULT TOLERANCE & EDGE CASES ─────────────────────────────────

    def test_09_nonexistent_pdf_file(self):
        """Verify graceful error reporting when PDF file does not exist."""
        res = self.ocr_engine.inspect_pdf("Tai_Lieu/non_existent_file.pdf")
        self.assertEqual(res["status"], "error")
        self.assertIn("Không tìm thấy tệp", res["message"])

        proc_res = self.ocr_engine.process_pdf_document("Tai_Lieu/non_existent_file.pdf")
        self.assertEqual(proc_res["status"], "error")

    def test_10_corrupt_pdf_handling(self):
        """Verify graceful error handling for corrupt / invalid PDF bytes."""
        corrupt_path = self.temp_workspace / "Tai_Lieu" / "corrupted.pdf"
        corrupt_path.write_bytes(b"%PDF-1.4 CORRUPTED DATA NOT A REAL PDF EOF")

        res = self.ocr_engine.inspect_pdf(corrupt_path)
        self.assertEqual(res["status"], "error")
        self.assertIn("Lỗi kiểm tra PDF", res["message"])

    def test_11_vietnamese_unicode_filename(self):
        """Verify that filenames with Vietnamese Unicode and spaces are handled seamlessly."""
        pdf_path = self.temp_workspace / "Tai_Lieu" / "Báo Cáo Nghiên Cứu Môi Trường Đất & Nước 2026.pdf"
        self._create_digital_pdf(pdf_path, pages=1)

        res = self.ocr_engine.process_pdf_document(pdf_source=pdf_path)
        self.assertEqual(res["status"], "success")
        md_file = self.temp_workspace / res["md_file_path"]
        self.assertTrue(md_file.exists())
        self.assertTrue(md_file.name.endswith("_Searchable_OCR.md"))
        
        docx_res = self.ocr_engine.export_searchable_docx(res)
        self.assertEqual(docx_res["status"], "success")
        self.assertTrue(Path(docx_res["full_path"]).exists())


def run_tests():
    """Test runner with formatted console output."""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPDFDocumentAIOcrEngine)
    runner = unittest.TextTestRunner(verbosity=2)
    start_time = time.time()
    result = runner.run(suite)
    elapsed = round(time.time() - start_time, 2)
    
    print("\n" + "=" * 70)
    print(f"📊 PDF OCR FULL FLOW TEST SUITE SUMMARY:")
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
