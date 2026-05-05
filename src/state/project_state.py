import operator
from typing import Annotated, List, TypedDict, Dict, Any

def aggregate_usage(existing: Dict[str, int], new: Dict[str, int]) -> Dict[str, int]:
    """Sums up token usage from the current turn into the global total."""
    if not new:
        return existing
    return {
        "total_tokens": existing.get("total_tokens", 0) + new.get("total_tokens", 0)
    }

class ProjectState(TypedDict):
    # --- Git & Workspace ---
    repo_url: str
    target_path: str
    feature_branch: str
    
    # --- Context & Discovery ---
    requirements_delta: str  # The diff between origin/main and current requirements
    codebase_summary: str    # Cleaned context (no lockfiles)
    env_context: Dict[str, Any] # Detected stack (Python, JS, etc.)
    
    # --- TDD & Architecture ---
    tech_spec: str           # Architect's plan & Mermaid diagram
    test_spec: str           # Test-Designer's pytest suite
    
    # --- Control & Routing ---
    next_step: str           # Router signal
    iteration_count: int     # Loop safety
    circuit_breaker: bool    # True = System Failure, Stop Immediately
    
    # --- Telemetry ---
    usage: Annotated[Dict[str, int], aggregate_usage]
    execution_logs: Annotated[List[str], operator.add]
