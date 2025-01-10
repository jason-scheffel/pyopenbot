from pyopenbot.platforms.cli_platform import CLIPlatform
from pyopenbot.commands.base_command import BaseCommand
from pyopenbot.pyopenbot_config import PyOpenBotConfig
from pyopenbot.character import Character
from pathlib import Path


class Run(BaseCommand):
    def __init__(self) -> None:
        self.cli_platform = CLIPlatform()

    def run(self, character_config: Path, openbot_config: Path) -> None:
        self.cli_platform.send_message("running the run command")

        pyopenbot_config = PyOpenBotConfig.from_yaml(openbot_config)
        character = Character.from_yaml(character_config)
