from openbot.platforms.base_platform import BasePlatform
from openbot.commands.base_command import BaseCommand

from pathlib import Path


class Check(BaseCommand):
    def __init__(self, platform: BasePlatform) -> None:
        self.platform = platform

    def run(
        self,
        character_config: Path,
        openbot_config: Path,
    ) -> None:
        if character_config.exists() and openbot_config.exists():
            self.platform.send_message(
                f"character config {character_config} and openbot config {openbot_config} exist"
            )
        else:
            if not character_config.exists():
                self.platform.send_message(
                    f"character config {character_config} does not exist"
                )
            if not openbot_config.exists():
                self.platform.send_message(
                    f"openbot config {openbot_config} does not exist"
                )
