#!/usr/bin/env bash
# generate_memory_pack.sh
# Cria a estrutura memory/ com ADRs + Playbooks + Glossário (Markdown) exatamente como definido.
# Uso:
#   bash generate_memory_pack.sh
#   bash generate_memory_pack.sh --force   # sobrescreve arquivos existentes

set -euo pipefail

FORCE=0
if [[ "${1:-}" == "--force" ]]; then
  FORCE=1
fi

BASE_DIR="memory"
ADR_DIR="${BASE_DIR}/adrs"
PB_DIR="${BASE_DIR}/playbooks"

mkdir -p "$ADR_DIR" "$PB_DIR"

write_file() {
  local path="$1"
  local content="$2"

  if [[ -f "$path" && "$FORCE" -ne 1 ]]; then
    echo "SKIP (já existe): $path  (use --force para sobrescrever)"
    return 0
  fi

  # Garante diretório
  mkdir -p "$(dirname "$path")"
  printf "%s" "$content" > "$path"
  echo "OK: $path"
}

# -------------------------
# ADRs
# -------------------------
write_file "${ADR_DIR}/ADR-0001-stack-tecnologico.md" \
"# ADR-0001 – Stack Tecnológico Principal

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
"

write_file "${ADR_DIR}/ADR-0002-multiagente-orquestracao.md" \
"# ADR-0002 – Arquitetura Multiagente e Orquestração

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
"

write_file "${ADR_DIR}/ADR-0003-memoria-longa-rag.md" \
"# ADR-0003 – Memória Longa e RAG

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
"

write_file "${ADR_DIR}/ADR-0004-uso-ia-externa.md" \
"# ADR-0004 – Uso Controlado de IA Externa

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
"

write_file "${ADR_DIR}/ADR-0005-quality-gates.md" \
"# ADR-0005 – Quality Gates Obrigatórios

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
"

# -------------------------
# Playbooks
# -------------------------
write_file "${PB_DIR}/playbook-desenvolvimento.md" \
"# Playbook – Desenvolvimento

## Princípios
- Pequenas mudanças
- Commits claros
- Código legível > código esperto

## Regras
- Uma feature = uma missão
- Não misturar refactor com feature
- Sempre ler memória antes de codar

## Estrutura padrão
- Backend: routers / services / tools
- Frontend: pages / components / hooks

## Anti-padrões
- Código sem testes
- Lógica duplicada
- Configuração hardcoded
"

write_file "${PB_DIR}/playbook-testes.md" \
"# Playbook – Testes

## Backend
- pytest
- Cobrir:
  - endpoints
  - regras de negócio
  - falhas esperadas

## Frontend
- Testes de renderização básica
- Smoke test de fluxo principal

## Regras
- Teste falhou → não integrar
- Teste flaky deve ser corrigido ou removido
"

write_file "${PB_DIR}/playbook-ux-ui.md" \
"# Playbook – UX / UI

## Objetivo
Interfaces simples, previsíveis e auditáveis.

## Regras
- Mensagens claras
- Erros explicativos
- Estados visíveis (loading, erro, sucesso)

## Acessibilidade mínima
- Labels em inputs
- Navegação por teclado
- Contraste aceitável
"

write_file "${PB_DIR}/playbook-seguranca.md" \
"# Playbook – Segurança

## Regras básicas
- Nunca logar tokens
- Usar variáveis de ambiente
- Redigir segredos automaticamente

## API
- Rate limit básico
- Validação de payload
- Erros sem stack trace exposto

## IA Externa
- Nunca enviar código completo
- Nunca enviar dados sensíveis
"

write_file "${PB_DIR}/playbook-versionamento.md" \
"# Playbook – Versionamento

## Git
- main: estável
- feature/*: missões
- fix/*: correções rápidas

## Commits
- Mensagens claras
- Um commit por responsabilidade

## Histórico
- Não reescrever história compartilhada
"

# -------------------------
# Glossário
# -------------------------
write_file "${BASE_DIR}/domain-glossary.md" \
"# Glossário de Domínio

## Missão
Unidade de trabalho criada pelo usuário.

## Orquestrador
Agente responsável por planejar, delegar e validar.

## Agente
Entidade especializada com escopo limitado.

## Memory / RAG
Base de conhecimento persistente do projeto.

## Quality Gate
Validação automática obrigatória antes da integração.

## IA Externa
Modelo cloud usado apenas como fallback controlado.
"

echo
echo "✅ Pacote criado em: ${BASE_DIR}/"
echo "Dica: rode novamente com --force se quiser sobrescrever arquivos."
