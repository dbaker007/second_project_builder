import os
from typing import Dict, Any
from nodes.base import BaseNode
from langchain_openai import ChatOpenAI
from utils.parser import parse_llm_json

class ReviewerNode(BaseNode):
    """
    The Quality Assurance Specialist (Architect's Guard).
    Acts as the 'Inner Loop' filter to ensure professional standards.
    """
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # 1. Initialize Reasoning Model (Architect-level thinking)
        model = ChatOpenAI(
            model=os.getenv("REASONING_MODEL"),
            api_key=os.getenv("REASONING_KEY"),
            base_url=os.getenv("REASONING_URL"),
            temperature=0
        )

        # 2. Build the Reviewer Prompt
        # This node compares the Coder's logs/output against the Architect's Spec
        prompt = f"""
You are a Principal Software Architect reviewing a PR.

### TECHNICAL SPECIFICATION:
{state['tech_spec']}

### LATEST IMPLEMENTATION LOGS:
{state.get('execution_logs', [])[-1]}

### PROJECT DNA:
{state['env_context']}

### CRITICAL STANDARDS:
1. Does the code strictly follow the project DNA?
2. Did the Coder preserve all immutable infrastructure (setup, env validation, logging)?
3. Is the code professional, idiomatic, and free of "quick hacks"?
4. Does the logic actually fulfill the Technical Specification?

### OUTPUT FORMAT:
Return ONLY a JSON object:
{{
    "decision": "LGTM" or "NEEDS_REVISION",
    "feedback": "Specific feedback if revisions are needed",
    "is_system_error": false
}}
"""
        self.log("🧐 Reviewing implementation against architecture standards...")
        response = model.invoke(prompt)
        
        try:
            review_data = parse_llm_json(response.content)
            
            if review_data['decision'] == "LGTM":
                self.log("✨ Review Passed: Code meets professional standards.")
                return {
                    "execution_logs": ["Reviewer: LGTM - Code approved for functional QA."],
                    "next_step": "qa"
                }
            else:
                self.log(f"🔄 Revision Requested: {review_data['feedback']}")
                return {
                    "execution_logs": [f"Reviewer: Needs Revision - {review_data['feedback']}"],
                    "next_step": "coder"
                }
        except Exception as e:
            self.log(f"❌ Reviewer Parse Error: {e}", level=40)
            # Route to circuit breaker
            return {"circuit_breaker": True, "next_step": "reporter"}
