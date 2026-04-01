# main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
from psycopg_pool import AsyncConnectionPool
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
import logging

from app.core.config import settings
from app.graph.workflow import build_graph
from app.api.routes import router as agent_router

# Setup logging
logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages application startup and shutdown events.
    Initializes DB connections and compiles the LangGraph.
    """
    # 1. Initialize PostgreSQL Connection Pool
    pool = AsyncConnectionPool(
        conninfo=settings.DATABASE_URL.replace("postgresql+asyncpg", "postgresql"),
        max_size=20,
        kwargs={"autocommit": True}
    )
    await pool.open()

    # 2. Setup LangGraph Checkpointer
    checkpointer = AsyncPostgresSaver(pool)
    await checkpointer.setup()  # Automatically creates necessary checkpoint tables

    # 3. Build and compile the Graph, defining the interrupt point
    workflow = build_graph()
    compiled_graph = workflow.compile(
        checkpointer=checkpointer,
        interrupt_before=["action_sender"]  # Pauses here for Human Approval
    )

    # 4. Attach to app state for global access in routes
    app.state.compiled_graph = compiled_graph
    app.state.db_pool = pool

    logging.info("Application successfully started and Graph compiled.")
    yield  # App is running

    # --- Shutdown sequence ---
    logging.info("Shutting down application...")
    await pool.close()


# Initialize FastAPI app
app = FastAPI(
    title="Việt Tree AI - Autonomous SDR Agent",
    description="Multi-agent B2B Sales workflow with human-in-the-loop",
    version="1.0.0",
    lifespan=lifespan
)

# Include the API routes
app.include_router(agent_router)


# Example Healthcheck Route
@app.get("/")
async def root():
    return {"status": "Agent API is running."}