# ADR-0005 – Quality Gates Obrigatórios

## Status
Aceito

## Contexto
Código gerado por IA sem validação automática gera dívida técnica.

## Decisão
Toda missão deve passar por:

- Lint (Python/JS)
- Testes (unitários e integração)
- Build local
- Smoke test básico

Falha em qualquer gate:
→ missão não é integrada
→ agente deve corrigir antes de prosseguir

## Consequências
- Menos bugs em produção
- Confiança no fluxo “vibe coding”
