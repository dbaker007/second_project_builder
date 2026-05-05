import os
import logging
from typing import Any

# Import Specialists
from nodes.init import InitNode
from nodes.discovery import DiscoveryNode
from nodes.architect import ArchitectNode
from nodes.test_designer import TestDesignerNode
from nodes.coder import CoderNode
from nodes.reviewer import ReviewerNode
from nodes.qa import QANode
from nodes.pr_creator import PRCreatorNode
from nodes.reporter import ReporterNode

logger = logging.getLogger("sentinel.factory")

class NodeFactory:
    @staticmethod
    def get_node(node_type: str) -> Any:
        is_mock = os.getenv("AGENT_MOCK_MODE", "false").lower() == "true"
        
        node_map = {
            "init": InitNode,
            "discovery": DiscoveryNode,
            "architect": ArchitectNode,
            "test_designer": TestDesignerNode,
            "coder": CoderNode,
            "reviewer": ReviewerNode,
            "qa": QANode,
            "pr_creator": PRCreatorNode,
            "reporter": ReporterNode
        }
        
        # KEY LOGIC: Init and Discovery should ALWAYS be real so we can see the repo.
        if is_mock and node_type not in ["init", "discovery"]:
            logger.info(f"🧪 Factory: Returning MOCK for '{node_type}'")
            return MockNode(node_type)
            
        node_class = node_map.get(node_type)
        if not node_class:
            raise ValueError(f"Unknown node type: {node_type}")
            
        return node_class()

class MockNode:
    """A mock node that follows the V2 graph routing."""
    def __init__(self, node_name: str):
        self.node_name = node_name
        self.logger = logging.getLogger(f"agent.mock.{node_name}")

    def __call__(self, state: dict) -> dict:
        self.logger.info(f"▶ MOCK START: {self.node_name}")
        
        # V2 Sequential Routing
        routes = {
            "architect": "test_designer",
            "test_designer": "coder",
            "coder": "reviewer",
            "reviewer": "qa",
            "qa": "pr_creator",
            "pr_creator": "reporter",
            "reporter": "end"
        }
        
        return {
            "execution_logs": [f"Mock: Simulated {self.node_name}"],
            "next_step": routes.get(self.node_name, "end")
        }
