# modules/editorial_office/editorial_router.py
from fastapi import APIRouter, HTTPException, Body, Depends
from modules.auth.auth_service import require_operational_user
from modules.auth.user_config_manager import load_user_config
from modules.editorial_office.editorial_engine import editorial_engine
from modules.shared.academic_fact_checker import academic_fact_checker
from modules.history.history_manager import history_mgr

editorial_router = APIRouter(tags=["Editorial Office AI v3.1 6-GATE"])

@editorial_router.get("/api/editorial/departments")
def get_editorial_departments():
    return editorial_engine.get_departments()

@editorial_router.post("/api/editorial/analyze")
def analyze_editorial_request(payload: dict = Body(...), user: dict = Depends(require_operational_user)):
    topic = payload.get("topic", "")
    user_input = payload.get("user_input", "ý tưởng")
    purpose = payload.get("purpose", "inform")
    audience = payload.get("audience", "công chúng")
    platform = payload.get("platform", "báo cáo")
    need_fact_check = payload.get("need_fact_check", True)
    if not topic:
        raise HTTPException(status_code=400, detail="Vui lòng nhập chủ đề.")
    return editorial_engine.analyze_request(topic, user_input, purpose, audience, platform, need_fact_check)

@editorial_router.post("/api/editorial/execute-gate")
def execute_editorial_gate(payload: dict = Body(...), user: dict = Depends(require_operational_user)):
    topic = payload.get("topic", "")
    gate_steps = payload.get("gate_steps", [])
    source_content = payload.get("source_content", "")
    if not topic or not gate_steps:
        raise HTTPException(status_code=400, detail="Topic và gate_steps là bắt buộc.")
    user_cfg = load_user_config(user)
    gemini_key = user_cfg.get("gemini_api_key", "").strip() or None
    openai_key = user_cfg.get("openai_api_key", "").strip() or None
    res = editorial_engine.execute_gate_workflow(
        topic,
        gate_steps,
        source_content=source_content,
        gemini_key=gemini_key,
        openai_key=openai_key
    )
    history_mgr.add_entry(
        module="editorial",
        action_title=f"Ấn phẩm Tòa Soạn Báo GATE: {topic}",
        inputs={"topic": topic, "gate_steps": gate_steps, "has_source": bool(source_content)},
        result_data=res,
        summary=f"Đã xuất bản qua 4 trạm GATE: {res.get('output_file', '')}"
    )
    return res


@editorial_router.post("/api/editorial/evaluate-q1")
def evaluate_q1_manuscript(payload: dict = Body(...), user: dict = Depends(require_operational_user)):
    """Chấm điểm bài báo theo Rubric ISI/Scopus Q1 (5 Tiêu chí, thang điểm 100)."""
    content = payload.get("content", "")
    topic = payload.get("topic", "Bài Báo Khoa Học")
    if not content:
        raise HTTPException(status_code=400, detail="Vui lòng cung cấp nội dung bản thảo.")
    return editorial_engine.evaluate_manuscript_q1_rubric(content, topic=topic)


@editorial_router.post("/api/editorial/adversarial-review")
def conduct_adversarial_review(payload: dict = Body(...), user: dict = Depends(require_operational_user)):
    """Chế độ Tranh luận học thuật AI: Giả lập 2 Reviewer ẩn danh và sinh Thư giải trình Rebuttal Letter."""
    content = payload.get("content", "")
    topic = payload.get("topic", "Bài Báo Khoa Học")
    if not content:
        raise HTTPException(status_code=400, detail="Vui lòng cung cấp nội dung bản thảo.")
    return editorial_engine.conduct_adversarial_peer_review(content, topic=topic)


@editorial_router.post("/api/editorial/looped-flows-audit")
@editorial_router.post("/api/reasoning/looped-flows/audit")
def audit_text_looped_flows(payload: dict = Body(...), user: dict = Depends(require_operational_user)):
    """Kiểm toán độc lập bất kỳ văn bản nào theo Giao thức Suy luận Luồng lặp Looped Flows (arXiv:2609.11801)."""
    text = payload.get("text") or payload.get("content", "")
    topic = payload.get("topic", "")
    evidence_claims = payload.get("evidence_claims") or []
    if not text:
        raise HTTPException(status_code=400, detail="Vui lòng cung cấp văn bản cần kiểm định.")
    from modules.shared.looped_flows_engine import looped_flows_engine
    return looped_flows_engine.audit_text_with_looped_flows(text, evidence_claims=evidence_claims, topic=topic)


@editorial_router.get("/api/reasoning/looped-flows/status")
def get_looped_flows_status():
    """Lấy trạng thái và thông số cấu hình của Looped Flows Reasoning Engine."""
    return {
        "status": "online",
        "protocol": "Looped Flows Reasoning (arXiv:2609.11801v1)",
        "version": "1.0",
        "act_threshold": 0.95,
        "gamma_backtrack": 0.20,
        "features": [
            "Continuous Probability Transport (Velocity field b_t)",
            "Temporally Aligned Denoising Stages (t_0 -> t_k)",
            "Stepwise Relative Residual Convergence (R_i)",
            "Spurious Attractor Detection (Overconfidence Guard)",
            "Stochastic Noise-Backtracking via SDE",
            "Adaptive Computation Time (ACT) Saturated Stopping",
            "Best-Q Trajectory Ensembling"
        ]
    }


# ─── 4. ACADEMIC FACT-CHECKER & GROUND-TRUTH VERIFICATION (EDGE COPILOT REVERSE PROTOCOL) ───

@editorial_router.post("/api/editorial/fact-check")
def fact_check_academic_manuscript(payload: dict = Body(...), user: dict = Depends(require_operational_user)):
    """
    Tự động hóa kiểm chứng thực chứng (Zero-Hallucination Fact-Checking):
    - Trích xuất dấu chân số liệu định lượng (Footprint Extraction).
    - Đối chiếu Ground-Truth với cơ sở dữ liệu thực nghiệm hoặc DOI gốc.
    - Kiểm tra phản hồi HTTP 200 OK của các DOI / URLs.
    - Phát hiện nguồn trích dẫn mồ côi hoặc số liệu nghi vấn bịa đặt.
    """
    text = payload.get("text", "")
    if not text or not text.strip():
        raise HTTPException(status_code=400, detail="Vui lòng cung cấp nội dung bản thảo cần kiểm chứng.")

    evidence_claims = payload.get("evidence_claims")
    allowed_dois = payload.get("allowed_dois")

    result = academic_fact_checker.verify_text_against_evidence(
        text=text,
        evidence_claims=evidence_claims,
        allowed_dois=allowed_dois
    )

    history_mgr.add_entry(
        module="editorial",
        action_title=f"Kiểm chứng Liêm chính Thực chứng ({result.get('grade')} - {result.get('fact_check_score')}đ)",
        inputs={"total_claims": result.get("total_quantitative_claims")},
        result_data=result,
        summary=f"Điểm kiểm chứng: {result.get('fact_check_score')}/100. Đạt {result.get('verified_claims_count')} mệnh đề hợp lệ."
    )

    return {
        "status": "success",
        "data": result,
        "message": "Đã hoàn thành kiểm định liêm chính học thuật thực chứng."
    }

