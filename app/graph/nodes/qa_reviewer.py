# app/graph/nodes/qa_reviewer.py
from app.graph.state import AgentState
from app.core.llm_setup import premium_llm
from langchain_core.messages import SystemMessage, HumanMessage
import logging

logger = logging.getLogger(__name__)


def qa_reviewer_node(state: AgentState) -> AgentState:
    """
    Reviews the drafted email. Returns 'PASS' or specific feedback for rewriting.
    """
    logger.info("--- NODE: QA REVIEWER ---")
    draft_email = state.get("draft_email", "")

    system_prompt = (
        "You are a strict B2B Sales Manager. Review the cold email."
        "Criteria: 1. Under 120 words. 2. Not overly 'salesy'. 3. Clear Call-to-Action. "
        "If it passes ALL criteria, reply with EXACTLY the word: PASS. "
        "If it fails, provide a short 1-sentence instruction on what to fix."
    )

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Review this email:\n\n{draft_email}")
    ]

    response = premium_llm.invoke(messages).content.strip()

    if "PASS" in response.upper():
        logger.info("QA Status: PASSED")
        return {"reviewer_feedback": "", "status": "pass_qa"}
    else:
        logger.warning(f"QA Status: FAILED. Feedback: {response}")
        return {"reviewer_feedback": response, "status": "needs_revision"}