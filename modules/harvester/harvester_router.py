# modules/harvester/harvester_router.py
"""
Data Harvester API Router for WEB SUPER v2.0
Supports multi-source academic harvesting (EuropePMC, OpenAlex, CrossRef, ArXiv, Google Scholar)
and Zotero sync / desktop connector.
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Body, Depends

from modules.auth.auth_service import require_operational_user
from modules.auth.user_config_manager import load_user_config
from modules.harvester.data_harvesting_engine import data_harvester
from modules.history.history_manager import history_mgr

harvester_router = APIRouter(tags=["Data Harvester"])


# ─── 1. BOOLEAN QUERY GENERATOR ───────────────────────────────────────────────

@harvester_router.post("/api/harvest/query")
@harvester_router.post("/api/harvester/query")
def generate_search_query(payload: dict = Body(...), user: dict = Depends(require_operational_user)):
    topic = payload.get("topic", "")
    if not topic:
        raise HTTPException(status_code=400, detail="Vui lòng nhập chủ đề.")
    user_cfg = load_user_config(user) if user else {}
    api_key = payload.get("api_key") or user_cfg.get("gemini_api_key", "").strip() or None
    return data_harvester.generate_boolean_query(topic, api_key=api_key)


@harvester_router.post("/api/harvest/multilingual-keywords")
@harvester_router.post("/api/harvester/multilingual-keywords")
def convert_multilingual_keywords(payload: dict = Body(...), user: dict = Depends(require_operational_user)):
    keywords = payload.get("keywords", [])
    topic = payload.get("topic", "")
    if not keywords and not topic:
        raise HTTPException(status_code=400, detail="Vui lòng cung cấp danh sách từ khóa hoặc chủ đề.")
    user_cfg = load_user_config(user) if user else {}
    api_key = payload.get("api_key") or user_cfg.get("gemini_api_key", "").strip() or None
    return data_harvester.translate_keywords_multilingual(keywords, topic=topic, api_key=api_key)


@harvester_router.post("/api/harvest/research-trends")
@harvester_router.post("/api/harvester/research-trends")
def get_research_trends(payload: dict = Body(...), user: dict = Depends(require_operational_user)):
    topic = payload.get("topic", "")
    query = payload.get("query", "")
    if not topic and not query:
        raise HTTPException(status_code=400, detail="Vui lòng cung cấp chủ đề hoặc câu truy vấn.")
    return data_harvester.fetch_research_trends(topic, query=query)


# ─── 2. SEARCH / HARVEST PAPERS ───────────────────────────────────────────────

@harvester_router.post("/api/harvest/run")
@harvester_router.post("/api/harvester/search")
def run_paper_harvest(payload: dict = Body(...), user: dict = Depends(require_operational_user)):
    topic = payload.get("topic", "")
    custom_query = payload.get("custom_query", "")
    max_papers = int(payload.get("max_papers", 10))
    language = str(payload.get("language", "all")).strip().lower()
    
    # Handle source / sources
    source = payload.get("source") or payload.get("preferred_source")
    if not source and "sources" in payload:
        sources_val = payload.get("sources")
        source = sources_val[0] if isinstance(sources_val, list) and sources_val else "all"
    source = source or "all"
    
    auto_save = bool(payload.get("auto_save", False))
    custom_storage = payload.get("custom_storage_dir") or payload.get("storage_dir")
    if not topic and not custom_query:
        raise HTTPException(status_code=400, detail="Vui lòng nhập chủ đề hoặc câu truy vấn.")

    search_topic = topic or custom_query
    
    res = data_harvester.search_candidates(search_topic, max_papers=max_papers, preferred_source=source, language=language, custom_query=custom_query)
    if auto_save:
        save_res = data_harvester.save_all_papers([p["id"] for p in res.get("papers", [])], custom_storage_dir=custom_storage)
        res["saved_papers"] = save_res.get("files", [])
        res["total_harvested"] = save_res.get("total_saved", 0)

    history_mgr.add_entry(
        module="harvester",
        action_title=f"Thu thập tài liệu: {search_topic}",
        inputs={"topic": search_topic, "max_papers": max_papers, "source": source},
        result_data=res,
        summary=f"Tìm thấy {res.get('total_found', len(res.get('papers', [])))} bài báo khoa học"
    )
    return res


# ─── 3. SAVE SINGLE PAPER TO ZOTERO & WORKSPACE ───────────────────────────────

@harvester_router.post("/api/harvest/save-to-zotero")
@harvester_router.post("/api/harvester/save-zotero")
def save_single_paper_to_zotero(payload: dict = Body(...), user: dict = Depends(require_operational_user)):
    paper_data = payload.get("paper_data", {})
    paper_id = payload.get("paper_id")
    custom_storage = payload.get("custom_storage_dir") or payload.get("storage_dir")
    if not paper_data and not paper_id:
        raise HTTPException(status_code=400, detail="Thiếu paper_data hoặc paper_id")
    
    res = data_harvester.save_paper_to_zotero(paper_id=paper_id, paper_data=paper_data, custom_storage_dir=custom_storage)
    return res


# ─── 4. SAVE BATCH PAPERS TO ZOTERO & WORKSPACE ───────────────────────────────

@harvester_router.post("/api/harvest/batch-save-to-zotero")
@harvester_router.post("/api/harvester/save-all-zotero")
def batch_save_papers_to_zotero(payload: dict = Body(...), user: dict = Depends(require_operational_user)):
    paper_ids = payload.get("paper_ids")
    papers = payload.get("papers")
    custom_storage = payload.get("custom_storage_dir") or payload.get("storage_dir")
    
    if not paper_ids and isinstance(papers, list):
        paper_ids = [p.get("id") for p in papers if isinstance(p, dict) and p.get("id")]
    
    res = data_harvester.save_all_papers(paper_ids=paper_ids, custom_storage_dir=custom_storage)
    history_mgr.add_entry(
        module="harvester",
        action_title=f"Lưu hàng loạt {res.get('total_saved', 0)} bài báo vào Zotero & Workspace",
        inputs={"total_requested": len(paper_ids) if paper_ids else 0},
        result_data=res,
        summary=f"Thành công: {res.get('total_saved', 0)} bài báo"
    )
    return res


# ─── 5. CLEAR TEMPORARY SEARCH CACHE ──────────────────────────────────────────

@harvester_router.post("/api/harvester/clear-cache")
def clear_search_cache(user: dict = Depends(require_operational_user)):
    return data_harvester.clear_temp_cache()


# ─── 6. UPLOAD USER PAPER FILE & AUTO-CONVERT TO .MD / .DOCX ──────────────────

from fastapi import UploadFile, File, Form
import json

@harvester_router.post("/api/harvest/upload-paper-file")
@harvester_router.post("/api/harvester/upload-paper-file")
async def upload_paper_file(
    file: UploadFile = File(...),
    paper_id: Optional[str] = Form(None),
    paper_data: Optional[str] = Form(None),
    custom_storage_dir: Optional[str] = Form(None),
    user: dict = Depends(require_operational_user)
):
    try:
        content = await file.read()
        parsed_paper = {}
        if paper_data:
            try:
                parsed_paper = json.loads(paper_data)
            except Exception:
                pass
        if paper_id and not parsed_paper.get("id"):
            parsed_paper["id"] = paper_id

        res = data_harvester.process_user_uploaded_paper_file(
            file_bytes=content,
            filename=file.filename or "uploaded_document.pdf",
            paper_data=parsed_paper,
            custom_storage_dir=custom_storage_dir
        )
        if res.get("status") == "error":
            return res

        history_mgr.add_entry(
            module="harvester",
            action_title=f"Nạp & chuyển đổi .MD cho tài liệu: {parsed_paper.get('title') or file.filename}",
            inputs={"filename": file.filename, "paper_id": paper_id},
            result_data=res,
            summary=f"Chuyển đổi thành công {res.get('word_count', 0)} từ sang Markdown và Word"
        )
        return res
    except Exception as e:
        return {
            "status": "error",
            "error_code": "UPLOAD_PROCESSING_ERROR",
            "message": f"⚠️ Lỗi xử lý tệp tải lên: {str(e)}"
        }


# ─── 7. TẢI FILE PDF GỐC VỀ MÁY TÍNH NGƯỜI DÙNG ─────────────────────────────

@harvester_router.get("/api/harvest/download-pdf/{paper_id}")
@harvester_router.post("/api/harvest/download-pdf")
def download_paper_pdf(
    paper_id: str = None,
    payload: dict = Body(default={}),
    user: dict = Depends(require_operational_user)
):
    """
    Tải file PDF gốc về máy tính (lưu vào Workspace/Tai_Lieu/PDFs/).
    Chỉ tải từ nguồn Open Access chính thức (OpenAlex, Unpaywall, PMC, arXiv).
    TUYỆT ĐỐI KHÔNG tạo nội dung giả — nếu không tìm thấy PDF, trả về thông báo rõ ràng.
    """
    pid = paper_id or payload.get("paper_id")
    paper_data = payload.get("paper_data", {})
    custom_storage = payload.get("custom_storage_dir")
    
    paper = {}
    if pid and pid in data_harvester._temp_cache:
        paper = data_harvester._temp_cache[pid]
    elif paper_data:
        paper = paper_data
    else:
        raise HTTPException(status_code=400, detail="Cần cung cấp paper_id hoặc paper_data.")
    
    res = data_harvester.download_pdf_to_disk(paper, custom_storage_dir=custom_storage)
    return res


# ─── 8. KIỂM TRA TÍNH TOÀN VẸN BÓC TÁCH ────────────────────────────────────

@harvester_router.post("/api/harvest/integrity-check")
def check_extraction_integrity(payload: dict = Body(...), user: dict = Depends(require_operational_user)):
    """
    Kiểm tra tính toàn vẹn nội dung bóc tách từ tài liệu.
    Trả về: word_count, completeness%, sections_found, quality (HIGH/MEDIUM/LOW/ABSTRACT_ONLY).
    """
    paper_id = payload.get("paper_id")
    paper_data = payload.get("paper_data", {})
    
    paper = {}
    if paper_id and paper_id in data_harvester._temp_cache:
        paper = data_harvester._temp_cache[paper_id]
    elif paper_data:
        paper = paper_data
    else:
        raise HTTPException(status_code=400, detail="Cần cung cấp paper_id hoặc paper_data.")
    
    extracted_data = data_harvester.extract_full_text(paper)
    audit = data_harvester.audit_extraction_integrity(extracted_data, paper)
    return {"status": "success", "paper_id": paper_id, **audit}


# ─── 9. PHỤC VỤ AI ĐỌC NỘI DUNG ĐÃ BÓC TÁCH (cho NotebookLM / RAG) ─────────

@harvester_router.post("/api/harvest/read-for-ai")
@harvester_router.post("/api/harvest/read-pdf")
def get_readable_content_for_ai(payload: dict = Body(...), user: dict = Depends(require_operational_user)):
    """
    Trả về toàn bộ nội dung verbatim đã bóc tách từ bài báo để AI đọc trực tiếp.
    Phục vụ Bước 3 (NotebookLM/RAG) mà không phải xử lý lại PDF.
    TUYỆT ĐỐI KHÔNG thêm, sửa hoặc diễn giải nội dung gốc.
    """
    paper_id = payload.get("paper_id")
    paper_data = payload.get("paper_data", {})
    if not paper_id and not paper_data:
        raise HTTPException(status_code=400, detail="Cần cung cấp paper_id hoặc paper_data.")
    
    res = data_harvester.get_readable_content_for_ai(paper_id=paper_id, paper_data=paper_data)
    
    if res.get("status") == "success":
        history_mgr.add_entry(
            module="harvester",
            action_title=f"AI đọc nội dung bài báo: {res.get('title', 'N/A')[:40]}",
            inputs={"paper_id": paper_id},
            result_data={"word_count": res.get("word_count"), "quality": res.get("extraction_quality")},
            summary=f"Bóc tách {res.get('word_count', 0)} từ, chất lượng {res.get('extraction_quality', 'N/A')}"
        )
    return res

