import os
import subprocess
from nodes.base import BaseNode


class ClonerNode(BaseNode):
    def execute(self, state: dict):
        target = state["target_path"]
        repo_url = state["repo_url"]

        # 1. Sync Logic
        if not os.path.exists(target):
            self.log(f"🚚 Cloning {repo_url}...")
            subprocess.run(["git", "clone", repo_url, target], check=True)
        else:
            self.log("📂 Repo exists. Syncing latest...")
            subprocess.run(["git", "fetch", "origin"], cwd=target, check=True)
            subprocess.run(
                ["git", "reset", "--hard", "origin/main"], cwd=target, check=True
            )

        # 🛡️ Sentinel Safety .gitignore
        # Added .sentinel_watermark and .sentinel_success to prevent tracking
        gitignore_path = os.path.join(target, ".gitignore")
        safety_lines = [
            ".aider*",
            "workspaces/",
            "targets/",
            "*.db",
            "__pycache__/",
            ".env*",
            ".venv/",
            ".sentinel_watermark",
            ".sentinel_success",
        ]

        if not os.path.exists(gitignore_path):
            self.log("🛡️ Creating new minimalist .gitignore.")
            with open(gitignore_path, "w") as f:
                f.write("\n".join(safety_lines) + "\n")
        else:
            self.log("📂 Existing .gitignore found. Syncing safety lines...")
            with open(gitignore_path, "r") as f:
                existing_content = f.read().splitlines()

            to_add = [line for line in safety_lines if line not in existing_content]
            if to_add:
                self.log(f"➕ Adding missing safety lines: {to_add}")
                with open(gitignore_path, "a") as f:
                    # Ensure we start on a new line
                    f.write("\n# Sentinel State Markers\n" + "\n".join(to_add) + "\n")

        return {"next_step": "scaffolder"}
