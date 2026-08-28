# backend/openai_service.py
"""
OpenAI / ChatGPT Service for WEB SUPER v2.0
Integrates ChatGPT (GPT-4o, GPT-4o-mini, GPT-4-turbo) with Google Gemini
for Dual-AI Multi-Agent Collaboration and Academic Polish.
"""

import os
import json
import time
from typing import Optional, Dict, Any, List
from pathlib import Path
import requests

from modules.shared.file_manager import file_mgr

CONFIG_FILE = Path(__file__).resolve().parent.parent.parent / "config.json"


class OpenAIService:
    def __init__(self):
        self.default_model = "gpt-4o"
        self.fallback_model = "gpt-4o-mini"

    def _get_config(self) -> dict:
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _get_api_key(self) -> str:
        key = os.getenv("OPENAI_API_KEY", "").strip()
        if not key:
            cfg = self._get_config()
            key = cfg.get("openai_api_key", "").strip()
        return key

    def has_api_key(self, api_key: str = None) -> bool:
        k = api_key or self._get_api_key()
        return bool(k and len(k) >= 15 and k.startswith("sk-"))

    def generate_text(
        self,
        prompt: str,
        system_instruction: str = "Bạn là Chuyên gia Biên tập Học thuật & Phản biện Khoa học Quốc tế (Lead Peer Reviewer & Academic Editor).",
        model: str = None,
        api_key: str = None,
        temperature: float = 0.4,
        timeout: int = 12
    ) -> Optional[str]:
        """Calls OpenAI Chat Completion API with robust error handling"""
        key = api_key or self._get_api_key()
        if not key or len(key) < 15:
            return None

        target_model = model or self.default_model
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}"
        }
        payload = {
            "model": target_model,
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "max_tokens": 4096
        }

        try:
            res = requests.post(url, headers=headers, json=payload, timeout=timeout)
            if res.status_code == 200:
                data = res.json()
                choices = data.get("choices", [])
                if choices and "message" in choices[0]:
                    content = choices[0]["message"].get("content", "").strip()
                    file_mgr.add_log("openai_service", f"OpenAI ({target_model}) phản hồi thành công ({len(content)} ký tự)")
                    return content
            elif res.status_code == 429 or "quota" in res.text.lower():
                file_mgr.add_log("openai_service", "OpenAI API hết hạn ngạch (429 Insufficient Quota). Tự động chuyển 100% sang Google Gemini Engine.")
                return None
            elif res.status_code == 404 or "model" in res.text.lower():
                payload["model"] = self.fallback_model
                res2 = requests.post(url, headers=headers, json=payload, timeout=min(timeout, 8))
                if res2.status_code == 200:
                    data2 = res2.json()
                    choices = data2.get("choices", [])
                    if choices and "message" in choices[0]:
                        return choices[0]["message"].get("content", "").strip()
            
            file_mgr.add_log("openai_service", f"Lỗi OpenAI API: HTTP {res.status_code} - {res.text[:200]}")
            return None
        except Exception as e:
            file_mgr.add_log("openai_service", f"Ngoại lệ kết nối OpenAI: {e}")
            return None

    def polish_academic_text(self, draft_text: str, topic: str, api_key: str = None) -> str:
        """Uses ChatGPT to refine and elevate the academic draft to peer-review standards"""
        if not self.has_api_key(api_key):
            return draft_text

        prompt = (
            f"Hãy đóng vai trò là Trưởng ban Biên tập Học thuật (Lead Academic Editor) của một Tạp chí Khoa học Quốc tế uy tín (Scopus Q1).\n"
            f"Nhiệm vụ của bạn: Rà soát, trau chuốt và nâng cao chất lượng học thuật của bản thảo chuyên đề sau đây về chủ đề \"{topic}\".\n\n"
            f"TIÊU CHÍ BIÊN TẬP BẮT BUỘC:\n"
            f"1. KHỬ TRIỆT ĐỂ KHUÔN MẪU VĂN PHONG AI:\n"
            f"   - Loại bỏ các từ ngữ sáo rỗng, sáo ngữ (như 'đóng vai trò quan trọng', 'là một bức tranh', 'như chúng ta đã biết', 'tóm lại', 'không thể phủ nhận', v.v.).\n"
            f"   - Đa dạng hóa độ dài câu: Kết hợp nhuần nhuyễn câu ngắn khẳng định đanh thép và câu ghép phân tích lập luận sâu.\n"
            f"2. TĂNG CƯỜNG TÍNH LOGIC & TÍNH HỌC THUẬT:\n"
            f"   - Đảm bảo các luận điểm có tính liên kết chặt chẽ theo cấu trúc 3 tầng: Bối cảnh -> Cơ chế -> Tác động & Hàm ý.\n"
            f"   - Giữ nguyên 100% các số liệu thực chứng, công thức và các trích dẫn tác giả (Author, Year) đã có trong văn bản gốc.\n"
            f"3. GIỮ NGUYÊN TOÀN BỘ CẤU TRÚC TIÊU ĐỀ ĐỀ MỤC:\n"
            f"   - Giữ nguyên các tiêu đề Heading (#, ##, 1.1, 1.2, Bảng biểu).\n\n"
            f"BẢN THẢO CẦN BIÊN TẬP:\n\"\"\"\n{draft_text}\n\"\"\"\n\n"
            f"HÃY XUẤT RA TOÀN BỘ VĂN BẢN ĐÃ ĐƯỢC BIÊN TẬP HOÀN CHỈNH (KHÔNG KÈM LỜI DẪN CỦA AI):"
        )

        polished = self.generate_text(prompt, api_key=api_key, temperature=0.3)
        return polished if polished and len(polished.strip()) > len(draft_text) * 0.6 else draft_text


openai_service = OpenAIService()

