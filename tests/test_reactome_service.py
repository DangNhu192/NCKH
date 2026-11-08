"""
Tests for Reactome Database Service (tests/test_reactome_service.py)
--------------------------------------------------------------------
Kiểm thử:
1. Tra cứu đường dẫn sinh học / phản ứng theo từ khóa.
2. Tra cứu chi tiết một pathway theo Stable ID.
3. Kiểm tra cơ chế fallback vào kiến thức cục bộ khi offline.
"""

import pytest
from modules.shared.reactome_service import reactome_service, ReactomeService


def test_01_search_pathways_nitrogen():
    results = reactome_service.search_pathways("nitrogen", max_results=3)
    assert len(results) > 0
    names = [r["name"].lower() for r in results]
    assert any("nitrogen" in n or "ammonium" in n for n in names)
    assert "stId" in results[0]


def test_02_search_pathways_carbon():
    results = reactome_service.search_pathways("carbon", max_results=2)
    assert len(results) > 0
    assert "stId" in results[0]


def test_03_get_pathway_details():
    details = reactome_service.get_pathway_details("R-HSA-71291")
    assert details is not None
    assert "stId" in details or "displayName" in details


def test_04_fallback_local_cache():
    # Kiểm tra truy vấn từ khóa đặc thù với fallback an toàn
    results = reactome_service.search_pathways("bioremediation of pollutants", max_results=2)
    assert len(results) > 0
    assert results[0]["stId"] is not None


def test_05_api_harvester_reactome_endpoints():
    from fastapi.testclient import TestClient
    from server import app
    from modules.auth.auth_service import create_jwt_token

    client = TestClient(app)
    token = create_jwt_token({"email": "admin@websuper.edu.vn", "role": "admin", "status": "active", "plan": "enterprise"})
    headers = {"Authorization": f"Bearer {token}"}

    # Test search
    res = client.post("/api/harvester/reactome-search", json={"query": "nitrogen", "max_results": 2}, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert len(data["results"]) > 0

    # Test detail
    res_det = client.get("/api/harvester/reactome-pathway/R-ALL-111933", headers=headers)
    assert res_det.status_code == 200
    assert res_det.json()["status"] == "success"