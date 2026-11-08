# modules/zotero/zotero_router.py
from typing import Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Form, Query

from modules.auth.auth_service import require_operational_user, get_current_user
from modules.zotero.zotero_converter_engine import zotero_converter
from modules.history.history_manager import history_mgr

zotero_router = APIRouter(tags=["Zotero Word Dynamic Citation Converter"])


@zotero_router.get("/api/zotero/status")
def get_zotero_status():
    """Kiểm tra trạng thái Zotero Desktop cục bộ (Cổng 23119) và Zotero Cloud API."""
    desktop_running = zotero_converter.is_zotero_desktop_running()
    items = zotero_converter.load_library(force=False)
    has_cloud_config = bool(zotero_converter.user_id and zotero_converter.api_key)
    
    return {
        "success": True,
        "desktop_running": desktop_running,
        "desktop_port": 23119,
        "has_cloud_config": has_cloud_config,
        "library_id": zotero_converter.user_id or "local",
        "total_library_items": len(items),
        "library_type": zotero_converter.library_type
    }


@zotero_router.post("/api/zotero/convert")
@zotero_router.post("/api/zotero/convert-docx")
async def convert_docx_zotero_citations(
    file: UploadFile = File(...),
    mode: Optional[str] = Form(None),
    mode_query: Optional[str] = Query(None, alias="mode"),
    user: dict = Depends(require_operational_user)
):
    selected_mode = mode or mode_query or "A"
    if not file.filename.lower().endswith(".docx"):
        raise HTTPException(status_code=400, detail="Chỉ hỗ trợ tệp định dạng .docx")
    try:
        content = await file.read()
        res = zotero_converter.convert_docx(content, file.filename, mode=selected_mode)
        history_mgr.add_entry(
            module="zotero",
            action_title=f"Chuyển đổi Zotero DOCX: {file.filename} (Mode {selected_mode})",
            inputs={"filename": file.filename, "mode": selected_mode},
            result_data=res,
            summary=f"Khớp {res.get('stats', {}).get('matched_citations', 0)}/{res.get('stats', {}).get('total_citations_found', 0)} trích dẫn"
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi chuyển đổi mã Zotero: {str(e)}")


@zotero_router.get("/api/zotero/library")
def get_zotero_library(force_refresh: bool = False, user: dict = Depends(get_current_user)):
    items = zotero_converter.load_library(force=force_refresh)
    return {
        "success": True,
        "library_id": zotero_converter.user_id,
        "total_items": len(items),
        "items": [{"key": it.get("key"), "title": it.get("data", {}).get("title"), "date": it.get("data", {}).get("date"), "type": it.get("data", {}).get("itemType")} for it in items[:50]]
    }


@zotero_router.post("/api/zotero/normalize-references")
async def normalize_text_references(
    payload: dict,
    user: dict = Depends(require_operational_user)
):
    """Chuẩn hóa danh sách chuỗi trích dẫn thô theo 3 chuẩn APA, MLA, ISO 690 dựa trên Google Scholar & Scholarly APIs."""
    raw_refs = payload.get("references", [])
    style = payload.get("style", "APA")
    if isinstance(raw_refs, str):
        raw_refs = [line.strip() for line in raw_refs.splitlines() if line.strip()]
    if not raw_refs:
        raise HTTPException(status_code=400, detail="Vui lòng cung cấp danh sách trích dẫn cần chuẩn hóa.")
    try:
        res = zotero_converter.normalize_reference_text_list(
            raw_refs,
            style=style,
            user_email=user.get("email")
        )
        history_mgr.add_entry(
            module="zotero",
            action_title=f"Chuẩn hóa trích dẫn ({style}): {len(raw_refs)} mục",
            inputs={"count": len(raw_refs), "style": style},
            result_data=res,
            summary=f"Chuẩn hóa {res.get('total', 0)} mục theo chuẩn {style} ({res.get('matched_dois', 0)} có DOI)"
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi chuẩn hóa danh mục trích dẫn: {str(e)}")


@zotero_router.post("/api/zotero/normalize-docx-references")
async def normalize_docx_references_endpoint(
    file: UploadFile = File(...),
    style: str = Form("APA"),
    user: dict = Depends(require_operational_user)
):
    """Quét và chuẩn hóa phần Tài Liệu Tham Khảo trong file Word (.docx) theo 3 chuẩn APA, MLA, ISO 690."""
    if not file.filename.lower().endswith(".docx"):
        raise HTTPException(status_code=400, detail="Chỉ hỗ trợ tệp Word định dạng .docx")
    try:
        content = await file.read()
        res = zotero_converter.normalize_docx_references(
            content,
            file.filename,
            style=style,
            user_email=user.get("email")
        )
        history_mgr.add_entry(
            module="zotero",
            action_title=f"Chuẩn hóa Tài Liệu Tham Khảo Word: {file.filename} ({style})",
            inputs={"filename": file.filename, "style": style},
            result_data=res,
            summary=f"Đã chuẩn hóa {res.get('total_references', 0)} tài liệu theo chuẩn {style}"
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi chuẩn hóa file Word: {str(e)}")


@zotero_router.post("/api/zotero/sync-references-to-zotero")
async def sync_references_to_zotero_endpoint(
    payload: dict,
    user: dict = Depends(require_operational_user)
):
    """Nạp trực tiếp danh sách tài liệu tham khảo vào phần mềm Zotero Desktop (port 23119) hoặc Cloud."""
    items = payload.get("items", [])
    if not items:
        raise HTTPException(status_code=400, detail="Danh sách tài liệu tham khảo rỗng.")
    try:
        res = zotero_converter.sync_items_to_zotero(items)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi đồng bộ vào Zotero: {str(e)}")


@zotero_router.post("/api/zotero/export-ris")
async def export_ris_endpoint(
    payload: dict,
    user: dict = Depends(require_operational_user)
):
    """Xuất bản danh mục tài liệu tham khảo sang định dạng chuẩn RIS tương thích Zotero."""
    papers = payload.get("papers") or payload.get("items") or []
    if not papers:
        papers = zotero_converter.load_library(force=False)
    try:
        from modules.zotero.zotero_converter_engine import export_batch_ris
        ris_text = export_batch_ris(papers)
        return {
            "status": "success",
            "ris_content": ris_text,
            "total_records": len(papers),
            "format": "ris"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xuất tệp RIS: {str(e)}")


@zotero_router.post("/api/zotero/export-bibtex")
async def export_bibtex_endpoint(
    payload: dict,
    user: dict = Depends(require_operational_user)
):
    """Xuất bản danh mục tài liệu tham khảo sang định dạng chuẩn BibTeX (.bib)."""
    papers = payload.get("papers") or payload.get("items") or []
    if not papers:
        papers = zotero_converter.load_library(force=False)
    try:
        from modules.zotero.zotero_converter_engine import export_batch_bibtex
        bib_text = export_batch_bibtex(papers)
        return {
            "status": "success",
            "bib_content": bib_text,
            "total_records": len(papers),
            "format": "bibtex"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xuất tệp BibTeX: {str(e)}")


@zotero_router.post("/api/zotero/standardize-vietnamese-names")
async def standardize_vietnamese_names_endpoint(
    payload: Optional[dict] = None,
    user: dict = Depends(require_operational_user)
):
    """Quét và chuẩn hóa tên tác giả tiếng Việt trong Zotero Cloud sang cấu trúc Hai ô (Two-Field Mode theo Thông báo 5343/TB-ĐHĐT)."""
    p = payload or {}
    try:
        res = zotero_converter.standardize_vietnamese_creators_via_api(
            user_id=p.get("user_id"),
            api_key=p.get("api_key")
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi chuẩn hóa tên tiếng Việt: {str(e)}")


@zotero_router.post("/api/zotero/optimize-storage")
async def optimize_storage_endpoint(
    payload: Optional[dict] = None,
    user: dict = Depends(require_operational_user)
):
    """Giao thức Zero-Risk: Quét và giải phóng tệp PDF đính kèm đã có DOI/URL trực tuyến, kèm sao lưu ZIP dự phòng."""
    p = payload or {}
    try:
        res = zotero_converter.optimize_storage_cleanup_pdfs(
            user_id=p.get("user_id"),
            api_key=p.get("api_key"),
            storage_dir=p.get("storage_dir"),
            backup_zip_path=p.get("backup_zip_path")
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi tối ưu dung lượng Zotero: {str(e)}")


@zotero_router.post("/api/zotero/convert-hyperlinks")
async def convert_hyperlinks_endpoint(
    payload: dict,
    user: dict = Depends(require_operational_user)
):
    """Chuyển đổi URL/DOI trong file Word thành đối tượng <w:hyperlink> tương tác hỗ trợ Ctrl + Click."""
    docx_path = payload.get("docx_path")
    if not docx_path:
        raise HTTPException(status_code=400, detail="Vui lòng cung cấp đường dẫn docx_path.")
    try:
        res = zotero_converter.convert_urls_to_interactive_hyperlinks(
            docx_path=docx_path,
            output_path=payload.get("output_path")
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi chuyển đổi liên kết: {str(e)}")


