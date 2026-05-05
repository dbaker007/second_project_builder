from typing import Dict, Any
from nodes.base import BaseNode
from utils.safety import get_llm, extract_usage
from utils.parser import parse_llm_json

class TestDesignerNode(BaseNode):
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        model = get_llm("REASONING")
        impact = state.get('file_impact', [])
        
        prompt = f"""
TASK: Write a pytest suite for this spec.
FILES: {impact}

### MANDATORY FORMAT:
You MUST use this exact header for your code block:
## tests/agent_test.py
```python
...
```
"""
        response = model.invoke(prompt)
        usage = extract_usage(response)
        # Use the hybrid parser which now handles the ## header
        data = parse_llm_json(response.content)
        
        return {
            "test_spec": data.get('tests/agent_test.py', ''),
            "usage": usage,
            "next_step": "coder"
        }
