from abc import ABC, abstractmethod


class BasePlatform(ABC):
    @abstractmethod
    def send_message(self, message: str) -> None:
        pass
