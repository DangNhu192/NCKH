import sys
from pathlib import Path
import pytest

# Ensure root directory is on sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from modules.humanizer.humanizer_engine import HumanizerEngine
from modules.academic_writer.academic_writer_engine import AcademicWriterEngine
from modules.editorial_office.editorial_engine import EditorialEngine
from modules.shared.skill_prompts import (
    ACADEMIC_WRITER_SYSTEM_PERSONA,
    DRAFTING_PROMPT_TEMPLATE,
    EDITORIAL_OFFICE_EXECUTION_PROMPT,
    UNIFIED_HUMANIZER_TURNITIN_PROMPT_TEMPLATE,
    COUNCIL_OF_10_PROFESSORS_FRAMEWORK
)


def test_humanizer_scientific_hedging_audit_clean_text():
    """Kiểm tra văn bản học thuật chuẩn mực đạt điểm tiết chế tri nhận cao (hedging_score >= 85)."""
    engine = HumanizerEngine()
    clean_academic_text = (
        "Nghiên cứu khảo sát hiệu năng phân loại của mô hình học sâu trên tập dữ liệu thực nghiệm. "
        "Kết quả thực nghiệm bước đầu gợi ý rằng phương pháp mới có khả năng cải thiện độ chính xác "
        "khoảng 4,2% với độ tin cậy 95% (p < 0,05) trong phạm vi mẫu khảo sát. "
        "Dữ liệu quan sát cho thấy xu hướng ổn định của các tham số khi tăng kích thước lô xử lý."
    )
    audit_res = engine.audit_scientific_hedging(clean_academic_text)
    assert audit_res["is_hedged"] is True
    assert audit_res["hedging_score"] >= 85.0
    assert audit_res["total_violations"] == 0
    assert len(audit_res["violations"]) == 0


def test_humanizer_scientific_hedging_audit_violations():
    """Kiểm tra phát hiện chính xác 4 nhóm vi phạm: over-assertion, over-emphasis, purple prose, non-academic."""
    engine = HumanizerEngine()
    flawed_text = (
        "Nghiên cứu này chắc chắn 100% chứng minh tuyệt đối giải pháp đề xuất là chân lý hiển nhiên. "
        "Đây là một bước tiến vĩ đại mang lại thành tựu vô cùng to lớn và vượt trội hoàn toàn. "
        "Bức tranh tráng lệ của công nghệ mở ra như ánh bình minh rực rỡ. "
        "Kết quả đo đạc rất hay và thần kỳ như một phép màu."
    )
    audit_res = engine.audit_scientific_hedging(flawed_text)
    assert audit_res["is_hedged"] is False
    assert audit_res["hedging_score"] < 70.0
    assert audit_res["total_violations"] >= 5

    cat_counts = audit_res["category_counts"]
    assert cat_counts["over_assertion"] >= 2  # chắc chắn 100%, chứng minh tuyệt đối, chân lý hiển nhiên
    assert cat_counts["over_emphasis"] >= 2   # bước tiến vĩ đại, vô cùng to lớn, vượt trội hoàn toàn
    assert cat_counts["purple_prose"] >= 2    # bức tranh tráng lệ, như ánh bình minh
    assert cat_counts["non_academic"] >= 2    # rất hay, thần kỳ, như một phép màu

    assert len(audit_res["recommendations"]) >= 3


def test_deterministic_cliche_replacement_hedging():
    """Kiểm tra bộ chuyển đổi tất định tự động thay thế các từ phóng đại, khẳng định tuyệt đối sang thể tiết chế."""
    engine = HumanizerEngine()
    raw_text = (
        "Kết quả khẳng định chắc chắn mô hình vượt trội hoàn toàn so với baseline. "
        "Nghiên cứu giải quyết triệt để vấn đề và là một thành tựu vĩ đại."
    )
    transformed = engine.replace_cliches_deterministic(raw_text)
    # Các từ vi phạm phải bị thay thế
    assert "khẳng định chắc chắn" not in transformed.lower()
    assert "vượt trội hoàn toàn" not in transformed.lower()
    assert "giải quyết triệt để" not in transformed.lower()
    # Các cụm thay thế học thuật xuất hiện
    assert "kết quả cho thấy" in transformed.lower()
    assert "khả quan hơn" in transformed.lower() or "xử lý hiệu quả" in transformed.lower()


