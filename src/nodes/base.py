import time
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseNode(ABC):
    """
    Standardized interface for all Graph Nodes.
    Handles timing, telemetry, and logging automatically.
    """
    def __init__(self):
        self.logger = logging.getLogger(f"agent.{self.__class__.__name__}")

    def log(self, message: str, level: int = logging.INFO):
        self.logger.log(level, message)

    @abstractmethod
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Business logic to be implemented by child nodes."""
        pass

    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        self.log("▶ START")
        start_time = time.time()
        
        try:
            result = self.execute(state)
            elapsed = time.time() - start_time
            self.log(f"⏹ END ({elapsed:.2f}s)")
            return result
        except Exception as e:
            self.logger.exception(f"❌ CRASH in {self.__class__.__name__}")
            return {
                "circuit_breaker": True,
                "execution_logs": [f"Error in {self.__class__.__name__}: {str(e)}"]
            }
