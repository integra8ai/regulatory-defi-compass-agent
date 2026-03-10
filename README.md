# Regulatory DeFi Compass Agent for Warden Protocol 🧭

This is a [Warden Protocol](https://wardenprotocol.org/) community agent designed to help users navigate the Decentralized Finance (DeFi) landscape with a strong focus on regulatory compliance. It assesses and ranks DeFi opportunities by combining real-time yield data with a comprehensive compliance and risk scoring mechanism.

## Features

- Risk-adjusted DeFi yield analysis
- Compliance scoring based on multiple factors (audits, jurisdiction, protocol age, etc.)
- Ranking of opportunities based on risk tolerance
- Natural language query processing
- Integration with DeFiLlama
- Read-only & non-custodial
- Powered by Grok

## Why Regulatory DeFi Compass Matters

With increasing regulatory scrutiny in the DeFi space, users need tools to assess not just yields but also compliance risks. This agent combines:

- Market yield data
- Regulatory compliance metrics
- Risk-adjusted ranking
- Zero custodial risk

Designed for clarity, safety, and informed DeFi investing.

## Tech Stack

- Python
- LangGraph
- FastAPI
- DeFiLlama API
- Grok

## API Endpoints

### Standard FastAPI Endpoints
- `GET /health` - Health check endpoint
- `POST /chat` - Main endpoint for processing user queries

### LangServe Endpoint
- `POST /regulatory-defi-compass-agent/invoke` - LangGraph workflow invocation via LangServe
- `POST /regulatory-defi-compass-agent/stream` - Streaming responses from the workflow
- `GET /regulatory-defi-compass-agent/playground` - Interactive playground for testing

All endpoints share the same agent instance for consistency.

## Running with Docker

### Option 1: Using Docker Compose (Recommended)
```bash
# Copy the example environment file and set your API keys
cp .env.example .env
# Edit .env file to add your actual API keys

# Build and run with environment variables
docker-compose up --build
```

Once running, access the application at `http://localhost:3000`
- Health check: `http://localhost:3000/health`
- Chat endpoint: `http://localhost:3000/chat` (POST requests)
- LangServe playground: `http://localhost:3000/regulatory-defi-compass-agent/playground`

### Option 2: Using Docker directly
```bash
# Build the image
docker build -t regulatory-defi-compass .

# Run with environment file
docker run -p 3000:3000 --env-file .env regulatory-defi-compass

# Or with API key directly
docker run -p 3000:3000 -e GROK_API_KEY=your_api_key_here regulatory-defi-compass
```

Once running, access the application at `http://localhost:3000`
- Health check: `http://localhost:3000/health`
- Chat endpoint: `http://localhost:3000/chat` (POST requests)
- LangServe playground: `http://localhost:3000/regulatory-defi-compass-agent/playground`

## Deploying to LangChain Cloud (LangServe) for Warden Protocol

This agent is designed for deployment as a [LangServe](https://github.com/langchain-ai/langserve) application to [LangChain Cloud](https://www.langchain.com/cloud), enabling seamless integration with the Warden Protocol. This deployment method exposes your agent via API endpoints that can be registered with Warden Protocol.

### Prerequisites
1.  **LangChain Cloud Account**: Sign up at [https://langchain.com/cloud](https://langchain.com/cloud).
2.  **LangServe CLI**: Install the LangServe CLI for deployment:
    ```bash
    pip install "langserve[cli]"
    ```
3.  **Environment Variables**: Prepare your environment variables. Sensitive keys like `GROK_API_KEY` and `WARDEN_PRIVATE_KEY` should be securely managed as secrets in the LangChain Cloud dashboard, not committed to your repository.

### Deployment Steps
1.  **Create LangServe Entry Point**: Ensure you have a `server.py` file (as detailed in the 'LangServe Wrapper' section below) in your agent's root directory that exposes your `ComplianceAgent`'s workflow.

2.  **Login to LangChain Cloud (via CLI)**:
    ```bash
    langserve login
    ```
    Follow the prompts to authenticate your CLI with your LangChain Cloud account.

3.  **Deploy Your Agent to LangChain Cloud**:
    Navigate to your agent's root directory (`regulatory-defi-compass/`) and run:
    ```bash
    langserve deploy --app-dir . --app-file server.py --app-name regulatory-defi-compass-agent --platform langchain
    ```
    *   `--app-dir .`: Specifies the current directory as the application root.
    *   `--app-file server.py`: Points to your LangServe entry point file.
    *   `--app-name regulatory-defi-compass-agent`: A unique name for your deployed application.

4.  **Configure Secrets in LangChain Cloud**: After deployment, navigate to your application in the LangChain Cloud dashboard to configure the following environment variables as secrets:
    *   `GROK_API_KEY`: Your Grok API key.
    *   `DEFILLAMA_API_URL`: `https://yields.llama.fi`
    *   `WARDEN_AGENT_ID`: The ID assigned by the Warden Protocol (if applicable).
    *   `WARDEN_API_URL`: `https://rpc.wardenprotocol.org`
    *   `WARDEN_CHAIN_ID`: `warden-1`
    *   `WARDEN_PRIVATE_KEY`: Your private key for Warden Protocol interactions (store securely).
    *   `LLM_MODEL`: `grok-beta` (or your chosen Grok model).
    *   `LLM_TEMPERATURE`: `0.7`
    *   `WARDEN_LOG_LEVEL`: `info`
    *   `WARDEN_RUN_INTERVAL`: `86400`

### LangServe Entry Point

The `server.py` file in your agent's root directory serves as the entry point for LangChain Cloud deployment. It exposes your `ComplianceAgent` as a LangServe runnable and includes the standard FastAPI endpoints (`/health` and `/chat`).

**Key Features:**
- Uses a singleton pattern to ensure a single agent instance across all endpoints
- Exposes the LangGraph workflow via LangServe at `/regulatory-defi-compass-agent`
- Includes `/health` and `/chat` endpoints from `src.agent.main` for backward compatibility
- All endpoints share the same agent instance for consistency and efficiency

```python
# server.py
from fastapi import FastAPI
from langserve import add_routes
from src.agent.main import get_agent, router as main_router

# Initialize your agent using the singleton pattern
agent_instance, runnable = get_agent()

app = FastAPI(
    title="Regulatory DeFi Compass Agent",
    version="1.0",
    description="A LangServe API for the Regulatory DeFi Compass Agent for Warden Protocol.",
)

# Add the LangGraph runnable as a LangServe route
add_routes(
    app,
    runnable,
    path="/regulatory-defi-compass-agent",
    enable_feedback=True,
    enable_events=True,
)

# Include the /health and /chat endpoints
app.include_router(main_router)
```

This `server.py` serves as the actual entry point for LangServe deployment and ensures all endpoints use the same agent instance.

## Configuration
 
To run the agent locally, create a `.env.example` file in the root directory of your project and copy it to a new file named `.env`. Then add your actual API keys and configurations.
 
**Important**: The `.env` file contains sensitive information (like API keys) and should **NEVER** be committed to version control, especially for public repositories. For deployment to platforms like LangChain Cloud, these variables should be configured as secrets in the platform's dashboard.
 
```bash
# Create a .env file for local development:
cp .env.example .env
# Now, open .env and add your actual API keys and configurations.
```

Ensure your `GROK_API_KEY`, `LLM_MODEL`, and other relevant API keys are correctly set in your `.env` file for local testing.

## Usage Examples

1. "Show me low-risk DeFi opportunities for staking 1000 USDC"
2. "Find high-yield ETH lending protocols with good audit history"
3. "What are the safest DeFi pools for DAI on Polygon?"

## Compliance

- No wallet access
- No transactions
- No financial advice
- Transparent data sourcing

## Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. Run the agent:
   ```bash
   # Method 1: LangServe mode with all endpoints (recommended for production)
   uvicorn server:app --host 0.0.0.0 --port 3000
   
   # Method 2: Standalone FastAPI mode (simpler, for development)
   python run_server.py
   # or
   uvicorn src.agent.main:app --host 0.0.0.0 --port 3000
   
   # Method 3: Development mode with auto-reload
   uvicorn server:app --host 0.0.0.0 --port 3000 --reload
   ```
   
   **Note:** Both modes use the same singleton agent instance. The LangServe mode (`server:app`) includes both LangServe routes and standard FastAPI endpoints, while standalone mode (`src.agent.main:app`) only includes the FastAPI endpoints.
   
4. Access the API:
   - Health check: `http://localhost:3000/health`
   - Chat endpoint: `http://localhost:3000/chat` (POST requests with JSON body)
   
5. Alternative Python scripts for API testing:
   ```bash
   # Health check using Python script
   python health_check.py
   
   # Chat endpoint test using Python script
   python chat_test.py
   
   # Combined API test
   python api_test.py
   
   # Chat test with custom message
   python chat_test.py "Find high-yield ETH lending protocols with good audit history"
   ```

6. Example API usage:
   ```bash
   # Health check
   curl http://localhost:3000/health
   
   # Chat endpoint
   curl -X POST http://localhost:3000/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "Show me low-risk DeFi opportunities for staking USDC on Ethereum"}'
   ```

## Project Structure

```
regulatory-defi-compass/
├── src/
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── agent.py         # Core agent implementation
│   │   ├── graph.py         # LangGraph implementation
│   │   └── main.py          # FastAPI application
│   ├── tools/               # Agent tools and utilities
│   │   ├── __init__.py
│   │   ├── llm_parser.py    # LLM-based query parser
│   │   ├── defillama_client.py  # DeFiLlama API client
│   │   ├── protocol_metadata.py  # Protocol metadata fetcher
│   │   ├── compliance_scorer.py  # Compliance scoring engine
│   │   └── opportunity_ranker.py  # Opportunity ranking algorithm
│   └── __init__.py
├── tests/                  # Test files
│   ├── test_agent.py
│   └── test_simplified_agent.py
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose configuration
├── .env.example            # Example environment variables
├── run_server.py           # Script to run the FastAPI server
├── server.py               # LangServe entry point for LangChain Cloud deployment
├── langgraph.json          # LangGraph configuration
└── README.md               # This file
```
