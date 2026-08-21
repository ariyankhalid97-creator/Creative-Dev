#!/usr/bin/env python3
"""
Lex HQ — Control Center backend.

Pure standard library (no pip installs). Serves the dashboard and a small JSON API
over the file-based state. The filesystem IS the database: tasks, approvals, and
activity are JSON files that both this server and the agents read/write directly.

Run:   python server.py            (opens http://localhost:8787)
       python server.py 9000       (custom port)
       python server.py --no-open  (don't auto-open the browser)
"""
import json, os, sys, time, uuid, glob, webbrowser, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

ROOT      = os.path.dirname(os.path.abspath(__file__))
WEB       = os.path.join(ROOT, "web")
TASKS     = os.path.join(ROOT, "tasks")
APPROVALS = os.path.join(ROOT, "approvals")
ACTIVITY  = os.path.join(ROOT, "activity")
STATE     = os.path.join(ROOT, "state")
for d in (WEB, TASKS, APPROVALS, ACTIVITY, STATE):
    os.makedirs(d, exist_ok=True)


# ---------- helpers ----------
def now_iso():
    return time.strftime("%Y-%m-%dT%H:%M:%S")

def new_id(prefix):
    return f"{prefix}-{time.strftime('%Y%m%d')}-{uuid.uuid4().hex[:4]}"

def read_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def write_json(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)

def load_dir(path):
    out = []
    for p in glob.glob(os.path.join(path, "*.json")):
        obj = read_json(p)
        if obj is not None:
            obj["_file"] = os.path.basename(p)
            out.append(obj)
    return out

def task_path(tid):     return os.path.join(TASKS, f"{tid}.json")
def approval_path(aid): return os.path.join(APPROVALS, f"{aid}.json")

def log_activity(agent, type_, text, task_id=None):
    ev = {"id": new_id("e"), "at": now_iso(), "agent": agent,
          "type": type_, "text": text}
    if task_id:
        ev["taskId"] = task_id
    fname = f"{time.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:4]}-{agent}.json"
    write_json(os.path.join(ACTIVITY, fname), ev)
    return ev


# ---------- state assembly ----------
STATUS_ORDER = {"blocked": 0, "running": 1, "queued": 2, "inbox": 3, "failed": 4, "done": 5}

def get_state():
    tasks = load_dir(TASKS)
    approvals = load_dir(APPROVALS)
    activity = sorted(load_dir(ACTIVITY), key=lambda e: e.get("at", ""), reverse=True)[:60]
    tasks.sort(key=lambda t: (STATUS_ORDER.get(t.get("status"), 9),
                              t.get("updatedAt") or t.get("createdAt") or ""), )
    tasks.sort(key=lambda t: (STATUS_ORDER.get(t.get("status"), 9), ))
    approvals.sort(key=lambda a: (0 if a.get("status") == "pending" else 1,
                                  a.get("createdAt", "")), reverse=False)
    agents = read_json(os.path.join(STATE, "agents.json")) or {"agents": []}
    counts = {
        "pendingApprovals": sum(1 for a in approvals if a.get("status") == "pending"),
        "openTasks": sum(1 for t in tasks if t.get("status") in ("inbox", "queued", "running", "blocked")),
        "blocked": sum(1 for t in tasks if t.get("status") == "blocked"),
    }
    return {"meta": {"now": now_iso(), "counts": counts},
            "agents": agents.get("agents", []),
            "tasks": tasks, "approvals": approvals, "activity": activity}


# ---------- mutations ----------
def create_task(body):
    tid = new_id("t")
    t = {
        "id": tid,
        "title": body.get("title", "Untitled task").strip() or "Untitled task",
        "detail": body.get("detail", "").strip(),
        "project": body.get("project") or None,
        "assignee": body.get("assignee") or "auto",
        "priority": body.get("priority") or "normal",
        "status": "queued" if body.get("start") else "inbox",
        "createdAt": now_iso(), "updatedAt": now_iso(),
        "updates": [], "result": "",
    }
    write_json(task_path(tid), t)
    log_activity("you", "task",
                 f'New task: "{t["title"]}" → {t["assignee"]}'
                 + (" (started)" if body.get("start") else ""), tid)
    return t

