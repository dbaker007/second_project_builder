import os
import subprocess
from nodes.base import BaseNode
from typing import Dict, Any

class DiscoveryNode(BaseNode):
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        target = state['target_path']
        branch = state.get('feature_branch', 'main')
        
        # 1. PHYSICAL SWITCH: Move to the branch we are actually working on
        try:
            subprocess.run(["git", "-C", target, "checkout", branch], capture_output=True)
        except Exception:
            pass # Fallback to main if branch doesn't exist yet (first turn)

        # 2. Detect DNA from actual files on that branch
        has_uv = os.path.exists(os.path.join(target, "pyproject.toml"))
        has_py = any(f.endswith('.py') for r, d, files in os.walk(target) for f in files)
        
        context = {
            "language": "python" if has_py or has_uv else "unknown",
            "manager": "uv" if has_uv else "pip",
            "test_runner": "pytest" if os.path.exists(os.path.join(target, "tests")) else "unittest"
        }

        self.log(f"🧬 DNA Detected on {branch}: {context['language']} via {context['manager']}")
        return {
            "env_context": context,
            "execution_logs": [f"Discovery: Found {context['language']} on {branch}."],
            "next_step": "architect"
        }
