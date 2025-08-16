from pyopenbot.platforms.cli_platform import CLIPlatform
from pyopenbot.commands.base_command import BaseCommand
from pyopenbot.character import Character
from pyopenbot.llm_service import LLMService
from pyopenbot.memory import Memory
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
import sys


class Run(BaseCommand):
    def __init__(self) -> None:
        self.cli_platform = CLIPlatform()
        self.console = Console()

    def run(self, character_config: Path) -> None:
        try:
            character = Character.from_yaml(character_config)
        except FileNotFoundError as e:
            self.console.print(f"[red]Error: {e}[/red]")
            return
        except Exception as e:
            self.console.print(f"[red]Error loading config: {e}[/red]")
            return
        
        llm_service = LLMService(character)
        memory = Memory(
            type=character.memory_type,
            max_context=character.settings.get("context_window", 8192)
        )
        
        self.console.print(Panel(
            f"[bold cyan]🤖 PyOpenBot v0.3.0 - {character.platform.title()}[/bold cyan]\n"
            f"Character: {character.character_name}\n"
            f"Model: {character.llm_model} via {character.llm_provider.title()}\n"
            f"Memory: {character.memory_type.title()}\n"
            f"Commands: /help /quit /clear /system /stats",
            title="PyOpenBot Started"
        ))
        
        self.conversation_loop(character, llm_service, memory)
    
    def conversation_loop(self, character, llm_service, memory):
        while True:
            try:
                user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]")
                
                if user_input.startswith("/"):
                    if not self.handle_command(user_input, character, memory):
                        break
                    continue
                
                memory.add_message("user", user_input)
                
                try:
                    self.console.print("\n[dim]Thinking...[/dim]", end="\r")
                    response = llm_service.get_response(user_input, memory.get_messages())
                    self.console.print(" " * 20, end="\r")  # Clear "Thinking..."
                    
                    memory.add_message("assistant", response)
                    
                    self.console.print(Panel(
                        response,
                        title=f"[bold green]{character.character_name}[/bold green]",
                        border_style="green"
                    ))
                    
                except Exception as e:
                    self.console.print(" " * 20, end="\r")  # Clear "Thinking..."
                    error_msg = str(e)
                    if "no providers" in error_msg.lower():
                        self.console.print("[red]Error: No providers available that comply with privacy requirements[/red]")
                    elif "api" in error_msg.lower() and "key" in error_msg.lower():
                        self.console.print("[red]Error: Invalid API key[/red]")
                    else:
                        self.console.print(f"[red]Error: {error_msg}[/red]")
                        
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Use /quit to exit[/yellow]")
                continue
            except EOFError:
                break
    
    def handle_command(self, command: str, character, memory) -> bool:
        cmd = command.lower().strip()
        
        if cmd in ["/quit", "/exit"]:
            self.console.print("[yellow]Goodbye![/yellow]")
            return False
        
        elif cmd == "/clear":
            memory.clear()
            self.console.print("[green]Conversation cleared[/green]")
        
        elif cmd == "/system":
            self.console.print(Panel(
                character.character_card,
                title="[bold]System Prompt[/bold]",
                border_style="blue"
            ))
        
        elif cmd == "/stats":
            stats = memory.get_stats()
            table = Table(title="Session Statistics")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")
            
            table.add_row("Messages", str(stats["message_count"]))
            table.add_row("Tokens", str(stats["token_count"]))
            table.add_row("Context Usage", stats["context_usage"])
            table.add_row("Context %", f"{stats['context_percentage']:.1f}%")
            
            self.console.print(table)
        
        elif cmd == "/help":
            help_text = """
[bold]Available Commands:[/bold]
  /help    - Show this help message
  /quit    - Exit the bot
  /clear   - Clear conversation history
  /system  - Show system prompt
  /stats   - Show session statistics
            """
            self.console.print(Panel(help_text.strip(), title="[bold]Help[/bold]"))
        
        else:
            self.console.print(f"[red]Unknown command: {command}[/red]")
        
        return True
