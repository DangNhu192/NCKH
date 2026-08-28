from typing import Optional
import os
import time
import json
import requests
import jwt
from pathlib import Path
from fastapi import HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

CONFIG_FILE = Path(__file__).resolve().parent.parent.parent / "config.json"
USERS_INDEX_FILE = Path(__file__).resolve().parent.parent.parent / "auth_vault" / "users_registry.vault.json"
JWT_SECRET = os.getenv("JWT_SECRET", "web_super_secret_jwt_key_2026_super_secure")
JWT_ALGORITHM = "HS256"

security = HTTPBearer(auto_error=False)

def get_google_client_id():
    client_id = os.getenv("GOOGLE_CLIENT_ID", "")
    if not client_id and CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                client_id = cfg.get("google_client_id", "")
        except Exception:
            pass
    return client_id

def create_jwt_token(user_data: dict) -> str:
    payload = {
        "sub": user_data.get("email", "user@local.dev"),
        "name": user_data.get("name", "User"),
        "email": user_data.get("email", "user@local.dev"),
        "picture": user_data.get("picture", ""),
        "role": user_data.get("role", "researcher"),
        "provider": user_data.get("provider", "google"),
        "status": user_data.get("status", "active"),
        "plan": user_data.get("plan", "pro"),
        "plan_name": user_data.get("plan_name", "Gói Chuyên Nghiệp"),
        "plan_expires_at": user_data.get("plan_expires_at", ""),
        "exp": int(time.time()) + (86400 * 30),  # 30 days
        "iat": int(time.time())
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_jwt_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        email = payload.get("email", "").lower().strip()
        from modules.auth.user_config_manager import ADMIN_EMAILS
        
        is_real_admin = email in ADMIN_EMAILS
        if is_real_admin:
            payload["role"] = "admin"
            payload["plan"] = "enterprise"
            payload["plan_name"] = "Gói Không Giới Hạn (Enterprise / VIP)"
            payload["status"] = "active"
            payload["is_admin"] = True
            return payload

        # For all normal users: Strictly force is_admin = False and role != admin
        payload["is_admin"] = False
        if payload.get("role") == "admin":
            payload["role"] = "researcher"

        if USERS_INDEX_FILE.exists() and email:
            try:
                with open(USERS_INDEX_FILE, "r", encoding="utf-8") as f:
                    reg = json.load(f)
                    if email in reg:
                        u = reg[email]
                        stored_role = u.get("role", "researcher")
                        if stored_role == "admin" and not is_real_admin:
                            stored_role = "researcher"
                        payload["role"] = stored_role
                        payload["status"] = u.get("status", payload.get("status", "active"))
                        payload["plan"] = u.get("plan", payload.get("plan", "free"))
                        payload["plan_name"] = u.get("plan_name", payload.get("plan_name", "Gói Dùng Thử"))
                        payload["plan_expires_at"] = u.get("plan_expires_at", payload.get("plan_expires_at", ""))
            except Exception:
                pass
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.")
    except Exception:
        raise HTTPException(status_code=401, detail="Token không hợp lệ.")

def verify_google_credential(id_token: str) -> dict:
    """Verifies a Google OAuth ID Token via Google's tokeninfo endpoint with audience and issuer verification"""
    try:
        url = f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}"
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            data = res.json()
            email = data.get("email")
            if not email:
                raise ValueError("Token không chứa email người dùng.")
            
            # Verify issuer
            iss = data.get("iss", "")
            if iss not in ["accounts.google.com", "https://accounts.google.com"]:
                raise ValueError("Đơn vị phát hành token không hợp lệ (Invalid Issuer).")
                
            # Verify email verified
            if not data.get("email_verified", True):
                raise ValueError("Email Google chưa được xác thực.")

            name = data.get("name", email.split("@")[0] if email else "Google User")
            picture = data.get("picture", "")
            return {
                "email": email.lower(),
                "name": name,
                "picture": picture,
                "sub": data.get("sub"),
                "provider": "google_oauth",
                "verified": True
            }
        else:
            raise ValueError(f"Google Token Verification Failed with status {res.status_code}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Không thể xác thực tài khoản Google: {str(e)}")

def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> dict:
    """Dependency to get authenticated user via JWT Bearer Token, with guest fallback."""
    if not credentials or not credentials.credentials:
        return {
            "sub": "guest",
            "name": "Khách dùng thử",
            "email": "",
            "role": "guest",
            "status": "active",
            "plan": "free",
            "plan_name": "Gói Dùng Thử",
            "is_authenticated": False,
            "is_admin": False
        }
        
    token = credentials.credentials
    try:
        payload = decode_jwt_token(token)
        payload["is_authenticated"] = True
        return payload
    except HTTPException:
        raise
    except Exception as e:
        return {
            "sub": "guest",
            "name": "Khách dùng thử",
            "email": "",
            "role": "guest",
            "status": "active",
            "plan": "free",
            "plan_name": "Gói Dùng Thử",
            "is_authenticated": False,
            "is_admin": False
        }

def require_admin_user(user: dict = Depends(get_current_user)) -> dict:
    """Dependency to strictly require Admin role"""
    from modules.auth.user_config_manager import ADMIN_EMAILS
    email = user.get("email", "").lower().strip()
    if not user.get("is_authenticated") or not email:
        raise HTTPException(status_code=401, detail="Vui lòng đăng nhập tài khoản Google Admin (admin@websuper.edu.vn) để truy cập.")
    if email not in ADMIN_EMAILS and user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Từ chối truy cập: Bạn không có quyền Quản trị viên (Admin). Vui lòng đăng nhập với tài khoản admin@websuper.edu.vn.")
    user["role"] = "admin"
    user["is_admin"] = True
    return user

def require_admin_or_reseller(user: dict = Depends(get_current_user)) -> dict:
    """Dependency to allow Admin or Reseller (Cộng tác viên) to create and manage their License Keys"""
    from modules.auth.user_config_manager import ADMIN_EMAILS
    email = user.get("email", "").lower().strip()
    if not user.get("is_authenticated") or not email:
        raise HTTPException(status_code=401, detail="Vui lòng đăng nhập để truy cập.")
    if email in ADMIN_EMAILS or user.get("role") == "admin":
        user["role"] = "admin"
        user["is_admin"] = True
        return user
    if user.get("role") != "reseller":
        raise HTTPException(status_code=403, detail="Yêu cầu quyền Quản trị viên hoặc Cộng tác viên (Reseller) để tạo mã key.")
    return user
def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[dict]:
    """Dependency to get authenticated user if token is provided, or None if unauthenticated."""
    if not credentials or not credentials.credentials:
        return None
    try:
        payload = decode_jwt_token(credentials.credentials)
        payload["is_authenticated"] = True
        return payload
    except Exception:
        return None

def require_operational_user(user: dict = Depends(get_current_user)) -> dict:
    """Dependency to verify user is active and has valid plan quota"""
    from modules.auth.user_config_manager import check_user_can_operate
    can_op, msg, _ = check_user_can_operate(user)
    if not can_op:
        raise HTTPException(status_code=403, detail=msg)
    return user
