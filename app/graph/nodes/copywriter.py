# app/graph/nodes/copywriter.py
from app.graph.state import AgentState
from app.core.llm_setup import premium_llm
from langchain_core.messages import SystemMessage, HumanMessage
import logging

logger = logging.getLogger(__name__)


def copywriter_node(state: AgentState) -> AgentState:
    """
    Generates or refines a personalized cold email using a premium LLM.
    """
    logger.info("--- NODE: COPYWRITER ---")
    lead_info = state.get("lead_info", {})
    research_data = state.get("research_data", "")
    feedback = state.get("reviewer_feedback", "")

    system_prompt = (
        "You are an expert B2B SDR copywriter for 'Việt Tree AI'. "
        "Your goal is to write highly personalized, concise cold emails (under 120 words). "
        "Focus on how our AI workflow automation can help them. Don't use generic greetings."
    )

    human_prompt = (
        f"Write an email to {lead_info.get('name')} at {lead_info.get('company')}.\n"
        f"Context/Research: {research_data}\n"
    )

    if feedback:
        logger.info(f"Refining email based on feedback: {feedback}")
        human_prompt += f"\nCRITICAL FEEDBACK FROM QA (Fix this): {feedback}"

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=human_prompt)
    ]

    response = premium_llm.invoke(messages)
    return {
        "draft_email": response.content.strip(),
        "status": "drafted"
    }