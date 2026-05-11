import logging
import os
import subprocess
import re
from nodes.base import BaseNode


class QANode(BaseNode):
    def execute(self, state: dict):
        target = state["target_path"]

        # 🛡️ Establish the import bridge
        test_env = os.environ.copy()
        test_env["PYTHONPATH"] = os.path.join(target, "src")

        self.log(f"🧪 QA: Verifying Full Suite")

        try:
            # 1. Execute Tests
            result = subprocess.run(
                ["uv", "run", "pytest"],
                cwd=target,
                capture_output=True,
                text=True,
                env=test_env,
            )

            output = f"{result.stdout}\n{result.stderr}"

            # 2. Check for "No tests found" (Anti-cheating)
            if (
                "no tests ran" in output.lower()
                or "collected 0 items" in output.lower()
            ):
                self.log("⚠️ No tests found.", logging.ERROR)
                return {
                    "next_step": "coder",
                    "qa_passed": False,
                    "surgical_critique": "QA System: No tests were found. You must implement behavioral tests in the 'tests/' directory that verify the logic.",
                }

            # 3. Binary Success: Does the suite pass?
            if result.returncode == 0:
                self.log("✅ QA Passed.")
                return {
                    "next_step": "pusher",
                    "qa_passed": True,
                    "surgical_critique": "",  # Clears breaker in BaseNode
                }

            # 4. Failure Branch
            self.log("❌ QA Failed.", logging.WARNING)
            return {
                "next_step": "coder",
                "qa_passed": False,
                "surgical_critique": output,
            }

        except Exception as e:
            self.log(f"💥 QA Crash: {e}", logging.ERROR)
            return {
                "next_step": "reporter",
                "surgical_critique": f"QA EXECUTION ERROR: {str(e)}",
            }
