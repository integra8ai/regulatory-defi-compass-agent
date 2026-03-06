#!/usr/bin/env python3
"""
Test script for the Regulatory DeFi Compass Agent
"""

import sys
import os

# Add the parent directory to the Python path so we can import from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agent.agent import ComplianceAgent, ComplianceAgentState

def test_agent():
    """Test the ComplianceAgent with a sample query"""
    print("Testing Regulatory DeFi Compass Agent")
    print("=" * 40)
    
    # Initialize the agent
    agent = ComplianceAgent()
    workflow = agent.create_workflow()
    
    # Create a test state
    test_state: ComplianceAgentState = {
        "user_query": "Show me low-risk DeFi opportunities for staking USDC",
        "amount": None,
        "token": "USDC",
        "chain": None,
        "risk_tolerance": "conservative",
        "raw_yields": [],
        "protocol_metadata": [],
        "compliance_scores": [],
        "ranked_opportunities": [],
        "response": ""
    }
    
    print(f"Input query: {test_state['user_query']}")
    print(f"Risk tolerance: {test_state['risk_tolerance']}")
    print()
    
    # Execute the workflow
    try:
        result = workflow.invoke(test_state)
        print("Agent Response:")
        print("-" * 20)
        print(result["response"])
        print()
        
        # Show some internal data for verification
        print("Internal Data:")
        print("-" * 20)
        print(f"Raw yields count: {len(result['raw_yields'])}")
        print(f"Protocol metadata count: {len(result['protocol_metadata'])}")
        print(f"Compliance scores count: {len(result['compliance_scores'])}")
        print(f"Ranked opportunities count: {len(result['ranked_opportunities'])}")
        
    except Exception as e:
        print(f"Error running agent: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_agent()