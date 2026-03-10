"""LangServe entry point for the Regulatory DeFi Compass Agent.

This file exposes the :class:`~src.agent.agent.ComplianceAgent` as a LangServe
application.  It is intentionally lightweight – the heavy lifting is done by
the agent itself.  The file is designed to be used with the LangServe CLI
(`langserve deploy`) and can also be run locally with `uvicorn` if desired.

The agent's :meth:`create_workflow` method returns a LangGraph runnable that
implements the full conversational flow.  LangServe automatically turns this
runnable into a REST endpoint that accepts JSON payloads and streams back
responses.

The ``/health`` and ``/chat`` endpoints from the original FastAPI app are
available in :mod:`src.agent.main`.  If you want to keep those endpoints
available in the LangServe deployment, you can import the router from
``src.agent.main`` and include it in the FastAPI instance below.
"""

from fastapi import FastAPI
from langserve import add_routes
from src.agent.main import get_agent

# ---------------------------------------------------------------------------
# Agent initialization - use shared singleton instance
# ---------------------------------------------------------------------------
# ``get_agent`` returns the singleton agent instance and its workflow.
# This ensures the same agent is used across both LangServe routes and
# the /health and /chat endpoints from src.agent.main.
agent_instance, runnable = get_agent()

# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Regulatory DeFi Compass Agent",
    version="1.0",
    description="A LangServe API for the Regulatory DeFi Compass Agent for Warden Protocol.",
)

# ---------------------------------------------------------------------------
# LangServe route
# ---------------------------------------------------------------------------
add_routes(
    app,
    runnable,
    path="/regulatory-defi-compass-agent",
    enable_feedback=True,
    enable_events=True,
)

# ---------------------------------------------------------------------------
# Optional: expose original FastAPI endpoints
# ---------------------------------------------------------------------------
# Include the /health and /chat endpoints from src.agent.main
from src.agent.main import router as main_router
app.include_router(main_router)

