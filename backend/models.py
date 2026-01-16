"""
Models - Estruturas de dados para mensagens WebSocket

Define os modelos de dados utilizados na comunicação WebSocket.
Utilizamos Pydantic para validação e serialização de dados.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class WebSocketMessage(BaseModel):
    """
    Modelo para mensagens trafegadas via WebSocket.
    
    Attributes:
        message: Conteúdo da mensagem enviada pelo cliente
        timestamp: Data/hora de processamento no servidor (gerado automaticamente)
    """
    message: str = Field(..., description="Conteúdo da mensagem")
    timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Timestamp gerado no servidor"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Novo evento recebido",
                "timestamp": "2026-01-15T14:45:00"
            }
        }


class IncomingMessage(BaseModel):
    """
    Modelo para mensagens recebidas dos clientes.
    
    Attributes:
        message: Conteúdo da mensagem enviada pelo cliente
    """
    message: str = Field(..., min_length=1, description="Conteúdo da mensagem")
