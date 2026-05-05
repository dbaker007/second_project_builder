import re
import json
import logging
from typing import Dict, Any

logger = logging.getLogger("sentinel.parser")

def parse_llm_json(raw_content: str) -> Any:
    """
    Universal Header Parser:
    Matches any header level (# to ###) followed by a file path.
    """
    cleaned = raw_content.strip()
    files = {}

    # Resilient Regex for # path/to/file or ## path/to/file
    # Group 1: The filename/path
    # Group 2: The code block content
    file_pattern = r"(?:#+)\s*`?([\w\.\/\-_ ]+)`?\s*?\n\s*?```[a-z]*\n(.*?)\n```"
    
    matches = list(re.finditer(file_pattern, cleaned, re.IGNORECASE | re.DOTALL))
    
    for m in matches:
        path = m.group(1).strip()
        # Filter out headers that are clearly not file paths (like "Running Instructions")
        if "." in path or "/" in path or "toml" in path:
            content = m.group(2)
            files[path] = content

    if files:
        return files

    # Fallback for Reviewer (JSON)
    json_match = re.search(r"(\{.*\})", cleaned, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except: pass

    # Fallback for single block
    code_match = re.search(r"```[a-z]*\n(.*?)\n```", cleaned, re.DOTALL)
    if code_match:
        return {"main_output": code_match.group(1)}

    with open("logs/failed_markdown.txt", "w") as f:
        f.write(raw_content)
    raise ValueError("Unparseable response. Check logs/failed_markdown.txt")
