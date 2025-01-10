from pyopenbot.platforms.cli_platform import CLIPlatform
from pyopenbot.commands.base_command import BaseCommand

class Init(BaseCommand):
    def __init__(self) -> None:
        self.cli_platform = CLIPlatform()

    def run(self) -> None:
        self.platform.send_message("running the init command")
