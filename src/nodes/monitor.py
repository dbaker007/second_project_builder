import os
import hashlib
from nodes.base import BaseNode

class MonitorNode(BaseNode):
    def execute(self, state: dict):
        target = state['target_path']
        repo_url = state.get('repo_url', 'default')
        
        # 📂 Orchestrator Local Memory (NOT in target_path)
        repo_id = hashlib.md5(repo_url.encode()).hexdigest()[:12]
        watermark_dir = os.path.abspath("workspaces/watermarks")
        os.makedirs(watermark_dir, exist_ok=True)
        watermark_file = os.path.join(watermark_dir, f"{repo_id}.mtime")
        
        req_file = os.path.join(target, "requirements.md")
        
        if not os.path.exists(req_file):
            return {"next_step": "reporter", "circuit_breaker": True}

        current_mtime = os.path.getmtime(req_file)
        last_mtime = 0
        if os.path.exists(watermark_file):
            with open(watermark_file, "r") as f:
                last_mtime = float(f.read().strip())

        if current_mtime > last_mtime:
            self.log(f"🚀 New task detected for {repo_id}")
            with open(req_file, "r") as f:
                content = f.read()
            return {"requirements_delta": content, "iteration_count": 1, "next_step": "planner"}
        
        return {"next_step": "reporter", "circuit_breaker": True}
