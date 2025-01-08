from .base_platform import BasePlatform


class CLIPlatform(BasePlatform):
    def send_message(self, message: str) -> None:
        print(message)
