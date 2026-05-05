from typing import Annotated, TypedDict, List, Dict, Any

def aggregate_usage(left: Dict[str, int], right: Dict[str, int]) -> Dict[str, int]:
    """Sum up token counts safely."""
    # Handle initialization where left might not be a dict yet
    l = left if isinstance(left, dict) else {}
    r = right if isinstance(right, dict) else {}
    
    new_usage = l.copy()
    for key, value in r.items():
        if isinstance(value, int):
            new_usage[key] = new_usage.get(key, 0) + value
    return new_usage

class ProjectState(TypedDict):
    repo_url: str
    target_path: str
    feature_branch: str
    usage: Annotated[Dict[str, int], aggregate_usage]
    env_context: Dict[str, Any]
    requirements_delta: str
    tech_spec: str
    test_spec: str
    file_impact: List[str]
    surgical_critique: str
    iteration_count: int
    circuit_breaker: bool
    execution_logs: Annotated[List[str], lambda x, y: x + y]
    next_step: str
