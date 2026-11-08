# -*- coding: utf-8 -*-
"""
tests/test_evidence_inspector_gate.py
=====================================
Bộ kiểm thử tự động cho Trình Đối Soát Dữ Liệu Gốc Song Song
& Cổng Kiểm Duyệt 4 Tầng Tự Động (Dual-Pane Evidence Inspector v4.2).

Bao quát 9 kịch bản kiểm thử:
1. Chuẩn hóa Multi-Evidence Catalog (Schema 10 trường dữ liệu).
2. Bóc tách & Chuẩn hóa mã định danh DOI (Single-Row Clean Access).
3. Tầng 1: Kiểm toán Match Ratio trên văn bản PDF thô (>= 0.60).
4. Tầng 2: Kiểm toán Nút bấm & Chống Gian Lận Chủ Đề (Anti-Topic Fraud).
5. Tầng 3: Đồng bộ hóa Word DOCX và Khóa Thông Số Đo Đạc.
6. Tầng 4: Ngắt mạch liêm chính (Zero-Hallucination Circuit Breaker).
7. Xuất bản Bảng Ma Trận Truy Xuất Nguồn Gốc A4 Landscape (.docx & .md).
8. Đóng gói Trọn bộ Sản phẩm Độc lập (Standalone Bundle: 1:1:1:1).
9. Kiểm thử Toàn diện API Endpoints (/api/inspector/*).
"""

import os
import json
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

from modules.inspector.evidence_inspector_engine import evidence_inspector_engine, EvidenceInspectorEngine
from server import app


@pytest.fixture
def sample_catalog_items():
    return [
        {
            "id": "EVID_THAPMUOI_2026",
            "title": "Nghiên cứu phát thải khí nhà kính trong canh tác lúa tại Đồng Tháp Mười",
            "author": "Trí et al., 2026",
            "pdf": "ThapMuoi_Rice_2026.pdf",
            "page": 3,
            "quote_en": "Methane emissions were quantified at 7.258 tons CO2e per hectare annually.",
            "quote_vi": "Phát thải khí mê-tan được định lượng ở mức 7,258 tấn CO2e/ha/năm.",
            "params": "7,258 tấn CO2e/ha/năm; CH4",
            "doi": "https://doi.org/10.1016/j.envpol.2025.1001",
            "rects": [[100, 200, 300, 250]]
        },
        {
            "id": "EVID_BIOCHAR_2025",
            "title": "Chế tạo vật liệu nano biochar từ vỏ trấu hấp phụ kim loại nặng",
            "author": "Nguyễn et al., 2025",
            "pdf": "Biochar_Adsorption_2025.pdf",
            "page": 5,
            "quote_en": "The maximum adsorption capacity q_max was determined to be 45.8 mg/g.",
            "quote_vi": "Dung lượng hấp phụ cực đại q_max đạt 45,8 mg/g.",
            "params": "q_max = 45,8 mg/g; S_BET = 120,5 m2/g",
            "doi": "10.1021/acs.est.2025.2045",
            "rects": [[120, 310, 450, 360]]
        }
    ]


def test_01_catalog_generation_and_schema_10_fields(sample_catalog_items):
    """Kiểm tra tạo catalog đạt chuẩn 10 trường dữ liệu bất biến."""
    catalog = evidence_inspector_engine.generate_multi_evidence_catalog(raw_items=sample_catalog_items)
    
    assert isinstance(catalog, dict)
    assert len(catalog) == 2
    assert "EVID_THAPMUOI_2026" in catalog
    
    item = catalog["EVID_THAPMUOI_2026"]
    required_keys = ["id", "title", "author", "pdf", "page", "quote_en", "quote_vi", "params", "doi", "rects"]
    for k in required_keys:
        assert k in item, f"Thiếu trường bắt buộc '{k}' trong catalog item"
    
    assert item["page"] == 3
    assert "7,258 tấn" in item["quote_vi"]
    assert item["doi"] == "10.1016/j.envpol.2025.1001"


def test_02_clean_doi_extraction():
    """Kiểm tra chuẩn hóa DOI, loại bỏ các tiền tố URL để đảm bảo nút bấm tinh gọn."""
    engine = EvidenceInspectorEngine()
    
    assert engine._clean_doi("https://doi.org/10.1016/j.envpol.2025.1001") == "10.1016/j.envpol.2025.1001"
    assert engine._clean_doi("http://dx.doi.org/10.1021/acs.est.2025.2045") == "10.1021/acs.est.2025.2045"
    assert engine._clean_doi("10.1007/s11270-025-0789-0") == "10.1007/s11270-025-0789-0"
    assert engine._clean_doi("") == ""
    assert engine._clean_doi(None) == ""


