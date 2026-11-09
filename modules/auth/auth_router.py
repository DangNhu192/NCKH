# modules/auth/auth_router.py
from typing import Optional
from fastapi import APIRouter, HTTPException, Body, Depends, Request
from modules.auth.auth_service import (
    get_google_client_id, create_jwt_token, decode_jwt_token,
    verify_google_credential, get_current_user, get_optional_user,
    require_admin_user, require_admin_or_reseller, require_operational_user
)
from modules.auth.user_config_manager import (
    load_user_config, save_user_config, activate_license_key_for_user,
    check_user_can_operate, get_plan_quota, register_or_update_user
)
from modules.shared.gemini_service import gemini_service
from modules.shared.file_manager import file_mgr

auth_router = APIRouter(tags=["Authentication & Configuration"])

@auth_router.post("/api/auth/google")
def google_auth_login(payload: dict = Body(...)):
    id_token = payload.get("id_token")
    if not id_token:
        raise HTTPException(status_code=400, detail="Thiếu id_token từ Google.")
    
    raw_user_info = verify_google_credential(id_token)
    if not raw_user_info:
        raise HTTPException(status_code=401, detail="Chữ ký số Google ID Token không hợp lệ hoặc đã hết hạn.")
    
    # Register or update in persistent user registry (assigns Admin/Enterprise role if Admin)
    user_record = register_or_update_user(raw_user_info)
    
    token = create_jwt_token(user_record)
    return {
        "success": True,
        "token": token,
        "user": user_record,
        "message": f"Đăng nhập thành công với tài khoản {user_record.get('email')}"
    }

@auth_router.post("/api/auth/direct-admin-login")
def direct_admin_login(payload: dict = Body(...)):
    """
    Direct Admin Login cho Quản trị viên (admin@websuper.edu.vn hoặc superadmin@local).
    Cho phép đăng nhập trực tiếp 1-click vào quyền Quản trị tối cao.
    """
    email = (payload.get("email") or "admin@websuper.edu.vn").strip().lower()
    from modules.auth.user_config_manager import ADMIN_EMAILS
    
    if email not in ADMIN_EMAILS:
        raise HTTPException(status_code=403, detail="Tài khoản này không nằm trong danh sách Quản trị viên hệ thống.")
        
    user_info = {
        "email": email,
        "name": "Web Super Administrator" if email == "admin@websuper.edu.vn" else "Web Super Admin",
        "picture": "",
        "provider": "admin_direct_auth",
        "role": "admin",
        "plan": "enterprise"
    }
    
    user_record = register_or_update_user(user_info)
    user_record["role"] = "admin"
    user_record["plan"] = "enterprise"
    
    token = create_jwt_token(user_record)
    return {
        "success": True,
        "token": token,
        "user": user_record,
        "message": f"Đăng nhập quyền Quản trị viên thành công: {email}"
    }

@auth_router.get("/api/auth/me")
def get_current_user_profile(user: dict = Depends(get_current_user)):
    user_cfg = load_user_config(user)
    has_api = bool(user_cfg.get("gemini_api_key", "").strip() or user_cfg.get("openai_api_key", "").strip())
    return {
        "success": True,
        "user": user,
        "quota": get_plan_quota(user.get("plan", "trial")),
        "has_api_configured": has_api,
        "is_admin": user.get("role") == "admin"
    }

@auth_router.post("/api/auth/activate-key")
def activate_user_license_key(payload: dict = Body(...), user: dict = Depends(get_current_user)):
    key = payload.get("key", "").strip()
    if not key:
        raise HTTPException(status_code=400, detail="Vui lòng nhập mã key kích hoạt.")
    res = activate_license_key_for_user(user.get("email"), key)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("message"))
    return res

@auth_router.get("/api/config")
def get_configuration(user: Optional[dict] = Depends(get_optional_user)):
    user_cfg = load_user_config(user)
    google_client_id = get_google_client_id()
    return {
        "success": True,
        "user_email": user.get("email") if user else None,
        "google_client_id": google_client_id,
        "gemini_api_key": user_cfg.get("gemini_api_key", ""),
        "openai_api_key": user_cfg.get("openai_api_key", ""),
        "zotero_user_id": user_cfg.get("zotero_user_id", ""),
        "zotero_api_key": user_cfg.get("zotero_api_key", ""),
        "selected_gemini_model": user_cfg.get("selected_gemini_model", "auto"),
        "custom_storage_dir": user_cfg.get("custom_storage_dir", ""),
        "config": {
            "gemini_api_key": bool(user_cfg.get("gemini_api_key")),
            "openai_api_key": bool(user_cfg.get("openai_api_key")),
            "zotero_user_id": user_cfg.get("zotero_user_id", ""),
            "zotero_api_key": bool(user_cfg.get("zotero_api_key")),
            "selected_gemini_model": user_cfg.get("selected_gemini_model", "auto"),
            "custom_storage_dir": user_cfg.get("custom_storage_dir", ""),
            "raw_keys": {
                "gemini_api_key": user_cfg.get("gemini_api_key", ""),
                "openai_api_key": user_cfg.get("openai_api_key", ""),
                "zotero_api_key": user_cfg.get("zotero_api_key", ""),
                "custom_storage_dir": user_cfg.get("custom_storage_dir", "")
            }
        }
    }

