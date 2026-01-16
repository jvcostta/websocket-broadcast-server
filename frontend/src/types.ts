/**
 * Tipos e interfaces do sistema de eventos
 */

export interface WebSocketMessage {
  message: string;
  timestamp: string;
}

export interface EventItem extends WebSocketMessage {
  id: number;
  receivedAt: number;
  latency?: number;
}

export interface Metrics {
  totalEvents: number;
  eventsPerMinute: number;
  averageLatency: number;
  minLatency: number;
  maxLatency: number;
  connectionUptime: number;
  lastEventTime: number | null;
}

export interface LatencyDataPoint {
  timestamp: number;
  latency: number;
}

export type ConnectionStatus = 'connected' | 'disconnected' | 'connecting';
