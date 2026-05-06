import os
import subprocess
from nodes.base import BaseNode
from utils.safety import get_llm, extract_usage
from utils.parser import parse_llm_json

class PlannerNode(BaseNode):
    def execute(self, state: dict):
        model = get_llm("FAST", self.name)
        target = state['target_path']
        reqs = state.get('requirements_delta', '')
        
        # Get the tree to find the correct test file path
        tree = subprocess.run(["tree", "-L", "3", target], capture_output=True, text=True).stdout

        prompt = f"""
        Requirements: {reqs}
        
        EXISTING PROJECT STRUCTURE:
        {tree}
        
        TASK:
        1. Identify the EXISTING source file to edit.
        2. Identify the EXISTING test file to populate.
        3. Define the exact pytest command.
        
        RETURN JSON ONLY:
        {{
          "files": ["src/project_manager/main.py", "tests/test_main.py"],
          "test_cmd": "uv run python -m pytest tests/test_main.py",
          "goal": "Implement CLI logic in main.py and corresponding mocks in test_main.py"
        }}
        """
        
        self.log("🧠 Planning with explicit Test-Drive requirements...")
        response = model.invoke(prompt)
        plan = parse_llm_json(response.content)
        
        return {
            "file_impact": plan.get('files', []),
            "test_command": plan.get('test_cmd', 'uv run pytest'),
            "tech_spec": plan.get('goal', ''),
            "usage": extract_usage(response),
            "next_step": "coder"
        }
