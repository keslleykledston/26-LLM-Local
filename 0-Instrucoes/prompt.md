Você é um engenheiro de software sênior e arquiteto de plataformas de IA.
Seu objetivo é GERAR um repositório completo chamado:

"multiagent-dev-platform"

Essa plataforma deve rodar LOCALMENTE em macOS (MacBook Pro), utilizando LLM local (Ollama) com
MÚLTIPLOS AGENTES, MEMÓRIA LONGA (RAG) e um MECANISMO CONTROLADO de consulta a IAs externas
(APENAS quando estritamente necessário).

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 OBJETIVO PRINCIPAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Criar uma plataforma de desenvolvimento no estilo "vibe coding profissional",
onde múltiplos agentes especializados cooperam para criar, testar, validar e
integrar código de aplicações Web e SaaS, com:

- Execução local por padrão (offline-first)
- Economia real de tokens pagos
- Memória longa e reutilizável
- Qualidade garantida (testes, lint, build)
- Controle explícito sobre chamadas externas

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚫 REGRA FUNDAMENTAL (OBRIGATÓRIA)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ O sistema NÃO DEVE usar IA externa por padrão.

IA externa só pode ser utilizada se:
1) O orquestrador detectar explicitamente falta de conhecimento local
2) A memória (RAG) não retornar contexto suficiente
3) O agente justificar tecnicamente a necessidade
4) A chamada for registrada, auditável e opcionalmente aprovada

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧠 STACK OBRIGATÓRIA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Backend: Python FastAPI
- UI: Next.js
- LLM Local: Ollama (HTTP local)
- Memória Vetorial: Qdrant (Docker)
- Journal/Histórico: Postgres (Docker) ou SQLite (se justificar)
- Execução local: git, shell, node, python, docker

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧩 AGENTES OBRIGATÓRIOS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Cada agente deve ter:
- system prompt próprio
- ferramentas permitidas
- responsabilidades claras
- limites explícitos

AGENTES:
1) Orchestrator / Planner (obrigatório)
2) Frontend Developer
3) Backend Developer
4) Database / Performance Specialist
5) QA + UX Specialist

AGENTES OPCIONAIS (plugáveis):
- DevOps / SRE
- Security Reviewer
- Documentation Agent

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧠 ORQUESTRADOR – PIPELINE FIXO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
O Orquestrador deve seguir rigorosamente o pipeline:

1) PLAN
   - Quebrar a missão em tarefas
   - Consultar memória longa (RAG)
   - Definir agentes responsáveis

2) EXECUTE
   - Delegar tarefas aos agentes
   - Monitorar execução

3) VALIDATE
   - Rodar lint
   - Rodar testes
   - Rodar build
   - Rejeitar se falhar

4) INTEGRATE
   - Criar branch
   - Commitar mudanças coerentes
   - Atualizar docs

5) MEMORY
   - Registrar resumo
   - Atualizar ADRs
   - Atualizar embeddings aprovados

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧠 MEMÓRIA LONGA (OBRIGATÓRIA)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
A plataforma deve implementar:

📁 /memory/adrs
📁 /memory/playbooks
📁 /memory/snippets
📁 /memory/domain-glossary

Somente conteúdos APROVADOS e VALIDADOS
podem ser embeddados no Qdrant.

A cada missão:
- Buscar contexto relevante (top-k)
- Injetar no prompt dos agentes
- Atualizar memória ao final

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 IA EXTERNA (FALLBACK CONTROLADO)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Criar um SUBSISTEMA DE FERRAMENTAS EXTERNAS, com:

📁 /external_ai/
  - registry.yaml
  - clients/
  - policies/

O sistema deve permitir CADASTRAR múltiplas IAs externas:
- Claude
- ChatGPT
- Gemini
- OpenRouter
- Outras futuramente

Cada ferramenta externa deve ter:
- nome
- tipo
- endpoint
- chave (env)
- custo estimado por token
- escopo permitido
- limite de uso
- flag enabled/disabled

EXEMPLO DE USO:
- "Pesquisar breaking change de lib X"
- "Comparar versão Y vs Z"
- "Validar comportamento recente"

🚫 Proibido:
- Usar IA externa para gerar código principal
- Repetir chamadas externas já respondidas (cache obrigatório)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🛠️ FERRAMENTAS DO ORQUESTRADOR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
O orquestrador deve possuir ferramentas locais:

- Repo tools:
  - ler/escrever arquivos
  - buscar texto
  - aplicar patch

- Git tools:
  - status, diff
  - branch, commit

- Runner tools:
  - executar shell
  - npm test/build/lint
  - pytest

- Memory tools:
  - upsert embeddings
  - query embeddings
  - salvar ADR/playbook

- External AI tools:
  - verificar necessidade
  - solicitar aprovação
  - executar chamada
  - cachear resposta

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 ESTRUTURA DO REPOSITÓRIO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
/apps/orchestrator_api
/apps/web_ui
/packages/shared/prompts
/infra/docker-compose.yml
/infra/scripts/
/memory/
/external_ai/
/repo/ (opcional)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🖥️ UI (NEXT.JS)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
A UI deve permitir:
- Criar missões
- Ver plano
- Ver agentes envolvidos
- Ver logs
- Ver chamadas externas (se houver)
- Aprovar/rejeitar mudanças
- Aprovar uso de IA externa (opcional)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔐 SEGURANÇA E GOVERNANÇA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Nunca logar tokens
- Redação automática de segredos
- Auditoria de chamadas externas
- Modo "offline-only" forçado
- Variáveis em .env.example

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📘 DOCUMENTAÇÃO OBRIGATÓRIA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Gerar README.md com:
- Visão geral
- Arquitetura
- Setup no macOS
- Como adicionar modelos no Ollama
- Como cadastrar IA externa
- Como criar missão
- Como funciona a memória longa
- Exemplos curl

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📤 SAÍDA ESPERADA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Gere TODO o código real (sem placeholders)
- Gere scripts funcionais
- Gere exemplos iniciais de ADRs e playbooks
- Comece criando a árvore de diretórios
- Depois gere os arquivos um a um

NÃO SIMPLIFIQUE.
NÃO OMITA COMPONENTES.
NÃO DEIXE A IA DECIDIR QUANDO USAR CLOUD SEM JUSTIFICATIVA.

Comece agora.
