import os
import subprocess
from gitingest import ingest
from nodes.base import BaseNode
from typing import Dict, Any

class InitNode(BaseNode):
    """
    Handles workspace synchronization and high-signal codebase ingestion.
    Utilizes Git as the absolute watermark.
    """
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        target_path = state['target_path']
        repo_url = state['repo_url']
        
        # 1. Ensure Target Directory Exists
        os.makedirs(target_path, exist_ok=True)
        
        # 2. Sync Logic: Aggressive Reset to origin/main (The Watermark)
        if not os.path.exists(os.path.join(target_path, ".git")):
            self.log(f"🚚 Initializing fresh clone of {repo_url}...")
            subprocess.run(["git", "clone", repo_url, target_path], check=True, capture_output=True)
        else:
            self.log("🔄 Synchronizing with remote main...")
            # Fetch remote state without merging
            subprocess.run(["git", "-C", target_path, "fetch", "origin", "main"], check=True)
            # Hard reset to ensure we are exactly at origin/main baseline
            subprocess.run(["git", "-C", target_path, "reset", "--hard", "origin/main"], check=True)
            # Clean any leftovers from previous failed agent runs
            subprocess.run(["git", "-C", target_path, "clean", "-fd"], check=True)

        # 3. Captured Surgical Delta (Requirements.md)
        # We diff the local (what you changed) vs origin/main (the truth)
        diff_cmd = ["git", "-C", target_path, "diff", "origin/main", "HEAD", "--", "requirements.md"]
        delta_result = subprocess.run(diff_cmd, capture_output=True, text=True)
        requirements_delta = delta_result.stdout.strip()
        
        # 4. Surgical Ingestion: Skip the noise
        self.log("📊 Ingesting codebase (filtering via .gitingestignore)...")
        # ingest() automatically respects .gitingestignore in the target_path
        summary_stats, tree, content = ingest(target_path)
        
        # 5. Telemetry
        char_count = len(content)
        self.log(f"📈 Ingested {char_count} chars (~{char_count // 4} tokens)")

        return {
            "requirements_delta": requirements_delta,
            "codebase_summary": content,
            "execution_logs": [f"Init: Workspace synced. Delta size: {len(requirements_delta)} chars."],
            "next_step": "discovery"
        }
