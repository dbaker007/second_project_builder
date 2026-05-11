from typing import Annotated, TypedDict, List, Dict, Any


def aggregate_usage(left: Dict[str, int], right: Dict[str, int]) -> Dict[str, int]:
    l = left if isinstance(left, dict) else {}
    r = right if isinstance(right, dict) else {}
    new_usage = l.copy()
    for key, value in r.items():
        if isinstance(value, int):
            new_usage[key] = new_usage.get(key, 0) + value
    return new_usage


def append_list(left: List[Any], right: List[Any]) -> List[Any]:
    return (left or []) + (right or [])


class ProjectState(TypedDict):
    repo_url: str
    target_path: str
    feature_branch: str
    env_context: Dict[str, Any]
    requirements_delta: str
    tech_spec: str
    test_spec: str
    requirements_fulfilled: bool
    file_impact: List[str]
    usage: Annotated[Dict[str, int], aggregate_usage]
    iteration_count: int
    execution_logs: Annotated[List[str], append_list]
    next_step: str
    pr_url: str
    qa_passed: bool
    surgical_critique: str
    last_error: str
    stall_count: int
    dependencies: List[str]
    violated_protocols: List[int]
    turn_history: Annotated[List[str], append_list]
    violation_history: Annotated[List[List[int]], append_list]  # Trace of all turns
    node_counter: int
