import os
import httpx
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from unittest.mock import MagicMock


def get_llm(model_type="REASONING", node_name=None):
    if os.getenv("AGENT_MOCK_MODE", "false").lower() == "true":
        mock = MagicMock()
        mock.invoke.return_value.content = "Mock response."
        mock.invoke.return_value.usage_metadata = {"total_tokens": 0}
        return mock

    prefix = "REASONING" if model_type == "REASONING" else "FAST"
    model_name = os.getenv(f"{prefix}_MODEL")
    base_url = os.getenv(f"{prefix}_URL", "").rstrip("/")

    timeout_seconds = 300.0

    if "11434" in base_url:
        return ChatOllama(
            model=model_name,
            base_url=base_url,
            temperature=0,
            timeout=timeout_seconds,
            keep_alive=0,
            num_predict=8192,
            num_ctx=16384,
            # 🛡️ Anti-Stutter Guardrails
            repeat_penalty=1.1,
            presence_penalty=0.0,
            frequency_penalty=0.0,
            top_k=40,
        )

    http_client = httpx.Client(timeout=timeout_seconds)
    return ChatOpenAI(
        model=model_name,
        api_key=os.getenv(f"{prefix}_KEY") or os.getenv("XAI_KEY"),
        base_url=base_url or "https://x.ai",
        http_client=http_client,
        temperature=0,
    )


def extract_usage(response):
    if hasattr(response, "usage_metadata"):
        return response.usage_metadata
    return getattr(response, "response_metadata", {}).get(
        "token_usage", {"total_tokens": 0}
    )
