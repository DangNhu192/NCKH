# audit_tab_buttons.py
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path("H:/My Drive/Ho so ca nhan/b. ThS KHMT/Skill/Web Super")
INDEX_HTML = ROOT / "static" / "index.html"
JS_DIR = ROOT / "static" / "js"

def audit_tabs():
    html = INDEX_HTML.read_text(encoding="utf-8")
    
    # Split by section / tab-pane
    section_matches = list(re.finditer(r'<section\s+id=["\']([^"\']+)["\']\s+class=["\']([^"\']*)tab-pane([^"\']*)["\']', html))
    
    tab_sections = []
    for i, sm in enumerate(section_matches):
        tab_id = sm.group(1)
        start_pos = sm.start()
        end_pos = section_matches[i+1].start() if i+1 < len(section_matches) else len(html)
        tab_sections.append({
            "tab_id": tab_id,
            "content": html[start_pos:end_pos]
        })
        
    all_js = {}
    for jf in JS_DIR.glob("*.js"):
        all_js[jf.name] = jf.read_text(encoding="utf-8")
        
    full_js_text = "\n".join(all_js.values())
    
    tab_results = {}
    for ts in tab_sections:
        tid = ts["tab_id"]
        sec_content = ts["content"]
        
        btn_matches = list(re.finditer(r'<button\b([^>]*)>(.*?)</button>', sec_content, re.DOTALL | re.IGNORECASE))
        tab_buttons = []
        
        for bm in btn_matches:
            attrs = bm.group(1)
            inner = re.sub(r'<[^>]+>', '', bm.group(2)).strip()[:35]
            id_m = re.search(r'id=["\']([^"\']+)["\']', attrs)
            onclick_m = re.search(r'onclick=["\']([^"\']+)["\']', attrs)
            class_m = re.search(r'class=["\']([^"\']+)["\']', attrs)
            
            btn_id = id_m.group(1) if id_m else None
            onclick = onclick_m.group(1) if onclick_m else None
            btn_cls = class_m.group(1) if class_m else ""
            
            handlers = []
            if onclick:
                handlers.append(f"inline: {onclick}")
            if btn_id:
                for jname, jtext in all_js.items():
                    if f"'{btn_id}'" in jtext or f'"{btn_id}"' in jtext or f'`{btn_id}`' in jtext:
                        handlers.append(f"{jname}")
            if "modal-close" in btn_cls or "btn-close" in btn_cls:
                handlers.append("modal-close class")
                
            tab_buttons.append({
                "id": btn_id,
                "text": inner,
                "handlers": handlers,
                "is_active": len(handlers) > 0
            })
            
        tab_results[tid] = {
            "total_buttons": len(tab_buttons),
            "active_buttons": sum(1 for b in tab_buttons if b["is_active"]),
            "dead_buttons": [b for b in tab_buttons if not b["is_active"]],
            "buttons": tab_buttons
        }
        
    for tid, res in tab_results.items():
        print(f"\n[{tid}] Total: {res['total_buttons']} | Active: {res['active_buttons']} | Dead: {len(res['dead_buttons'])}")
        if res['dead_buttons']:
            for db in res['dead_buttons']:
                print(f"  [DEAD] ID: {db['id']} | Text: '{db['text']}'")

if __name__ == "__main__":
    audit_tabs()
