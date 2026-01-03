# ADR-0003 – Memória Longa e RAG

## Status
Aceito

## Contexto
Projetos de médio/longo prazo sofrem com perda de contexto,
repetição de decisões e retrabalho.

## Decisão
Implementar memória longa baseada em:

- Documentos versionados em Markdown
- Embeddings armazenados no Qdrant
- Journal relacional para histórico

Tipos de memória:
- ADRs (decisões arquiteturais)
- Playbooks (padrões de trabalho)
- Snippets aprovados
- Glossário de domínio

## Regras
- Apenas conteúdo validado pode ser embeddado
- Logs brutos não entram na memória vetorial
- Resumos são preferidos a dumps

## Consequências
- Redução de tokens e retrabalho
- Comportamento mais consistente dos agentes
