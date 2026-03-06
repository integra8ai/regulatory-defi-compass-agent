import math
from typing import List, Dict

class OpportunityRanker:
    def __init__(self):
        """Initialize the opportunity ranker."""
        pass
    
    def rank_opportunities(self, opportunities: List[Dict], risk_tolerance: str = "moderate") -> List[Dict]:
        """
        Rank opportunities based on APY and compliance score.
        
        Args:
            opportunities: List of dictionaries with opportunity data
            risk_tolerance: User's risk tolerance ("conservative", "moderate", "aggressive")
            
        Returns:
            List of opportunities sorted by final score (higher is better)
        """
        # Determine weights based on risk tolerance
        if risk_tolerance == "conservative":
            w_apy = 0.3
            w_compliance = 0.7
        elif risk_tolerance == "aggressive":
            w_apy = 0.7
            w_compliance = 0.3
        else:  # moderate
            w_apy = 0.5
            w_compliance = 0.5
        
        ranked_opportunities = []
        
        for opp in opportunities:
            # Extract APY and compliance score
            apy = opp.get("apy", 0) / 100  # Convert percentage to decimal
            compliance_score = opp.get("compliance_score", 5)  # 1-10 scale
            
            # Calculate final score using weighted harmonic mean
            # We use (10 - compliance_score) to invert the compliance score
            # (so that lower compliance scores, which are better, contribute more positively)
            inverted_compliance = 10 - compliance_score
            
            # Weighted score calculation
            final_score = (apy * w_apy) + (inverted_compliance / 10 * w_compliance)
            
            # Add final score to opportunity data
            opp_with_score = opp.copy()
            opp_with_score["final_score"] = round(final_score, 4)
            ranked_opportunities.append(opp_with_score)
        
        # Sort by final score descending (higher is better)
        ranked_opportunities.sort(key=lambda x: x["final_score"], reverse=True)
        
        return ranked_opportunities
    
    def format_opportunity(self, opportunity: Dict) -> str:
        """
        Format a single opportunity for display.
        
        Args:
            opportunity: Dictionary with opportunity data
            
        Returns:
            Formatted string describing the opportunity
        """
        project = opportunity.get("project", "Unknown")
        chain = opportunity.get("chain", "Unknown")
        symbol = opportunity.get("symbol", "Unknown")
        apy = opportunity.get("apy", 0)
        compliance_score = opportunity.get("compliance_score", 5)
        
        return f"{project} on {chain} ({symbol}): {apy:.2f}% APY, Compliance Score: {compliance_score}/10"

# Example usage
if __name__ == "__main__":
    ranker = OpportunityRanker()
    
    # Sample opportunities
    sample_opportunities = [
        {
            "project": "Aave",
            "chain": "Ethereum",
            "symbol": "USDC",
            "apy": 4.5,
            "compliance_score": 2.5
        },
        {
            "project": "Compound",
            "chain": "Ethereum",
            "symbol": "DAI",
            "apy": 3.8,
            "compliance_score": 3.0
        },
        {
            "project": "NewProtocol",
            "chain": "Arbitrum",
            "symbol": "USDT",
            "apy": 15.2,
            "compliance_score": 7.5
        }
    ]
    
    # Rank opportunities with different risk tolerances
    for tolerance in ["conservative", "moderate", "aggressive"]:
        print(f"\nRisk Tolerance: {tolerance.capitalize()}")
        ranked = ranker.rank_opportunities(sample_opportunities, tolerance)
        for i, opp in enumerate(ranked, 1):
            formatted = ranker.format_opportunity(opp)
            print(f"  {i}. {formatted} (Score: {opp['final_score']:.3f})")