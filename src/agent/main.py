from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn
from src.agent.agent import ComplianceAgent, ComplianceAgentState

app = FastAPI(
    title="Regulatory DeFi Compass Agent",
    description="An agent that helps users assess DeFi opportunities through a compliance and regulatory lens, overlaying risk scores on top of yield data.",
    version="1.0.0"
)

# Initialize the agent
agent = ComplianceAgent()
workflow = agent.create_workflow()

class HealthResponse(BaseModel):
    status: str
    message: str

@app.get("/health", response_model=HealthResponse)
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

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint for processing user queries"""
    try:
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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)