# Guia Docker

Documentação completa para executar a aplicação usando Docker e Docker Compose.

## 📋 Arquitetura Docker

O projeto utiliza uma arquitetura multi-container com:

### Backend Container
- **Base:** `python:3.10-slim`
- **Porta:** 8000
- **Funcionalidades:**
  - Servidor FastAPI com WebSocket
  - Pool de conexões em memória
  - Health check em `/health`

### Frontend Container
- **Build Stage:** `node:18-alpine` (compilação TypeScript/Vite)
- **Production Stage:** `nginx:alpine` (servir arquivos estáticos)
- **Porta:** 80 (mapeada para 3000 no host)
- **Funcionalidades:**
  - Servir aplicação React buildada
  - Proxy reverso para backend (WebSocket + API)
  - Configuração otimizada do Nginx

## 🚀 Quick Start

```bash
# Clone o repositório
git clone https://github.com/jvcostta/websocket-broadcast-server.git
cd websocket-broadcast-server

# Inicie tudo com um comando (build automático na primeira vez)
docker-compose up -d
```

> **💡 Nota:** O comando `docker-compose up -d` automaticamente faz o build das imagens na primeira execução. Você não precisa executar `docker-compose build` separadamente, a menos que queira forçar um rebuild após mudanças no código.

**Pronto!** Acesse:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📦 Estrutura de Arquivos Docker

```
.
├── docker-compose.yml          # Orquestração dos serviços
├── .dockerignore               # Arquivos ignorados no build
├── backend/
│   ├── Dockerfile              # Imagem do backend Python
│   └── .dockerignore           # Ignora venv, cache, etc
└── frontend/
    ├── Dockerfile              # Build multi-stage
    ├── nginx.conf              # Configuração Nginx
    └── .dockerignore           # Ignora node_modules, dist, etc
```

## 🔧 Comandos Docker Compose

### Gerenciamento Básico

```bash
# Iniciar containers em background
docker-compose up -d

# Parar containers (mantém dados)
docker-compose stop

# Parar e remover containers
docker-compose down

# Ver status dos containers
docker-compose ps

# Ver logs em tempo real
docker-compose logs -f

# Ver logs de um serviço específico
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Rebuild e Atualização

```bash
# Rebuildar após mudanças no código
docker-compose up -d --build

# Forçar recriação de containers
docker-compose up -d --force-recreate

# Rebuildar apenas um serviço
docker-compose build backend
docker-compose build frontend
```

### Execução de Comandos

```bash
# Acessar shell do container backend
docker-compose exec backend /bin/bash

# Executar testes (os testes estão em /tests/ dentro do container)
docker-compose exec backend pytest /tests/ -v

# Testes com cobertura
docker-compose exec backend pytest /tests/backend/ --cov=/app --cov-report=html

# Copiar relatório de cobertura para host
docker cp websocket-backend:/app/htmlcov ./htmlcov

# Ver variáveis de ambiente
docker-compose exec backend env

# Instalar dependência adicional (temporário)
docker-compose exec backend pip install nome-do-pacote
```

### Limpeza

```bash
# Parar e remover containers, redes
docker-compose down

# Remover também volumes
docker-compose down -v

# Remover imagens criadas
docker-compose down --rmi all

