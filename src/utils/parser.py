import re
import json
import logging

logger = logging.getLogger("agent.utils.parser")

def parse_llm_json(raw_content: str):
    """
    Extracts JSON from LLM responses, handling 'Thinking' blocks, 
    markdown code fences, and conversational noise.
    """
    # 1. Strip DeepSeek/R1 thinking blocks
    cleaned = re.sub(r"<think>.*?</think>", "", raw_content, flags=re.DOTALL).strip()
    
    # 2. Try to find JSON inside markdown code blocks
    code_block_match = re.search(r"```json\s*(.*?)\s*```", cleaned, re.DOTALL)
    if code_block_match:
        content_to_parse = code_block_match.group(1)
    else:
        # 3. Fallback: Find the first '{' and last '}'
        json_match = re.search(r"(\{.*\})", cleaned, re.DOTALL)
        content_to_parse = json_match.group(1) if json_match else cleaned

    try:
        return json.loads(content_to_parse)
    except json.JSONDecodeError:
        logger.warning("⚠️ Failed to parse JSON. Returning raw content as main_output.")
        return {"main_output": cleaned}
