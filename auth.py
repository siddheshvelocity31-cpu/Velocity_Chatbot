"""
Authentication module for Velocity Chatbot.

Handles user signup / login / lookup.
- Primary storage: Supabase 'users' table (if configured, same as chat history).
- Fallback storage: local JSON file (users/users.json), mirroring the
  local-fallback pattern already used for chat_history in app.py.

Passwords are NEVER stored in plain text - they're hashed with
werkzeug.security (already a Flask dependency, no new package needed).
"""

from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import json
import re
import uuid

from werkzeug.security import generate_password_hash, check_password_hash

import config
import supabase_db

# ============================================================
# LOCAL FALLBACK STORAGE
# ============================================================

USERS_DIR = Path(__file__).resolve().parent / "users"
USERS_DIR.mkdir(exist_ok=True)
USERS_FILE = USERS_DIR / "users.json"


def _load_local_users() -> Dict[str, Any]:
    if not USERS_FILE.exists():
        return {}
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return {}


def _save_local_users(users: Dict[str, Any]) -> None:
    with open(USERS_FILE, "w", encoding="utf-8") as file:
        json.dump(users, file, indent=2, ensure_ascii=False)


# ============================================================
# VALIDATION HELPERS
# ============================================================

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_signup(email: str, password: str, confirm_password: str) -> Optional[str]:
    """Return an error message string, or None if valid."""
    email = (email or "").strip().lower()
    if not email or not EMAIL_RE.match(email):
        return "Please enter a valid email address."
    if not password or len(password) < 6:
        return "Password must be at least 6 characters."
    if password != confirm_password:
        return "Passwords do not match."
    return None


# ============================================================
# SUPABASE-BACKED OPERATIONS
# ============================================================

def _get_client():
    if supabase_db.is_supabase_configured(config.SUPABASE_URL, config.SUPABASE_KEY):
        return supabase_db.get_supabase_client(config.SUPABASE_URL, config.SUPABASE_KEY)
    return None


def create_user(email: str, password: str, name: str = "") -> Dict[str, Any]:
    """
    Create a new user. Tries Supabase first, falls back to local JSON.
    Returns {"success": True, "user": {...}} or {"success": False, "error": "..."}
    """
    email = email.strip().lower()
    password_hash = generate_password_hash(password)
    user_id = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat()

    client = _get_client()
    if client:
        try:
            existing = client.table("users").select("id").eq("email", email).limit(1).execute()
            if existing.data:
                return {"success": False, "error": "An account with this email already exists."}

            client.table("users").insert({
                "id": user_id,
                "email": email,
                "name": name or email.split("@")[0],
                "password_hash": password_hash,
                "created_at": created_at,
            }).execute()

            return {"success": True, "user": {"id": user_id, "email": email, "name": name or email.split("@")[0]}}
        except Exception as error:
            print("Supabase signup error:", error)
            # fall through to local fallback below

    # Local fallback
    users = _load_local_users()
    if email in users:
        return {"success": False, "error": "An account with this email already exists."}

    users[email] = {
        "id": user_id,
        "email": email,
        "name": name or email.split("@")[0],
        "password_hash": password_hash,
        "created_at": created_at,
    }
    _save_local_users(users)
    return {"success": True, "user": {"id": user_id, "email": email, "name": name or email.split("@")[0]}}


def verify_login(email: str, password: str) -> Dict[str, Any]:
    """
    Check credentials. Returns {"success": True, "user": {...}} or
    {"success": False, "error": "..."}
    """
    email = (email or "").strip().lower()

    client = _get_client()
    if client:
        try:
            resp = client.table("users").select("*").eq("email", email).limit(1).execute()
            if resp.data:
                record = resp.data[0]
                if check_password_hash(record["password_hash"], password):
                    return {
                        "success": True,
                        "user": {"id": record["id"], "email": record["email"], "name": record.get("name", email)},
                    }
                return {"success": False, "error": "Incorrect email or password."}
        except Exception as error:
            print("Supabase login error:", error)
            # fall through to local fallback below

    # Local fallback
    users = _load_local_users()
    record = users.get(email)
    if not record or not check_password_hash(record["password_hash"], password):
        return {"success": False, "error": "Incorrect email or password."}

    return {
        "success": True,
        "user": {"id": record["id"], "email": record["email"], "name": record.get("name", email)},
    }
