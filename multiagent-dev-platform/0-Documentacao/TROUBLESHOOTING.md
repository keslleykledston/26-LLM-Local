# Troubleshooting

## Problemas Comuns

### 1. Orchestrator nao consegue conectar ao Ollama

**Sintoma**: Logs mostram "Connection refused" ou timeout ao chamar Ollama

**Solucao**:
- Verifique se o Ollama esta rodando: `ollama list`
- No Mac/Windows com Docker Desktop, use `host.docker.internal` no .env
- No Linux, use IP da interface docker0 ou `172.17.0.1`
- Teste a conexao: `curl http://host.docker.internal:11434/api/tags`

```bash
# Testar do container
docker-compose exec orchestrator curl http://host.docker.internal:11434/api/tags
```

### 2. Qdrant nao inicializa

**Sintoma**: Orchestrator nao consegue criar collections

**Solucao**:
```bash
# Verificar logs do Qdrant
docker-compose logs qdrant

# Reiniciar servico
docker-compose restart qdrant

# Se necessario, remover volumes
docker-compose down -v
docker-compose up -d
```

### 3. PostgreSQL nao aceita conexoes

**Sintoma**: "Connection refused" no banco de dados

**Solucao**:
```bash
# Verificar se esta rodando
docker-compose ps postgres

# Ver logs
docker-compose logs postgres

# Conectar manualmente para testar
docker-compose exec postgres psql -U multiagent -d multiagent
```

### 4. Frontend nao carrega

**Sintoma**: Erro 404 ou pagina em branco

**Solucao**:
```bash
# Verificar logs
docker-compose logs web_ui

# Rebuild
docker-compose up -d --build web_ui

# Verificar se node_modules foi copiado
docker-compose exec web_ui ls -la node_modules
```

### 5. Missao fica "stuck" em "planning" ou "executing"

**Sintoma**: Status nao muda apos muito tempo

**Solucao**:
```bash
# Verificar logs do orchestrator
docker-compose logs -f orchestrator

# Cancelar missao via API
curl -X POST http://localhost:8001/api/v1/missions/{mission_id}/cancel

# Reiniciar orchestrator
docker-compose restart orchestrator
```

### 6. Timeout ao gerar plano

**Sintoma**: "Ollama request timed out"

**Solucao**:
- Aumentar timeout no .env: `OLLAMA_TIMEOUT=600`
- Usar modelo mais leve: `OLLAMA_MODEL=llama2:7b`
- Verificar recursos da maquina (RAM, CPU)

### 7. Erro de permissao em logs/temp

**Sintoma**: "Permission denied" ao escrever logs

**Solucao**:
```bash
# Ajustar permissoes no host
chmod 777 apps/orchestrator_api/logs
chmod 777 apps/orchestrator_api/temp

# Ou rebuild container
docker-compose up -d --build orchestrator
```

### 8. SSE nao funciona (frontend ainda faz polling)

**Sintoma**: Frontend nao recebe atualizacoes em tempo real

**Solucao**:
- Implementar consumidor SSE no frontend (ainda nao feito)
- Por enquanto, polling funciona normalmente
- Endpoint disponivel: GET /api/v1/missions/stream

## Comandos Uteis

### Ver logs em tempo real
```bash
docker-compose logs -f
docker-compose logs -f orchestrator
docker-compose logs -f web_ui
```

### Reiniciar servico especifico
```bash
docker-compose restart orchestrator
docker-compose restart qdrant
```

### Acessar shell do container
```bash
docker-compose exec orchestrator bash
docker-compose exec web_ui sh
```

### Limpar tudo e recomear
```bash
docker-compose down -v
docker system prune -a
docker-compose up -d --build
```

### Verificar saude dos servicos
```bash
curl http://localhost:8001/api/v1/health/
```

### Testar API manualmente
```bash
# Criar missao
curl -X POST http://localhost:8001/api/v1/missions/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test mission",
    "description": "This is a test mission to verify the system"
  }'

# Listar missoes
curl http://localhost:8001/api/v1/missions/

# Ver detalhes
curl http://localhost:8001/api/v1/missions/1

# Ver tarefas
curl http://localhost:8001/api/v1/missions/1/tasks

# Cancelar
curl -X POST http://localhost:8001/api/v1/missions/1/cancel
```

## Performance

### Missoes demoram muito

- Verifique modelo Ollama (modelos maiores = mais lento)
- Aumente recursos do Docker (Settings > Resources)
- Use SSD ao inves de HDD
- Feche outros aplicativos pesados

### Alto uso de memoria

- Limite recursos no docker-compose.yml
- Use modelos menores do Ollama
- Reduza `max_concurrent_tasks` em orchestrator.py (padrao: 3)

## Observabilidade

### Logs estruturados

Os logs seguem o formato:
```
[TIMESTAMP] [LEVEL] [MODULE] Message
```

Niveis:
- DEBUG: Detalhes internos
- INFO: Operacoes normais
- WARNING: Situacoes nao ideais mas nao criticas
- ERROR: Falhas que podem ser recuperadas
- CRITICAL: Falhas fatais

### Metricas importantes

- Tempo de resposta do Ollama (deve ser < 30s para prompts simples)
- Tempo de embedding (deve ser < 5s)
- Taxa de sucesso de missoes (deve ser > 80%)
- Tempo medio de validacao (lint + test + build)
