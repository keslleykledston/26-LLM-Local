# 🤖 Multiagent Dev Platform

> **A local-first, multiagent development platform powered by Ollama**

Build production-quality applications using specialized AI agents running entirely on your machine, with controlled fallback to external AI only when necessary.

---

## 🎯 Key Features

- **🏠 Local-First**: Runs entirely offline using Ollama (no external API costs by default)
- **🧠 Long-Term Memory**: RAG-powered knowledge base using Qdrant vector database
- **👥 Specialized Agents**: Frontend, Backend, Database, QA experts working together
- **🔒 Controlled External AI**: Optional fallback to Claude/ChatGPT/Gemini with strict approval
- **✅ Quality Assured**: Automatic linting, testing, and building before integration
- **📚 Knowledge Base**: ADRs, playbooks, code snippets stored and retrieved via RAG

---

## 🏗️ Architecture

### Pipeline
Every mission follows a fixed 5-phase pipeline:

```
PLAN → EXECUTE → VALIDATE → INTEGRATE → MEMORY
  ↓        ↓          ↓           ↓         ↓
Query    Delegate   Lint/Test   Git      Update
 RAG     to Agents    Build    Commit     RAG
```

### Stack
- **Backend**: FastAPI (Python)
- **Frontend**: Next.js (TypeScript)
- **Local LLM**: Ollama (Llama 3.1, CodeLlama, etc.)
- **Vector DB**: Qdrant
- **Database**: PostgreSQL
- **Containerization**: Docker Compose

---

## 🚀 Quick Start

### Prerequisites
- **macOS** (tested on MacBook Pro)
- **Docker** & **Docker Compose**
- **Ollama** (install from [ollama.ai](https://ollama.ai))
- **Node.js 20+**
- **Python 3.11+**

### Installation

1. **Clone the repository**
```bash
cd /path/to/your/projects
git clone <your-repo-url> multiagent-dev-platform
cd multiagent-dev-platform
```

2. **Install Ollama models**
```bash
# Install the primary model (choose one)
ollama pull llama3.1:latest
# OR for code-specific tasks
ollama pull codellama:latest

# Install embedding model
ollama pull nomic-embed-text
```

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env and set your preferences
```

4. **Start services**
```bash
cd infra/docker
docker-compose up -d
```

5. **Access the platform**
- **Web UI**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Qdrant Dashboard**: http://localhost:6333/dashboard

---

## 📖 Usage

### Creating a Mission

**Via Web UI:**
1. Open http://localhost:3000
2. Fill in mission title and description
3. Click "Create Mission"
4. Watch agents execute the pipeline

**Via API (curl):**
```bash
curl -X POST http://localhost:8000/api/v1/missions/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Add user authentication",
    "description": "Implement JWT-based authentication with login and signup endpoints. Include password hashing, token refresh, and protected routes.",
    "created_by": "user"
  }'
```

**Via Python:**
```python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/api/v1/missions/",
        json={
            "title": "Optimize database queries",
            "description": "Add indexes to user and posts tables. Optimize N+1 queries in the feed endpoint.",
        }
    )
    mission = response.json()
    print(f"Mission #{mission['id']} created!")
```

---

## 🤖 Available Agents

| Agent | Expertise | Tools |
|-------|-----------|-------|
| **Orchestrator** | Planning, coordination, pipeline management | All tools |
| **Frontend Developer** | React, Next.js, TypeScript, Tailwind CSS | repo, git, npm |
| **Backend Developer** | Python, FastAPI, APIs, business logic | repo, git, python |
| **Database Specialist** | SQL, indexes, performance, data modeling | repo, database |
| **QA + UX** | Testing, validation, accessibility, UX | repo, test, lint |
| **DevOps** (optional) | Docker, CI/CD, deployment | repo, docker, shell |
| **Security** (optional) | Security audits, vulnerability scanning | repo, security_scan |
| **Documentation** (optional) | README, docs, comments, ADRs | repo, git |

---

## 🧠 Long-Term Memory (RAG)

The platform learns from every mission and stores knowledge in Qdrant for semantic search.

### Memory Types

```
memory/
├── adrs/              # Architecture Decision Records
├── playbooks/         # Step-by-step guides
├── snippets/          # Code snippets
└── domain-glossary/   # Domain terminology
```

### How It Works

1. **Query**: When planning a mission, the orchestrator queries RAG with the mission description
2. **Retrieve**: Top-k relevant documents are retrieved from Qdrant (semantic search)
3. **Inject**: Retrieved context is injected into agent prompts
4. **Update**: After mission completion, a summary is created and (after approval) embedded

### Managing Memory

**Add a new playbook:**
```bash
curl -X POST http://localhost:8000/api/v1/memory/ \
  -H "Content-Type: application/json" \
  -d '{
    "type": "playbook",
    "title": "Setting up Redis caching",
    "content": "Step 1: Install redis...",
    "category": "infrastructure",
    "tags": ["redis", "caching", "performance"],
    "approved": true
  }'
