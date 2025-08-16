from pyopenbot.platforms.cli_platform import CLIPlatform
from pyopenbot.commands.base_command import BaseCommand
from pyopenbot.character import Character
from pathlib import Path
from rich.console import Console
from rich.panel import Panel


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
        
        self.console.print(Panel(
            f"[bold cyan]🤖 PyOpenBot v0.3.0 - {character.platform.title()}[/bold cyan]\n"
            f"Character: {character.character_name}\n"
            f"Model: {character.llm_model} via {character.llm_provider.title()}\n"
            f"Memory: {character.memory_type.title()}\n"
            f"Commands: /help /quit /clear /system /stats",
            title="PyOpenBot Started"
        ))
        
        # TODO: Implement conversation loop
        self.console.print("[yellow]not done yet[/yellow]")
