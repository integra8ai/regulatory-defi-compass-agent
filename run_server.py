#!/usr/bin/env python3
"""
Script to run the Regulatory DeFi Compass Agent server
"""

import uvicorn
import argparse

def main():
    parser = argparse.ArgumentParser(description="Run the Regulatory DeFi Compass Agent server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=3000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    
    args = parser.parse_args()
    
    print(f"Starting Regulatory DeFi Compass Agent server on {args.host}:{args.port}")
    print("Press CTRL+C to stop the server")
    
    uvicorn.run(
        "src.agent.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info"
    )

if __name__ == "__main__":
    main()