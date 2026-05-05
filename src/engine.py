from langgraph.graph import StateGraph, END
from state.project_state import ProjectState
from factory import NodeFactory

def build_graph():
    workflow = StateGraph(ProjectState)
    factory = NodeFactory()

    for node in ["init", "discovery", "architect", "test_designer", "coder", "reviewer", "qa", "pr_creator", "reporter"]:
        workflow.add_node(node, factory.get_node(node))

    workflow.set_entry_point("init")
    workflow.add_edge("init", "discovery")
    workflow.add_edge("discovery", "architect")
    workflow.add_edge("architect", "test_designer")
    workflow.add_edge("test_designer", "coder")
    workflow.add_edge("coder", "reviewer")

    def reviewer_router(state):
        # HARD TERMINATION: Max 2 laps
        if state.get("iteration_count", 0) >= 5:
            return "reporter"
        if state.get("next_step") == "coder":
            return "coder"
        return "qa"

    workflow.add_conditional_edges("reviewer", reviewer_router, {
        "coder": "coder",
        "qa": "qa",
        "reporter": "reporter"
    })

    def qa_router(state):
        if state.get("next_step") == "pr_creator":
            return "pr_creator"
        return "coder"

    workflow.add_conditional_edges("qa", qa_router, {
        "pr_creator": "pr_creator",
        "coder": "coder"
    })

    workflow.add_edge("pr_creator", "reporter")
    workflow.add_edge("reporter", END)

    return workflow.compile()
