from langgraph.graph import StateGraph, END
from state.project_state import ProjectState
from factory import NodeFactory

def build_graph():
    """
    Constructs the Sentinel Healer V2 TDD Graph.
    """
    workflow = StateGraph(ProjectState)
    factory = NodeFactory()

    # 1. Register Nodes
    workflow.add_node("init", factory.get_node("init"))
    workflow.add_node("discovery", factory.get_node("discovery"))
    workflow.add_node("architect", factory.get_node("architect"))
    workflow.add_node("test_designer", factory.get_node("test_designer"))
    workflow.add_node("coder", factory.get_node("coder"))
    workflow.add_node("reviewer", factory.get_node("reviewer"))
    workflow.add_node("qa", factory.get_node("qa"))
    workflow.add_node("pr_creator", factory.get_node("pr_creator"))

    # 2. Define Main Edge Flow
    workflow.set_entry_point("init")
    workflow.add_edge("init", "discovery")
    workflow.add_edge("discovery", "architect")
    workflow.add_edge("architect", "test_designer")
    workflow.add_edge("test_designer", "coder")
    workflow.add_edge("coder", "reviewer")

    # 3. Define Conditional Routing (The Loops & Circuit Breaker)
    def router(state):
        if state.get("circuit_breaker"):
            return "end"
        return state.get("next_step", "end")

    workflow.add_conditional_edges(
        "reviewer",
        router,
        {
            "coder": "coder",        # Inner Loop: Polish
            "qa": "qa",              # LGTM -> Move to QA
            "end": END
        }
    )

    workflow.add_conditional_edges(
        "qa",
        router,
        {
            "coder": "coder",        # Outer Loop: Test Fail
            "pr_creator": "pr_creator", # Success
            "end": END
        }
    )

    workflow.add_edge("pr_creator", END)

    return workflow.compile()
