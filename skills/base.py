from abc import ABC, abstractmethod

class BaseSkill(ABC):
    name: str = "base"
    description: str = ""
    intents: list = []

    @abstractmethod
    def handle(self, text: str, intent: str, entities: dict) -> str:
        pass

    def can_handle(self, intent: str) -> bool:
        return intent in self.intents
