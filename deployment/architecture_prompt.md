Design an architecture diagram for a **Scalable Enterprise Agentic RPA Platform** that automates web browser tasks using Large Language Models (LLMs). The system must support high concurrency, real-time observability, and secure execution.

### **1. Core Components**

*   **Frontend (Next.js)**: A React-based Single Page Application (SPA).
    *   **User Actions**: Submit tasks, view active sessions, replay history.
    *   **Real-time Updates**: Connects via **WebSocket** to stream logs and screenshots.
    *   **Tech**: Next.js 14, Tailwind CSS, Lucide Icons.

*   **API Gateway (FastAPI)**: The central control plane.
    *   **Responsibilities**: Authentication, Rate Limiting, Session Management, WebSocket Proxy.
    *   **Endpoints**: `/api/v1/sessions` (REST), `/ws/logs` (WebSocket).
    *   **Dependencies**: Redis (for Pub/Sub), MongoDB (for Metadata).

*   **Task Queue (Redis)**: Decouples the API from the heavy worker processes.
    *   **Job Type**: `agent_task` (contains `url`, `goal`, `session_id`).
    *   **Pattern**: Producer-Consumer (API produces, Workers consume).

*   **Worker Nodes (Celery)**: Horizontally scalable container instances.
    *   **Role**: Execute the long-running Agent loop.
    *   **Agent Orchestrator**: Manages the "Observe -> Think -> Act" cycle.
    *   **Browser Runtime**: Runs **Playwright** (Chromium) in a strictly isolated context (incognito mode) per session.
    *   **LLM Integration**: Calls external AI models (Grok, Azure OpenAI, GPT-4) to determine the next action based on the DOM state.

*   **Data Storage**:
    *   **Redis (Cache/PubSub)**: heavily used for:
        *   **Ephemeral State**: Screenshots, current step info.
        *   **Pub/Sub**: Publishing live events to the API Gateway.
        *   **Distributed Lock**: Ensuring one agent doesn't overwrite another.
    *   **MongoDB (Persistence)**: Stores:
        *   **Audit Logs**: Every click, type, and navigation event.
        *   **Session Results**: Final extraction data.
        *   **User Profiles**: RBAC and settings.

### **2. Data Flow (The "Agent Loop")**

1.  **Submission**: User submits a prompt ("Go to Amazon and find headphones under $50") via Frontend.
2.  **Dispatch**: API generates `session_id`, saves metadata to Mongo, and pushes a job to Redis Queue.
3.  **Execution Start**: A Worker picks up the job, launches a Headless Browser via Playwright.
4.  **Cyclic Process**:
    *   **Observe**: Worker captures HTML snapshot and Screenshot.
    *   **Think**: Orchestrator sends simplified HTML + History to **LLM Service** (e.g., Azure OpenAI).
    *   **Plan**: LLM returns a JSON plan (e.g., `{"action": "click", "selector": "#search-btn"}`).
    *   **Act**: Playwright executes the action on the browser.
    *   **Stream**: Worker publishes the step result (JSON + Image) to **Redis Pub/Sub**.
5.  **Feedback**: API Gateway (subscribed to Redis) pushes the event to the Frontend via WebSocket.
6.  **Persistence**: Worker asynchronously saves the step log to MongoDB.
7.  **Completion**: Loop ends when LLM outputs `{"action": "finish"}` or max steps reached.

### **3. Key Constraints & Qualities**

*   **Isolation**: Each session runs in its own Browser Context. No cookies/local storage shared.
*   **Scalability**: Workers can scale from 1 to 100+ replicas based on Queue depth (HPA).
*   **Resilience**: If a worker crashes, the job is retried (with backoff).
*   **Security**: No direct user access to the browser. All interactions verified by the Orchestrator.