def update_task(tid, body):
    t = read_json(task_path(tid))
    if not t:
        return None
    action = body.get("action")
    note = (body.get("note") or "").strip()
    if action == "start":
        t["status"] = "queued"
    elif action == "cancel":
        t["status"] = "failed"
    elif action == "complete":
        t["status"] = "done"
    elif action == "requeue":
        t["status"] = "queued"
    if note or action:
        t.setdefault("updates", []).append(
            {"at": now_iso(), "by": "you", "text": note or f"action: {action}"})
    t["updatedAt"] = now_iso()
    write_json(task_path(tid), t)
    log_activity("you", "task", f'{action or "note"} on "{t["title"]}"'
                 + (f' — {note}' if note else ""), tid)
    return t

def decide_approval(aid, body):
    a = read_json(approval_path(aid))
    if not a:
        return None
    decision = body.get("decision")           # "approve" | "reject"
    note = (body.get("note") or "").strip()
    a["status"] = "approved" if decision == "approve" else "rejected"
    a["decidedAt"] = now_iso()
    a["decidedNote"] = note
    write_json(approval_path(aid), a)
    # nudge the linked task
    tid = a.get("taskId")
    if tid:
        t = read_json(task_path(tid))
        if t:
            t.setdefault("updates", []).append(
                {"at": now_iso(), "by": "you",
                 "text": f'{a["status"].upper()} approval "{a.get("title","")}"'
                         + (f' — {note}' if note else "")})
            t["status"] = "queued" if decision == "approve" else "blocked"
            t["updatedAt"] = now_iso()
            write_json(task_path(tid), t)
    log_activity("you", "approval",
                 f'{a["status"].upper()}: {a.get("title","(untitled)")}', tid)
    return a


# ---------- HTTP ----------
class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        data = body if isinstance(body, (bytes, bytearray)) else json.dumps(body).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _body(self):
        n = int(self.headers.get("Content-Length") or 0)
        if not n:
            return {}
        try:
            return json.loads(self.rfile.read(n).decode("utf-8"))
        except Exception:
            return {}

    def log_message(self, *a):   # quieter console
        pass

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/state":
            return self._send(200, get_state())
        if path in ("/", "/index.html"):
            return self._file(os.path.join(WEB, "index.html"), "text/html; charset=utf-8")
        if path.startswith("/web/"):
            return self._file(os.path.join(WEB, os.path.basename(path)),
                              self._ctype(path))
        return self._send(404, {"error": "not found"})

    def do_POST(self):
        path = urlparse(self.path).path
        body = self._body()
        if path == "/api/tasks":
            return self._send(200, create_task(body))
        if path.startswith("/api/task/"):
            r = update_task(path.rsplit("/", 1)[-1], body)
            return self._send(200 if r else 404, r or {"error": "no task"})
        if path.startswith("/api/approval/"):
            r = decide_approval(path.rsplit("/", 1)[-1], body)
            return self._send(200 if r else 404, r or {"error": "no approval"})
        if path == "/api/activity":
            return self._send(200, log_activity(body.get("agent", "lex"),
                              body.get("type", "info"), body.get("text", ""),
                              body.get("taskId")))
        return self._send(404, {"error": "not found"})

    def _file(self, p, ctype):
        try:
            with open(p, "rb") as f:
                return self._send(200, f.read(), ctype)
        except FileNotFoundError:
            return self._send(404, b"not found", "text/plain")

    @staticmethod
    def _ctype(path):
        if path.endswith(".css"):  return "text/css"
        if path.endswith(".js"):   return "application/javascript"
        if path.endswith(".html"): return "text/html; charset=utf-8"
        return "application/octet-stream"


def main():
    args = [a for a in sys.argv[1:]]
    no_open = "--no-open" in args
    ports = [a for a in args if a.isdigit()]
    port = int(ports[0]) if ports else 8787
    httpd = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    url = f"http://localhost:{port}"
    print(f"\n  Lex HQ — Control Center running at  {url}")
    print(f"  Serving state from: {ROOT}")
    print("  Ctrl+C to stop.\n")
    if not no_open:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n  Stopped.")


if __name__ == "__main__":
    main()
