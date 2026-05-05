import os
import httpx
import truststore
from langchain_openai import ChatOpenAI

def get_llm(model_type="REASONING"):
    ssl_context = truststore.SSLContext()
    http_client = httpx.Client(verify=ssl_context, trust_env=True)
    
    prefix = "REASONING" if model_type == "REASONING" else "FAST"
    
    return ChatOpenAI(
        model=os.getenv(f"{prefix}_MODEL"),
        api_key=os.getenv(f"{prefix}_KEY"),
        base_url=os.getenv(f"{prefix}_URL", "").rstrip('/'),
        http_client=http_client,
        max_tokens=int(os.getenv("MAX_OUTPUT_TOKENS", 4096)) if model_type == "FAST" else None,
        temperature=0
    )

def extract_usage(response):
    """Helper to safely extract tokens even if metadata is missing."""
    return getattr(response, 'usage_metadata', {"total_tokens": 0})
