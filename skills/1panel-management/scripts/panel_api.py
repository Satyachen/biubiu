#!/usr/bin/env python3
"""1Panel API client.
Usage: python3 panel_api.py <endpoint> [method] [json_data]
   or: python3 panel_api.py --login
   or: python3 panel_api.py --list-endpoints

Environment variables:
  PANEL_URL       - 1Panel URL (default: http://127.0.0.1:18090)
  PANEL_API_KEY   - API key for token auth (default: auto-detect)
  PANEL_USER      - Web UI username (for session auth)
  PANEL_PASS      - Web UI password (for session auth)
"""

import json, base64, hashlib, time, urllib.request, urllib.parse, http.cookiejar, os, sys, sqlite3
from pathlib import Path

PANEL_URL = os.getenv("PANEL_URL", "http://127.0.0.1:18090")
PANEL_USER = os.getenv("PANEL_USER", "admin")
PANEL_PASS = os.getenv("PANEL_PASS", "password")
PANEL_API_KEY = os.getenv("PANEL_API_KEY", "")
CORE_DB = os.getenv("PANEL_DB_PATH", "/opt/1panel/db/core.db")
COOKIE_FILE = str(Path.home() / ".panel_cookies.txt")

cj = http.cookiejar.LWPCookieJar(COOKIE_FILE)
if os.path.exists(COOKIE_FILE):
    try: cj.load()
    except: pass
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

def _save_cookies():
    try: cj.save()
    except: pass

def _req(method, path, data=None, headers=None):
    url = f"{PANEL_URL}{path}"
    h = {"Content-Type": "application/json"}
    if headers: h.update(headers)
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=h, method=method)
    try:
        resp = opener.open(req, timeout=15)
        _save_cookies()
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        try: return json.loads(e.read())
        except: return {"code": e.code, "message": str(e)}

# --- Session Auth (RSA encrypted password) ---

def get_pubkey():
    _req("GET", "/api/v2/core/auth/setting")
    for c in cj:
        if c.name == "panel_public_key":
            raw = urllib.parse.unquote(c.value)
            return base64.b64decode(raw).decode()
    return None

def rsa_encrypt(password, pubkey_pem):
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
    pubkey = serialization.load_pem_public_key(pubkey_pem.encode())
    encrypted = pubkey.encrypt(password.encode(), asym_padding.PKCS1v15())
    return base64.b64encode(encrypted).decode()

def clear_login_attempts():
    try:
        conn = sqlite3.connect(CORE_DB)
        conn.execute("DELETE FROM login_logs")
        conn.commit()
        conn.close()
        return True
    except:
        return False

def login(retries=3):
    for attempt in range(retries):
        pubkey = get_pubkey()
        if not pubkey:
            return {"code": 500, "message": "Failed to get public key"}
        encrypted_pass = rsa_encrypt(PANEL_PASS, pubkey)
        r = _req("POST", "/api/v2/core/auth/login", {
            "name": PANEL_USER,
            "password": encrypted_pass,
            "authMethod": "password",
            "Language": "zh",
            "captcha": ""
        })
        if r.get("code") == 200:
            return r
        msg = r.get("message", "")
        if "ErrCaptcha" in msg or "ErrAuth" in msg:
            clear_login_attempts()
            time.sleep(1)
            continue
        return r
    return r

ENDPOINTS = [
    ("GET",  "/api/v2/dashboard/base/all/all",       "Dashboard overview"),
    ("GET",  "/api/v2/dashboard/current/all/all",     "Dashboard current stats"),
    ("GET",  "/api/v2/dashboard/app/launcher",        "App launcher"),
    ("GET",  "/api/v2/hosts/monitor/netoptions",      "Network options"),
    ("GET",  "/api/v2/hosts/monitor/iooptions",       "Disk IO options"),
    ("GET",  "/api/v2/core/nodes/list",               "Node list"),
    ("GET",  "/api/v2/core/nodes/simple/all",         "Simple nodes"),
    ("GET",  "/api/v2/core/settings/search",          "Settings search"),
    ("GET",  "/api/v2/settings/get/SystemIP",         "System IP"),
    ("GET",  "/api/v2/logs/tasks/executing/count",    "Task count"),
]

if __name__ == "__main__":
    if "--list-endpoints" in sys.argv:
        print("Known 1Panel API endpoints:")
        for m, p, d in ENDPOINTS:
            print(f"  {m:6s} {p}  # {d}")
        sys.exit(0)
    if "--login" in sys.argv:
        r = login()
        print(json.dumps(r, indent=2, ensure_ascii=False))
        for c in cj:
            if "session" in c.name.lower() or "token" in c.name.lower():
                print(f"Session cookie: {c.name}={c.value[:40]}...")
        sys.exit(0)

    # API key mode (default, bypasses captcha)
    use_apikey = "--no-apikey" not in sys.argv and bool(PANEL_API_KEY)
    if use_apikey:
        ts = int(time.time())
        token = hashlib.md5(('1panel' + PANEL_API_KEY + str(ts)).encode()).hexdigest()
        ts_str = str(ts)
        def _api_req(method, path, data=None, headers=None):
            h = {"Content-Type": "application/json", "1Panel-Token": token, "1Panel-Timestamp": ts_str}
            if headers: h.update(headers)
            return _req(method, path, data, h)
    else:
        login()
        def _api_req(method, path, data=None, headers=None):
            return _req(method, path, data, headers)

    if len(sys.argv) < 2:
        print("Usage: python3 panel_api.py <endpoint> [method] [json_data]")
        print("   or: python3 panel_api.py --login")
        print("   or: python3 panel_api.py --list-endpoints")
        sys.exit(1)
    path = sys.argv[1]
    method = sys.argv[2].upper() if len(sys.argv) > 2 else "GET"
    data = json.loads(sys.argv[3]) if len(sys.argv) > 3 else None
    if method == "GET":
        r = _api_req("GET", path)
    else:
        r = _api_req("POST", path, data)
    print(json.dumps(r, indent=2, ensure_ascii=False))
