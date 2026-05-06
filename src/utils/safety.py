import os
import httpx
import truststore
from langchain_openai import ChatOpenAI
from unittest.mock import MagicMock

def get_llm(model_type="REASONING", node_name=None):
    if os.getenv("AGENT_MOCK_MODE", "false").lower() == "true":
        mock = MagicMock()
        mock_path = f"mocks/{node_name}.txt"
        content = "Mock response."
        if node_name and os.path.exists(mock_path):
            with open(mock_path, "r") as f:
                content = f.read()
        mock.invoke.return_value.content = content
        mock.invoke.return_value.usage_metadata = {"total_tokens": 0}
        return mock

    ssl_context = truststore.SSLContext()
    http_client = httpx.Client(verify=ssl_context, trust_env=True)
    
    # Map to your .env keys
    prefix = "REASONING" if model_type == "REASONING" else "FAST"
    
    return ChatOpenAI(
        model=os.getenv(f"{prefix}_MODEL"),
        api_key=os.getenv(f"{prefix}_KEY") or os.getenv("XAI_KEY"),
        base_url=os.getenv(f"{prefix}_URL", "https://api.x.ai/v1").rstrip('/'),
        http_client=http_client,
        temperature=0
    )

def extract_usage(response):
    return getattr(response, 'usage_metadata', {"total_tokens": 0})
