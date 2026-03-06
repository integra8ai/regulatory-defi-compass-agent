"""
LangGraph implementation for the Regulatory DeFi Compass Agent
"""

from langgraph.graph import StateGraph

from src.agent.agent import ComplianceAgent, ComplianceAgentState


# Initialize the agent
agent = ComplianceAgent()

# Create the workflow
workflow = agent.create_workflow()

# Create the graph
graph = workflow

if __name__ == "__main__":
    # Example usage
    initial_state = {
        "user_query": "Show me low-risk DeFi opportunities for staking 1000 USDC on Ethereum",
        "amount": 1000.0,
        "token": "USDC",
        "chain": "Ethereum",
        "risk_tolerance": "conservative",
        "raw_yields": [],
        "protocol_metadata": [],
        "compliance_scores": [],
        "ranked_opportunities": [],
        "response": ""
    }
    
    # Execute the workflow
    result = workflow.invoke(initial_state)
    print(result["response"])