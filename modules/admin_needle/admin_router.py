# modules/admin_needle/admin_router.py
from fastapi import APIRouter, HTTPException, Body, Depends
from modules.auth.auth_service import require_admin_user, require_admin_or_reseller
from modules.auth.user_config_manager import (
    list_all_users, update_user_role_status, delete_user_account,
    generate_license_key, list_all_license_keys, revoke_or_delete_license_key,
    PLAN_CONFIGS
)
from modules.admin_needle.needle_admin_assistant import needle_admin

admin_router = APIRouter(tags=["Admin Management & Needle Sentinel"])

@admin_router.get("/api/admin/users")
def admin_get_all_users(user: dict = Depends(require_admin_or_reseller)):
    users = list_all_users()
    return {
        "success": True,
        "total": len(users),
        "users": users
    }

@admin_router.post("/api/admin/users/update")
def admin_update_user_body(payload: dict = Body(...), user: dict = Depends(require_admin_user)):
    email = payload.get("email", "")
    if not email:
        raise HTTPException(status_code=400, detail="Thiếu email tài khoản.")
    role = payload.get("role")
    status = payload.get("status")
    plan = payload.get("plan")
    extend_days = payload.get("extend_days")
    res = update_user_role_status(email, role=role, status=status, plan=plan, extend_days=extend_days)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("message"))
    return res

@admin_router.post("/api/admin/users/{email}/role-status")
def admin_update_user(email: str, payload: dict = Body(...), user: dict = Depends(require_admin_user)):
    role = payload.get("role")
    status = payload.get("status")
    plan = payload.get("plan")
    extend_days = payload.get("extend_days")
    res = update_user_role_status(email, role=role, status=status, plan=plan, extend_days=extend_days)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("message"))
    return res

@admin_router.post("/api/admin/users/delete")
def admin_delete_user_body(payload: dict = Body(...), user: dict = Depends(require_admin_user)):
    email = payload.get("email", "")
    if not email:
        raise HTTPException(status_code=400, detail="Thiếu email tài khoản.")
    res = delete_user_account(email)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("message"))
    return res

@admin_router.delete("/api/admin/users/{email}")
def admin_delete_user(email: str, user: dict = Depends(require_admin_user)):
    res = delete_user_account(email)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("message"))
    return res

@admin_router.get("/api/admin/keys")
@admin_router.get("/api/admin/license-keys")
def admin_get_keys(user: dict = Depends(require_admin_or_reseller)):
    filter_creator = None if user.get("role") == "admin" else user.get("email")
    keys = list_all_license_keys(filter_creator=filter_creator)
    return {
        "success": True,
        "total": len(keys),
        "keys": keys
    }

@admin_router.post("/api/admin/keys")
@admin_router.post("/api/admin/license-keys/create")
def admin_create_key(payload: dict = Body(...), user: dict = Depends(require_admin_or_reseller)):
    plan = payload.get("plan", "pro")
    duration_days = int(payload.get("duration_days", 30))
    max_activations = int(payload.get("max_activations", 1))
    note = payload.get("note", "")
    key_obj = generate_license_key(
        plan=plan,
        duration_days=duration_days,
        max_activations=max_activations,
        note=note,
        created_by=user.get("email", "admin")
    )
    return {
        "success": True,
        "key": key_obj
    }

@admin_router.post("/api/admin/license-keys/revoke")
def admin_revoke_key_body(payload: dict = Body(...), user: dict = Depends(require_admin_or_reseller)):
    key = payload.get("key", "")
    delete = bool(payload.get("delete", False))
    if not key:
        raise HTTPException(status_code=400, detail="Thiếu mã key cần thu hồi.")
    res = revoke_or_delete_license_key(key, delete_permanently=delete, actor_email=user.get("email", ""))
    return {"success": res}

@admin_router.delete("/api/admin/keys/{key}")
def admin_revoke_or_delete_key(key: str, delete: bool = False, user: dict = Depends(require_admin_or_reseller)):
    res = revoke_or_delete_license_key(key, delete_permanently=delete, actor_email=user.get("email", ""))
    return {"success": res}

@admin_router.get("/api/admin/plans")
def admin_get_plans():
    return {
        "success": True,
        "plans": PLAN_CONFIGS
    }

@admin_router.get("/api/admin/needle/health-audit")
@admin_router.post("/api/admin/needle/health-audit")
def needle_health_audit_endpoint(user: dict = Depends(require_admin_or_reseller)):
    return needle_admin.run_health_audit()

@admin_router.post("/api/admin/needle/chat")
def needle_chat_command_endpoint(payload: dict = Body(...), user: dict = Depends(require_admin_or_reseller)):
    command = payload.get("command") or payload.get("message") or ""
    if not command:
        raise HTTPException(status_code=400, detail="Vui lòng nhập câu lệnh hoặc yêu cầu cho Needle AI.")
    return needle_admin.execute_admin_command(command, admin_user=user)