```

**Search memory:**
```bash
curl -X POST http://localhost:8000/api/v1/memory/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How to optimize database queries?",
    "limit": 5
  }'
```

---

## 🌐 External AI (Controlled Fallback)

### When to Use
External AI should **ONLY** be used when:
1. Local LLM lacks specific knowledge (e.g., recent library changes)
2. RAG memory returns insufficient context
3. Agent justifies technical necessity
4. Request is approved and logged

### Configuration

Edit `.env`:
```bash
# Enable Claude
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_ENABLED=true

# Enable OpenAI
OPENAI_API_KEY=sk-...
OPENAI_ENABLED=true

# Policy
REQUIRE_APPROVAL_FOR_EXTERNAL_AI=true
CACHE_EXTERNAL_AI_RESPONSES=true
MAX_EXTERNAL_AI_COST_PER_MISSION_USD=5.00
```

### Registry
External AI providers are configured in `external_ai/registry.yaml`:
- Allowed scopes (what they can be used for)
- Forbidden scopes (what they cannot do)
- Cost limits
- Token limits

### Approval Workflow
1. Agent requests external AI with justification
2. Request is logged to database
3. If `REQUIRE_APPROVAL_FOR_EXTERNAL_AI=true`, waits for user approval
4. User approves via UI or API
5. External AI is called
6. Response is cached and logged

---

## ✅ Validation Pipeline

Every mission must pass validation before integration:

### Checks
- **Lint**: Code style and quality (eslint, flake8, black)
- **Test**: Unit and integration tests (pytest, jest)
- **Build**: Successful compilation (npm build, webpack)

### Configuration
The runner automatically detects your project setup:
- Looks for `npm run lint`, `pytest`, `npm run build`
- Configures defaults if not found
- Fails mission if any validation fails

---

## 🛠️ Development

### Running Locally (without Docker)

**Backend:**
```bash
cd apps/orchestrator_api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd apps/web_ui
npm install
npm run dev
```

**Qdrant:**
```bash
docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant
```

**PostgreSQL:**
```bash
docker run -p 5432:5432 -e POSTGRES_PASSWORD=multiagent_dev_2024 postgres:16-alpine
```

### Adding a New Agent

1. Create agent class in `apps/orchestrator_api/app/agents/`
2. Inherit from `BaseAgent`
3. Implement `execute_task()` and `get_system_prompt()`
4. Register with `AgentFactory.register_agent()`

Example:
```python
from app.agents.base import BaseAgent, AgentFactory

class SecurityAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.agent_type = "security"
        self.agent_name = "Security Reviewer"

    def get_system_prompt(self) -> str:
        return "You are a security expert..."

    async def execute_task(self, task):
        # Implementation here
        pass

# Register
AgentFactory.register_agent("security", SecurityAgent)
```

---

## 📊 API Reference

### Missions
- `POST /api/v1/missions/` - Create mission
- `GET /api/v1/missions/` - List missions
- `GET /api/v1/missions/{id}` - Get mission details
- `GET /api/v1/missions/{id}/tasks` - Get mission tasks
- `POST /api/v1/missions/{id}/cancel` - Cancel mission

### Memory
- `POST /api/v1/memory/` - Add memory item
- `GET /api/v1/memory/` - List memory items
- `POST /api/v1/memory/search` - Semantic search
- `POST /api/v1/memory/{id}/approve` - Approve and embed item

### External AI
- `POST /api/v1/external-ai/request` - Request external AI
- `GET /api/v1/external-ai/calls` - List AI calls
- `POST /api/v1/external-ai/calls/{id}/approve` - Approve AI call
- `GET /api/v1/external-ai/stats` - Usage statistics

### Health
- `GET /api/v1/health/` - System health check
- `GET /api/v1/health/ollama/models` - List Ollama models

Full API documentation: http://localhost:8000/docs

---

## 🔐 Security & Governance

- **No token logging**: API keys are never logged
- **Secret redaction**: Automatic redaction in logs
- **External AI audit**: All external calls logged with justification
- **Offline-only mode**: Force offline operation (`OFFLINE_ONLY_MODE=true`)
- **Environment variables**: Secrets in `.env`, never committed

---

## 🧪 Testing

```bash
# Backend tests
cd apps/orchestrator_api
pytest

# Frontend tests
cd apps/web_ui
npm test

# Integration tests
docker-compose -f infra/docker/docker-compose.test.yml up
```

---

## 📚 Documentation

- **ADRs**: `memory/adrs/` - Architecture decisions
- **Playbooks**: `memory/playbooks/` - How-to guides
- **Glossary**: `memory/domain-glossary/` - Terminology
- **API Docs**: http://localhost:8000/docs (Swagger)

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Ensure tests pass
5. Submit a pull request

---

## 📄 License

MIT License - see LICENSE file for details

---

## 🙏 Acknowledgments

- **Ollama** - Local LLM runtime
- **Qdrant** - Vector database
- **FastAPI** - Python web framework
- **Next.js** - React framework

---

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing ADRs and playbooks
- Review API documentation

---

**Built with ❤️ for local-first, cost-effective AI development**
