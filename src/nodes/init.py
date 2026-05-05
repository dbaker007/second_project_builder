import os
import shutil
import subprocess
from gitingest import ingest
from nodes.base import BaseNode
from typing import Dict, Any

class InitNode(BaseNode):
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        target = state['target_path']
        repo_url = state['repo_url']
        
        # 1. THE NUKE: Total directory deletion
        if os.path.exists(target):
            self.log(f"🧹 Nuking {target} for a fresh start...")
            shutil.rmtree(target)
        
        # 2. THE FRESH START: Re-clone from origin
        self.log(f"🚚 Fresh clone from {repo_url}...")
        os.makedirs(os.path.dirname(target), exist_ok=True)
        subprocess.run(["git", "clone", repo_url, target], check=True, capture_output=True)

        # 3. Capture Requirements Delta
        # In a fresh clone, we compare against origin/main
        diff_cmd = ["git", "-C", target, "diff", "HEAD", "HEAD", "--", "requirements.md"] 
        # Note: In a fresh clone, local requirements.md is our baseline.
        # We read the file content directly for the prompt.
        req_path = os.path.join(target, "requirements.md")
        requirements_content = ""
        if os.path.exists(req_path):
            with open(req_path, "r") as f:
                requirements_content = f.read()

        # 4. Ingest Clean State
        _, _, content = ingest(target)
        
        return {
            "requirements_delta": requirements_content or "INITIAL_BUILD_REQUIRED",
            "codebase_summary": content,
            "execution_logs": ["Init: Workspace nuked and fresh clone established."],
            "next_step": "discovery"
        }
