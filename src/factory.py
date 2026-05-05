import os
import logging
from typing import Any

logger = logging.getLogger("sentinel.factory")

class NodeFactory:
    """
    Dependency Injection layer to manage node instantiation.
    Ensures AGENT_MOCK_MODE is respected across the graph.
    """
    
    @staticmethod
    def get_node(node_type: str) -> Any:
        is_mock = os.getenv("AGENT_MOCK_MODE", "false").lower() == "true"
        
        # In a real run, we would import the actual node classes here.
        # For now, we map to placeholders until those files are populated.
        
        if is_mock:
            logger.info(f"🧪 Factory: Returning MOCK implementation for '{node_type}'")
            return MockNode(node_type)
        
        # Once specialists are coded, we will import and return them here.
        # from nodes.init import InitNode
        # if node_type == "init": return InitNode()
        
        logger.warning(f"⚠️ Factory: Real node for '{node_type}' not yet implemented. Falling back to Mock.")
        return MockNode(node_type)

class MockNode:
    """A generic fallback node that logs its execution without calling APIs."""
    def __init__(self, node_name: str):
        self.node_name = node_name
        self.logger = logging.getLogger(f"agent.mock.{node_name}")

    def __call__(self, state: dict) -> dict:
        self.logger.info(f"▶ MOCK START: {self.node_name}")
        # Simulated state update
        return {
            "execution_logs": [f"MockNode: Successfully simulated {self.node_name}"],
            "next_step": "next" 
        }

