# Enterprise Agentic RPA Platform - Walkthrough

This document outlines the steps to run and verify the Enterprise Agentic RPA Platform.

## System Overview
- **Backend API**: FastAPI service usually running on port 8000.
- **Worker**: Celery worker for executing agent tasks.
- **Frontend**: Next.js dashboard on port 3000.
- **Infrastructure**: Redis (Broker/State), MongoDB (Logs/Persistence).

## Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for local frontend dev)
- Python 3.11+ (for local backend dev)
- OpenAI API Key

## Quick Start (Docker Compose)

The easiest way to run the entire stack is via Docker Compose.

1.  **Configure Environment**:
    Create a `.env` file in `backend/` using `.env.example` as a template.
    ```env
    # For Grok (X.AI)
    LLM_PROVIDER=grok
    LLM_API_KEY=your_key_here
    LLM_BASE_URL=https://api.grok.x.ai/v1
    
    # For Azure OpenAI
    # LLM_PROVIDER=azure
    # LLM_BASE_URL=https://your-resource.openai.azure.com/
    # LLM_API_KEY=your_key
    # LLM_MODEL=deployment-name
    ```

2.  **Build and Run**:
    ```bash
    docker-compose up --build
    ```
    *Note: If Docker is not running, this command will fail. For verification without Docker, see below.*

3.  **Access the Dashboard**:
    Open [http://localhost:3000](http://localhost:3000).

## Validation & Testing (No Docker Required)

We have implemented a comprehensive test suite that mocks external dependencies (Redis, MongoDB, Browser), allowing you to verify the system logic even if Docker is unavailable.

1.  **Install Test Dependencies**:
    ```bash
    cd backend
    pip install -r requirements.txt
    pip install pytest pytest-asyncio fakeredis openai anthropic celery structlog tenacity httpx
    ```

2.  **Run the Validation Suite**:
    ```bash
    # PowerShell
    $env:PYTHONPATH = "$PWD"
    pytest tests/test_functional.py -v
    ```

    **What this covers:**
    -   **API Health**: key endpoints are responsive.
    -   **Session Creation**: UUID generation and state initialization in (mock) Redis.
    -   **Concurrency**: Simulates 10 concurrent session creation requests to ensure no data collision.

## Manual Verification Steps

### 1. Start a Session
1.  Open the User Interface at `http://localhost:3000`.
2.  In the "New Session" box, enter a task like:
    > "Go to google.com and search for 'Playwright Python'"
3.  Click "Run Agent".

### 2. Monitor execution
-   **Session ID**: You should see a new Session ID appear.
-   **Live Logs**: The log viewer panel should start streaming JSON logs from the backend via WebSocket.

## Architecture Highlights
-   **Isolation**: Every session gets a fresh Playwright Context.
-   **Structured Planning**: Agents use a strict JSON schema for "Think" steps.
-   **Scalability**: Workers can be scaled horizontally using K8s HPA.
-   **Resource Management**: All services have defined CPU/Memory requests and limits.

## Troubleshooting
-   **Docker Not Running**: Use the `pytest` based validation described above.
-   **Import Errors**: Ensure you are in the `backend` directory and generic `PYTHONPATH` is set correctly if running tests from root.
