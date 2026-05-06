import os
import subprocess
from nodes.base import BaseNode

class QANode(BaseNode):
    def execute(self, state: dict):
        target = state['target_path']
        test_cmd = state.get('test_command', 'uv run python -m pytest')
        iters = state.get('iteration_count', 0)
        
        self.log(f"🧪 QA: Preparing environment (Attempt {iters})")

        # Environment Hardening
        env = os.environ.copy()
        ca_bundle = "/opt/homebrew/lib/python3.14/site-packages/certifi/cacert.pem"
        env["SSL_CERT_FILE"] = ca_bundle
        env["UV_CERT_BUNDLE"] = ca_bundle

        # 📦 BOOTSTRAP: Ensure pytest exists in the target sandbox
        # We use 'uv add --dev' to inject it into the target's environment
        self.log("📦 Ensuring pytest is installed in target...")
        subprocess.run(["uv", "add", "--dev", "pytest"], cwd=target, env=env, capture_output=True)

        # 🏃 Execute Test Suite
        self.log(f"🏃 Running: {test_cmd}")
        result = subprocess.run(
            test_cmd.split(),
            cwd=target,
            env=env,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            self.log("✅ QA Passed.")
            return {"next_step": "pusher", "surgical_critique": None}
        
        if iters < 3:
            self.log(f"❌ Failed. Sending feedback to Coder ({iters}/3)", level=30)
            return {
                "next_step": "coder",
                "surgical_critique": f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}",
                "iteration_count": 1
            }
        
        return {"next_step": "reporter", "circuit_breaker": True}
