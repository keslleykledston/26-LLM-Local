# Correcoes de instalacao

- Falha ao instalar dependencias do backend com Python 3.14: `psycopg2-binary` tentou compilar e exigiu `pg_config`.
- Correcao aplicada: criado o ambiente virtual `.venv-3.11` (Python 3.11, conforme README) e a instalacao foi refeita nesse ambiente.
- Correcao aplicada: remocao da instalacao local (venv/node_modules/.next/logs) e troca para instalacao via Docker conforme solicitado.
- Correcao aplicada: pinagem de `torch` CPU-only no Linux para evitar downloads massivos de CUDA no build Docker.
- Correcao aplicada: ajuste do healthcheck do Qdrant (sem `wget` no container) para usar `bash` + `/dev/tcp`.
- Correcao aplicada: porta do orchestrator alterada para `8001` para evitar conflito com container ja usando `8000`.
