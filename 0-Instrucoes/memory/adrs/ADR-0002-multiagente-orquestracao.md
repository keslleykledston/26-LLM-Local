# ADR-0002 – Arquitetura Multiagente e Orquestração

## Status
Aceito

## Contexto
O desenvolvimento assistido por IA precisa ser controlável, auditável
e previsível, evitando comportamento autônomo excessivo.

## Decisão
Implementar arquitetura multiagente com:

- Orquestrador central obrigatório
- Agentes especializados com escopo limitado
- Pipeline fixo:
  PLAN → EXECUTE → VALIDATE → INTEGRATE → MEMORY

## Agentes iniciais
- Orchestrator / Planner
- Frontend Developer
- Backend Developer
- Database Specialist
- QA + UX Specialist

## Consequências
- Nenhum agente atua sem delegação explícita
- Orquestrador é o único com visão global
- Facilita auditoria e repetibilidade
