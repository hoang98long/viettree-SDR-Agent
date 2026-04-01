# app/graph/state.py
from typing import TypedDict, Optional, Dict, Any

class AgentState(TypedDict):
    """
    Represents the state of our LangGraph execution.
    """
    lead_info: Dict[str, Any]       # e.g., {"name": "John Doe", "company": "TechCorp", "linkedin": "..."}
    research_data: Optional[str]    # Data scraped from the web/LinkedIn
    lead_score: Optional[int]       # 0-100 score indicating lead quality
    draft_email: Optional[str]      # The generated email content
    reviewer_feedback: Optional[str]# Feedback from the QA agent or Human
    status: str                     # Current status: 'new', 'researching', 'qualified', 'rejected', 'needs_revision', 'approved', 'sent'