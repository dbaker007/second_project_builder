import json
import re
import logging
import ast
from typing import Any, Dict

logger = logging.getLogger("sentinel.parser")

def parse_llm_json(raw_content: str) -> Dict[str, Any]:
    """
    Robust JSON extraction from LLM responses.
    Handles markdown wrappers, single-quote fallbacks, and truncation detection.
    """
    # 1. Cleaning & Truncation Check
    cleaned = raw_content.strip()
    
    # We check for closing brace or the end of a markdown block
    if not (cleaned.endswith('}') or cleaned.endswith('```')):
        logger.error("❌ LLM Response appears truncated (no closing brace or backticks).")
        raise ValueError("Truncated LLM response detected.")

    # 2. Extraction: Find JSON block within markdown or raw text
    # Search for markdown first (supports json or python tags)
    json_match = re.search(r"```(?:json|python)?\s*(\{.*?\})\s*```", cleaned, re.DOTALL)
    if json_match:
        json_str = json_match.group(1)
    else:
        # Fallback to finding the outer-most { and }
        brace_match = re.search(r"(\{.*\})", cleaned, re.DOTALL)
        if not brace_match:
            raise ValueError("No JSON object found in response.")
        json_str = brace_match.group(1)

    # 3. Parsing: Standard JSON first, then Python literal_eval
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        logger.warning("⚠️ Standard JSON parse failed, trying literal_eval fallback...")
        try:
            # We strip to handle any stray newlines that literal_eval dislikes
            return ast.literal_eval(json_str.strip())
        except Exception as e:
            raise ValueError(f"Both JSON and literal_eval failed: {e}")
