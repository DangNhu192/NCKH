# tests/test_document_evidence_extractor.py
"""
WEB SUPER v3.2 / v2.0 - Test Suite: Document-by-Document Evidence Extractor & Empirical Database
Kiểm thử toàn diện tính năng:
1. Bóc tách dữ liệu theo từng tài liệu được cung cấp (PDF, DOCX, MD).
2. Trích dẫn viễn dẫn chuẩn APA 7th (in-text, narrative, bibliography, pinpoint page & section).
3. Thống kê định lượng số lượng theo từng tài liệu và tổng thể corpus.
4. Quản trị và lưu trữ Cơ sở dữ liệu Thực chứng (.json, .docx, .md, .ris, .bib).
5. Liên thông trực tiếp sang Trình soạn thảo Học thuật 2-File (Tệp A & Tệp B).
6. Kiểm tra các API Router /api/evidence-db/*.
"""

import os
import sys
import io
import json
import pytest
from pathlib import Path
from docx import Document

# Ensure root directory is on sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi.testclient import TestClient
from server import app
from modules.pipeline.document_extractor_engine import document_evidence_extractor, DocumentEvidenceExtractor
from modules.academic_writer.academic_writer_engine import academic_writer
from modules.shared.file_manager import file_mgr
from modules.auth.auth_service import create_jwt_token


@pytest.fixture
def auth_headers():
    token = create_jwt_token({"email": "admin@websuper.edu.vn", "role": "admin", "status": "active", "plan": "enterprise"})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def sample_docx_bytes():
    """Tạo tệp Word .docx thực tế trong bộ nhớ với các đề mục, bảng số liệu và trích dẫn chuẩn."""
    doc = Document()
    doc.add_heading("Deep Learning and Neural Transformer Scalability", level=1)
    
    p_meta = doc.add_paragraph()
    p_meta.add_run("Tác giả: LeCun, Y., Bengio, Y., & Hinton, G. (2015)\n")
    p_meta.add_run("Tạp chí: Nature, 521(7553), 436-444. DOI: 10.1038/nature14539\n")
    
    doc.add_heading("1. Giới thiệu và Mục tiêu Nghiên cứu", level=2)
    doc.add_paragraph(
        "Mục tiêu nghiên cứu là khám phá khả năng tự học biểu diễn đa tầng của mô hình Deep Learning. "
        "Deep learning allows computational models that are composed of multiple processing layers to learn representations."
    )
    
    doc.add_heading("2. Phương pháp Thực nghiệm & Kết quả Định lượng", level=2)
    doc.add_paragraph(
        "Phương pháp nghiên cứu sử dụng thuật toán lan truyền ngược (backpropagation) trên tập dữ liệu ImageNet gồm 1.200.000 hình ảnh. "
        "The convolutional network achieves a top-5 error rate of 15.3%, significantly outperforming the previous state-of-the-art of 26.2%."
    )
    
    # Bảng số liệu thực tế
    tbl = doc.add_table(rows=3, cols=3)
    hdr_cells = tbl.rows[0].cells
    hdr_cells[0].text = "Mô hình"
    hdr_cells[1].text = "Độ chính xác Top-1 (%)"
    hdr_cells[2].text = "Thời gian huấn luyện (giờ)"
    
    r1 = tbl.rows[1].cells
    r1[0].text = "Baseline SVM"
    r1[1].text = "73,8%"
    r1[2].text = "48,5"
    
    r2 = tbl.rows[2].cells
    r2[0].text = "Deep CNN"
    r2[1].text = "84,7%"
    r2[2].text = "12,0"
    
    doc.add_heading("3. Hạn chế và Khoảng trống Nghiên cứu", level=2)
    doc.add_paragraph(
        "Một hạn chế then chốt là chi phí tính toán phần cứng GPU đòi hỏi rất cao và mô hình dễ bị tấn công bởi dữ liệu nhiễu. "
        "Hướng nghiên cứu tương lai cần tập trung vào học không giám sát (unsupervised learning) và giải thích tính đóng thùng đen."
    )
    
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


