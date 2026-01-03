# ADR-0001 – Stack Tecnológico Principal

## Status
Aceito

## Contexto
A plataforma multiagente precisa operar localmente em macOS (MacBook Pro),
com baixo custo de operação, alta previsibilidade e possibilidade de expansão
para ambientes Linux no futuro.

## Decisão
Adotamos o seguinte stack:

- Backend: Python + FastAPI
- UI: Next.js (React)
- LLM Local: Ollama (HTTP local)
- Memória Vetorial: Qdrant
- Journal/Historico: Postgres (Docker)
- Infra local: Docker Compose
- Execução: git + shell + runners locais

## Justificativa
- Python oferece maior maturidade para orquestração e tooling de IA
- FastAPI é simples, rápido e bem suportado
- Next.js atende UI e futura expansão SaaS
- Ollama garante execução offline-first
- Qdrant é leve e ideal para RAG local

## Consequências
- Dependência de GPU impacta performance
- Stack prioriza clareza e governança em vez de hype
