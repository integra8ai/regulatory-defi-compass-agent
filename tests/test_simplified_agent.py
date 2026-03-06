#!/usr/bin/env python3
"""
Test script for the simplified Regulatory DeFi Compass Agent (DeFiLlama only)
"""

import sys
import os

# Add the parent directory to the Python path so we can import from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.tools.protocol_metadata import ProtocolMetadataFetcher

def test_protocol_metadata_fetcher():
    """Test the ProtocolMetadataFetcher with DeFiLlama data"""
    print("Testing ProtocolMetadataFetcher with DeFiLlama data")
    print("=" * 50)
    
    # Initialize the fetcher
    fetcher = ProtocolMetadataFetcher()
    
    # Test with sample protocol data (similar to what DeFiLlama would return)
    sample_protocols = [
        {
            "project": "aave",
            "symbol": "USDC",
            "chain": "Ethereum",
            "apy": 4.5,
            "tvl": 1000000000
        },
        {
            "project": "uniswap",
            "symbol": "ETH-USDC",
            "chain": "Ethereum",
            "apy": 15.2,
            "tvl": 2000000000
        },
        {
            "project": "curve",
            "symbol": "3POOL",
            "chain": "Ethereum",
            "apy": 3.8,
            "tvl": 500000000
        }
    ]
    
    print("Input protocols:")
    for protocol in sample_protocols:
        print(f"  - {protocol['project']}: {protocol['apy']}% APY")
    print()
    
    # Enrich protocols with metadata
    try:
        enriched_protocols = fetcher.enrich_protocols(sample_protocols)
        print("Enriched protocols:")
        for protocol in enriched_protocols:
            print(f"  - {protocol['project']}:")
            print(f"    Audited: {protocol['audited']}")
            print(f"    Type: {protocol['type']}")
            print(f"    APY: {protocol['apy']}%")
            print()
        
        print("Test completed successfully!")
        
    except Exception as e:
        print(f"Error testing ProtocolMetadataFetcher: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_protocol_metadata_fetcher()