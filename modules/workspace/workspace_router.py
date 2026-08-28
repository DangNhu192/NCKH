# modules/workspace/workspace_router.py
"""
Workspace File Management API Router for WEB SUPER v2.0
Handles listing, reading, writing, downloading, deleting, and native OS opening of workspace files.
"""

from typing import Optional, List, Dict, Any
from pathlib import Path
import urllib.parse
from fastapi import APIRouter, HTTPException, Query, Body, Depends, UploadFile, File
from fastapi.responses import FileResponse

from modules.shared.file_manager import file_mgr
from modules.shared.docx_styler import sanitize_and_repair_docx
from modules.auth.auth_service import get_current_user, require_operational_user
from modules.auth.user_config_manager import load_user_config
from modules.shared.pdf_ocr_engine import pdf_ocr_engine

workspace_router = APIRouter(tags=["Workspace & File Manager"])


@workspace_router.get("/api/files")
def list_workspace_files(category: Optional[str] = Query(None, description="Danh mục: docs, drafts, publish, zotero")):
    """Trả về danh sách tệp tin trong Workspace dạng Array cho Frontend"""
    return file_mgr.list_files(category=category)


@workspace_router.get("/api/workspace/files")
def list_workspace_files_alias(category: Optional[str] = Query(None)):
    """Route alias tương thích ngược"""
    files = file_mgr.list_files(category=category)
    return {"success": True, "files": files}


@workspace_router.get("/api/files/read")
def read_workspace_file(path: str = Query(..., description="Đường dẫn tương đối của tệp trong Workspace")):
    try:
        clean_path = urllib.parse.unquote(path).strip().replace("\\", "/").lstrip("/")
        return file_mgr.read_file(clean_path)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi đọc tệp: {str(e)}")


@workspace_router.post("/api/files/save")
def save_workspace_file(payload: Dict[str, Any] = Body(...)):
    rel_path = payload.get("rel_path")
    content = payload.get("content", "")
    file_format = payload.get("file_format", "md")
    topic = payload.get("topic", "")
    references = payload.get("references", None)

    if not rel_path:
        raise HTTPException(status_code=400, detail="Thiếu đường dẫn rel_path.")

    try:
        clean_path = urllib.parse.unquote(rel_path).strip().replace("\\", "/").lstrip("/")
        res = file_mgr.save_file(clean_path, content, file_format=file_format, topic=topic, references=references)
        return res
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi lưu tệp: {str(e)}")


@workspace_router.delete("/api/files/delete")
def delete_workspace_file(path: str = Query(..., description="Đường dẫn tệp cần xóa")):
    try:
        clean_path = urllib.parse.unquote(path).strip().replace("\\", "/").lstrip("/")
        res = file_mgr.delete_file(clean_path)
        if not res.get("success"):
            raise HTTPException(status_code=404, detail=res.get("message", "Không tìm thấy tệp"))
        return res
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xóa tệp: {str(e)}")


@workspace_router.post("/api/files/batch-delete")
def batch_delete_workspace_files(payload: Dict[str, Any] = Body(...)):
    paths = payload.get("paths", [])
    if not paths:
        return {"success": True, "deleted_count": 0, "deleted_files": [], "failed_files": []}
    return file_mgr.delete_files(paths)


@workspace_router.get("/api/files/download")
def download_workspace_file(path: str = Query(..., description="Đường dẫn tệp cần tải về")):
    clean_path = urllib.parse.unquote(path).strip().replace("\\", "/").lstrip("/")
    fpath = (file_mgr.workspace / clean_path).resolve()
    
    # Check candidates if not found directly
    if not fpath.exists() or not fpath.is_file():
        fname = Path(clean_path).name
        for sub in [file_mgr.drafts_dir, file_mgr.docs_dir, file_mgr.publish_dir, file_mgr.zotero_dir]:
            cand = (sub / fname).resolve()
            if cand.exists() and cand.is_file():
                fpath = cand
                break

    if not fpath.exists() or not fpath.is_file():
        raise HTTPException(status_code=404, detail=f"Không tìm thấy tệp để tải về: {clean_path}")

    # Security check
    ws_str = str(file_mgr.workspace.resolve()).lower()
    if not str(fpath).lower().startswith(ws_str):
        raise HTTPException(status_code=403, detail="Truy cập ngoài Workspace bị từ chối.")

    return FileResponse(
        path=str(fpath),
        filename=fpath.name,
        media_type="application/octet-stream"
    )


@workspace_router.get("/api/files/open-folder")
def open_workspace_folder(
    path: Optional[str] = Query(None, description="Đường dẫn tương đối của tệp hoặc thư mục"),
    custom_dir: Optional[str] = Query(None, description="Đường dẫn thư mục tùy chỉnh")
):
    return file_mgr.open_folder(rel_path=path, custom_dir=custom_dir)


