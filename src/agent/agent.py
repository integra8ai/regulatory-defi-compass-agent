from typing import List, Dict, Optional
from langgraph.graph import StateGraph
from pydantic import BaseModel, Field
from typing_extensions import TypedDict
from src.tools.llm_parser import LLMQueryParser
from src.tools.defillama_client import DeFiLlamaClient
from src.tools.protocol_metadata import ProtocolMetadataFetcher
from src.tools.compliance_scorer import ComplianceScorer
from src.tools.opportunity_ranker import OpportunityRanker

class ComplianceAgentState(TypedDict):
    user_query: str                  # Original natural language query
    amount: Optional[float]           # Extracted amount
    token: Optional[str]              # Extracted token
    chain: Optional[str]              # Preferred chain
    risk_tolerance: str               # "conservative", "moderate", "aggressive"
    raw_yields: List[Dict]            # Yield data from DeFiLlama
    protocol_metadata: List[Dict]     # Enriched data for each protocol
    compliance_scores: List[Dict]     # Risk scores per opportunity
    ranked_opportunities: List[Dict]  # Final ranked list
    response: str                     # Formatted output

class ComplianceAgent:
    def __init__(self):
        """Initialize the Regulatory DeFi Compass agent with all required tools."""
        self.query_parser = LLMQueryParser()
        self.defillama_client = DeFiLlamaClient()
        self.metadata_fetcher = ProtocolMetadataFetcher()
        self.compliance_scorer = ComplianceScorer()
        self.opportunity_ranker = OpportunityRanker()
    
    def parse_query(self, state: ComplianceAgentState) -> ComplianceAgentState:
        """
        Parse the user query to extract structured parameters.
        
        Args:
            state: Current agent state with user_query
            
        Returns:
            Updated state with extracted parameters
        """
        print("Parsing user query...")
        
        # Use LLM to parse the query
        parsed_data = self.query_parser.parse_query(state["user_query"])
        
        # Update state with parsed data
        state["amount"] = parsed_data.get("amount")
        state["token"] = parsed_data.get("token")
        state["chain"] = parsed_data.get("chain")
        state["risk_tolerance"] = parsed_data.get("risk_tolerance", "moderate")
        
        return state
    
    def fetch_yields(self, state: ComplianceAgentState) -> ComplianceAgentState:
        """
        Fetch yield data from DeFiLlama API.
        
        Args:
            state: Current agent state with token and chain info
            
        Returns:
            Updated state with raw yield data
        """
        print("Fetching yield data...")
        
        # Fetch pools from DeFiLlama
        pools = self.defillama_client.fetch_pools(
            chain=state.get("chain"),
            token=state.get("token"),
            limit=20
        )
        
        # Deduplicate pools by pool ID to prevent duplicate opportunities
        seen_pools = set()
        deduplicated_pools = []
        for pool in pools:
            pool_id = pool.get("pool")
            # If pool ID is missing, create a composite key from project, symbol, and chain
            if not pool_id:
                pool_id = f"{pool.get('project', '')}_{pool.get('symbol', '')}_{pool.get('chain', '')}"
            
            if pool_id not in seen_pools:
                seen_pools.add(pool_id)
                deduplicated_pools.append(pool)
        
        state["raw_yields"] = deduplicated_pools
        return state
    
    def fetch_protocol_metadata(self, state: ComplianceAgentState) -> ComplianceAgentState:
        """
        Fetch protocol metadata from DeFiLlama data.
        
        Args:
            state: Current agent state with raw yield data
            
        Returns:
            Updated state with protocol metadata
        """
        print("Fetching protocol metadata...")
        
        # Enrich protocols with metadata derived from DeFiLlama data
        enriched_protocols = self.metadata_fetcher.enrich_protocols(state["raw_yields"])
        
        state["protocol_metadata"] = enriched_protocols
        return state
    
    def calculate_compliance_score(self, state: ComplianceAgentState) -> ComplianceAgentState:
        """
        Calculate compliance scores for each opportunity.
        
        Args:
            state: Current agent state with protocol metadata
            
        Returns:
            Updated state with compliance scores
        """
        print("Calculating compliance scores...")
        
        # Score protocols based on metadata and user risk tolerance
        scored_protocols = self.compliance_scorer.score_protocols(
            state["protocol_metadata"],
            state["risk_tolerance"]
        )
        
        state["compliance_scores"] = scored_protocols
        return state
    
    def rank_opportunities(self, state: ComplianceAgentState) -> ComplianceAgentState:
        """
        Rank opportunities based on APY and compliance score.
        
        Args:
            state: Current agent state with compliance scores
            
        Returns:
            Updated state with ranked opportunities
        """
        print("Ranking opportunities...")
        
        # Merge yield data with compliance scores
        opportunities_by_project = {}
        for yield_data in state["raw_yields"]:
            # Find matching compliance score
            protocol_name = yield_data.get("project", "")
            compliance_data = next(
                (item for item in state["compliance_scores"] if item["protocol"] == protocol_name),
                {"compliance_score": 5.0}
            )
            
            # Combine yield and compliance data
            opportunity = yield_data.copy()
            opportunity.update(compliance_data)

            # Rank this individual opportunity to get its score
            scored_opportunity_list = self.opportunity_ranker.rank_opportunities([opportunity], state["risk_tolerance"])
            if scored_opportunity_list:
                scored_opportunity = scored_opportunity_list[0]
                project_key = scored_opportunity.get("project", "Unknown")

                # Keep only the best opportunity per project
                if project_key not in opportunities_by_project or \
                   scored_opportunity["final_score"] > opportunities_by_project[project_key]["final_score"]:
                    opportunities_by_project[project_key] = scored_opportunity
        
        # Convert dictionary values back to a list
        opportunities = list(opportunities_by_project.values())

        # Rank the unique opportunities (already scored)
        # Note: The opportunity_ranker will re-sort them, but we already have scores
        #       This step ensures global ranking across all unique projects.
        ranked = self.opportunity_ranker.rank_opportunities(
            opportunities,
            state["risk_tolerance"]
        )
        
        state["ranked_opportunities"] = ranked
        return state
    
    def format_response(self, state: ComplianceAgentState) -> ComplianceAgentState:
        """
        Format the final response for the user.
        
        Args:
            state: Current agent state with ranked opportunities
            
        Returns:
            Updated state with formatted response
        """
        print("Formatting response...")
        
        # Take top 5 opportunities
        top_opportunities = state["ranked_opportunities"][:5]
        
        # Format response
        if not top_opportunities:
            response = "No DeFi opportunities found matching your criteria."
        else:
            response_lines = ["Here are the top DeFi opportunities based on your criteria:", ""]
            for i, opp in enumerate(top_opportunities, 1):
                formatted = self.opportunity_ranker.format_opportunity(opp)
                response_lines.append(f"{i}. {formatted}")
            
            response_lines.append("")
            response_lines.append(f"Risk Tolerance: {state['risk_tolerance'].capitalize()}")
            response = "\n".join(response_lines)
        
        state["response"] = response
        return state
    
    def create_workflow(self):
        """
        Create the LangGraph workflow for the agent.
        
        Returns:
            Compiled LangGraph workflow
        """
        # Create the graph
        workflow = StateGraph(ComplianceAgentState)
        
        # Add nodes
        workflow.add_node("parse_query", self.parse_query)
        workflow.add_node("fetch_yields", self.fetch_yields)
        workflow.add_node("fetch_protocol_metadata", self.fetch_protocol_metadata)
        workflow.add_node("calculate_compliance_score", self.calculate_compliance_score)
        workflow.add_node("rank_opportunities", self.rank_opportunities)
        workflow.add_node("format_response", self.format_response)
        
        # Add edges
        workflow.add_edge("parse_query", "fetch_yields")
        workflow.add_edge("fetch_yields", "fetch_protocol_metadata")
        workflow.add_edge("fetch_protocol_metadata", "calculate_compliance_score")
        workflow.add_edge("calculate_compliance_score", "rank_opportunities")
        workflow.add_edge("rank_opportunities", "format_response")
        
        # Set entry point
        workflow.set_entry_point("parse_query")
        
        # Add conditional edges for proper flow control
        # In this linear workflow, we can just connect nodes sequentially
        
        return workflow.compile()

# Example usage
if __name__ == "__main__":
    agent = ComplianceAgent()
    workflow = agent.create_workflow()
    
    # Example state
    initial_state = {
        "user_query": "Show me low-risk DeFi opportunities for staking 1000 USDC on Ethereum",
        "amount": 1000.0,
        "token": "USDC",
        "chain": "Ethereum",
        "risk_tolerance": "conservative"
    }
    
    # Execute the workflow
    result = workflow.invoke(initial_state)
    print(result["response"])