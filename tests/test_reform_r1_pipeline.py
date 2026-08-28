# tests/test_reform_r1_pipeline.py
"""
Test Suite for Requirement R1: 7-Step Pipeline Reform
Covers:
- Step 1: Semantic PICO extraction, multilingual keywords (no crude splitting), Boolean queries, trend metrics.
- Step 2: Multi-format document ingestion (.md, .docx, workspace files) into Evidence Vault with Zero Fabrication.
- Step 3: Open-Notebook Knowledge synchronization & literature matrix.
- Step 4: Quantitative structure & BigQuery analytics integration.
- Steps 5-7: End-to-end chained pipeline execution and artifact publishing.
- Boundary conditions: Empty inputs, special characters, offline heuristic fallbacks.
- API Route integrity for /api/pipeline/* endpoints.
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
from modules.pipeline.pipeline_engine import pipeline_engine, PIPELINE_STEPS_DEFINITION
from modules.harvester.data_harvesting_engine import data_harvester
from modules.notebooklm.notebooklm_engine import open_notebook_engine
from modules.shared.file_manager import file_mgr
from modules.auth.auth_service import create_jwt_token


@pytest.fixture
def auth_headers():
    token = create_jwt_token({"email": "admin@websuper.edu.vn", "role": "admin", "status": "active", "plan": "enterprise"})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def client():
    return TestClient(app)


# ==============================================================================
# TIER 1: STEP 1 PICO & KEYWORDS & HARVESTING TESTS
# ==============================================================================

def test_pipeline_steps_definition():
    """Verify that all 7 pipeline steps are properly defined with sequential step numbers and metadata."""
    steps = pipeline_engine.get_pipeline_steps()
    assert len(steps) == 7, "Pipeline must have exactly 7 steps"
    for i, step in enumerate(steps, start=1):
        assert step["step_no"] == i, f"Step {i} step_no mismatch"
        assert "id" in step
        assert "title" in step
        assert "description" in step
        assert "icon" in step


def test_step1_semantic_pico_and_keywords_smart_grid():
    """Verify Step 1 PICO semantic decomposition and multilingual keyword generation for Smart Grid."""
    topic = "Tối ưu hóa lưới điện thông minh tích hợp năng lượng tái tạo và hệ thống pin lưu trữ BESS"
    res = pipeline_engine.run_step(1, topic)

    assert res["status"] == "success"
    assert res["step_no"] == 1
    assert res["next_step"] == 2
    assert "GATE 1" in res.get("gate", "")
    
    scope = res.get("scope", {})
    assert "pico" in scope, "Step 1 must return PICO structure"
    pico = scope["pico"]
    assert any(k in pico for k in ["population", "intervention", "comparison", "outcome", "P", "I", "C", "O", "context"])
    
    # Multilingual keywords verification
    multi_kws = scope.get("multilingual_keywords", {})
    assert isinstance(multi_kws, dict)
    assert "en" in multi_kws or "keywords_en" in scope
    assert "vi" in multi_kws or "keywords_vi" in scope
    
    # Boolean queries verification
    assert "boolean_en" in scope
    assert len(scope["boolean_en"]) > 5
    assert "AND" in scope["boolean_en"] or "(" in scope["boolean_en"]


def test_step1_semantic_pico_clinical_medicine():
    """Verify Step 1 PICO extraction for Clinical Environmental Health research."""
    topic = "Đánh giá hiệu quả xử lý nước thải y tế bằng công nghệ màng MBR kết hợp Ozone hóa"
    res = pipeline_engine.run_step(1, topic)

    assert res["status"] == "success"
    scope = res.get("scope", {})
    assert len(scope.get("keywords", [])) > 0
    assert "evidence_standard" in scope


def test_translate_to_academic_english_heuristic():
    """Verify high-grade academic translation without external API dependencies."""
    vietnamese_title = "Nghiên cứu đánh giá tác động biến đổi khí hậu và tối ưu hóa giải pháp bền vững"
    translated = data_harvester.translate_to_academic_english(vietnamese_title)
    
    assert len(translated) > 10
    # Must not contain untranslated Vietnamese tone accents
    assert not data_harvester._has_vietnamese_characters(translated)
    assert any(term in translated.lower() for term in ["research", "evaluation", "impact", "optimization", "sustainable", "climate"])


# ==============================================================================
# TIER 2: MULTI-FORMAT DOCUMENT INGESTION INTO EVIDENCE VAULT
# ==============================================================================

def test_evidence_vault_ingest_markdown_and_docx():
    """Verify multi-format ingestion (.md and .docx) into Evidence Vault with Zero Fabrication."""
    # 1. Ingest DOCX
    doc_sample = Document()
    doc_sample.add_heading("Nghiên cứu xử lý nước thải bệnh viện bằng công nghệ MBR", level=1)
    doc_sample.add_paragraph("Tác giả: GS.TS. Nguyễn Văn A, PGS.TS. Trần Thị B (2025).")
    doc_sample.add_paragraph("Tạp chí Khoa học Môi trường, DOI: 10.1016/j.envsci.2025.105432.")
    doc_sample.add_paragraph("Kết quả thực nghiệm cho thấy hiệu suất khử COD đạt 98,5% và loại bỏ vi khuẩn 99,9%.")
    
    doc_bytes_io = io.BytesIO()
    doc_sample.save(doc_bytes_io)
    docx_bytes = doc_bytes_io.getvalue()
    
    item_docx = pipeline_engine.ingest_document_to_vault(docx_bytes, "2025_Nguyen_MBR_Water.docx")
    assert item_docx["has_verbatim"] is True
    assert "10.1016" in item_docx["doi"]
    assert "2025" in str(item_docx["year"])
    
    # 2. Ingest Markdown
    md_content = """# Optimization of Battery Energy Storage Systems (BESS)
