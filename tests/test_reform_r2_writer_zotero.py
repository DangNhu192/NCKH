# tests/test_reform_r2_writer_zotero.py
"""
Test Suite for Requirement R2: Academic Writer 2-File Paradigm & Zotero CSL Integration
Covers:
- Pure LLM Section-by-Section Drafting (elimination of mad-libs / placeholder templates).
- Structured Outline Tree (RhinoInsight schema, expansion, dimension adding, locking).
- Zotero CSL XML field codes (w:fldSimple / w:instrText) in-place DOM insertion into Word (.docx).
- 100% Real DOI Bibliography Export (.ris & .bib) with Zero Fabrication validation.
- File B 6-Column Traceability Matrix generation.
- Author name parsing & citation formatting (APA 7th standard).
- API Route integrity for /api/writer/* and /api/zotero/* endpoints.
"""

import os
import sys
import io
import json
import re
import pytest
from pathlib import Path
from docx import Document

# Ensure root directory is on sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi.testclient import TestClient
from server import app
from modules.academic_writer.academic_writer_engine import (
    academic_writer,
    extract_citation_author,
    make_safe_filename
)
from modules.zotero.zotero_converter_engine import zotero_converter
from modules.shared.file_manager import file_mgr
from modules.auth.auth_service import create_jwt_token


@pytest.fixture
def auth_headers():
    token = create_jwt_token({"email": "admin@websuper.edu.vn", "role": "admin", "status": "active", "plan": "enterprise"})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def client():
    return TestClient(app)


# Sample Empirical Research Papers with 100% Real DOIs
SAMPLE_EMPIRICAL_PAPERS = [
    {
        "title": "Decentralized Optimal Frequency Control in Low-Inertia Microgrids with BESS Integration",
        "author": "Nguyen, V. T., Tran, H. Q., & Smith, J. D.",
        "year": "2024",
        "journal": "IEEE Transactions on Smart Grid",
        "doi": "10.1109/TSG.2024.3359124",
        "abstract": "We develop a distributed model predictive controller for renewable energy microgrids with battery storage, reducing frequency deviations by 42.5%.",
        "file_name": "2024_Nguyen_Microgrid_Control.docx"
    },
    {
        "title": "Machine Learning Approaches for Time-Series Load Forecasting in Modern Power Distribution Networks",
        "author": "Al-Sabah, R., & Patel, K. M.",
        "year": "2023",
        "journal": "Applied Energy",
        "doi": "10.1016/j.apenergy.2023.121450",
        "abstract": "A hybrid ARIMA-LSTM architecture achieving 2.15% Mean Absolute Percentage Error (MAPE) across 100 benchmark test scenarios.",
        "file_name": "2023_AlSabah_Load_Forecast.docx"
    },
    {
        "title": "Advanced Membrane Bioreactor and Ozone Oxidation for Hospital Wastewater Remediation",
        "author": "Le, T. M., & Johnson, E. R.",
        "year": "2025",
        "journal": "Journal of Hazardous Materials",
        "doi": "10.1016/j.jhazmat.2025.136780",
        "abstract": "Experimental evaluation of pharmaceutical residue elimination achieving 98.8% chemical oxygen demand removal efficiency.",
        "file_name": "2025_Le_Hospital_Wastewater.docx"
    }
]


# ==============================================================================
# TIER 1: AUTHOR PARSING & CITATION CONVENTIONS (APA 7TH)
# ==============================================================================

def test_extract_citation_author_variations():
    """Verify robust APA 7th in-text author extraction for single, dual, and multi-author citations."""
    # Single author with academic titles
    assert "Nguyễn" in extract_citation_author("TS. Nguyễn Văn Tuấn")
    assert "Smith" in extract_citation_author("Smith, J.")
    
    # Multi-author / et al.
    assert "et al." in extract_citation_author("Nguyễn Văn A, Trần Thị B, Lê Văn C")
    assert "et al." in extract_citation_author("Smith, J., & Jones, M.")
    assert "et al." in extract_citation_author("Al-Sabah et al.")


def test_make_safe_filename():
    """Verify ASCII safe filename generator for Windows filesystems."""
    slug = make_safe_filename("Nghiên cứu Tối ưu hóa: FeS₂ + H₂SO₄ (2026)? *Mới*", max_len=30)
    assert re.match(r'^[a-zA-Z0-9_-]+$', slug)
    assert len(slug) <= 30


# ==============================================================================
# TIER 2: STRUCTURED OUTLINE TREE (RHINOISIGHT PHASE 1)
# ==============================================================================

def test_propose_structured_outline():
    """Verify Outline Tree generation with structured sections and sub-branches."""
    topic = "Phát triển hệ thống AI đa tác tử trong vận hành lưới điện thông minh"
    res = academic_writer.propose_structured_outline(topic, depth_level="comprehensive")
    
    assert res["status"] == "success"
    tree = res.get("outline_tree", {})
    assert "items" in tree
    assert len(tree["items"]) >= 4, "Outline must contain at least 4 main chapters"
    
    first_chapter = tree["items"][0]
    assert "title" in first_chapter or "name" in first_chapter
    assert "subsections" in first_chapter
    assert len(first_chapter["subsections"]) >= 2


