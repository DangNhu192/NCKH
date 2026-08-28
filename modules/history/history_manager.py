import json
import uuid
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from modules.shared.file_manager import WORKSPACE_DIR

HISTORY_DIR = WORKSPACE_DIR / ".history"
HISTORY_DIR.mkdir(parents=True, exist_ok=True)

def _sanitize_email_for_filename(email: Optional[str]) -> str:
    if not email or not email.strip():
        return "guest"
    clean = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', email.strip().lower())
    return clean or "guest"

class HistoryManager:
    def __init__(self):
        self.active_session_ids: Dict[str, str] = {}
        self._ensure_storage()

    def _get_history_file(self, user_email: Optional[str] = None) -> Path:
        clean = _sanitize_email_for_filename(user_email)
        fpath = HISTORY_DIR / f"history_{clean}.json"
        if not fpath.exists():
            try:
                legacy = HISTORY_DIR / "activity_history.json"
                if clean == "guest" and legacy.exists():
                    fpath.write_text(legacy.read_text(encoding="utf-8"), encoding="utf-8")
                else:
                    with open(fpath, "w", encoding="utf-8") as f:
                        json.dump([], f, ensure_ascii=False, indent=2)
            except Exception:
                pass
        return fpath

    def _get_sessions_file(self, user_email: Optional[str] = None) -> Path:
        clean = _sanitize_email_for_filename(user_email)
        fpath = HISTORY_DIR / f"sessions_{clean}.json"
        if not fpath.exists():
            try:
                legacy = HISTORY_DIR / "sessions_meta.json"
                if clean == "guest" and legacy.exists():
                    fpath.write_text(legacy.read_text(encoding="utf-8"), encoding="utf-8")
                else:
                    with open(fpath, "w", encoding="utf-8") as f:
                        json.dump({}, f, ensure_ascii=False, indent=2)
            except Exception:
                pass
        return fpath

    def _ensure_storage(self, user_email: Optional[str] = None):
        self._get_history_file(user_email)
        self._get_sessions_file(user_email)

    def _read_raw(self, user_email: Optional[str] = None) -> List[Dict[str, Any]]:
        fpath = self._get_history_file(user_email)
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _write_raw(self, entries: List[Dict[str, Any]], user_email: Optional[str] = None):
        fpath = self._get_history_file(user_email)
        try:
            with open(fpath, "w", encoding="utf-8") as f:
                json.dump(entries, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving history for {user_email}: {e}")

    def _read_sessions_meta(self, user_email: Optional[str] = None) -> Dict[str, Any]:
        fpath = self._get_sessions_file(user_email)
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _write_sessions_meta(self, meta: Dict[str, Any], user_email: Optional[str] = None):
        fpath = self._get_sessions_file(user_email)
        try:
            with open(fpath, "w", encoding="utf-8") as f:
                json.dump(meta, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving sessions meta for {user_email}: {e}")

    def create_session(self, title: str = "", topic: str = "", user_email: Optional[str] = None) -> Dict[str, Any]:
        """Tạo phiên nghiên cứu / thao tác mới cho người dùng cụ thể"""
        now = datetime.now()
        session_id = f"sess_{now.strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        clean_topic = (topic or "").strip()
        default_title = f"Phiên: {clean_topic}" if clean_topic else f"Phiên làm việc {now.strftime('%d/%m/%Y %H:%M')}"
        session_title = (title or "").strip() or default_title

        meta = self._read_sessions_meta(user_email)
        session_data = {
            "session_id": session_id,
            "session_title": session_title,
            "topic": clean_topic,
            "user_email": (user_email or "").strip().lower(),
            "created_at_iso": now.isoformat(),
            "created_at_display": now.strftime("%d/%m/%Y %H:%M:%S"),
            "updated_at_display": now.strftime("%d/%m/%Y %H:%M:%S"),
            "timestamp": now.timestamp(),
            "actions_count": 0
        }
        meta[session_id] = session_data
        meta["_active_session_id"] = session_id
        clean_key = _sanitize_email_for_filename(user_email)
        self.active_session_ids[clean_key] = session_id
        self._write_sessions_meta(meta, user_email)
        return session_data

    def get_active_session(self, user_email: Optional[str] = None) -> Dict[str, Any]:
        """Lấy phiên làm việc hiện tại của người dùng hoặc tự động tạo nếu chưa có"""
        meta = self._read_sessions_meta(user_email)
        clean_key = _sanitize_email_for_filename(user_email)
        active_id = self.active_session_ids.get(clean_key) or meta.get("_active_session_id")
        if active_id and active_id in meta:
            return meta[active_id]
        
        return self.create_session(user_email=user_email)

    def set_active_session(self, session_id: str, user_email: Optional[str] = None) -> bool:
        meta = self._read_sessions_meta(user_email)
        if session_id in meta:
            meta["_active_session_id"] = session_id
            clean_key = _sanitize_email_for_filename(user_email)
            self.active_session_ids[clean_key] = session_id
            self._write_sessions_meta(meta, user_email)
            return True
        return False

    def rename_session(self, session_id: str, new_title: str, user_email: Optional[str] = None) -> bool:
        meta = self._read_sessions_meta(user_email)
        if session_id in meta and new_title.strip():
            meta[session_id]["session_title"] = new_title.strip()
            self._write_sessions_meta(meta, user_email)

            entries = self._read_raw(user_email)
            for e in entries:
                if e.get("session_id") == session_id:
                    e["session_title"] = new_title.strip()
            self._write_raw(entries, user_email)
            return True
        return False

    def get_history(
        self,
        limit: int = 100,
        module: Optional[str] = None,
        query: Optional[str] = None,
        session_id: Optional[str] = None,
        user_email: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        entries = self._read_raw(user_email)
        
        if session_id and session_id != "all":
            entries = [e for e in entries if e.get("session_id") == session_id]

        if module and module != "all":
            entries = [e for e in entries if e.get("module") == module]

        if query:
            q = query.lower().strip()
            entries = [
                e for e in entries
                if q in e.get("action_title", "").lower()
                or q in e.get("summary", "").lower()
                or q in e.get("session_title", "").lower()
                or q in str(e.get("inputs", {})).lower()
                or q in e.get("created_at_display", "").lower()
            ]

        entries.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
        return entries[:limit]

    def get_sessions(
        self,
        limit: int = 50,
        module: Optional[str] = None,
        query: Optional[str] = None,
        user_email: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Lấy danh sách các Phiên thao tác nhóm kèm toàn bộ lịch sử bên trong của riêng người dùng"""
        entries = self._read_raw(user_email)
        meta = self._read_sessions_meta(user_email)

        session_groups: Dict[str, List[Dict[str, Any]]] = {}
        for e in entries:
            s_id = e.get("session_id")
            if not s_id:
                date_str = e.get("created_at_display", "").split(" ")[0] if " " in e.get("created_at_display", "") else "Chung"
                topic_str = (e.get("inputs", {}).get("topic") or e.get("action_title", "Hoạt động")).strip()[:30]
                s_id = f"legacy_{date_str.replace('/', '_')}_{topic_str.replace(' ', '_')}"
                e["session_id"] = s_id
                e["session_title"] = f"Phiên: {topic_str} ({date_str})"
            
            if s_id not in session_groups:
                session_groups[s_id] = []
            session_groups[s_id].append(e)

        sessions_list = []
        for s_id, act_list in session_groups.items():
            act_list.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
            
            s_meta = meta.get(s_id, {})
            title = s_meta.get("session_title") or act_list[0].get("session_title") or act_list[0].get("action_title", "Phiên nghiên cứu")
            topic = s_meta.get("topic") or act_list[0].get("inputs", {}).get("topic", "")
            
            first_ts = act_list[-1].get("timestamp", 0)
            last_ts = act_list[0].get("timestamp", 0)
            created_disp = act_list[-1].get("created_at_display", "")
            updated_disp = act_list[0].get("created_at_display", "")

            filtered_actions = act_list
            if module and module != "all":
                filtered_actions = [a for a in act_list if a.get("module") == module]
                if not filtered_actions:
                    continue

            if query:
                q = query.lower().strip()
                match_session = q in title.lower() or q in topic.lower() or q in created_disp.lower()
                if not match_session:
                    filtered_actions = [
                        a for a in filtered_actions
                        if q in a.get("action_title", "").lower()
                        or q in a.get("summary", "").lower()
                        or q in str(a.get("inputs", {})).lower()
                    ]
                    if not filtered_actions:
                        continue

            modules_used = list(set(a.get("module") for a in act_list if a.get("module")))
            
            sessions_list.append({
                "session_id": s_id,
                "session_title": title,
                "topic": topic,
                "created_at_display": created_disp,
                "updated_at_display": updated_disp,
                "timestamp": last_ts or first_ts,
                "actions_count": len(filtered_actions),
                "total_session_actions": len(act_list),
                "modules_used": modules_used,
                "actions": filtered_actions
            })

        sessions_list.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
        return sessions_list[:limit]

    def add_entry(
        self,
        module: str,
        action_title: str,
        inputs: Dict[str, Any],
        result_data: Dict[str, Any],
        summary: str = "",
        extra_meta: Optional[Dict[str, Any]] = None,
        user_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """Thêm mới 1 bản ghi lịch sử thao tác gắn liền với Phiên làm việc (Session) của tài khoản"""
        extra_meta = extra_meta or {}
        resolved_email = (user_email or extra_meta.get("user_email") or inputs.get("user_email") or "").strip().lower()

        entries = self._read_raw(resolved_email)
        meta = self._read_sessions_meta(resolved_email)
        now = datetime.now()
        entry_id = f"hist_{now.strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"

        session_id = extra_meta.get("session_id")
        topic = (inputs.get("topic") or extra_meta.get("topic") or "").strip()

        if not session_id:
            active_session = self.get_active_session(resolved_email)
            session_id = active_session["session_id"]
            meta = self._read_sessions_meta(resolved_email)
            
            if topic and ("Phiên làm việc" in active_session.get("session_title", "") or not active_session.get("topic")):
                new_title = f"Phiên: {topic}"
                if session_id in meta:
                    meta[session_id]["session_title"] = new_title
                    meta[session_id]["topic"] = topic
                    self._write_sessions_meta(meta, resolved_email)

        session_title = meta.get(session_id, {}).get("session_title", "Phiên nghiên cứu")

        artifacts = []
        if isinstance(result_data, dict):
            for k in ["files", "saved_papers", "artifacts", "download_links"]:
                if k in result_data and isinstance(result_data[k], list):
                    for item in result_data[k]:
                        if isinstance(item, dict) and "name" in item:
                            artifacts.append({
                                "name": item.get("name"),
                                "rel_path": item.get("rel_path") or item.get("name"),
                                "file_url": item.get("file_url") or f"/api/files/download?path={item.get('name')}",
                                "format": item.get("format") or (item.get("name").split(".")[-1] if "." in item.get("name") else "txt")
                            })
            if "final_artifact" in result_data and isinstance(result_data["final_artifact"], dict):
                fa = result_data["final_artifact"]
                artifacts.append({
                    "name": fa.get("docx_rel_path", "Bao_cao_xuat_ban.docx").split("/")[-1],
                    "rel_path": fa.get("docx_rel_path"),
                    "file_url": fa.get("file_url") or f"/api/files/download?path={fa.get('docx_rel_path')}",
                    "format": "docx"
                })

        entry = {
            "id": entry_id,
            "entry_id": entry_id,
            "session_id": session_id,
            "session_title": session_title,
            "user_email": resolved_email,
            "module": module,
            "action_title": action_title,
            "summary": summary or self._generate_summary(module, action_title, inputs, result_data),
            "inputs": inputs,
            "result_preview": self._build_preview(result_data),
            "artifacts": artifacts,
            "extra_meta": extra_meta,
            "created_at_iso": now.isoformat(),
            "created_at_display": now.strftime("%d/%m/%Y %H:%M:%S"),
            "timestamp": now.timestamp()
        }

        entries.insert(0, entry)
        self._write_raw(entries, resolved_email)

        if session_id in meta:
            meta[session_id]["updated_at_display"] = now.strftime("%d/%m/%Y %H:%M:%S")
            meta[session_id]["timestamp"] = now.timestamp()
            meta[session_id]["actions_count"] = meta[session_id].get("actions_count", 0) + 1
            self._write_sessions_meta(meta, resolved_email)

        return entry

    def _generate_summary(self, module: str, action: str, inputs: dict, res: dict) -> str:
        topic = inputs.get("topic") or inputs.get("query") or ""
        if module == "harvester":
            cnt = len(res.get("saved_papers") or res.get("files") or res.get("papers") or [])
            return f"Thu thập {cnt} tài liệu học thuật cho đề tài: '{topic}'"
        elif module == "pipeline":
            step = inputs.get("step_no", "")
            return f"Thực thi Bước {step} Quy trình 7 Bước: '{topic}'"
        elif module == "humanizer":
            score = res.get("human_score") or res.get("after_analysis", {}).get("human_score") or "95%"
            return f"Khử dấu vết AI & chống Turnitin (Human Score: {score})"
        elif module == "academic_writer":
            return f"Viết học thuật Bộ đôi 2-File: '{topic}'"
        elif module == "editorial_office":
            dept = inputs.get("department_name") or inputs.get("department_id") or "Tòa soạn"
            return f"Biên tập báo chí qua {dept}: '{topic}'"
        elif module == "zotero":
            return f"Chuyển đổi mã trích dẫn Zotero CSL trong Word (.docx)"
        return f"{action}: {topic}" if topic else action

    def _build_preview(self, res: Any) -> Dict[str, Any]:
        if not isinstance(res, dict):
            return {"raw": str(res)[:300]}
        preview = {}
        for k in ["status", "gate", "message", "human_score", "similarity_index", "total_found", "total_harvested"]:
            if k in res:
                preview[k] = res[k]
        if "after_analysis" in res:
            preview["human_score"] = res["after_analysis"].get("human_score")
            preview["similarity_index"] = res["after_analysis"].get("similarity_index")
        return preview

    def delete_entry(self, entry_id: str, user_email: Optional[str] = None) -> bool:
        entries = self._read_raw(user_email)
        initial_len = len(entries)
        entries = [e for e in entries if e.get("entry_id") != entry_id and e.get("id") != entry_id]
        if len(entries) < initial_len:
            self._write_raw(entries, user_email)
            return True
        return False

    def delete_entries_batch(self, entry_ids: List[str], user_email: Optional[str] = None) -> int:
        entries = self._read_raw(user_email)
        initial_len = len(entries)
        id_set = set(entry_ids)
        entries = [e for e in entries if e.get("entry_id") not in id_set]
        cleared = initial_len - len(entries)
        if cleared > 0:
            self._write_raw(entries, user_email)
        return cleared

    def delete_session(self, session_id: str, user_email: Optional[str] = None) -> bool:
        meta = self._read_sessions_meta(user_email)
        entries = self._read_raw(user_email)
        
        found = False
        if session_id in meta:
            del meta[session_id]
            found = True
            if meta.get("_active_session_id") == session_id:
                meta["_active_session_id"] = None
            self._write_sessions_meta(meta, user_email)

        new_entries = [e for e in entries if e.get("session_id") != session_id]
        if len(new_entries) < len(entries):
            found = True
            self._write_raw(new_entries, user_email)

        return found

    def delete_sessions_batch(self, session_ids: List[str], user_email: Optional[str] = None) -> int:
        s_set = set(session_ids)
        meta = self._read_sessions_meta(user_email)
        entries = self._read_raw(user_email)
        
        cleared = 0
        for sid in s_set:
            if sid in meta:
                del meta[sid]
                cleared += 1
                if meta.get("_active_session_id") == sid:
                    meta["_active_session_id"] = None
        self._write_sessions_meta(meta, user_email)

        new_entries = [e for e in entries if e.get("session_id") not in s_set]
        self._write_raw(new_entries, user_email)
        return cleared

    def clear_all(self, user_email: Optional[str] = None):
        self._write_raw([], user_email)
        self._write_sessions_meta({}, user_email)

history_mgr = HistoryManager()
