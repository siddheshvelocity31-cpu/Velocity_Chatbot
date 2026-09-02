from bot import GeminiChatbot
bot = GeminiChatbot()

tests = [
    ("i want to buy a house", False),
    ("i need to buy an iphone", False),
    ("i want to buy a car", True),
    ("suggest me a family car", True),
    ("i want to buy a laptop", False),
]

for query, expect_car in tests:
    bot.conversation_history.clear()
    bot.tool_call_history.clear()
    r = bot.send_message(query)
    has_car = any(w in r.lower() for w in ["porsche", "tesla", "ferrari", "bmw", "sedan", "suv", "hatchback", "electric car"])
    status = "PASS" if has_car == expect_car else "FAIL"
    print(f"[{status}] \"{query}\" -> car shown={has_car} (expected={expect_car})")
