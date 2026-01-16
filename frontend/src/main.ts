/**
 * WebSocket Event Panel - Aplicação Principal
 * Dashboard profissional com métricas técnicas em tempo real
 */

import './style.css';
import type { 
  WebSocketMessage, 
  EventItem, 
  ConnectionStatus,
  Metrics 
} from './types';
import { MetricsCollector } from './metrics';

const WS_URL = 'ws://localhost:8000/ws/events';
const RECONNECT_DELAY = 3000;
const METRICS_UPDATE_INTERVAL = 1000;

class EventPanelApp {
  private websocket: WebSocket | null = null;
  private metricsCollector: MetricsCollector;
  private reconnectTimeout: number | null = null;
  private metricsInterval: number | null = null;
  private eventIdCounter = 0;
  private sentTimestamps: Map<string, number> = new Map();
  private sentEventsCount = 0; // Contador de eventos enviados

  // Elementos DOM
  private elements = {
    connectionBadge: document.getElementById('connection-badge')!,
    connectionText: document.getElementById('connection-text')!,
    sidebarStatus: document.getElementById('sidebar-status')!,
    sidebarStatusText: document.getElementById('sidebar-status-text')!,
    eventInput: document.getElementById('event-input') as HTMLInputElement,
    sendButton: document.getElementById('send-button') as HTMLButtonElement,
    disconnectButton: document.getElementById('disconnect-button') as HTMLButtonElement,
    clearButton: document.getElementById('clear-button') as HTMLButtonElement,
    clearChatButton: document.getElementById('clear-chat-button') as HTMLButtonElement,
    eventsContainer: document.getElementById('events-container')!,
    chatContainer: document.getElementById('chat-container')!,
    
    metricReceived: document.getElementById('metric-received')!,
    metricReceivedChange: document.getElementById('metric-received-change')!,
    metricSent: document.getElementById('metric-sent')!,
    metricUptime: document.getElementById('metric-uptime')!,
  };

  constructor() {
    this.metricsCollector = new MetricsCollector();
    this.init();
  }

  private init(): void {
    this.setupEventListeners();
    this.connectWebSocket();
    this.startMetricsUpdate();
  }

