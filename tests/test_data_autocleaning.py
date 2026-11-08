"""
Tests for Data Autocleaning Service (tests/test_data_autocleaning.py)
--------------------------------------------------------------------
Kiểm thử toàn diện:
1. Phát hiện và xử lý ngoại lai khoa học (pH, %, q_max, COD, BOD).
2. Chuẩn hóa đơn vị đo khoa học (mg/g, m2/g, mg/L...).
3. Chuẩn hóa số thập phân phong cách tiếng Việt (dấu phẩy '1,5', dấu chấm '1.000').
4. Làm sạch bảng Ma trận Đối soát 6 cột File B.
5. Thẩm định bộ dữ liệu (Data Profiling) và API /api/evidence-db/autoclean.
"""

import pytest
from modules.shared.data_autocleaning import scientific_data_cleaner, ScientificDataCleaner


def test_01_vietnamese_number_formatting():
    # Thập phân đơn giản
    assert scientific_data_cleaner.format_vietnamese_number(1.5) == "1,5"
    assert scientific_data_cleaner.format_vietnamese_number(0.05) == "0,05"
    # Hàng nghìn
    assert scientific_data_cleaner.format_vietnamese_number(1000) == "1.000"
    assert scientific_data_cleaner.format_vietnamese_number(1234567.89) == "1.234.567,89"
    # Chuỗi văn bản chứa số
    assert scientific_data_cleaner.format_vietnamese_number("28.5%") == "28,5%"


def test_02_clean_scientific_text_units_and_chemistry():
    text = "Hap phu kim loai dat q_max 45.8 mg/g voi dien tich be mat 120.5 m2/g o nong do COD 350.0 mg/L va sinh ra FeS2, H2SO4 cung NH4+."
    cleaned = scientific_data_cleaner.clean_scientific_text(text)
    assert "45,8 mg/g" in cleaned
    assert "120,5 m²/g" in cleaned
    assert "350,0 mg/L" in cleaned
    assert "FeS₂" in cleaned
    assert "H₂SO₄" in cleaned
    assert "NH₄⁺" in cleaned


def test_03_detect_and_fix_outliers():
    # Hiệu suất > 100% -> trần hóa về 100%
    is_outlier, val, msg = scientific_data_cleaner.detect_and_fix_outliers("efficiency", 105.0)
    assert is_outlier is True
    assert val == 100.0

    # Nồng độ COD âm -> điều chỉnh về 0.0
    is_outlier_cod, val_cod, _ = scientific_data_cleaner.detect_and_fix_outliers("COD", -15.0)
    assert is_outlier_cod is True
    assert val_cod == 0.0

    # Giá trị hợp lệ
    is_normal, val_norm, _ = scientific_data_cleaner.detect_and_fix_outliers("ph", 6.8)
    assert is_normal is False
    assert val_norm == 6.8


def test_04_clean_evidence_matrix_rows():
    raw_rows = [
        [
            "1",
            "Nong do NH4+ dat 15.2 mg/L.",
            "Nguyen, V. A. (2025)",
            "Doc1.docx",
            "Du lieu COD giam 85.5% voi dien tich S_BET dat 250.0 m2/g.",
            "Trang 12"
        ],
        [
            "2",
            "Hieu qua xu ly dat 98.4% tai pH 7.2.",
            "Tran, T. B. (2024)",
            "Doc2.docx",
            "Chat luong nuoc dat chuan voi FeS2 on dinh.",
            "Trang 45"
        ]
    ]

    cleaned_rows = scientific_data_cleaner.clean_evidence_matrix_rows(raw_rows)
    assert len(cleaned_rows) == 2
    assert "NH₄⁺" in cleaned_rows[0][1]
    assert "15,2 mg/L" in cleaned_rows[0][1]
    assert "85,5%" in cleaned_rows[0][4]
    assert "250,0 m²/g" in cleaned_rows[0][4]
    assert "FeS₂" in cleaned_rows[1][4]


def test_05_profile_and_clean_dataset():
    records = [
        {"id": 1, "ph": 7.4, "efficiency": 85.0, "note": "H2SO4 on dinh"},
        {"id": 2, "ph": 15.5, "efficiency": 110.0, "note": "Gia tri vuot nguong"},
        {"id": 3, "ph": None, "efficiency": "N/A", "note": "Mat mau"}
    ]

    profile_res = scientific_data_cleaner.profile_and_clean_dataset(records)
    assert profile_res["total_records"] == 3
    assert profile_res["total_anomalies"] > 0
    assert profile_res["field_profiles"]["ph"]["null_count"] == 1
    assert profile_res["field_profiles"]["efficiency"]["outliers"] >= 1


def test_06_api_evidence_db_autoclean():
    from fastapi.testclient import TestClient
    from server import app
    from modules.auth.auth_service import create_jwt_token

    client = TestClient(app)
    token = create_jwt_token({"email": "admin@websuper.edu.vn", "role": "admin", "status": "active", "plan": "enterprise"})
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "text": "Nong do dat 12.5 mg/L voi FeS2 va H2SO4.",
        "records": [{"metric": "COD", "val": 150.0}]
    }

    res = client.post("/api/evidence-db/autoclean", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "cleaned_text" in data["data"]
    assert "12,5 mg/L" in data["data"]["cleaned_text"]
    assert "FeS₂" in data["data"]["cleaned_text"]