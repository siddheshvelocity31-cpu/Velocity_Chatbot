# 🤖 Gemini AI Assistant & Tool Engine

A feature-rich prototype demonstrating **Tool Calling (Function Calling)** with the **Google Gemini API** (`gemini-3.6-flash`) using the official **`google-genai` SDK**.

Featuring both an interactive **Streamlit Web UI** and a **Rich Terminal Interface**.

---

## 🌟 Capabilities & Registered Tools

| Icon | Tool | Description |
| :--- | :--- | :--- |
| 🏎️ | [`get_car_details`](file:///d:/USERS/Desktop/chatbot/tools/automotive.py) | Full horsepower, 0-60 mph, range/fuel economy, price & specs for any car (Tesla, Porsche, Mustang, BMW, Toyota, Honda, etc.) |
| 💻 | [`get_laptop_specs`](file:///d:/USERS/Desktop/chatbot/tools/gadgets.py) | Full display, CPU, GPU, RAM, battery life, and pricing for any laptop (MacBook Pro/Air, Dell XPS, ThinkPad, ASUS ROG, etc.) |
| 📱 | [`get_mobile_specs`](file:///d:/USERS/Desktop/chatbot/tools/gadgets.py) | Camera setup, processor, display, battery, and price for any smartphone (iPhone 16 Pro, S24 Ultra, Pixel 9, OnePlus 12, etc.) |
| 🌤️ | [`get_current_weather`](file:///d:/USERS/Desktop/chatbot/tools/weather.py) | Real-time and simulated weather conditions for any city worldwide. |
| 🧮 | [`calculate_expression`](file:///d:/USERS/Desktop/chatbot/tools/calculator.py) | Safe mathematical, algebraic, and financial formula evaluator. |
| 🕒 | [`get_current_time`](file:///d:/USERS/Desktop/chatbot/tools/datetime_tool.py) | Current time and date for any world timezone. |
| 📚 | [`search_knowledge_base`](file:///d:/USERS/Desktop/chatbot/tools/database.py) | Knowledge base lookup for policies, returns, and support FAQs. |
| 💬 | **Empathetic Companion** | Warm, supportive, uplifting conversational AI for everyday chatting, feelings, and companionship. |

---

## 🚀 Running in VS Code

Open the integrated terminal in VS Code (`Ctrl + ~`) and run:

### 1. Launch the Web Interface (Streamlit)
```powershell
.\venv\Scripts\streamlit run app.py
```
*Opens in browser at `http://localhost:8501`.*

### 2. Launch the Terminal Interactive Chat (Rich CLI)
```powershell
.\venv\Scripts\python cli.py
```

### 3. Run the Automated Demo Showcase
```powershell
.\venv\Scripts\python demo.py
```

---

## 💡 Everyday Example Prompts to Try

1. **Cars**: *"What is the horsepower and 0-60 time for the Tesla Model 3 and Porsche 911?"*
2. **Laptops**: *"What are the specs and battery life of the MacBook Pro M3 and Dell XPS 16?"*
3. **Mobiles**: *"Compare the camera, processor, and price of iPhone 16 Pro and Galaxy S24 Ultra."*
4. **Companionship**: *"Hi, I had a long day and feel a bit lonely, can we chat?"*
5. **Weather & Greeting**: *"Hi how are you! What's the weather in Tokyo today?"*
6. **Math**: *"Calculate (1500 * 0.18) + (250 / 5) - sqrt(81)"*

---

## 🗄️ Cloud Database (Supabase Integration)

Chat history is automatically saved to **Supabase PostgreSQL Cloud Database** (with automatic local JSON file backup).

### How to Set Up Supabase (Free):
1. Create a free project at [supabase.com](https://supabase.com).
2. Go to **SQL Editor** in Supabase and run the queries from [`supabase_schema.sql`](file:///d:/USERS/Desktop/chatbot/supabase_schema.sql).
3. Copy your **Project URL** and **API Key (anon/public)** from **Project Settings > API**.
4. Paste them into your `.env` file or directly in the Streamlit sidebar under **🗄️ Database (Supabase Cloud)**:
   ```ini
   SUPABASE_URL=https://your-project-id.supabase.co
   SUPABASE_KEY=your_supabase_anon_public_key_here
   ```
5. Click **🧪 Test Supabase Connection** in the sidebar to verify!

---

## 📂 Project Structure

```
chatbot/
├── .env                      # API keys & model configuration
├── .env.example              # Template configuration
├── .gitignore                # Git ignore configuration
├── config.py                 # Configuration loader & system prompts
├── bot.py                    # Core Gemini engine with tools & fallback
├── app.py                    # Streamlit Web Frontend with Supabase history
├── supabase_db.py            # Supabase PostgreSQL database manager
├── supabase_schema.sql       # Ready-to-run SQL table schemas & RLS policies
├── chat_history/             # Local backup JSON chat files
├── cli.py                    # Interactive terminal chat UI (Rich)
├── demo.py                   # Automated showcase runner
├── requirements.txt          # Dependencies (google-genai, streamlit, supabase, rich)
├── README.md                 # Complete documentation
└── tools/
    ├── __init__.py           # Exports all tools & UI metadata
    ├── automotive.py         # Car & vehicle specs tool
    ├── gadgets.py            # Laptop & smartphone specs tool
    ├── weather.py            # Weather lookup tool
    ├── calculator.py         # Safe math tool
    ├── database.py           # Knowledge base tool
    └── datetime_tool.py      # Timezone & date tool
```

