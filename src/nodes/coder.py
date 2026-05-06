import os
import subprocess
from nodes.base import BaseNode

class CoderNode(BaseNode):
    def execute(self, state: dict):
        target = state['target_path']
        impacted_files = state.get('file_impact', [])
        critique = state.get('surgical_critique', '')
        
        message = f"Implement these requirements exactly: {state.get('requirements_delta')}"
        if critique:
            message = f"Fix previous failures based on this critique: {critique}"

        self.log(f"🛠️ Aider: Executing surgical graft...")

        # Environment Hardening
        env = os.environ.copy()
        ca_bundle = "/opt/homebrew/lib/python3.14/site-packages/certifi/cacert.pem"
        
        # 🛡️ SSL & Auth Mapping
        env["SSL_CERT_FILE"] = ca_bundle
        env["REQUESTS_CA_BUNDLE"] = ca_bundle
        env["LITELLM_SSL_VERIFY"] = "False"  # Force bypass if Zscaler blocks the handshake
        
        # Ensure Aider/LiteLLM sees the key (Mapping XAI_KEY to XAI_API_KEY)
        if "XAI_KEY" in env:
            env["XAI_API_KEY"] = env["XAI_KEY"]

        cmd = [
            "aider",
            "--model", f"xai/{os.getenv('FAST_MODEL')}",
            "--message", message,
            "--yes",
            "--no-git",
            "--no-show-model-warnings"
        ]
        
        if impacted_files:
            cmd.extend(impacted_files)

        # Run Aider
        result = subprocess.run(cmd, cwd=target, env=env)

        if result.returncode != 0:
            self.log(f"❌ Aider failed with exit code {result.returncode}", level=40)
            return {"circuit_breaker": True, "next_step": "reporter"}

        self.log("✅ Aider graft successful.")
        return {"next_step": "qa", "surgical_critique": ""}
