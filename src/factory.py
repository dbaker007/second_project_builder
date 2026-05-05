import os
import logging
from typing import Any

# Specialist Imports
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
        # 1. Force a clean read of the env
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
        
        node_class = node_map.get(node_type)
        
        if not node_class:
            raise ValueError(f"❌ Factory Error: Node type '{node_type}' not found in map.")

        # 2. Return REAL node if Mock Mode is off
        if not is_mock:
            return node_class()
            
        # 3. If Mock Mode is ON, only Init/Discovery stay real
        if node_type in ["init", "discovery"]:
            return node_class()
            
        logger.info(f"🧪 Factory: Returning MOCK implementation for '{node_type}'")
        return MockNode(node_type)

class MockNode:
    """Standard V2 Mock Routing"""
    def __init__(self, node_name: str):
        self.node_name = node_name
        self.logger = logging.getLogger(f"agent.mock.{node_name}")

    def __call__(self, state: dict) -> dict:
        self.logger.info(f"▶ MOCK START: {self.node_name}")
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
