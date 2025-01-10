from pyopenbot.platforms.cli_platform import CLIPlatform
from pyopenbot.commands.base_command import BaseCommand
from pathlib import Path


class Run(BaseCommand):
    def __init__(self) -> None:
        self.cli_platform = CLIPlatform()

    def run(self, character_config: Path, openbot_config: Path) -> None:
        self.platform.send_message("running the run command")
