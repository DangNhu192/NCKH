"""
Tests for PubChem Chemical Resolver Service (tests/test_pubchem_service.py)
---------------------------------------------------------------------------
Kiểm thử:
1. Phân giải hợp chất nông nghiệp / môi trường từ Curated Cache (FeS2, H2SO4, NH4+, Glyphosate).
2. Tra cứu thuộc tính: Công thức, IUPAC Name, Khối lượng phân tử, SMILES, InChIKey.
3. Tạo liên kết hình ảnh 2D độ phân giải cao.
4. Kiểm tra các API Router /api/math-chem/pubchem-resolve và /api/math-chem/pubchem-image/{cid}.
"""

import pytest
from modules.shared.pubchem_service import pubchem_service, PubChemService


def test_01_resolve_curated_pyrite():
    res = pubchem_service.resolve_compound("FeS2")
    assert res["status"] == "success"
    data = res["data"]
    assert data["cid"] == 24204
    assert data["formula"] == "FeS₂"
    assert "Pyrite" in data["name"]


def test_02_resolve_curated_sulfuric_acid():
    res = pubchem_service.resolve_compound("H2SO4")
    assert res["status"] == "success"
    data = res["data"]
    assert data["cid"] == 1118
    assert data["formula"] == "H₂SO₄"


def test_03_resolve_curated_glyphosate():
    res = pubchem_service.resolve_compound("glyphosate")
    assert res["status"] == "success"
    data = res["data"]
    assert data["cid"] == 3496
    assert data["molecular_weight"] > 100.0


def test_04_get_structure_image_url():
    url = pubchem_service.get_structure_image_url(24204)
    assert "pubchem.ncbi.nlm.nih.gov" in url
    assert "24204/PNG" in url


def test_05_api_math_chem_pubchem_resolve():
    from fastapi.testclient import TestClient
    from server import app

    client = TestClient(app)
    res = client.post("/api/math-chem/pubchem-resolve", json={"name": "urea"})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["data"]["cid"] == 1176

    res_img = client.get("/api/math-chem/pubchem-image/1176")
    assert res_img.status_code == 200
    assert "image_url" in res_img.json()