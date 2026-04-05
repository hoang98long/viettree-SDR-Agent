# app/api/routes.py
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from app.api.dependencies import get_product_rag_service
from app.services.rag_service import ProductRAGService

router = APIRouter(prefix="/api", tags=["Agent Operations"])


# --- Request Models ---
class LeadRequest(BaseModel):
    thread_id: str
    name: str
    company: str


class ApprovalRequest(BaseModel):
    thread_id: str
    action: str  # "approve" or "reject"
    feedback: str = ""


class ProductQueryRequest(BaseModel):
    query: str
    top_k: int | None = None


# --- Routes ---

@router.post("/trigger-graph")
async def trigger_agent(payload: LeadRequest, request: Request):
    """Triggers the agent workflow for a new lead."""
    compiled_graph = request.app.state.compiled_graph

    config = {"configurable": {"thread_id": payload.thread_id}}
    initial_state = {
        "lead_info": {"name": payload.name, "company": payload.company},
        "status": "new"
    }

    # ainvoke runs the graph asynchronously
    result = await compiled_graph.ainvoke(initial_state, config)

    return {
        "message": "Workflow started successfully",
        "current_state": result
    }


@router.post("/approve-email")
async def approve_email(payload: ApprovalRequest, request: Request):
    """Handles the human-in-the-loop approval or rejection of the draft email."""
    compiled_graph = request.app.state.compiled_graph
    config = {"configurable": {"thread_id": payload.thread_id}}

    # 1. Get current state to ensure the graph is paused/waiting
    current_state = await compiled_graph.aget_state(config)

    if not current_state.next:
        raise HTTPException(status_code=400, detail="Graph is not currently paused or waiting for approval.")

    if payload.action == "approve":
        # Resume graph with no updates, letting it proceed to action_sender
        result = await compiled_graph.ainvoke(None, config)
        return {"message": "Email approved and sent.", "status": result}

    elif payload.action == "reject":
        # Update state with human feedback and force routing back
        state_update = {
            "reviewer_feedback": payload.feedback,
            "status": "needs_revision"
        }
        # Inject the update as if it came from the qa_reviewer node
        await compiled_graph.aupdate_state(config, state_update, as_node="qa_reviewer")

        # Resume the graph
        result = await compiled_graph.ainvoke(None, config)
        return {"message": "Email rejected. Sent back to Copywriter.", "status": result}

    raise HTTPException(status_code=400, detail="Invalid action. Use 'approve' or 'reject'.")


@router.post("/rag/products/query")
async def query_product_catalog(
    payload: ProductQueryRequest,
    rag_service: ProductRAGService = Depends(get_product_rag_service)
):
    """Queries the ChromaDB `stock_market` collection for products, prices, and promotions."""
    result = await rag_service.answer_product_question(
        question=payload.query,
        top_k=payload.top_k
    )
    return result