def test_academic_writer_fallback_hedging_and_no_latex_dollars():
    """Kiểm tra fallback của AcademicWriterEngine không chứa cliché, khẳng định quá mức hoặc dấu $ LaTeX trong văn xuôi."""
    engine = AcademicWriterEngine()
    section_text = engine._synthesize_grounded_academic_section(
        section_idx=2,
        section_title="2. CƠ SỞ LÝ THUYẾT & TỔNG QUAN TÀI LIỆU",
        section_subsections=["2.1. Khung lý thuyết", "2.2. Tổng quan tình hình", "2.3. Khoảng trống tri thức"],
        topic="Mạng Nơ-ron Tích Chập Trong Xử Lý Ảnh Y Tế",
        paper_type="Báo cáo khoa học",
        evidence_block="",
        allowed_citation_keys=["Nguyen et al., 2024", "Smith & Jones, 2023"]
    )

    # 1. Không chứa dấu $ đơn lẻ trong văn xuôi tiếng Việt (phải dùng H₁, H₂ thay vì $H_1$, $H_2$)
    assert "$H_1$" not in section_text
    assert "$H_2$" not in section_text
    assert "H₁" in section_text or "H1" in section_text
    assert "H₂" in section_text or "H2" in section_text

    # 2. Không chứa các cliché và khẳng định quá mức
    assert "Trong bối cảnh hiện nay" not in section_text
    assert "bức tranh phát triển đa diện" not in section_text
    assert "khẳng định tính đúng đắn" not in section_text

    # 3. Phải có cờ [uncertain]
    assert "[uncertain" in section_text


def test_editorial_engine_rubric_and_adversarial_hedging():
    """Kiểm tra Q1 Rubric và Adversarial Review trong EditorialEngine phản ứng với over-claiming."""
    engine = EditorialEngine()
    # Văn bản chứa khẳng định tuyệt đối
    over_claimed_text = (
        "Nghiên cứu này chắc chắn 100% chứng minh tuyệt đối thuật toán là chân lý hiển nhiên và hoàn hảo. "
        "Kết quả vô cùng vĩ đại và vượt trội hoàn toàn mọi công trình trong lịch sử."
    )
    rubric_res = engine.evaluate_manuscript_q1_rubric(over_claimed_text, topic="Trí Tuệ Nhân Tạo")
    assert "tiết chế tri nhận" in rubric_res["reviewer_summary"].lower() or "khẳng định quá mức" in rubric_res["reviewer_summary"].lower()

    # Kiểm tra adversarial review template chứa chỉ dẫn tiết chế khoa học
    adv_res = engine.conduct_adversarial_peer_review(over_claimed_text, topic="Trí Tuệ Nhân Tạo")
    assert "adversarial_review" in adv_res
    rev1_focus = adv_res["adversarial_review"]["reviewer_1"]["focus"]
    assert "Epistemic Hedging" in rev1_focus or "Tiết chế" in rev1_focus or "Khung lý thuyết" in rev1_focus


def test_skill_prompts_contain_hedging_framework():
    """Kiểm tra toàn bộ các prompt lõi đều tích hợp chỉ thị Epistemic Hedging và Scientific Restraint."""
    assert "Epistemic Hedging" in ACADEMIC_WRITER_SYSTEM_PERSONA
    assert "khẳng định quá mức" in ACADEMIC_WRITER_SYSTEM_PERSONA.lower()
    assert "miêu tả quá nhiều" in ACADEMIC_WRITER_SYSTEM_PERSONA.lower()
    assert "nhấn mạnh quá mức" in ACADEMIC_WRITER_SYSTEM_PERSONA.lower()

    assert "TIẾT CHẾ HỌC THUẬT" in DRAFTING_PROMPT_TEMPLATE
    assert "TIẾT CHẾ HỌC THUẬT" in EDITORIAL_OFFICE_EXECUTION_PROMPT
    assert "EPISTEMIC HEDGING" in UNIFIED_HUMANIZER_TURNITIN_PROMPT_TEMPLATE
    assert "over-claiming" in COUNCIL_OF_10_PROFESSORS_FRAMEWORK.lower()
