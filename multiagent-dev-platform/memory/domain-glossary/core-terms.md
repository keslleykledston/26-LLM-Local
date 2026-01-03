# Core Terms Glossary

## Mission
A development task that follows the orchestrator pipeline (PLAN → EXECUTE → VALIDATE → INTEGRATE → MEMORY). Missions are created by users and executed by specialized agents.

## Agent
A specialized AI worker with specific expertise and tools. Examples: Frontend Developer, Backend Developer, QA Specialist.

## Orchestrator
The main coordinating agent responsible for planning missions, delegating to specialized agents, and ensuring quality through the pipeline.

## RAG (Retrieval-Augmented Generation)
A technique that uses vector search to find relevant context from a knowledge base and inject it into LLM prompts, improving response accuracy and relevance.

## Vector Embedding
A numerical representation of text as a list of floating-point numbers, enabling semantic similarity search.

## Qdrant
The vector database used to store embeddings and perform semantic search for RAG.

## Ollama
A local LLM runtime that allows running large language models (like Llama, CodeLlama) on your own hardware without external API calls.

## ADR (Architecture Decision Record)
A document capturing an important architectural decision, its context, the decision made, and its consequences.

## Playbook
A step-by-step guide for accomplishing a specific technical task, with code examples and best practices.

## External AI
Cloud-based AI providers (Claude, ChatGPT, Gemini) used sparingly as fallback when local LLM lacks specific knowledge. All usage is logged and audited.

## Validation Pipeline
The VALIDATE phase where code is tested with linting, unit tests, and builds before integration. Failures block the mission.

## Task
An individual unit of work within a mission, assigned to a specific agent type.

## Memory Item
Approved content (ADR, playbook, snippet, glossary term) stored in both PostgreSQL and Qdrant for RAG retrieval.
