from ABC import ABC, abstractmethod


class BaseCommand(ABC):
    @abstractmethod
    def run(self) -> None:
        pass
