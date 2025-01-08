from ..platforms.base_platform import BasePlatform
from .base_command import BaseCommand

class Check(BaseCommand):
    def __init__(self, platform: BasePlatform) -> None:
        self.platform = platform

    def run(self) -> None:
        self.platform.send_message("running the check command")