  private setupEventListeners(): void {
    this.elements.sendButton.addEventListener('click', () => this.sendEvent());
    
    this.elements.eventInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter' && !this.elements.sendButton.disabled) {
        this.sendEvent();
      }
    });

    this.elements.clearButton.addEventListener('click', () => this.clearEvents());
    this.elements.clearChatButton.addEventListener('click', () => this.clearChat());
    this.elements.disconnectButton.addEventListener('click', () => this.disconnect());

    window.addEventListener('beforeunload', () => {
      this.cleanup();
    });
  }

  private connectWebSocket(): void {
    this.updateConnectionStatus('connecting');

    try {
      this.websocket = new WebSocket(WS_URL);

      this.websocket.onopen = () => this.handleOpen();
      this.websocket.onmessage = (event) => this.handleMessage(event);
      this.websocket.onerror = (error) => this.handleError(error);
      this.websocket.onclose = (event) => this.handleClose(event);

    } catch (error) {
      console.error('Erro ao criar WebSocket:', error);
      this.updateConnectionStatus('disconnected');
      this.scheduleReconnect();
    }
  }

  private handleOpen(): void {
    console.log('✅ WebSocket conectado');
    this.updateConnectionStatus('connected');
    this.elements.sendButton.disabled = false;
    this.elements.disconnectButton.disabled = false;
    this.metricsCollector.startConnection();

    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }
  }

  private handleMessage(event: MessageEvent): void {
    try {
      const data: WebSocketMessage = JSON.parse(event.data);
      
      if ('error' in data) {
        console.error('❌ Erro do servidor:', data.error);
        return;
      }

      const receivedAt = Date.now();
      let latency: number | undefined;

      // Calcular latência apenas para mensagens que enviamos (round-trip time)
      const sentTime = this.sentTimestamps.get(data.message);
      if (sentTime) {
        latency = receivedAt - sentTime;
        this.sentTimestamps.delete(data.message);
      }

      const eventItem: EventItem = {
        ...data,
        id: ++this.eventIdCounter,
        receivedAt,
        latency
      };

      this.metricsCollector.addEvent(eventItem);
      this.addEventToUI(eventItem); // Broadcast: só recebidos
      this.addEventToChatUI(eventItem, 'received'); // Chat: lado esquerdo
      this.updateMetricsUI();

    } catch (error) {
      console.error('❌ Erro ao processar mensagem:', error);
    }
  }

  private handleError(error: Event): void {
    console.error('❌ Erro no WebSocket:', error);
  }

  private handleClose(event: CloseEvent): void {
    console.log('🔌 WebSocket desconectado', event.code, event.reason);
    this.updateConnectionStatus('disconnected');
    this.elements.sendButton.disabled = true;
    this.elements.disconnectButton.disabled = true;
    this.scheduleReconnect();
  }

  private scheduleReconnect(): void {
    if (!this.reconnectTimeout) {
      console.log('🔄 Reconectando em 3 segundos...');
      this.reconnectTimeout = window.setTimeout(() => {
        this.reconnectTimeout = null;
        this.connectWebSocket();
      }, RECONNECT_DELAY);
    }
  }

  private updateConnectionStatus(status: ConnectionStatus): void {
    const statusConfig = {
      connected: { text: 'Conectado', class: 'connected' },
      disconnected: { text: 'Desconectado', class: 'disconnected' },
      connecting: { text: 'Conectando...', class: 'connecting' }
    };

    const config = statusConfig[status];
    
    // Badge principal
    this.elements.connectionBadge.className = `status-badge ${config.class}`;
    this.elements.connectionText.textContent = config.text;
    
    // Sidebar
    this.elements.sidebarStatus.className = `connection-indicator ${config.class}`;
    this.elements.sidebarStatusText.textContent = config.text;
  }

  private sendEvent(): void {
    const message = this.elements.eventInput.value.trim();

    if (!message) {
      this.elements.eventInput.focus();
      return;
    }

    if (!this.websocket || this.websocket.readyState !== WebSocket.OPEN) {
      alert('❌ Não conectado ao servidor. Aguarde a reconexão.');
      return;
    }

    try {
      const sentAt = Date.now();
      this.sentTimestamps.set(message, sentAt);

      const payload = JSON.stringify({ message });
      this.websocket.send(payload);

      console.log('📤 Evento enviado:', message);

      // Adicionar evento enviado localmente apenas no chat (lado direito)
      this.sentEventsCount++;
      this.addEventToChatUI({ message, timestamp: new Date(sentAt).toISOString() } as any, 'sent');
      this.updateMetricsUI();

      // Limpar campo
      this.elements.eventInput.value = '';
      this.elements.eventInput.focus();

      // Limpar timestamps antigos (mais de 10 segundos)
      setTimeout(() => {
        this.sentTimestamps.delete(message);
      }, 10000);

    } catch (error) {
      console.error('❌ Erro ao enviar evento:', error);
      alert('❌ Erro ao enviar evento. Verifique a conexão.');
    }
  }

  private addEventToUI(event: EventItem): void {
    // Remover estado vazio
    const emptyState = this.elements.eventsContainer.querySelector('.empty-state');
    if (emptyState) {
      emptyState.remove();
    }

    const eventElement = document.createElement('div');
    eventElement.className = 'event-item'; // Broadcast: sem distinção de lado

    const timestamp = new Date(event.timestamp).toLocaleString('pt-BR', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });

    eventElement.innerHTML = `
      <div class="event-bubble">
        <div class="event-description">${this.escapeHtml(event.message)}</div>
        <div class="event-time">${timestamp}</div>
      </div>
    `;

    this.elements.eventsContainer.insertBefore(
      eventElement, 
      this.elements.eventsContainer.firstChild
    );
  }

  private addEventToChatUI(event: EventItem | { message: string, timestamp: string }, type: 'sent' | 'received'): void {
    // Remover estado vazio
    const emptyState = this.elements.chatContainer.querySelector('.empty-state');
    if (emptyState) {
      emptyState.remove();
    }

    const eventElement = document.createElement('div');
    eventElement.className = `event-item event-${type}`;

    const timestamp = new Date(event.timestamp).toLocaleString('pt-BR', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });

    eventElement.innerHTML = `
      <div class="event-bubble">
        <div class="event-description">${this.escapeHtml(event.message)}</div>
        <div class="event-time">${timestamp}</div>
      </div>
    `;

    this.elements.chatContainer.insertBefore(
      eventElement, 
      this.elements.chatContainer.firstChild
    );
  }

  private disconnect(): void {
    if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
      console.log('🔌 Desconectando manualmente...');
      
      // Limpar timeout de reconexão para não reconectar automaticamente
      if (this.reconnectTimeout) {
        clearTimeout(this.reconnectTimeout);
        this.reconnectTimeout = null;
      }
      
      this.websocket.close(1000, 'Desconexão manual');
      this.updateConnectionStatus('disconnected');
      this.elements.sendButton.disabled = true;
      this.elements.disconnectButton.disabled = true;
    }
  }

  private clearEvents(): void {
    this.elements.eventsContainer.innerHTML = `
      <div class="empty-state">
        <svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
          <polyline points="14 2 14 8 20 8"></polyline>
          <line x1="16" y1="13" x2="8" y2="13"></line>
          <line x1="16" y1="17" x2="8" y2="17"></line>
          <polyline points="10 9 9 9 8 9"></polyline>
        </svg>
        <h3>Nenhum evento recebido ainda</h3>
        <p>Os eventos aparecerão aqui em tempo real assim que forem disparados</p>
      </div>
    `;

    this.metricsCollector.clearEvents();
    this.eventIdCounter = 0;
    this.sentEventsCount = 0;
    this.updateMetricsUI();
  }

  private clearChat(): void {
    this.elements.chatContainer.innerHTML = `
      <div class="empty-state">
        <svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
        </svg>
        <h3>Nenhuma mensagem ainda</h3>
        <p>Suas mensagens aparecerão à direita, mensagens recebidas à esquerda</p>
      </div>
    `;
  }

  private startMetricsUpdate(): void {
    this.metricsInterval = window.setInterval(() => {
      this.updateMetricsUI();
    }, METRICS_UPDATE_INTERVAL);
  }

  private updateMetricsUI(): void {
    const metrics: Metrics = this.metricsCollector.getMetrics();

    // Eventos recebidos
    this.elements.metricReceived.textContent = metrics.totalEvents.toString();
    this.elements.metricReceivedChange.textContent = `+${metrics.totalEvents}`;

    // Eventos enviados
    this.elements.metricSent.textContent = this.sentEventsCount.toString();

    // Tempo online (uptime)
    this.elements.metricUptime.textContent = this.formatUptime(metrics.connectionUptime);
  }

  private formatUptime(ms: number): string {
    const seconds = Math.floor(ms / 1000);
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;

    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }

  private escapeHtml(text: string): string {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  private cleanup(): void {
    if (this.websocket) {
      this.websocket.close();
    }
    
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
    }
    
    if (this.metricsInterval) {
      clearInterval(this.metricsInterval);
    }
  }
}

// Inicializar aplicação
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => new EventPanelApp());
} else {
  new EventPanelApp();
}
