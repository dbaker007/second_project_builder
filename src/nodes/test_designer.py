import os
from typing import Dict, Any
from nodes.base import BaseNode
from langchain_openai import ChatOpenAI
from utils.parser import parse_llm_json

class TestDesignerNode(BaseNode):
    """
    The Spec-Writer Specialist.
    Generates a pytest suite (the Contract) before any code is written.
    """
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # 1. Initialize Reasoning Model
        model = ChatOpenAI(
            model=os.getenv("REASONING_MODEL"),
            api_key=os.getenv("REASONING_KEY"),
            base_url=os.getenv("REASONING_URL"),
            temperature=0
        )

        # 2. Build the Test Design Prompt
        prompt = f"""
You are a Senior QA Engineer implementing TDD.

### ARCHITECT'S SPEC:
{state['tech_spec']}

### TARGET ENVIRONMENT:
{state['env_context']}

### TASK:
Generate a comprehensive pytest suite in a single file: 'tests/agent_test.py'.
1. The tests must define the "Definition of Done" for the Architect's Spec.
2. Use Mocks for any external APIs or network calls.
3. Ensure the test file is self-contained.

### OUTPUT FORMAT:
Return ONLY a JSON object with:
{{
    "test_file_path": "tests/agent_test.py",
    "test_code": "The full python pytest code string"
}}
"""
        self.log("🧪 Designing test contract (Definition of Done)...")
        response = model.invoke(prompt)
        
        try:
            test_data = parse_llm_json(response.content)
            self.log(f"✅ Test contract generated: {test_data['test_file_path']}")
            
            return {
                "test_spec": test_data['test_code'],
                "execution_logs": ["TestDesigner: Pytest contract generated."],
                "next_step": "coder"
            }
        except Exception as e:
            self.log(f"❌ TestDesigner Parse Error: {e}", level=40)
            return {"circuit_breaker": True}