@pytest.fixture
def sample_md_bytes():
    """Tạo nội dung Markdown mẫu cho một bài báo thứ 2."""
    md_text = (
        "# Attention Is All You Need\n\n"
        "Tác giả: Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., Kaiser, Ł., & Polosukhin, I.\n"
        "Năm: 2017\n"
        "Tạp chí: Advances in Neural Information Processing Systems\n"
        "DOI: 10.48550/arXiv.1706.03762\n\n"
        "## 1. Abstract & Objective\n"
        "We propose a new simple network architecture, the Transformer, based solely on attention mechanisms.\n"
        "The objective is to dispense with recurrence and convolutions entirely for sequence modeling.\n\n"
        "## 2. Experimental Results & Performance\n"
        "On the WMT 2014 English-to-German translation task, the big transformer model achieves 28.4 BLEU, "
        "improving over the existing best results by over 2.0 BLEU points. "
        "Training required only 3.5 days on 8 P100 GPUs.\n\n"
        "## 3. Limitations & Future Work\n"
        "A major limitation is the quadratic memory footprint O(N^2) with long contexts. "
        "Future research must evaluate linear attention and multi-modal scaling."
    )
    return md_text.encode("utf-8")


# ── TEST CASES ───────────────────────────────────────────────────────────────

def test_parse_document_pages_and_sections(sample_docx_bytes, sample_md_bytes):
    """Kiểm tra khả năng phân rã trang, phân mục và bóc tách bảng từ DOCX và MD."""
    extractor = DocumentEvidenceExtractor()
    
    # 1. Kiểm tra DOCX
    docx_pages = extractor.parse_document_pages_and_sections("lecun_2015_nature.docx", sample_docx_bytes)
    assert len(docx_pages) >= 1
    assert "text" in docx_pages[0]
    assert len(docx_pages[0]["text"]) > 100
    assert len(docx_pages[0]["tables"]) >= 1
    assert docx_pages[0]["tables"][0]["rows"][0] == ["Mô hình", "Độ chính xác Top-1 (%)", "Thời gian huấn luyện (giờ)"]
    
    # 2. Kiểm tra MD
    md_pages = extractor.parse_document_pages_and_sections("vaswani_2017_attention.md", sample_md_bytes)
    assert len(md_pages) >= 1
    assert any("Transformer" in p["text"] for p in md_pages)


def test_metadata_and_apa_citation_generation(sample_docx_bytes, sample_md_bytes):
    """Kiểm tra trích xuất metadata và kiến tạo trích dẫn chuẩn APA 7th."""
    extractor = DocumentEvidenceExtractor()
    pages_docx = extractor.parse_document_pages_and_sections("lecun_2015_nature.docx", sample_docx_bytes)
    meta = extractor.extract_document_metadata_and_citations("lecun_2015_nature.docx", pages_docx)
    
    assert "LeCun" in meta["first_author"] or "LeCun" in meta["author"]
    assert meta["year"] == "2015"
    assert "10.1038/nature14539" in meta["doi"]
    # APA in-text parenthetical: (LeCun et al., 2015)
    assert "(LeCun" in meta["apa_in_text"]
    assert "2015" in meta["apa_in_text"]
    # APA narrative: LeCun et al. (2015)
    assert "LeCun" in meta["apa_narrative"]
    assert "(2015)" in meta["apa_narrative"]
    # APA reference entry contains DOI
    assert "https://doi.org/10.1038/nature14539" in meta["apa_reference_entry"]


def test_deep_evidence_extraction_categorization_and_pinpoint(sample_docx_bytes):
    """Kiểm tra bóc tách chuyên sâu 5 nhóm luận cứ với viễn dẫn pinpoint APA."""
    extractor = DocumentEvidenceExtractor()
    pages = extractor.parse_document_pages_and_sections("lecun_2015_nature.docx", sample_docx_bytes)
    meta = extractor.extract_document_metadata_and_citations("lecun_2015_nature.docx", pages)
    doc_res = extractor.extract_document_deep("lecun_2015_nature.docx", pages, meta)
    evidence_items = doc_res["extracted_items"]
    assert len(evidence_items) >= 3
    categories = {it["category"] for it in evidence_items}
    # Phải có ít nhất các nhóm chính
    assert any(c in categories for c in ["QUANTITATIVE_RESULT", "METHODOLOGY", "OBJECTIVE", "LIMITATION", "RESEARCH_GAP"])
    
    # Kiểm tra cấu trúc từng item
    for it in evidence_items:
        assert "apa_pinpoint_citation" in it
        assert "p." in it["apa_pinpoint_citation"] or "Trang" in it["pinpoint_location"]
        assert it["original_verbatim_excerpt"] != ""
        assert it["vietnamese_translation"] != ""
        assert "claim_statement" in it
        assert it["confidence_or_uncertainty"] != ""


