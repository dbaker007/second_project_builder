import os
import logging
from typing import Any

# Node Imports
from nodes.cloner import ClonerNode
from nodes.monitor import MonitorNode
from nodes.planner import PlannerNode
from nodes.coder import CoderNode
from nodes.reviewer import ReviewerNode
from nodes.environment import EnvironmentNode
from nodes.qa import QANode
from nodes.pusher import PusherNode
from nodes.reporter import ReporterNode
from nodes.scaffold import ScaffoldNode

logger = logging.getLogger("sentinel.factory")

class MockNode:
    def __init__(self, node_name: str):
        self.node_name = node_name
        self.logger = logging.getLogger(f"agent.mock.{node_name}")

    def __call__(self, state: dict) -> dict:
        self.logger.info(f"🧪 MOCK START: {self.node_name}")
        
        # Updated routes to match the new professional pipeline
        routes = {
            "planner": "coder",
            "coder": "reviewer",
            "reviewer": "environment",
            "environment": "qa",
            "qa": "pusher",
            "pusher": "reporter",
            "reporter": "end"
        }
        
        return {
            "execution_logs": [f"Mock: Simulated {self.node_name}"],
            "next_step": routes.get(self.node_name, "end"),
            "qa_passed": True,
            "requirements_fulfilled": self.node_name == "pusher"
        }

class NodeFactory:
    @staticmethod
    def get_node(node_type: str) -> Any:
        is_mock = os.getenv("AGENT_MOCK_MODE", "false").lower() == "true"
        
        node_map = {
            "cloner": ClonerNode,
            "scaffolder": ScaffoldNode,
            "monitor": MonitorNode,
            "planner": PlannerNode,
            "coder": CoderNode,
            "reviewer": ReviewerNode,
            "environment": EnvironmentNode,
            "qa": QANode,
            "pusher": PusherNode,
            "reporter": ReporterNode
        }
        
        node_class = node_map.get(node_type)
        if not node_class:
            raise ValueError(f"❌ Factory Error: Node type '{node_type}' not found.")

        # Environmental nodes always stay real to maintain project state
        if node_type in ["cloner", "scaffolder", "monitor", "reporter"]:
            return node_class()

        if is_mock:
            return MockNode(node_type)
            
        return node_class()
