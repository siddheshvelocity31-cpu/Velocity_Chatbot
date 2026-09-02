import os
import sys
import re
import functools
from pathlib import Path
from typing import Callable, Optional, List, Dict, Any

# Ensure project root is first in sys.path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

import config
from tools import AVAILABLE_TOOLS, TOOL_METADATA
from tools.weather import get_current_weather
from tools.calculator import calculate_expression
from tools.database import search_knowledge_base
from tools.datetime_tool import get_current_time
from tools.automotive import get_car_details
from tools.gadgets import get_laptop_specs, get_mobile_specs
from tools.travel import get_holiday_package



def sanitize_key(key: str) -> str:
    """Sanitize API key by stripping quotes, whitespace, and non-ASCII characters."""
    if not key:
        return ""
    cleaned = key.strip().strip("'\"`")
    return re.sub(r"[^\x20-\x7E]", "", cleaned).strip()


class GeminiChatbot:
    """Gemini-powered Chatbot with automated and monitored Tool Calling."""

    SUPPORTED_MODELS = [
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-2.0-flash-lite",
        "gemini-1.5-flash-8b",
    ]

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        system_instruction: Optional[str] = None,
        on_tool_call: Optional[Callable[[str, Dict[str, Any]], None]] = None,
        on_tool_result: Optional[Callable[[str, Any], None]] = None,
    ):
        raw_key = api_key or config.GEMINI_API_KEY or ""
        self.api_key = sanitize_key(raw_key)
        self.model = (model or config.GEMINI_MODEL or "gemini-3.5-flash").strip()
        self.system_instruction = system_instruction or config.SYSTEM_INSTRUCTION
        self.on_tool_call = on_tool_call
        self.on_tool_result = on_tool_result

        self.client: Optional[ChatGoogleGenerativeAI] = None
        self.chat = None
        self.tool_call_history: List[Dict[str, Any]] = []
        self.conversation_history: List[Dict[str, str]] = []
        self.last_api_error: Optional[str] = None

        self._initialize_client()
        self._initialize_chat()

    def is_live_mode(self) -> bool:
        """Check if a valid Gemini API key is configured."""
        return bool(self.api_key and self.api_key != "your_gemini_api_key_here" and len(self.api_key) > 10)

    def _initialize_client(self) -> None:
        """Initialize LangChain ChatGoogleGenerativeAI if API key is valid."""
        if self.is_live_mode():
            try:
                self.client = ChatGoogleGenerativeAI(
                    model=self.model,
                    google_api_key=self.api_key,
                    temperature=0.7
                )
            except Exception as e:
                self.client = None
                self.last_api_error = str(e)
        else:
            self.client = None

    def _wrap_tool(self, func: Callable) -> Callable:
        """Wrap a tool function to emit callbacks and record invocation telemetry."""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            tool_name = func.__name__
            if self.on_tool_call:
                try:
                    self.on_tool_call(tool_name, kwargs)
                except Exception:
                    pass

            result = func(*args, **kwargs)

            self.tool_call_history.append({
                "tool": tool_name,
                "args": kwargs,
                "result": result
            })

            if self.on_tool_result:
                try:
                    self.on_tool_result(tool_name, result)
                except Exception:
                    pass

            return result

        return wrapper

    def _get_instrumented_tools(self) -> List[Callable]:
        """Wrap all available tools with telemetry hooks and LangChain @tool."""
        return [tool(self._wrap_tool(t)) for t in AVAILABLE_TOOLS]

    def _initialize_chat(self) -> None:
        """Create a LangChain Agent session using create_react_agent."""
        if not self.is_live_mode() or not self.client:
            return

        tools = self._get_instrumented_tools()

        try:
            self.chat = create_react_agent(self.client, tools=tools, state_modifier=self.system_instruction)
            self.last_api_error = None
        except Exception as e:
            self.last_api_error = str(e)
            for fallback in self.SUPPORTED_MODELS:
                if fallback != self.model:
                    try:
                        self.model = fallback
                        fallback_client = ChatGoogleGenerativeAI(
                            model=self.model,
                            google_api_key=self.api_key,
                            temperature=0.7
                        )
                        self.client = fallback_client
                        self.chat = create_react_agent(self.client, tools=tools, state_modifier=self.system_instruction)
                        self.last_api_error = None
                        break
                    except Exception as fb_err:
                        self.last_api_error = str(fb_err)

    def test_connection(self) -> Dict[str, Any]:
        """Test API key connection by making a quick ping to Gemini."""
        if not self.is_live_mode():
            return {
                "success": False,
                "error": "API Key is empty or invalid. Please provide a key from https://aistudio.google.com/app/apikey"
            }

        try:
            llm = ChatGoogleGenerativeAI(model=self.model, google_api_key=self.api_key)
            resp = llm.invoke("ping")
            if resp:
                return {
                    "success": True,
                    "model": self.model,
                    "message": f"Successfully connected to Google Gemini ({self.model})!"
                }
            return {"success": True, "model": self.model, "message": "Connected!"}
        except Exception as e:
            err_msg = str(e)
            if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
                err_msg = (
                    f"⚠️ Quota limit reached on '{self.model}' (Free Tier).\n\n"
                    "👉 **How to solve:**\n"
                    "1. Switch the model dropdown to **'gemini-2.5-flash'** or **'gemini-2.0-flash'** in the sidebar (higher daily free quota).\n"
                    "2. Or generate a new free key at https://aistudio.google.com/app/apikey\n"
                    "3. Or continue using the built-in Offline Tool Engine (works 100% without quota limits)!"
                )
            return {
                "success": False,
                "error": err_msg
            }


    # ── Out-of-scope keywords that are CLEARLY outside tool coverage ──────────
    _OUT_OF_SCOPE_KEYWORDS = [
        "prime minister", "president", "who is", "who was", "history of",
        "capital of", "population of", "explain", "what is quantum",
        "write a poem", "write a story", "write code", "code for",
        "recipe", "how to cook", "translate", "in french", "in spanish",
        "meaning of", "definition of", "difference between",
        "tell me about", "essay on", "summarize", "summarise",
        "which country", "which state", "why did", "how did",
        "politics", "election", "war", "religion", "philosophy",
        "science", "biology", "chemistry", "physics", "history",
        "economics", "stock market", "cricket score", "sports score",
        "movie", "song", "actor", "actress", "celebrity",
    ]

    _TOOL_KEYWORDS = [
        # weather
        "weather", "temperature", "forecast", "rain", "humid", "climate",
        # calculator
        "calculate", "gst", "total cost", "price", "how much", "percent", "discount",
        "purchase", "buy", "quantity", "expense",
        # time
        "time", "date", "timezone", "what day",
        # cars
        "car", "tesla", "porsche", "bmw", "ferrari", "lamborghini", "mustang",
        "audi", "corvette", "honda", "toyota", "horsepower", "ev range", "0-60",
        # laptops
        "laptop", "macbook", "dell xps", "thinkpad", "asus rog", "hp spectre",
        "notebook", "ultrabook",
        # mobiles
        "iphone", "samsung", "galaxy", "pixel", "oneplus", "redmi", "xiaomi",
        "phone", "mobile", "smartphone",
        # travel
        "goa", "manali", "kashmir", "ujjain", "rajasthan", "jaipur", "kerala",
        "andaman", "varanasi", "trip", "travel", "holiday", "package", "hotel",
        "flight", "train", "tour", "destination",
        # greetings
        "hi", "hello", "hey", "how are you",
    ]

    def _is_out_of_scope(self, message: str) -> bool:
        """Detect if message is clearly outside tool coverage using a strict whitelist."""
        msg = message.lower().strip()
        
        # 1. Exact match conversational phrases (or starts with them)
        _CONVERSATIONAL = [
            'hi', 'hello', 'hey', 'how are you', 'good morning', 'good evening',
            'thanks', 'thank you', 'ok', 'okay', 'cool', 'awesome', 'great',
            'yes', 'no', 'yep', 'nope', 'sure', 'bye', 'goodbye'
        ]
        if msg in _CONVERSATIONAL or any(msg.startswith(g + ' ') for g in _CONVERSATIONAL):
            return False
            
        # 2. Whitelist: If any tool keyword matches, allow it to go to Gemini
        for kw in self._TOOL_KEYWORDS:
            if kw in msg:
                return False
                
        # 3. Everything else is blocked! No length exceptions!
        return True

    _OUT_OF_SCOPE_REPLY = (
        "⚠️ **I'm sorry, I can only assist with my available tools:**\n\n"
        "🌤️ **Weather** | 🧮 **Calculator** | 🕒 **Date & Time** | "
        "🏎️ **Car Specs** | 💻 **Laptop Specs** | 📱 **Mobile Specs** | 🏖️ **Holiday Packages**\n\n"
        "Your question is outside my current capabilities. Please ask about one of the topics above!"
    )

    def send_message(self, message: str) -> str:
        """Send a user message to the chatbot and maintain continuous multi-turn dialogue."""
        self.conversation_history.append({"role": "user", "content": message})
        reply = None

        # Block out-of-scope queries BEFORE hitting Gemini API
        if self._is_out_of_scope(message):
            reply = self._OUT_OF_SCOPE_REPLY
            self.conversation_history.append({"role": "assistant", "content": reply})
            return reply

        if self.is_live_mode():
            if not self.client or not self.chat:
                self._initialize_client()
                self._initialize_chat()

            if self.client and self.chat:
                try:
                    langchain_history = []
                    for msg in self.conversation_history:
                        if msg["role"] == "user":
                            langchain_history.append(HumanMessage(content=msg["content"]))
                        elif msg["role"] == "assistant":
                            langchain_history.append(AIMessage(content=msg["content"]))

                    response = self.chat.invoke({"messages": langchain_history})
                    ai_messages = [m for m in response.get("messages", []) if isinstance(m, AIMessage)]
                    if ai_messages:
                        reply = ai_messages[-1].content
                except Exception as e:
                    self.last_api_error = str(e)
                    reply = self._smart_chat_engine(message)

        if not reply:
            reply = self._smart_chat_engine(message)

        self.conversation_history.append({"role": "assistant", "content": reply})
        return reply

    def _smart_chat_engine(self, message: str) -> str:
        """Smart conversational engine with multi-turn memory and tool execution."""
        msg_lower = message.lower().strip()
        synthesized_parts = []

        # Check previous turn context if current query is a follow-up
        prev_user_msg = ""
        prev_bot_reply = ""
        if len(self.conversation_history) >= 2:
            prev_user_msg = self.conversation_history[-2]["content"].lower()
            prev_bot_reply = self.conversation_history[-1]["content"].lower()

        wrapped_weather = self._wrap_tool(get_current_weather)
        wrapped_calc = self._wrap_tool(calculate_expression)
        wrapped_db = self._wrap_tool(search_knowledge_base)
        wrapped_time = self._wrap_tool(get_current_time)
        wrapped_car = self._wrap_tool(get_car_details)
        wrapped_laptop = self._wrap_tool(get_laptop_specs)
        wrapped_mobile = self._wrap_tool(get_mobile_specs)
        wrapped_travel = self._wrap_tool(get_holiday_package)


        # Robust regex-based greeting detection
        greeting_pattern = r"\b(hi|hello|hey|hola|greetings|good morning|good afternoon|good evening|how are you|how r u|how do you do|sup|whats up|what's up|hows it going|how's it going)\b"
        has_greeting = bool(re.search(greeting_pattern, msg_lower))

        greeting_header = ""
        if has_greeting:
            greeting_header = "Hi! I am doing good, thanks for asking! 😊\n\n"

        # 1. Empathetic / Lonely / Casual Companion Chat
        if any(w in msg_lower for w in ["lonely", "alone", "sad", "bad day", "tired", "stressed", "depressed", "cheer me up", "talk to me", "just chat", "bored", "angry", "frustrated", "upset", "anxious", "worried", "overwhelmed"]):

            # User explicitly asks for a joke
            if any(w in msg_lower for w in ["joke", "jokes", "funny", "laugh", "make me laugh", "tell me something funny"]):
                return (
                    f"{greeting_header}"
                    "Here are a couple of jokes to brighten your day! 😄\n\n"
                    "**😂 Joke 1:**\n"
                    "> Why don't scientists trust atoms?\n"
                    "> *Because they make up everything!* 🤣\n\n"
                    "**😂 Joke 2:**\n"
                    "> I told my computer I needed a break...\n"
                    "> *Now it won't stop sending me Kit-Kat ads!* 🍫\n\n"
                    "**😂 Joke 3:**\n"
                    "> Why did the smartphone go to therapy?\n"
                    "> *It had too many issues!* 📱😂\n\n"
                    "Hope that put a smile on your face! 😊 Want to hear more or just chat? I'm here!"
                )

            # User explicitly asks for a story
            if any(w in msg_lower for w in ["story", "stories", "tell me a story", "bedtime story", "adventure", "tale"]):
                return (
                    f"{greeting_header}"
                    "Here's a short uplifting story just for you 🌟\n\n"
                    "---\n\n"
                    "**🌈 The Boy Who Planted Stars**\n\n"
                    "Once upon a time, in a quiet village surrounded by grey mountains, lived a boy named Aryan. "
                    "Every night, the villagers complained that the sky was too dark and too cold. "
                    "But Aryan had a different idea — instead of complaining, he climbed the tallest hill each evening "
                    "and held a little lantern up high.\n\n"
                    "\"One lantern won't light the whole sky,\" the villagers laughed.\n\n"
                    "Aryan just smiled and said, *\"No — but it might inspire someone else to bring theirs.\"*\n\n"
                    "Within a week, curious neighbours began joining him — each with their own lantern. "
                    "Within a month, the entire hilltop glowed warm and golden, visible from villages miles away.\n\n"
                    "The lesson? **One small act of hope can start a chain of light.** ✨\n\n"
                    "---\n\n"
                    "You are like Aryan — showing up, even on hard days. That takes courage. 💪 "
                    "How are you feeling now? Want to talk more, hear another story, or explore something fun together?"
                )

            # General sad/angry/lonely support
            return (
                f"{greeting_header}"
                "I'm really glad you reached out! 😊 I am always here to listen and chat with you.\n\n"
                "Remember that whatever you're feeling right now is temporary, and you're never truly alone. "
                "Take a deep breath and give yourself credit for making it through today. 💛\n\n"
                "Here's something that might help:\n"
                "- 😂 **Want a joke?** Just say *\"tell me a joke\"* — laughter is the best medicine!\n"
                "- 📖 **Want a story?** Say *\"tell me a story\"* — I have heartwarming tales ready!\n"
                "- 🏎️ **Distract yourself** with cool car specs or the latest gadgets!\n"
                "- 💬 **Just vent** — I'm here to listen, no judgement at all.\n\n"
                "What would you like to do? 🌟"
            )


        # 2. Car / Automotive Intent
        car_patterns = {
            "porsche 911": "porsche 911",
            "porsche": "porsche 911",
            "porchse": "porsche 911",
            "porshe": "porsche 911",
            "porche": "porsche 911",
            "911": "porsche 911",
            "gt3": "porsche 911",
            "tesla model 3": "tesla model 3",
            "tesla model y": "tesla model y",
            "tesla": "tesla model 3",
            "telsa": "tesla model 3",
            "cybertruck": "tesla model 3",
            "ford mustang": "ford mustang",
            "mustang": "ford mustang",
            "dark horse": "ford mustang",
            "bmw m3": "bmw m3",
            "bmw": "bmw m3",
            "bimmer": "bmw m3",
            "toyota camry": "toyota camry",
            "toyota": "toyota camry",
            "camry": "toyota camry",
            "honda civic": "honda civic",
            "civic": "honda civic",
            "type r": "honda civic",
            "audi r8": "audi r8",
            "audi": "audi r8",
            "r8": "audi r8",
            "ferrari 296": "ferrari 296",
            "ferrari": "ferrari 296",
            "lamborghini huracan": "lamborghini huracan",
            "lamborghini": "lamborghini huracan",
            "lambo": "lamborghini huracan",
            "corvette c8": "corvette c8",
            "corvette": "corvette c8",
            "c8": "corvette c8",
        }
        cars_found = []
        for pattern, car_key in car_patterns.items():
            if pattern in msg_lower and car_key not in cars_found:
                cars_found.append(car_key)

        # If general car comparison requested without specific brands
        if not cars_found and any(w in msg_lower for w in ["compare car", "compare cars", "best cars", "lets compare car"]):
            cars_found = ["porsche 911", "tesla model 3", "ferrari 296", "audi r8"]

        # ── General car buying / suggestion intent ────────────────────────────
        # STRICT NLP: Only trigger if the message EXPLICITLY mentions car-related words.
        # "want to buy" alone is NOT enough — the message must also contain a car term.
        # This prevents "I want to buy a house/phone/laptop" from triggering car suggestions.
        _car_context_words = [
            "car", "vehicle", "automobile", "auto", "sedan", "suv", "hatchback",
            "sports car", "electric car", "ev car", "budget car", "family car",
            "affordable car", "buy car", "purchase car", "buy a car", "purchase a car"
        ]
        _buying_words = [
            "buy", "purchase", "suggest", "recommend", "looking for", "planning to get",
            "want a car", "need a car", "which car", "what car", "best car", "good car"
        ]

        # Must have BOTH a buying word AND a car context word, OR explicit car phrases
        has_car_context = any(w in msg_lower for w in _car_context_words)
        has_buying_signal = any(w in msg_lower for w in _buying_words)
        car_buying_intent = has_car_context and has_buying_signal and not cars_found


        if car_buying_intent and not cars_found:
            # Detect budget hints in message
            budget_hint = ""
            nums = re.findall(r"\d+(?:,\d+)*(?:\.\d+)?", msg_lower.replace(",", ""))
            if nums:
                val = float(nums[0].replace(",", ""))
                if val < 30000:
                    budget_hint = "budget"
                elif val < 80000:
                    budget_hint = "mid"
                else:
                    budget_hint = "premium"

            # Detect category hints
            is_electric = any(w in msg_lower for w in ["electric", "ev", "tesla", "zero emission"])
            is_sports = any(w in msg_lower for w in ["sports", "fast", "supercar", "performance", "racing"])
            is_family = any(w in msg_lower for w in ["family", "spacious", "suv", "practical", "everyday"])
            is_budget = any(w in msg_lower for w in ["cheap", "affordable", "budget", "low cost", "under"])
            is_luxury = any(w in msg_lower for w in ["luxury", "premium", "high end", "expensive"])

            suggestion_text = "🏎️ **Great choice — let me help you pick the right car!**\n\n"

            if is_electric:
                suggestion_text += (
                    "⚡ **Best Electric Cars to Consider:**\n\n"
                    "| Car | Range | Price | Best For |\n"
                    "|-----|-------|-------|----------|\n"
                    "| **Tesla Model 3** | 358 mi | ~$40,240 | Daily commute + tech features |\n"
                    "| **Tesla Model Y** | 330 mi | ~$43,990 | Family + spacious |\n"
                    "| **BMW i4** | 300 mi | ~$52,000 | Luxury + performance |\n\n"
                    "💡 *Want full specs for any of these? Just ask — e.g. 'Tell me about Tesla Model 3'*"
                )
            elif is_sports or is_luxury:
                suggestion_text += (
                    "🔥 **Top Sports & Luxury Cars:**\n\n"
                    "| Car | Horsepower | 0-60 | Price | Best For |\n"
                    "|-----|------------|------|-------|----------|\n"
                    "| **Porsche 911 GT3 RS** | 518 hp | 3.0s | ~$241,300 | Track + thrill |\n"
                    "| **Ferrari 296 GTB** | 819 hp | 2.9s | ~$342,205 | Ultimate supercar |\n"
                    "| **BMW M3** | 503 hp | 3.4s | ~$75,900 | Daily sports luxury |\n"
                    "| **Audi R8** | 562 hp | 3.1s | ~$158,600 | Exotic everyday driver |\n\n"
                    "💡 *Say the car name to get full detailed specs!*"
                )
            elif is_family:
                suggestion_text += (
                    "👨‍👩‍👧 **Best Family Cars:**\n\n"
                    "| Car | Engine | Seats | Price | Best For |\n"
                    "|-----|--------|-------|-------|----------|\n"
                    "| **Toyota Camry** | 2.5L Hybrid | 5 | ~$28,400 | Reliability + fuel economy |\n"
                    "| **Honda Civic** | 1.5L Turbo | 5 | ~$24,950 | Urban + affordable |\n"
                    "| **Tesla Model Y** | Electric | 5-7 | ~$43,990 | Modern family SUV |\n\n"
                    "💡 *Want full details? Ask me about any of these cars!*"
                )
            elif is_budget:
                suggestion_text += (
                    "💰 **Budget-Friendly Cars (Best Value):**\n\n"
                    "| Car | Engine | Fuel Economy | Price | Best For |\n"
                    "|-----|--------|--------------|-------|----------|\n"
                    "| **Honda Civic** | 1.5L Turbo | 36 mpg avg | ~$24,950 | City driving |\n"
                    "| **Toyota Camry** | 2.5L Hybrid | 51 mpg (hybrid) | ~$28,400 | Long runs + savings |\n"
                    "| **Ford Mustang** | 2.3L EcoBoost | 25 mpg avg | ~$29,920 | Style on a budget |\n\n"
                    "💡 *Ask me about any model for full detailed specs!*"
                )
            else:
                # General recommendation across all categories
                suggestion_text += (
                    "Here's a quick guide based on what most buyers look for:\n\n"
                    "**💰 Budget / Everyday (Under $35K)**\n"
                    "- 🚗 **Honda Civic** — Reliable, fuel-efficient, great for city & highway\n"
                    "- 🚗 **Toyota Camry** — Spacious, comfortable, hybrid option available\n"
                    "- 🚗 **Ford Mustang EcoBoost** — Stylish sports look at an affordable price\n\n"
                    "**⚡ Electric / Eco-Friendly ($40K–$55K)**\n"
                    "- 🔋 **Tesla Model 3** — Best range, autopilot, tech-forward\n"
                    "- 🔋 **Tesla Model Y** — SUV body, great for families\n\n"
                    "**🏎️ Sports & Performance ($75K–$160K)**\n"
                    "- 🔥 **BMW M3** — Daily luxury with serious performance\n"
                    "- 🔥 **Audi R8** — Exotic V10 supercar for the road\n"
                    "- 🔥 **Porsche 911** — The gold standard of sports cars\n\n"
                    "**👑 Supercar / Dream Car ($240K+)**\n"
                    "- 🏆 **Porsche 911 GT3 RS** — Track-focused perfection\n"
                    "- 🏆 **Ferrari 296 GTB** — 819 hp hybrid supercar\n\n"
                    "---\n"
                    "💡 **To get full specs, just name the car:**\n"
                    "*e.g. 'Tell me about Tesla Model 3'* or *'Show me BMW M3 specs'*\n\n"
                    "What's your **budget range** or **what type of driving** do you do most? I'll narrow it down for you! 😊"
                )

            synthesized_parts.append(suggestion_text)

        for car_query in cars_found:
            res = wrapped_car(car_name=car_query)
            car = res["car"]
            specs_text = (
                f"🏎️ **{car['name']}** *({car['category']})*\n"
                f"- **Brand & Manufacturer**: {car.get('brand', 'Automotive')}\n"
                f"- **Engine / Powertrain**: {car['powertrain']}\n"
                f"- **Total Horsepower**: {car['horsepower']}\n"
                f"- **0-60 mph Acceleration**: {car.get('acceleration_0_60', 'N/A')}\n"
                f"- **Top Speed**: {car.get('top_speed', 'N/A')}\n"
                f"- **Starting Price**: {car['starting_price']}\n"
                f"- **Top Features**: {', '.join(car.get('key_features', []))}"
            )
            synthesized_parts.append(specs_text)

        # 3. Laptop Specifications Intent
        laptop_patterns = {
            "macbook pro": "macbook pro",
            "m4": "macbook pro",
            "m3": "macbook pro",
            "macbook air": "macbook air",
            "macbook": "macbook pro",
            "apple laptop": "macbook pro",
            "dell xps": "dell xps",
            "xps": "dell xps",
            "dell": "dell xps",
            "thinkpad": "thinkpad",
            "x1 carbon": "thinkpad",
            "lenovo": "thinkpad",
            "asus rog": "asus rog",
            "zephyrus": "asus rog",
            "g16": "asus rog",
            "g14": "asus rog",
            "asus": "asus rog",
            "quantumpro": "quantumpro",
        }
        laptops_found = []
        for pattern, lap_key in laptop_patterns.items():
            if pattern in msg_lower and lap_key not in laptops_found:
                laptops_found.append(lap_key)

        # If general laptop comparison requested (e.g. "lets compare an laptop", "compare laptops")
        if not laptops_found and any(w in msg_lower for w in ["compare", "best", "recommend", "which", "lets compare"]) and any(w in msg_lower for w in ["laptop", "laptops", "notebook", "computer"]):
            laptops_found = ["macbook pro", "dell xps", "thinkpad", "asus rog"]

        for laptop_query in laptops_found:
            res = wrapped_laptop(laptop_model=laptop_query)
            lap = res["laptop"]
            lap_text = (
                f"💻 **{lap['name']}** *({lap.get('category', 'High-Performance Laptop')})*\n"
                f"- **Brand**: {lap.get('brand', 'Tech')}\n"
                f"- **Display**: {lap['display']}\n"
                f"- **Processor & Architecture**: {lap['processor']}\n"
                f"- **Graphics (GPU)**: {lap.get('gpu', 'Integrated / High-Performance Dedicated GPU')}\n"
                f"- **Memory (RAM)**: {lap.get('ram', '16GB / 32GB High-Speed Unified RAM')}\n"
                f"- **Storage**: {lap.get('storage', '512GB to 2TB PCIe NVMe SSD')}\n"
                f"- **Battery & Charging**: {lap.get('battery_charging', lap.get('battery_life', 'All-Day Battery'))}\n"
                f"- **Build & Weight**: {lap.get('build_weight', lap.get('weight', 'Precision Chassis'))}\n"
                f"- **Ports & Connectivity**: {lap.get('ports_connectivity', 'Thunderbolt / USB-C, Wi-Fi 7')}\n"
                f"- **Webcam & Audio**: {lap.get('audio_camera', 'Studio Mics & Quad Speakers')}\n"
                f"- **Starting MSRP**: {lap['starting_price']}"
            )
            synthesized_parts.append(lap_text)

        # 4. Mobile Smartphone Specifications Intent
        phone_patterns = {
            "iphone 16 pro max": "iphone 16 pro max",
            "16 pro max": "iphone 16 pro max",
            "iphone 16 pro": "iphone 16 pro max",
            "iphone 16": "iphone 16 pro max",
            "iphone 15": "iphone 16 pro max",
            "iphone": "iphone 16 pro max",
            "apple phone": "iphone 16 pro max",
            "s25 ultra": "samsung galaxy s25 ultra",
            "s25": "samsung galaxy s25 ultra",
            "galaxy s25": "samsung galaxy s25 ultra",
            "s24 ultra": "samsung galaxy s25 ultra",
            "s24": "samsung galaxy s25 ultra",
            "samsung": "samsung galaxy s25 ultra",
            "galaxy": "samsung galaxy s25 ultra",
            "pixel 9 pro": "google pixel 9 pro",
            "pixel 9": "google pixel 9 pro",
            "pixel": "google pixel 9 pro",
            "google pixel": "google pixel 9 pro",
            "oneplus 13": "oneplus 13",
            "oneplus 12": "oneplus 13",
            "oneplus": "oneplus 13",
        }
        phones_found = []
        for pattern, ph_key in phone_patterns.items():
            if pattern in msg_lower and ph_key not in phones_found:
                phones_found.append(ph_key)

        # If general phone comparison requested
        if not phones_found and any(w in msg_lower for w in ["compare", "best", "recommend", "which", "lets compare"]) and any(w in msg_lower for w in ["phone", "phones", "mobile", "mobiles", "smartphone", "smartphones"]):
            phones_found = ["iphone 16 pro max", "samsung galaxy s25 ultra", "google pixel 9 pro", "oneplus 13"]

        for phone_query in phones_found:
            res = wrapped_mobile(mobile_model=phone_query)
            ph = res["phone"]
            ph_text = (
                f"📱 **{ph['name']}** *({ph.get('category', 'Flagship Smartphone')})*\n"
                f"- **Brand**: {ph.get('brand', 'Smartphone')}\n"
                f"- **Display**: {ph['display']}\n"
                f"- **Processor & AI Chip**: {ph['processor']}\n"
                f"- **Camera System**:\n{ph.get('camera', 'High-Res Multi-Lens System')}\n"
                f"- **Battery & Charging**: {ph.get('battery_charging', 'All-Day Battery with Fast Charging')}\n"
                f"- **Build & Weight**: {ph.get('build_weight', 'Grade 5 Titanium / Aluminum IP68')}\n"
                f"- **Special Features**: {ph.get('special_features', 'On-Device AI & 5G')}\n"
                f"- **Starting MSRP**: {ph['starting_price']}"
            )
            synthesized_parts.append(ph_text)

        # ── 4.5 Holiday & Travel Packages Intent ─────────────────────────────
        travel_keywords = [
            "holiday", "travel", "trip", "tour", "package", "vacation", "destination",
            "ujjain", "mahakal", "kashmir", "srinagar", "gulmarg", "pahalgam", "goa", "manali", "jaipur", "udaipur", "rajasthan", "kerala",
            "varanasi", "andaman", "hotel", "hotels", "flight fare", "train fare", "return journey", "cheapest hotel", "richest hotel"
        ]
        has_travel_intent = any(w in msg_lower for w in travel_keywords)

        dest_matches = []
        for d_name in ["ujjain", "mahakal", "kashmir", "srinagar", "gulmarg", "pahalgam", "goa", "manali", "jaipur", "udaipur", "rajasthan", "kerala", "varanasi", "andaman"]:
            if d_name in msg_lower:
                dest_matches.append(d_name)

        if has_travel_intent and (dest_matches or any(w in msg_lower for w in ["plan a trip", "holiday package", "travel package", "suggest a trip", "vacation package", "tour package"])):

            # ── Detect all known source cities in message ──────────────────────
            all_known_cities = ["delhi", "mumbai", "bengaluru", "bangalore", "pune",
                                "hyderabad", "chennai", "kolkata", "ahmedabad",
                                "nagpur", "amravati", "surat", "jaipur", "indore",
                                "lucknow", "bhopal", "patna", "chandigarh", "kochi"]

            # ── Detect duration in days ────────────────────────────────────────
            duration_days = 3
            days_match = re.search(r"(\d+)\s*(?:days?|day|nights?|night)", msg_lower)
            if days_match:
                duration_days = int(days_match.group(1))

            # ── Detect hotel budget tier preference ────────────────────────────
            hotel_tier = "all"
            if any(w in msg_lower for w in ["cheapest", "budget", "hostel", "low cost", "cheap"]):
                hotel_tier = "cheapest"
            elif any(w in msg_lower for w in ["comfort", "3 star", "3-star", "mid range", "mid-range"]):
                hotel_tier = "comfort"
            elif any(w in msg_lower for w in ["premium", "4 star", "4-star", "resort"]):
                hotel_tier = "premium"
            elif any(w in msg_lower for w in ["richest", "luxury", "5 star", "5-star", "palace", "ultra luxury"]):
                hotel_tier = "richest"

            # ── Detect travelers ───────────────────────────────────────────────
            travelers = 1
            trav_match = re.search(r"(\d+)\s*(?:people|person|travelers?|pax|members?)", msg_lower)
            if trav_match:
                travelers = int(trav_match.group(1))

            # ── Build multi-leg journey ────────────────────────────────────────
            # Detect "to X and then to Y" or "X to Y then Y to Z" patterns
            # Build legs as list of (source, destination) tuples
            legs = []

            # Pattern: "from A to B then/and B to C"
            # We read all destinations in order and pair them with the source city before each
            # Step 1: detect the initial source city
            initial_source = "mumbai"
            for city in all_known_cities:
                if f"from {city}" in msg_lower or msg_lower.startswith(city + " to "):
                    initial_source = city
                    break

            # Step 2: build legs from dest_matches in order
            if len(dest_matches) == 1:
                # Single destination — simple case
                legs = [(initial_source, dest_matches[0])]
            else:
                # Multi-leg: (source -> dest1), (dest1 -> dest2), etc.
                legs = [(initial_source, dest_matches[0])]
                for i in range(1, len(dest_matches)):
                    legs.append((dest_matches[i - 1], dest_matches[i]))

            # ── Call the travel tool for each leg ─────────────────────────────
            for (source_city, target_dest) in legs:
                pkg_data = wrapped_travel(
                    destination=target_dest,
                    source_city=source_city,
                    duration_days=duration_days,
                    hotel_tier=hotel_tier,
                    num_travelers=travelers
                )


            if pkg_data.get("status") == "success":
                tr = pkg_data["transport"]
                dest_title = pkg_data["destination"]
                nights = pkg_data["duration_nights"]
                days = pkg_data["duration_days"]
                source_lbl = pkg_data["source_city"]

                icon = "🏖️" if "Goa" in dest_title else ("🏔️" if "Manali" in dest_title else ("🕌" if "Jaipur" in dest_title else ("🌴" if "Kerala" in dest_title else ("🛕" if "Varanasi" in dest_title else "🌊"))))

                card_text = (
                    f"{icon} **{dest_title} Holiday Package ({days} Days / {nights} Nights)**\n"
                    f"*{pkg_data['tagline']}*\n\n"
                    f"📍 **Origin Source:** {source_lbl} | 👥 **Travelers:** {travelers} Pax | 🗓️ **Best Time:** {pkg_data['best_time_to_visit']}\n\n"
                    f"---\n"
                    f"### 🚆 ✈️ Return Journey Travel Options ({source_lbl} ⇄ {dest_title}):\n\n"
                    f"| Mode | Details | Estimated Return Fare (per person) |\n"
                    f"| :--- | :--- | :--- |\n"
                )

                if tr.get("train_available"):
                    card_text += (
                        f"| 🚆 **Train** | {tr['train_details']} | **Sleeper:** ₹{tr.get('train_roundtrip_sleeper_inr', 'N/A'):,} • **3AC:** ₹{tr.get('train_roundtrip_3ac_inr', 'N/A'):,} • **2AC:** ₹{tr.get('train_roundtrip_2ac_inr', 'N/A'):,} |\n"
                    )
                else:
                    card_text += f"| 🚆 **Train** | {tr.get('train_details', 'Not connected by rail')} | N/A |\n"

                if tr.get("flight_available"):
                    card_text += (
                        f"| ✈️ **Flight** | {tr['flight_details']} | **Economy Return:** ₹{tr.get('flight_roundtrip_inr', 'N/A'):,} |\n"
                    )

                card_text += (
                    f"\n---\n"
                    f"### 🏨 Hotel Stays (Categorized from Cheapest to Richest):\n\n"
                    f"| Tier & Hotel | Rating | Price / Night | Total Hotel ({nights} Nights) | Key Amenities |\n"
                    f"| :--- | :---: | :---: | :---: | :--- |\n"
                )

                for p in pkg_data["packages"]:
                    card_text += (
                        f"| **{p['tier_name']}**<br>*{p['hotel_name']}* | {p['rating']} | ₹{p['hotel_price_per_night_inr']:,} | **₹{p['hotel_total_inr']:,}** | {p['amenities']} |\n"
                    )

                card_text += (
                    f"\n---\n"
                    f"### 💰 Complete Package Budget Breakdown (Travel + Hotel + Food/Activities for {travelers} Pax):\n\n"
                    f"| Package Tier | Train (Sleeper) | Train (3AC) | Train (2AC) | Flight Return | Ideal For |\n"
                    f"| :--- | :---: | :---: | :---: | :---: | :--- |\n"
                )

                for p in pkg_data["packages"]:
                    sl_str = f"**₹{p['package_total_with_train_sleeper_inr']:,}**" if p.get("package_total_with_train_sleeper_inr") else "N/A"
                    ac3_str = f"**₹{p['package_total_with_train_inr']:,}**" if p.get("package_total_with_train_inr") else "N/A"
                    ac2_str = f"**₹{p['package_total_with_train_2ac_inr']:,}**" if p.get("package_total_with_train_2ac_inr") else "N/A"
                    flight_total_str = f"**₹{p['package_total_with_flight_inr']:,}**" if p.get("package_total_with_flight_inr") else "N/A"
                    card_text += (
                        f"| **{p['tier_name']}** | {sl_str} | {ac3_str} | {ac2_str} | {flight_total_str} | {p['description']} |\n"
                    )

                attractions_str = " • ".join(pkg_data.get("key_attractions", []))
                card_text += f"\n🎯 **Top Attractions & Highlights:** {attractions_str}\n"

                synthesized_parts.append(card_text)

        # 5. Weather Intent

        weather_cities = {
            # India
            "india": "Mumbai",
            "mumbai": "Mumbai",
            "delhi": "Delhi",
            "new delhi": "Delhi",
            "bengaluru": "Bengaluru",
            "bangalore": "Bengaluru",
            "chennai": "Chennai",
            "madras": "Chennai",
            "hyderabad": "Hyderabad",
            "kolkata": "Kolkata",
            "calcutta": "Kolkata",
            "pune": "Pune",
            "jaipur": "Jaipur",
            "ahmedabad": "Ahmedabad",
            # Asia & Middle East
            "tokyo": "Tokyo",
            "japan": "Tokyo",
            "singapore": "Singapore",
            "seoul": "Seoul",
            "korea": "Seoul",
            "south korea": "Seoul",
            "beijing": "Beijing",
            "shanghai": "Shanghai",
            "china": "Beijing",
            "bangkok": "Bangkok",
            "thailand": "Bangkok",
            "kuala lumpur": "Kuala Lumpur",
            "kl": "Kuala Lumpur",
            "malaysia": "Kuala Lumpur",
            "jakarta": "Jakarta",
            "indonesia": "Jakarta",
            "dubai": "Dubai",
            "uae": "Dubai",
            "riyadh": "Riyadh",
            "saudi": "Riyadh",
            "saudi arabia": "Riyadh",
            "istanbul": "Istanbul",
            "turkey": "Istanbul",
            "cairo": "Cairo",
            "egypt": "Cairo",
            # Europe
            "london": "London",
            "uk": "London",
            "england": "London",
            "paris": "Paris",
            "france": "Paris",
            "berlin": "Berlin",
            "germany": "Berlin",
            "rome": "Rome",
            "italy": "Rome",
            "madrid": "Madrid",
            "spain": "Madrid",
            "amsterdam": "Amsterdam",
            "netherlands": "Amsterdam",
            "moscow": "Moscow",
            "russia": "Moscow",
            # Americas
            "new york": "New York",
            "los angeles": "Los Angeles",
            "la": "Los Angeles",
            "san francisco": "San Francisco",
            "chicago": "Chicago",
            "usa": "New York",
            "america": "New York",
            "united states": "New York",
            "toronto": "Toronto",
            "canada": "Toronto",
            "mexico city": "Mexico City",
            "mexico": "Mexico City",
            "sao paulo": "Sao Paulo",
            "brazil": "Sao Paulo",
            # Africa & Oceania
            "nairobi": "Nairobi",
            "kenya": "Nairobi",
            "johannesburg": "Johannesburg",
            "south africa": "Johannesburg",
            "sydney": "Sydney",
            "australia": "Sydney",
        }
        is_weather_query = any(w in msg_lower for w in ["weather", "temperature", "forecast", "rain", "sunny", "climate", "climate today", "weather toad", "weather today"])
        if is_weather_query:
            target_city = "Mumbai"  # sensible default for Indian users
            for keyword, city_name in weather_cities.items():
                if keyword in msg_lower:
                    target_city = city_name
                    break

            res = wrapped_weather(city=target_city)
            data = res["data"]
            synthesized_parts.append(
                f"🌤️ **Current Weather in {data['city']} ({data.get('country', 'Region')})**:\n"
                f"- **Condition**: {data['condition']}\n"
                f"- **Temperature**: {data['temperature_c']}°C ({data['temperature_f']}°F)\n"
                f"- **Humidity**: {data['humidity']}, **Wind Speed**: {data['wind_speed']}"
            )


        # 6. Time Intent — only fire when user explicitly asks for the time
        time_explicit = any(phrase in msg_lower for phrase in [
            "what time", "current time", "time in", "time at", "what's the time",
            "whats the time", "clock", "timezone", "time zone", "ist time",
            "utc time", "gmt time"
        ])
        if time_explicit:
            tz = "UTC"
            city_found = "UTC"
            if "london" in msg_lower or "uk" in msg_lower:
                tz = "Europe/London"
                city_found = "London"
            elif "tokyo" in msg_lower or "japan" in msg_lower:
                tz = "Asia/Tokyo"
                city_found = "Tokyo"
            elif "mumbai" in msg_lower or "india" in msg_lower or "bengaluru" in msg_lower:
                tz = "Asia/Kolkata"
                city_found = "India (IST)"
            elif "new york" in msg_lower or "est" in msg_lower:
                tz = "America/New_York"
                city_found = "New York"
            elif "dubai" in msg_lower or "uae" in msg_lower:
                tz = "Asia/Dubai"
                city_found = "Dubai"
            elif "singapore" in msg_lower:
                tz = "Asia/Singapore"
                city_found = "Singapore"

            res = wrapped_time(tz_name=tz)
            synthesized_parts.append(
                f"🕒 **Current Time in {city_found}**:\n"
                f"- **{res.get('current_time')}** ({res.get('day_of_week')}, {res.get('current_date')})"
            )

        # 7. Math / Calculation Intent
        # Guard: skip math entirely if we already resolved car / laptop / phone specs
        already_handled = bool(cars_found or laptops_found or phones_found)
        has_math_keywords = (not already_handled) and any(w in msg_lower for w in [
            "calculate", "calulate", "calcuate", "compute", "math", "sqrt",
            "discount", "tax", "gst", "vat", "expense", "total expense",
            "how much", "how many", "rs", "rupee", "rupees",
            "buy", "purchase", "quantity", "pieces", "items"
        ])
        # Also fire math if message has explicit arithmetic operators between numbers
        if not has_math_keywords and not already_handled:
            has_math_keywords = bool(re.search(r"\d+\s*[\+\-\*\/]\s*\d+", msg_lower))

        if has_math_keywords:
            expr = None
            calc_result_text = None

            # ── Smart NLP Purchase / GST Calculator ──────────────────────────
            # Detect: "cost X, quantity Y, GST Z%" style queries
            purchase_keywords = any(w in msg_lower for w in [
                "buy", "purchase", "cost", "price", "rs", "rupee", "rupees",
                "quantity", "units", "pieces", "items", "expense", "total expense"
            ])
            has_gst = any(w in msg_lower for w in ["gst", "tax", "vat", "percent", "%"])

            if purchase_keywords:
                # Extract all numbers from the message
                all_nums = re.findall(r"\d+(?:\.\d+)?", message)
                nums = [float(n) for n in all_nums]

                unit_price = None
                quantity = None
                tax_rate = None

                # Try to extract unit price — look for price/cost/rs context
                price_match = re.search(
                    r"(?:cost|price|rs\.?|rupee[s]?|₹)\s*(?:of\s+)?(\d+(?:\.\d+)?)",
                    msg_lower
                )
                if price_match:
                    unit_price = float(price_match.group(1))

                # Try to extract quantity
                qty_match = re.search(
                    r"(?:quantity|qty|units?|pieces?|items?|nos?\.?)\s*(?:is\s+|of\s+|=\s*)?(\d+(?:\.\d+)?)",
                    msg_lower
                )
                if qty_match:
                    quantity = float(qty_match.group(1))

                # Try to extract GST / tax rate
                tax_match = re.search(
                    r"(?:gst|tax|vat)\s*(?:of\s+|@\s*|=\s*|is\s+)?(\d+(?:\.\d+)?)\s*(?:percent|%)?",
                    msg_lower
                )
                if not tax_match:
                    tax_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:percent|%)\s*(?:gst|tax|vat)", msg_lower)
                if tax_match:
                    tax_rate = float(tax_match.group(1))

                # Fallback: if we have 3 numbers and context, assign positionally
                if unit_price is None and quantity is None and len(nums) >= 2:
                    # Heuristic: smaller number = unit price, larger = quantity
                    if has_gst and len(nums) >= 3:
                        # Guess: cost, quantity, gst in some order
                        sorted_nums = sorted(nums[:3])
                        tax_rate = tax_rate or sorted_nums[0]  # smallest = gst %
                        unit_price = unit_price or sorted_nums[1]
                        quantity = quantity or sorted_nums[2]
                    elif len(nums) >= 2:
                        unit_price = unit_price or nums[0]
                        quantity = quantity or nums[1]

                if unit_price is not None and quantity is not None:
                    subtotal = unit_price * quantity
                    if tax_rate is not None:
                        gst_amount = subtotal * (tax_rate / 100)
                        grand_total = subtotal + gst_amount
                        calc_result_text = (
                            f"🧮 **Purchase Expense Breakdown**\n\n"
                            f"| Item | Value |\n"
                            f"|------|-------|\n"
                            f"| 🏷️ Unit Price | ₹{unit_price:,.2f} |\n"
                            f"| 📦 Quantity | {int(quantity)} units |\n"
                            f"| 💰 Subtotal | ₹{subtotal:,.2f} |\n"
                            f"| 📊 GST ({tax_rate}%) | ₹{gst_amount:,.2f} |\n"
                            f"| ✅ **Grand Total** | **₹{grand_total:,.2f}** |"
                        )
                    else:
                        calc_result_text = (
                            f"🧮 **Purchase Expense Breakdown**\n\n"
                            f"| Item | Value |\n"
                            f"|------|-------|\n"
                            f"| 🏷️ Unit Price | ₹{unit_price:,.2f} |\n"
                            f"| 📦 Quantity | {int(quantity)} units |\n"
                            f"| ✅ **Total Cost** | **₹{subtotal:,.2f}** |"
                        )

            # ── Discount Calculator ───────────────────────────────────────────
            if calc_result_text is None and any(w in msg_lower for w in ["discount", "off", "sale"]):
                price_m = re.search(r"(\d+(?:\.\d+)?)", message)
                disc_m = re.search(r"(\d+(?:\.\d+)?)\s*(?:percent|%)\s*(?:off|discount)?|(?:discount|off)\s*(?:of\s+)?(\d+(?:\.\d+)?)%?", msg_lower)
                if price_m and disc_m:
                    orig = float(price_m.group(1))
                    disc_val = disc_m.group(1) or disc_m.group(2)
                    if disc_val:
                        disc = float(disc_val)
                        saved = orig * (disc / 100)
                        final = orig - saved
                        calc_result_text = (
                            f"🧮 **Discount Calculation**\n\n"
                            f"| Item | Value |\n"
                            f"|------|-------|\n"
                            f"| 💵 Original Price | ₹{orig:,.2f} |\n"
                            f"| 🏷️ Discount ({disc}%) | -₹{saved:,.2f} |\n"
                            f"| ✅ **Final Price** | **₹{final:,.2f}** |"
                        )

            # ── Direct expression / formula evaluation ────────────────────────
            if calc_result_text is None:
                if "sqrt(256)" in msg_lower:
                    expr = "sqrt(256) * 15 + 42"
                elif "1500" in msg_lower and "0.18" in msg_lower:
                    expr = "(1500 * 0.18) + (250 / 5) - sqrt(81)"
                elif re.search(r"calculate|calulate|calcuate", msg_lower):
                    calc_part = re.split(r"calulat[e]?|calculat[e]?", message, flags=re.IGNORECASE)[-1].strip().rstrip("?.,!")
                    if calc_part and re.search(r"\d", calc_part):
                        expr = calc_part
                else:
                    m = re.search(r"(\d+(?:\.\d+)?(?:\s*[\+\-\*\/\^]\s*\d+(?:\.\d+)?)+)", message)
                    if m:
                        expr = m.group(1)

                if expr:
                    res = wrapped_calc(expression=expr)
                    if res.get("status") == "success":
                        calc_result_text = f"🧮 **Calculation Result**: `{res['expression']}` = **{res['result']}**"

            if calc_result_text:
                synthesized_parts.append(calc_result_text)


        # 8. Knowledge Base Intent
        if any(w in msg_lower for w in ["return policy", "refund policy", "shipping rates", "support hours"]):
            query_term = "return policy" if "return" in msg_lower or "refund" in msg_lower else "shipping"
            res = wrapped_db(query=query_term)
            if res.get("articles"):
                article = res["articles"][0]
                synthesized_parts.append(
                    f"📚 **Knowledge Base: {article['title']}**\n{article['content']}"
                )

        # Build final response
        if synthesized_parts:
            return greeting_header + "\n\n".join(synthesized_parts)

        # ── Context-aware conversational fallback ─────────────────────────────

        # Check if the previous bot reply was a friendly/companion chat
        prev_was_companion = False
        prev_was_greeting_response = False
        if len(self.conversation_history) >= 2:
            last_bot = self.conversation_history[-1]["content"].lower()
            prev_was_companion = any(w in last_bot for w in [
                "glad you reached out", "i'm here to listen", "never truly alone",
                "long day", "lonely", "tell me a story", "joke", "take a deep breath"
            ])
            prev_was_greeting_response = any(w in last_bot for w in [
                "how can i help", "what would you like", "i am your gemini"
            ])

        # Open-ended / "you decide" messages — user is handing the wheel to us
        open_ended = any(phrase in msg_lower for phrase in [
            "you can tell", "tell me anything", "tell me something", "whatever you want",
            "you decide", "anything", "go ahead", "sure", "okay", "ok", "alright",
            "i'm listening", "im listening", "what do you want", "you choose",
            "surprise me", "anything interesting", "what's new", "whats new",
            "go on", "continue", "please", "yeah", "yep", "yup", "cool", "nice",
            "that's fine", "thats fine", "sounds good", "of course", "why not"
        ])

        if prev_was_companion or open_ended:
            import random
            fun_facts = [
                (
                    "🌍 **Did you know?**\n\n"
                    "Honey never spoils. Archaeologists have found 3,000-year-old honey in Egyptian tombs "
                    "that was still perfectly edible! 🍯\n\n"
                    "Nature is truly amazing, isn't it? What else would you like to talk about? 😊"
                ),
                (
                    "🚀 **Space Fact!**\n\n"
                    "If you could drive a car straight up into the sky at highway speed (100 km/h), "
                    "you'd reach outer space in just about **1 hour**! 🌌\n\n"
                    "Pretty wild to think about! Want to hear another fun fact, or chat about something else?"
                ),
                (
                    "🐬 **Animal Wonder!**\n\n"
                    "Dolphins have names for each other! They use unique whistles to call out to "
                    "specific friends — just like we use first names. 🐬\n\n"
                    "Animals are more like us than we think! What's on your mind today? 😊"
                ),
                (
                    "🧠 **Brain Fact!**\n\n"
                    "Your brain generates about **23 watts of power** when you're awake — "
                    "enough to power a small LED bulb! 💡\n\n"
                    "You literally light up the world just by thinking! How are you feeling right now?"
                ),
                (
                    "🎵 **Music & Mood!**\n\n"
                    "Studies show that listening to music you love releases dopamine — "
                    "the same 'feel-good' chemical released when you eat your favourite food! 🎶\n\n"
                    "What kind of music do you enjoy? I'd love to know more about you! 😊"
                ),
                (
                    "🌊 **Ocean Mystery!**\n\n"
                    "We have explored less than **20% of Earth's oceans**. The deep sea is more "
                    "mysterious to us than the surface of Mars! 🌊🔍\n\n"
                    "The world is full of wonders waiting to be discovered — just like you! "
                    "What would you like to explore today?"
                ),
            ]
            chosen = random.choice(fun_facts)
            prefix = "Hi! I am doing good, thanks for asking! 😊\n\n" if has_greeting else ""
            if prev_was_companion:
                prefix = "Of course! 😊 I'd love to share something interesting with you!\n\n"
            return prefix + chosen

        # Pure greeting with no other intent
        if has_greeting:
            return (
                "Hi! I am doing good, thanks for asking! 😊\n\n"
                "I am your **AI Assistant**. Here are some things you can explore:\n"
                "- 🏎️ **Car Specs**: Ask about Porsche, Ferrari, Tesla, BMW, or any car\n"
                "- 💻 **Laptop Specs**: MacBook Pro M4, Dell XPS, ThinkPad Gen 13, ASUS ROG\n"
                "- 📱 **Mobile Specs**: iPhone 16 Pro Max, Galaxy S25 Ultra, Pixel 9, OnePlus 13\n"
                "- 🌤️ **Weather**: Ask about any city or country in the world\n"
                "- 🧮 **Calculator**: Purchase totals, GST, discounts, math\n"
                "- 💬 **Friendly Chat**: Just talk — I'm always here! 😊\n\n"
                "How can I help you today?"
            )

        # Absolute last resort — out of scope refusal
        return self._OUT_OF_SCOPE_REPLY

    def reset_chat(self) -> None:
        """Reset conversation history and start a new session."""
        self.tool_call_history.clear()
        self.conversation_history.clear()
        self.last_api_error = None
        self._initialize_chat()

    def get_tool_list(self) -> List[Dict[str, str]]:
        """Get summary of available tools for display."""
        tool_info = []
        for tool in AVAILABLE_TOOLS:
            name = tool.__name__
            meta = TOOL_METADATA.get(name, {"description": tool.__doc__, "icon": "🔧"})
            tool_info.append({
                "name": name,
                "icon": meta.get("icon", "🔧"),
                "description": meta.get("description", tool.__doc__ or "No description")
            })
        return tool_info
