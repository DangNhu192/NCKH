# modules/editorial_office/editorial_router.py
from fastapi import APIRouter, HTTPException, Body, Depends
from modules.auth.auth_service import require_operational_user
from modules.auth.user_config_manager import load_user_config
from modules.editorial_office.editorial_engine import editorial_engine
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

