# ADR-0004 – Uso Controlado de IA Externa

## Status
Aceito

## Contexto
Modelos externos possuem custo e risco de vazamento de contexto.

## Decisão
Adotar política offline-first:

IA externa só pode ser usada se:
1. LLM local falhar ou tiver baixa confiança
2. RAG não retornar contexto suficiente
3. Houver justificativa técnica explícita
4. Estiver dentro do orçamento da missão

IA externa é proibida para:
- Geração de código principal
- Escrita de segredos
- Análise completa de repositório

## Consequências
- Economia real de tokens pagos
- Maior governança e previsibilidade
