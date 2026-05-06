import re
import json
import logging

def parse_llm_json(raw_content: str):
    cleaned = raw_content.strip()
    files = {}
    # Matches ## path/to/file followed by ```code```
    file_pattern = r"(?:#+)\s*`?([\w\.\/\-_ ]+)`?\s*?\n\s*?```[a-z]*\n(.*?)\n```"
    matches = list(re.finditer(file_pattern, cleaned, re.IGNORECASE | re.DOTALL))
    
    for m in matches:
        path, content = m.group(1).strip(), m.group(2)
        if "." in path or "/" in path:
            files[path] = content
            
    if files: return files
    
    # Fallback for structured JSON
    json_match = re.search(r"(\{.*\})", cleaned, re.DOTALL)
    if json_match:
        try: return json.loads(json_match.group(1))
        except: pass
        
    return {"main_output": cleaned}
