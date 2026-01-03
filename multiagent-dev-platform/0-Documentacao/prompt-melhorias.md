# Prompt de Direcionamento de Melhorias

Contexto:
- Repositorio: multiagent-dev-platform (FastAPI + Next.js + Ollama + Qdrant + Postgres).
- Objetivo: otimizar funcionamento da aplicacao, melhorar codigo e funcionalidades, e fortalecer a documentacao.

Tarefa:
Analise o codebase e aplique melhorias nas areas abaixo. Mantenha a abordagem local-first e o pipeline PLAN -> EXECUTE -> VALIDATE -> INTEGRATE -> MEMORY.

Escopo de melhorias (prioridade alta -> baixa):

1) Backend (FastAPI / Orchestrator)
- Otimize o fluxo do orchestrator para permitir execucao paralela de tarefas sem dependencias (ex.: DAG simples), mantendo limites de concorrencia.
- Trate cancelamento de missao de forma efetiva (interromper execucoes em andamento e atualizar status).
- Evite chamadas bloqueantes no event loop: migrar Qdrant para cliente async ou usar threadpool.
- Corrigir retornos incorretos em `MemoryService.get_collection_info` (nome da collection, contagens).
- Melhorar resiliencia: timeouts e retry/backoff para Ollama/Qdrant/External AI.
- Padronizar estados de missao/tarefa com enum/constantes e validar transicoes.

2) Validacao e RunnerTools
- Detectar monorepo: rodar lint/test/build por app (backend e frontend), com caminhos e comandos dedicados.
- Remover o uso de `2>&1` nas strings de comando (ja capturado por subprocess) e retornar logs estruturados.
- Registrar resultados de validacao no banco e expor no endpoint.

3) Repositorio e Ferramentas
- Melhorar RepoTools para respeitar `.gitignore`, evitar varredura em venv/node_modules e usar `rg` quando disponivel.
- Adicionar `.gitignore` (se faltar) para `__pycache__`, `.venv*`, `.next`, `node_modules` e logs.

4) Frontend (Next.js)
- Trocar polling agressivo por atualizacao incremental (SSE/WebSocket) ou intervalo dinamico.
- Usar `react-query` (ja nas deps) para cache, retries e estados de loading/erro.
- Adicionar tela de detalhes da missao (tasks, logs, validacao) e pagina de aprovacao de External AI.
- Exibir erros de API com mensagens claras e fallback de conectividade.

5) DevOps / Docker
- Reduzir tempo de build: separar dependencias de runtime e evitar install pesado no orchestrator quando desnecessario.
- Documentar portas e variaveis em `.env.example` e garantir consistencia com o compose.

6) Documentacao (0-Documentacao)
- Criar guias: Setup local, Setup via Docker, Troubleshooting, Observabilidade/Logs, API e exemplos.
- Incluir um roadmap de melhorias e checklist de validacao.

Regras:
- Nao remover funcionalidades existentes.
- Manter compatibilidade com modo offline-first.
- Evitar dependencias externas desnecessarias.
- Atualizar testes e documentacao conforme as mudancas.

Entrega esperada:
- Mudancas no backend e frontend com foco em performance, estabilidade e UX.
- Documentacao atualizada em `0-Documentacao` com instrucoes objetivas.
- Resumo das melhorias e instrucoes de execucao/validacao.
