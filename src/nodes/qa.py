import os
import shutil
import subprocess
from typing import Dict, Any
from nodes.base import BaseNode

class QANode(BaseNode):
    """
    The Functional Validation Specialist.
    Executes tests in a clean-room environment with Mock-safety.
    """
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        branch = state.get('feature_branch', 'agent/fix-v2')
        qa_path = os.path.join("temp", f"qa_{branch.replace('/', '_')}")
        
        try:
            # 1. Setup Clean Room
            if os.path.exists(qa_path):
                shutil.rmtree(qa_path)
            os.makedirs(qa_path, exist_ok=True)

            # 2. Clone the implementation branch
            self.log(f"🧪 QA: Cloning branch {branch} into clean room...")
            subprocess.run(
                ["git", "clone", "--branch", branch, state['target_path'], qa_path],
                check=True, capture_output=True
            )

            # 3. Environment Preparation (The Mock Firewall)
            qa_env = os.environ.copy()
            qa_env["AGENT_MOCK_MODE"] = "true"
            qa_env["PYTHONPATH"] = f"{qa_path}:{qa_env.get('PYTHONPATH', '')}"

            # 4. Execution: Run the specific test contract
            # We assume the Test-Designer wrote to 'tests/agent_test.py'
            test_file = os.path.join(qa_path, "tests", "agent_test.py")
            if not os.path.exists(test_file):
                 self.log("❌ QA Failed: Test contract file not found in branch.", level=30)
                 return {"next_step": "coder"}

            self.log("🏃 Executing pytest contract...")
            result = subprocess.run(
                ["pytest", test_file],
                env=qa_env,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                self.log("✅ QA Passed: Functional requirements met.")
                return {
                    "execution_logs": ["QA: All tests passed."],
                    "next_step": "pr_creator"
                }
            else:
                self.log(f"❌ QA Failed: {result.stderr or result.stdout}", level=30)
                return {
                    "execution_logs": [f"QA: Test failures - {result.stdout[:200]}"],
                    "next_step": "coder"
                }

        except Exception as e:
            self.log(f"❌ QA System Error: {e}", level=40)
            return {"circuit_breaker": True}
        
        finally:
            # 5. Cleanup: Always wipe the clean room
            if os.path.exists(qa_path):
                self.log(f"🧹 QA: Cleaning up {qa_path}")
                shutil.rmtree(qa_path, ignore_errors=True)
