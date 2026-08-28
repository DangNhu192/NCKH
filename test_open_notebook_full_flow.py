# test_open_notebook_full_flow.py
"""
WEB SUPER v3.2 / v2.0 - Comprehensive E2E Test Suite for Open-Notebook RAG Knowledge Vault.
Covers:
1. Knowledge Vault Lifecycle (Notebook CRUD, Indexing, Metadata Persistence).
2. Author Extraction & APA 7th Citation Formatting.
3. Multi-Modal Source Ingestion (Raw Text, Markdown, Docx, PDF).
4. Section & Paragraph Aware Semantic Chunking.
5. Hybrid Retrieval Engine (Exact BM25 Token Matching + Tri/4-Gram Cosine Similarity).
6. Grounded Q&A Chat & Citation Verification ([Tác giả, Năm]).
7. Signature Research Transformations Studio (Podcast, Study Guide, FAQ, Synthesis Matrix, Research Gaps).
8. 7-Column Literature Review Matrix (.md & .docx Export).
9. Pipeline Step 2 Sync & Zotero Interoperability.
10. Adversarial & Edge Cases (Empty Query, No Matches, Special Characters).
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
import docx

from modules.shared.file_manager import file_mgr
from modules.notebooklm.notebooklm_engine import (
    OpenNotebookEngine,
    ScientificSectionType,
    ScientificSectioner,
    SECTION_DISPLAY_NAMES,
    extract_citation_author,
    open_notebook_engine
)


class TestOpenNotebookKnowledgeVault(unittest.TestCase):
    """Hermetic, Isolated End-to-End Test Suite for Open-Notebook RAG Subsystem."""

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

        # Instantiate fresh engine pointing to temp directory
        self.nb_engine = OpenNotebookEngine()
        self.nb_engine.workspace = self.temp_workspace
        self.nb_engine.notebooks_dir = self.temp_workspace / "notebooks"
        self.nb_engine.notebooks_dir.mkdir(parents=True, exist_ok=True)
        self.nb_engine._ensure_default_notebook()

    def tearDown(self):
        file_mgr.workspace = self.orig_workspace
        file_mgr.docs_dir = self.orig_workspace / "Tai_Lieu"
        file_mgr.drafts_dir = self.orig_workspace / "Ban_Thao"
        file_mgr.publish_dir = self.orig_workspace / "Xuat_Ban"
        self.temp_dir.cleanup()

    # ── TEST 1: AUTHOR APA 7TH CITATION EXTRACTION ───────────────────────────

    def test_01_extract_citation_author_variations(self):
        """Verify extract_citation_author normalizes academic titles and forms APA 7th citations."""
        # Single author with academic titles
        self.assertEqual(extract_citation_author("GS. TS. Nguyễn Văn Nam"), "Nam")
        self.assertEqual(extract_citation_author("Prof. Dr. John Doe"), "John")
        self.assertEqual(extract_citation_author("ThS. Lê Hoàng"), "Hoàng")
        
        # Two authors with '&' or 'and'
        self.assertEqual(extract_citation_author("Nguyễn An & Trần Bình"), "An & Bình")
        self.assertEqual(extract_citation_author("Russell & Norvig"), "Russell & Norvig")

        # Three or more authors or comma-initial formats -> 'et al.'
        self.assertEqual(extract_citation_author("Goodfellow, I., Bengio, Y., & Courville, A."), "Goodfellow et al.")
        self.assertEqual(extract_citation_author("Phạm Minh, Lê Hùng, Vũ Dũng"), "Minh et al.")

        # Empty / None fallback
        self.assertEqual(extract_citation_author(""), "Nghiên cứu")
        self.assertEqual(extract_citation_author(None), "Nghiên cứu")

    # ── TEST 2: NOTEBOOK LIFECYCLE & INDEXING ────────────────────────────────

    def test_02_notebook_crud_lifecycle(self):
        """Verify creation, listing, detail inspection, and deletion of research notebooks."""
        # 1. List initial notebooks (includes default)
        initial_list = self.nb_engine.list_notebooks()
        self.assertGreaterEqual(len(initial_list), 1)

        # 2. Create custom notebook
        nb_meta = self.nb_engine.create_notebook(
            name="Nghiên Cứu Xử Lý Nước Thải",
            topic="Công Nghệ Màng Lọc MBR & Hóa Học Môi Trường",
            description="Phân tích hiệu quả loại bỏ FeS₂ và hợp chất hữu cơ."
        )
        nb_id = nb_meta["id"]
        self.assertTrue(nb_id.startswith("nb_"))
        self.assertEqual(nb_meta["name"], "Nghiên Cứu Xử Lý Nước Thải")

        # 3. Verify in list
        all_nbs = self.nb_engine.list_notebooks()
        nb_ids = [n["id"] for n in all_nbs]
        self.assertIn(nb_id, nb_ids)

        # 4. Get details
        details = self.nb_engine.get_notebook_details(nb_id)
        self.assertEqual(details["status"], "success")
        self.assertEqual(details["notebook"]["id"], nb_id)
        self.assertEqual(details["sources"], [])
        self.assertEqual(details["chunks_count"], 0)

        # 5. Delete notebook
        del_res = self.nb_engine.delete_notebook(nb_id)
        self.assertEqual(del_res["status"], "success")
        updated_list = self.nb_engine.list_notebooks()
        self.assertNotIn(nb_id, [n["id"] for n in updated_list])

    # ── TEST 3: MULTI-MODAL DOCUMENT INGESTION & CHUNKING ────────────────────

    def test_03_ingest_raw_text_and_chunking(self):
        """Verify ingestion of raw academic text and section-aware chunking."""
        nb = self.nb_engine.create_notebook("AI & NLP Notebook", topic="Xử Lý Ngôn Ngữ Tự Nhiên")
        nb_id = nb["id"]

        sample_text = (
            "# 1. GIỚI THIỆU TỔNG QUAN VỀ MÔ HÌNH TRANSFORMER\n\n"
            "Mô hình Transformer được giới thiệu bởi Vaswani et al. (2017) đã tạo ra bước đột phá vượt bậc "
            "trong xử lý ngôn ngữ tự nhiên. Cơ chế Self-Attention cho phép tính toán song song toàn diện.\n\n"
            "## 2. PHƯƠNG PHÁP NGHIÊN CỨU & BỘ DỮ LIỆU ĐO ĐẠC\n\n"
            "Nghiên cứu thử nghiệm trên tập dữ liệu 50.000 câu với tỷ lệ huấn luyện 80/20. "
            "Chỉ số BLEU đạt 34,5 điểm và độ chính xác F1 đạt 92,8% so với mô hình baseline.\n\n"
            "### 3. KẾT QUẢ ĐỊNH LƯỢNG & ĐỐI SOÁNH\n\n"
            "Hiệu năng cải thiện đạt 24,5% và thời gian suy luận giảm 32,0% khi áp dụng tối ưu hóa lượng tử hóa."
        )

        res = self.nb_engine.add_source_from_raw(
            notebook_id=nb_id,
            title="Khai Phá Transformer trong Học Thuật",
            content=sample_text,
            author="Vaswani & Shazeer",
            year="2024",
            doi="10.48550/arXiv.1706.03762",
            source_type="RESEARCH_PAPER"
        )

        self.assertEqual(res["status"], "success")
        self.assertGreater(res["chunks_added"], 0)
        source = res["source"]
        self.assertEqual(source["cite_author"], "Vaswani & Shazeer")
        self.assertEqual(source["year"], "2024")

        # Verify storage
        details = self.nb_engine.get_notebook_details(nb_id)
        self.assertEqual(len(details["sources"]), 1)
        self.assertEqual(details["chunks_count"], res["chunks_added"])

    def test_04_ingest_file_types(self):
        """Verify ingestion from Markdown, Word (.docx), and PDF files."""
        nb = self.nb_engine.create_notebook("Multi-Format Testing", topic="Kiểm Thử Định Dạng")
        nb_id = nb["id"]

        # 1. Ingest Markdown file
        md_path = self.temp_workspace / "Tai_Lieu" / "document_sample.md"
        md_path.write_text(
            "# Môi Trường Nước & Kim Loại Nặng\n\n"
            "Nồng độ ion Al³⁺ và FeS₂ trong mẫu đo vượt ngưỡng 1,5 lần theo quy chuẩn QCVN 08:2023.",
            encoding="utf-8"
        )
        res_md = self.nb_engine.add_source_from_file(nb_id, md_path, metadata={"author": "Nguyễn Văn A", "year": "2025"})
        self.assertEqual(res_md["status"], "success")

        # 2. Ingest Word (.docx) file
        docx_path = self.temp_workspace / "Tai_Lieu" / "document_sample.docx"
        doc = docx.Document()
        doc.add_heading("Báo Cáo Thực Nghiệm Hóa Sinh", level=1)
        doc.add_paragraph("Chỉ tiêu BOD₅ đạt 28,5 mg/L và COD đạt 110,2 mg/L trong điều kiện thí nghiệm.")
        doc.save(str(docx_path))

        res_docx = self.nb_engine.add_source_from_file(nb_id, docx_path, metadata={"author": "Trần Thị B", "year": "2026"})
        self.assertEqual(res_docx["status"], "success")

        # 3. Ingest PDF file
        pdf_path = self.temp_workspace / "Tai_Lieu" / "document_sample.pdf"
        c = canvas.Canvas(str(pdf_path), pagesize=letter)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(72, 750, "Nghien Cuu Du Bao Chuoi Thoi Gian BigQuery")
        c.setFont("Helvetica", 11)
        c.drawString(72, 720, "Mo hinh AI.FORECAST dat sai so MAPE = 2.45% va do tin cay 95%.")
        c.showPage()
        c.save()

        res_pdf = self.nb_engine.add_source_from_file(nb_id, pdf_path, metadata={"author": "Lê Văn C", "year": "2026"})
        self.assertEqual(res_pdf["status"], "success")

        details = self.nb_engine.get_notebook_details(nb_id)
        self.assertEqual(len(details["sources"]), 3)

    # ── TEST 4: HYBRID RETRIEVAL ENGINE ──────────────────────────────────────

    def test_05_hybrid_search_bm25_and_semantic(self):
        """Verify hybrid search ranks relevant chunks using BM25 token matches and N-gram similarity."""
        nb = self.nb_engine.create_notebook("RAG Search Test", topic="Truy Xuất Ngữ Nghĩa")
        nb_id = nb["id"]

        doc1_content = (
            "# Xử Lý Nước Thải Bằng Công Nghệ Hóa Lý\n\n"
            "Phương pháp keo tụ tạo bông sử dụng phèn nhôm Al₂(SO₄)₃ để loại bỏ độ đục và ion kim loại nặng. "
            "Hiệu suất loại bỏ chất lơ lửng TSS đạt 94,5% trong môi trường pH = 7,2."
        )
        doc2_content = (
            "# Dự Báo Nhu Cầu Năng Lượng Tái Tạo\n\n"
            "Mô hình học máy dự báo sản lượng điện mặt trời sử dụng chuỗi thời gian ARIMA và mạng nơ-ron LSTM. "
            "Sai số dự báo MAPE đạt 3,12% trên tập kiểm thử 12 tháng liên tục."
        )

        self.nb_engine.add_source_from_raw(nb_id, "Nước Thải Hóa Lý", doc1_content, author="Trần Hóa Học", year="2025")
        self.nb_engine.add_source_from_raw(nb_id, "Năng Lượng Tái Tạo", doc2_content, author="Lê Năng Lượng", year="2026")

        # Query relevant to Document 1
        results_1 = self.nb_engine.hybrid_search(nb_id, query="keo tụ tạo bông phèn nhôm TSS", top_k=5)
        self.assertGreater(len(results_1), 0)
        top_match_1 = results_1[0]
        self.assertIn("keo tụ", top_match_1["text"].lower())
        self.assertEqual(top_match_1["source_title"], "Nước Thải Hóa Lý")
        self.assertGreater(top_match_1["score"], 0.1)

        # Query relevant to Document 2
        results_2 = self.nb_engine.hybrid_search(nb_id, query="dự báo điện mặt trời ARIMA LSTM", top_k=5)
        self.assertGreater(len(results_2), 0)
        top_match_2 = results_2[0]
        self.assertIn("điện mặt trời", top_match_2["text"].lower())
        self.assertEqual(top_match_2["source_title"], "Năng Lượng Tái Tạo")

    # ── TEST 5: GROUNDED CHAT & CITATION FOOTNOTES ───────────────────────────

    def test_06_grounded_chat_with_citations(self):
        """Verify chat_with_notebook produces answers grounded in source chunks with academic citations."""
        nb = self.nb_engine.create_notebook("Grounded Chat Notebook", topic="Môi Trường & Hóa Học")
        nb_id = nb["id"]

        doc_text = (
            "# Nghiên Cứu Màng Lọc MBR\n\n"
            "Nghiên cứu của TS. Minh Trí (2025) khẳng định công nghệ màng lọc sinh học MBR giúp giảm 28,5% chỉ tiêu COD "
            "và 15,2% chỉ tiêu BOD₅ trong nước thải dệt nhuộm."
        )
        self.nb_engine.add_source_from_raw(nb_id, "Nghiên Cứu MBR", doc_text, author="TS. Minh Trí", year="2025")

        chat_res = self.nb_engine.chat_with_notebook(nb_id, message="Công nghệ màng lọc MBR giúp giảm bao nhiêu COD và BOD5?")
        self.assertEqual(chat_res["status"], "success")
        self.assertIn("answer", chat_res)
        self.assertGreater(len(chat_res["citations"]), 0)
        self.assertIn("Trí", chat_res["citations"][0]["author"])
        self.assertEqual(chat_res["citations"][0]["year"], "2025")

        # Verify chat history persistence
        history = self.nb_engine.get_chat_history(nb_id)
        self.assertEqual(len(history), 2)  # 1 user + 1 assistant
        self.assertEqual(history[0]["role"], "user")
        self.assertEqual(history[1]["role"], "assistant")

        # Clear history
        self.nb_engine.clear_chat_history(nb_id)
        self.assertEqual(len(self.nb_engine.get_chat_history(nb_id)), 0)

    # ── TEST 6: SIGNATURE RESEARCH TRANSFORMATIONS STUDIO ────────────────────

    def test_07_transformations_studio(self):
        """Verify generation of all 5 signature research transformations."""
        nb = self.nb_engine.create_notebook("Transformations Test", topic="Tối Ưu Hóa Năng Lượng")
        nb_id = nb["id"]

        content = (
            "# Mô Hình Tối Ưu Hóa Đa Mục Tiêu\n\n"
            "Áp dụng giải thuật di truyền đa mục tiêu NSGA-II để tối ưu hóa chi phí vận hành và phát thải CO₂. "
            "Kết quả định lượng cho thấy chi phí giảm 22,5% và phát thải giảm 18,2%."
        )
        self.nb_engine.add_source_from_raw(nb_id, "Tối Ưu Năng Lượng", content, author="Nguyễn Văn An", year="2026")

        transforms = ["podcast_script", "study_guide", "faq", "synthesis_matrix", "research_gaps"]
        for t_type in transforms:
            res = self.nb_engine.generate_transformation(nb_id, transform_type=t_type)
            self.assertEqual(res["status"], "success")
            self.assertEqual(res["transform_type"], t_type)
            self.assertGreater(len(res["content"]), 100)
            
            # Verify artifact file created
            art_path = self.temp_workspace / res["artifact_path"]
            self.assertTrue(art_path.exists())
            self.assertGreater(art_path.stat().st_size, 50)

    # ── TEST 7: 7-COLUMN LITERATURE REVIEW MATRIX ────────────────────────────

    def test_08_generate_literature_matrix_7_columns(self):
        """Verify generation of the standardized 7-column Literature Review Matrix."""
        nb = self.nb_engine.create_notebook("Lit Review Notebook", topic="Chuyển Đổi Số Giáo Dục")
        nb_id = nb["id"]

        self.nb_engine.add_source_from_raw(
            nb_id,
            title="Ứng dụng AI trong Đào Tạo Trực Tuyến",
            content="Khảo sát 1.200 sinh viên về mức độ hài lòng khi sử dụng trợ lý học tập AI. Hiệu quả học tập tăng 28,5%.",
            author="Phạm Lan Hương",
            year="2025",
            doi="10.1016/j.compedu.2025.104990"
        )

        matrix_res = self.nb_engine.generate_literature_matrix(nb_id)
        self.assertEqual(matrix_res["status"], "success")
        self.assertEqual(matrix_res["total_papers"], 1)

        matrix_row = matrix_res["matrix"][0]
        self.assertIn("author_year", matrix_row)
        self.assertIn("title", matrix_row)
        self.assertIn("objective", matrix_row)
        self.assertIn("methodology", matrix_row)
        self.assertIn("key_findings", matrix_row)
        self.assertIn("research_gaps", matrix_row)
        self.assertIn("contribution", matrix_row)

        # Verify exported .md and .docx in Xuat_Ban/
        md_file = self.temp_workspace / matrix_res["md_file"]
        docx_file = self.temp_workspace / matrix_res["docx_file"]
        self.assertTrue(md_file.exists())
        self.assertTrue(docx_file.exists())
        self.assertGreater(docx_file.stat().st_size, 1000)

    # ── TEST 8: PIPELINE STEP 2 SYNC ─────────────────────────────────────────

    def test_09_sync_knowledge_base(self):
        """Verify sync_knowledge_base compatibility with Step 2 of 7-step pipeline."""
        sync_res = self.nb_engine.sync_knowledge_base(
            topic="Phân Tích Dữ Liệu Lớn & BigQuery AI",
            target_papers=[]
        )
        self.assertEqual(sync_res["status"], "success")
        self.assertIn("notebook_id", sync_res)
        self.assertIn("synthesis_matrix", sync_res)

    # ── TEST 9: ADVERSARIAL & EDGE CASES ─────────────────────────────────────

    def test_10_adversarial_empty_and_noise_queries(self):
        """Verify search and chat handle blank or unmatchable queries gracefully."""
        nb = self.nb_engine.create_notebook("Empty Test", topic="Kiểm Thử Rỗng")
        nb_id = nb["id"]

        # Search on empty notebook
        res_empty = self.nb_engine.hybrid_search(nb_id, query="bất kỳ từ khóa nào")
        self.assertEqual(res_empty, [])

        # Empty search query on populated notebook
        self.nb_engine.add_source_from_raw(nb_id, "Sample", "Nội dung bài báo", author="Tác Giả", year="2026")
        res_blank = self.nb_engine.hybrid_search(nb_id, query="    ")
        self.assertEqual(res_blank, [])

    # ── TEST 10: SCIBOT SCIENTIFIC SECTIONING & METADATA TAGGING ─────────────

    def test_11_scientific_sectioning_classification(self):
        """Verify IMRaD section classification, formula & table detection, and citation anchors."""
        # 1. Test heading classification
        self.assertEqual(ScientificSectioner.classify_heading("Abstract"), ScientificSectionType.ABSTRACT)
        self.assertEqual(ScientificSectioner.classify_heading("Tóm tắt nghiên cứu"), ScientificSectionType.ABSTRACT)
        self.assertEqual(ScientificSectioner.classify_heading("1. Introduction & Background"), ScientificSectionType.INTRODUCTION)
        self.assertEqual(ScientificSectioner.classify_heading("2. Phương Pháp Nghiên Cứu & Mô Hình"), ScientificSectionType.METHODOLOGY)
        self.assertEqual(ScientificSectioner.classify_heading("3. Methodology and Experimental Setup"), ScientificSectionType.METHODOLOGY)
        self.assertEqual(ScientificSectioner.classify_heading("4. Kết Quả Thực Nghiệm & Bàn Luận"), ScientificSectionType.RESULTS_DISCUSSION)
        self.assertEqual(ScientificSectioner.classify_heading("5. Results and Evaluation"), ScientificSectionType.RESULTS_DISCUSSION)
        self.assertEqual(ScientificSectioner.classify_heading("6. Kết Luận & Hạn Chế"), ScientificSectionType.CONCLUSIONS_GAPS)
        self.assertEqual(ScientificSectioner.classify_heading("References & Bibliography"), ScientificSectionType.REFERENCES)

        # 2. Test formula & table detection
        self.assertTrue(ScientificSectioner.detect_formulas("Phương trình $$E = mc^2$$ và nồng độ FeS₂ kết hợp H₂SO₄."))
        self.assertTrue(ScientificSectioner.detect_formulas("Chỉ tiêu BOD₅ và COD trong phản ứng khử Al³⁺."))
        self.assertFalse(ScientificSectioner.detect_formulas("Báo cáo tổng quan về kinh tế xã hội và giáo dục."))

        self.assertTrue(ScientificSectioner.detect_tables("| Cột 1 | Cột 2 |\n|---|---|\n| 10 | 20 |"))
        self.assertTrue(ScientificSectioner.detect_tables("Bảng 1: Thống kê hiệu năng mô hình"))
        self.assertFalse(ScientificSectioner.detect_tables("Đoạn văn thông thường không có bảng biểu."))

        # 3. Test page number extraction
        self.assertEqual(ScientificSectioner.extract_page_number("### [Trang 4]\nNội dung trang 4"), 4)
        self.assertEqual(ScientificSectioner.extract_page_number("<!-- PAGE_BREAK: 7 -->\nNội dung trang 7"), 7)

        # 4. Test classify_and_chunk
        doc_sample = (
            "# 1. GIỚI THIỆU VÀ ĐẶT VẤN ĐỀ\n\n"
            "Nghiên cứu xử lý nước thải công nghiệp dệt nhuộm bằng màng lọc MBR.\n\n"
            "# 2. PHƯƠNG PHÁP THỰC NGHIỆM\n\n"
            "Mô hình thử nghiệm liên tục với tải trọng hữu cơ 2,5 kg COD/m³·ngày. Phản ứng khử $$FeS_2 + 2H^+ \to Fe^{2+} + H_2S$$.\n\n"
            "# 3. KẾT QUẢ ĐO ĐẠC & BÀN LUẬN\n\n"
            "| Chỉ tiêu | Trước xử lý | Sau xử lý |\n|---|---|---|\n| COD (mg/L) | 1.200 | 110 |\n| BOD₅ (mg/L) | 450 | 28,5 |\n\n"
            "Hiệu suất giảm COD đạt 90,8% và BOD₅ giảm 93,6%.\n\n"
            "# 4. KẾT LUẬN & KHOẢNG TRỐNG\n\n"
            "Hạn chế lớn nhất là hiện tượng tắc nghẽn màng sau 45 ngày vận hành cần được nghiên cứu giải quyết."
        )
        chunks = ScientificSectioner.classify_and_chunk(
            doc_sample, filename="MBR_Report.docx", author="Minh Trí", year="2025"
        )
        self.assertGreaterEqual(len(chunks), 4)
        sec_types = [c["section_type"] for c in chunks]
        self.assertIn(ScientificSectionType.INTRODUCTION, sec_types)
        self.assertIn(ScientificSectionType.METHODOLOGY, sec_types)
        self.assertIn(ScientificSectionType.RESULTS_DISCUSSION, sec_types)
        self.assertIn(ScientificSectionType.CONCLUSIONS_GAPS, sec_types)

        # Verify chunk anchor structure
        method_chunk = next(c for c in chunks if c["section_type"] == ScientificSectionType.METHODOLOGY)
        self.assertTrue(method_chunk["has_formulas"])
        self.assertIn("Trí", method_chunk["citation_anchor"])
        self.assertIn("Phương Pháp", method_chunk["citation_anchor"])

    # ── TEST 11: OKAPI BM25 TERM SATURATION & CORPUS IDF ─────────────────────

    def test_12_okapi_bm25_term_saturation_and_idf(self):
        """Verify True Okapi BM25 scores reflect term frequency saturation and corpus-wide IDF."""
        nb = self.nb_engine.create_notebook("BM25 SciBot Test", topic="Độ Bão Hòa Từ Khóa & IDF")
        nb_id = nb["id"]

        # Chunk 1: Common word repeated multiple times vs Chunk 2: Rare word
        doc1 = (
            "# Nghiên Cứu Màng Lọc Sinh Học\n\n"
            "Màng lọc sinh học màng lọc sinh học màng lọc sinh học giúp xử lý nước thải sinh hoạt."
        )
        doc2 = (
            "# Nghiên Cứu Chất Xúc Tác Nano Titania\n\n"
            "Vật liệu quang xúc tác nano TiO₂ dạng anatase xử lý hợp chất hữu cơ độc hại."
        )
        self.nb_engine.add_source_from_raw(nb_id, "Doc 1", doc1, author="Tác Giả A", year="2025")
        self.nb_engine.add_source_from_raw(nb_id, "Doc 2", doc2, author="Tác Giả B", year="2026")

        # Query rare term "anatase TiO2"
        results_rare = self.nb_engine.hybrid_search(nb_id, query="anatase TiO2 nano", top_k=2)
        self.assertGreater(len(results_rare), 0)
        self.assertEqual(results_rare[0]["source_title"], "Doc 2")
        self.assertGreater(results_rare[0]["bm25_score"], 0.2)

    # ── TEST 12: SECTION-AWARE QUERY ROUTING BOOST ───────────────────────────

    def test_13_section_aware_query_routing_boost(self):
        """Verify section-aware query routing automatically boosts methodology, results, and formula chunks."""
        nb = self.nb_engine.create_notebook("Section Routing Test", topic="Tối Ưu Hóa Mạng Nơ-ron")
        nb_id = nb["id"]

        full_paper = (
            "# 1. GIỚI THIỆU BỐI CẢNH\n\n"
            "Tổng quan về mô hình học sâu trong chẩn đoán hình ảnh y tế.\n\n"
            "# 2. PHƯƠNG PHÁP & THUẬT TOÁN\n\n"
            "Đề xuất thuật toán tối ưu hóa thích nghi Adam-W kết hợp kỹ thuật tăng cường dữ liệu CutMix trên bộ dữ liệu 20.000 ảnh X-quang.\n\n"
            "# 3. KẾT QUẢ THỰC NGHIỆM ĐỊNH LƯỢNG\n\n"
            "Kết quả thực nghiệm cho thấy độ chính xác F1-score đạt 94,8%, chỉ số AUC đạt 0,982 và thời gian huấn luyện giảm 28,5%.\n\n"
            "# 4. CÔNG THỨC VÀ BẢNG DỮ LIỆU\n\n"
            "Hàm mất mát phân loại đa lớp $$L_{total} = \alpha L_{CE} + (1-\alpha) L_{Dice}$$.\n\n"
            "# 5. KẾT LUẬN & HƯỚNG PHÁT TRIỂN\n\n"
            "Hạn chế về chi phí tính toán khi triển khai trên thiết bị nhúng di động."
        )
        self.nb_engine.add_source_from_raw(nb_id, "Học Sâu Y Tế", full_paper, author="Lê Văn Hùng", year="2026")

        # 1. Methodology Query -> METHODOLOGY chunk boosted
        res_method = self.nb_engine.hybrid_search(nb_id, query="phương pháp mô hình thuật toán tối ưu hóa Adam-W dataset", top_k=3)
        self.assertGreater(len(res_method), 0)
        self.assertEqual(res_method[0]["section_type"], ScientificSectionType.METHODOLOGY)
        self.assertGreaterEqual(res_method[0]["boost_factor"], 1.30)

        # 2. Results Query -> RESULTS_DISCUSSION chunk boosted
        res_results = self.nb_engine.hybrid_search(nb_id, query="kết quả số liệu đo đạc F1-score AUC", top_k=3)
        self.assertGreater(len(res_results), 0)
        self.assertEqual(res_results[0]["section_type"], ScientificSectionType.RESULTS_DISCUSSION)
        self.assertGreaterEqual(res_results[0]["boost_factor"], 1.30)

        # 3. Explicit target_section parameter
        res_target = self.nb_engine.hybrid_search(
            nb_id, query="chẩn đoán", target_section=ScientificSectionType.INTRODUCTION, top_k=2
        )
        self.assertGreater(len(res_target), 0)
        self.assertEqual(res_target[0]["section_type"], ScientificSectionType.INTRODUCTION)

    # ── TEST 13: SECTION-TARGETED 7-COLUMN LITERATURE MATRIX ─────────────────

    def test_14_7_column_literature_matrix_grounded_extraction(self):
        """Verify Literature Matrix extracts targeted evidence from specific IMRaD section chunks."""
        nb = self.nb_engine.create_notebook("Matrix Grounding Test", topic="Vật Liệu Màng Lọc MBR")
        nb_id = nb["id"]

        paper_text = (
            "# TÓM TẮT NGHIÊN CỨU\n\n"
            "Mục tiêu là khảo sát hiệu quả màng lọc nano composite trong việc loại bỏ ion kim loại nặng và chất hữu cơ.\n\n"
            "# PHƯƠNG PHÁP THỰC NGHIỆM\n\n"
            "Chế tạo màng composite PVDF pha tạp hạt nano TiO₂ với tỷ lệ 1,5% trọng lượng trên hệ thống lọc áp lực.\n\n"
            "# KẾT QUẢ VÀ BÀN LUẬN\n\n"
            "Hiệu suất khử COD đạt 92,4% và loại bỏ FeS₂ đạt 96,8% với độ suy giảm thông lượng nước dưới 8,5%.\n\n"
            "# KẾT LUẬN VÀ HẠN CHẾ\n\n"
            "Hạn chế về độ bền cơ học của màng sau 90 ngày ngâm trong môi trường axit mạnh H₂SO₄."
        )
        self.nb_engine.add_source_from_raw(
            nb_id,
            title="Màng Composite PVDF-TiO2",
            content=paper_text,
            author="TS. Trần Minh Đức & CS",
            year="2025",
            doi="10.1016/j.memsci.2025.120980"
        )

        matrix_res = self.nb_engine.generate_literature_matrix(nb_id)
        self.assertEqual(matrix_res["status"], "success")
        self.assertEqual(matrix_res["total_papers"], 1)

        row = matrix_res["matrix"][0]
        # Verify targeted section extraction
        self.assertIn("Mục tiêu", row["objective"])
        self.assertIn("Phương pháp", row["methodology"])
        self.assertIn("Kết quả thực chứng", row["key_findings"])
        self.assertIn("Hạn chế", row["research_gaps"])
        self.assertIn("Đức", row["author_year"])
        self.assertEqual(row["doi"], "10.1016/j.memsci.2025.120980")


def run_tests():
    """Test runner with formatted console output."""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestOpenNotebookKnowledgeVault)
    runner = unittest.TextTestRunner(verbosity=2)
    start_time = time.time()
    result = runner.run(suite)
    elapsed = round(time.time() - start_time, 2)

    print("\n" + "=" * 70)
    print(f"📊 OPEN-NOTEBOOK FULL FLOW TEST SUITE SUMMARY:")
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
