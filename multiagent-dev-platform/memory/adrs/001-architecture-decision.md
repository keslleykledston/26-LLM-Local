# ADR 001: Local-First Architecture with Controlled External AI

## Status
Accepted

## Context
We need a development platform that:
- Runs primarily on local infrastructure
- Minimizes cloud API costs
- Maintains high quality code generation
- Allows fallback to external AI when necessary

## Decision
We will build a **local-first multiagent platform** with the following architecture:

### Primary Components
1. **Local LLM (Ollama)**: Primary AI engine running locally
2. **Vector Database (Qdrant)**: Long-term memory for RAG
3. **Relational Database (PostgreSQL)**: Audit trail and journal
4. **Specialized Agents**: Frontend, Backend, Database, QA specialists
5. **Orchestrator**: Coordinates agents through PLAN → EXECUTE → VALIDATE → INTEGRATE → MEMORY pipeline

### External AI Policy
External AI providers (Claude, ChatGPT, Gemini) are:
- **Disabled by default**
- **Only used when**:
  - Local LLM lacks specific knowledge
  - RAG returns insufficient context
  - Agent provides technical justification
  - Request is approved and logged
- **Forbidden for**:
  - Generating main application code
  - Replacing local LLM as primary engine

## Consequences

### Positive
- **Cost savings**: 90%+ reduction in AI API costs
- **Privacy**: Code and data stay local
- **Offline capability**: Works without internet
- **Control**: Full transparency over external calls
- **Performance**: Lower latency with local models

### Negative
- **Setup complexity**: Requires Ollama, Docker, models
- **Hardware requirements**: Needs decent CPU/GPU
- **Model limitations**: Local models may be less capable than GPT-4/Claude
- **Maintenance**: Need to update local models

## Implementation Notes
- Use `llama3.1:latest` or `codellama` as default model
- Implement strict approval workflow for external AI
- Cache all external AI responses
- Log every external call with justification
- Set cost limits per mission and per day
