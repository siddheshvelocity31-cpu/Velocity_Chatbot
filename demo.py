"""Automated demonstration script for Gemini API Tool Calling."""

import sys
import time

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from bot import GeminiChatbot
from cli import on_tool_call, on_tool_result

console = Console(force_terminal=True, legacy_windows=False)

DEMO_PROMPTS = [
    {
        "title": "Scenario 1: Single Tool Calling (Weather Lookup)",
        "prompt": "What is the current weather condition and temperature in Tokyo?",
        "expected_tool": "get_current_weather"
    },
    {
        "title": "Scenario 2: Mathematical Evaluation Tool",
        "prompt": "Calculate (1500 * 0.18) + (250 / 5) - sqrt(81)",
        "expected_tool": "calculate_expression"
    },
    {
        "title": "Scenario 3: Knowledge Base Search",
        "prompt": "What are the key specifications and price of the QuantumPro Ultra Laptop?",
        "expected_tool": "search_knowledge_base"
    },
    {
        "title": "Scenario 4: Multi-Tool Execution (Weather + Timezone + Math in one prompt)",
        "prompt": "What is the weather in London right now, what time is it in London, and if an umbrella costs £25 with a 20% discount, what will I pay?",
        "expected_tool": "Multiple tools: get_current_weather, get_current_time, calculate_expression"
    },
    {
        "title": "Scenario 5: No Tool Needed (Standard LLM Reasoning)",
        "prompt": "Explain the difference between supervised and unsupervised machine learning in 2 bullet points.",
        "expected_tool": "None (Gemini recognizes tools are not required)"
    }
]


def run_demo():
    """Run all automated test cases."""
    console.print(
        Panel.fit(
            "[bold cyan]Google Gemini Tool-Calling Automated Demo[/bold cyan]\n"
            "[dim]Showcasing Tool Selection, Execution Loop, and Response Synthesis[/dim]",
            border_style="cyan"
        )
    )

    chatbot = GeminiChatbot(
        on_tool_call=on_tool_call,
        on_tool_result=on_tool_result,
    )

    if chatbot.is_live_mode():
        console.print(f"[bold green]🟢 Live Mode Active[/bold green] - Using model: [cyan]{chatbot.model}[/cyan]\n")
    else:
        console.print(
            Panel(
                "[bold yellow]🟡 Running in Smart Local Mode[/bold yellow]\n"
                "To connect to live Gemini API, add your key to `.env`:\n"
                "[dim]GEMINI_API_KEY=your_api_key_here[/dim]",
                border_style="yellow"
            )
        )

    for i, test_case in enumerate(DEMO_PROMPTS, 1):
        console.print(f"\n[bold magenta]========================================================================[/bold magenta]")
        console.print(f"[bold magenta]▶ {test_case['title']}[/bold magenta]")
        console.print(f"[dim]Expected tool: {test_case['expected_tool']}[/dim]")
        console.print(f"[bold cyan]User:[/bold cyan] {test_case['prompt']}\n")

        with console.status("[bold green]Gemini is evaluating tools and responding...[/bold green]", spinner="dots"):
            response = chatbot.send_message(test_case["prompt"])

        console.print(
            Panel(
                Markdown(response),
                title="Gemini Response",
                border_style="blue"
            )
        )
        time.sleep(0.3)

    console.print("\n[bold green]All demo scenarios completed successfully![/bold green]")


if __name__ == "__main__":
    run_demo()
