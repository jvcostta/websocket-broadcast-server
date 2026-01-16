# WebSocket Broadcast Server

Sistema de comunicação em tempo real usando WebSockets com broadcast de mensagens entre múltiplos clientes conectados.

[![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=flat&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)

## 📋 Descrição

Implementação de comunicação bidirecional e persistente usando protocolo WebSocket, permitindo que múltiplos clientes enviem e recebam mensagens em tempo real através de um servidor centralizado.

### Backend
- Endpoint WebSocket que mantém pool de conexões ativas em memória
- Broadcast automático: mensagens recebidas são enviadas para todos os outros clientes
- Tratamento de desconexões e reconexões
- Validação de mensagens com Pydantic

### Frontend
- Interface web interativa para envio e recebimento de eventos
- Visualização dual: lista de broadcasts e chat com mensagens enviadas/recebidas
- Métricas em tempo real: total de eventos, eventos enviados, tempo online
- Reconexão automática em caso de falha

## 🚀 Tecnologias

**Backend:**
- Python 3.10+ | FastAPI | Uvicorn | Pydantic | WebSockets

**Frontend:**
- TypeScript | Vite | WebSocket API | CSS3

**Testes:**
- pytest | pytest-asyncio | pytest-cov | httpx

## 🏗️ Estrutura do Projeto

```
websocket-broadcast-server/
├── backend/
│   ├── main.py                 # Servidor FastAPI e endpoint WebSocket
│   ├── connection_manager.py   # Gerenciamento do pool de conexões
│   ├── models.py               # Modelos Pydantic
│   └── requirements.txt        # Dependências Python
├── frontend/
│   ├── src/
│   │   ├── main.ts             # Lógica principal da aplicação
│   │   ├── metrics.ts          # Sistema de métricas
│   │   └── style.css           # Estilos
│   ├── index.html              # Interface web
│   ├── package.json            # Dependências Node.js
│   └── vite.config.ts          # Configuração Vite
├── tests/
│   ├── backend/                # Testes unitários do backend
│   ├── integration/            # Testes de integração
│   ├── pyproject.toml          # Configuração pytest
│   └── run_tests.py            # Script para executar testes
├── docs/
│   ├── TESTING.md              # Documentação de testes
│   └── desafio.md              # Especificação do desafio
├── start.bat                   # Script de inicialização (Windows)
└── start.sh                    # Script de inicialização (Linux/Mac)
```

## 📦 Instalação