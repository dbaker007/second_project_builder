from langgraph.graph import StateGraph, END
from state.project_state import ProjectState
from nodes.factory import NodeFactory


def build_graph():
    factory = NodeFactory()
    workflow = StateGraph(ProjectState)

    # 1. Register Nodes
    workflow.add_node("cloner", factory.get_node("cloner"))
    workflow.add_node("scaffolder", factory.get_node("scaffolder"))
    workflow.add_node("monitor", factory.get_node("monitor"))
    workflow.add_node("planner", factory.get_node("planner"))
    workflow.add_node("coder", factory.get_node("coder"))
    workflow.add_node("reviewer", factory.get_node("reviewer"))
    workflow.add_node("environment", factory.get_node("environment"))
    workflow.add_node("qa", factory.get_node("qa"))
    workflow.add_node("pusher", factory.get_node("pusher"))
    workflow.add_node("reporter", factory.get_node("reporter"))

    # 2. Entry Point
    workflow.set_entry_point("cloner")

    # 3. Foundations
    workflow.add_conditional_edges(
        "cloner",
        lambda x: x.get("next_step"),
        {
            "scaffolder": "scaffolder",
            "reporter": "reporter",  # 🚨 This allows the exit
        },
    )

    workflow.add_conditional_edges(
        "scaffolder",
        lambda x: x.get("next_step"),
        {
            "monitor": "monitor",
            "reporter": "reporter",  # 🚨 This allows the exit
        },
    )
    # 4. Monitoring & Planning Loop
    # Monitor now flows into Planner to provide the requirements_delta
    workflow.add_conditional_edges(
        "monitor",
        lambda x: x.get("next_step"),
        {
            "planner": "planner",
            "reporter": "reporter",  # 🚨 This allows the exit
        },
    )
    workflow.add_conditional_edges(
        "planner",
        lambda x: x.get("next_step", "coder"),
        {"monitor": "monitor", "coder": "coder", "qa": "qa", "reporter": "reporter"},
    )

    # 5. The Implementation Pipeline
    workflow.add_conditional_edges(
        "coder",
        lambda x: x.get("next_step"),
        {
            "reviewer": "reviewer",
            "reporter": "reporter",  # 🚨 This allows the exit
        },
    )
    workflow.add_conditional_edges(
        "reviewer",
        lambda x: x.get("next_step", "environment"),
        {
            "coder": "coder",
            "environment": "environment",
            "reporter": "reporter",  # 🚨 This allows the exit
        },
    )

    workflow.add_edge("environment", "qa")
    workflow.add_conditional_edges(
        "environment",
        lambda x: x.get("next_step", "environment"),
        {
            "qa": "qa",
            "reporter": "reporter",  # 🚨 This allows the exit
        },
    )
    # 6. The Verification & Pivot Loop
    workflow.add_conditional_edges(
        "qa",
        lambda x: x.get("next_step", "pusher"),
        {
            "coder": "coder",
            "planner": "planner",
            "pusher": "pusher",
            "reporter": "reporter",
        },
    )

    # 7. Phased Completion Loop
    workflow.add_conditional_edges(
        "pusher",
        lambda x: "monitor" if not x.get("requirements_fulfilled") else "reporter",
        {
            "monitor": "monitor",
            "reporter": "reporter",
        },
    )

    workflow.add_edge("reporter", END)

    return workflow.compile()
