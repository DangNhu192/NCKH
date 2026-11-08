"""
Tests for Academic Fact Checker & Ground-Truth Verification (tests/test_academic_fact_checker.py)
--------------------------------------------------------------------------------------------------
Kiểm thử toàn diện:
1. Trích xuất mệnh đề định lượng kèm citation và DOI.
2. Xác minh tính khả dụng của DOI (HTTP 200 OK).
3. Đối chiếu số liệu bài viết với cơ sở dữ liệu thực chứng (Ground-Truth Matching).
4. Phát hiện số liệu mồ côi (không trích dẫn) và số liệu nghi vấn sai lệch.
5. Endpoint API POST /api/editorial/fact-check.
"""

import pytest
from modules.shared.academic_fact_checker import academic_fact_checker, AcademicFactChecker


def test_01_extract_quantitative_claims():
    text = (
        "Nghiên cứu tại Tháp Mười ghi nhận lượng phát thải 7,258 tấn CO2e/ha/năm (Trí et al., 2026). "
        "Mặt khác, dung lượng hấp phụ đạt 45,8 mg/g với diện tích bề mặt 120,5 m²/g theo DOI 10.1016/j.envpol.2025.1001. "
        "Ngoài ra, một câu văn không có số liệu chỉ thảo luận về phương pháp."
    )
    claims = academic_fact_checker.extract_quantitative_claims(text)
    assert len(claims) == 2
    assert "7,258 tấn CO2e/ha/năm" in claims[0]["metrics"] or "7,258 tấn" in claims[0]["sentence"]
    assert claims[0]["has_citation"] is True
    assert len(claims[1]["dois"]) > 0


def test_02_verify_doi_status():
    # Kiểm tra DOI chuẩn
    res = academic_fact_checker.verify_doi_status("10.1016/j.envpol.2025.1001")
    assert res is not None
    assert "is_valid" in res
    assert res["doi"] == "10.1016/j.envpol.2025.1001"


def test_03_verify_text_against_evidence_clean():
    evidence_claims = [
        {"claim": "Dung lượng hấp phụ đạt 45.8 mg/g", "verbatim_extract": "q_max was determined to be 45.8 mg/g."},
        {"claim": "Giảm phát thải 15.5%", "verbatim_extract": "Emissions reduced by 15.5%."}
    ]
    text = (
        "Thực nghiệm cho thấy dung lượng hấp phụ cực đại đạt 45,8 mg/g (Nguyen et al., 2025). "
        "Bên cạnh đó, mô hình giúp giảm phát thải 15,5% so với đối chứng (Tran et al., 2024)."
    )
    result = academic_fact_checker.verify_text_against_evidence(text, evidence_claims=evidence_claims)
    assert result["fact_check_score"] >= 80.0
    assert result["grade"] in ["EXCELLENT", "GOOD"]
    assert result["unreferenced_claims_count"] == 0


def test_04_verify_text_unreferenced_alert():
    text = "Hiệu suất xử lý đạt 98,5% nhưng không có bất kỳ trích dẫn nào trong câu này."
    result = academic_fact_checker.verify_text_against_evidence(text)
    assert result["unreferenced_claims_count"] == 1
    assert len(result["alerts"]) > 0
    assert "thiếu trích dẫn" in result["alerts"][0]


def test_05_api_editorial_fact_check():
    from fastapi.testclient import TestClient
    from server import app
    from modules.auth.auth_service import create_jwt_token

    client = TestClient(app)
    token = create_jwt_token({"email": "admin@websuper.edu.vn", "role": "admin", "status": "active", "plan": "enterprise"})
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "text": "Nồng độ COD giảm 85,2% tại pH 7,0 theo nghiên cứu (Le & cs., 2025)."
    }
    res = client.post("/api/editorial/fact-check", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "fact_check_score" in data["data"]