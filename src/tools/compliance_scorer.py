from typing import List, Dict
from datetime import datetime

class ComplianceScorer:
    def __init__(self):
        """Initialize the compliance scorer."""
        pass
    
    def calculate_compliance_score(self, protocol_metadata: Dict, risk_tolerance: str = "moderate") -> float:
        """
        Calculate a compliance score for a protocol based on various factors.
        
        Args:
            protocol_metadata: Dictionary with protocol metadata
            risk_tolerance: User's risk tolerance ("conservative", "moderate", "aggressive")
            
        Returns:
            Compliance score between 1-10 (lower = safer)
        """
        score = 5.0  # Start with neutral score
        
        # Factor 1: Audit status
        if protocol_metadata.get("audited", False):
            score -= 1.0  # Bonus for audited protocols
        else:
            score += 1.0  # Penalty for unaudited protocols
        
        # Factor 2: Number of audits
        audit_count = protocol_metadata.get("audit_count", 0)
        if audit_count >= 5:
            score -= 0.5
        elif audit_count >= 2:
            score -= 0.25
        else:
            score += 0.5
        
        # Factor 3: Protocol age
        launch_date_str = protocol_metadata.get("launch_date", "")
        if launch_date_str:
            try:
                launch_date = datetime.strptime(launch_date_str, "%Y-%m-%d")
                age_days = (datetime.now() - launch_date).days
                
                if age_days > 365:  # More than 1 year old
                    score -= 0.5
                elif age_days < 180:  # Less than 6 months old
                    score += 1.0
                # 6-12 months gets no adjustment
            except ValueError:
                # Invalid date format
                score += 0.5
        
        # Factor 4: Jurisdiction
        jurisdiction = protocol_metadata.get("jurisdiction", "").lower()
        if "usa" in jurisdiction or "united states" in jurisdiction:
            score += 1.0  # Penalty for US jurisdiction due to higher regulatory scrutiny
        elif "offshore" in jurisdiction or "cayman" in jurisdiction:
            score -= 0.5  # Bonus for offshore jurisdictions
        
        # Factor 5: Protocol type
        protocol_type = protocol_metadata.get("type", "").lower()
        if "lp" in protocol_type or "liquidity" in protocol_type:
            score += 0.5  # Slight penalty for LP pools (higher complexity)
        elif "lending" in protocol_type:
            score -= 0.5  # Slight bonus for lending protocols (more established)
        
        # Factor 6: Recent negative news
        recent_news_flags = protocol_metadata.get("recent_news_flags", 0)
        if recent_news_flags > 0:
            score += 2.0 * recent_news_flags  # Significant penalty for negative news
        
        # Adjust weights based on risk tolerance
        if risk_tolerance == "conservative":
            # Double the weight of safety factors
            if score < 5.0:  # Already safer than average
                score = max(1.0, score * 0.8)
            else:  # Less safe than average
                score = min(10.0, score * 1.2)
        elif risk_tolerance == "aggressive":
            # Reduce the weight of safety factors
            if score < 5.0:  # Safer than average
                score = min(10.0, score * 1.2)
            else:  # Less safe than average
                score = max(1.0, score * 0.8)
        
        # Ensure score is within bounds
        score = max(1.0, min(10.0, score))
        
        return round(score, 2)
    
    def score_protocols(self, protocols_metadata: List[Dict], risk_tolerance: str = "moderate") -> List[Dict]:
        """
        Score a list of protocols based on their metadata.
        
        Args:
            protocols_metadata: List of dictionaries with protocol metadata
            risk_tolerance: User's risk tolerance ("conservative", "moderate", "aggressive")
            
        Returns:
            List of dictionaries with protocol data and compliance scores
        """
        scored_protocols = []
        for protocol in protocols_metadata:
            score = self.calculate_compliance_score(protocol, risk_tolerance)
            protocol_with_score = protocol.copy()
            protocol_with_score["compliance_score"] = score
            scored_protocols.append(protocol_with_score)
        return scored_protocols

# Example usage
if __name__ == "__main__":
    scorer = ComplianceScorer()
    
    # Sample protocol metadata
    sample_protocols = [
        {
            "protocol": "aave",
            "audited": True,
            "audit_count": 5,
            "launch_date": "2017-01-01",
            "jurisdiction": "Cayman Islands",
            "type": "lending",
            "recent_news_flags": 0
        },
        {
            "protocol": "new-protocol",
            "audited": False,
            "audit_count": 0,
            "launch_date": "2023-01-01",
            "jurisdiction": "USA",
            "type": "lp",
            "recent_news_flags": 1
        }
    ]
    
    # Score protocols with different risk tolerances
    for tolerance in ["conservative", "moderate", "aggressive"]:
        print(f"\nRisk Tolerance: {tolerance.capitalize()}")
        scored = scorer.score_protocols(sample_protocols, tolerance)
        for protocol in scored:
            print(f"  {protocol['protocol']}: {protocol['compliance_score']}/10")