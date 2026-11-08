# tests/test_multi_source_keyword_trends.py
"""
Test Suite: Multi-Source Open Bibliometrics and Keyword Research Trends
Kiem thu tinh nang thu thap so lieu thong ke khoa hoc tu cac nguon mo (OpenAlex, Europe PMC, arXiv, Crossref)
theo tu khoa cua de tai va tich hop vao cau truc bai lam, cay de cuong va bao cao thuc chung.
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from modules.harvester.data_harvesting_engine import data_harvester
from modules.pipeline.document_extractor_engine import document_evidence_extractor
from server import app

client = TestClient(app)


def test_extract_topic_keywords():
    """Kiem tra tinh nang tu dong trich xuat tu khoa hoc thuat tu ten de tai."""
    topic = "Ung dung Tri tue Nhan tao va Hoc Sau trong Chan doan Hinh anh Y te"
    kws = data_harvester.extract_topic_keywords(topic, max_keywords=5)
    assert isinstance(kws, list)
    assert len(kws) >= 2
    combined = " ".join(kws).lower()
    assert any(term in combined for term in ["tri tue", "hoc sau", "chan doan", "hinh anh", "intelligence", "learning", "imaging"])


def test_fetch_per_keyword_trends_sources():
    """Kiem tra ham fetch_per_keyword_trends voi cac nguon du lieu mo khac nhau."""
    keywords = ["Deep Learning", "Transformer Model"]
    
    # 1. OpenAlex
    trends_oa = data_harvester.fetch_per_keyword_trends(keywords, source="openalex", years_range=["2021", "2022", "2023", "2024", "2025"])
    assert len(trends_oa) == 2
    for t in trends_oa:
        assert "keyword" in t
        assert "yearly_counts" in t
        assert "cagr_percent" in t
        assert "trend_direction" in t
        assert t["total"] > 0
        assert "OpenAlex" in t["source"]

    # 2. Europe PMC
    trends_epmc = data_harvester.fetch_per_keyword_trends(["Clinical Trial"], source="europepmc", years_range=["2022", "2023", "2024", "2025"])
    assert len(trends_epmc) == 1
    assert "Europe PMC" in trends_epmc[0]["source"]

    # 3. Crossref
    trends_cr = data_harvester.fetch_per_keyword_trends(["Renewable Energy"], source="crossref", years_range=["2022", "2023", "2024", "2025"])
    assert len(trends_cr) == 1
    assert "Crossref" in trends_cr[0]["source"]

    # 4. arXiv
    trends_ax = data_harvester.fetch_per_keyword_trends(["Quantum Computing"], source="arxiv", years_range=["2022", "2023", "2024", "2025"])
    assert len(trends_ax) == 1
    assert "arXiv" in trends_ax[0]["source"]

    # 5. All (Multi-Source)
    trends_all = data_harvester.fetch_per_keyword_trends(["Artificial Intelligence"], source="all", years_range=["2022", "2023", "2024", "2025"])
    assert len(trends_all) == 1
    assert trends_all[0]["total"] > 0


def test_fetch_multi_source_keyword_trends_summary():
    """Kiem tra tong hop thong ke vi mo va chi so tang truong CAGR."""
    topic = "Nang luong Tai tao va Luoi dien Thong minh"
    pkg = data_harvester.fetch_multi_source_keyword_trends(topic, source="openalex")
    assert pkg["topic"] == topic
    assert pkg["source_code"] == "openalex"
    assert "OpenAlex" in pkg["source_name"]
    assert len(pkg["trends"]) >= 2
    stats = pkg["summary_statistics"]
    assert stats["total_publications"] > 0
    assert isinstance(stats["average_cagr_percent"], float)
    assert len(stats["overview_text"]) > 40


def test_topic_outline_includes_bibliometrics_section():
    """Kiem tra Cay de cuong sinh ra co chua phan muc Thu muc hoc va Xu huong Cong bo."""
    topic = "Phat trien He thong Luoi dien Thong minh"
    res = document_evidence_extractor.generate_topic_structured_outline(
        topic=topic,
        trend_source="europepmc"
    )
    assert res["status"] == "success"
    items = res["outline_tree"]["items"]
    
    ch2 = next((it for it in items if it.get("section_number") == 2), None)
    assert ch2 is not None
    
    subsections = ch2.get("subsections", [])
    bib_sub = next((s for s in subsections if "thư mục học" in s.get("title", "").lower() or "xu hướng" in s.get("title", "").lower()), None)
    assert bib_sub is not None
    assert "Europe PMC" in bib_sub.get("title", "")


def test_extract_evidence_by_topic_with_multi_source_trends(tmp_path):
    """Kiem tra qua trinh boc tach thuc chung tich hop bang xu huong thu muc hoc tu nguon mo."""
    topic = "Tri tue Nhan tao trong Y te"
    docs = [
        {
            "filename": "medical_ai_trial.docx",
            "content": (
                "Nghien cuu ve Tri tue Nhan tao trong Y te (Smith et al., 2023). "
                "He thong dat do chinh xac 94,8% tren 1.200 ca benh (Trang 15). "
                "Thoi gian chan doan giam tu 45 phut xuong con 12 phut. "
                "Thach thuc chinh la bao mat du lieu benh an dien tu."
            )
        }
    ]

    res = document_evidence_extractor.extract_evidence_by_topic_outline(
        topic=topic,
        provided_documents=docs,
        save_docx_report=True,
        trend_source="crossref",
        trend_keywords=["Medical AI", "Deep Learning in Healthcare"]
    )

    assert res["status"] == "success"
    full_rec = res["full_record"]
    assert "bibliometric_trends" in full_rec
    assert full_rec["trend_source"] == "crossref"
    assert "Crossref" in full_rec["bibliometric_trends"]["source_name"]

    aligned = res["aligned_nodes"]
    ch2 = next((n for n in aligned if n.get("section_number") == 2), None)
    assert ch2 is not None
    assert ch2["has_evidence"] is True
    assert any(it.get("category") == "BIBLIOMETRICS" for it in ch2.get("evidence_items", []))

    assert res["report_docx"]["filename"] is not None
    assert res["report_md"]["filename"] is not None
    assert "MA TRẬN XU HƯỚNG CÔNG BỐ KHOA HỌC QUỐC TẾ" in res["report_md"]["content"]


def test_api_keyword_trends_endpoint():
    """Kiem tra API endpoint /api/harvest/keyword-trends."""
    from modules.auth.auth_service import require_operational_user
    app.dependency_overrides[require_operational_user] = lambda: {"user_id": "test_user", "role": "admin"}
    try:
        response = client.post(
            "/api/harvest/keyword-trends",
            json={
                "topic": "Internet of Things",
                "keywords": ["IoT Security", "Edge Computing"],
                "source": "arxiv"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "trends" in data
        assert "summary_statistics" in data
    finally:
        app.dependency_overrides.pop(require_operational_user, None)
