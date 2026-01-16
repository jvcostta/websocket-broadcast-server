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

### Pré-requisitos
- Python 3.10+
- Node.js 18+
- pip e npm

### Opção 1: Inicialização Rápida

**Windows:**
```bash
start.bat
```

**Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

Os scripts instalam dependências e iniciam automaticamente backend e frontend.

---

### Opção 2: Instalação Manual

**Backend:**
```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate

pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

## ▶️ Executando a Aplicação

### Backend

```bash
cd backend
python main.py
```

Servidor disponível em:
- **WebSocket:** `ws://localhost:8000/ws/events`
- **API:** `http://localhost:8000`
- **Docs:** `http://localhost:8000/docs`

### Frontend

```bash
cd frontend
npm run dev
```

Interface disponível em: `http://localhost:3000`

### Build de Produção

```bash
cd frontend
npm run build
npm run preview
```

## 🧪 Executando Testes

### Todos os testes (31 testes)

```bash
cd backend
.venv\Scripts\python -m pytest ..\tests\ -v
```

### Testes do backend apenas (26 testes)

```bash
cd backend
.venv\Scripts\python -m pytest ..\tests\backend\ -v
```

### Testes de integração (5 testes)

```bash
cd backend
.venv\Scripts\python -m pytest ..\tests\integration\ -v
```

### Testes com cobertura

```bash
cd backend
.venv\Scripts\python -m pytest ..\tests\backend\ --cov=. --cov-report=html
```

O relatório HTML será gerado em `backend/htmlcov/index.html`

### Script interativo de testes

```bash
cd tests
python run_tests.py
```

Documentação completa em [`docs/TESTING.md`](docs/TESTING.md)

## 🔌 Como Usar

### Interface Web

1. Acesse `http://localhost:3000` com o backend rodando
2. Status "Conectado" indica conexão ativa
3. Digite uma mensagem e clique em "Enviar Evento"
4. Mensagens aparecem em duas visualizações:
   - **Eventos Recebidos (Broadcast):** apenas mensagens de outros clientes
   - **Eventos Modelo Chat:** todas as mensagens (suas à direita, outras à esquerda)
5. Use o botão "Desconectar" para encerrar a conexão manualmente

### Programaticamente

**JavaScript:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/events');

ws.onopen = () => {
    ws.send(JSON.stringify({ message: 'Olá, WebSocket!' }));
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Recebido:', data.message, data.timestamp);
};
```

**Python:**
```python
import asyncio
import websockets
import json

async def client():
    uri = "ws://localhost:8000/ws/events"
    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps({"message": "Olá do Python!"}))
        response = await websocket.recv()
        print(f"Recebido: {response}")

asyncio.run(client())
```

### Formato de Mensagens

**Envio:**
```json
{
  "message": "Conteúdo da mensagem"
}
```

**Recebimento (com timestamp do servidor):**
```json
{
  "message": "Conteúdo da mensagem",
  "timestamp": "2026-01-16T14:30:00.123456"
}
```

## 📊 Endpoints

### HTTP
- `GET /` - Status do servidor
- `GET /health` - Health check com contador de conexões
- `GET /docs` - Documentação interativa Swagger

### WebSocket
- `WS /ws/events` - Endpoint de comunicação bidirecional

## ✨ Funcionalidades

**Backend:**
- ✅ Pool de conexões WebSocket em memória
- ✅ Broadcast automático (exclui remetente)
- ✅ Tratamento de desconexões
- ✅ Validação de mensagens JSON
- ✅ Timestamp do servidor
- ✅ Logging estruturado

**Frontend:**
- ✅ Conexão WebSocket com reconexão automática
- ✅ Envio e recebimento de mensagens
- ✅ Visualização dual (broadcast + chat)
- ✅ Métricas em tempo real
- ✅ Controle de conexão manual
- ✅ Interface responsiva

**Testes:**
- ✅ 12 testes do ConnectionManager
- ✅ 8 testes de endpoints WebSocket
- ✅ 11 testes de modelos Pydantic
- ✅ 5 testes de integração end-to-end

## 🎯 Decisões Técnicas

### Armazenamento em Memória
Pool de conexões mantido em `Set` Python para operações O(1) de adição/remoção. Dados são perdidos ao reiniciar o servidor (comportamento esperado para o escopo do projeto).

### Broadcast Assíncrono
Operações assíncronas evitam bloqueio durante envio de mensagens e permitem remoção automática de conexões com falha.

### Exclusão do Remetente
Por design, mensagens não são enviadas de volta ao cliente que as originou, apenas para os outros conectados.

### Reconexão Automática
Frontend tenta reconectar automaticamente a cada 3 segundos em caso de perda de conexão.

## 📝 Notas

- **Produção:** Para ambientes de produção, considere usar Gunicorn com workers Uvicorn
- **CORS:** Configurado para aceitar qualquer origem (restringir em produção)
- **Persistência:** Não há persistência de dados (por escolha de escopo)
- **Autenticação:** Não implementada (fora do escopo)

## 📚 Documentação Adicional

- [Documentação de Testes](docs/TESTING.md)
- [Especificação do Desafio](docs/desafio.md)
- [Estrutura do Projeto](docs/STRUCTURE.md)

---

**Desenvolvido como solução para desafio técnico com foco em código limpo, arquitetura clara e funcionalidade robusta.**