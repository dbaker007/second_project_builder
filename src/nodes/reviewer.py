import logging

from nodes.base import BaseNode
from utils.safety import get_llm, extract_usage
from utils.parser import parse_llm_json
import os
from utils.protocols import ENGINEERING_PROTOCOLS


class ReviewerNode(BaseNode):
    def execute(self, state: dict):
        model = get_llm("REASONING", self.name)
        target = state["target_path"]  # Add this

        # 🛠️ GATHER ACTUAL CODE CONTENT
        source_context = ""
        for f_path in state.get("file_impact", []):
            full_path = os.path.normpath(os.path.join(target, f_path))
            if os.path.exists(full_path):
                with open(full_path, "r") as f:
                    source_context += f"\nFILE: {f_path}\n---\n{f.read()}\n"
            else:
                self.log(
                    f"🚨 Reviewer Error: Impacted file missing at {full_path}",
                    level=logging.CRITICAL,
                )
                return {
                    "next_step": "reporter",
                    "surgical_critique": f"FATAL REVIEW ERROR: The file '{f_path}' was listed as impacted but does not exist on disk. Review aborted to prevent stale analysis.",
                    "requirements_fulfilled": False,
                }
            prompt = f"""
                Role: Senior Python Architect
                Phase Goal: {state.get("tech_spec")}
                
                CODE TO REVIEW:
                {source_context} 

                TASK: Audit the implementation against these 8 MANDATORY ENGINEERING PROTOCOLS:
                {ENGINEERING_PROTOCOLS}

                INSTRUCTIONS:
                1. If the code violates ANY protocol above, you must set "approved": false.
                2. Identify specific protocol numbers in the "violated_protocols" list.
                3. If no protocols are violated and the code is professional, set "approved": true.

                JSON FORMAT:
                {{
                    "approved": true/false,
                    "violated_protocols": [1, 2], 
                    "critique": "Identify the specific breach or root cause of failure.",
                    "suggestions": ["Specific refactor steps to satisfy the protocols."]
                }}
            """

        self.log("🧐 Reviewer: Verifying engineering quality...")
        response = model.invoke(prompt)
        review = parse_llm_json(response.content)

        if review.get("approved", False):
            self.log("✅ Review Passed.")
            return {"next_step": "environment", "usage": extract_usage(response)}
        else:
            self.log(f"❌ Review Rejected: {review.get('critique')}", logging.WARNING)
            return {
                "next_step": "coder",
                "surgical_critique": f"ARCHITECTURAL REJECTION: {review.get('critique')}",
                "violated_protocols": review.get("violated_protocols", []),
                "usage": extract_usage(response),
            }
