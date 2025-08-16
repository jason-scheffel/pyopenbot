from pyopenbot.platforms.cli_platform import CLIPlatform
from pyopenbot.commands.base_command import BaseCommand
from pyopenbot.character import Character
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table


class Check(BaseCommand):
    def __init__(self) -> None:
        self.cli_platform = CLIPlatform()
        self.console = Console()

    def run(self, character_config: Path) -> None:
        table = Table(title=f"Configuration Check: {character_config.name}")
        table.add_column("Check", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Details")
        
        has_errors = False
        
        if not character_config.exists():
            table.add_row(
                "File exists",
                "❌",
                f"[red]File {character_config} not found[/red]"
            )
            self.console.print(table)
            return
        
        table.add_row("File exists", "✅", str(character_config))
        
        try:
            character = Character.from_yaml(character_config)
            table.add_row("Valid YAML", "✅", "Successfully parsed")
            
            # Validate required fields
            if character.character_name:
                table.add_row("Character name", "✅", character.character_name)
            else:
                table.add_row("Character name", "❌", "[red]Missing[/red]")
                has_errors = True
            
            if character.character_card:
                table.add_row("Character card", "✅", f"{len(character.character_card)} chars")
            else:
                table.add_row("Character card", "❌", "[red]Missing system prompt[/red]")
                has_errors = True
            
            if character.platform in ["terminal", "discord"]:
                table.add_row("Platform", "✅", character.platform)
            else:
                table.add_row("Platform", "❌", f"[red]Invalid: {character.platform}[/red]")
                has_errors = True
            
            if character.llm_provider:
                table.add_row("Provider", "✅", character.llm_provider)
            else:
                table.add_row("Provider", "❌", "[red]Missing[/red]")
                has_errors = True
            
            if character.llm_model:
                table.add_row("Model", "✅", character.llm_model)
            else:
                table.add_row("Model", "❌", "[red]Missing[/red]")
                has_errors = True
            
            if character.api_key:
                table.add_row("API key", "✅", "Configured")
            else:
                table.add_row("API key", "❌", "[red]Not configured[/red]")
                has_errors = True
            
            # Validate settings
            required_settings = ["temperature", "top_p", "max_tokens", "context_window"]
            for setting in required_settings:
                if setting in character.settings:
                    table.add_row(setting.replace("_", " ").title(), "✅", str(character.settings[setting]))
                else:
                    table.add_row(setting.replace("_", " ").title(), "❌", "[red]Missing[/red]")
                    has_errors = True
            
            if character.memory_type:
                table.add_row("Memory", "✅", character.memory_type)
            else:
                table.add_row("Memory", "❌", "[red]Missing[/red]")
                has_errors = True
            
            self.console.print(table)
            
            if has_errors:
                self.console.print(Panel(
                    "[bold red]❌ Configuration has errors[/bold red]",
                    title="Status"
                ))
            else:
                self.console.print(Panel(
                    "[bold green]🎉 Ready to run![/bold green]",
                    title="Status"
                ))
            
        except Exception as e:
            table.add_row("Valid config", "❌", f"[red]{str(e)}[/red]")
            self.console.print(table)
