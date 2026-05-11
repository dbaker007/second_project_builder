import os
import subprocess
from nodes.base import BaseNode
from utils.safety import get_llm, extract_usage
from utils.parser import parse_llm_json


class PlannerNode(BaseNode):
    def execute(self, state: dict):
        model = get_llm("REASONING", self.name)
        target = state["target_path"]
        package_name = state.get("env_context", {}).get(
            "package_name", "project_manager"
        )
        plan_file = os.path.join(target, "IMPLEMENTATION_PLAN.md")

        # 1. Gather Grounding Context
        tree = state.get("project_tree", "")
        sigs = state.get("project_signatures", "")
        reqs = state.get("requirements_delta", "")
        stall_count = state.get("stall_count", 0)
        critique = state.get("surgical_critique", "")

        # 2. Determine Planning Mode
        mode = "ARCHITECT"
        if os.path.exists(plan_file):
            mode = "LEAD_ENGINEER"
            if stall_count > 0:
                mode = "DEBUGGER_IN_CHIEF"

        # 3. Mode-Specific Prompting
        if mode == "ARCHITECT":
            prompt = f"""
            TASK: Decompose the following Requirements into a Phased Implementation Plan.
            REQUIREMENTS: {reqs}
            
            STRICT ARCHITECTURAL RULES:
            1. ZERO HALLUCINATION: Only include features explicitly stated in the REQUIREMENTS.
            2. ATOMIC PHASING: Break the work into the smallest possible testable increments.
            3. HIERARCHY: Start with foundational data/logic before building interfaces.
            4. MINIMUM VIABLE ARCHITECTURE: Design for the MVP. Do not engineer for scale or features not yet requested.
            5. BEHAVIORAL VERIFICATION: Do NOT plan internal "check" or "verify" functions in the source code (e.g., verify_table_structure). Tests should verify state by attempting operations (INSERT/SELECT) and asserting success.
            6. REQUIREMENT FIDELITY: Only include data fields, logic, and features explicitly defined in the REQUIREMENTS. Do not infer, assume, or add "standard" fields (like timestamps or status codes) that are not requested.

            SUCCESS CRITERIA:
            1. The implementation plan MUST satisfy every requirement in the REQUIREMENTS input.
            2. The plan MUST NOT creep beyond the scope of the defined requirements.
            3. Every phase MUST result in a testable state.
            
            FORMAT: Return a JSON with a 'plan' key containing a Markdown Checklist.
            
            JSON Output:
            {{
              "plan": "# Implementation Plan\n- [ ] Phase 1: [First Required Component]\n- [ ] Phase 2: [Next Required Component]",
              "goal": "Faithful implementation of the requirements delta."
            }}
            """

        elif mode == "DEBUGGER_IN_CHIEF":
            prompt = f"""
            TASK: Strategic Pivot to Break Stall.
            STALL CRITIQUE: {critique}
            CURRENT SIGNATURES: {sigs}
            
            The Coder is stuck in a loop. You must REVISE the current phase in the IMPLEMENTATION_PLAN.md.
            Suggest a different technical approach (e.g., refactor, simplify, or change library).
            
            JSON Output:
            {{
              "revised_plan": "Updated IMPLEMENTATION_PLAN.md content with the pivot included.",
              "tech_spec": "New surgical instructions to break the stutter.",
              "test_spec": "Updated test requirements for the new approach."
            }}
            """

        else:  # LEAD_ENGINEER
            prompt = f"""
            TASK: Generate Surgical Phase Brief.
            CURRENT PHASE: {state.get("tech_spec")}
            PROJECT REALITY: {tree}
            SIGNATURES: {sigs}
            
            Provide the Coder with the specific logic, file impacts, and test requirements for ONLY this phase.
            Mandate that ALL existing tests + new tests MUST pass.
            
            JSON Output:
            {{
              "tech_spec": "Detailed implementation logic.",
              "file_impact": ["src/{package_name}/file.py"],
              "test_spec": "Specific pytest requirements for this phase.",
              "dependencies": ["list", "of", "required", "external", "libraries"]
            }}
            """

        response = model.invoke(prompt)
        res = parse_llm_json(response.content)

        # 4. Persistence & State Updates
        if mode == "ARCHITECT":
            with open(plan_file, "w") as f:
                f.write(res.get("plan", ""))
            return {"next_step": "monitor", "usage": extract_usage(response)}

        if mode == "DEBUGGER_IN_CHIEF":
            with open(plan_file, "w") as f:
                f.write(res.get("revised_plan", ""))
            # After a pivot, we clear the stall count to give the Coder a fresh start
            return {
                "tech_spec": res.get("tech_spec"),
                "test_spec": res.get("test_spec"),
                "stall_count": 0,
                "next_step": "coder",
                "usage": extract_usage(response),
            }

        return {
            "tech_spec": res.get("tech_spec"),
            "file_impact": res.get("file_impact", []),
            "test_spec": res.get("test_spec"),
            "next_step": "coder",
            "usage": extract_usage(response),
        }
