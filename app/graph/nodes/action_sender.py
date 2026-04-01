# app/graph/nodes/action_sender.py
from app.graph.state import AgentState
import logging

logger = logging.getLogger(__name__)


def action_sender_node(state: AgentState) -> AgentState:
    """
    Final node. Simulates sending the approved email.
    """
    logger.info("--- NODE: ACTION SENDER ---")
    draft_email = state.get("draft_email", "")
    lead_info = state.get("lead_info", {})

    # In a real environment, call Gmail API, SendGrid, or Resend here.
    logger.info(f"🚀 SENDING EMAIL TO {lead_info.get('name')}...")
    logger.info(f"CONTENT:\n{draft_email}")

    return {"status": "sent"}