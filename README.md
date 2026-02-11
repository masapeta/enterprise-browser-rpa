# Enterprise Agentic RPA Platform

A scalable, production-grade Browser Automation Platform powered by LLMs (Search, Think, Act). This system is designed for high concurrency, strict security, and real-time observability.

## 🚀 Key Features
-   **Autonomous Agents**: Uses LLMs (Grok, Azure OpenAI, GPT-4) to plan and execute web tasks.
-   **Session Isolation**: Every agent runs in a strictly isolated Playwright browser context.
-   **Real-time Observability**: Live logs and screen updates streamed via WebSockets.
-   **Scalable Architecture**: Decoupled Worker nodes (Celery) separate from the API.
-   **Enterprise Ready**: Structured logging, audit trails (MongoDB), and RBAC-ready design.

## 📂 Project Structure
```text
/enterprise-browser-rpa
├── /backend            # FastAPI, Celery, Agent Orchestrator
│   ├── /app            # Application Source
│   ├── /tests          # Functional & Unit Tests
│   ├── .env.example    # Configuration template
│   └── requirements.txt
├── /frontend           # Next.js Dashboard
├── /deployment         # Kubernetes & Docker configurations
└── docker-compose.yml  # Local development stack
```

## 🛠️ Quick Start (Docker)

The easiest way to run the platform is using Docker Compose.

1.  **Configure Environment**:
    ```bash
    cd backend
    cp .env.example .env
    # Edit .env and add your LLM_API_KEY (Grok/Azure/OpenAI)
    ```

2.  **Start Services**:
    ```bash
    docker-compose up --build
    ```
    This starts:
    -   API Gateway (http://localhost:8000)
    -   Worker Nodes
    -   Redis & MongoDB
    -   (Frontend needs to be started separately if not enabled in compose)

3.  **Start Frontend**:
    ```bash
    cd frontend
    npm install
    npm run dev
    ```
    Access dashboard at [http://localhost:3000](http://localhost:3000).

## ⚙️ Manual Setup (No Docker)

### Backend
1.  Navigate to `backend`: `cd backend`
2.  Install dependencies: `pip install -r requirements.txt`
3.  Setup `.env` as above.
4.  Run API: `uvicorn app.main:app --reload`
5.  Run Worker: `celery -A app.worker.celery_app worker --pool=solo` (Windows) or `--pool=prefork` (Linux/Mac).

### Frontend
1.  Navigate to `frontend`: `cd frontend`
2.  Install: `npm install`
3.  Run: `npm run dev`

## 🧠 LLM Configuration

You can switch providers in `backend/.env`:

**Grok (X.AI)**
```ini
LLM_PROVIDER=grok
LLM_BASE_URL=https://api.grok.x.ai/v1
LLM_API_KEY=your_key
LLM_MODEL=grok-1
```

**Azure OpenAI**
```ini
LLM_PROVIDER=azure
LLM_BASE_URL=https://your-resource.openai.azure.com/
LLM_API_KEY=your_key
LLM_MODEL=deployment_name
OPENAI_API_VERSION=2023-05-15
```

## 🧪 Testing
Run the validation suite to verify system logic (mocks external services):
```bash
cd backend
python -m pytest tests/test_functional.py
```
# enterprise-browser-rpa
