# modules/zotero/zotero_connect.py
"""
Kết nối Zotero theo từng người dùng (tương thích Vercel serverless).

- Đăng nhập Zotero qua trình duyệt (OAuth 1.0a của zotero.org)  -> cần ZOTERO_OAUTH_CLIENT_KEY / ZOTERO_OAUTH_CLIENT_SECRET
- Đăng nhập bằng API Key (https://www.zotero.org/settings/keys)  -> không cần cấu hình máy chủ
- Zotero Desktop: trình duyệt đọc trực tiếp Local API (http://localhost:23119/api/) rồi gửi thư viện kèm request

Thông tin đăng nhập được lưu ở trình duyệt người dùng và gửi kèm mỗi request qua header:
    X-Zotero-User-Id, X-Zotero-Api-Key, X-Zotero-Library-Type
"""

import base64
import copy
import hashlib
import hmac
import json
import os
import secrets
import threading
import time
import urllib.parse
from typing import Any, Dict, List, Optional, Tuple

import requests
from fastapi import Request

from modules.zotero.zotero_converter_engine import ZoteroConverterEngine, zotero_converter

ZOTERO_OAUTH_REQUEST_URL = "https://www.zotero.org/oauth/request"
ZOTERO_OAUTH_AUTHORIZE_URL = "https://www.zotero.org/oauth/authorize"
ZOTERO_OAUTH_ACCESS_URL = "https://www.zotero.org/oauth/access"
ZOTERO_API_BASE = "https://api.zotero.org"

OAUTH_COOKIE = "zt_oauth_req"
_ENGINE_TTL = 600  # giây
_ENGINE_MAX = 32
_engines: Dict[str, Tuple[float, ZoteroConverterEngine]] = {}
_lock = threading.Lock()


# ── OAuth 1.0a (HMAC-SHA1) ───────────────────────────────────────────────────

def oauth_client() -> Tuple[str, str]:
    return (
        os.getenv("ZOTERO_OAUTH_CLIENT_KEY", "").strip(),
        os.getenv("ZOTERO_OAUTH_CLIENT_SECRET", "").strip(),
    )


def oauth_available() -> bool:
    key, secret = oauth_client()
    return bool(key and secret)


def _enc(s: Any) -> str:
    return urllib.parse.quote(str(s), safe="~")


def _oauth_header(method: str, url: str, extra: Dict[str, str], token_secret: str = "") -> str:
    consumer_key, consumer_secret = oauth_client()
    params = {
        "oauth_consumer_key": consumer_key,
        "oauth_nonce": secrets.token_hex(16),
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": str(int(time.time())),
        "oauth_version": "1.0",
        **extra,
    }
    norm = "&".join(f"{k}={v}" for k, v in sorted((_enc(k), _enc(v)) for k, v in params.items()))
    base = "&".join([method.upper(), _enc(url), _enc(norm)])
    key = f"{_enc(consumer_secret)}&{_enc(token_secret)}".encode()
    params["oauth_signature"] = base64.b64encode(hmac.new(key, base.encode(), hashlib.sha1).digest()).decode()
    return "OAuth " + ", ".join(f'{_enc(k)}="{_enc(v)}"' for k, v in sorted(params.items()))


def oauth_get_request_token(callback_url: str) -> Dict[str, str]:
    hdr = _oauth_header("POST", ZOTERO_OAUTH_REQUEST_URL, {"oauth_callback": callback_url})
    r = requests.post(ZOTERO_OAUTH_REQUEST_URL, headers={"Authorization": hdr}, timeout=15)
    r.raise_for_status()
    data = dict(urllib.parse.parse_qsl(r.text))
    if not data.get("oauth_token"):
        raise RuntimeError(f"Zotero không trả về request token: {r.text[:200]}")
    return data


def oauth_authorize_url(oauth_token: str) -> str:
    q = urllib.parse.urlencode({
        "oauth_token": oauth_token,
        "library_access": "1",
        "notes_access": "1",
        "write_access": "1",
        "all_groups": "read",
        "name": "WEB SUPER",
    })
    return f"{ZOTERO_OAUTH_AUTHORIZE_URL}?{q}"


def oauth_get_access_token(oauth_token: str, token_secret: str, verifier: str) -> Dict[str, str]:
    hdr = _oauth_header("POST", ZOTERO_OAUTH_ACCESS_URL,
                        {"oauth_token": oauth_token, "oauth_verifier": verifier}, token_secret)
    r = requests.post(ZOTERO_OAUTH_ACCESS_URL, headers={"Authorization": hdr}, timeout=15)
    r.raise_for_status()
    data = dict(urllib.parse.parse_qsl(r.text))
    if not data.get("oauth_token_secret") or not data.get("userID"):
        raise RuntimeError(f"Zotero không trả về access token: {r.text[:200]}")
    # Với Zotero, oauth_token_secret chính là API key của người dùng
    return {"api_key": data["oauth_token_secret"], "user_id": data["userID"], "username": data.get("username", "")}


def _cookie_secret() -> bytes:
    from modules.auth.auth_service import JWT_SECRET
    return ("zotero-oauth:" + JWT_SECRET).encode()


def sign_cookie(value: str) -> str:
    sig = hmac.new(_cookie_secret(), value.encode(), hashlib.sha256).hexdigest()
    return f"{value}|{sig}"


