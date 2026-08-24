"""Interactive Rich CLI for the Gemini Tool-Calling Chatbot."""

import sys
import json

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
from rich.table import Table
from rich.prompt import Prompt
from rich.text import Text
from rich import box

from bot import GeminiChatbot
import config

console = Console(force_terminal=True, legacy_windows=False)


def display_welcome_banner(bot: GeminiChatbot):
    """Display startup header and available tools."""
    banner_text = Text()
    banner_text.append("Google Gemini Tool-Calling Chatbot\n", style="bold cyan")
    mode_str = f"Live ({bot.model})" if bot.is_live_mode() else "Smart Local Mode"
    banner_text.append(f"Status: {mode_str} | SDK: google-genai 2.x\n", style="dim")
    banner_text.append("Type your question below, or use /tools, /reset, /exit.", style="italic green")

    console.print(Panel(banner_text, title="Welcome", border_style="cyan", box=box.ROUNDED))

    table = Table(title="Registered Tools", show_header=True, header_style="bold magenta", box=box.SIMPLE)
    table.add_column("Icon", justify="center", width=6)
    table.add_column("Function Name", style="bold yellow", width=26)
    table.add_column("Description", style="white")

    for tool in bot.get_tool_list():
        table.add_row(tool["icon"], tool["name"], tool["description"])

    console.print(table)
    console.print()


def on_tool_call(tool_name: str, args: dict):
    """Callback when Gemini decides to invoke a tool."""
    args_json = json.dumps(args, indent=2)
    console.print(
        Panel(
            f"[bold yellow]Tool:[/bold yellow] [cyan]{tool_name}[/cyan]\n"
            f"[bold yellow]Arguments:[/bold yellow]\n[dim]{args_json}[/dim]",
            title="[Tool Call] Gemini Invoking Tool",
            border_style="yellow",
            box=box.ROUNDED,
        )
    )


def on_tool_result(tool_name: str, result: any):
    """Callback when the tool finishes execution."""
    result_str = json.dumps(result, indent=2) if isinstance(result, (dict, list)) else str(result)
    console.print(
        Panel(
            f"[bold green]Tool Result ({tool_name}):[/bold green]\n"
            f"[dim]{result_str}[/dim]",
            title="[Tool Result] Output Sent to Gemini",
            border_style="green",
            box=box.ROUNDED,
        )
    )
    console.print()


def main():
    """Main interactive chat loop."""
    chatbot = GeminiChatbot(
        on_tool_call=on_tool_call,
        on_tool_result=on_tool_result,
    )

    display_welcome_banner(chatbot)

    while True:
        try:
            user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]").strip()

            if not user_input:
                continue

            if user_input.lower() in ("/exit", "/quit", "exit", "quit"):
                console.print("[italic yellow]Goodbye![/italic yellow]")
                break

            elif user_input.lower() == "/reset":
                chatbot.reset_chat()
                console.print("[italic green]Conversation history reset.[/italic green]")
                continue

            elif user_input.lower() == "/tools":
                tools = chatbot.get_tool_list()
                table = Table(title="Available Tools", show_header=True, header_style="bold magenta", box=box.SIMPLE)
                table.add_column("Icon", justify="center", width=6)
                table.add_column("Function Name", style="bold yellow", width=26)
                table.add_column("Description", style="white")
                for tool in tools:
                    table.add_row(tool["icon"], tool["name"], tool["description"])
                console.print(table)
                continue

            elif user_input.lower() == "/help":
                console.print(
                    Panel(
                        "Commands:\n"
                        "  [bold cyan]/tools[/bold cyan]  - List registered tools\n"
                        "  [bold cyan]/reset[/bold cyan]  - Clear conversation session\n"
                        "  [bold cyan]/help[/bold cyan]   - Show this help menu\n"
                        "  [bold cyan]/exit[/bold cyan]   - Exit the chatbot\n\n"
                        "Example queries to test tool calling:\n"
                        "  - 'What is the weather in Tokyo and London?'\n"
                        "  - 'Can you calculate (1500 * 0.18) + (250 / 5) - sqrt(81)?'\n"
                        "  - 'What is our 30-day return policy and laptop price?'\n"
                        "  - 'What is the current time in Tokyo and London?'\n"
                        "  - 'What is the weather in London right now, and what time is it there?'",
                        title="Help & Example Prompts",
                        border_style="cyan",
                        box=box.ROUNDED,
                    )
                )
                continue

            with console.status("[bold green]Processing and selecting tools...[/bold green]", spinner="dots"):
                response_text = chatbot.send_message(user_input)

            console.print(
                Panel(
                    Markdown(response_text),
                    title="Gemini",
                    border_style="blue",
                    box=box.ROUNDED,
                )
            )

        except KeyboardInterrupt:
            console.print("\n[italic yellow]Session ended.[/italic yellow]")
            break
        except Exception as e:
            console.print(f"[bold red]Unexpected error:[/bold red] {e}")


if __name__ == "__main__":
    main()
