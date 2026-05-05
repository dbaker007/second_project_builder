import os
from typing import Dict, Any
from nodes.base import BaseNode
from langchain_openai import ChatOpenAI
from utils.parser import parse_llm_json

class ArchitectNode(BaseNode):
    """
    The Reasoning Specialist.
    Analyzes the delta and generates the Technical Spec + Mermaid Diagram.
    """
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # 1. Initialize Reasoning Model
        model = ChatOpenAI(
            model=os.getenv("REASONING_MODEL"),
            api_key=os.getenv("REASONING_KEY"),
            base_url=os.getenv("REASONING_URL"),
            temperature=0
        )

        # 2. Build the Architect Prompt
        prompt = f"""
You are a Principal Software Architect. 

### CONTEXT:
Stack DNA: {state['env_context']}
Existing Diagram: {state['env_context'].get('existing_diagram', 'None')}

### SURGICAL DELTA (Requirements):
{state['requirements_delta']}

### TASK:
1. Design a technical specification to fulfill the requirements.
2. Update the Mermaid diagram to reflect the new state.
3. Define the file impact (which files to create/modify).

### OUTPUT FORMAT:
Return ONLY a JSON object with:
{{
    "tech_spec": "Markdown string of your design",
    "mermaid_diagram": "Raw mermaid code string",
    "file_impact": ["list", "of", "paths"]
}}
"""
        self.log("🧠 Consulting Reasoning Model for architecture design...")
        response = model.invoke(prompt)
        
        try:
            spec_data = parse_llm_json(response.content)
            self.log("✅ Technical Spec and Mermaid diagram generated.")
            
            return {
                "tech_spec": spec_data['tech_spec'],
                "test_spec": spec_data.get('mermaid_diagram', ''), # We'll use this for README later
                "execution_logs": ["Architect: Design finalized and spec generated."],
                "next_step": "test_designer"
            }
        except Exception as e:
            self.log(f"❌ Architect Parse Error: {e}", level=40)
            return {"circuit_breaker": True}
