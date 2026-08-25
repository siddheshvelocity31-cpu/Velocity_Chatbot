import os, uuid, json
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import traceback
from bot import GeminiChatbot, sanitize_key
import config, supabase_db

app = Flask(__name__)

class VercelFix(object):
    def __init__(self, app):
        self.app = app
    def __call__(self, environ, start_response):
        environ['SCRIPT_NAME'] = ''
        return self.app(environ, start_response)

app.wsgi_app = VercelFix(app.wsgi_app)
CORS(app)
app.secret_key = os.urandom(24)
ROOT_DIR = Path(__file__).resolve().parent
CHAT_HISTORY_DIR = ROOT_DIR / "chat_history"
try:
    CHAT_HISTORY_DIR.mkdir(exist_ok=True)
except Exception:
    pass # Vercel read-only filesystem fallback
_bots = {}

def _bot(sid, api_key="", model=""):
    k = api_key or config.GEMINI_API_KEY or ""
    m = model or config.GEMINI_MODEL or "gemini-3.5-flash"
    if sid not in _bots:
        _bots[sid] = GeminiChatbot(api_key=k, model=m)
    return _bots[sid]

def _save_local(msgs, sid):
    try:
        p = CHAT_HISTORY_DIR / (sid + ".json")
        p.write_text(json.dumps({"session_id": sid, "messages": msgs}, ensure_ascii=False, indent=2), encoding="utf-8")
    except: pass

def _local_sessions():
    out = []
    for f in sorted(CHAT_HISTORY_DIR.glob("chat_*.json"), reverse=True):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
            msgs = d.get("messages", [])
            title = next((m["content"][:50] for m in msgs if m["role"]=="user"), "New Chat")
            out.append({"session_id": d.get("session_id", f.stem), "title": title, "message_count": len(msgs), "filename": f.name})
        except: pass
    return out

@app.route("/")
def index():
    if "session_id" not in session:
        session["session_id"] = "chat_" + datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + uuid.uuid4().hex[:6]
    return render_template("index.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    d = request.get_json()
    msg = (d.get("message") or "").strip()
    sid = d.get("session_id") or session.get("session_id", "default")
    if not msg:
        return jsonify({"error": "Empty message"}), 400
    try:
        bot = _bot(sid, d.get("api_key", ""), d.get("model", ""))
        reply = bot.send_message(msg)
        tools = [t["tool"] for t in (bot.tool_call_history[-3:] if bot.tool_call_history else [])]
        return jsonify({"reply": reply, "tool_calls": tools, "session_id": sid})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/session/new", methods=["POST"])
def new_session():
    d = request.get_json() or {}
    old, msgs = d.get("session_id"), d.get("messages", [])
    surl, skey = d.get("supabase_url", ""), d.get("supabase_key", "")
    if old and msgs:
        _save_local(msgs, old)
        if supabase_db.is_supabase_configured(surl, skey):
            try:
                t = next((m["content"][:60] for m in msgs if m["role"]=="user"), "Chat")
                supabase_db.save_chat_session(surl, skey, old, t, msgs)
            except: pass
    nid = "chat_" + datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + uuid.uuid4().hex[:6]
    if old in _bots: del _bots[old]
    return jsonify({"session_id": nid})

@app.route("/api/history", methods=["POST"])
def history():
    d = request.get_json() or {}
    surl, skey = d.get("supabase_url", ""), d.get("supabase_key", "")
    if supabase_db.is_supabase_configured(surl, skey):
        try: return jsonify({"source": "supabase", "sessions": supabase_db.get_all_chat_sessions(surl, skey)})
        except: pass
    return jsonify({"source": "local", "sessions": _local_sessions()})

@app.route("/api/history/load", methods=["POST"])
def load_hist():
    d = request.get_json() or {}
    sid, surl, skey = d.get("session_id", ""), d.get("supabase_url", ""), d.get("supabase_key", "")
    if supabase_db.is_supabase_configured(surl, skey):
        try:
            msgs = supabase_db.get_chat_messages(surl, skey, sid)
            if msgs: return jsonify({"messages": msgs})
        except: pass
    p = CHAT_HISTORY_DIR / (sid + ".json")
    if p.exists():
        try: return jsonify({"messages": json.loads(p.read_text(encoding="utf-8")).get("messages", [])})
        except: pass
    return jsonify({"messages": []})

@app.route("/api/history/delete", methods=["POST"])
def del_hist():
    d = request.get_json() or {}
    sid, surl, skey = d.get("session_id", ""), d.get("supabase_url", ""), d.get("supabase_key", "")
    if supabase_db.is_supabase_configured(surl, skey):
        try: supabase_db.delete_chat_session(surl, skey, sid)
        except: pass
    p = CHAT_HISTORY_DIR / (sid + ".json")
    if p.exists(): p.unlink()
    return jsonify({"success": True})

@app.route("/api/history/save", methods=["POST"])
def save_hist():
    d = request.get_json() or {}
    sid, msgs = d.get("session_id", ""), d.get("messages", [])
    surl, skey = d.get("supabase_url", ""), d.get("supabase_key", "")
    _save_local(msgs, sid)
    if supabase_db.is_supabase_configured(surl, skey) and msgs:
        try:
            t = next((m["content"][:60] for m in msgs if m["role"]=="user"), "Chat")
            supabase_db.save_chat_session(surl, skey, sid, t, msgs)
        except: pass
    return jsonify({"success": True})

@app.route("/api/supabase/test", methods=["POST"])
def test_supa():
    d = request.get_json() or {}
    return jsonify(supabase_db.test_supabase_connection(d.get("supabase_url", ""), d.get("supabase_key", "")))

@app.route("/api/user/sync", methods=["POST"])
def sync_user():
    d = request.get_json() or {}
    email = d.get("email", "")
    name = d.get("name", "")
    picture = d.get("picture", "")
    surl = d.get("supabase_url", "")
    skey = d.get("supabase_key", "")
    res = supabase_db.sync_user_login(email, name, picture, surl, skey)
    return jsonify(res)

@app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
def catch_all(path):
    print(f"DEBUG: Catch-all triggered for path: {path}")
    return jsonify({"error": f"Path not found by Flask: {path}", "method": request.method, "headers": dict(request.headers)}), 404

@app.route("/api/models")
def models():
    return jsonify({"models": GeminiChatbot.SUPPORTED_MODELS})

@app.route("/api/tools")
def tools():
    from tools import TOOL_METADATA
    return jsonify({"tools": TOOL_METADATA})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    print(f"\n  Gemini AI Chatbot - Flask Web Server")
    print(f"  Listening on port {port}\n")
    app.run(debug=False, host="0.0.0.0", port=port)
