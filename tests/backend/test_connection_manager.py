"""
Testes para o ConnectionManager
Testa o gerenciamento do pool de conexões WebSocket
"""

import pytest
from fastapi import WebSocket
from unittest.mock import AsyncMock, MagicMock
import sys
from pathlib import Path

# Adicionar diretório backend ao path
backend_path = Path(__file__).parent.parent.parent / 'backend'
sys.path.insert(0, str(backend_path))

from connection_manager import ConnectionManager


@pytest.fixture
def manager():
    """Fixture que cria uma nova instância do ConnectionManager"""
    return ConnectionManager()


@pytest.fixture
def mock_websocket():
    """Fixture que cria um mock de WebSocket"""
    ws = MagicMock(spec=WebSocket)
    ws.send_text = AsyncMock()
    ws.accept = AsyncMock()
    return ws


class TestConnectionManager:
    """Suite de testes para ConnectionManager"""

    def test_init(self, manager):
        """Testa inicialização do manager"""
        assert len(manager.active_connections) == 0
        assert isinstance(manager.active_connections, set)

    @pytest.mark.asyncio
    async def test_connect(self, manager, mock_websocket):
        """Testa conexão de um cliente"""
        await manager.connect(mock_websocket)
        
        assert mock_websocket in manager.active_connections
        assert len(manager.active_connections) == 1
        mock_websocket.accept.assert_called_once()

    @pytest.mark.asyncio
    async def test_connect_multiple(self, manager):
        """Testa conexão de múltiplos clientes"""
        ws1 = MagicMock(spec=WebSocket)
        ws1.accept = AsyncMock()
        ws2 = MagicMock(spec=WebSocket)
        ws2.accept = AsyncMock()
        ws3 = MagicMock(spec=WebSocket)
        ws3.accept = AsyncMock()

        await manager.connect(ws1)
        await manager.connect(ws2)
        await manager.connect(ws3)

        assert len(manager.active_connections) == 3
        assert ws1 in manager.active_connections
        assert ws2 in manager.active_connections
        assert ws3 in manager.active_connections

    def test_disconnect(self, manager, mock_websocket):
        """Testa desconexão de um cliente"""
        manager.active_connections.add(mock_websocket)
        
        manager.disconnect(mock_websocket)
        
        assert mock_websocket not in manager.active_connections
        assert len(manager.active_connections) == 0

    def test_disconnect_nonexistent(self, manager, mock_websocket):
        """Testa desconexão de cliente não existente (não deve gerar erro)"""
        manager.disconnect(mock_websocket)
        assert len(manager.active_connections) == 0

    @pytest.mark.asyncio
    async def test_broadcast_to_all(self, manager):
        """Testa broadcast para todos os clientes"""
        ws1 = MagicMock(spec=WebSocket)
        ws1.send_text = AsyncMock()
        ws2 = MagicMock(spec=WebSocket)
        ws2.send_text = AsyncMock()
        ws3 = MagicMock(spec=WebSocket)
        ws3.send_text = AsyncMock()

        manager.active_connections = {ws1, ws2, ws3}
        message = "test message"

        await manager.broadcast(message)

        ws1.send_text.assert_called_once_with(message)
        ws2.send_text.assert_called_once_with(message)
        ws3.send_text.assert_called_once_with(message)

    @pytest.mark.asyncio
    async def test_broadcast_excludes_sender(self, manager):
        """Testa que broadcast exclui o remetente"""
        sender = MagicMock(spec=WebSocket)
        sender.send_text = AsyncMock()
        
        ws1 = MagicMock(spec=WebSocket)
        ws1.send_text = AsyncMock()
        ws2 = MagicMock(spec=WebSocket)
        ws2.send_text = AsyncMock()

        manager.active_connections = {sender, ws1, ws2}
        message = "test message"

        await manager.broadcast(message, sender=sender)

        sender.send_text.assert_not_called()
        ws1.send_text.assert_called_once_with(message)
        ws2.send_text.assert_called_once_with(message)

    @pytest.mark.asyncio
    async def test_broadcast_handles_errors(self, manager):
        """Testa que broadcast remove conexões com erro"""
        ws_error = MagicMock(spec=WebSocket)
        ws_error.send_text = AsyncMock(side_effect=Exception("Connection error"))
        
        ws_ok = MagicMock(spec=WebSocket)
        ws_ok.send_text = AsyncMock()

        manager.active_connections = {ws_error, ws_ok}
        message = "test message"

        await manager.broadcast(message)

        # Conexão com erro deve ser removida
        assert ws_error not in manager.active_connections
        assert ws_ok in manager.active_connections
        assert len(manager.active_connections) == 1
        
        # Mensagem deve ter sido enviada para a conexão válida
        ws_ok.send_text.assert_called_once_with(message)

    @pytest.mark.asyncio
    async def test_broadcast_empty_connections(self, manager):
        """Testa broadcast sem conexões ativas"""
        message = "test message"
        # Não deve gerar erro
        await manager.broadcast(message)
        assert len(manager.active_connections) == 0
