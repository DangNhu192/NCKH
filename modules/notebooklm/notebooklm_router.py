# modules/notebooklm/notebooklm_router.py
"""
FastAPI Router for Open-Notebook (Open Source NotebookLM).
Provides comprehensive REST endpoints for Notebooks, Sources, Hybrid Retrieval, Grounded Chat, and Transformations.
"""

from fastapi import APIRouter, HTTPException, Body, Depends, UploadFile, File, Form
from typing import Optional, List
from pathlib import Path
import json

from modules.auth.auth_service import require_operational_user
from modules.notebooklm.notebooklm_engine import open_notebook_engine, notebooklm_engine
from modules.history.history_manager import history_mgr
from modules.shared.file_manager import file_mgr

notebooklm_router = APIRouter(tags=["Open-Notebook Knowledge Management"])


# 1. NOTEBOOKS CRUD
@notebooklm_router.get("/api/notebooklm/notebooks")
@notebooklm_router.get("/api/open-notebook/list")
def list_notebooks(user: dict = Depends(require_operational_user)):
    """Lấy danh sách tất cả các Notebooks."""
    return {
        "status": "success",
        "notebooks": open_notebook_engine.list_notebooks()
    }


@notebooklm_router.post("/api/notebooklm/notebooks")
def create_notebook(payload: dict = Body(...), user: dict = Depends(require_operational_user)):
    """Tạo một Notebook nghiên cứu mới."""
    name = payload.get("name", "").strip()
    topic = payload.get("topic", "").strip()
    desc = payload.get("description", "").strip()
    if not name and not topic:
        raise HTTPException(status_code=400, detail="Vui lòng nhập tên hoặc đề tài cho Notebook.")
    
    nb = open_notebook_engine.create_notebook(name=name or topic, topic=topic or name, description=desc)
    history_mgr.add_entry(
        module="notebooklm",
        action_title=f"Tạo Notebook: {nb['name']}",
        inputs={"name": name, "topic": topic},
        result_data=nb,
        summary=f"Đã tạo Notebook mới (ID: {nb['id']})"
    )
    return {
        "status": "success",
        "notebook": nb,
        "message": f"Đã tạo Notebook '{nb['name']}' thành công."
    }


@notebooklm_router.get("/api/notebooklm/notebooks/{notebook_id}")
def get_notebook_details(notebook_id: str, user: dict = Depends(require_operational_user)):
    """Lấy chi tiết Notebook kèm danh sách tài liệu và tệp phái sinh."""
    try:
        return open_notebook_engine.get_notebook_details(notebook_id)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@notebooklm_router.delete("/api/notebooklm/notebooks/{notebook_id}")
def delete_notebook(notebook_id: str, user: dict = Depends(require_operational_user)):
    """Xóa một Notebook."""
    res = open_notebook_engine.delete_notebook(notebook_id)
    history_mgr.add_entry(
        module="notebooklm",
        action_title=f"Xóa Notebook: {notebook_id}",
        inputs={"notebook_id": notebook_id},
        result_data=res,
        summary=f"Đã xóa Notebook {notebook_id}"
    )
    return res


# 2. SOURCES MANAGEMENT
@notebooklm_router.post("/api/notebooklm/notebooks/{notebook_id}/sources/upload")
async def upload_source_file(
    notebook_id: str,
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    author: Optional[str] = Form(None),
    year: Optional[str] = Form(None),
    doi: Optional[str] = Form(None),
    user: dict = Depends(require_operational_user)
):
    """Tải lên tệp Word/PDF/MD/TXT và nạp vào Notebook."""
    try:
        file_bytes = await file.read()
        save_dir = file_mgr.docs_dir
        save_dir.mkdir(parents=True, exist_ok=True)
        dest_path = save_dir / file.filename
        dest_path.write_bytes(file_bytes)

        meta = {
            "title": title or Path(file.filename).stem.replace("_", " "),
            "author": author or "Tác giả Khoa học",
            "year": year or "",
            "doi": doi or ""
        }
        res = open_notebook_engine.add_source_from_file(notebook_id, dest_path, metadata=meta)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi nạp tệp tài liệu: {str(e)}")


@notebooklm_router.post("/api/notebooklm/notebooks/{notebook_id}/sources/raw")
def add_raw_text_source(notebook_id: str, payload: dict = Body(...), user: dict = Depends(require_operational_user)):
    """Nạp văn bản thô / ghi chú cá nhân / nội dung Web vào Notebook."""
    title = payload.get("title", "").strip() or "Ghi chú Nghiên cứu"
    content = payload.get("content", "").strip()
    author = payload.get("author", "")
    year = payload.get("year", "")
    doi = payload.get("doi", "")
    source_type = payload.get("source_type", "TEXT")
    if not content:
        raise HTTPException(status_code=400, detail="Nội dung tài liệu không được để trống.")
    
    return open_notebook_engine.add_source_from_raw(
        notebook_id, title=title, content=content, author=author, year=year, doi=doi, source_type=source_type
    )


