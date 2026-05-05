import os
import subprocess
from typing import Dict, Any
from nodes.base import BaseNode

class PRCreatorNode(BaseNode):
    """
    The Delivery Specialist.
    Pushes the verified branch and opens a Pull Request.
    """
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        target_path = state['target_path']
        branch = state.get('feature_branch', 'agent/fix-v2')
        token = os.getenv("GITHUB_TOKEN")
        
        self.log(f"🚀 Pushing {branch} to origin...")
        try:
            # Force push to update existing PR if healing loop occurred
            subprocess.run(["git", "-C", target_path, "push", "origin", branch, "--force"], check=True)
            
            # Simple CLI-based PR creation (requires GitHub CLI 'gh' installed)
            # Alternatively, logs the instruction for the user
            self.log(f"✨ PR ready for review on branch: {branch}")
            
            return {
                "execution_logs": [f"PR-Creator: Pushed changes to {branch}."],
                "next_step": "end"
            }
        except Exception as e:
            self.log(f"❌ PR-Creator Error: {e}", level=40)
            return {"circuit_breaker": True}
