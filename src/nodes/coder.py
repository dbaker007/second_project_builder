import os
import subprocess
from typing import Dict, Any
from nodes.base import BaseNode
from langchain_openai import ChatOpenAI
from utils.parser import parse_llm_json

class CoderNode(BaseNode):
    """
    The Implementation Specialist.
    Grafts code surgically to satisfy the Technical Spec and Test Contract.
    """
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # 1. Initialize Fast Model with Truncation Guard
        model = ChatOpenAI(
            model=os.getenv("FAST_MODEL"),
            api_key=os.getenv("FAST_KEY"),
            base_url=os.getenv("FAST_URL"),
            max_tokens=int(os.getenv("MAX_OUTPUT_TOKENS", 4096)),
            temperature=0
        )

        # 2. Build the Surgical Implementation Prompt
        prompt = f"""
You are a Senior Software Engineer performing a SURGICAL update.

### TECHNICAL SPECIFICATION:
{state['tech_spec']}

### TEST CONTRACT (Definition of Done):
{state['test_spec']}

### PROJECT DNA:
{state['env_context']}

### CRITICAL RULES:
1. DO NOT DELETE existing imports, safety checks, or directory setup logic.
2. Maintain all existing setup code (os.makedirs, env validation).
3. Return ONLY a valid JSON object. No conversational text.
4. Output MUST be a flat dictionary: {{"path/to/file": "content_string"}}

### TASK:
Implement the files required by the Technical Specification.
Ensure the code passes the Test Contract.
"""
        self.log("🚀 Implementing surgical code changes...")
        response = model.invoke(prompt)
        
        try:
            generated_files = parse_llm_json(response.content)
            target_path = state['target_path']
            
            # 3. Write Files to Workspace
            for rel_path, content in generated_files.items():
                full_path = os.path.join(target_path, rel_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(content)
                self.log(f"💾 Updated: {rel_path}")

            # 4. Commit to local branch
            branch = state.get('feature_branch', 'agent/fix-v2')
            subprocess.run(["git", "-C", target_path, "add", "."], check=True)
            subprocess.run(["git", "-C", target_path, "commit", "-m", "Agent: Implementation Round"], check=True)

            return {
                "execution_logs": [f"Coder: {len(generated_files)} files modified."],
                "usage": getattr(response, 'usage_metadata', {}),
                "next_step": "reviewer"
            }
        except Exception as e:
            self.log(f"❌ Coder Error/Truncation: {e}", level=40)
            return {"circuit_breaker": True}
