# modules/history/history_router.py
from fastapi import APIRouter, HTTPException, Body, Depends, Query
from modules.auth.auth_service import get_current_user
from modules.history.history_manager import history_mgr
from modules.shared.file_manager import file_mgr

history_router = APIRouter(tags=["History & Workspace Sessions"])

@history_router.get("/api/workspace/files")
def list_workspace_files(category: str = None, user: dict = Depends(get_current_user)):
    return {
        "success": True,
        "workspace_root": str(file_mgr.workspace),
        "files": file_mgr.list_files(category=category)
    }

@history_router.get("/api/history")
def get_activity_history(
    limit: int = 50,
    module: str = "all",
    session_id: str = None,
    query: str = "",
    user: dict = Depends(get_current_user)
):
    user_email = user.get("email") or ""
    entries = history_mgr.get_history(limit=limit, module=module, query=query, session_id=session_id, user_email=user_email)
    total_count = len(history_mgr._read_raw(user_email))
    return {
        "status": "success",
        "total": total_count,
        "entries": entries,
        "history": entries
    }

@history_router.get("/api/history/sessions")
def get_activity_sessions(limit: int = 50, module: str = "all", query: str = "", user: dict = Depends(get_current_user)):
    user_email = user.get("email") or ""
    sessions = history_mgr.get_sessions(limit=limit, module=module, query=query, user_email=user_email)
    active_sess = history_mgr.get_active_session(user_email=user_email)
    return {
        "status": "success",
        "total": len(sessions),
        "active_session": active_sess,
        "sessions": sessions
    }

@history_router.post("/api/history/sessions")
def create_new_session(payload: dict = Body({}), user: dict = Depends(get_current_user)):
    user_email = user.get("email") or ""
    title = payload.get("title", "")
    topic = payload.get("topic", "")
    session = history_mgr.create_session(title=title, topic=topic, user_email=user_email)
    return {"status": "success", "session": session}

@history_router.get("/api/history/sessions/active")
def get_current_active_session(user: dict = Depends(get_current_user)):
    user_email = user.get("email") or ""
    session = history_mgr.get_active_session(user_email=user_email)
    return {"status": "success", "session": session}

@history_router.post("/api/history/sessions/active")
def set_current_active_session(payload: dict = Body(...), user: dict = Depends(get_current_user)):
    user_email = user.get("email") or ""
    session_id = payload.get("session_id")
    if not session_id:
        raise HTTPException(status_code=400, detail="Thiếu session_id")
    success = history_mgr.set_active_session(session_id, user_email=user_email)
    return {"status": "success" if success else "not_found", "active": success}

@history_router.post("/api/history/sessions/rename")
def rename_session_endpoint(payload: dict = Body(...), user: dict = Depends(get_current_user)):
    user_email = user.get("email") or ""
    session_id = payload.get("session_id")
    new_title = payload.get("title", "")
    if not session_id or not new_title:
        raise HTTPException(status_code=400, detail="Thiếu session_id hoặc title")
    success = history_mgr.rename_session(session_id, new_title, user_email=user_email)
    return {"status": "success" if success else "not_found", "renamed": success}

@history_router.delete("/api/history/sessions/{session_id}")
def delete_session_item(session_id: str, user: dict = Depends(get_current_user)):
    user_email = user.get("email") or ""
    success = history_mgr.delete_session(session_id, user_email=user_email)
    return {"status": "success" if success else "not_found", "deleted": success}

@history_router.post("/api/history/sessions/batch-delete")
def batch_delete_sessions_endpoint(payload: dict = Body(...), user: dict = Depends(get_current_user)):
    user_email = user.get("email") or ""
    session_ids = payload.get("session_ids", [])
    if not session_ids or not isinstance(session_ids, list):
        raise HTTPException(status_code=400, detail="Danh sách session_ids không hợp lệ.")
    cleared = history_mgr.delete_sessions_batch(session_ids, user_email=user_email)
    return {"status": "success", "deleted_sessions_count": cleared}

@history_router.post("/api/history/batch-delete")
def batch_delete_history_entries(payload: dict = Body(...), user: dict = Depends(get_current_user)):
    user_email = user.get("email") or ""
    entry_ids = payload.get("entry_ids", [])
    if not entry_ids or not isinstance(entry_ids, list):
        raise HTTPException(status_code=400, detail="Danh sách entry_ids không hợp lệ.")
    cleared = history_mgr.delete_entries_batch(entry_ids, user_email=user_email)
    return {"status": "success", "deleted_count": cleared}

@history_router.post("/api/history/record")
def record_activity_history(payload: dict = Body(...), user: dict = Depends(get_current_user)):
    user_email = user.get("email") or ""
    entry = history_mgr.add_entry(
        module=payload.get("module", "general"),
        action_title=payload.get("action_title", "Thao tác người dùng"),
        inputs=payload.get("inputs", {}),
        result_data=payload.get("result_data", {}),
        summary=payload.get("summary", ""),
        extra_meta=payload.get("extra_meta", {}),
        user_email=user_email
    )
    return {"status": "success", "entry": entry}
