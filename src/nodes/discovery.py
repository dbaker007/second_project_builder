import re
from nodes.base import BaseNode
from typing import Dict, Any

class DiscoveryNode(BaseNode):
    """
    Identifies the project's tech stack, test tools, and existing diagrams.
    """
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        content = state.get("codebase_summary", "")
        
        # 1. Detect Stack (DNA)
        context = {
            "language": "python" if "pyproject.toml" in content or ".py" in content else "unknown",
            "manager": "uv" if "uv.lock" in content else "pip",
            "test_runner": "pytest" if "pytest" in content or "tests/" in content else "unittest",
            "has_readme": "README.md" in content
        }

        # 2. Extract Existing Mermaid Diagrams
        # This helps the Architect maintain documentation continuity
        mermaid_match = re.search(r"", content, re.DOTALL)
        context["existing_diagram"] = mermaid_match.group(1) if mermaid_match else None

        self.log(f"🧬 DNA Detected: {context['language']} via {context['manager']}")
        if context["existing_diagram"]:
            self.log("🎨 Existing Mermaid diagram found in README.")

        return {
            "env_context": context,
            "execution_logs": [f"Discovery: Stack identified as {context['language']}"],
            "next_step": "architect"
        }
