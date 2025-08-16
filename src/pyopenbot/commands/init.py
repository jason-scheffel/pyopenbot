from pyopenbot.platforms.cli_platform import CLIPlatform
from pyopenbot.commands.base_command import BaseCommand
from pyopenbot.character import Character
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt, FloatPrompt, Confirm
from rich.table import Table
from typing import Dict, Any


class Init(BaseCommand):
    def __init__(self) -> None:
        self.cli_platform = CLIPlatform()
        self.console = Console()

    def run(self) -> None:
        """
        Setup the config for a character
        """
        self.console.print(Panel(
            "[bold cyan]🤖 PyOpenBot Setup Wizard[/bold cyan]",
            title="Welcome"
        ))
        
        self.console.print("\n[bold]📝 Character Setup[/bold]")
        self.console.print("─" * 40)
        
        character_name = Prompt.ask("Character name", default="Assistant")
        
        self.console.print("\n[bold]📖 Create System Prompt[/bold]")
        self.console.print("─" * 40)
        self.console.print("Enter the system prompt (this defines your bot's behavior):")
        self.console.print("[dim]Press Enter twice when done[/dim]\n")
        
        character_card_lines = []
        while True:
            line = input()
            if line == "" and character_card_lines and character_card_lines[-1] == "":
                character_card_lines.pop()  # Remove last empty line
                break
            character_card_lines.append(line)
        
        character_card = "\n".join(character_card_lines)
        if not character_card:
            character_card = "You are a helpful AI assistant. Be concise and friendly."
        
        self.console.print("\n[bold]🌐 Platform Selection[/bold]")
        self.console.print("─" * 40)
        platform = Prompt.ask(
            "Select platform",
            choices=["terminal", "discord"],
            default="terminal"
        )
        
        self.console.print("\n[bold]🤖 LLM Configuration[/bold]")
        self.console.print("─" * 40)
        
        provider = "openrouter"
        self.console.print(f"Provider: [cyan]{provider}[/cyan]")
        
        table = Table(title="Available Models")
        table.add_column("Model", style="cyan")
        table.add_column("Context", style="green")
        table.add_column("Description")
        table.add_row("z-ai/glm-4.5", "8K", "Fast and cost-effective")
        table.add_row("microsoft/mai-ds-r1:free", "8K", "Free model (trains on data)")
        self.console.print(table)
        
        model = Prompt.ask(
            "Select model",
            choices=["z-ai/glm-4.5", "microsoft/mai-ds-r1:free"],
            default="z-ai/glm-4.5"
        )
        
        self.console.print("\n[bold]🔑 API Configuration[/bold]")
        self.console.print("─" * 40)
        
        use_file = Confirm.ask("Read API key from file?", default=False)
        
        if use_file:
            api_key_file = Prompt.ask("API key file path")
            api_key_config = {"api_key_file": api_key_file}
        else:
            api_key = Prompt.ask("Enter OpenRouter API key", password=True)
            api_key_config = {"api_key": api_key}
        
        self.console.print("\n[bold]⚙️ Model Settings[/bold]")
        self.console.print("─" * 40)
        
        temperature = FloatPrompt.ask("Temperature (0.0-2.0)", default=0.7)
        top_p = FloatPrompt.ask("Top-p (0.0-1.0)", default=0.9)
        max_tokens = IntPrompt.ask("Max response tokens", default=2000)
        context_window = IntPrompt.ask("Context window size", default=8192)
        
        settings = {
            "temperature": temperature,
            "top_p": top_p,
            "max_tokens": max_tokens,
            "context_window": context_window,
            "presence_penalty": 0.0,
            "frequency_penalty": 0.0
        }
        
        self.console.print("\n[bold]🧠 Memory Configuration[/bold]")
        self.console.print("─" * 40)
        
        memory_type = Prompt.ask(
            "Memory type",
            choices=["unlimited"],
            default="unlimited"
        )
        
        self.console.print("\n[bold]💾 Save Configuration[/bold]")
        self.console.print("─" * 40)
        
        filename = Prompt.ask(
            "Save as",
            default=f"{character_name.lower().replace(' ', '_')}.yaml"
        )
        
        config_path = Path(filename)
        
        config = {
            "character_name": character_name,
            "character_card": character_card,
            "platform": platform,
            "llm": {
                "provider": provider,
                "model": model,
                **api_key_config,
                "settings": settings
            },
            "memory": {
                "type": memory_type
            }
        }
        
        if use_file:
            character = Character(
                character_name=character_name,
                character_card=character_card,
                platform=platform,
                llm_provider=provider,
                llm_model=model,
                api_key="",
                settings=settings,
                memory_type=memory_type
            )

            character._api_key_source = f"file:{api_key_file}"
        else:
            character = Character(
                character_name=character_name,
                character_card=character_card,
                platform=platform,
                llm_provider=provider,
                llm_model=model,
                api_key=api_key,
                settings=settings,
                memory_type=memory_type
            )
            character._api_key_source = "direct"
        
        character.save_to_yaml(config_path)
        
        self.console.print(Panel(
            f"[bold green]✅ Setup Complete![/bold green]\n\n"
            f"Created: {config_path}\n"
            f"Platform: {platform}\n"
            f"Model: {model}\n"
            f"Memory: {memory_type}\n\n"
            f"Run with: [cyan]pyopenbot run {config_path}[/cyan]",
            title="Success"
        ))
