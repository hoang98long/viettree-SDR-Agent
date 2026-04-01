# app/graph/edges.py
from app.graph.state import AgentState

def route_qualify(state: AgentState) -> str:
    """Routes based on lead score."""
    if state["status"] == "rejected":
        return "end"
    return "continue"

def route_qa(state: AgentState) -> str:
    """Routes based on QA review result."""
    if state["status"] == "needs_revision":
        return "rewrite"
    return "human_approval"