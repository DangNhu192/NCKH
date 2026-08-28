# modules/pipeline/pipeline_router.py
from fastapi import APIRouter, HTTPException, Body, Depends, UploadFile, File
from modules.auth.auth_service import require_operational_user
from modules.auth.user_config_manager import load_user_config
from modules.pipeline.pipeline_engine import pipeline_engine
from modules.history.history_manager import history_mgr

pipeline_router = APIRouter(tags=["Research Pipeline 7 Steps"])

@pipeline_router.get("/api/pipeline/steps")
def get_pipeline_steps():
    return pipeline_engine.get_pipeline_steps()

@pipeline_router.post("/api/pipeline/run-step")
def run_pipeline_step(payload: dict = Body(...), user: dict = Depends(require_operational_user)):
    step_no = int(payload.get("step_no", 1))
    topic = payload.get("topic", "")
    params = payload.get("params", {})
    if not topic:
        raise HTTPException(status_code=400, detail="Topic là bắt buộc.")
    
    user_cfg = load_user_config(user)
    params["api_key"] = user_cfg.get("gemini_api_key", "").strip() or None
    params["openai_key"] = user_cfg.get("openai_api_key", "").strip() or None
    
    res = pipeline_engine.run_step(step_no, topic, params)
    history_mgr.add_entry(
        module="pipeline",
        action_title=f"Quy trình 7 Bước (Bước {step_no}): {topic}",
        inputs={"step_no": step_no, "topic": topic, "params": params},
        result_data=res,
        summary=f"Đã hoàn thành Bước {step_no} ({res.get('gate', '')})"
    )
    return res

@pipeline_router.post("/api/pipeline/run-full")
def run_full_chained_pipeline(payload: dict = Body(...), user: dict = Depends(require_operational_user)):
    topic = payload.get("topic", "")
    params = payload.get("params", {})
    if not topic:
        raise HTTPException(status_code=400, detail="Topic là bắt buộc.")
    
    user_cfg = load_user_config(user)
    params["api_key"] = user_cfg.get("gemini_api_key", "").strip() or None
    params["openai_key"] = user_cfg.get("openai_api_key", "").strip() or None
    
    res = pipeline_engine.run_full_pipeline(topic, params)
    history_mgr.add_entry(
        module="pipeline",
        action_title=f"Quy trình 7 Bước Toàn Bộ (1-Click): {topic}",
        inputs={"topic": topic, "params": params},
        result_data=res,
        summary="Đã thực thi thành công toàn bộ 7/7 bước"
    )
    return res


# ── EVIDENCE VAULT APIS ──────────────────────────────────────────────────

@pipeline_router.get("/api/pipeline/vault/list")
def list_pipeline_vault(user: dict = Depends(require_operational_user)):
    """Lấy danh sách các tài liệu thực chứng trong Evidence Vault"""
    vault_items = pipeline_engine.get_vault_items()
    return {
        "status": "success",
        "total": len(vault_items),
        "vault": vault_items
    }


@pipeline_router.post("/api/pipeline/vault/upload")
async def upload_document_to_vault(
    file: UploadFile = File(...),
    user: dict = Depends(require_operational_user)
):
    """Nạp tệp đa định dạng (.docx, .md, .pdf, .txt) vào Evidence Vault"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Tên tệp không hợp lệ.")
    
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Tệp rỗng.")
    
    vault_item = pipeline_engine.ingest_document_to_vault(content, file.filename)
    history_mgr.add_entry(
        module="pipeline",
        action_title=f"Nạp tài liệu Vault: {file.filename}",
        inputs={"filename": file.filename, "size": len(content)},
        result_data=vault_item,
        summary=f"Đã nạp {file.filename} vào Evidence Vault"
    )
    return {
        "status": "success",
        "message": f"Đã nạp thành công '{file.filename}' vào Evidence Vault.",
        "item": vault_item
    }


@pipeline_router.post("/api/pipeline/vault/import-workspace")
def import_workspace_documents_to_vault(payload: dict = Body(...), user: dict = Depends(require_operational_user)):
    """Nạp các tệp sẵn có trong Workspace vào Evidence Vault"""
    rel_paths = payload.get("rel_paths", [])
    if not rel_paths or not isinstance(rel_paths, list):
        raise HTTPException(status_code=400, detail="Danh sách đường dẫn 'rel_paths' là bắt buộc.")
    
    res = pipeline_engine.import_workspace_files_to_vault(rel_paths)
    history_mgr.add_entry(
        module="pipeline",
        action_title="Import Workspace vào Vault",
        inputs={"rel_paths": rel_paths},
        result_data=res,
        summary=f"Đã import {res.get('total_imported', 0)} tệp vào Evidence Vault"
    )
    return res


@pipeline_router.delete("/api/pipeline/vault/item/{item_id}")
def delete_pipeline_vault_item(item_id: str, user: dict = Depends(require_operational_user)):
    """Xóa 1 tài liệu khỏi Evidence Vault"""
    removed = pipeline_engine.remove_vault_item(item_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài liệu trong Vault.")
    return {
        "status": "success",
        "message": f"Đã xóa tài liệu '{item_id}' khỏi Vault."
    }


@pipeline_router.post("/api/pipeline/vault/clear")
def clear_pipeline_vault(user: dict = Depends(require_operational_user)):
    """Xóa sạch bộ nhớ tạm của Evidence Vault"""
    pipeline_engine.clear_vault()
    return {
        "status": "success",
        "message": "Đã làm trống Evidence Vault."
    }

