import requests
from typing import List, Dict, Optional
import os

# Disable compression to avoid brotli issues
requests.adapters.HTTPAdapter.DEFAULT_POOLSIZE = 10

class DeFiLlamaClient:
    def __init__(self):
        """Initialize the DeFiLlama API client."""
        self.base_url = os.getenv("DEFILLAMA_API_URL", "https://yields.llama.fi")
    
    def fetch_pools(self, chain: Optional[str] = None, token: Optional[str] = None, limit: int = 20) -> List[Dict]:
        """
        Fetch yield pools from DeFiLlama API.
        
        Args:
            chain: Specific blockchain to filter by (optional)
            token: Specific token to filter by (optional)
            limit: Maximum number of pools to return
            
        Returns:
            List of yield pool data
        """
        try:
            # Get all pools
            headers = {
                'Accept-Encoding': 'gzip, deflate',
                'User-Agent': 'Regulatory-DeFi-Compass-Agent/1.0'
            }
            response = requests.get(f"{self.base_url}/pools", headers=headers)
            response.raise_for_status()
            data = response.json()
            pools = data.get("data", []) if isinstance(data, dict) else []
            
            # Filter by chain if specified
            if chain:
                pools = [pool for pool in pools if pool.get("chain", "").lower() == chain.lower()]
            
            # Filter by token if specified
            if token:
                token_lower = token.lower()
                pools = [
                    pool for pool in pools 
                    if token_lower in pool.get("symbol", "").lower() or 
                       token_lower in pool.get("underlyingTokens", [])
                ]
            
            # Sort by APY descending and limit results
            pools.sort(key=lambda x: x.get("apy", 0), reverse=True)
            return pools[:limit]
            
        except Exception as e:
            print(f"Error fetching pools from DeFiLlama: {e}")
            return []
    
    def get_pool_info(self, pool_id: str) -> Dict:
        """
        Get detailed information about a specific pool.
        
        Args:
            pool_id: The unique identifier for the pool
            
        Returns:
            Dictionary with pool information
        """
        try:
            response = requests.get(f"{self.base_url}/pools/chart/{pool_id}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching pool info from DeFiLlama: {e}")
            return {}

# Example usage
if __name__ == "__main__":
    client = DeFiLlamaClient()
    pools = client.fetch_pools(chain="Ethereum", token="USDC", limit=5)
    print(f"Found {len(pools)} pools")
    for pool in pools:
        print(f"- {pool.get('project', '')} {pool.get('symbol', '')}: {pool.get('apy', 0):.2f}%")