# Limpeza completa do Docker (cuidado!)
docker system prune -a
```

## 🏗️ Arquitetura de Rede

```
┌─────────────────────────────────────┐
│         Host Machine                │
│                                     │
│  Browser ──> localhost:3000         │
│         ──> localhost:8000          │
└──────────────┬──────────────────────┘
               │
      ┌────────┴────────┐
      │ Docker Network  │
      │ (websocket-net) │
      └────────┬────────┘
               │
       ┌───────┴────────┐
       │                │
  ┌────▼─────┐   ┌─────▼─────┐
  │ Frontend │   │  Backend  │
  │ (nginx)  │   │ (FastAPI) │
  │  :80     │   │  :8000    │
  └────┬─────┘   └───────────┘
       │
       │ Proxy Pass
       └──> /ws/* ──> backend:8000/ws/*
       └──> /api/* ──> backend:8000/*
```

## 🔍 Health Checks

Ambos os containers possuem health checks configurados:

**Backend:**
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
```

**Frontend:**
```yaml
healthcheck:
  test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost/"]
  interval: 30s
  timeout: 10s
  retries: 3
```

Ver status:
```bash
docker-compose ps
```

## 🐛 Troubleshooting

### Container não inicia

```bash
# Ver logs detalhados
docker-compose logs backend
docker-compose logs frontend

# Verificar configuração
docker-compose config
```

### Porta já em uso

```bash
# Ver processos usando a porta
# Windows
netstat -ano | findstr :3000
netstat -ano | findstr :8000

# Linux/Mac
lsof -i :3000
lsof -i :8000

# Matar processo (Windows)
taskkill /PID <pid> /F
```

### Rebuild não funciona

```bash
# Limpar cache do build
docker-compose build --no-cache

# Remover imagens antigas
docker-compose down --rmi all
docker-compose up -d --build
```

### WebSocket não conecta

Verifique se o Nginx está fazendo proxy corretamente:

```bash
# Acessar container do frontend
docker-compose exec frontend sh

# Ver configuração do Nginx
cat /etc/nginx/conf.d/default.conf

# Testar configuração
nginx -t
```

### Mudanças no código não aparecem

```bash
# Backend: precisa rebuild
docker-compose up -d --build backend

# Frontend: precisa rebuild (multi-stage)
docker-compose up -d --build frontend
```

## 📊 Monitoramento

### Uso de Recursos

```bash
# Ver uso de CPU/Memória/Rede
docker stats

# Apenas containers do projeto
docker stats websocket-backend websocket-frontend
```

### Logs Estruturados

```bash
# Últimas 100 linhas
docker-compose logs --tail=100

# Seguir logs com timestamp
docker-compose logs -f -t

# Filtrar por severidade (se configurado)
docker-compose logs | grep ERROR
```

## 🔐 Segurança

### Boas Práticas Implementadas

- ✅ Multi-stage builds (reduz tamanho da imagem final)
- ✅ Usuário não-root no Nginx
- ✅ .dockerignore para não incluir arquivos sensíveis
- ✅ Health checks configurados
- ✅ Restart policy: `unless-stopped`
- ✅ Rede isolada para comunicação entre containers

### Melhorias para Produção

```yaml
# Adicionar secrets
secrets:
  db_password:
    file: ./secrets/db_password.txt

# Limitar recursos
deploy:
  resources:
    limits:
      cpus: '0.5'
      memory: 512M
    reservations:
      cpus: '0.25'
      memory: 256M

# Adicionar autenticação ao backend
environment:
  - API_KEY=${API_KEY}
```

## 📝 Variáveis de Ambiente

Edite `docker-compose.yml` para adicionar variáveis:

```yaml
services:
  backend:
    environment:
      - PYTHONUNBUFFERED=1
      - LOG_LEVEL=INFO
      - MAX_CONNECTIONS=100
      
  frontend:
    environment:
      - NGINX_HOST=localhost
      - NGINX_PORT=80
```

## 🚀 Deploy em Produção

### Docker Swarm

```bash
# Inicializar swarm
docker swarm init

# Deploy da stack
docker stack deploy -c docker-compose.yml websocket

# Ver serviços
docker service ls

# Escalar serviço
docker service scale websocket_backend=3
```

### Kubernetes

Converter para Kubernetes:
```bash
# Instalar kompose
curl -L https://github.com/kubernetes/kompose/releases/download/v1.26.0/kompose-linux-amd64 -o kompose

# Converter
kompose convert -f docker-compose.yml

# Aplicar no cluster
kubectl apply -f .
```

## 📚 Referências

- [Documentação Docker](https://docs.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Multi-stage builds](https://docs.docker.com/build/building/multi-stage/)
- [Nginx Docker](https://hub.docker.com/_/nginx)
- [Python Docker](https://hub.docker.com/_/python)

---

Última atualização: 16 de Janeiro de 2026
