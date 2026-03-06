import os
import json
from typing import Dict, Optional
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

class LLMQueryParser:
    def __init__(self):
        """Initialize the LLM query parser with API configuration."""
        self.api_key = os.getenv("GROK_API_KEY")
        self.api_url = "https://api.x.ai/v1/chat/completions"
        self.model = os.getenv("LLM_MODEL", "grok-beta")
        
        # Headers for API requests
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def parse_query(self, user_query: str) -> Dict:
        """
        Parse the user query to extract structured parameters using LLM.
        
        Args:
            user_query: The natural language query from the user
            
        Returns:
            Dictionary with extracted parameters
        """
        # Create the prompt for the LLM
        prompt = f"""
        Extract structured information from the following DeFi investment query.
        Respond ONLY with a JSON object containing the extracted information.
        
        Query: "{user_query}"
        
        Extract these fields:
        - amount: numerical amount mentioned (or null if not specified)
        - token: cryptocurrency token symbol (e.g., USDC, ETH, DAI) or null if not specified
        - chain: blockchain network (e.g., Ethereum, Polygon, Arbitrum) or null if not specified
        - risk_tolerance: one of "conservative", "moderate", or "aggressive"
        
        Example response format:
        {{
            "amount": 1000.0,
            "token": "USDC",
            "chain": "Ethereum",
            "risk_tolerance": "conservative"
        }}
        
        If a field is not mentioned in the query, set it to null (for amount/token/chain) 
        or "moderate" (for risk_tolerance).
        """
        
        # Prepare the API request
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that extracts structured data from DeFi investment queries."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "response_format": {"type": "json_object"}
        }
        
        try:
            # Make the API request
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            # Parse the response
            result = response.json()
            parsed_data = json.loads(result["choices"][0]["message"]["content"])
            
            # Set defaults for missing values
            if "risk_tolerance" not in parsed_data or not parsed_data["risk_tolerance"]:
                parsed_data["risk_tolerance"] = "moderate"
            
            return parsed_data
            
        except Exception as e:
            print(f"Error parsing query with LLM: {e}")
            # Return default values if LLM parsing fails
            return {
                "amount": None,
                "token": None,
                "chain": None,
                "risk_tolerance": "moderate"
            }

# Example usage
if __name__ == "__main__":
    parser = LLMQueryParser()
    query = "Show me low-risk DeFi opportunities for staking 1000 USDC on Ethereum"
    result = parser.parse_query(query)
    print(result)