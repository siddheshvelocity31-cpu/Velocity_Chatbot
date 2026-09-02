from flask import Flask, render_template, request, jsonify, session

from pathlib import Path
from datetime import datetime

import json
import re
import uuid

import config
import supabase_db
from bot import GeminiChatbot


app = Flask(__name__)

from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Secret key used by Flask sessions
app.secret_key = "gemini-chatbot-secret-key-change-this"


# ============================================================
# LOCAL CHAT HISTORY
# ============================================================

CHAT_HISTORY_DIR = Path(__file__).resolve().parent / "chat_history"
CHAT_HISTORY_DIR.mkdir(exist_ok=True)


def sanitize_api_key(key: str) -> str:
    """
    Remove quotes, whitespace and invalid characters.
    """
    if not key:
        return ""

    cleaned = key.strip().strip("'\"`")

    return re.sub(
        r"[^\x20-\x7E]",
        "",
        cleaned
    ).strip()


def save_chat_to_file(messages, session_id):
    """
    Save chat messages to local JSON.
    """

    if not messages:
        return

    filepath = CHAT_HISTORY_DIR / f"{session_id}.json"

    chat_data = {
        "session_id": session_id,
        "created_at": (
            messages[0].get("timestamp")
            if messages
            else datetime.now().isoformat()
        ),
        "message_count": len(messages),
        "messages": messages
    }

    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(
            chat_data,
            file,
            indent=2,
            ensure_ascii=False
        )


def save_chat_history(
    messages,
    session_id,
    supabase_url=None,
    supabase_key=None
):
    """
    Save chat locally and to Supabase if configured.
    """

    if not messages:
        return

    # Local backup
    save_chat_to_file(messages, session_id)

    # Supabase
    if supabase_db.is_supabase_configured(
        supabase_url,
        supabase_key
    ):
        supabase_db.save_chat_session(
            session_id,
            messages,
            url=supabase_url,
            key=supabase_key
        )


# ============================================================
# LOAD CHAT HISTORY
# ============================================================

