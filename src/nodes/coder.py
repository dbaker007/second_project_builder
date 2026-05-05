import os
import subprocess
from typing import Dict, Any
from nodes.base import BaseNode
from utils.safety import get_llm, extract_usage
from utils.parser import parse_llm_json

class CoderNode(BaseNode):
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        model = get_llm("FAST")
        target = state['target_path']
        branch = state.get('feature_branch', 'agent/patch')
        
        critique = state.get('surgical_critique', '')
        feedback_block = f"\n### 🚨 FIX THESE ISSUES:\n{critique}\n" if critique else ""

        prompt = f"""
{feedback_block}
TASK: Implement the files for this spec: {state.get('tech_spec')}

### ⚡️ CRITICAL FORMATTING RULE (MANDATORY):
You MUST provide the code using Markdown headers for every single file. 
DO NOT explain your work. DO NOT use JSON. DO NOT use generic titles.

Example:
## app/main.py
```python
# code here
```

## pyproject.toml
```toml
# config here
```
"""
        self.log("🚀 Implementing code (Strict Markdown Mode)...")
        response = model.invoke(prompt)
        usage = extract_usage(response)
        
        try:
            files = parse_llm_json(response.content)
            
            # Ensure test contract is included
            if state.get("test_spec"):
                files["tests/agent_test.py"] = state["test_spec"]

            # Ensure we are on the correct branch
            subprocess.run(["git", "-C", target, "checkout", "-b", branch], capture_output=True)
            
            for rel_path, content in files.items():
                full_path = os.path.join(target, rel_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, "w") as f: f.write(content)
                self.log(f"💾 Grafted: {rel_path}")
                
            subprocess.run(["git", "-C", target, "add", "."], check=True)
            subprocess.run(["git", "-C", target, "commit", "-m", "Agent: Implementation"], check=True)
            
            # Prepare snapshot for Reviewer
            snapshot = "\n".join([f"FILE: {p}\n---\n{c}\n" for p, c in files.items()])
            
            return {
                "usage": usage,
                "tech_spec": f"{state['tech_spec']}\n\n### CURRENT IMPLEMENTATION:\n{snapshot}",
                "next_step": "reviewer",
                "surgical_critique": "" 
            }
        except Exception as e:
            self.log(f"❌ Coder Formatting Error: {e}", level=40)
            # We return to Coder to try one more time if it fails parsing
            return {"next_step": "coder", "surgical_critique": "Your last response was not in the '## filename' format. Try again using EXACTLY that format."}