@auth_router.post("/api/config")
def save_configuration(payload: dict = Body(...), user: Optional[dict] = Depends(get_optional_user)):
    user_cfg = save_user_config(payload, user=user)
    google_client_id = get_google_client_id()
    return {
        "success": True,
        "message": "Đã lưu cài đặt cấu hình cá nhân thành công.",
        "google_client_id": google_client_id,
        "gemini_api_key": user_cfg.get("gemini_api_key", ""),
        "openai_api_key": user_cfg.get("openai_api_key", ""),
        "zotero_user_id": user_cfg.get("zotero_user_id", ""),
        "zotero_api_key": user_cfg.get("zotero_api_key", ""),
        "selected_gemini_model": user_cfg.get("selected_gemini_model", "auto"),
        "custom_storage_dir": user_cfg.get("custom_storage_dir", ""),
        "config": {
            "gemini_api_key": bool(user_cfg.get("gemini_api_key")),
            "openai_api_key": bool(user_cfg.get("openai_api_key")),
            "zotero_user_id": user_cfg.get("zotero_user_id", ""),
            "zotero_api_key": bool(user_cfg.get("zotero_api_key")),
            "selected_gemini_model": user_cfg.get("selected_gemini_model", "auto"),
            "custom_storage_dir": user_cfg.get("custom_storage_dir", "")
        }
    }

@auth_router.get("/api/status")
def get_system_status(user: Optional[dict] = Depends(get_optional_user)):
    user_cfg = load_user_config(user)
    key = user_cfg.get("gemini_api_key", "").strip() or None
    if key and (key.startswith("AQ.Test") or "test" in key.lower()):
        key = None
    if not key:
        model_status = {"status": "unconfigured", "active_model": "gemini-2.0-flash", "message": "Chưa cấu hình API Key"}
    else:
        model_status = {"status": "connected", "active_model": user_cfg.get("selected_gemini_model") or "gemini-2.0-flash"}
    google_client_id = get_google_client_id()
    all_files = file_mgr.list_files()
    return {
        "status": "online",
        "google_client_id": google_client_id,
        "gemini": model_status,
        "has_gemini_key": bool(key),
        "active_gemini_model": model_status.get("active_model") or "gemini-2.5-flash",
        "has_google_auth": bool(user),
        "total_files": len(all_files),
        "user": user
    }

@auth_router.get("/api/user/check-ready")
def check_user_ready_state(user: Optional[dict] = Depends(get_optional_user)):
    if not user:
        return {
            "ready": False,
            "reason": "not_logged_in",
            "message": "Vui lòng đăng nhập tài khoản Google để sử dụng tính năng.",
            "action": "open_login"
        }
    
    can_op, op_msg, op_code = check_user_can_operate(user)
    if not can_op:
        return {
            "ready": False,
            "reason": op_code,
            "message": op_msg,
            "action": "open_payment" if op_code == "no_plan" else "contact_admin"
        }
    
    user_cfg = load_user_config(user)
    has_api = bool(user_cfg.get("gemini_api_key", "").strip() or user_cfg.get("openai_api_key", "").strip())
    if not has_api:
        return {
            "ready": False,
            "reason": "no_api",
            "message": "Bạn chưa cấu hình API Gemini hoặc ChatGPT cá nhân trong Cài Đặt.",
            "action": "open_settings"
        }
    
    return {
        "ready": True,
        "reason": "ready",
        "message": "Tài khoản đã sẵn sàng sử dụng toàn bộ 8 chức năng.",
        "action": "none"
    }

@auth_router.get("/api/gemini/models")
def get_gemini_models_list(api_key: Optional[str] = None, user: Optional[dict] = Depends(get_optional_user)):
    user_cfg = load_user_config(user)
    effective_key = api_key or user_cfg.get("gemini_api_key", "").strip() or None
    return gemini_service.list_available_models(api_key=effective_key)

@auth_router.post("/api/gemini/refresh-models")
def refresh_gemini_models_list(payload: Optional[dict] = Body(default={}), user: Optional[dict] = Depends(get_optional_user)):
    user_cfg = load_user_config(user)
    passed_key = payload.get("api_key", "").strip() if payload else ""
    effective_key = passed_key or user_cfg.get("gemini_api_key", "").strip() or None
    return gemini_service.list_available_models(force_refresh=True, api_key=effective_key)
