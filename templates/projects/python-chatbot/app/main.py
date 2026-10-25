"""Chatbot main entry point."""

import asyncio

from rich.console import Console
from rich.markdown import Markdown

from app.chat.engine import ChatEngine
from app.config import settings
from app.utils.logging import configure_logging, get_logger

console = Console()
logger = get_logger(__name__)


async def main():
    """Run the chatbot."""
    configure_logging()
    logger.info("chatbot_starting", model=settings.LLM_MODEL)

    console.print("[bold blue]Chatbot[/bold blue]")
    console.print("Type 'quit' or 'exit' to end the conversation.\n")

    engine = ChatEngine()

    while True:
        try:
            user_input = console.input("[bold green]You:[/bold green] ")

            if user_input.lower() in ("quit", "exit"):
                console.print("\n[bold blue]Goodbye![/bold blue]")
                break

            if not user_input.strip():
                continue

            response = await engine.chat(user_input)

            console.print("\n[bold blue]Assistant:[/bold blue]")
            console.print(Markdown(response))
            console.print()

        except KeyboardInterrupt:
            console.print("\n[bold blue]Goodbye![/bold blue]")
            break
        except Exception as e:
            logger.error("chat_error", error=str(e))
            console.print(f"[red]Error: {e}[/red]")


if __name__ == "__main__":
    asyncio.run(main())
