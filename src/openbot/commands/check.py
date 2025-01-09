from openbot.platforms.base_platform import BasePlatform
from openbot.commands.base_command import BaseCommand

from pathlib import Path
from typing import List


class Check(BaseCommand):
    def __init__(self, platform: BasePlatform) -> None:
        self.platform = platform

    def run(
        self,
        character_config: Path,
        openbot_config: Path,
    ) -> None:
        messages: List[str] = []

        if character_config.exists():
            messages.append(f"character config {character_config} exists")
        else:
            messages.append(
                f"character config {character_config} does not exist"
            )

        if openbot_config.exists():
            messages.append(f"openbot config {openbot_config} exists")
        else:
            messages.append(f"openbot config {openbot_config} does not exist")

        for message in messages:
            self.platform.send_message(message)
