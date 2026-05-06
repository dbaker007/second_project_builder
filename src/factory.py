import os
import logging
from typing import Any

# Node Imports
from nodes.cloner import ClonerNode
from nodes.monitor import MonitorNode
from nodes.planner import PlannerNode
from nodes.coder import CoderNode
from nodes.qa import QANode
from nodes.pusher import PusherNode
from nodes.reporter import ReporterNode

logger = logging.getLogger("sentinel.factory")

class NodeFactory:
    @staticmethod
    def get_node(node_type: str) -> Any:
        is_mock = os.getenv("AGENT_MOCK_MODE", "false").lower() == "true"
        
        node_map = {
            "cloner": ClonerNode,
            "monitor": MonitorNode,
            "planner": PlannerNode,
            "coder": CoderNode,
            "qa": QANode,
            "pusher": PusherNode,
            "reporter": ReporterNode
        }
        
        node_class = node_map.get(node_type)
        if not node_class:
            raise ValueError(f"❌ Factory Error: Node type '{node_type}' not found.")

        if not is_mock:
            return node_class()

        # Monitor and Cloner stay real to handle environmental setup
        if node_type in ["monitor", "cloner"]:
            return node_class()

        logger.info(f"🧪 Factory: Returning MOCK implementation for '{node_type}'")
        return MockNode(node_type)

class MockNode:
    def __init__(self, node_name: str):
        self.node_name = node_name
        self.logger = logging.getLogger(f"agent.mock.{node_name}")

    def __call__(self, state: dict) -> dict:
        self.logger.info(f"▶ MOCK START: {self.node_name}")
        
        routes = {
            "planner": "coder",
            "coder": "qa",
            "qa": "pusher",
            "pusher": "reporter",
            "reporter": "end"
        }
        
        return {
            "execution_logs": [f"Mock: Simulated {self.node_name}"],
            "next_step": routes.get(self.node_name, "end")
        }
