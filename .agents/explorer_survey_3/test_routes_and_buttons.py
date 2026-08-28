# test_routes_and_buttons.py
import re
import sys
import json
from pathlib import Path

ROOT = Path("H:/My Drive/Ho so ca nhan/b. ThS KHMT/Skill/Web Super")
sys.path.insert(0, str(ROOT))
from server import app

JS_DIR = ROOT / "static" / "js"
INDEX_HTML = ROOT / "static" / "index.html"

def get_registered_routes():
    routes = []
    for route in app.routes:
        if hasattr(route, "path") and hasattr(route, "methods"):
            routes.append({
                "path": route.path,
                "methods": list(route.methods) if route.methods else []
            })
    return routes

def get_js_fetch_calls():
    js_files = list(JS_DIR.glob("*.js"))
    fetch_map = {}
    for jf in js_files:
        content = jf.read_text(encoding="utf-8")
        # Match fetch('/...', ` /api/...`, etc.
        calls = re.findall(r'fetch\(\s*[\'"](/api/[^\'"]+)[\'"]', content)
        # Also match template literals fetch(`/api/...`)
        template_calls = re.findall(r'fetch\(\s*`(/api/[^`$?]+)', content)
        all_calls = set(calls + template_calls)
        fetch_map[jf.name] = sorted(list(all_calls))
    return fetch_map

if __name__ == "__main__":
    registered_routes = get_registered_routes()
    route_paths = {r["path"] for r in registered_routes}
    js_fetches = get_js_fetch_calls()
    
    print(f"Total FastAPI registered routes: {len(registered_routes)}")
    
    missing_routes = {}
    for js_name, urls in js_fetches.items():
        missing = []
        for url in urls:
            if not url.startswith("/api/"):
                continue
            # Strip query params
            clean_url = url.split("?")[0]
            # Match against registered paths (including path params like {file_path:path} or {id})
            matched = False
            for rp in route_paths:
                if clean_url == rp:
                    matched = True
                    break
                # Handle path params {param} or {param:path}
                rp_regex = "^" + re.sub(r'\{[^}]+\}', r'.+', rp) + "$"
                if re.match(rp_regex, clean_url):
                    matched = True
                    break
            if not matched:
                missing.append(url)
        if missing:
            missing_routes[js_name] = missing
            
    print("\n--- API ROUTE CHECK RESULTS ---")
    if not missing_routes:
        print("✅ 100% of frontend fetch calls match registered backend routes!")
    else:
        print(f"⚠️ Found missing/unmatched routes in {len(missing_routes)} JS files:")
        for js_f, m_urls in missing_routes.items():
            print(f"  [{js_f}]: {m_urls}")
            
    # Check all button IDs in index.html and verify if they have event listeners
    html_text = INDEX_HTML.read_text(encoding="utf-8")
    btn_matches = re.finditer(r'<button\b([^>]*)>(.*?)</button>', html_text, re.DOTALL | re.IGNORECASE)
    
    all_js_text = "\n".join([f.read_text(encoding="utf-8") for f in JS_DIR.glob("*.js")])
    
    unbound_buttons = []
    bound_buttons = []
    
    for bm in btn_matches:
        attrs = bm.group(1)
        inner = re.sub(r'<[^>]+>', '', bm.group(2)).strip()[:30]
        line = html_text[:bm.start()].count('\n') + 1
        
        id_m = re.search(r'id=["\']([^"\']+)["\']', attrs)
        onclick_m = re.search(r'onclick=["\']([^"\']+)["\']', attrs)
        class_m = re.search(r'class=["\']([^"\']+)["\']', attrs)
        
        btn_id = id_m.group(1) if id_m else None
        onclick = onclick_m.group(1) if onclick_m else None
        btn_cls = class_m.group(1) if class_m else ""
        
        is_bound = False
        reason = []
        if onclick:
            is_bound = True
            reason.append(f"onclick: {onclick}")
        if btn_id:
            if f"'{btn_id}'" in all_js_text or f'"{btn_id}"' in all_js_text or f'`{btn_id}`' in all_js_text:
                is_bound = True
                reason.append(f"id referenced in JS: {btn_id}")
        if "modal-close" in btn_cls or "btn-close" in btn_cls:
            is_bound = True
            reason.append("modal-close class handled by general modal dismissal")
            
        if is_bound:
            bound_buttons.append({"line": line, "id": btn_id, "text": inner, "reasons": reason})
        else:
            unbound_buttons.append({"line": line, "id": btn_id, "text": inner, "attrs": attrs})
            
    print(f"\n--- BUTTON AUDIT RESULTS ---")
    print(f"Total buttons: {len(bound_buttons) + len(unbound_buttons)}")
    print(f"Bound / Active buttons: {len(bound_buttons)}")
    print(f"Unbound / Dead buttons: {len(unbound_buttons)}")
    if unbound_buttons:
        for ub in unbound_buttons:
            print(f"  Line {ub['line']} | ID: {ub['id']} | Text: '{ub['text']}'")
