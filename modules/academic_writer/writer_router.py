# modules/academic_writer/writer_router.py
from fastapi import APIRouter, HTTPException, Body, Depends
from modules.auth.auth_service import require_operational_user
from modules.auth.user_config_manager import load_user_config
from modules.academic_writer.academic_writer_engine import academic_writer
from modules.history.history_manager import history_mgr

writer_router = APIRouter(tags=["Academic Writer 2-File Paradigm & Deep Research"])

@writer_router.post("/api/writer/outline")
def propose_academic_outline(payload: dict = Body(...), user: dict = Depends(require_operational_user)):
    topic = payload.get("topic", "")
    paper_type = payload.get("paper_type", "Báo cáo khoa học")
    if not topic:
        raise HTTPException(status_code=400, detail="Vui lòng nhập chủ đề.")
    user_cfg = load_user_config(user)
    gemini_key = user_cfg.get("gemini_api_key", "").strip() or None
    openai_key = user_cfg.get("openai_api_key", "").strip() or None
    res = academic_writer.propose_structure(topic, paper_type=paper_type, gemini_key=gemini_key, openai_key=openai_key)
    try:
        history_mgr.add_entry(
            module="writer",
            action_title=f"Đề xuất Dàn ý Cấu trúc: {topic}",
            inputs={"topic": topic, "paper_type": paper_type},
            result_data=res,
            summary=f"Đã lập khung cấu trúc đề xuất ({paper_type})"
        )
    except Exception:
        pass
    return res

@writer_router.post("/api/writer/outline/structured")
def propose_structured_outline(payload: dict = Body(...), user: dict = Depends(require_operational_user)):
    """Phase 1: Khởi tạo cây đề cương phân nhánh (Tree Schema) chuẩn RhinoInsight."""
    topic = payload.get("topic", "")
    paper_type = payload.get("paper_type", "Báo cáo khoa học")
    depth_level = payload.get("depth_level", "comprehensive")
    if not topic:
        raise HTTPException(status_code=400, detail="Vui lòng nhập chủ đề.")
    user_cfg = load_user_config(user)
    gemini_key = user_cfg.get("gemini_api_key", "").strip() or None
    openai_key = user_cfg.get("openai_api_key", "").strip() or None
    res = academic_writer.propose_structured_outline(
        topic,
        paper_type=paper_type,
        depth_level=depth_level,
        gemini_key=gemini_key,
        openai_key=openai_key
    )
    try:
        history_mgr.add_entry(
            module="writer",
            action_title=f"Đề xuất Cây Đề Cương Cấu Trúc: {topic}",
            inputs={"topic": topic, "paper_type": paper_type, "depth_level": depth_level},
            result_data=res,
            summary=f"Đã lập Outline Tree ({len(res.get('outline_tree', {}).get('items', []))} chương mục)"
        )
    except Exception:
        pass
    return res

@writer_router.post("/api/writer/outline/expand-branch")
def expand_outline_branch(payload: dict = Body(...), user: dict = Depends(require_operational_user)):
    """Phase 1: Mở rộng nhánh luận điểm (Add Items / Sub-branches) trong cây đề cương."""
    topic = payload.get("topic", "")
    outline_tree = payload.get("outline_tree", {})
    target_node_id = payload.get("target_node_id", "")
    expansion_prompt = payload.get("expansion_prompt", "")
    
    if not topic:
        raise HTTPException(status_code=400, detail="Vui lòng cung cấp chủ đề nghiên cứu.")
    
    user_cfg = load_user_config(user)
    gemini_key = user_cfg.get("gemini_api_key", "").strip() or None
    openai_key = user_cfg.get("openai_api_key", "").strip() or None
    
    res = academic_writer.expand_outline_branch(
        topic=topic,
        outline_tree=outline_tree,
        target_node_id=target_node_id,
        expansion_prompt=expansion_prompt,
        gemini_key=gemini_key,
        openai_key=openai_key
    )
    return res

@writer_router.post("/api/writer/outline/add-dimension")
def add_outline_dimension(payload: dict = Body(...), user: dict = Depends(require_operational_user)):
    """Phase 1: Bổ sung chiều thông tin / tiêu chí phân tích (Add Dimensions / Fields)."""
    topic = payload.get("topic", "")
    outline_tree = payload.get("outline_tree", {})
    dimension_name = payload.get("dimension_name", "")
    dimension_description = payload.get("dimension_description", "")
    
    if not dimension_name:
        raise HTTPException(status_code=400, detail="Vui lòng nhập tên chiều phân tích cần thêm.")
    
    res = academic_writer.add_outline_dimension(
        topic=topic,
        outline_tree=outline_tree,
        dimension_name=dimension_name,
        dimension_description=dimension_description
    )
    return res

@writer_router.post("/api/writer/outline/lock")
def lock_outline_structure(payload: dict = Body(...), user: dict = Depends(require_operational_user)):
    """Phase 1 Approval Gate: Khóa & Phê duyệt cấu trúc đề cương trước khi điều tra sâu."""
    topic = payload.get("topic", "")
    outline_tree = payload.get("outline_tree", {})
    
    res = academic_writer.lock_structured_outline(
        topic=topic,
        outline_tree=outline_tree
    )
    return res

@writer_router.post("/api/writer/generate-2file")
def generate_2file_report(payload: dict = Body(...), user: dict = Depends(require_operational_user)):
    topic = payload.get("topic", "")
    paper_type = payload.get("paper_type", "Báo cáo khoa học")
    author_name = payload.get("author_name", "Học viên")
    course_name = payload.get("course_name", "")
    custom_outline = payload.get("custom_outline", None)
    outline_tree = payload.get("outline_tree", None)
    
    if not topic:
        raise HTTPException(status_code=400, detail="Vui lòng nhập chủ đề.")
    
    full_author = f"{author_name} ({course_name})" if course_name else author_name
    
    user_cfg = load_user_config(user)
    gemini_key = user_cfg.get("gemini_api_key", "").strip() or None
    openai_key = user_cfg.get("openai_api_key", "").strip() or None
    
    res = academic_writer.generate_2_files(
        topic,
        paper_type=paper_type,
        author_name=full_author,
        custom_outline=custom_outline,
        outline_tree=outline_tree,
        gemini_key=gemini_key,
        openai_key=openai_key
    )
    try:
        history_mgr.add_entry(
            module="writer",
            action_title=f"Viết học thuật 2-File: {topic}",
            inputs={"topic": topic, "paper_type": paper_type, "author_name": full_author, "custom_outline": custom_outline},
            result_data=res,
            summary=f"Tệp A: {res.get('file_a', {}).get('docx')} | Tệp B: {res.get('file_b', {}).get('docx')}"
        )
    except Exception:
        pass
    return res
