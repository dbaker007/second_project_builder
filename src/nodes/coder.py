import os
import subprocess
from nodes.base import BaseNode


class CoderNode(BaseNode):
    @staticmethod
    def _get_instructions(state: dict) -> str:
        from utils.protocols import ENGINEERING_PROTOCOLS

        critique = state.get("surgical_critique", "")
        history = state.get("turn_history", [])

        # 1. No-Op Logic
        noop_protocol = ""
        if len(history) > 1 and history[-1] == history[-2]:
            noop_protocol = (
                "NO-OP PREVENTION PROTOCOL:\n"
                "1. You are currently in a loop because no changes were detected on disk in the previous turn.\n"
                "2. You MUST modify the source code or tests to satisfy the protocols.\n"
                "3. Refactor for clarity, add documentation, or tighten type hints to ensure a state change occurs.\n"
                "4. Do NOT submit a response that results in zero file modifications.\n\n"
            )

        # 2. Revision Logic (Conditional)
        revision_logic = ""
        if critique:
            revision_logic = (
                f"CRITICAL FEEDBACK FROM ARCHITECT:\n{critique}\n\n"
                f"REASONING PROTOCOL:\n"
                f"1. ANALYZE: Identify every numbered Protocol breached in the ARCHITECT'S CRITIQUE.\n"
                f"2. PIVOT: Determine a valid implementation that satisfies both the TEST CONTRACT and the 8 PROTOCOLS.\n"
                f"3. EXECUTE: Rewrite the code ensuring 100% adherence. Do not use previously rejected patterns.\n\n"
                f"CRITICAL: The ARCHITECT'S CRITIQUE proves your previous technical assumptions were WRONG. "
                f"You must find a different way to satisfy the TEST CONTRACT while adhering to the 8 PROTOCOLS.\n\n"
            )

        # 3. Combined Final Instruction
        return (
            f"{revision_logic}"
            f"{noop_protocol}"
            f"PHASE GOAL: {state.get('tech_spec')}\n"
            f"TEST CONTRACT: {state.get('test_spec')}\n\n"
            f"STRICT ARCHITECTURAL PROTOCOLS:\n{ENGINEERING_PROTOCOLS}\n"
        ).strip()

    def execute(self, state: dict):
        target = state["target_path"]

        self.log("🛠️ Aider: Executing Phase Implementation")

        instruction = self._get_instructions(state)

        # 🛠️ THE FIX: Map the file_impact list to absolute paths for Aider
        impacted_files = list(state.get("file_impact", []))

        if "pyproject.toml" not in impacted_files:
            impacted_files.append("pyproject.toml")

        # 🛠️ Command uses relative paths (Aider handles the 'cwd=target')
        cmd = [
            "uv",
            "tool",
            "run",
            "--from",
            "aider-chat",
            "aider",
            "--model",
            f"openai/{os.getenv('FAST_MODEL')}",
            "--openai-api-base",
            f"{os.getenv('FAST_URL')}/v1",
            "--openai-api-key",
            "ollama",
            "--message",
            instruction,
            "--yes",
            "--no-stream",
            "--no-show-model-warnings",
            "--edit-format",
            "whole",
            *impacted_files,
        ]

        result = subprocess.run(cmd, cwd=target, env=os.environ.copy())
        return {"next_step": "reviewer" if result.returncode == 0 else "reporter"}
