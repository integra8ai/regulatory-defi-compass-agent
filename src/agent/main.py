from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
from typing import Optional
import uvicorn
from src.agent.agent import ComplianceAgent, ComplianceAgentState

# Module-level agent initialization (singleton pattern)
_agent = None
_workflow = None

def get_agent():
    """Get or create the singleton agent instance.
    
    Returns:
        tuple: (agent, workflow) - The ComplianceAgent instance and its workflow
    """
    global _agent, _workflow
    if _agent is None:
        _agent = ComplianceAgent()
        _workflow = _agent.create_workflow()
    return _agent, _workflow

# Create a router for the endpoints
router = APIRouter()

class HealthResponse(BaseModel):
    status: str
    message: str

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="ok",
        message="Regulatory DeFi Compass Agent is running"
    )

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint for processing user queries"""
    try:
        # Get the singleton agent and workflow
        _, workflow = get_agent()
        
        # Create initial state
        initial_state: ComplianceAgentState = {
            "user_query": request.message,
            "amount": None,
            "token": None,
            "chain": None,
            "risk_tolerance": "moderate",
            "raw_yields": [],
            "protocol_metadata": [],
            "compliance_scores": [],
            "ranked_opportunities": [],
            "response": ""
        }
        
        # Execute the agent workflow
        result = workflow.invoke(initial_state)
        
        return ChatResponse(
            response=result["response"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

# Create the FastAPI app and include the router
app = FastAPI(
    title="Regulatory DeFi Compass Agent",
    description="An agent that helps users assess DeFi opportunities through a compliance and regulatory lens, overlaying risk scores on top of yield data.",
    version="1.0.0"
)
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)