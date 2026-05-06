from langgraph.graph import StateGraph, END
from state.project_state import ProjectState
from factory import NodeFactory

def build_graph():
    workflow = StateGraph(ProjectState)
    factory = NodeFactory()

    # Register Nodes
    workflow.add_node("cloner", factory.get_node("cloner"))
    workflow.add_node("monitor", factory.get_node("monitor"))
    workflow.add_node("planner", factory.get_node("planner"))
    workflow.add_node("coder", factory.get_node("coder"))
    workflow.add_node("qa", factory.get_node("qa"))
    workflow.add_node("pusher", factory.get_node("pusher"))
    workflow.add_node("reporter", factory.get_node("reporter"))

    # Define Linear Path
    workflow.set_entry_point("cloner")
    workflow.add_edge("cloner", "monitor")
    workflow.add_edge("monitor", "planner")
    workflow.add_edge("planner", "coder")
    workflow.add_edge("coder", "qa")

    # Conditional Routing for Loops
    workflow.add_conditional_edges(
        "qa",
        lambda x: x["next_step"],
        {
            "pusher": "pusher",
            "coder": "coder",
            "reporter": "reporter"
        }
    )

    workflow.add_edge("pusher", "reporter")
    workflow.add_edge("reporter", END)

    return workflow.compile()
