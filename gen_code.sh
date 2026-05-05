#!/bin/bash
# V2.31: Path-Strict Architect

echo "📝 Updating ArchitectNode to enforce path alignment..."
cat <<'EOF' > src/nodes/architect.py
from typing import Dict, Any
from nodes.base import BaseNode
from utils.safety import get_llm, extract_usage
from utils.parser import parse_llm_json

class ArchitectNode(BaseNode):
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        model = get_llm("REASONING")
        prompt = f"""
TASK: Design a modular FastAPI app for: {state.get('requirements_delta')}

### CRITICAL PATH RULE:
- All routes MUST be served under the root prefix '/' unless versioning is explicitly requested.
- If you use '/api/v1', the TestDesigner MUST be informed.

OUTPUT FORMAT:
## tech_spec
```markdown
Specify the exact BASE_URL (e.g. http://localhost:8000/health)
```
## file_impact
```json
["app/main.py", "app/routers/health.py"]
```
"""
        response = model.invoke(prompt)
        data = parse_llm_json(response.content)
        return {
            "tech_spec": data.get('tech_spec', ''),
            "file_impact": data.get('file_impact', []),
            "usage": extract_usage(response),
            "next_step": "test_designer"
        }
EOF
