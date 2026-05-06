import os
import subprocess
from nodes.base import BaseNode

class ClonerNode(BaseNode):
    def execute(self, state: dict):
        repo_url = state.get('repo_url')
        target = state.get('target_path')

        if not repo_url:
            self.log("❌ REPO_URL missing from .env", level=40)
            return {"circuit_breaker": True}

        # 1. Prepare Parent Dir
        os.makedirs(os.path.dirname(target), exist_ok=True)

        # 2. Clone or Pull
        if not os.path.exists(os.path.join(target, ".git")):
            self.log(f"🚚 Cloning {repo_url}...")
            subprocess.run(["git", "clone", repo_url, target], check=True)
        else:
            self.log("📂 Repo exists. Syncing latest...")
            subprocess.run(["git", "fetch", "--all"], cwd=target, check=True)
            subprocess.run(["git", "reset", "--hard", "origin/main"], cwd=target, check=True)

        return {"next_step": "monitor"}