def verify_cookie(raw: Optional[str]) -> Optional[str]:
    if not raw or "|" not in raw:
        return None
    value, sig = raw.rsplit("|", 1)
    expected = hmac.new(_cookie_secret(), value.encode(), hashlib.sha256).hexdigest()
    return value if hmac.compare_digest(sig, expected) else None


def public_base_url(request: Request) -> str:
    proto = request.headers.get("x-forwarded-proto") or request.url.scheme
    host = request.headers.get("x-forwarded-host") or request.headers.get("host") or request.url.netloc
    return f"{proto.split(',')[0].strip()}://{host.split(',')[0].strip()}"


# ── API key ──────────────────────────────────────────────────────────────────

def validate_api_key(api_key: str) -> Dict[str, Any]:
    """Xác thực API key với api.zotero.org, trả về userID / username / quyền truy cập."""
    r = requests.get(f"{ZOTERO_API_BASE}/keys/current",
                     headers={"Zotero-API-Key": api_key, "Zotero-API-Version": "3"}, timeout=15)
    if r.status_code in (403, 404):
        raise ValueError("API key Zotero không hợp lệ hoặc đã bị thu hồi.")
    r.raise_for_status()
    data = r.json()
    access = (data.get("access") or {}).get("user") or {}
    return {
        "user_id": str(data.get("userID", "")),
        "username": data.get("username", ""),
        "can_read": bool(access.get("library")),
        "can_write": bool(access.get("write")),
    }


# ── Chọn engine theo request ─────────────────────────────────────────────────

def request_credentials(request: Request) -> Tuple[str, str, str]:
    h = request.headers
    return (
        (h.get("x-zotero-user-id") or "").strip(),
        (h.get("x-zotero-api-key") or "").strip(),
        (h.get("x-zotero-library-type") or "user").strip() or "user",
    )


def engine_for_request(request: Request) -> ZoteroConverterEngine:
    """Engine Zotero của người dùng hiện tại (theo header), hoặc engine mặc định của máy chủ."""
    user_id, api_key, lib_type = request_credentials(request)
    if not (user_id and api_key):
        return zotero_converter
    if lib_type not in ("user", "group"):
        lib_type = "user"

    cache_key = hashlib.sha256(f"{lib_type}:{user_id}:{api_key}".encode()).hexdigest()
    now = time.time()
    with _lock:
        hit = _engines.get(cache_key)
        if hit and now - hit[0] < _ENGINE_TTL:
            return hit[1]
        engine = ZoteroConverterEngine(user_id=user_id, api_key=api_key, library_type=lib_type)
        _engines[cache_key] = (now, engine)
        if len(_engines) > _ENGINE_MAX:
            oldest = min(_engines, key=lambda k: _engines[k][0])
            _engines.pop(oldest, None)
        return engine


def parse_library_json(raw: Optional[str]) -> Optional[List[Dict[str, Any]]]:
    """Đọc thư viện do trình duyệt gửi lên (lấy từ Zotero Desktop Local API)."""
    if not raw:
        return None
    try:
        items = json.loads(raw)
    except Exception:
        return None
    if not isinstance(items, list):
        return None
    out = []
    for it in items:
        if not isinstance(it, dict):
            continue
        data = it.get("data") if isinstance(it.get("data"), dict) else it
        if data.get("itemType") in ("attachment", "note", "annotation"):
            continue
        key = it.get("key") or data.get("key") or ""
        out.append({"key": key, "data": {**data, "key": key}})
    return out


def engine_with_library(base: ZoteroConverterEngine, items: Optional[List[Dict[str, Any]]]) -> ZoteroConverterEngine:
    if items is None:
        return base
    eng = copy.copy(base)
    eng._cache = list(items)
    eng._cache_loaded = True
    return eng


# ── Tệp kết quả gửi kèm response (Vercel) ────────────────────────────────────
# Trên Vercel, tệp được ghi vào /tmp của một máy chủ; yêu cầu "Tải về" sau đó có thể rơi vào
# máy chủ khác => 404. Vì vậy gửi luôn nội dung tệp (base64) trong kết quả để trình duyệt tự tải.

INLINE_EXTS = (".docx", ".ris", ".bib", ".md", ".txt", ".csv", ".xlsx", ".json")
INLINE_MAX_TOTAL = 3_500_000  # byte, dưới giới hạn response 4.5MB của Vercel


def is_serverless() -> bool:
    return bool(os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"))


def attach_inline_files(res: Any, force: bool = False) -> Any:
    if not isinstance(res, dict) or not (force or is_serverless()):
        return res
    from modules.shared.file_manager import file_mgr
    ws = file_mgr.workspace.resolve()
    inline: Dict[str, str] = {}
    total = 0
    for val in list(res.values()):
        if not isinstance(val, str) or not val.lower().endswith(INLINE_EXTS):
            continue
        rel = urllib.parse.unquote(val).replace("\\", "/")
        if rel.startswith("file:"):
            continue
        rel = rel.split("/workspace/", 1)[-1].lstrip("/")
        if rel in inline:
            continue
        try:
            fpath = (ws / rel).resolve()
            if not str(fpath).startswith(str(ws)) or not fpath.is_file():
                continue
            size = fpath.stat().st_size
            if total + size > INLINE_MAX_TOTAL:
                continue
            inline[rel] = base64.b64encode(fpath.read_bytes()).decode("ascii")
            total += size
        except OSError:
            continue
    if inline:
        res["inline_files"] = inline
    return res
