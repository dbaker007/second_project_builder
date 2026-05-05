import os
import shutil
import subprocess
import sys
from typing import Dict, Any
from nodes.base import BaseNode

class QANode(BaseNode):
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        branch = state.get('feature_branch')
        target = state['target_path']
        qa_path = os.path.abspath(os.path.join("temp", f"qa_{branch.replace('/', '_')}"))
        
        try:
            if os.path.exists(qa_path): shutil.rmtree(qa_path)
            subprocess.run(["git", "clone", "--branch", branch, target, qa_path], check=True, capture_output=True)

            env = os.environ.copy()
            env["PYTHONPATH"] = f"{qa_path}:{env.get('PYTHONPATH', '')}"

            self.log(f"🏃 QA: Executing tests...")
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "-v", "tests/agent_test.py"],
                cwd=qa_path,
                env=env,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                self.log("✅ QA Passed.")
                return {"next_step": "pr_creator", "surgical_critique": ""}
            else:
                error_context = result.stderr if len(result.stderr) > 10 else result.stdout
                self.log(f"❌ QA Failed. Feeding Traceback to state.", level=30)
                return {
                    "next_step": "coder", 
                    "surgical_critique": f"PYTEST FAILURE:\n{error_context[-1000:]}"
                }

        except Exception as e:
            self.log(f"❌ QA System Error: {e}", level=40)
            return {"circuit_breaker": True, "next_step": "reporter"}
        finally:
            if os.path.exists(qa_path): shutil.rmtree(qa_path, ignore_errors=True)
