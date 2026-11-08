# tests/test_topic_outline_extractor.py
"""
WEB SUPER v3.2 / v2.0 - Test Suite: Topic-Driven Outline Generation & Document Evidence Extractor
Kiểm thử toàn diện tính năng:
1. Tự động sinh Cây Đề Cương có cấu trúc dựa trên Tên Đề Tài bằng Google Gemini AI (với fallback chuẩn viện hàn lâm).
2. Dùng chính Cây Đề Cương để truy vấn, bóc tách thực chứng và số liệu từ tài liệu cung cấp.
3. Gắn nhãn [uncertain] cho các phân mục thiếu chứng cứ xác thực.
4. Xuất bản Báo Cáo Thực Chứng Theo Đề Cương chuẩn Word (.docx) và Markdown (.md).
5. Kiểm thử các API Endpoints: /api/evidence-db/generate-topic-outline và /api/evidence-db/extract-by-topic.
"""

import os
import io
import json
import base64
import pytest
from pathlib import Path
from docx import Document

from fastapi.testclient import TestClient
from server import app
from modules.pipeline.document_extractor_engine import document_evidence_extractor
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
def sample_ai_paper_docx():
    """Tạo tệp Word .docx về ứng dụng AI trong kiểm soát ô nhiễm nước."""
    doc = Document()
    doc.add_heading("Ứng dụng Trí tuệ Nhân tạo trong Quan trắc và Xử lý Nước thải Công nghiệp", level=1)
    
    p_meta = doc.add_paragraph()
    p_meta.add_run("Tác giả: Nguyễn Văn An, Trần Thị Bình, & Lê Hoàng Cường (2024)\n")
    p_meta.add_run("Tạp chí: Tạp chí Khoa học Môi trường và Trí tuệ Nhân tạo, 18(2), 112-125. DOI: 10.1016/j.envai.2024.03.015\n")
    
    doc.add_heading("1. Mở đầu và Đặt vấn đề Nghiên cứu", level=2)
    doc.add_paragraph(
        "Mục tiêu nghiên cứu là phát triển mô hình học sâu dự báo nồng độ COD và BOD trong nước thải công nghiệp. "
        "The primary objective is to enhance water quality monitoring using neural network algorithms."
    )
    
    doc.add_heading("2. Phương pháp Thực nghiệm và Dữ liệu", level=2)
    doc.add_paragraph(
        "Phương pháp nghiên cứu sử dụng thuật toán mạng nơ-ron tích chập kết hợp LSTM (CNN-LSTM) huấn luyện trên 45.000 mẫu đo cảm biến IoT. "
        "The proposed methodology integrates sensor data streams with an adaptive loss function."
    )
    
    # Bảng số liệu thực nghiệm
    tbl = doc.add_table(rows=3, cols=3)
    tbl.rows[0].cells[0].text = "Phương pháp"
    tbl.rows[0].cells[1].text = "Độ chính xác R²"
    tbl.rows[0].cells[2].text = "Thời gian phản hồi (ms)"
    
    tbl.rows[1].cells[0].text = "Mô hình ARIMA truyền thống"
    tbl.rows[1].cells[1].text = "0,74"
    tbl.rows[1].cells[2].text = "120,5 ms"
    
    tbl.rows[2].cells[0].text = "Mô hình Đề xuất CNN-LSTM"
    tbl.rows[2].cells[1].text = "0,94"
    tbl.rows[2].cells[2].text = "14,2 ms"
    
    doc.add_heading("3. Kết quả Đo đạc Định lượng", level=2)
    doc.add_paragraph(
        "Kết quả thực nghiệm cho thấy hệ thống đạt độ chính xác dự báo 94,5% và giảm 48,2% lượng hóa chất tiêu thụ trong quá trình keo tụ tạo bông. "
        "The empirical results demonstrate a 94.5% accuracy rate, significantly outperforming baseline systems."
    )
    
    doc.add_heading("4. Giới hạn và Hướng nghiên cứu Tiếp theo", level=2)
    doc.add_paragraph(
        "Một giới hạn then chốt của nghiên cứu là các cảm biến quang học dễ bị bám bẩn trong môi trường nước thải có độ đục cao. "
        "Hướng nghiên cứu tương lai cần tích hợp cơ chế tự làm sạch bằng sóng siêu âm và mở rộng thử nghiệm tại các khu công nghiệp phía Nam."
    )
    
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def test_generate_topic_structured_outline():
    """Kiểm tra chức năng sinh Cây Đề Cương có cấu trúc theo Tên Đề Tài."""
    topic = "Ứng dụng AI và Trí tuệ Nhân tạo trong Xử lý Nước thải Công nghiệp"
    res = document_evidence_extractor.generate_topic_structured_outline(topic)

    assert res["status"] == "success"
    assert "outline_tree" in res
    tree = res["outline_tree"]
    assert "items" in tree
    assert len(tree["items"]) >= 5

    # Kiểm tra tính toàn vẹn cấu trúc từng Node
    for node in tree["items"]:
        assert "node_id" in node
        assert "section_number" in node
        assert "title" in node
        assert "search_keywords" in node
        assert len(node["search_keywords"]) >= 2
        assert "target_categories" in node