def test_document_statistics_and_corpus_summary(sample_docx_bytes, sample_md_bytes):
    """Kiểm tra tính toán số lượng/thống kê theo từng tài liệu và toàn bộ corpus."""
    extractor = DocumentEvidenceExtractor()
    
    docs_input = [
        {"filename": "lecun_2015_nature.docx", "content_bytes": sample_docx_bytes},
        {"filename": "vaswani_2017_attention.md", "content_bytes": sample_md_bytes}
    ]
    
    db_result = extractor.build_empirical_database(
        topic="Mô hình Học sâu và Kiến trúc Transformer",
        provided_docs=docs_input,
        save_docx_report=True
    )
    
    # 1. Kiểm tra thống kê tổng thể corpus
    stats = db_result["corpus_statistics"]
    assert stats["total_documents_analyzed"] == 2
    assert stats["total_claims_extracted"] >= 4
    assert stats["total_pages_scanned"] >= 2
    assert stats["total_tables_extracted"] >= 1
    assert stats["doi_coverage_percentage"] == "100.0%"
    assert stats["overall_corpus_quality"] == "HIGH"
    
    # 2. Kiểm tra thống kê theo từng tài liệu
    doc_records = db_result["documents"]
    assert len(doc_records) == 2
    for doc_rec in doc_records:
        doc_stats = doc_rec["document_statistics"]
        assert doc_stats["page_count"] >= 1
        assert doc_stats["total_words"] > 50
        assert doc_stats["total_claims_extracted"] >= 2
        assert doc_stats["extraction_quality"] in ["HIGH", "MEDIUM"]


def test_empirical_database_persistence_and_docx_report(sample_docx_bytes, sample_md_bytes):
    """Kiểm tra lưu trữ cơ sở dữ liệu thực chứng vào đĩa và tạo báo cáo Word .docx chuẩn A4."""
    extractor = DocumentEvidenceExtractor()
    docs_input = [
        {"filename": "lecun_2015_nature.docx", "content_bytes": sample_docx_bytes},
        {"filename": "vaswani_2017_attention.md", "content_bytes": sample_md_bytes}
    ]
    
    db_result = extractor.build_empirical_database(
        topic="Học Sâu & Transformer",
        provided_docs=docs_input,
        save_docx_report=True
    )
    
    db_id = db_result["database_id"]
    # 1. Kiểm tra tệp JSON
    json_path = file_mgr.workspace / f"Evidence_Database/{db_id}.json"
    latest_json = file_mgr.workspace / "Evidence_Database/latest_database.json"
    assert json_path.exists()
    assert latest_json.exists()
    
    with open(json_path, "r", encoding="utf-8") as f:
        saved_data = json.load(f)
    assert saved_data["database_id"] == db_id
    assert len(saved_data["documents"]) == 2
    
    # 2. Kiểm tra tệp Word .docx
    docx_rel = db_result.get("report_docx", {}).get("rel_path")
    assert docx_rel is not None
    docx_path = file_mgr.workspace / docx_rel
    assert docx_path.exists()
    
    # Đọc lại file docx để xác minh cấu trúc DOM
    doc_opened = Document(docx_path)
    assert len(doc_opened.paragraphs) > 10
    assert len(doc_opened.tables) >= 2  # Bảng scorecard + bảng ma trận thực chứng
    
    # 3. Kiểm tra tệp Markdown
    md_rel = db_result.get("report_md", {}).get("rel_path")
    assert md_rel is not None
    assert (file_mgr.workspace / md_rel).exists()
    
    # 4. Kiểm tra thư viện Zotero (.ris và .bib)
    ris_rel = db_result.get("zotero_libraries", {}).get("file_ris", {}).get("rel_path")
    bib_rel = db_result.get("zotero_libraries", {}).get("file_bib", {}).get("rel_path")
    assert ris_rel is not None and (file_mgr.workspace / ris_rel).exists()
    assert bib_rel is not None and (file_mgr.workspace / bib_rel).exists()


