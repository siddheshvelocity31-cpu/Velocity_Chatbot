"""Supabase database client for persisting Gemini Chatbot conversation history."""

from typing import List, Dict, Any, Optional
from datetime import datetime
import json

try:
    from supabase import create_client, Client
    HAS_SUPABASE_PKG = True
except ImportError:
    HAS_SUPABASE_PKG = False
    Client = Any

import config


def is_supabase_configured(url: Optional[str] = None, key: Optional[str] = None) -> bool:
    """Check if valid Supabase credentials exist."""
    u = (url or config.SUPABASE_URL or "").strip()
    k = (key or config.SUPABASE_KEY or "").strip()
    return bool(
        HAS_SUPABASE_PKG
        and u
        and k
        and u.startswith("http")
        and not u.endswith("your-project-id.supabase.co")
        and k != "your_supabase_anon_public_key_here"
        and len(k) > 15
    )


def get_supabase_client(url: Optional[str] = None, key: Optional[str] = None) -> Optional[Client]:
    """Create and return a Supabase Client instance if credentials are valid."""
    if not HAS_SUPABASE_PKG:
        return None

    u = (url or config.SUPABASE_URL or "").strip()
    k = (key or config.SUPABASE_KEY or "").strip()

    if not is_supabase_configured(u, k):
        return None

    try:
        return create_client(u, k)
    except Exception:
        return None


def test_supabase_connection(url: Optional[str] = None, key: Optional[str] = None) -> Dict[str, Any]:
    """Test connection to Supabase and verify required tables exist."""
    if not HAS_SUPABASE_PKG:
        return {
            "success": False,
            "error": "The 'supabase' Python package is not installed. Please run `pip install supabase`."
        }

    u = (url or config.SUPABASE_URL or "").strip()
    k = (key or config.SUPABASE_KEY or "").strip()

    if not is_supabase_configured(u, k):
        return {
            "success": False,
            "error": "Supabase URL or Key is missing or invalid. Please configure them in .env or the sidebar."
        }

    try:
        client = create_client(u, k)
        # Check if chat_sessions table is reachable
        resp = client.table("chat_sessions").select("id").limit(1).execute()
        return {
            "success": True,
            "message": "Successfully connected to Supabase database! 'chat_sessions' table verified."
        }
    except Exception as e:
        err_msg = str(e)
        if "relation \"public.chat_sessions\" does not exist" in err_msg or "PGRST204" in err_msg or "not found" in err_msg.lower():
            return {
                "success": False,
                "error": "Connected to Supabase, but the 'chat_sessions' table does not exist yet!\n\n"
                         "👉 **Action Required:** Open Supabase SQL Editor and run the queries in `supabase_schema.sql`."
            }
        return {
            "success": False,
            "error": f"Connection failed: {err_msg}"
        }


def save_chat_session(
    session_id: str,
    messages: List[Dict[str, Any]],
    url: Optional[str] = None,
    key: Optional[str] = None
) -> Dict[str, Any]:
    """Upsert a conversation session and all its messages into Supabase.

    Args:
        session_id: The unique identifier for the conversation session.
        messages: List of message dictionaries with 'role', 'content', 'timestamp', and optional 'tools'.
        url: Optional Supabase URL override.
        key: Optional Supabase API key override.

    Returns:
        A dict with status success or failure details.
    """
    client = get_supabase_client(url, key)
    if not client or not messages:
        return {"success": False, "reason": "client_not_configured_or_no_messages"}

    try:
        # Determine title from the first user query
        first_user_msg = ""
        for m in messages:
            if m.get("role") == "user":
                first_user_msg = m.get("content", "").strip()
                break

        title = (first_user_msg[:45] + "...") if len(first_user_msg) > 45 else (first_user_msg or "Conversation")
        created_at_val = messages[0].get("timestamp") or datetime.utcnow().isoformat()

        # 1. Upsert session metadata into chat_sessions
        session_payload = {
            "session_id": session_id,
            "title": title,
            "updated_at": datetime.utcnow().isoformat(),
            "message_count": len(messages)
        }
        client.table("chat_sessions").upsert(session_payload, on_conflict="session_id").execute()

        # 2. Re-sync messages: Delete previous turns for this session and insert fresh batch
        client.table("chat_messages").delete().eq("session_id", session_id).execute()

        message_rows = []
        for msg in messages:
            message_rows.append({
                "session_id": session_id,
                "role": msg.get("role", "user"),
                "content": msg.get("content", ""),
                "tools": msg.get("tools") or [],
                "timestamp": msg.get("timestamp") or datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            })

        if message_rows:
            client.table("chat_messages").insert(message_rows).execute()

        return {"success": True, "session_id": session_id, "messages_saved": len(message_rows)}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_all_chat_sessions(url: Optional[str] = None, key: Optional[str] = None) -> List[Dict[str, Any]]:
    """Fetch all saved chat sessions ordered by newest updated first."""
    client = get_supabase_client(url, key)
    if not client:
        return []

    try:
        resp = client.table("chat_sessions").select("*").order("updated_at", desc=True).execute()
        return resp.data or []
    except Exception:
        return []


def get_chat_messages(session_id: str, url: Optional[str] = None, key: Optional[str] = None) -> List[Dict[str, Any]]:
    """Fetch all messages for a specific session ordered chronologically."""
    client = get_supabase_client(url, key)
    if not client:
        return []

    try:
        resp = (
            client.table("chat_messages")
            .select("role, content, tools, timestamp, created_at")
            .eq("session_id", session_id)
            .order("created_at", desc=False)
            .execute()
        )
        return resp.data or []
    except Exception:
        return []


def delete_chat_session(session_id: str, url: Optional[str] = None, key: Optional[str] = None) -> bool:
    """Delete a chat session and cascade-delete its messages."""
    client = get_supabase_client(url, key)
    if not client:
        return False

    try:
        client.table("chat_sessions").delete().eq("session_id", session_id).execute()
        return True
    except Exception:
        return False


def sync_user_login(email: str, name: str = "", picture: str = "", url: Optional[str] = None, key: Optional[str] = None) -> Dict[str, Any]:
    """Save or update logged-in Google user in Supabase user_logins table."""
    client = get_supabase_client(url, key)
    if not client or not email:
        return {"success": False, "reason": "client_not_configured_or_no_email"}

    try:
        user_payload = {
            "email": email.strip(),
            "name": name.strip(),
            "picture": picture.strip(),
            "last_login": datetime.utcnow().isoformat()
        }
        client.table("user_logins").upsert(user_payload, on_conflict="email").execute()
        return {"success": True, "email": email}
    except Exception as e:
        return {"success": False, "error": str(e)}

