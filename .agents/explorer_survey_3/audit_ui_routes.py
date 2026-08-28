# audit_ui_routes.py
import re
import os
import json
from pathlib import Path

ROOT = Path("H:/My Drive/Ho so ca nhan/b. ThS KHMT/Skill/Web Super")
INDEX_HTML = ROOT / "static" / "index.html"
JS_DIR = ROOT / "static" / "js"
MODULES_DIR = ROOT / "modules"
SERVER_PY = ROOT / "server.py"

def audit_html_buttons():
    content = INDEX_HTML.read_text(encoding="utf-8")
    button_regex = re.compile(r'<button\b([^>]*)>(.*?)</button>', re.DOTALL | re.IGNORECASE)
    buttons = []
    for match in button_regex.finditer(content):
        attrs_str = match.group(1)
        inner_html = match.group(2).strip()
        line_num = content[:match.start()].count('\n') + 1
        
        # Extract id, class, onclick, data-tab, etc.
        id_match = re.search(r'id=["\']([^"\']+)["\']', attrs_str)
        onclick_match = re.search(r'onclick=["\']([^"\']+)["\']', attrs_str)
        class_match = re.search(r'class=["\']([^"\']+)["\']', attrs_str)
        data_tab_match = re.search(r'data-tab=["\']([^"\']+)["\']', attrs_str)
        
        buttons.append({
            "line": line_num,
            "id": id_match.group(1) if id_match else None,
            "onclick": onclick_match.group(1) if onclick_match else None,
            "class": class_match.group(1) if class_match else None,
            "data_tab": data_tab_match.group(1) if data_tab_match else None,
            "text": re.sub(r'<[^>]+>', '', inner_html).strip()[:40],
            "raw_attrs": attrs_str.strip()
        })
    return buttons

def audit_js_event_listeners():
    js_files = list(JS_DIR.glob("*.js"))
    listeners = {}
    fetch_calls = {}
    
    for js_file in js_files:
        text = js_file.read_text(encoding="utf-8")
        fname = js_file.name
        
        # 1. document.getElementById('...').addEventListener('click'...) or $ / onclick
        ev_matches = re.findall(r'(?:getElementById\([\'"]([^\'"]+)[\'"]\)|querySelector\([\'"]#([^\'"]+)[\'"]\))\s*\.\s*addEventListener\(\s*[\'"]click[\'"]', text)
        
        # Also direct onclick assignments
        onclick_assigns = re.findall(r'getElementById\([\'"]([^\'"]+)[\'"]\)\s*\.\s*onclick\s*=', text)
        
        # Also delegated or dynamic matches
        all_ids = []
        for m in ev_matches:
            btn_id = m[0] or m[1]
            if btn_id:
                all_ids.append(btn_id)
        all_ids.extend(onclick_assigns)
        
        listeners[fname] = list(set(all_ids))
        
        # 2. fetch('/api/...')
        fetches = re.findall(r'fetch\([\'"`]([^\'"`$]+)[\'"`]', text)
        fetch_calls[fname] = list(set(fetches))
        
    return listeners, fetch_calls

def audit_backend_routes():
    routes = []
    # Check server.py and all *_router.py in modules/
    router_files = [SERVER_PY] + list(MODULES_DIR.glob("**/*_router.py")) + list(MODULES_DIR.glob("**/*_service.py"))
    
    for rf in router_files:
        if not rf.exists():
            continue
        text = rf.read_text(encoding="utf-8")
        matches = re.findall(r'@\w+\.(?:get|post|put|delete|patch)\([\'"]([^\'"]+)[\'"]', text)
        for m in matches:
            routes.append({
                "file": rf.relative_to(ROOT).as_posix(),
                "route": m
            })
    return routes

if __name__ == "__main__":
    buttons = audit_html_buttons()
    listeners, fetch_calls = audit_js_event_listeners()
    routes = audit_backend_routes()
    
    all_listener_ids = set()
    for f, id_list in listeners.items():
        all_listener_ids.update(id_list)
        
    all_backend_routes = {r["route"] for r in routes}
    
    unhandled_buttons = []
    handled_buttons = []
    
    for b in buttons:
        btn_id = b["id"]
        onclick = b["onclick"]
        is_handled = False
        handlers = []
        
        if onclick:
            is_handled = True
            handlers.append(f"inline onclick: {onclick}")
        if btn_id and btn_id in all_listener_ids:
            is_handled = True
            # Find which js file
            for js_f, ids in listeners.items():
                if btn_id in ids:
                    handlers.append(f"JS listener in {js_f}")
                    
        b["handlers"] = handlers
        if is_handled:
            handled_buttons.append(b)
        else:
            unhandled_buttons.append(b)
            
    # Check JS fetch calls against backend routes
    dead_fetches = {}
    for js_f, f_list in fetch_calls.items():
        dead = []
        for url in f_list:
            if not url.startswith("/api/"):
                continue
            # Check prefix or exact match
            matched = any(url == br or url.startswith(br + "/") or (br.endswith("}") and url.split("?")[0].startswith(br.split("{")[0])) for br in all_backend_routes)
            if not matched:
                dead.append(url)
        if dead:
            dead_fetches[js_f] = dead
            
    report = {
        "total_buttons_in_html": len(buttons),
        "handled_buttons_count": len(handled_buttons),
        "unhandled_buttons_count": len(unhandled_buttons),
        "unhandled_buttons": unhandled_buttons,
        "total_backend_routes": len(all_backend_routes),
        "dead_fetch_calls": dead_fetches,
        "listeners_by_file": listeners,
        "routes_by_file": routes
    }
    
    out_file = ROOT / ".agents" / "explorer_survey_3" / "ui_audit_result.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
        
    print(f"Total HTML Buttons: {len(buttons)}")
    print(f"Handled: {len(handled_buttons)}")
    print(f"Unhandled/Potential dead buttons: {len(unhandled_buttons)}")
    print(f"Dead fetch calls in JS: {len(dead_fetches)}")
    for f, d in dead_fetches.items():
        print(f"  {f}: {d}")
    print(f"Report saved to {out_file}")
