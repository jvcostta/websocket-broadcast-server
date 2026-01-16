"""
ConnectionManager - Gerenciador de conexões WebSocket ativas

Este módulo implementa o gerenciamento centralizado de conexões WebSocket em memória.
A escolha de manter as conexões em memória foi feita deliberadamente para atender
ao escopo do desafio, que não requer persistência de dados.

Decisão arquitetural:
- Pool de conexões mantido em memória (Set) para performance O(1) em adição/remoção
- Não há persistência em banco por ser um requisito explícito do projeto
- A estrutura é perdida ao reiniciar o servidor, comportamento esperado
"""

from fastapi import WebSocket
from typing import Set
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Gerencia o ciclo de vida das conexões WebSocket ativas.
    
    Mantém um pool de conexões em memória e fornece métodos para:
    - Adicionar novas conexões
    - Remover conexões encerradas
    - Broadcast de mensagens para todas as conexões ativas
    """
    
    def __init__(self):
        # Pool de conexões ativas mantido em memória
        # Utilizando Set para garantir unicidade e performance em operações de busca
        self.active_connections: Set[WebSocket] = set()
    
    async def connect(self, websocket: WebSocket):
        """
        Aceita uma nova conexão WebSocket e a adiciona ao pool.
        
        Args:
            websocket: Instância do WebSocket a ser adicionada
        """
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"Nova conexão estabelecida. Total de conexões: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """
        Remove uma conexão do pool de conexões ativas.
        
        Chamado quando o cliente desconecta ou quando ocorre erro na conexão.
        
        Args:
            websocket: Instância do WebSocket a ser removida
        """
        self.active_connections.discard(websocket)
        logger.info(f"Conexão encerrada. Total de conexões: {len(self.active_connections)}")
    
    async def broadcast(self, message: str, sender: WebSocket = None):
        """
        Envia uma mensagem para todas as conexões ativas, exceto o remetente.
        
        Decisão de design:
        - O broadcast não envia a mensagem de volta para o remetente
        - Conexões que falharem ao receber são automaticamente removidas
        - A operação é assíncrona para não bloquear outras conexões
        
        Args:
            message: Mensagem em formato JSON string a ser enviada
            sender: WebSocket do remetente (opcional). Se fornecido, não receberá a mensagem
        """
        disconnected = []
        
        for connection in self.active_connections:
            # Não enviar a mensagem de volta para o remetente
            if connection == sender:
                continue
            
            try:
                await connection.send_text(message)
            except Exception as e:
                # Se houver erro ao enviar, marcar conexão para remoção
                logger.warning(f"Erro ao enviar mensagem para conexão: {e}")
                disconnected.append(connection)
        
        # Remover conexões que falharam
        for connection in disconnected:
            self.disconnect(connection)
    
    def get_connection_count(self) -> int:
        """
        Retorna o número atual de conexões ativas.
        
        Returns:
            int: Quantidade de conexões ativas no pool
        """
        return len(self.active_connections)
