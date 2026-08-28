import os
import re
import json
import time
from typing import List, Dict, Any, Optional
from pathlib import Path
import requests

from modules.shared.file_manager import file_mgr

CONFIG_FILE = Path(__file__).resolve().parent.parent.parent / "config.json"

OFFICIAL_FALLBACK_MODELS = [
    {
        "name": "models/gemini-3.6-flash",
        "clean_name": "gemini-3.6-flash",
        "displayName": "Gemini 3.6 Flash (Khuyến nghị chuẩn)",
        "description": "Mô hình Flash thế hệ mới nhất của Google, cân bằng tối ưu giữa tốc độ và chất lượng lập luận học thuật.",
        "inputTokenLimit": 1048576,
        "outputTokenLimit": 8192,
        "is_latest": True,
        "score": 400
    },
    {
        "name": "models/gemini-3.7-flash",
        "clean_name": "gemini-3.7-flash",
        "displayName": "Gemini 3.7 Flash (Lập luận nâng cao)",
        "description": "Mô hình Flash cao cấp, hỗ trợ suy luận sâu cho nghiên cứu khoa học.",
        "inputTokenLimit": 1048576,
        "outputTokenLimit": 8192,
        "is_latest": False,
        "score": 390
    },
    {
        "name": "models/gemini-1.5-flash",
        "clean_name": "gemini-1.5-flash",
        "displayName": "Gemini 1.5 Flash (Tiêu chuẩn)",
        "description": "Mô hình Flash phổ biến, độ tin cậy và tính tương thích cao.",
        "inputTokenLimit": 1048576,
        "outputTokenLimit": 8192,
        "is_latest": False,
        "score": 350
    },
    {
        "name": "models/gemini-1.5-pro",
        "clean_name": "gemini-1.5-pro",
        "displayName": "Gemini 1.5 Pro (Ngữ cảnh 2M token)",
        "description": "Mô hình Pro ổn định với cửa sổ ngữ cảnh 2 triệu token.",
        "inputTokenLimit": 2097152,
        "outputTokenLimit": 8192,
        "is_latest": False,
        "score": 320
    }
]

