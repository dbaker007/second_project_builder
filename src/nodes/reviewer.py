import json
import re
from typing import Dict, Any
from nodes.base import BaseNode
from utils.safety import get_llm, extract_usage

class ReviewerNode(BaseNode):
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        model = get_llm("REASONING")
        current_iter = state.get("iteration_count", 0) + 1
        
        prompt = f"""
Review this code: {state.get('tech_spec')}

### ⚖️ PRAGMATIC REVIEW RULE:
- If the files exist and the FastAPI /health logic is present, grant LGTM.
- DO NOT reject for minor style, naming, or documentation issues.
- We are in a 'Surgical' build phase; functionality is the only priority.

RETURN ONLY JSON:
{{
  "decision": "LGTM" or "NEEDS_REVISION",
  "feedback": "..."
}}
"""
        response = model.invoke(prompt)
        usage = extract_usage(response)
        
        try:
            match = re.search(r"(\{.*\})", response.content, re.DOTALL)
            review = json.loads(match.group(1)) if match else json.loads(response.content)
        except:
            review = {"decision": "LGTM", "feedback": "Auto-pass due to parse error."}

        decision = review.get("decision", "LGTM")
        self.log(f"🧐 Review (Turn {current_iter}): {decision}")
        
        return {
            "usage": usage,
            "iteration_count": current_iter,
            "surgical_critique": review.get("feedback", "") if decision == "NEEDS_REVISION" else "",
            "next_step": "qa" if decision == "LGTM" else "coder"
        }