@workspace_router.get("/api/files/open-system")
def open_workspace_file_in_system(path: str = Query(..., description="Đường dẫn tương đối của tệp")):
    return file_mgr.open_file_in_system(path)


# ==============================================================================
# DOCX CONTENT & NUMERICAL DATA EDITOR ENDPOINTS
# ==============================================================================
from fastapi import UploadFile, File
from modules.workspace.docx_editor_engine import docx_editor
from modules.auth.auth_service import get_current_user


@workspace_router.post("/api/files/docx/upload-and-parse")
async def upload_and_parse_docx_file(file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    """Nạp tệp .docx từ máy tính người dùng và phân tích thành cấu trúc đoạn văn, bảng biểu, số liệu."""
    if not file.filename.lower().endswith(".docx"):
        raise HTTPException(status_code=400, detail="Chỉ hỗ trợ tệp Microsoft Word (.docx).")
    try:
        content_bytes = await file.read()
        repaired_bytes = sanitize_and_repair_docx(content_bytes)
        # Save to Ban_Thao for persistence
        clean_name = file.filename
        rel_path = f"Ban_Thao/{clean_name}"
        file_mgr.save_bytes(rel_path, repaired_bytes)

        parsed = docx_editor.parse_docx(repaired_bytes, filename=clean_name)
        parsed["rel_path"] = rel_path
        parsed["file_url"] = f"file:///{(file_mgr.workspace / rel_path).as_posix()}"
        return parsed
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi phân tích tệp .docx: {str(e)}")


@workspace_router.get("/api/files/docx/parse")
def parse_existing_docx_file(path: str = Query(..., description="Đường dẫn tương đối của tệp .docx")):
    """Phân tích tệp .docx đã có sẵn trong Workspace."""
    clean_path = urllib.parse.unquote(path).strip().replace("\\", "/").lstrip("/")
    try:
        parsed = docx_editor.parse_docx(clean_path, filename=Path(clean_path).name)
        parsed["rel_path"] = clean_path
        parsed["file_url"] = f"file:///{(file_mgr.workspace / clean_path).as_posix()}"
        return parsed
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi đọc tệp .docx: {str(e)}")


@workspace_router.post("/api/files/docx/save")
def save_edited_docx_file(payload: Dict[str, Any] = Body(...), user: dict = Depends(get_current_user)):
    """Lưu văn bản và bảng số liệu đã chỉnh sửa thành file Word .docx chuẩn In-Place DOM."""
    rel_path = payload.get("rel_path")
    if not rel_path:
        raise HTTPException(status_code=400, detail="Thiếu đường dẫn rel_path.")
    
    content_text = payload.get("content_text", "")
    paragraphs = payload.get("paragraphs", None)
    tables = payload.get("tables", None)
    topic = payload.get("topic", "Tài Liệu Chỉnh Sửa")

    try:
        res = docx_editor.save_edited_docx(
            rel_path=rel_path,
            content_text=content_text,
            paragraphs=paragraphs,
            tables=tables,
            topic=topic
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi lưu file .docx: {str(e)}")


@workspace_router.post("/api/files/docx/batch-replace")
def batch_replace_docx_data(payload: Dict[str, Any] = Body(...), user: dict = Depends(get_current_user)):
    """Tìm và thay thế hàng loạt số liệu hoặc thuật ngữ trong toàn bộ tệp Word .docx."""
    rel_path = payload.get("rel_path")
    replacements = payload.get("replacements", [])
    output_rel_path = payload.get("output_rel_path", None)

    if not rel_path or not replacements:
        raise HTTPException(status_code=400, detail="Thiếu đường dẫn rel_path hoặc danh sách replacements.")

    try:
        res = docx_editor.batch_replace_in_docx(
            rel_path=rel_path,
            replacements=replacements,
            output_rel_path=output_rel_path
        )
        return res
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi thay thế số liệu: {str(e)}")


# ==========================================
# 📄 PURPOSE-BUILT PDF AI & OCR ENDPOINTS (ABBYY & VISION AI RAG)
# ==========================================

@workspace_router.post("/api/pdf-ocr/inspect")
def inspect_pdf_document(payload: Dict[str, Any] = Body(...), user: dict = Depends(get_current_user)):
    """Đánh giá chất lượng lớp chữ PDF và phân loại Digital vs Scan thuần ảnh."""
    rel_path = payload.get("rel_path")
    if not rel_path:
        raise HTTPException(status_code=400, detail="Thiếu đường dẫn file PDF.")
    
    full_path = (file_mgr.workspace / rel_path.strip().replace("\\", "/").lstrip("/")).resolve()
    if not full_path.exists():
        raise HTTPException(status_code=404, detail=f"Không tìm thấy tệp: {rel_path}")

    res = pdf_ocr_engine.inspect_pdf(full_path)
    return res


@workspace_router.post("/api/pdf-ocr/upload-and-process")
async def upload_and_process_pdf_ocr(
    file: UploadFile = File(...),
    mode: str = Query("auto", description="auto, vision_ai, abbyy, fast_native"),
    max_pages: int = Query(30, description="Tối đa số trang xử lý"),
    topic_hint: str = Query("", description="Chủ đề bài báo để trợ lực OCR"),
    user: dict = Depends(require_operational_user)
):
    """Upload tệp PDF bất kỳ từ máy tính và thực hiện Purpose-Built AI OCR + RAG Chunking."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Chỉ hỗ trợ tải lên định dạng .pdf")

    pdf_bytes = await file.read()
    if len(pdf_bytes) < 100:
        raise HTTPException(status_code=400, detail="Tệp tải lên rỗng hoặc không hợp lệ.")

    # Save original PDF to workspace/Tai_Lieu/PDFs/
    pdf_dir = file_mgr.workspace / "Tai_Lieu" / "PDFs"
    pdf_dir.mkdir(parents=True, exist_ok=True)
    clean_name = Path(file.filename).name
    save_path = pdf_dir / clean_name
    save_path.write_bytes(pdf_bytes)

    user_cfg = load_user_config(user)
    user_api_key = user_cfg.get("gemini_api_key")
    abbyy_token = user_cfg.get("abbyy_api_key")
    abbyy_endpoint = user_cfg.get("abbyy_endpoint")

    try:
        res = pdf_ocr_engine.process_pdf_document(
            pdf_source=pdf_bytes,
            mode=mode,
            max_pages=max_pages,
            api_key=user_api_key,
            abbyy_token=abbyy_token,
            abbyy_endpoint=abbyy_endpoint,
            topic_hint=topic_hint
        )
        res["saved_pdf_path"] = f"Tai_Lieu/PDFs/{clean_name}"
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý PDF OCR: {str(e)}")


@workspace_router.post("/api/pdf-ocr/process")
def process_existing_pdf_ocr(payload: Dict[str, Any] = Body(...), user: dict = Depends(require_operational_user)):
    """Thực hiện OCR trên file PDF sẵn có trong Workspace."""
    rel_path = payload.get("rel_path")
    mode = payload.get("mode", "auto")
    max_pages = payload.get("max_pages", 50)
    topic_hint = payload.get("topic_hint", "")

    if not rel_path:
        raise HTTPException(status_code=400, detail="Thiếu đường dẫn tệp rel_path.")

    full_path = (file_mgr.workspace / rel_path.strip().replace("\\", "/").lstrip("/")).resolve()
    if not full_path.exists():
        raise HTTPException(status_code=404, detail=f"Không tìm thấy tệp: {rel_path}")

    user_cfg = load_user_config(user)
    user_api_key = user_cfg.get("gemini_api_key")
    abbyy_token = user_cfg.get("abbyy_api_key")
    abbyy_endpoint = user_cfg.get("abbyy_endpoint")

    try:
        res = pdf_ocr_engine.process_pdf_document(
            pdf_source=full_path,
            mode=mode,
            max_pages=max_pages,
            api_key=user_api_key,
            abbyy_token=abbyy_token,
            abbyy_endpoint=abbyy_endpoint,
            topic_hint=topic_hint
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi thực thi PDF OCR: {str(e)}")


@workspace_router.post("/api/pdf-ocr/export-docx")
def export_pdf_ocr_to_docx(payload: Dict[str, Any] = Body(...), user: dict = Depends(get_current_user)):
    """Xuất kết quả OCR sang tệp Word .docx chuẩn In-Place DOM."""
    ocr_result = payload.get("ocr_result")
    output_name = payload.get("output_name")
    if not ocr_result:
        raise HTTPException(status_code=400, detail="Thiếu dữ liệu ocr_result.")

    try:
        res = pdf_ocr_engine.export_searchable_docx(ocr_result=ocr_result, output_name=output_name)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xuất bản Word .docx: {str(e)}")


@workspace_router.post("/api/pdf-ocr/ingest-to-notebook")
def ingest_pdf_ocr_to_notebook(payload: Dict[str, Any] = Body(...), user: dict = Depends(require_operational_user)):
    """Nạp trực tiếp toàn văn và các RAG Chunks đã OCR vào Kho Tri Thức (Open-Notebook)."""
    ocr_result = payload.get("ocr_result")
    notebook_id = payload.get("notebook_id")
    if not ocr_result or not notebook_id:
        raise HTTPException(status_code=400, detail="Thiếu dữ liệu ocr_result hoặc notebook_id.")

    try:
        res = pdf_ocr_engine.ingest_to_open_notebook(ocr_result=ocr_result, notebook_id=notebook_id)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi nạp vào Open-Notebook: {str(e)}")