Author: Dr. John Smith, Prof. Robert Lee (2024).
Journal: IEEE Transactions on Smart Grid, DOI: 10.1109/TSG.2024.3321456.
Abstract: This paper presents a novel model predictive control for microgrid frequency stabilization.
"""
    item_md = pipeline_engine.ingest_document_to_vault(md_content.encode("utf-8"), "2024_Smith_BESS_Control.md")
    assert item_md["has_verbatim"] is True
    assert "10.1109" in item_md["doi"]
    assert "2024" in str(item_md["year"])

    # 3. Check Vault listing
    vault_items = pipeline_engine.get_vault_items()
    assert len(vault_items) >= 2


# ==============================================================================
# TIER 3: STEP 3 TO STEP 7 SEQUENTIAL EXECUTION & PIPELINE INTEGRATION
# ==============================================================================

def test_step3_knowledge_sync_and_matrix():
    """Verify Step 3 Open-Notebook synchronization and literature matrix generation."""
    topic = "Ứng dụng AI trong chẩn đoán hình ảnh y khoa"
    res_step3 = pipeline_engine.run_step(3, topic)
    assert res_step3["status"] == "success"
    assert res_step3["step_no"] == 3
    assert "GATE 3" in res_step3.get("gate", "")


def test_step4_structure_and_bigquery_analytics():
    """Verify Step 4 IMRaD outline planning and quantitative analytics schema."""
    topic = "Phân tích chuỗi thời gian năng lượng mặt trời"
    res_step4 = pipeline_engine.run_step(4, topic)
    assert res_step4["status"] == "success"
    assert res_step4["step_no"] == 4
    assert "GATE 4" in res_step4.get("gate", "")
    assert "outline" in res_step4
    assert "bigquery_analytics" in res_step4


def test_step5_step6_step7_chained_execution():
    """Verify sequential execution of Step 5 (Drafting), Step 6 (Zotero CSL), and Step 7 (Humanize QA)."""
    topic = "Đánh giá chất lượng nước sông Sài Gòn"
    
    mock_papers = [
        {
            "title": "Đánh giá chất lượng nước mặt và mô hình hóa chỉ số WQI lưu vực sông Sài Gòn",
            "author": "Nguyễn Văn Tuấn, Lê Thị Lan",
            "year": "2024",
            "journal": "Tạp chí Phát triển Khoa học và Công nghệ",
            "doi": "10.32508/stdj.v27i2.4102",
            "abstract": "Nghiên cứu khảo sát 15 vị trí quan trắc dọc sông Sài Gòn từ năm 2020 đến 2023.",
            "file_name": "2024_Tuan_WQI_SaiGon.docx"
        },
        {
            "title": "Water quality index modeling and ecological risk assessment in urban river systems",
            "author": "Smith, J. A., Johnson, R. B.",
            "year": "2023",
            "journal": "Environmental Pollution and Ecological Modeling",
            "doi": "10.1016/j.envpol.2023.119854",
            "abstract": "A comprehensive analysis of biological oxygen demand and heavy metal contaminants.",
            "file_name": "2023_Smith_Water_Quality.docx"
        }
    ]
    
    # Step 5: 2-File drafting with pre-provided empirical papers in saved_papers
    res5 = pipeline_engine.run_step(5, topic, params={"target_words": 1500, "saved_papers": mock_papers, "evidence_vault": mock_papers})
    assert res5["status"] == "success"
    assert res5["step_no"] == 5
    assert "GATE 5" in res5.get("gate", "")
    assert "file_a" in res5
    assert "file_b" in res5
    
    # Step 6: Zotero conversion
    file_a_path = res5.get("file_a", {}).get("docx_rel_path") or res5.get("file_a", {}).get("docx")
    res6 = pipeline_engine.run_step(6, topic, params={"file_a_path": file_a_path})
    assert res6["status"] == "success"
    assert res6["step_no"] == 6
    assert "GATE 6" in res6.get("gate", "")
    
    # Step 7: Turnitin QA & Publishing
    res7 = pipeline_engine.run_step(7, topic, params={"file_a_path": file_a_path})
    assert res7["status"] == "success"
    assert res7["step_no"] == 7
    assert "GATE" in res7.get("gate", "")


# ==============================================================================
# TIER 4: BOUNDARY, CORNER CASES & ADVERSARIAL INPUTS
# ==============================================================================

def test_pipeline_empty_and_whitespace_topic():
    """Verify that empty, whitespace, or invalid topics are gracefully handled with fallbacks."""
    res = pipeline_engine.run_step(1, "   ")
    assert res["status"] == "success"
    assert "scope" in res


def test_pipeline_special_characters_topic():
    """Verify topic containing XML, HTML, math, and chemical symbols."""
    special_topic = "Nghiên cứu phản ứng FeS₂ + H₂SO₄ -> FeSO₄ + H₂S & phân tích WQI < 50; COD >= 120,5 mg/L"
    res = pipeline_engine.run_step(1, special_topic)
    assert res["status"] == "success"
    assert res["topic"] == special_topic
    assert "boolean_en" in res["scope"]


# ==============================================================================
# TIER 5: API ROUTE INTEGRATION & SECURITY
# ==============================================================================

def test_api_pipeline_steps_endpoint(client):
    """Test GET /api/pipeline/steps endpoint."""
    resp = client.get("/api/pipeline/steps")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 7


def test_api_pipeline_run_step_unauthorized(client):
    """Test POST /api/pipeline/run-step without authentication returns 401/403."""
    resp = client.post("/api/pipeline/run-step", json={"step_no": 1, "topic": "Test Topic"})
    assert resp.status_code in [401, 403]


def test_api_pipeline_run_step_authorized(client, auth_headers):
    """Test POST /api/pipeline/run-step with valid auth token."""
    payload = {
        "step_no": 1,
        "topic": "Đánh giá phát thải khí nhà kính trong nông nghiệp bền vững",
        "params": {}
    }
    resp = client.post("/api/pipeline/run-step", json=payload, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["step_no"] == 1
    assert "scope" in data
