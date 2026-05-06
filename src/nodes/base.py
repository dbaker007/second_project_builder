import logging
from abc import ABC, abstractmethod
from utils.debug import save_snapshot

class BaseNode(ABC):
    def __init__(self):
        self.name = self.__class__.__name__.lower().replace("node", "")
        self.logger = logging.getLogger(f"agent.{self.__class__.__name__}")

    def log(self, message: str, level: int = logging.INFO):
        self.logger.log(level, message)

    @abstractmethod
    def execute(self, state: dict) -> dict:
        pass

    def __call__(self, state: dict) -> dict:
        self.log("▶ START")
        result = self.execute(state)
        
        # Merge result into state to capture the snapshot of the "After"
        new_state = {**state, **result}
        save_snapshot(new_state, self.name)
        
        self.log("⏹ END")
        return result