def test_extract_evidence_by_topic_outline_with_docs(sample_ai_paper_docx):
    """Kiểm tra quét tài liệu và ánh xạ bằng chứng vào Cây Đề Cương dựa trên Tên Đề Tài."""
    topic = "Ứng dụng Trí tuệ Nhân tạo trong Giám sát Nước thải"
    docs_input = [
        {"filename": "ai_water_treatment_2024.docx", "content_bytes": sample_ai_paper_docx}
    ]

    res = document_evidence_extractor.extract_evidence_by_topic_outline(
        topic=topic,
        provided_documents=docs_input,
        save_docx_report=True
    )

    assert res["status"] == "success"
    assert "summary_statistics" in res
    stats = res["summary_statistics"]
    assert stats["total_outline_nodes"] >= 5
    assert stats["covered_nodes_with_evidence"] >= 2
    assert stats["coverage_rate_percent"] > 0
    assert stats["total_evidence_claims_mapped"] >= 2

    # Kiểm tra các node được ánh xạ
    nodes = res["aligned_nodes"]
    assert len(nodes) >= 5

    # Kiểm tra node có bằng chứng chứa viễn dẫn APA và trích đoạn nguyên văn
    nodes_with_ev = [n for n in nodes if n["has_evidence"]]
    assert len(nodes_with_ev) >= 2
    first_ev = nodes_with_ev[0]["evidence_items"][0]
    assert "apa_pinpoint_citation" in first_ev
    assert "original_verbatim_excerpt" in first_ev
    assert "claim_statement" in first_ev

    # Kiểm tra node không có bằng chứng được gắn nhãn [uncertain]
    empty_nodes = [n for n in nodes if not n["has_evidence"]]
    if empty_nodes:
        assert "[uncertain:" in empty_nodes[0]["uncertainty_flag"]

    # Kiểm tra tệp báo cáo Word .docx được tạo và đọc lại
    docx_rel = res.get("report_docx", {}).get("rel_path")
    assert docx_rel is not None
    full_docx = file_mgr.workspace / docx_rel
    assert full_docx.exists()
    opened_doc = Document(str(full_docx))
    assert len(opened_doc.paragraphs) > 5

    # Kiểm tra tệp Markdown
    md_rel = res.get("report_md", {}).get("rel_path")
    assert md_rel is not None
    assert (file_mgr.workspace / md_rel).exists()


def test_api_endpoints_generate_outline_and_extract_by_topic(client, auth_headers, sample_ai_paper_docx):
    """Kiểm tra các API Router /api/evidence-db/generate-topic-outline và /api/evidence-db/extract-by-topic."""
    topic = "Học sâu trong Phân tích Môi trường Nước"
    
    # 1. Test POST /api/evidence-db/generate-topic-outline
    resp_outline = client.post(
        "/api/evidence-db/generate-topic-outline",
        headers=auth_headers,
        json={"topic": topic}
    )
    assert resp_outline.status_code == 200
    outline_data = resp_outline.json()
    assert outline_data["status"] == "success"
    assert "outline_tree" in outline_data
    assert len(outline_data["outline_tree"]["items"]) >= 5

    # 2. Test POST /api/evidence-db/extract-by-topic
    b64_docx = base64.b64encode(sample_ai_paper_docx).decode("utf-8")
    resp_extract = client.post(
        "/api/evidence-db/extract-by-topic",
        headers=auth_headers,
        json={
            "topic": topic,
            "documents": [
                {
                    "filename": "ai_env_sample.docx",
                    "content_base64": b64_docx
                }
            ],
            "outline": outline_data["outline_tree"],
            "save_docx_report": True
        }
    )
    assert resp_extract.status_code == 200
    extract_res = resp_extract.json()
    assert extract_res["status"] == "success"
    assert "summary_statistics" in extract_res
    assert extract_res["summary_statistics"]["covered_nodes_with_evidence"] >= 2
    assert "aligned_nodes" in extract_res
    assert len(extract_res["aligned_nodes"]) >= 5
