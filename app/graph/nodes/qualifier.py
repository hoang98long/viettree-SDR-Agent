# app/graph/nodes/qualifier.py
from app.graph.state import AgentState
import logging

logger = logging.getLogger(__name__)


def qualifier_node(state: AgentState) -> AgentState:
    """
    Evaluates the lead based on research data against the Ideal Customer Profile (ICP).
    """
    logger.info("--- NODE: QUALIFIER ---")
    research_data = state.get("research_data", "").lower()

    # Simple evaluation logic (Can be replaced with LLM evaluation for complex ICPs)
    score = 50
    if "scale" in research_data or "scaling" in research_data:
        score += 20
    if "workflow optimization" in research_data or "automation" in research_data:
        score += 25

    status = "qualified" if score >= 70 else "rejected"
    logger.info(f"Lead Score: {score} - Status: {status}")

    return {
        "lead_score": score,
        "status": status
    }