# app/graph/nodes/researcher.py
from app.graph.state import AgentState
import logging

logger = logging.getLogger(__name__)


def lead_researcher_node(state: AgentState) -> AgentState:
    """
    Simulates researching a lead by scraping web/LinkedIn data.
    In production, integrate with Tavily API or Proxycurl here.
    """
    logger.info("--- NODE: LEAD RESEARCHER ---")
    lead_info = state.get("lead_info", {})
    company = lead_info.get("company", "Unknown Company")
    name = lead_info.get("name", "Unknown Lead")

    # Mock data generation based on inputs
    # Use your local extraction_llm here if parsing raw HTML
    mock_research = (
        f"{company} has recently scaled their operations and is actively "
        f"hiring in their IT department. {name} has been with the company for 3 years "
        f"and focuses on workflow optimization."
    )

    return {
        "research_data": mock_research,
        "status": "researching"
    }