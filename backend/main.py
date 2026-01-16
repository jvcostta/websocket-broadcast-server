"""
WebSocket Broadcast Server

Servidor WebSocket simples e eficiente que implementa broadcast de mensagens
entre múltiplos clientes conectados.

Decisões arquiteturais principais:
1. Uso de FastAPI/Starlette para lidar com WebSockets de forma nativa
2. Pool de conexões mantido em memória (sem persistência por design)
3. Broadcast assíncrono para não bloquear outras conexões
4. Tratamento robusto de desconexões e erros

Escopo deliberadamente mantido simples, alinhado aos requisitos do desafio técnico.
Não implementamos autenticação, banco de dados ou cache por escolha de escopo.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import logging
import json
from connection_manager import ConnectionManager
from models import IncomingMessage, WebSocketMessage

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inicialização da aplicação
app = FastAPI(
    title="WebSocket Broadcast Server",
    description="Servidor WebSocket que implementa broadcast de mensagens entre clientes conectados",
    version="1.0.0"
)

# Configuração de CORS para permitir conexões de qualquer origem
# Em produção, seria recomendável restringir as origens permitidas
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instância única do gerenciador de conexões
# Mantida em memória durante o ciclo de vida da aplicação
manager = ConnectionManager()


@app.get("/")
async def root():
    """
    Endpoint raiz para verificação de status do servidor.
    """
    return {
        "status": "online",
        "service": "WebSocket Broadcast Server",
        "active_connections": manager.get_connection_count()
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint para monitoramento.
    """
    return {
        "status": "healthy",
        "connections": manager.get_connection_count()
    }


@app.websocket("/ws/events")
async def websocket_endpoint(websocket: WebSocket):
    """
    Endpoint WebSocket principal.
    
    Fluxo de operação:
    1. Aceita a conexão (handshake HTTP 101 Switching Protocols)
    2. Adiciona a conexão ao pool de conexões ativas
    3. Entra em loop de escuta contínua de mensagens
    4. Para cada mensagem recebida:
       - Valida o formato
       - Adiciona timestamp do servidor
       - Faz broadcast para todos os outros clientes
    5. Ao desconectar, remove a conexão do pool
    
    Args:
        websocket: Instância do WebSocket fornecida pelo FastAPI
    """
    # Aceitar conexão e adicionar ao pool
    await manager.connect(websocket)
    
    try:
        # Loop infinito de escuta de mensagens
        while True:
            # Aguardar próxima mensagem do cliente
            data = await websocket.receive_text()
            
            try:
                # Parsear e validar mensagem recebida
                incoming = json.loads(data)
                validated_message = IncomingMessage(**incoming)
                
                # Criar mensagem de broadcast com timestamp do servidor
                broadcast_message = WebSocketMessage(
                    message=validated_message.message
                )
                
                logger.info(f"Mensagem recebida e processada: {validated_message.message[:50]}...")
                
                # Fazer broadcast para todos os outros clientes
                await manager.broadcast(
                    message=broadcast_message.model_dump_json(),
                    sender=websocket
                )
                
            except json.JSONDecodeError:
                logger.warning("Mensagem recebida não é um JSON válido")
                await websocket.send_text(
                    json.dumps({"error": "Formato de mensagem inválido. Use JSON."})
                )
            except Exception as e:
                logger.error(f"Erro ao processar mensagem: {e}")
                await websocket.send_text(
                    json.dumps({"error": "Erro ao processar mensagem"})
                )
    
    except WebSocketDisconnect:
        # Desconexão normal do cliente
        logger.info("Cliente desconectado normalmente")
        manager.disconnect(websocket)
    
    except Exception as e:
        # Erro inesperado na conexão
        logger.error(f"Erro inesperado na conexão WebSocket: {e}")
        manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn
    
    # Configuração para execução direta do script
    # Em produção, recomenda-se usar gunicorn com workers uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