def load_all_chats():
    """
    Load all saved conversations.
    """

    chats = []

    # --------------------------------------------------------
    # First try Supabase
    # --------------------------------------------------------

    supabase_url = config.SUPABASE_URL
    supabase_key = config.SUPABASE_KEY

    if supabase_db.is_supabase_configured(
        supabase_url,
        supabase_key
    ):
        try:

            supa_sessions = supabase_db.get_all_chat_sessions(
                url=supabase_url,
                key=supabase_key
            )

            if supa_sessions:

                for chat in supa_sessions:

                    chats.append({
                        "session_id": chat["session_id"],
                        "title": chat.get(
                            "title",
                            "Conversation"
                        ),
                        "created_at": chat.get(
                            "created_at",
                            ""
                        ),
                        "message_count": chat.get(
                            "message_count",
                            0
                        ),
                        "source": "supabase"
                    })

                return chats

        except Exception as error:

            print(
                "Supabase history error:",
                error
            )

    # --------------------------------------------------------
    # Local fallback
    # --------------------------------------------------------

    for filepath in sorted(
        CHAT_HISTORY_DIR.glob("*.json"),
        reverse=True
    ):

        try:

            with open(
                filepath,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

            first_message = ""

            for message in data.get(
                "messages",
                []
            ):

                if message.get("role") == "user":

                    first_message = message.get(
                        "content",
                        ""
                    )

                    break

            chats.append({
                "session_id": data.get(
                    "session_id",
                    filepath.stem
                ),
                "title": (
                    first_message[:40]
                    if first_message
                    else "Conversation"
                ),
                "created_at": data.get(
                    "created_at",
                    ""
                ),
                "message_count": data.get(
                    "message_count",
                    0
                ),
                "source": "local"
            })

        except Exception as error:

            print(
                "Could not read chat:",
                error
            )

    return chats


def load_chat_messages(session_id):
    """
    Load a particular conversation.
    """

    supabase_url = config.SUPABASE_URL
    supabase_key = config.SUPABASE_KEY

    # --------------------------------------------------------
    # Supabase first
    # --------------------------------------------------------

    if supabase_db.is_supabase_configured(
        supabase_url,
        supabase_key
    ):

        try:

            messages = supabase_db.get_chat_messages(
                session_id,
                url=supabase_url,
                key=supabase_key
            )

            if messages:
                return messages

        except Exception as error:

            print(
                "Supabase message error:",
                error
            )

    # --------------------------------------------------------
    # Local fallback
    # --------------------------------------------------------

    filepath = CHAT_HISTORY_DIR / f"{session_id}.json"

    if filepath.exists():

        try:

            with open(
                filepath,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

            return data.get(
                "messages",
                []
            )

        except Exception as error:

            print(
                "Local chat error:",
                error
            )

    return []


def delete_chat(session_id):
    """
    Delete chat from Supabase and local storage.
    """

    supabase_url = config.SUPABASE_URL
    supabase_key = config.SUPABASE_KEY

    # --------------------------------------------------------
    # Supabase
    # --------------------------------------------------------

    if supabase_db.is_supabase_configured(
        supabase_url,
        supabase_key
    ):

        try:

            supabase_db.delete_chat_session(
                session_id,
                url=supabase_url,
                key=supabase_key
            )

        except Exception as error:

            print(
                "Supabase delete error:",
                error
            )

    # --------------------------------------------------------
    # Local file
    # --------------------------------------------------------

    filepath = CHAT_HISTORY_DIR / f"{session_id}.json"

    if filepath.exists():
        filepath.unlink()


# ============================================================
# CHATBOT MANAGEMENT
# ============================================================

# Store chatbot instances for active browser sessions
chatbots = {}


def get_session_id():
    """
    Get or create a browser session ID.
    """

    if "session_id" not in session:

        session["session_id"] = str(
            uuid.uuid4()
        )

    return session["session_id"]


def get_chatbot():
    """
    Get or create Gemini chatbot for current session.
    """

    session_id = get_session_id()

    if session_id not in chatbots:

        chatbot = GeminiChatbot(
            api_key=config.GEMINI_API_KEY,
            model=getattr(
                config,
                "GEMINI_MODEL",
                "gemini-3.5-flash"
            )
        )

        chatbots[session_id] = chatbot

    return chatbots[session_id]


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def home():

    session_id = get_session_id()

    messages = load_chat_messages(
        session_id
    )

    return render_template(
        "index.html",
        messages=messages,
        model=getattr(
            config,
            "GEMINI_MODEL",
            "gemini-3.5-flash"
        )
    )


# ============================================================
# API: SEND MESSAGE
# ============================================================

@app.route(
    "/api/chat",
    methods=["POST"]
)
def api_chat():

    try:

        data = request.get_json(
            silent=True
        ) or {}

        user_query = data.get(
            "message",
            ""
        ).strip()

        if not user_query:

            return jsonify({
                "success": False,
                "error": "Message cannot be empty."
            }), 400

        session_id = get_session_id()

        chatbot = get_chatbot()

        # ----------------------------------------------------
        # Track tool calls
        # ----------------------------------------------------

        tool_events = []

        def on_tool_call(name, args):

            tool_events.append({
                "type": "call",
                "name": name,
                "args": args
            })

        def on_tool_result(name, result):

            tool_events.append({
                "type": "result",
                "name": name,
                "result": result
            })

        chatbot.on_tool_call = on_tool_call
        chatbot.on_tool_result = on_tool_result

        # ----------------------------------------------------
        # Current timestamp
        # ----------------------------------------------------

        timestamp = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        # ----------------------------------------------------
        # Generate Gemini response
        # ----------------------------------------------------

        response_text = chatbot.send_message(
            user_query
        )

        # ----------------------------------------------------
        # Get existing messages
        # ----------------------------------------------------

        messages = load_chat_messages(
            session_id
        )

        # ----------------------------------------------------
        # Add user message
        # ----------------------------------------------------

        messages.append({
            "role": "user",
            "content": user_query,
            "timestamp": timestamp
        })

        # ----------------------------------------------------
        # Add assistant response
        # ----------------------------------------------------

        messages.append({
            "role": "assistant",
            "content": response_text,
            "tools": tool_events,
            "timestamp": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        })

        # ----------------------------------------------------
        # Save conversation
        # ----------------------------------------------------

        save_chat_history(
            messages,
            session_id,
            config.SUPABASE_URL,
            config.SUPABASE_KEY
        )

        return jsonify({
            "success": True,
            "response": response_text,
            "tools": tool_events,
            "session_id": session_id
        })

    except Exception as error:

        print(
            "CHAT ERROR:",
            error
        )

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# ============================================================
# API: NEW CHAT
# ============================================================

@app.route(
    "/new-chat",
    methods=["POST"]
)
def new_chat():

    old_session_id = get_session_id()

    # Remove old chatbot
    chatbots.pop(
        old_session_id,
        None
    )

    # Create new session
    session["session_id"] = str(
        uuid.uuid4()
    )

    return jsonify({
        "success": True,
        "session_id": session["session_id"]
    })


# ============================================================
# API: CHAT HISTORY
# ============================================================

@app.route(
    "/api/history",
    methods=["GET", "POST"]
)
def api_history():

    try:

        # ----------------------------------------------------
        # GET = list conversations
        # ----------------------------------------------------

        if request.method == "GET":

            chats = load_all_chats()

            return jsonify({
                "success": True,
                "chats": chats
            })

        # ----------------------------------------------------
        # POST = load specific conversation
        # ----------------------------------------------------

        data = request.get_json(
            silent=True
        ) or {}

        session_id = data.get(
            "session_id"
        )

        if not session_id:

            return jsonify({
                "success": False,
                "error": "session_id is required."
            }), 400

        messages = load_chat_messages(
            session_id
        )

        return jsonify({
            "success": True,
            "messages": messages
        })

    except Exception as error:

        print(
            "HISTORY ERROR:",
            error
        )

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# ============================================================
# API: LOAD PARTICULAR CHAT
# ============================================================

@app.route(
    "/api/history/<session_id>",
    methods=["GET"]
)
def api_history_messages(session_id):

    messages = load_chat_messages(
        session_id
    )

    return jsonify({
        "success": True,
        "messages": messages
    })


# ============================================================
# API: DELETE CHAT
# ============================================================

@app.route(
    "/api/history/<session_id>",
    methods=["DELETE"]
)
def api_delete_history(session_id):

    delete_chat(
        session_id
    )

    chatbots.pop(
        session_id,
        None
    )

    return jsonify({
        "success": True
    })


# ============================================================
# API: TEST GEMINI CONNECTION
# ============================================================

@app.route(
    "/api/gemini/test",
    methods=["POST"]
)
def api_test_gemini():

    try:

        chatbot = GeminiChatbot(
            api_key=config.GEMINI_API_KEY,
            model=getattr(
                config,
                "GEMINI_MODEL",
                "gemini-3.5-flash"
            )
        )

        result = chatbot.test_connection()

        return jsonify(result)

    except Exception as error:

        print(
            "GEMINI TEST ERROR:",
            error
        )

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# ============================================================
# API: TEST SUPABASE CONNECTION
# ============================================================

@app.route(
    "/api/supabase/test",
    methods=["POST", "GET"]
)
def api_test_supabase():

    try:

        result = (
            supabase_db
            .test_supabase_connection(
                config.SUPABASE_URL,
                config.SUPABASE_KEY
            )
        )

        return jsonify(result)

    except Exception as error:

        print(
            "SUPABASE TEST ERROR:",
            error
        )

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# ============================================================
# API: AVAILABLE TOOLS
# ============================================================

@app.route(
    "/api/tools",
    methods=["GET"]
)
def api_tools():

    try:

        chatbot = get_chatbot()

        tool_list = chatbot.get_tool_list()

        return jsonify({
            "success": True,
            "tools": tool_list
        })

    except Exception as error:

        print(
            "TOOLS ERROR:",
            error
        )

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# ============================================================
# API: AVAILABLE MODELS
# ============================================================

@app.route(
    "/api/models",
    methods=["GET"]
)
def api_models():

    try:

        current_model = getattr(
            config,
            "GEMINI_MODEL",
            "gemini-3.5-flash"
        )

        return jsonify({
            "success": True,
            "models": [
                {
                    "id": current_model,
                    "name": current_model,
                    "provider": "Google Gemini"
                }
            ],
            "current_model": current_model
        })

    except Exception as error:

        print(
            "MODELS ERROR:",
            error
        )

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/health")
def health():

    return jsonify({
        "status": "running",
        "service": "Gemini Tool Calling Chatbot"
    })


# ============================================================
# COMPATIBILITY ROUTES
# ============================================================
#
# These keep your older frontend/API URLs working too.
# Your new frontend should use /api/... routes.
# ============================================================


@app.route(
    "/chat",
    methods=["POST"]
)
def old_chat():

    return api_chat()


@app.route(
    "/history",
    methods=["GET"]
)
def old_history():

    return api_history()


@app.route(
    "/history/<session_id>",
    methods=["GET"]
)
def old_history_messages(session_id):

    return api_history_messages(
        session_id
    )


@app.route(
    "/history/<session_id>",
    methods=["DELETE"]
)
def old_delete_history(session_id):

    return api_delete_history(
        session_id
    )


@app.route(
    "/tools",
    methods=["GET"]
)
def old_tools():

    return api_tools()


@app.route(
    "/test-gemini",
    methods=["POST"]
)
def old_test_gemini():

    return api_test_gemini()


@app.route(
    "/test-supabase",
    methods=["GET"]
)
def old_test_supabase():

    return api_test_supabase()


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("Gemini AI Tool-Calling Chatbot")
    print("=" * 60)
    print()

    print("Open your browser:")
    print("http://127.0.0.1:5000")

    print()

    print("API endpoints:")
    print("  GET  /api/models")
    print("  GET  /api/tools")
    print("  GET  /api/history")
    print("  POST /api/history")
    print("  POST /api/chat")
    print("  POST /api/supabase/test")
    print("  POST /api/gemini/test")

    print()
    print("=" * 60)

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )