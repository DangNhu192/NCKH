import os
import json
import re
import time
import secrets
import string
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List

from modules.auth.vault_crypto_engine import vault_crypto

BASE_DIR = Path(__file__).resolve().parent.parent.parent
import tempfile
IS_VERCEL = bool(os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"))
if IS_VERCEL:
    VAULT_DIR = Path(tempfile.gettempdir()) / "auth_vault"
else:
    VAULT_DIR = BASE_DIR / "auth_vault"
VAULT_PROFILES_DIR = VAULT_DIR / "profiles"
try:
    VAULT_DIR.mkdir(parents=True, exist_ok=True)
except OSError:
    pass
try:
    VAULT_PROFILES_DIR.mkdir(parents=True, exist_ok=True)
except OSError:
    pass

USERS_INDEX_FILE = VAULT_DIR / "users_registry.vault.json"
LICENSE_KEYS_FILE = VAULT_DIR / "license_keys.vault.json"
CONFIG_GLOBAL_FILE = BASE_DIR / "config.json"

# Package definitions
PLAN_CONFIGS = {
    "free": {
        "name": "Gói Dùng Thử (Trial)",
        "price_label": "Miễn phí",
        "features": ["harvester"],
        "locked_features": ["pipeline", "writer", "editorial", "humanizer"],
        "max_papers_per_search": 3,
        "max_topics_pipeline": 0,
        "max_ai_calls_per_day": 5,
        "can_use_ai": False,
        "requires_own_api": True,
        "default_duration_days": 7,
        "badge_color": "#64748b",
        "description": "Trải nghiệm cơ bản 7 ngày, chỉ thu thập tối đa 3 bài/lần tìm kiếm."
    },
    "standard": {
        "name": "Gói Tiêu Chuẩn (Standard)",
        "price_label": "Liên hệ",
        "features": ["harvester", "zotero", "workspace", "history"],
        "locked_features": ["pipeline", "writer", "editorial", "humanizer"],
        "max_papers_per_search": 15,
        "max_topics_pipeline": 2,
        "max_ai_calls_per_day": 30,
        "can_use_ai": True,
        "requires_own_api": True,
        "default_duration_days": 30,
        "badge_color": "#0ea5e9",
        "description": "Tìm kiếm tối đa 15 bài/lần, 2 chủ đề pipeline, 30 ngày sử dụng."
    },
    "pro": {
        "name": "Gói Chuyên Nghiệp (Pro)",
        "price_label": "Liên hệ",
        "features": ["pipeline", "harvester", "zotero", "writer", "editorial", "humanizer", "workspace", "history"],
        "locked_features": [],
        "max_papers_per_search": 50,
        "max_topics_pipeline": 10,
        "max_ai_calls_per_day": 100,
        "can_use_ai": True,
        "requires_own_api": True,
        "default_duration_days": 90,
        "badge_color": "#8b5cf6",
        "description": "Toàn bộ 8 chức năng. Tối đa 50 bài/lần, 10 chủ đề pipeline, 90 ngày."
    },
    "enterprise": {
        "name": "Gói Không Giới Hạn (Enterprise / VIP)",
        "price_label": "Liên hệ",
        "features": ["*"],
        "locked_features": [],
        "max_papers_per_search": 999,
        "max_topics_pipeline": 999,
        "max_ai_calls_per_day": -1,
        "can_use_ai": True,
        "requires_own_api": True,
        "default_duration_days": 365,
        "badge_color": "#f59e0b",
        "description": "Không giới hạn bài báo, chủ đề, lượt AI. Hỗ trợ ưu tiên. 365 ngày."
    }
}

ROLE_CONFIGS = {
    "admin": "👑 Quản Trị Viên (Admin)",
    "reseller": "🤝 Đại Lý / Cộng Tác Viên (Reseller)",
    "researcher": "🎓 Nhà Nghiên Cứu (User)"
}

ADMIN_EMAILS = {"admin@websuper.edu.vn"}

def get_plan_quota(plan: str) -> dict:
    return PLAN_CONFIGS.get(plan, PLAN_CONFIGS["free"])

def check_user_can_operate(user_dict: dict, user_config: Optional[dict] = None, feature: str = "ai"):
    email = (user_dict.get("email") or "").strip().lower()
    role = user_dict.get("role", "researcher")

    if email in ADMIN_EMAILS or role == "admin":
        return True, "Quản trị viên có toàn quyền vận hành.", "admin"

    registry = load_user_registry()
    user_record = registry.get(email)

    if not user_record:
        return False, "Tài khoản chưa được kích hoạt. Vui lòng đăng nhập lại.", "unregistered"

    if user_record.get("status") == "blocked":
        return False, "Tài khoản của bạn đã bị khóa. Vui lòng liên hệ Admin.", "blocked"

    expires_at_str = user_record.get("plan_expires_at", "")
    if expires_at_str:
        try:
            exp_date = datetime.strptime(expires_at_str, "%Y-%m-%d %H:%M:%S")
            if datetime.now() > exp_date:
                return False, f"Gói sử dụng đã hết hạn ngày {expires_at_str}. Vui lòng mua hoặc kích hoạt key mới.", "expired"
        except Exception:
            pass

    user_plan = user_record.get("plan", "free")
    plan_info = PLAN_CONFIGS.get(user_plan, PLAN_CONFIGS["free"])

    if feature in ["pipeline", "writer", "editorial", "humanizer"] and not plan_info.get("can_use_ai", False):
        return False, f"Gói hiện tại ({plan_info['name']}) không hỗ trợ chức năng AI này. Vui lòng nâng cấp lên gói Pro hoặc Enterprise.", "plan_restricted"

    if plan_info.get("requires_own_api", True):
        cfg = user_config or load_user_config(user_dict)
        gemini_key = (cfg.get("gemini_api_key") or "").strip()
        openai_key = (cfg.get("openai_api_key") or "").strip()
        if not gemini_key and not openai_key:
            return False, "Chưa cấu hình API Gemini hoặc OpenAI cá nhân. Vui lòng vào mục Cài Đặt để nhập API Key.", "no_api_key"

    return True, "Hợp lệ", "ok"

def get_user_file_path(user_id: str) -> Path:
    clean_id = re.sub(r'[^a-zA-Z0-9_\-]', '_', user_id)
    return VAULT_PROFILES_DIR / f"user_{clean_id}.vault.json"

def load_user_registry() -> Dict[str, Any]:
    if not USERS_INDEX_FILE.exists():
        return {}
    try:
        with open(USERS_INDEX_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_user_registry(registry: Dict[str, Any]):
    with open(USERS_INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(registry, f, ensure_ascii=False, indent=2)

def register_or_update_user(user_info: dict) -> dict:
    email = user_info.get("email", "").lower().strip()
    if not email:
        return user_info

    registry = load_user_registry()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    is_admin_email = email in ADMIN_EMAILS
    default_role = "admin" if is_admin_email else "researcher"
    default_plan = "enterprise" if is_admin_email else "free"
    default_plan_name = PLAN_CONFIGS[default_plan]["name"]
    duration_days = PLAN_CONFIGS[default_plan]["default_duration_days"]
    default_expires = (datetime.now() + timedelta(days=duration_days)).strftime("%Y-%m-%d %H:%M:%S")

    if email in registry:
        existing = registry[email]
        existing["last_login"] = now_str
        existing["name"] = user_info.get("name") or existing.get("name", "User")
        existing["picture"] = user_info.get("picture") or existing.get("picture", "")
        if is_admin_email:
            existing["role"] = "admin"
            existing["plan"] = "enterprise"
            existing["plan_name"] = "Gói Không Giới Hạn (Enterprise / VIP)"
            existing["status"] = "active"
        else:
            if existing.get("role") == "admin":
                existing["role"] = "researcher"
            if existing.get("plan") == "enterprise" and not existing.get("activated_keys"):
                existing["plan"] = "free"
                existing["plan_name"] = "Gói Dùng Thử"
        registry[email] = existing
    else:
        new_record = {
            "email": email,
            "name": user_info.get("name", "User"),
            "picture": user_info.get("picture", ""),
            "provider": user_info.get("provider", "google"),
            "role": default_role,
            "status": "active",
            "plan": default_plan,
            "plan_name": default_plan_name,
            "plan_expires_at": default_expires,
            "created_at": now_str,
            "last_login": now_str,
            "activated_keys": []
        }
        registry[email] = new_record

    save_user_registry(registry)
    return registry[email]

def load_user_config(user_or_dict: Optional[dict] = None) -> Dict[str, Any]:
    user_dict = user_or_dict or {}
    email = user_dict.get("email", "").lower().strip()
    user_id = email or user_dict.get("sub", "default_user")
    user_file = get_user_file_path(user_id)

    config = {}
    if user_file.exists():
        try:
            with open(user_file, "r", encoding="utf-8") as f:
                raw_cfg = json.load(f)
                for k, v in raw_cfg.items():
                    if isinstance(v, str) and v.startswith("ENC:"):
                        config[k] = vault_crypto.decrypt_secret(v)
                    else:
                        config[k] = v
        except Exception:
            pass

    # Nếu là Admin hoặc chưa có cấu hình -> Kế thừa từ config.json toàn cục
    if email in ADMIN_EMAILS or not email:
        if CONFIG_GLOBAL_FILE.exists():
            try:
                with open(CONFIG_GLOBAL_FILE, "r", encoding="utf-8") as f:
                    global_cfg = json.load(f)
                    for k in ["gemini_api_key", "openai_api_key", "zotero_api_key", "zotero_user_id", "zotero_library_type", "selected_gemini_model", "abbyy_api_key", "abbyy_endpoint", "pdf_ocr_preferred_mode"]:
                        if not config.get(k) and global_cfg.get(k):
                            config[k] = global_cfg[k]
            except Exception:
                pass

    return config

def save_user_config(arg1: Any, arg2: Optional[Any] = None, user: Optional[dict] = None) -> Dict[str, Any]:
    """Hỗ trợ cả save_user_config(user_dict, config_data) và save_user_config(config_data, user=user)"""
    if isinstance(arg1, dict) and isinstance(arg2, dict):
        user_dict = arg1
        config_data = arg2
    elif isinstance(arg1, dict) and arg2 is None:
        config_data = arg1
        user_dict = user or {}
    else:
        user_dict = {}
        config_data = {}

    email = user_dict.get("email", "").lower().strip()
    user_id = email or user_dict.get("sub", "default_user")
    user_file = get_user_file_path(user_id)

    existing_cfg = load_user_config(user_dict)
    existing_cfg.update(config_data)

    encrypted_cfg = {}
    sensitive_keys = {"gemini_api_key", "openai_api_key", "zotero_api_key", "abbyy_api_key"}

    for k, v in existing_cfg.items():
        if k in sensitive_keys and isinstance(v, str) and v.strip() and not v.startswith("ENC:"):
            encrypted_cfg[k] = vault_crypto.encrypt_secret(v.strip())
        else:
            encrypted_cfg[k] = v

    try:
        with open(user_file, "w", encoding="utf-8") as f:
            json.dump(encrypted_cfg, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

    # Nếu là Admin -> Cập nhật luôn vào config.json
    if email in ADMIN_EMAILS:
        if CONFIG_GLOBAL_FILE.exists():
            try:
                with open(CONFIG_GLOBAL_FILE, "r", encoding="utf-8") as f:
                    gcfg = json.load(f)
                for k in ["gemini_api_key", "openai_api_key", "zotero_api_key", "zotero_user_id", "zotero_library_type", "selected_gemini_model"]:
                    if k in config_data:
                        gcfg[k] = config_data[k]
                with open(CONFIG_GLOBAL_FILE, "w", encoding="utf-8") as f:
                    json.dump(gcfg, f, ensure_ascii=False, indent=2)
            except Exception:
                pass

    return existing_cfg

def load_license_keys() -> List[Dict[str, Any]]:
    if not LICENSE_KEYS_FILE.exists():
        return []
    try:
        with open(LICENSE_KEYS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_license_keys(keys_list: List[Dict[str, Any]]):
    with open(LICENSE_KEYS_FILE, "w", encoding="utf-8") as f:
        json.dump(keys_list, f, ensure_ascii=False, indent=2)

def list_all_users() -> List[Dict[str, Any]]:
    registry = load_user_registry()
    return list(registry.values())

def list_all_license_keys() -> List[Dict[str, Any]]:
    return load_license_keys()

def update_user_role_status(email: str, role: Optional[str] = None, status: Optional[str] = None, plan: Optional[str] = None, extend_days: Optional[int] = None) -> dict:
    email = email.lower().strip()
    registry = load_user_registry()
    if email not in registry:
        return {"success": False, "message": "Không tìm thấy người dùng."}

    user = registry[email]
    if role:
        user["role"] = role
    if status:
        user["status"] = status
    if plan and plan in PLAN_CONFIGS:
        user["plan"] = plan
        user["plan_name"] = PLAN_CONFIGS[plan]["name"]
    if extend_days and extend_days > 0:
        current_exp_str = user.get("plan_expires_at", "")
        now = datetime.now()
        if current_exp_str:
            try:
                curr_exp = datetime.strptime(current_exp_str, "%Y-%m-%d %H:%M:%S")
                base_time = curr_exp if curr_exp > now else now
            except Exception:
                base_time = now
        else:
            base_time = now
        user["plan_expires_at"] = (base_time + timedelta(days=extend_days)).strftime("%Y-%m-%d %H:%M:%S")

    registry[email] = user
    save_user_registry(registry)
    return {"success": True, "message": "Cập nhật thành công.", "user": user}

def delete_user_account(email: str) -> dict:
    email = email.lower().strip()
    registry = load_user_registry()
    if email not in registry:
        return {"success": False, "message": "Không tìm thấy người dùng."}
    del registry[email]
    save_user_registry(registry)

    # Delete profile file
    pfile = get_user_file_path(email)
    if pfile.exists():
        try:
            pfile.unlink()
        except Exception:
            pass

    return {"success": True, "message": "Đã xóa tài khoản."}

def list_all_license_keys(filter_creator: Optional[str] = None) -> List[dict]:
    keys = load_license_keys()
    if filter_creator:
        keys = [k for k in keys if k.get("created_by", "").lower() == filter_creator.lower()]
    return keys

def generate_license_key(plan: str, duration_days: int, creator_email: str, note: str = "", max_activations: int = 1) -> dict:
    if plan not in PLAN_CONFIGS:
        raise ValueError(f"Gói '{plan}' không hợp lệ.")

    rand_part = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(16))
    key_formatted = f"SUPER-{plan.upper()[:3]}-{rand_part[:4]}-{rand_part[4:8]}-{rand_part[8:12]}-{rand_part[12:16]}"
    sig = vault_crypto.sign_license_key(key_formatted, plan, duration_days)

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    record = {
        "key": key_formatted,
        "plan": plan,
        "plan_name": PLAN_CONFIGS[plan]["name"],
        "duration_days": duration_days,
        "max_activations": max_activations,
        "created_by": creator_email,
        "created_at": now_str,
        "status": "unused",
        "used_by": None,
        "used_at": None,
        "expires_after_activation": None,
        "note": note,
        "hmac_signature": sig
    }

    all_keys = load_license_keys()
    all_keys.insert(0, record)
    save_license_keys(all_keys)
    return record

def activate_license_key(key_string: str, user_email: str) -> dict:
    key_clean = key_string.strip().upper()
    user_email = user_email.strip().lower()

    all_keys = load_license_keys()
    target_key = None
    target_idx = -1

    for i, k in enumerate(all_keys):
        if k.get("key", "").upper() == key_clean:
            target_key = k
            target_idx = i
            break

    if not target_key:
        return {"success": False, "message": "Mã License Key không tồn tại."}

    if target_key.get("status") == "used":
        used_by = target_key.get("used_by", "người dùng khác")
        used_at = target_key.get("used_at", "")
        return {"success": False, "message": f"Mã Key này đã được kích hoạt bởi {used_by} vào lúc {used_at}."}

    if target_key.get("status") == "revoked":
        return {"success": False, "message": "Mã Key này đã bị thu hồi bởi Admin."}

    sig = target_key.get("hmac_signature")
    if sig:
        is_valid_sig = vault_crypto.verify_license_key_signature(
            target_key["key"], target_key["plan"], target_key["duration_days"], sig
        )
        if not is_valid_sig:
            return {"success": False, "message": "Cảnh báo bảo mật: Mã Key có dấu hiệu bị chỉnh sửa bất hợp pháp."}

    plan = target_key.get("plan", "standard")
    duration_days = int(target_key.get("duration_days", 30))
    now = datetime.now()
    now_str = now.strftime("%Y-%m-%d %H:%M:%S")

    registry = load_user_registry()
    user_rec = registry.get(user_email)
    if not user_rec:
        user_rec = register_or_update_user({"email": user_email, "name": user_email.split("@")[0]})

    current_exp_str = user_rec.get("plan_expires_at", "")
    current_plan = user_rec.get("plan", "free")

    if current_plan == plan and current_exp_str:
        try:
            curr_exp = datetime.strptime(current_exp_str, "%Y-%m-%d %H:%M:%S")
            if curr_exp > now:
                new_exp = curr_exp + timedelta(days=duration_days)
            else:
                new_exp = now + timedelta(days=duration_days)
        except Exception:
            new_exp = now + timedelta(days=duration_days)
    else:
        new_exp = now + timedelta(days=duration_days)

    new_exp_str = new_exp.strftime("%Y-%m-%d %H:%M:%S")

    target_key["status"] = "used"
    target_key["used_by"] = user_email
    target_key["used_at"] = now_str
    target_key["expires_after_activation"] = new_exp_str
    all_keys[target_idx] = target_key
    save_license_keys(all_keys)

    user_rec["plan"] = plan
    user_rec["plan_name"] = PLAN_CONFIGS[plan]["name"]
    user_rec["plan_expires_at"] = new_exp_str
    if "activated_keys" not in user_rec:
        user_rec["activated_keys"] = []
    user_rec["activated_keys"].append({
        "key": key_clean,
        "plan": plan,
        "activated_at": now_str,
        "duration_days": duration_days
    })
    registry[user_email] = user_rec
    save_user_registry(registry)

    return {
        "success": True,
        "message": f"Kích hoạt thành công {PLAN_CONFIGS[plan]['name']}! Hạn sử dụng đến: {new_exp_str}",
        "plan": plan,
        "plan_name": PLAN_CONFIGS[plan]["name"],
        "plan_expires_at": new_exp_str,
        "duration_days": duration_days
    }

def activate_license_key_for_user(user_email: str, key_string: str) -> dict:
    return activate_license_key(key_string, user_email)

def revoke_or_delete_license_key(key_string: str, action: str = "revoke") -> dict:
    key_clean = key_string.strip().upper()
    all_keys = load_license_keys()
    found = False

    if action == "delete":
        all_keys = [k for k in all_keys if k.get("key", "").upper() != key_clean]
        save_license_keys(all_keys)
        return {"success": True, "message": f"Đã xóa mã key {key_clean}."}
    else:
        for k in all_keys:
            if k.get("key", "").upper() == key_clean:
                k["status"] = "revoked"
                found = True
                break
        if found:
            save_license_keys(all_keys)
            return {"success": True, "message": f"Đã thu hồi mã key {key_clean}."}
        return {"success": False, "message": "Không tìm thấy mã key."}
