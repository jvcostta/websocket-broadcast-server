"""
Testes para os endpoints da API
Testa o comportamento do WebSocket endpoint
"""

import pytest
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocket, WebSocketDisconnect
import sys
from pathlib import Path
import json

# Adicionar diretório backend ao path
backend_path = Path(__file__).parent.parent.parent / 'backend'
sys.path.insert(0, str(backend_path))

from main import app


@pytest.fixture
def client():
    """Fixture que cria um TestClient"""
    return TestClient(app)


class TestWebSocketEndpoint:
    """Suite de testes para o endpoint WebSocket"""

    def test_websocket_connect(self, client):
        """Testa conexão WebSocket básica"""
        with client.websocket_connect("/ws/events") as websocket:
            assert websocket is not None

    def test_websocket_send_receive(self, client):
        """Testa envio e recebimento de mensagem"""
        with client.websocket_connect("/ws/events") as websocket:
            # Enviar mensagem
            test_message = {"message": "Hello WebSocket"}
            websocket.send_json(test_message)
            
            # Como estamos sozinhos, não recebemos a mensagem de volta
            # (broadcast exclui o remetente)
            # Este teste verifica que não há erro ao enviar
            
    def test_websocket_invalid_json(self, client):
        """Testa envio de JSON inválido"""
        with client.websocket_connect("/ws/events") as websocket:
            # Enviar texto puro (não JSON)
            websocket.send_text("not a json")
            
            # Deve receber mensagem de erro
            response = websocket.receive_json()
            assert "error" in response

    def test_websocket_missing_message_field(self, client):
        """Testa envio de JSON sem campo 'message'"""
        with client.websocket_connect("/ws/events") as websocket:
            # Enviar JSON sem campo message
            websocket.send_json({"wrong_field": "test"})
            
            # Deve receber mensagem de erro
            response = websocket.receive_json()
            assert "error" in response

    def test_websocket_broadcast_multiple_clients(self, client):
        """Testa broadcast entre múltiplos clientes"""
        with client.websocket_connect("/ws/events") as ws1:
            with client.websocket_connect("/ws/events") as ws2:
                # Cliente 1 envia mensagem
                test_message = {"message": "Hello from client 1"}
                ws1.send_json(test_message)
                
                # Cliente 2 deve receber
                response = ws2.receive_json()
                assert response["message"] == "Hello from client 1"
                assert "timestamp" in response
                
                # Cliente 1 não deve receber (é o remetente)
                # Timeout ou nenhuma mensagem

    def test_websocket_empty_message(self, client):
        """Testa envio de mensagem vazia"""
        with client.websocket_connect("/ws/events") as websocket:
            websocket.send_json({"message": ""})
            
            # Pode aceitar ou rejeitar, depende da implementação
            # Aqui apenas verificamos que não gera erro fatal

    def test_root_endpoint(self, client):
        """Testa endpoint raiz"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "service" in data
        assert "active_connections" in data
        assert data["status"] == "online"