def test_downstream_feeder_to_academic_writer(sample_docx_bytes, sample_md_bytes):
    """Kiểm tra liên thông Cơ sở dữ liệu Thực chứng sang Academic Writer (Ma trận 6 cột File B & Khối chứng cứ File A)."""
    extractor = DocumentEvidenceExtractor()
    docs_input = [
        {"filename": "lecun_2015_nature.docx", "content_bytes": sample_docx_bytes},
        {"filename": "vaswani_2017_attention.md", "content_bytes": sample_md_bytes}
    ]
    
    db_result = extractor.build_empirical_database(
        topic="Khảo sát Thực nghiệm Học Sâu",
        provided_docs=docs_input,
        save_docx_report=False
    )
    
    # 1. Thử nghiệm feeder sang bảng 6 cột
    matrix_rows = extractor.feed_database_to_2file_matrix(db_result)
    assert len(matrix_rows) >= 4
    for r in matrix_rows:
        assert "stt" in r
        assert "claim" in r
        assert "author_year" in r
        assert "original_quote" in r
        assert "vietnamese_translation" in r
        assert "page" in r
        
    # 2. Thử nghiệm feeder sang khối văn bản File A
    evidence_block = extractor.feed_database_to_writer_evidence_block(db_result)
    assert "KHO DỮ LIỆU THỰC CHỨNG" in evidence_block
    assert len(evidence_block.splitlines()) >= 3

    # 3. Thử nghiệm gọi academic_writer.generate_2_files với evidence_database tích hợp
    writer_res = academic_writer.generate_2_files(
        topic="Khảo sát Thực nghiệm Học Sâu",
        author_name="GS. Nghiên cứu sinh",
        paper_type="Báo cáo khoa học",
        target_words=1000,
        target_pages=4,
        evidence_database=db_result
    )
    
    assert "file_a" in writer_res
    assert "file_b" in writer_res
    assert writer_res["file_a"]["docx"].endswith(".docx")
    assert writer_res["file_b"]["docx"].endswith(".docx")
    assert (file_mgr.workspace / writer_res["file_a"]["rel_path"]).exists()
    assert (file_mgr.workspace / writer_res["file_b"]["rel_path"]).exists()


def test_api_router_extract_and_feed(client, auth_headers, sample_docx_bytes):
    """Kiểm tra toàn diện các API Router /api/evidence-db/* thông qua FastAPI TestClient."""
    import base64
    b64_content = base64.b64encode(sample_docx_bytes).decode("utf-8")
    
    # 1. API: POST /api/evidence-db/extract-provided-documents
    resp_extract = client.post(
        "/api/evidence-db/extract-provided-documents",
        headers=auth_headers,
        json={
            "topic": "Học sâu và Biểu diễn Đa tầng",
            "documents": [
                {
                    "filename": "lecun_2015_nature_test.docx",
                    "content_base64": b64_content
                }
            ],
            "save_docx_report": True
        }
    )
    assert resp_extract.status_code == 200
    extract_data = resp_extract.json()
    assert "database_id" in extract_data
    db_id = extract_data["database_id"]
    assert extract_data["corpus_statistics"]["total_documents_analyzed"] == 1
    assert extract_data["corpus_statistics"]["total_claims_extracted"] >= 2
    
    # 2. API: GET /api/evidence-db/list
    resp_list = client.get("/api/evidence-db/list", headers=auth_headers)
    assert resp_list.status_code == 200
    list_data = resp_list.json()
    assert list_data["total"] >= 1
    assert any(d["database_id"] == db_id for d in list_data["databases"])
    
    # 3. API: GET /api/evidence-db/{db_id}
    resp_detail = client.get(f"/api/evidence-db/{db_id}", headers=auth_headers)
    assert resp_detail.status_code == 200
    detail_data = resp_detail.json()
    assert detail_data["database_id"] == db_id
    assert len(detail_data["documents"]) == 1
    
    # 4. API: GET /api/evidence-db/{db_id}/download-docx
    resp_dl = client.get(f"/api/evidence-db/{db_id}/download-docx", headers=auth_headers)
    assert resp_dl.status_code == 200
    assert resp_dl.headers["content-type"] == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    assert len(resp_dl.content) > 1000
    
    # 5. API: POST /api/evidence-db/feed-to-writer
    resp_feed = client.post(
        "/api/evidence-db/feed-to-writer",
        headers=auth_headers,
        json={
            "database_id": db_id,
            "topic": "Học sâu và Biểu diễn Đa tầng",
            "author_name": "TS. Kiểm thử viên",
            "target_words": 1000,
            "target_pages": 4
        }
    )
    assert resp_feed.status_code == 200
    feed_data = resp_feed.json()
    assert feed_data["status"] == "success"
    assert "writer_result" in feed_data
    assert "file_a" in feed_data["writer_result"]
    assert "file_b" in feed_data["writer_result"]