def test_03_layer1_raw_pdf_matching(sample_catalog_items, tmp_path):
    """Kiểm tra Tầng 1: Kiểm toán tỷ lệ trùng khớp mặt chữ PDF (Match Ratio) qua run_4_layer_verification_gate."""
    catalog = evidence_inspector_engine.generate_multi_evidence_catalog(raw_items=sample_catalog_items)
    
    # Chạy cổng kiểm định 4 tầng với thư mục pdf test
    report = evidence_inspector_engine.run_4_layer_verification_gate(
        catalog=catalog,
        pdf_dir=tmp_path / "empty_pdf_dir"
    )
    
    assert isinstance(report, dict)
    assert "layer1" in report
    l1 = report["layer1"]
    assert "total_verified" in l1
    assert "errors" in l1
    # Do file PDF chưa tạo nên layer 1 sẽ bắt lỗi missing file
    assert len(l1["errors"]) == 2


def test_04_layer2_interactive_buttons_and_anti_topic_fraud(sample_catalog_items, tmp_path):
    """Kiểm tra Tầng 2: Kiểm toán nút trích dẫn và Chống gian lận chủ đề."""
    catalog = evidence_inspector_engine.generate_multi_evidence_catalog(raw_items=sample_catalog_items)
    
    # Tạo mock HTML chứa các nút bấm tương ứng
    mock_html_path = tmp_path / "doi_soat_test.html"
    mock_html = """
    <!DOCTYPE html>
    <html><body>
    <div class="imrad-body">
      <p>Nghiên cứu của Trí et al. (2026) ghi nhận phát thải 
        <button class="cite-btn" data-evidence-id="EVID_THAPMUOI_2026">[Trí et al., 2026]</button>.
      </p>
      <p>Vật liệu biochar hấp phụ cực đại 
        <button class="cite-btn" data-evidence-id="EVID_BIOCHAR_2025">[Nguyễn et al., 2025]</button>.
      </p>
    </div>
    </body></html>
    """
    mock_html_path.write_text(mock_html, encoding="utf-8")
    
    report = evidence_inspector_engine.run_4_layer_verification_gate(
        catalog=catalog,
        html_path=mock_html_path
    )
    
    assert "layer2" in report
    l2 = report["layer2"]
    assert l2["total_buttons"] == 2
    assert l2["passed"] is True


def test_05_layer3_docx_synchronization_and_locked_metrics(sample_catalog_items, tmp_path):
    """Kiểm tra Tầng 3: Kiểm toán đồng bộ hóa Word DOCX và Khóa số liệu."""
    import docx
    catalog = evidence_inspector_engine.generate_multi_evidence_catalog(raw_items=sample_catalog_items)
    
    # Tạo mock file DOCX chứa các thông số định lượng bị khóa
    test_docx_path = tmp_path / "test_manuscript.docx"
    doc = docx.Document()
    doc.add_heading("Báo Cáo Nghiên Cứu Khí Nhà Kính & Biochar", level=1)
    doc.add_paragraph("Lượng phát thải đo được là 7,258 tấn CO2e/ha/năm theo Trí et al. (2026).")
    doc.add_paragraph("Dung lượng hấp phụ cực đại q_max đạt 45,8 mg/g (Nguyễn et al., 2025).")
    doc.save(str(test_docx_path))
    
    mock_html_path = tmp_path / "test_sync.html"
    mock_html = """
    <p>Lượng phát thải đo được là 7,258 tấn CO2e/ha/năm theo Trí et al. (2026).</p>
    <p>Dung lượng hấp phụ cực đại q_max đạt 45,8 mg/g (Nguyễn et al., 2025).</p>
    <button class="cite-btn" data-evidence-id="EVID_THAPMUOI_2026">[1]</button>
    <button class="cite-btn" data-evidence-id="EVID_BIOCHAR_2025">[2]</button>
    """
    mock_html_path.write_text(mock_html, encoding="utf-8")
    
    report = evidence_inspector_engine.run_4_layer_verification_gate(
        catalog=catalog,
        docx_path=test_docx_path,
        html_path=mock_html_path
    )
    
    assert "layer3" in report
    l3 = report["layer3"]
    assert l3["passed"] is True
    assert l3["locked_metrics_count"] >= 2


def test_06_layer4_zero_hallucination_circuit_breaker(sample_catalog_items):
    """Kiểm tra Tầng 4: Ngắt mạch liêm chính học thuật (Circuit Breaker)."""
    # Khi chạy với catalog rỗng
    report = evidence_inspector_engine.run_4_layer_verification_gate(catalog={})
    assert "layer4" in report
    l4 = report["layer4"]
    assert "status" in l4
    assert l4["passed"] is True
    assert "PASSED" in l4["status"]


