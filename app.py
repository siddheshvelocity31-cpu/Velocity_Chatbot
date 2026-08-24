"""Streamlit Web UI for the Google Gemini Tool-Calling Chatbot."""

import sys
from pathlib import Path

# Ensure project root is first in sys.path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import json
import re
import os
from datetime import datetime
import streamlit as st
import tools
import config
import bot
import supabase_db
from bot import GeminiChatbot


def sanitize_api_key(key: str) -> str:
    """Sanitize API key by stripping quotes, whitespace, and non-ASCII characters."""
    if not key:
        return ""
    cleaned = key.strip().strip("'\"`")
    return re.sub(r"[^\x20-\x7E]", "", cleaned).strip()


# ── Chat History Persistence (Supabase + Local JSON Fallback) ─────────────────
CHAT_HISTORY_DIR = Path(__file__).resolve().parent / "chat_history"
CHAT_HISTORY_DIR.mkdir(exist_ok=True)


def save_chat_to_file(messages: list, session_id: str) -> None:
    """Save current chat messages to a local JSON file."""
    if not messages:
        return
    filepath = CHAT_HISTORY_DIR / f"{session_id}.json"
    chat_data = {
        "session_id": session_id,
        "created_at": messages[0].get("timestamp", session_id.replace("chat_", "").replace("_", " ")),
        "message_count": len(messages),
        "messages": [
            {
                "role": msg["role"],
                "content": msg["content"],
                "tools": msg.get("tools") or [],
                "timestamp": msg.get("timestamp", ""),
            }
            for msg in messages
        ]
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(chat_data, f, indent=2, ensure_ascii=False)


def save_chat_history(messages: list, session_id: str, supabase_url: str = None, supabase_key: str = None) -> None:
    """Unified save: persists to Supabase (if configured) AND local JSON."""
    if not messages:
        return
    # 1. Always save local backup
    save_chat_to_file(messages, session_id)

    # 2. Save to Supabase Cloud Database if configured
    if supabase_db.is_supabase_configured(supabase_url, supabase_key):
        supabase_db.save_chat_session(session_id, messages, url=supabase_url, key=supabase_key)


def load_all_chats_unified(supabase_url: str = None, supabase_key: str = None) -> list:
    """Fetch all saved chat sessions from Supabase (or local disk if unconfigured)."""
    if supabase_db.is_supabase_configured(supabase_url, supabase_key):
        supa_sessions = supabase_db.get_all_chat_sessions(url=supabase_url, key=supabase_key)
        if supa_sessions:
            formatted = []
            for s in supa_sessions:
                formatted.append({
                    "session_id": s["session_id"],
                    "title": s.get("title") or "Conversation",
                    "created_at": s.get("created_at") or s.get("updated_at") or "",
                    "message_count": s.get("message_count", 0),
                    "source": "supabase",
                    "filename": f"{s['session_id']}.json"
                })
            return formatted

    # Fallback to local files
    local_chats = []
    for filepath in sorted(CHAT_HISTORY_DIR.glob("*.json"), reverse=True):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                first_msg = ""
                for m in data.get("messages", []):
                    if m.get("role") == "user":
                        first_msg = m.get("content", "")[:40] + ("..." if len(m.get("content", "")) > 40 else "")
                        break
                data["title"] = first_msg if first_msg else data.get("created_at", filepath.stem)
                data["filename"] = filepath.name
                data["source"] = "local"
                local_chats.append(data)
        except (json.JSONDecodeError, KeyError):
            continue
    return local_chats


def load_chat_messages_unified(session_id: str, filename: str, supabase_url: str = None, supabase_key: str = None) -> list:
    """Load messages for a specific session from Supabase or local JSON."""
    if supabase_db.is_supabase_configured(supabase_url, supabase_key):
        messages = supabase_db.get_chat_messages(session_id, url=supabase_url, key=supabase_key)
        if messages:
            return messages

    # Fallback to local file
    filepath = CHAT_HISTORY_DIR / filename
    if filepath.exists():
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("messages", [])
        except Exception:
            return []
    return []


def delete_chat_unified(session_id: str, filename: str, supabase_url: str = None, supabase_key: str = None) -> None:
    """Delete a chat from Supabase and local disk."""
    if supabase_db.is_supabase_configured(supabase_url, supabase_key):
        supabase_db.delete_chat_session(session_id, url=supabase_url, key=supabase_key)

    filepath = CHAT_HISTORY_DIR / filename
    if filepath.exists():
        filepath.unlink()



# Page setup
st.set_page_config(
    page_title="Gemini AI Assistant & Tool Engine",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern chat aesthetic
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E88E5;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #616161;
        margin-bottom: 20px;
    }
    .stChatMessage {
        border-radius: 12px;
        padding: 14px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = datetime.now().strftime("chat_%Y%m%d_%H%M%S")
if "api_key" not in st.session_state:
    st.session_state.api_key = config.GEMINI_API_KEY
if "model" not in st.session_state:
    st.session_state.model = "gemini-3.5-flash"
if "supabase_url" not in st.session_state:
    st.session_state.supabase_url = config.SUPABASE_URL
if "supabase_key" not in st.session_state:
    st.session_state.supabase_key = config.SUPABASE_KEY
if "tool_events" not in st.session_state:
    st.session_state.tool_events = []


# Sidebar Configuration
with st.sidebar:
    st.image("https://www.gstatic.com/lamda/images/gemini_sparkle_v002_d4735304ff6292a690345.svg", width=48)
    st.title("Gemini Assistant")

    # API Key Configuration
    api_key_input = st.text_input(
        "Gemini API Key",
        value=st.session_state.api_key if st.session_state.api_key != "your_gemini_api_key_here" else "",
        type="password",
        placeholder="AIzaSy...",
        help="Get a free key from https://aistudio.google.com/app/apikey"
    )

    cleaned_key = sanitize_api_key(api_key_input)
    if cleaned_key != st.session_state.api_key:
        st.session_state.api_key = cleaned_key
        st.session_state.chatbot = None  # Re-init bot with new key

    # Model Selection
    model_options = ["gemini-3.5-flash", "gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-3.7-flash"]
    current_index = model_options.index(st.session_state.model) if st.session_state.model in model_options else 0
    model_choice = st.selectbox(
        "Gemini Model",
        options=model_options,
        index=current_index,
        help="gemini-3.5-flash is ultra-fast with high free-tier quotas!"
    )
    if model_choice != st.session_state.model:
        st.session_state.model = model_choice
        st.session_state.chatbot = None

    # Test Connection Button
    if st.button("🧪 Test API Key Connection", use_container_width=True):
        test_bot = GeminiChatbot(api_key=st.session_state.api_key, model=st.session_state.model)
        with st.spinner("Testing connection to Google Gemini..."):
            result = test_bot.test_connection()
            if result["success"]:
                st.success(f"✅ {result.get('message', 'Connected to Gemini API!')}")
            else:
                st.error(f"❌ Connection Failed:\n{result.get('error')}")

    # Status Indicator
    is_live = bool(st.session_state.api_key and st.session_state.api_key != "your_gemini_api_key_here" and len(st.session_state.api_key) > 10)
    if is_live:
        st.caption(f"🟢 **AI Mode:** Live Gemini API ({st.session_state.model})")
    else:
        st.caption("🔵 **AI Mode:** Local Tool Engine (Offline)")

    # ── Supabase Database Configuration ───────────────────────────────────────
    with st.expander("🗄️ Database (Supabase Cloud)", expanded=False):
        st.caption("Store chat history permanently in Supabase PostgreSQL database.")
        supa_url_input = st.text_input(
            "Supabase URL",
            value=st.session_state.supabase_url if st.session_state.supabase_url != "https://your-project-id.supabase.co" else "",
            placeholder="https://xyzcompany.supabase.co",
            help="Found under Supabase Dashboard > Project Settings > API > Project URL"
        )
        supa_key_input = st.text_input(
            "Supabase Anon Key",
            value=st.session_state.supabase_key if st.session_state.supabase_key != "your_supabase_anon_public_key_here" else "",
            type="password",
            placeholder="eyJhbGciOiJIUzI1NiIsIn...",
            help="Found under Supabase Dashboard > Project Settings > API > Project API keys (anon / public)"
        )

        cleaned_supa_url = sanitize_api_key(supa_url_input)
        cleaned_supa_key = sanitize_api_key(supa_key_input)
        if cleaned_supa_url != st.session_state.supabase_url or cleaned_supa_key != st.session_state.supabase_key:
            st.session_state.supabase_url = cleaned_supa_url
            st.session_state.supabase_key = cleaned_supa_key

        if st.button("🧪 Test Supabase Connection", use_container_width=True):
            with st.spinner("Connecting to Supabase..."):
                test_res = supabase_db.test_supabase_connection(st.session_state.supabase_url, st.session_state.supabase_key)
                if test_res["success"]:
                    st.success(f"✅ {test_res.get('message')}")
                else:
                    st.error(f"❌ {test_res.get('error')}")

        st.caption("💡 *To create tables: Run `supabase_schema.sql` in your Supabase SQL Editor.*")

    # Storage Status Badge
    is_supa_live = supabase_db.is_supabase_configured(st.session_state.supabase_url, st.session_state.supabase_key)
    if is_supa_live:
        st.caption("🟢 **Storage:** Supabase Cloud Database")
    else:
        st.caption("🔵 **Storage:** Local JSON File Storage")

    st.divider()

    # Chat Controls
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        if st.button("➕ New Chat", use_container_width=True):
            if st.session_state.messages:
                save_chat_history(st.session_state.messages, st.session_state.session_id, st.session_state.supabase_url, st.session_state.supabase_key)
            st.session_state.messages = []
            st.session_state.session_id = datetime.now().strftime("chat_%Y%m%d_%H%M%S")
            if "chatbot" in st.session_state and st.session_state.chatbot:
                st.session_state.chatbot.reset_chat()
            st.rerun()
    with col_c2:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.messages = []
            if "chatbot" in st.session_state and st.session_state.chatbot:
                st.session_state.chatbot.reset_chat()
            st.rerun()

    # Saved Chat History Browser
    with st.expander("📜 Previous Chat History", expanded=False):
        saved_chats = load_all_chats_unified(st.session_state.supabase_url, st.session_state.supabase_key)
        if not saved_chats:
            st.caption("No saved conversations yet. Chat questions will be automatically saved here!")
        else:
            storage_label = "Supabase Cloud" if is_supa_live else "local storage"
            st.caption(f"📁 **{len(saved_chats)}** session(s) found in {storage_label}")
            for idx, chat_item in enumerate(saved_chats):
                title = chat_item.get("title") or chat_item.get("created_at") or f"Session #{idx+1}"
                badge = "☁️" if chat_item.get("source") == "supabase" else "💾"
                st.markdown(f"**{badge} {title}**")
                st.caption(f"📅 {chat_item.get('created_at', '')} • {chat_item.get('message_count', 0)} msgs")
                
                btn_col1, btn_col2 = st.columns([1, 1])
                with btn_col1:
                    if st.button("📂 Open", key=f"load_{chat_item['session_id']}_{idx}", use_container_width=True):
                        msgs = load_chat_messages_unified(chat_item["session_id"], chat_item.get("filename", ""), st.session_state.supabase_url, st.session_state.supabase_key)
                        if msgs:
                            st.session_state.messages = msgs
                            st.session_state.session_id = chat_item["session_id"]
                            if "chatbot" in st.session_state and st.session_state.chatbot:
                                st.session_state.chatbot.reset_chat()
                                for m in st.session_state.messages:
                                    st.session_state.chatbot.conversation_history.append({
                                        "role": m["role"],
                                        "content": m["content"]
                                    })
                        st.rerun()
                with btn_col2:
                    if st.button("🗑️ Del", key=f"del_{chat_item['session_id']}_{idx}", use_container_width=True):
                        delete_chat_unified(chat_item["session_id"], chat_item.get("filename", ""), st.session_state.supabase_url, st.session_state.supabase_key)
                        st.rerun()
                st.divider()

    st.divider()


    # Available Tools Section
    st.subheader("🛠️ Registered Tools")
    
    temp_bot = GeminiChatbot(api_key=st.session_state.api_key, model=st.session_state.model)
    for tool in temp_bot.get_tool_list():
        with st.expander(f"{tool['icon']} `{tool['name']}`"):
            st.write(tool["description"])

    st.divider()
    st.caption("Google GenAI SDK 2.x • Everyday AI Companion")


# Main UI Header
st.markdown('<p class="main-header">🤖 Gemini AI Assistant & Tool Hub</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Your intelligent companion for friendly chat, car details, laptop & mobile specs, weather, and math.</p>', unsafe_allow_html=True)

# Quick Prompts / Suggestions
if len(st.session_state.messages) == 0:
    st.markdown("##### 💡 Popular topics to try:")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🏖️ Goa 3-Day Trip from Mumbai", use_container_width=True):
            st.session_state.prompt_to_send = "Plan a 3 days holiday package for Goa from Mumbai with train and flight return cost, and show all hotel options from cheapest to richest!"
        if st.button("📱 iPhone 16 Pro vs Galaxy S25 Ultra", use_container_width=True):
            st.session_state.prompt_to_send = "Compare the camera sensors, Snapdragon 8 Elite vs A18 Pro, display, and price of iPhone 16 Pro Max and Samsung Galaxy S25 Ultra."
        if st.button("💻 MacBook Pro M4 Max vs ThinkPad X1", use_container_width=True):
            st.session_state.prompt_to_send = "What are the specs, battery life, and display features of the new MacBook Pro M4 Max and ThinkPad X1 Carbon Gen 13?"
    with col2:
        if st.button("🏔️ Manali 4-Day Trip from Delhi", use_container_width=True):
            st.session_state.prompt_to_send = "Suggest a 4 days Manali holiday package from Delhi with return travel fares and hotel stays from budget hostel to luxury resort."
        if st.button("🏎️ Porsche 911 GT3 RS vs Ferrari 296", use_container_width=True):
            st.session_state.prompt_to_send = "Tell me the horsepower, 0-60 time, powertrain, and pricing for the Porsche 911 GT3 RS and Ferrari 296 GTB."
        if st.button("🌤️ Tokyo & London Weather", use_container_width=True):
            st.session_state.prompt_to_send = "Hi how are you! What is the weather like in Tokyo and London right now?"
    with col3:
        if st.button("👑 Jaipur Royal Palace Trip", use_container_width=True):
            st.session_state.prompt_to_send = "What is the holiday package for Jaipur from Mumbai with 5-star heritage palace hotel and flight return cost?"
        if st.button("🌴 Kerala Munnar & Alleppey Package", use_container_width=True):
            st.session_state.prompt_to_send = "Show me the holiday package for Kerala with deluxe houseboat and return fares from Bengaluru."
        if st.button("🧮 Purchase Calculator with GST", use_container_width=True):
            st.session_state.prompt_to_send = "i want to buy an umberla cost of 40 rs and quantity is 500 with an gst of 5 percent calulate the total expense"


# Event collector for tools executed during the turn
tool_events_this_turn = []

def on_tool_call_handler(name: str, args: dict):
    tool_events_this_turn.append({"type": "call", "name": name, "args": args})

def on_tool_result_handler(name: str, result: any):
    tool_events_this_turn.append({"type": "result", "name": name, "result": result})

# Build a fingerprint of the current config so we can detect changes
import hashlib as _hashlib
_config_fingerprint = _hashlib.md5(
    f"{st.session_state.api_key}|{st.session_state.model}|{config.SYSTEM_INSTRUCTION}".encode()
).hexdigest()

# Get or create persistent chatbot instance — reinitialize if config changed
if (
    "chatbot" not in st.session_state
    or st.session_state.chatbot is None
    or st.session_state.get("_config_fingerprint") != _config_fingerprint
):
    st.session_state.chatbot = GeminiChatbot(
        api_key=st.session_state.api_key,
        model=st.session_state.model,
    )
    st.session_state["_config_fingerprint"] = _config_fingerprint

chatbot = st.session_state.chatbot
# Update handlers for current render
chatbot.on_tool_call = on_tool_call_handler
chatbot.on_tool_result = on_tool_result_handler


# Render previous chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🧑‍💻" if msg["role"] == "user" else "🤖"):
        if "tools" in msg and msg["tools"]:
            for event in msg["tools"]:
                if event["type"] == "call":
                    with st.status(f"⚙️ Tool Invoked: `{event['name']}`", state="complete"):
                        st.json(event["args"])
                elif event["type"] == "result":
                    with st.expander(f"📥 Output from `{event['name']}`"):
                        st.json(event["result"])
        st.markdown(msg["content"])

# Handle prompt input — always render chat_input to keep widget tree stable
chat_typed = st.chat_input("Ask about cars, laptop specs, smartphones, weather, math, or just chat...")
prompt_from_button = st.session_state.pop("prompt_to_send", None)

# Button prompt takes priority; otherwise use whatever the user typed
user_query = prompt_from_button or chat_typed


if user_query:
    current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 1. Append user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_query,
        "timestamp": current_time_str,
    })
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(user_query)

    # 2. Generate response with tool tracking
    with st.chat_message("assistant", avatar="🤖"):
        tool_events_this_turn.clear()
        
        with st.status("Analyzing request and evaluating tools...", expanded=True) as status_box:
            response_text = chatbot.send_message(user_query)
            
            if tool_events_this_turn:
                status_box.update(label=f"Executed {len(tool_events_this_turn)//2 or 1} tool(s) successfully!", state="complete", expanded=False)
            else:
                status_box.update(label="Response ready", state="complete", expanded=False)

        # Show executed tools
        for event in tool_events_this_turn:
            if event["type"] == "call":
                with st.status(f"⚙️ Tool Invoked: `{event['name']}`", state="complete"):
                    st.write("**Parameters:**")
                    st.json(event["args"])
            elif event["type"] == "result":
                with st.expander(f"📥 Tool Output: `{event['name']}`"):
                    st.json(event["result"])

        # Display final response
        st.markdown(response_text)

        # Save assistant message to session state
        st.session_state.messages.append({
            "role": "assistant",
            "content": response_text,
            "tools": list(tool_events_this_turn),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })

        # 3. Persist full conversation to Supabase Cloud and local disk
        save_chat_history(
            st.session_state.messages,
            st.session_state.session_id,
            st.session_state.supabase_url,
            st.session_state.supabase_key
        )