@notebooklm_router.post("/api/notebooklm/notebooks/{notebook_id}/sources/import-workspace")
def import_source_from_workspace(notebook_id: str, payload: dict = Body(...), user: dict = Depends(require_operational_user)):
    """Nạp tệp đã có trong Tai_Lieu/ vào Notebook."""
    file_name = payload.get("file_name", "").strip()
    if not file_name:
        raise HTTPException(status_code=400, detail="Vui lòng chọn tên tệp trong Tai_Lieu/.")
    
    fpath = file_mgr.docs_dir / file_name
    if not fpath.exists():
        raise HTTPException(status_code=404, detail=f"Không tìm thấy tệp '{file_name}' trong thư mục Tai_Lieu/.")
    
    return open_notebook_engine.add_source_from_file(notebook_id, fpath)


@notebooklm_router.post("/api/notebooklm/notebooks/{notebook_id}/sources/url")
def add_source_from_url(notebook_id: str, payload: dict = Body(...), user: dict = Depends(require_operational_user)):
    """Thu thập và nạp trực tiếp tài liệu từ URL web hoặc PDF vào Notebook (hỗ trợ Obscura stealth)."""
    url = payload.get("url", "").strip()
    if not url:
        raise HTTPException(status_code=400, detail="Vui lòng cung cấp URL bài báo hoặc trang web.")
    try:
        res = open_notebook_engine.add_source_from_url(notebook_id, url=url, metadata=payload)
        history_mgr.add_entry(
            module="notebooklm",
            action_title=f"Nạp nguồn từ URL: {url[:50]}",
            inputs={"notebook_id": notebook_id, "url": url},
            result_data=res,
            summary="Đã nạp thành công tài liệu từ URL vào Notebook"
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi thu thập dữ liệu từ URL: {str(e)}")


@notebooklm_router.get("/api/notebooklm/notebooks/{notebook_id}/export/ris")
def export_notebook_to_ris(notebook_id: str, user: dict = Depends(require_operational_user)):
    """Xuất toàn bộ danh mục tài liệu trong Notebook ra tệp RIS tương thích Zotero/Mendeley."""
    try:
        ris_path = open_notebook_engine.export_notebook_to_ris(notebook_id)
        return {
            "status": "success",
            "ris_path": str(ris_path),
            "file_name": ris_path.name,
            "message": "Đã xuất tệp RIS thành công, sẵn sàng nhập vào Zotero."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xuất tệp RIS: {str(e)}")


@notebooklm_router.delete("/api/notebooklm/notebooks/{notebook_id}/sources/{source_id}")
def delete_source(notebook_id: str, source_id: str, user: dict = Depends(require_operational_user)):
    """Xóa một tài liệu nguồn khỏi Notebook."""
    return open_notebook_engine.delete_source(notebook_id, source_id)


# 3. HYBRID SEARCH & RETRIEVAL
@notebooklm_router.post("/api/notebooklm/notebooks/{notebook_id}/search")
def search_notebook(notebook_id: str, payload: dict = Body(...), user: dict = Depends(require_operational_user)):
    """Tìm kiếm lai (BM25 + Semantic Cosine) trên toàn bộ phân đoạn của Notebook."""
    query = payload.get("query", "").strip()
    top_k = int(payload.get("top_k", 6))
    source_id = payload.get("source_id", None)
    target_section = payload.get("target_section", None)
    if not query:
        return {"status": "success", "query": query, "results": []}
    
    results = open_notebook_engine.hybrid_search(
        notebook_id,
        query=query,
        top_k=top_k,
        source_id=source_id,
        target_section=target_section
    )
    return {
        "status": "success",
        "query": query,
        "total_matches": len(results),
        "results": results
    }


# 4. GROUNDED CHAT & Q&A
@notebooklm_router.post("/api/notebooklm/notebooks/{notebook_id}/chat")
def chat_with_notebook(notebook_id: str, payload: dict = Body(...), user: dict = Depends(require_operational_user)):
    """Trò chuyện đối soát nguồn với tài liệu trong Notebook."""
    from modules.auth.user_config_manager import load_user_config
    cfg = load_user_config(user)
    user_api_key = cfg.get("gemini_api_key", "").strip() or None

    message = payload.get("message", "").strip()
    selected_source_ids = payload.get("selected_source_ids", None)
    if not message:
        raise HTTPException(status_code=400, detail="Vui lòng nhập câu hỏi.")
    
    res = open_notebook_engine.chat_with_notebook(notebook_id, message=message, selected_source_ids=selected_source_ids, api_key=user_api_key)
    history_mgr.add_entry(
        module="notebooklm",
        action_title=f"Chat Kho Tri Thức: {message[:40]}...",
        inputs={"notebook_id": notebook_id, "question": message},
        result_data=res,
        summary=f"Đã trả lời câu hỏi với {len(res.get('citations', []))} trích dẫn đối soát"
    )
    return res


@notebooklm_router.get("/api/notebooklm/notebooks/{notebook_id}/chat/history")
def get_chat_history(notebook_id: str, user: dict = Depends(require_operational_user)):
    """Lấy lịch sử hội thoại của Notebook."""
    return {
        "status": "success",
        "history": open_notebook_engine.get_chat_history(notebook_id)
    }


@notebooklm_router.delete("/api/notebooklm/notebooks/{notebook_id}/chat/history")
def clear_chat_history(notebook_id: str, user: dict = Depends(require_operational_user)):
    """Xóa lịch sử hội thoại của Notebook."""
    return open_notebook_engine.clear_chat_history(notebook_id)


# 5. RESEARCH TRANSFORMATIONS STUDIO
@notebooklm_router.post("/api/notebooklm/notebooks/{notebook_id}/transform")
def generate_transformation(notebook_id: str, payload: dict = Body(...), user: dict = Depends(require_operational_user)):
    """
    Sinh các sản phẩm nghiên cứu chuyên sâu:
    - podcast_script: Kịch bản Audio Podcast 2 người đàm thoại
    - study_guide: Sổ tay hướng dẫn nghiên cứu & Tóm lược
    - faq: Bộ câu hỏi thường gặp & Câu hỏi phản biện bảo vệ
    - synthesis_matrix: Ma trận so sánh phương pháp và kết quả thực nghiệm
    - research_gaps: Phân tích khoảng trống nghiên cứu và xu hướng
    """
    transform_type = payload.get("transform_type", "study_guide").strip()
    custom_instructions = payload.get("custom_instructions", "")
    
    from modules.auth.user_config_manager import load_user_config
    cfg = load_user_config(user)
    user_api_key = cfg.get("gemini_api_key", "").strip() or None

    res = open_notebook_engine.generate_transformation(
        notebook_id, transform_type=transform_type, custom_instructions=custom_instructions, api_key=user_api_key
    )
    history_mgr.add_entry(
        module="notebooklm",
        action_title=f"Sinh Transform: {transform_type}",
        inputs={"notebook_id": notebook_id, "type": transform_type},
        result_data=res,
        summary=f"Đã tạo {res.get('artifact_name', 'Artifact')}"
    )
    return res


@notebooklm_router.post("/api/notebooklm/notebooks/{notebook_id}/literature-matrix")
def generate_literature_matrix_endpoint(notebook_id: str, payload: dict = Body({}), user: dict = Depends(require_operational_user)):
    """Tự động sinh Ma Trận Tổng Thuật Y Văn (Literature Review Matrix)."""
    from modules.auth.user_config_manager import load_user_config
    cfg = load_user_config(user)
    user_api_key = cfg.get("gemini_api_key", "").strip() or None

    selected_source_ids = payload.get("selected_source_ids", None)
    res = open_notebook_engine.generate_literature_matrix(notebook_id, selected_source_ids=selected_source_ids, api_key=user_api_key)
    history_mgr.add_entry(
        module="notebooklm",
        action_title=f"Lập Ma Trận Y Văn: {res.get('topic')}",
        inputs={"notebook_id": notebook_id, "selected_sources": selected_source_ids},
        result_data=res,
        summary=f"Đã lập Ma Trận Y Văn với {res.get('total_papers', 0)} bài báo"
    )
    return res


# 6. LEGACY / PIPELINE STEP 2 SYNC COMPATIBILITY
@notebooklm_router.post("/api/notebooklm/sync")
def sync_notebooklm_knowledge_base(payload: dict = Body(...), user: dict = Depends(require_operational_user)):
    """Đồng bộ kho tri thức từ Bước 2 của Pipeline."""
    topic = payload.get("topic", "").strip()
    target_papers = payload.get("target_papers", [])
    custom_url = payload.get("custom_url", None)
    if not topic:
        raise HTTPException(status_code=400, detail="Vui lòng nhập chủ đề.")
    
    res = open_notebook_engine.sync_knowledge_base(topic, target_papers=target_papers, custom_url=custom_url)
    history_mgr.add_entry(
        module="notebooklm",
        action_title=f"Đồng bộ Kho Tri Thức: {topic}",
        inputs={"topic": topic, "target_papers_count": len(target_papers)},
        result_data=res,
        summary=f"Đã đồng bộ {res.get('documents_synced', 0)} tài liệu vào Open-Notebook"
    )
    return res

