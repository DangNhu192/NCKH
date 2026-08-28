# comprehensive_route_audit.py
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path("H:/My Drive/Ho so ca nhan/b. ThS KHMT/Skill/Web Super")
MODULES_DIR = ROOT / "modules"
JS_DIR = ROOT / "static" / "js"

def audit_all_routers():
    router_files = sorted(list(MODULES_DIR.glob("**/*_router.py")) + [ROOT / "server.py"])
    all_routes = []
    
    for rf in router_files:
        text = rf.read_text(encoding="utf-8")
        matches = re.finditer(r'@(?:\w+)\.(get|post|put|delete|patch)\(\s*[\'"]([^\'"]+)[\'"]', text)
        for m in matches:
            method = m.group(1).upper()
            route_path = m.group(2)
            after = text[m.end():m.end()+200]
            fn_m = re.search(r'(?:async\s+)?def\s+([a-zA-Z0-9_]+)\(', after)
            fn_name = fn_m.group(1) if fn_m else "unknown"
            all_routes.append({
                "file": rf.relative_to(ROOT).as_posix(),
                "method": method,
                "path": route_path,
                "func": fn_name
            })
    return all_routes

def audit_js_endpoints():
    js_files = sorted(list(JS_DIR.glob("*.js")))
    endpoint_calls = []
    for jf in js_files:
        text = jf.read_text(encoding="utf-8")
        fetches = re.finditer(r'fetch\(\s*[`\'"](/api/[^`\'"?]+)(?:\?[^`\'"]*)?[`\'"]', text)
        for f in fetches:
            raw_url = f.group(1)
            line = text[:f.start()].count('\n') + 1
            endpoint_calls.append({
                "file": jf.name,
                "line": line,
                "endpoint": raw_url
            })
    return endpoint_calls

if __name__ == "__main__":
    routes = audit_all_routers()
    js_endpoints = audit_js_endpoints()
    
    print(f"Total Backend Routes Found: {len(routes)}")
    print(f"Total Frontend API Calls: {len(js_endpoints)}")
    
    backend_paths = {r["path"] for r in routes}
    
    print("\n--- FRONTEND API CALLS VERIFICATION ---")
    missing_calls = []
    for jc in js_endpoints:
        ep = jc["endpoint"]
        matched = False
        for bp in backend_paths:
            if ep == bp:
                matched = True
                break
            bp_regex = "^" + re.sub(r'\{[^}]+\}', r'[^/]+', bp) + "$"
            if re.match(bp_regex, ep):
                matched = True
                break
        if not matched:
            missing_calls.append(jc)
            
    if not missing_calls:
        print("[PASS] ALL frontend API calls have corresponding backend routes!")
    else:
        print(f"[WARN] Found {len(missing_calls)} unmatched frontend API calls:")
        for mc in missing_calls:
            print(f"  {mc['file']}:{mc['line']} -> {mc['endpoint']}")