def test_07_traceability_matrix_landscape_docx(sample_catalog_items, tmp_path):
    """Kiểm tra xuất bản Bảng Ma Trận Truy Xuất Nguồn Gốc A4 Landscape (Khổ Ngang 7 Cột)."""
    import docx
    catalog = evidence_inspector_engine.generate_multi_evidence_catalog(raw_items=sample_catalog_items)
    
    custom_docx_file = tmp_path / "xuat_ban" / "Bang_Truy_Xuat_Nguon_Goc_Tai_Lieu.docx"
    res_path = evidence_inspector_engine.generate_traceability_matrix_docx(
        catalog=catalog,
        output_docx_path=custom_docx_file,
        title="BẢNG MA TRẬN TRUY XUẤT NGUỒN GỐC TÀI LIỆU"
    )
    
    assert res_path.exists()
    assert res_path.stat().st_size > 0
    
    # Mở kiểm tra thuộc tính hướng trang A4 Landscape
    doc = docx.Document(str(res_path))
    section = doc.sections[0]
    assert section.orientation == docx.enum.section.WD_ORIENT.LANDSCAPE
    assert len(doc.tables) >= 1
    
    table = doc.tables[0]
    assert len(table.columns) == 7
    # Dòng tiêu đề + 2 dòng dữ liệu
    assert len(table.rows) == 3


def test_08_standalone_bundle_packaging(sample_catalog_items, tmp_path):
    """Kiểm tra đóng gói trọn bộ đối soát độc lập (Nguyên tắc Bất biến 1:1:1:1)."""
    dest_dir = tmp_path / "bundle_test"
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    # Tạo catalog trước
    catalog = evidence_inspector_engine.generate_multi_evidence_catalog(raw_items=sample_catalog_items)
    cat_file = dest_dir / "multi_evidence_catalog.json"
    cat_file.write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")
    
    # Tạo ma trận docx & md
    evidence_inspector_engine.generate_traceability_matrix_docx(catalog, dest_dir / "Bang_Truy_Xuat_Nguon_Goc_Tai_Lieu.docx")
    evidence_inspector_engine.generate_traceability_matrix_md(catalog, dest_dir / "Bang_Truy_Xuat_Nguon_Goc_Tai_Lieu.md")
    
    # Tạo HTML
    evidence_inspector_engine.generate_dual_pane_html(
        docx_path=dest_dir / "Bao_Cao.docx",
        catalog=catalog,
        output_html_path=dest_dir / "doi_soat.html"
    )
    
    bundle_path = evidence_inspector_engine.package_standalone_bundle(
        target_dir=dest_dir,
        port=8765
    )
    
    assert bundle_path.exists()
    assert (dest_dir / "multi_evidence_catalog.json").exists()
    assert (dest_dir / "Bang_Truy_Xuat_Nguon_Goc_Tai_Lieu.docx").exists()
    assert (dest_dir / "Bang_Truy_Xuat_Nguon_Goc_Tai_Lieu.md").exists()
    assert (dest_dir / "doi_soat.html").exists()
    assert (dest_dir / "server.js").exists()
    assert (dest_dir / "Khoi_Chay_Doi_Soat.bat").exists()
    
    # Kiểm tra nội dung doi_soat.html có chứa cấu trúc Spotlight Card chuẩn DOI line duy nhất
    html_text = (dest_dir / "doi_soat.html").read_text(encoding="utf-8")
    assert "spotlight-doi-row" in html_text
    assert "btn-open-doi" in html_text
    assert "btn-open-scihub" in html_text
    assert "the-canvas" in html_text


def test_09_api_inspector_endpoints(sample_catalog_items):
    """Kiểm thử toàn bộ các API Endpoints trong modules/inspector/inspector_router.py."""
    client = TestClient(app)
    
    # 1. GET /api/inspector/catalog
    res = client.get("/api/inspector/catalog")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "catalog" in data
    
    # 2. POST /api/inspector/generate-bundle
    res = client.post("/api/inspector/generate-bundle", json={
        "article_title": "Báo cáo thử nghiệm API Inspector",
        "evidence_items": sample_catalog_items
    })
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "files" in data
    
    # 3. POST /api/inspector/verify-gate
    res = client.post("/api/inspector/verify-gate", json={})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "report" in data
    assert "gate_passed" in data
    
    # 4. POST /api/inspector/generate-matrix
    res = client.post("/api/inspector/generate-matrix", json={
        "evidence_items": sample_catalog_items
    })
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "docx_path" in data
    
    # 5. GET /api/inspector/view-html
    res = client.get("/api/inspector/view-html")
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
