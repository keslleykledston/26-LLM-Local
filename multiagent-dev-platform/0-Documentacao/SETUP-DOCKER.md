# Setup via Docker

## Pre-requisitos

- Docker e Docker Compose instalados
- Ollama rodando localmente (na maquina host)
- Portas disponiveis: 3000 (frontend), 8001 (backend), 5432 (postgres), 6333 (qdrant)

## Passos para Executar

### 1. Verificar Ollama

Certifique-se que o Ollama esta rodando:

```bash
ollama list
```

Se necessario, baixe os modelos:

```bash
ollama pull llama2
ollama pull nomic-embed-text
```

### 2. Configurar Variaveis de Ambiente

Copie o arquivo de exemplo:

```bash
cd multiagent-dev-platform
cp .env.example .env
```

Edite o `.env` se necessario. As configuracoes padrao devem funcionar.

### 3. Iniciar os Servicos

```bash
cd infra/docker
docker-compose up -d
```

Isso ira iniciar:
- PostgreSQL (porta 5432)
- Qdrant (porta 6333)
- Orchestrator API (porta 8001)
- Web UI (porta 3000)

### 4. Verificar Status

```bash
docker-compose ps
docker-compose logs -f
```

Aguarde ate que todos os servicos estejam "healthy".

### 5. Acessar a Aplicacao

- Frontend: http://localhost:3000
- API Backend: http://localhost:8001
- API Docs: http://localhost:8001/docs
- Qdrant UI: http://localhost:6333/dashboard

## Parar os Servicos

```bash
docker-compose down
```

Para remover volumes (dados do banco):

```bash
docker-compose down -v
```

## Rebuild dos Containers

Se voce fizer mudancas no codigo:

```bash
docker-compose up -d --build
```

## Melhorias Aplicadas

### Backend
- **Async Qdrant**: Migracao para AsyncQdrantClient (nao bloqueia event loop)
- **Paralelismo**: Tarefas sem dependencias executam em paralelo (max 3 concorrentes)
- **Cancelamento**: Suporte a cancelamento efetivo de missoes
- **Resiliencia**: Retry com backoff exponencial para Ollama (3 tentativas)
- **RepoTools**: Respeita .gitignore, usa ripgrep quando disponivel
- **SSE**: Endpoint /stream para atualizacoes em tempo real

### Frontend
- **SSE**: Substituir polling por Server-Sent Events (conectar em /api/v1/missions/stream)
- **Cache otimizado**: Multi-stage build com melhor cache de dependencias

### Docker
- **Multi-stage builds**: Reduz tamanho das imagens
- **Seguranca**: Containers rodam como usuario nao-root
- **Health checks**: Monitoramento automatico de saude dos servicos
- **Build otimizado**: Separacao de dependencias de runtime

### Estrutura
- **.gitignore**: Adicionado no root do projeto
- **Documentacao**: Guias de setup, troubleshooting e melhorias
