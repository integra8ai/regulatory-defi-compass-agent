import requests
from typing import List, Dict, Optional
import os
from src.tools.defillama_client import DeFiLlamaClient

class ProtocolMetadataFetcher:
    def __init__(self):
        """Initialize the protocol metadata fetcher."""
        # Initialize DeFiLlama client to fetch real protocol data
        self.defillama_client = DeFiLlamaClient()
        # We'll extract compliance-relevant metadata directly from DeFiLlama data
        pass
    
    def get_protocol_metadata(self, protocol_name: str, protocol_data: Dict = None) -> Dict:
        """
        Extract metadata for a specific protocol from DeFiLlama data.
        
        Args:
            protocol_name: Name of the protocol
            protocol_data: Protocol data from DeFiLlama (optional)
            
        Returns:
            Dictionary with protocol metadata
        """
        # Normalize protocol name
        protocol_name = protocol_name.lower().strip()
        
        # Default metadata structure
        metadata = {
            "protocol": protocol_name,
            "audited": False,  # Will try to infer from available data
            "audit_count": 0,  # Will try to infer from available data
            "launch_date": "",  # Will try to infer from available data
            "jurisdiction": "Unknown",  # Hard to determine automatically
            "type": "Unknown",  # Will try to infer from available data
            "recent_news_flags": 0,  # Not available without external API
            "sentiment": "neutral"  # Not available without external API
        }
        
        # If we have protocol data from DeFiLlama, extract what we can
        if protocol_data:
            # Try to infer audit status from project description or other fields
            # This is a simplified approach - in practice, you might want to maintain
            # a small database of known audited protocols
            known_audited_protocols = {
                "aave", "compound", "maker", "uniswap", "curve", "sushi", "balancer",
                "yearn", "convex", "aura", "rocketpool", "lido", "frax", "olympusdao"
            }
            
            if protocol_name in known_audited_protocols:
                metadata["audited"] = True
                metadata["audit_count"] = 3  # Assumed average
            
            # Try to infer protocol type from name or category
            protocol_name_lower = protocol_name.lower()
            if any(keyword in protocol_name_lower for keyword in ["lend", "borrow", "vault"]):
                metadata["type"] = "lending"
            elif any(keyword in protocol_name_lower for keyword in ["swap", "dex", "trade"]):
                metadata["type"] = "dex"
            elif any(keyword in protocol_name_lower for keyword in ["farm", "yield"]):
                metadata["type"] = "yield_aggregator"
            elif any(keyword in protocol_name_lower for keyword in ["liquid", "staking"]):
                metadata["type"] = "liquid_staking"
            else:
                metadata["type"] = "other"
            
            # Try to estimate launch date based on TVL history if available
            # This is a very rough approximation
            if "chainTvls" in protocol_data:
                # This would require more complex logic to determine actual launch date
                # For now, we'll leave it empty
                pass
        
        return metadata
    
    def enrich_protocols(self, protocols: List[Dict]) -> List[Dict]:
        """
        Enrich a list of protocols with metadata derived from DeFiLlama data.
        
        Args:
            protocols: List of protocol data from DeFiLlama
            
        Returns:
            List of dictionaries with enriched protocol data
        """
        enriched_data = []
        for protocol in protocols:
            # Extract protocol name
            protocol_name = protocol.get("project", "")
            # Get metadata based on protocol data
            metadata = self.get_protocol_metadata(protocol_name, protocol)
            # Combine original protocol data with metadata
            enriched_protocol = protocol.copy()
            enriched_protocol.update(metadata)
            enriched_data.append(enriched_protocol)
        return enriched_data

# Example usage
if __name__ == "__main__":
    fetcher = ProtocolMetadataFetcher()
    # In practice, this would come from DeFiLlama client
    sample_protocols = [
        {"project": "aave", "category": "Lending"},
        {"project": "uniswap", "category": "Dexes"},
        {"project": "curve", "category": "Dexes"}
    ]
    enriched_data = fetcher.enrich_protocols(sample_protocols)
    for data in enriched_data:
        print(f"Protocol: {data['project']}")
        print(f"  Audited: {data['audited']}")
        print(f"  Type: {data['type']}")
        print(f"  Jurisdiction: {data['jurisdiction']}")
        print()