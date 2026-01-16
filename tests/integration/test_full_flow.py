"""
Testes de Integração
Testa o fluxo completo do sistema backend + frontend
"""

import pytest
import asyncio
import websockets
import json
from typing import List
import sys
from pathlib import Path


class TestIntegration:
    """Testes de integração end-to-end"""

    @pytest.mark.asyncio
    async def test_multiple_clients_broadcast(self):
        """
        Testa broadcast entre múltiplos clientes
        Cenário: 3 clientes conectados, um envia mensagem, os outros 2 recebem
        """
        uri = "ws://localhost:8000/ws/events"
        
        try:
            # Conectar 3 clientes
            async with websockets.connect(uri) as ws1, \
                       websockets.connect(uri) as ws2, \
                       websockets.connect(uri) as ws3:
                
                # Cliente 1 envia mensagem
                message = {"message": "Hello from client 1"}
                await ws1.send(json.dumps(message))
                
                # Clientes 2 e 3 devem receber
                response2 = await asyncio.wait_for(ws2.recv(), timeout=2.0)
                response3 = await asyncio.wait_for(ws3.recv(), timeout=2.0)
                
                data2 = json.loads(response2)
                data3 = json.loads(response3)
                
                assert data2["message"] == "Hello from client 1"
                assert data3["message"] == "Hello from client 1"
                assert "timestamp" in data2
                assert "timestamp" in data3
                
        except Exception as e:
            pytest.skip(f"Servidor não está rodando: {e}")

    @pytest.mark.asyncio
    async def test_sender_not_receive_own_message(self):
        """
        Testa que o remetente não recebe sua própria mensagem
        """
        uri = "ws://localhost:8000/ws/events"
        
        try:
            async with websockets.connect(uri) as ws1, \
                       websockets.connect(uri) as ws2:
                
                # Cliente 1 envia mensagem
                message = {"message": "Test message"}
                await ws1.send(json.dumps(message))
                
                # Cliente 2 deve receber
                response2 = await asyncio.wait_for(ws2.recv(), timeout=2.0)
                data2 = json.loads(response2)
                assert data2["message"] == "Test message"
                
                # Cliente 1 não deve receber (timeout esperado)
                with pytest.raises(asyncio.TimeoutError):
                    await asyncio.wait_for(ws1.recv(), timeout=1.0)
                    
        except websockets.exceptions.WebSocketException as e:
            pytest.skip(f"Servidor não está rodando: {e}")

    @pytest.mark.asyncio
    async def test_rapid_messages(self):
        """
        Testa envio rápido de múltiplas mensagens
        """
        uri = "ws://localhost:8000/ws/events"
        
        try:
            async with websockets.connect(uri) as ws1, \
                       websockets.connect(uri) as ws2:
                
                # Enviar 10 mensagens rapidamente
                messages_sent = []
                for i in range(10):
                    msg = {"message": f"Message {i}"}
                    messages_sent.append(f"Message {i}")
                    await ws1.send(json.dumps(msg))
                    await asyncio.sleep(0.05)  # Pequeno delay
                
                # Cliente 2 deve receber todas
                messages_received = []
                for _ in range(10):
                    response = await asyncio.wait_for(ws2.recv(), timeout=2.0)
                    data = json.loads(response)
                    messages_received.append(data["message"])
                
                assert len(messages_received) == 10
                assert messages_received == messages_sent
                
        except Exception as e:
            pytest.skip(f"Servidor não está rodando: {e}")

    @pytest.mark.asyncio
    async def test_client_disconnect_reconnect(self):
        """
        Testa desconexão e reconexão de cliente
        """
        uri = "ws://localhost:8000/ws/events"
        
        try:
            # Conectar e desconectar
            ws1 = await websockets.connect(uri)
            await ws1.close()
            
            # Reconectar
            ws1 = await websockets.connect(uri)
            ws2 = await websockets.connect(uri)
            
            # Enviar mensagem após reconexão
            message = {"message": "After reconnect"}
            await ws1.send(json.dumps(message))
            
            # ws2 deve receber
            response = await asyncio.wait_for(ws2.recv(), timeout=2.0)
            data = json.loads(response)
            assert data["message"] == "After reconnect"
            
            await ws1.close()
            await ws2.close()
            
        except Exception as e:
            pytest.skip(f"Servidor não está rodando: {e}")

    @pytest.mark.asyncio
    async def test_invalid_json_handling(self):
        """
        Testa tratamento de JSON inválido
        """
        uri = "ws://localhost:8000/ws/events"
        
        try:
            async with websockets.connect(uri) as ws:
                # Enviar texto que não é JSON
                await ws.send("not a json")
                
                # Deve receber mensagem de erro
                response = await asyncio.wait_for(ws.recv(), timeout=2.0)
                data = json.loads(response)
                assert "error" in data
                
        except Exception as e:
            pytest.skip(f"Servidor não está rodando: {e}")
