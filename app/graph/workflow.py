# app/graph/workflow.py
from langgraph.graph import StateGraph, START, END
from app.graph.state import AgentState
from app.graph.nodes.researcher import lead_researcher_node
from app.graph.nodes.qualifier import qualifier_node
from app.graph.nodes.copywriter import copywriter_node
from app.graph.nodes.qa_reviewer import qa_reviewer_node
from app.graph.nodes.action_sender import action_sender_node
from app.graph.edges import route_qualify, route_qa


def build_graph():
    """Constructs and compiles the LangGraph workflow."""
    workflow = StateGraph(AgentState)

    # 1. Add Nodes
    workflow.add_node("researcher", lead_researcher_node)
    workflow.add_node("qualifier", qualifier_node)
    workflow.add_node("copywriter", copywriter_node)
    workflow.add_node("qa_reviewer", qa_reviewer_node)
    workflow.add_node("action_sender", action_sender_node)

    # 2. Add Edges
    workflow.add_edge(START, "researcher")
    workflow.add_edge("researcher", "qualifier")

    # Conditional edge after qualifying
    workflow.add_conditional_edges(
        "qualifier",
        route_qualify,
        {
            "end": END,
            "continue": "copywriter"
        }
    )

    workflow.add_edge("copywriter", "qa_reviewer")

    # Cyclic conditional edge for QA self-correction
    workflow.add_conditional_edges(
        "qa_reviewer",
        route_qa,
        {
            "rewrite": "copywriter",
            "human_approval": "action_sender"  # We route to action_sender, but interrupt before it
        }
    )

    workflow.add_edge("action_sender", END)

    return workflow