class GeminiService:
    def __init__(self):
        self._cached_models_by_key: Dict[str, List[Dict[str, Any]]] = {}
        self._cache_timestamp: Dict[str, float] = {}
        self._cache_ttl: float = 600  # Cache 10 phút per key
        self._model_429_until: Dict[str, float] = {}

    def _get_config(self) -> dict:
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _get_api_key(self) -> str:
        key = os.getenv("GEMINI_API_KEY", "").strip()
        if not key:
            cfg = self._get_config()
            key = cfg.get("gemini_api_key", "").strip()
        return key

    def has_api_key(self) -> bool:
        k = self._get_api_key()
        return bool(k and len(k) >= 8)

    def generate_content(self, prompt: str, **kwargs) -> Optional[str]:
        return self.generate_text(prompt, **kwargs)

    def _rank_model(self, model_info: dict) -> float:
        name = model_info.get("name", "").replace("models/", "").lower()
        score = 0.0

        v_match = re.search(r'gemini-(\d+(?:\.\d+)?)', name)
        if v_match:
            try:
                version = float(v_match.group(1))
                score += version * 100
            except ValueError:
                pass
        elif "gemini" in name:
            score += 100

        if "flash" in name and "lite" not in name and "8b" not in name:
            score += 30
        elif "pro" in name:
            score += 35
        elif "flash-lite" in name or "lite" in name:
            score += 15
        elif "8b" in name:
            score += 10

        if "3.6-flash" in name:
            score += 150

        if "exp" in name or "preview" in name or "experimental" in name:
            score -= 5
        if "001" in name or "002" in name or "deprecated" in name or "legacy" in name:
            score -= 20

        return score

    def fetch_available_models(self, api_key: str = None, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Truy vấn trực tiếp danh sách mô hình thực tế từ Google AI API (https://generativelanguage.googleapis.com/v1beta/models)
        Không tự tạo danh sách giả lập. Nếu lỗi hoặc key không hợp lệ, trả về lỗi chi tiết từ Google.
        """
        key = (api_key if api_key is not None else self._get_api_key() or "").strip()
        now = time.time()

        if not key or len(key) < 8:
            return {
                "success": False,
                "source": "no_key",
                "total": 0,
                "models": [],
                "error": "Chưa có API Key. Vui lòng nhập Google Gemini API Key và bấm 'Làm Mới' để tải danh sách mô hình thực tế từ Google."
            }

        # Check in-memory cache for this specific API key
        if not force_refresh and key in self._cached_models_by_key:
            last_time = self._cache_timestamp.get(key, 0)
            if (now - last_time) < self._cache_ttl:
                cached = self._cached_models_by_key[key]
                return {
                    "success": True,
                    "source": "cache",
                    "total": len(cached),
                    "models": cached
                }

        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"
            res = requests.get(url, timeout=12)
            if res.status_code == 200:
                data = res.json()
                raw_models = data.get("models", [])
                
                valid_models = []
                for m in raw_models:
                    supported = m.get("supportedGenerationMethods", [])
                    m_name = m.get("name", "")
                    clean_name = m_name.replace("models/", "")
                    
                    if "generateContent" in supported:
                        score = self._rank_model(m)
                        display_name = m.get("displayName") or clean_name
                        desc = m.get("description") or "Mô hình ngôn ngữ lớn từ Google DeepMind."
                        
                        valid_models.append({
                            "name": m_name,
                            "clean_name": clean_name,
                            "displayName": display_name,
                            "description": desc,
                            "inputTokenLimit": m.get("inputTokenLimit", 1048576),
                            "outputTokenLimit": m.get("outputTokenLimit", 8192),
                            "supportedGenerationMethods": supported,
                            "temperature": m.get("temperature"),
                            "topP": m.get("topP"),
                            "topK": m.get("topK"),
                            "score": score,
                            "is_latest": False
                        })

                if valid_models:
                    valid_models.sort(key=lambda x: x["score"], reverse=True)
                    valid_models[0]["is_latest"] = True
                    self._cached_models_by_key[key] = valid_models
                    self._cache_timestamp[key] = now
                    file_mgr.add_log("gemini_service", f"Đã quét và tải trực tiếp {len(valid_models)} mô hình Google Gemini thực tế. Mô hình ưu tiên: {valid_models[0]['clean_name']}")
                    return {
                        "success": True,
                        "source": "google_api",
                        "total": len(valid_models),
                        "models": valid_models,
                        "active_model": self.get_active_model(key)
                    }
                else:
                    return {
                        "success": False,
                        "source": "google_api_empty",
                        "total": 0,
                        "models": [],
                        "error": "Google API không trả về mô hình nào hỗ trợ sinh nội dung (generateContent) cho API Key này."
                    }
            else:
                try:
                    err_json = res.json()
                    err_msg = err_json.get("error", {}).get("message", res.text)
                except Exception:
                    err_msg = res.text
                file_mgr.add_log("gemini_service", f"Lỗi Google AI (HTTP {res.status_code}): {err_msg}")
                return {
                    "success": False,
                    "source": "google_api_error",
                    "status_code": res.status_code,
                    "total": 0,
                    "models": [],
                    "error": f"Lỗi Google AI (HTTP {res.status_code}): {err_msg}"
                }
        except Exception as e:
            file_mgr.add_log("gemini_service", f"Lỗi kết nối máy chủ Google API: {e}")
            return {
                "success": False,
                "source": "network_error",
                "total": 0,
                "models": [],
                "error": f"Lỗi kết nối máy chủ Google API: {str(e)}"
            }

    def list_available_models(self, api_key: str = None, force_refresh: bool = False) -> Dict[str, Any]:
        """Alias cho fetch_available_models để tương thích toàn diện với auth_router và frontend"""
        res = self.fetch_available_models(api_key=api_key, force_refresh=force_refresh)
        if res.get("success") and "active_model" not in res:
            res["active_model"] = self.get_active_model(api_key)
        return res

    def get_active_model(self, api_key: str = None) -> str:
        cfg = self._get_config()
        user_choice = cfg.get("selected_gemini_model", "auto")
        if user_choice and user_choice != "auto":
            return user_choice.replace("models/", "")

        fetch_res = self.fetch_available_models(api_key)
        if fetch_res.get("success") and fetch_res.get("models"):
            return fetch_res["models"][0]["clean_name"]
        return "gemini-3.6-flash"

    def generate_text(self, prompt: str, model_name: str = None, api_key: str = None, timeout: int = 90) -> Optional[str]:
        """
        Gọi Google Gemini API sinh văn bản với danh sách mô hình thực tế.
        """
        key = (api_key or "").strip()
        if not key:
            cfg = self._get_config()
            key = (cfg.get("gemini_api_key") or os.getenv("GEMINI_API_KEY") or "").strip()

        if not key or len(key) < 8:
            file_mgr.add_log("gemini_service", "Không tìm thấy API key cá nhân. User cần nhập API Gemini trong Cài Đặt.")
            return None

        if hasattr(self, "_quota_exhausted_until") and time.time() < self._quota_exhausted_until:
            return None

        preferred_model = model_name or self.get_active_model(key)
        
        # Candidate models for failover (active Google v1beta models)
        candidate_models = [
            "gemini-3.6-flash",
            preferred_model,
            "gemini-3.7-flash",
            "gemini-flash-latest",
            "gemini-pro-latest"
        ]
        seen = set()
        ordered_candidates = []
        for m in candidate_models:
            c = m.replace("models/", "").strip()
            if c and c not in seen:
                seen.add(c)
                ordered_candidates.append(c)

        now_t = time.time()
        for attempt_model in ordered_candidates:
            if self._model_429_until.get(attempt_model, 0) > now_t:
                continue

            url = f"https://generativelanguage.googleapis.com/v1beta/models/{attempt_model}:generateContent?key={key}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.5,
                    "topP": 0.95,
                    "maxOutputTokens": 8192
                }
            }

            try:
                effective_timeout = min(timeout, 75)
                res = requests.post(url, json=payload, timeout=effective_timeout)
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        text_out = candidates[0]["content"]["parts"][0]["text"]
                        file_mgr.add_log("gemini_service", f"Thành công sinh văn bản với mô hình: {attempt_model} ({len(text_out)} ký tự)")
                        return text_out
                elif res.status_code == 429:
                    self._model_429_until[attempt_model] = time.time() + 60
                    file_mgr.add_log("gemini_service", f"Mô hình '{attempt_model}' tạm chạm hạn mức (HTTP 429). Đang chuyển sang mô hình tiếp theo...")
                    continue
                elif res.status_code in [404, 400]:
                    file_mgr.add_log("gemini_service", f"Mô hình '{attempt_model}' trả về {res.status_code}. Thử mô hình tiếp theo...")
                    continue
                else:
                    file_mgr.add_log("gemini_service", f"Gọi Gemini ({attempt_model}) thất bại: HTTP {res.status_code} - {res.text[:200]}")
            except Exception as e:
                file_mgr.add_log("gemini_service", f"Ngoại lệ khi gọi Gemini ({attempt_model}): {e}")

        return None

    def generate_vision_text(self, prompt: str, image_bytes: bytes, mime_type: str = "image/jpeg", model_name: str = None, api_key: str = None, timeout: int = 90) -> Optional[str]:
        """
        Gọi Google Gemini Multimodal Vision API để đọc ảnh trang tài liệu scan và thực hiện OCR chính xác cao.
        """
        import base64
        key = (api_key or "").strip()
        if not key:
            cfg = self._get_config()
            key = (cfg.get("gemini_api_key") or os.getenv("GEMINI_API_KEY") or "").strip()

        if not key or len(key) < 8:
            file_mgr.add_log("gemini_service", "Không tìm thấy API key cá nhân cho Vision OCR.")
            return None

        if hasattr(self, "_quota_exhausted_until") and time.time() < self._quota_exhausted_until:
            return None

        preferred_model = model_name or self.get_active_model(key)
        candidate_models = ["gemini-3.6-flash", preferred_model, "gemini-3.7-flash", "gemini-flash-latest"]
        seen = set()
        ordered_candidates = []
        for m in candidate_models:
            c = m.replace("models/", "").strip()
            if c and c not in seen:
                seen.add(c)
                ordered_candidates.append(c)

        b64_image = base64.b64encode(image_bytes).decode("utf-8")

        now_t = time.time()
        for attempt_model in ordered_candidates:
            if self._model_429_until.get(attempt_model, 0) > now_t:
                continue

            url = f"https://generativelanguage.googleapis.com/v1beta/models/{attempt_model}:generateContent?key={key}"
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt},
                            {
                                "inlineData": {
                                    "mimeType": mime_type,
                                    "data": b64_image
                                }
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.1,
                    "topP": 0.95,
                    "maxOutputTokens": 8192
                }
            }

            try:
                effective_timeout = min(timeout, 35)
                res = requests.post(url, json=payload, timeout=effective_timeout)
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        text_out = candidates[0]["content"]["parts"][0]["text"]
                        file_mgr.add_log("gemini_service", f"Vision OCR thành công ({attempt_model}): {len(text_out)} ký tự")
                        return text_out
                elif res.status_code == 429:
                    self._quota_exhausted_until = time.time() + 60
                    file_mgr.add_log("gemini_service", f"Vision OCR Quota 429 trên {attempt_model}.")
                    break
                elif res.status_code in [404, 400]:
                    file_mgr.add_log("gemini_service", f"Vision OCR {attempt_model} trả về {res.status_code}. Thử mô hình khác...")
                    continue
                else:
                    file_mgr.add_log("gemini_service", f"Vision OCR lỗi HTTP {res.status_code}: {res.text[:200]}")
            except Exception as e:
                file_mgr.add_log("gemini_service", f"Ngoại lệ Vision OCR ({attempt_model}): {e}")

        return None

    def check_connection(self, api_key: str = None) -> Dict[str, Any]:
        key = api_key or self._get_api_key()
        if not key or len(key) < 8:
            return {"status": "unconfigured", "active_model": None, "message": "Chưa cấu hình API Key"}
        try:
            res = self.fetch_available_models(api_key=key)
            if res.get("success"):
                active = self.get_active_model(api_key=key)
                return {"status": "connected", "active_model": active, "available_models_count": res.get("total", 0)}
            else:
                return {"status": "error", "error": res.get("error")}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def has_api_key(self, api_key: str = None) -> bool:
        k = (api_key or self._get_api_key() or "").strip()
        return bool(k and len(k) >= 8)

    def generate_content(self, prompt: str, **kwargs) -> Optional[str]:
        return self.generate_text(prompt, **kwargs)

gemini_service = GeminiService()