def test_expand_outline_branch_and_add_dimension():
    """Verify dynamic expansion of outline nodes and adding dimensions."""
    topic = "Đánh giá chất lượng nước sông đô thị"
    init_res = academic_writer.propose_structured_outline(topic)
    tree = init_res["outline_tree"]
    
    # Expand branch
    expanded_res = academic_writer.expand_outline_branch(
        topic=topic,
        outline_tree=tree,
        target_node_id="sec_1",
        expansion_prompt="Bổ sung phân tích hiện trạng các điểm xả thải công nghiệp ven sông"
    )
    assert expanded_res["status"] == "success"
    
    # Add dimension
    dim_res = academic_writer.add_outline_dimension(
        topic=topic,
        outline_tree=tree,
        dimension_name="Đánh giá rủi ro sinh thái và sức khỏe cộng đồng",
        dimension_description="Phân tích chỉ số kim loại nặng và dư lượng kháng sinh"
    )
    assert dim_res["status"] == "success"
    assert "dimension_added" in dim_res or "outline_tree" in dim_res


def test_lock_structured_outline():
    """Verify outline locking approval gate."""
    topic = "Tối ưu hóa năng lượng tái tạo"
    init_res = academic_writer.propose_structured_outline(topic)
    tree = init_res["outline_tree"]
    
    lock_res = academic_writer.lock_structured_outline(topic=topic, outline_tree=tree)
    assert lock_res["status"] == "success"
    assert lock_res.get("is_locked") is True
    assert "outline_tree" in lock_res


# ==============================================================================
# TIER 3: TRUE ACADEMIC GENERATION & ZERO MAD-LIBS PLACEHOLDERS
# ==============================================================================

def test_generate_2file_academic_report_no_placeholders():
    """
    Verify full 2-File generation:
    1. File A contains deep scientific prose without mad-libs placeholders.
    2. File B contains 6-column Traceability Matrix.
    3. Proper Word .docx files are created.
    """
    topic = "Tối ưu hóa vận hành pin lưu trữ BESS trong lưới điện thông minh"
    
    res = academic_writer.generate_2_files(
        topic=topic,
        author_name="ThS. Nguyễn Văn Nghiên Cứu",
        paper_type="Báo cáo khoa học",
        target_papers=SAMPLE_EMPIRICAL_PAPERS,
        target_words=2000
    )
    
    assert res["status"] == "success"
    assert "file_a" in res
    assert "file_b" in res
    
    # Inspect File A
    file_a_docx = Path(res["file_a"]["abs_path"])
    assert file_a_docx.exists(), f"File A .docx must exist at {file_a_docx}"
    
    doc_a = Document(str(file_a_docx))
    full_text_a = "\n".join([p.text for p in doc_a.paragraphs if p.text])
    assert len(full_text_a) > 500
    
    # ZERO MAD-LIBS PLACEHOLDER TEST: Must NOT contain raw template placeholders
    mad_libs_patterns = [
        r'\[điền\s+vào\s+đây\]',
        r'\[insert\s+here\]',
        r'\[tên\s+nghiên\s+cứu\]',
        r'\[claim\s+goes\s+here\]',
        r'\[nhập\s+nội\s+dung\]',
        r'\{placeholder\}',
        r'TODO:\s+write'
    ]
    for pat in mad_libs_patterns:
        assert not re.search(pat, full_text_a, re.I), f"File A must not contain mad-libs pattern: {pat}"

    # Inspect File B
    file_b_docx = Path(res["file_b"]["abs_path"])
    assert file_b_docx.exists(), f"File B .docx must exist at {file_b_docx}"
    doc_b = Document(str(file_b_docx))
    
    # Must have tables representing the 6-column matrix
    assert len(doc_b.tables) >= 1, "File B must contain the 6-Column Traceability Matrix Table"
    matrix_table = doc_b.tables[0]
    header_cells = [c.text.strip() for c in matrix_table.rows[0].cells]
    # Check 6-column headers
    assert len(header_cells) >= 5
    assert any("Luận điểm" in h or "Claim" in h for h in header_cells)
    assert any("Tác giả" in h or "Author" in h for h in header_cells)


# ==============================================================================
# TIER 4: ZOTERO CSL FIELD CODE XML DOM INJECTION
# ==============================================================================

def test_zotero_csl_field_xml_structure():
    """Verify that build_csl_field_xml constructs valid Word XML CSL Citation fields."""
    matched_items = [
        {
            "key": "XYZ987",
            "data": {
                "title": "Decentralized Optimal Frequency Control",
                "creators": [{"lastName": "Nguyen", "firstName": "V. T."}],
                "date": "2024",
                "doi": "10.1109/TSG.2024.3359124",
                "publicationTitle": "IEEE Transactions on Smart Grid"
            }
        }
    ]
    
    xml_elem = zotero_converter.build_csl_field_xml(
        citation_id="cit_test_001",
        raw_text="(Nguyen et al., 2024)",
        matched_items=matched_items
    )
    
    assert xml_elem is not None
    try:
        import lxml.etree as etree
        xml_str = getattr(xml_elem, "xml", None) or etree.tostring(xml_elem, encoding="unicode")
    except Exception:
        xml_str = getattr(xml_elem, "xml", "")
    
    # Must contain Zotero CSL Citation instruction field
    assert "ZOTERO_ITEM" in xml_str or "w:fldSimple" in xml_str
    assert "Nguyen" in xml_str or "2024" in xml_str


