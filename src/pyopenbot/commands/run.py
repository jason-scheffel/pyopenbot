from pyopenbot.platforms.base_platform import BasePlatform
from pyopenbot.commands.base_command import BaseCommand
from pathlib import Path


class Run(BaseCommand):
    def __init__(self, platform: BasePlatform) -> None:
        self.platform = platform

    def run(self, character_config: Path, openbot_config: Path) -> None:
        self.platform.send_message("running the run command")
