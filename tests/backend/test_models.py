"""
Testes para os modelos Pydantic
Testa validação de dados
"""

import pytest
from pydantic import ValidationError
from datetime import datetime
import sys
from pathlib import Path

# Adicionar diretório backend ao path
backend_path = Path(__file__).parent.parent.parent / 'backend'
sys.path.insert(0, str(backend_path))

from models import IncomingMessage, WebSocketMessage


class TestIncomingMessage:
    """Testes para o modelo IncomingMessage"""

    def test_valid_message(self):
        """Testa criação de mensagem válida"""
        data = {"message": "Test message"}
        msg = IncomingMessage(**data)
        
        assert msg.message == "Test message"

    def test_empty_message(self):
        """Testa mensagem vazia (deve falhar validação)"""
        data = {"message": ""}
        
        with pytest.raises(ValidationError):
            IncomingMessage(**data)

    def test_missing_message_field(self):
        """Testa ausência do campo message (deve falhar)"""
        data = {}
        
        with pytest.raises(ValidationError):
            IncomingMessage(**data)

    def test_wrong_type(self):
        """Testa tipo incorreto para message (deve falhar validação)"""
        data = {"message": 123}  # Número em vez de string
        
        with pytest.raises(ValidationError):
            IncomingMessage(**data)

    def test_extra_fields_ignored(self):
        """Testa que campos extras são ignorados"""
        data = {"message": "test", "extra_field": "should be ignored"}
        msg = IncomingMessage(**data)
        
        assert msg.message == "test"
        assert not hasattr(msg, 'extra_field')


class TestWebSocketMessage:
    """Testes para o modelo WebSocketMessage"""

    def test_valid_websocket_message(self):
        """Testa criação de mensagem WebSocket válida"""
        data = {
            "message": "Test message",
            "timestamp": datetime.now().isoformat()
        }
        msg = WebSocketMessage(**data)
        
        assert msg.message == "Test message"
        assert isinstance(msg.timestamp, (str, datetime))

    def test_auto_timestamp(self):
        """Testa geração automática de timestamp"""
        data = {"message": "Test message"}
        msg = WebSocketMessage(**data)
        
        assert msg.message == "Test message"
        # Timestamp deve ser gerado automaticamente se não fornecido

    def test_missing_message(self):
        """Testa ausência do campo message"""
        data = {"timestamp": datetime.now().isoformat()}
        
        with pytest.raises(ValidationError):
            WebSocketMessage(**data)

    def test_timestamp_formats(self):
        """Testa diferentes formatos de timestamp"""
        # ISO format string
        data = {
            "message": "Test",
            "timestamp": "2024-01-01T12:00:00"
        }
        msg = WebSocketMessage(**data)
        assert msg.message == "Test"

    def test_long_message(self):
        """Testa mensagem muito longa"""
        long_msg = "a" * 10000
        data = {"message": long_msg}
        msg = WebSocketMessage(**data)
        
        assert msg.message == long_msg
        assert len(msg.message) == 10000