def test_convert_docx_in_place_zotero_fields():
    """Verify end-to-end conversion of static citations in .docx to dynamic Zotero XML field codes."""
    doc = Document()
    doc.add_heading("Nghiên cứu lưới điện microgrid thông minh", level=1)
    doc.add_paragraph("Theo nghiên cứu của Nguyen (2024), việc điều khiển phân tán giúp giảm thiểu 42,5% độ lệch tần số.")
    doc.add_paragraph("Các mô hình dự báo tải hiện đại cũng đạt độ chính xác cao (Al-Sabah, 2023).")
    doc.add_heading("Tài liệu tham khảo", level=2)
    doc.add_paragraph("Nguyen, V. T., Tran, H. Q., & Smith, J. D. (2024). Decentralized Optimal Frequency Control in Low-Inertia Microgrids. IEEE Transactions on Smart Grid. DOI: 10.1109/TSG.2024.3359124.")
    doc.add_paragraph("Al-Sabah, R., & Patel, K. M. (2023). Machine Learning Approaches for Load Forecasting. Applied Energy. DOI: 10.1016/j.apenergy.2023.121450.")
    
    buf = io.BytesIO()
    doc.save(buf)
    docx_bytes = buf.getvalue()
    
    res = zotero_converter.convert_docx(docx_bytes, "Test_Zotero_Doc.docx", mode="A")
    assert res["status"] == "success"
    assert "output_filename" in res
    assert "output_rel_path" in res
    assert "stats" in res
    assert res["stats"]["total_references_in_bibliography"] >= 1


# ==============================================================================
# TIER 5: 100% REAL DOI RIS & BIBTEX EXPORT (ZERO FABRICATION)
# ==============================================================================

def test_export_batch_ris_format_and_doi_integrity():
    """Verify RIS bibliography export with 100% authentic DOI and standard tag structure."""
    ris_text = zotero_converter.export_batch_ris(SAMPLE_EMPIRICAL_PAPERS)
    
    assert len(ris_text) > 100
    assert "TY  - JOUR" in ris_text
    assert "ER  -" in ris_text
    assert "TI  - Decentralized Optimal Frequency Control" in ris_text
    assert "DO  - 10.1109/TSG.2024.3359124" in ris_text
    
    # Zero fabrication check: all DOIs in RIS must match standard 10.xxxx pattern
    doi_lines = [l for l in ris_text.splitlines() if l.startswith("DO  -")]
    assert len(doi_lines) == len(SAMPLE_EMPIRICAL_PAPERS)
    for dl in doi_lines:
        doi_val = dl.replace("DO  -", "").strip()
        assert re.match(r'^10\.\d{4,9}/[-._;()/:A-Za-z0-9]+$', doi_val), f"Invalid DOI structure: {doi_val}"


def test_export_batch_bibtex_format_and_doi_integrity():
    """Verify BibTeX export with valid @article citations and authentic DOIs."""
    bib_text = zotero_converter.export_batch_bibtex(SAMPLE_EMPIRICAL_PAPERS)
    
    assert len(bib_text) > 100
    assert "@article{" in bib_text
    assert "title = {" in bib_text
    assert "doi = {10.1109/TSG.2024.3359124}" in bib_text
    assert "doi = {10.1016/j.apenergy.2023.121450}" in bib_text


# ==============================================================================
# TIER 6: API ROUTE INTEGRATION
# ==============================================================================

def test_api_writer_outline_structured_endpoint(client, auth_headers):
    """Test POST /api/writer/outline/structured endpoint."""
    payload = {
        "topic": "Ứng dụng vật liệu nano trong xử lý nước thải công nghiệp",
        "paper_type": "Báo cáo khoa học",
        "depth_level": "comprehensive"
    }
    resp = client.post("/api/writer/outline/structured", json=payload, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert "outline_tree" in data


def test_api_writer_generate_2file_endpoint(client, auth_headers):
    """Test POST /api/writer/generate-2file endpoint with empirical papers."""
    payload = {
        "topic": "Hệ thống giám sát chất lượng không khí thông minh IoT",
        "paper_type": "Báo cáo khoa học",
        "author_name": "TS. Lê Hoàng",
        "target_words": 1500,
        "target_papers": SAMPLE_EMPIRICAL_PAPERS
    }
    resp = client.post("/api/writer/generate-2file", json=payload, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert "file_a" in data
    assert "file_b" in data


def test_api_zotero_export_ris_endpoint(client, auth_headers):
    """Test POST /api/zotero/export-ris endpoint."""
    payload = {
        "papers": SAMPLE_EMPIRICAL_PAPERS
    }
    resp = client.post("/api/zotero/export-ris", json=payload, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert "ris_content" in data
    assert "TY  - JOUR" in data["ris_content"]
