# modules/zotero/zotero_router.py
import json
import os
from typing import Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Form, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from modules.auth.auth_service import require_zotero_user, get_current_user
from modules.zotero.zotero_converter_engine import zotero_converter
from modules.history.history_manager import history_mgr
from modules.zotero import zotero_connect as zc

IS_SERVERLESS = bool(os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"))

zotero_router = APIRouter(tags=["Zotero Word Dynamic Citation Converter"])


@zotero_router.get("/api/zotero/status")
def get_zotero_status(request: Request):
    """Trạng thái kết nối Zotero của người dùng hiện tại (Cloud qua header / Desktop cục bộ của máy chủ)."""
    eng = zc.engine_for_request(request)
    user_id, api_key, _ = zc.request_credentials(request)
    server_is_cloud = IS_SERVERLESS
    desktop_running = False if server_is_cloud else eng.is_zotero_desktop_running()
    has_cloud_config = bool(eng.user_id and eng.api_key)

    total = len(eng._cache) if eng._cache_loaded else 0
    error = None
    if not eng._cache_loaded:
        if eng.zot is not None:
            try:
                total = int(eng.zot.num_items())
            except Exception as e:
                error = f"Không đọc được thư viện Zotero Cloud: {e}"
        elif not server_is_cloud:
            total = len(eng.load_library(force=False))

    return {
        "success": error is None,
        "error": error,
        "server_mode": "cloud" if server_is_cloud else "local",
        "desktop_running": desktop_running,
        "desktop_port": 23119,
        "has_cloud_config": has_cloud_config,
        "connected_via_request": bool(user_id and api_key),
        "oauth_available": zc.oauth_available(),
        "library_id": eng.user_id or "local",
        "total_library_items": total,
        "library_type": eng.library_type
    }


# ── ĐĂNG NHẬP ZOTERO (TRÌNH DUYỆT / API KEY) ─────────────────────────────────

@zotero_router.post("/api/zotero/connect-key")
def connect_zotero_api_key(payload: dict):
    """Xác thực API key Zotero (tạo tại zotero.org/settings/keys) và trả về userID để trình duyệt lưu lại."""
    api_key = (payload.get("api_key") or "").strip()
    if not api_key:
        raise HTTPException(status_code=400, detail="Vui lòng nhập API key Zotero.")
    try:
        info = zc.validate_api_key(api_key)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Không kết nối được api.zotero.org: {e}")
    if not info["can_read"]:
        raise HTTPException(status_code=403, detail="API key chưa được cấp quyền đọc thư viện (Allow library access).")
    return {"success": True, "api_key": api_key, "library_type": "user", **info}


@zotero_router.get("/api/zotero/oauth/start")
def zotero_oauth_start(request: Request):
    """Bắt đầu đăng nhập Zotero qua trình duyệt (OAuth 1.0a zotero.org)."""
    if not zc.oauth_available():
        return HTMLResponse(_oauth_result_page(None, "Máy chủ chưa cấu hình ZOTERO_OAUTH_CLIENT_KEY / ZOTERO_OAUTH_CLIENT_SECRET. Hãy dùng đăng nhập bằng API key."), status_code=501)
    callback = f"{zc.public_base_url(request)}/api/zotero/oauth/callback"
    try:
        tok = zc.oauth_get_request_token(callback)
    except Exception as e:
        return HTMLResponse(_oauth_result_page(None, f"Không lấy được request token từ Zotero: {e}"), status_code=502)
    resp = RedirectResponse(zc.oauth_authorize_url(tok["oauth_token"]), status_code=302)
    resp.set_cookie(
        zc.OAUTH_COOKIE,
        zc.sign_cookie(f"{tok['oauth_token']}:{tok['oauth_token_secret']}"),
        max_age=900, httponly=True, samesite="lax",
        secure=callback.startswith("https://"), path="/api/zotero/oauth",
    )
    return resp


@zotero_router.get("/api/zotero/oauth/callback")
def zotero_oauth_callback(request: Request, oauth_token: str = "", oauth_verifier: str = ""):
    stored = zc.verify_cookie(request.cookies.get(zc.OAUTH_COOKIE))
    if not stored or ":" not in stored:
        page = _oauth_result_page(None, "Phiên đăng nhập Zotero đã hết hạn. Vui lòng thử lại.")
    else:
        req_token, req_secret = stored.split(":", 1)
        if not oauth_verifier or oauth_token != req_token:
            page = _oauth_result_page(None, "Bạn đã từ chối hoặc huỷ cấp quyền cho WEB SUPER trên Zotero.")
        else:
            try:
                info = zc.oauth_get_access_token(req_token, req_secret, oauth_verifier)
                page = _oauth_result_page({"mode": "cloud", "via": "oauth", "library_type": "user", **info}, None)
            except Exception as e:
                page = _oauth_result_page(None, f"Không đổi được access token Zotero: {e}")
    resp = HTMLResponse(page)
    resp.delete_cookie(zc.OAUTH_COOKIE, path="/api/zotero/oauth")
    return resp


def _oauth_result_page(conn: Optional[dict], error: Optional[str]) -> str:
    payload = json.dumps({"conn": conn, "error": error}, ensure_ascii=False).replace("<", "\\u003c")
    return f"""<!doctype html><html lang="vi"><head><meta charset="utf-8"><title>Zotero</title></head>
<body style="font-family:system-ui;background:#0f172a;color:#e2e8f0;padding:32px">
<p id="msg">Đang hoàn tất đăng nhập Zotero...</p>
<script>
(function() {{
  var r = {payload};
  if (r.conn) {{ try {{ localStorage.setItem("web_super_zotero", JSON.stringify(r.conn)); }} catch (e) {{}} }}
  try {{ if (window.opener && window.opener.postMessage) window.opener.postMessage({{type: "zotero-auth", conn: r.conn, error: r.error}}, window.location.origin); }} catch (e) {{}}
  document.getElementById("msg").textContent = r.error ? ("❌ " + r.error) : ("✅ Đã kết nối Zotero: " + (r.conn.username || r.conn.user_id) + ". Bạn có thể đóng cửa sổ này.");
  if (!r.error) setTimeout(function() {{ if (window.opener) window.close(); else window.location.href = "/"; }}, 1200);
}})();
</script></body></html>"""


@zotero_router.post("/api/zotero/convert")
@zotero_router.post("/api/zotero/convert-docx")
async def convert_docx_zotero_citations(
    request: Request,
    file: UploadFile = File(...),
    mode: Optional[str] = Form(None),
    mode_query: Optional[str] = Query(None, alias="mode"),
    zotero_library: Optional[str] = Form(None),
    user: dict = Depends(require_zotero_user)
):
    selected_mode = mode or mode_query or "A"
    eng = zc.engine_with_library(zc.engine_for_request(request), zc.parse_library_json(zotero_library))
    if not file.filename.lower().endswith(".docx"):
        raise HTTPException(status_code=400, detail="Chỉ hỗ trợ tệp định dạng .docx")
    try:
        content = await file.read()
        res = eng.convert_docx(content, file.filename, mode=selected_mode)
        history_mgr.add_entry(
            module="zotero",
            action_title=f"Chuyển đổi Zotero DOCX: {file.filename} (Mode {selected_mode})",
            inputs={"filename": file.filename, "mode": selected_mode},
            result_data=res,
            summary=f"Khớp {res.get('stats', {}).get('matched_citations', 0)}/{res.get('stats', {}).get('total_citations_found', 0)} trích dẫn"
        )
        return zc.attach_inline_files(res)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi chuyển đổi mã Zotero: {str(e)}")


@zotero_router.get("/api/zotero/library")
def get_zotero_library(request: Request, force_refresh: bool = False, user: dict = Depends(get_current_user)):
    eng = zc.engine_for_request(request)
    items = eng.load_library(force=force_refresh)
    return {
        "success": True,
        "library_id": eng.user_id,
        "total_items": len(items),
        "items": [{"key": it.get("key"), "title": it.get("data", {}).get("title"), "date": it.get("data", {}).get("date"), "type": it.get("data", {}).get("itemType")} for it in items[:50]]
    }


@zotero_router.post("/api/zotero/normalize-references")
async def normalize_text_references(
    request: Request,
    payload: dict,
    user: dict = Depends(require_zotero_user)
):
    eng = zc.engine_for_request(request)
    """Chuẩn hóa danh sách chuỗi trích dẫn thô theo 3 chuẩn APA, MLA, ISO 690 dựa trên Google Scholar & Scholarly APIs."""
    raw_refs = payload.get("references", [])
    style = payload.get("style", "APA")
    if isinstance(raw_refs, str):
        raw_refs = [line.strip() for line in raw_refs.splitlines() if line.strip()]
    if not raw_refs:
        raise HTTPException(status_code=400, detail="Vui lòng cung cấp danh sách trích dẫn cần chuẩn hóa.")
    try:
        res = eng.normalize_reference_text_list(
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
        return zc.attach_inline_files(res)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi chuẩn hóa danh mục trích dẫn: {str(e)}")


@zotero_router.post("/api/zotero/normalize-docx-references")
async def normalize_docx_references_endpoint(
    request: Request,
    file: UploadFile = File(...),
    style: str = Form("APA"),
    user: dict = Depends(require_zotero_user)
):
    eng = zc.engine_for_request(request)
    """Quét và chuẩn hóa phần Tài Liệu Tham Khảo trong file Word (.docx) theo 3 chuẩn APA, MLA, ISO 690."""
    if not file.filename.lower().endswith(".docx"):
        raise HTTPException(status_code=400, detail="Chỉ hỗ trợ tệp Word định dạng .docx")
    try:
        content = await file.read()
        res = eng.normalize_docx_references(
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
        return zc.attach_inline_files(res)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi chuẩn hóa file Word: {str(e)}")


@zotero_router.post("/api/zotero/sync-references-to-zotero")
async def sync_references_to_zotero_endpoint(
    request: Request,
    payload: dict,
    user: dict = Depends(require_zotero_user)
):
    eng = zc.engine_for_request(request)
    """Nạp trực tiếp danh sách tài liệu tham khảo vào phần mềm Zotero Desktop (port 23119) hoặc Cloud."""
    items = payload.get("items", [])
    if not items:
        raise HTTPException(status_code=400, detail="Danh sách tài liệu tham khảo rỗng.")
    try:
        res = eng.sync_items_to_zotero(items)
        return zc.attach_inline_files(res)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi đồng bộ vào Zotero: {str(e)}")


@zotero_router.post("/api/zotero/export-ris")
async def export_ris_endpoint(
    request: Request,
    payload: dict,
    user: dict = Depends(require_zotero_user)
):
    eng = zc.engine_for_request(request)
    """Xuất bản danh mục tài liệu tham khảo sang định dạng chuẩn RIS tương thích Zotero."""
    papers = payload.get("papers") or payload.get("items") or []
    if not papers:
        papers = eng.load_library(force=False)
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
    request: Request,
    payload: dict,
    user: dict = Depends(require_zotero_user)
):
    eng = zc.engine_for_request(request)
    """Xuất bản danh mục tài liệu tham khảo sang định dạng chuẩn BibTeX (.bib)."""
    papers = payload.get("papers") or payload.get("items") or []
    if not papers:
        papers = eng.load_library(force=False)
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
    request: Request,
    payload: Optional[dict] = None,
    user: dict = Depends(require_zotero_user)
):
    eng = zc.engine_for_request(request)
    """Quét và chuẩn hóa tên tác giả tiếng Việt trong Zotero Cloud sang cấu trúc Hai ô (Two-Field Mode theo Thông báo 5343/TB-ĐHĐT)."""
    p = payload or {}
    try:
        res = eng.standardize_vietnamese_creators_via_api(
            user_id=p.get("user_id") or eng.user_id,
            api_key=p.get("api_key") or eng.api_key
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi chuẩn hóa tên tiếng Việt: {str(e)}")


@zotero_router.post("/api/zotero/optimize-storage")
async def optimize_storage_endpoint(
    request: Request,
    payload: Optional[dict] = None,
    user: dict = Depends(require_zotero_user)
):
    eng = zc.engine_for_request(request)
    """Giao thức Zero-Risk: Quét và giải phóng tệp PDF đính kèm đã có DOI/URL trực tuyến, kèm sao lưu ZIP dự phòng."""
    p = payload or {}
    try:
        res = eng.optimize_storage_cleanup_pdfs(
            user_id=p.get("user_id") or eng.user_id,
            api_key=p.get("api_key") or eng.api_key,
            storage_dir=p.get("storage_dir"),
            backup_zip_path=p.get("backup_zip_path")
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi tối ưu dung lượng Zotero: {str(e)}")


@zotero_router.post("/api/zotero/convert-hyperlinks")
async def convert_hyperlinks_endpoint(
    request: Request,
    payload: dict,
    user: dict = Depends(require_zotero_user)
):
    eng = zc.engine_for_request(request)
    """Chuyển đổi URL/DOI trong file Word thành đối tượng <w:hyperlink> tương tác hỗ trợ Ctrl + Click."""
    docx_path = payload.get("docx_path")
    if not docx_path:
        raise HTTPException(status_code=400, detail="Vui lòng cung cấp đường dẫn docx_path.")
    try:
        res = eng.convert_urls_to_interactive_hyperlinks(
            docx_path=docx_path,
            output_path=payload.get("output_path")
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi chuyển đổi liên kết: {str(e)}")


