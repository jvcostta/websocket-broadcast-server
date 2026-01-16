/**
 * Sistema de métricas e estatísticas
 */

import type { Metrics, LatencyDataPoint, EventItem } from './types';

export class MetricsCollector {
  private events: EventItem[] = [];
  private latencyHistory: LatencyDataPoint[] = [];
  private connectionStartTime: number = 0;
  private maxHistorySize = 100;
  private maxLatencyPoints = 50;

  constructor() {
    this.reset();
  }

  reset(): void {
    this.events = [];
    this.latencyHistory = [];
    this.connectionStartTime = Date.now();
  }

  addEvent(event: EventItem): void {
    this.events.push(event);
    
    // Manter apenas os últimos N eventos
    if (this.events.length > this.maxHistorySize) {
      this.events.shift();
    }

    // Adicionar latência ao histórico se disponível
    if (event.latency !== undefined) {
      this.latencyHistory.push({
        timestamp: event.receivedAt,
        latency: event.latency
      });

      // Manter apenas os últimos N pontos
      if (this.latencyHistory.length > this.maxLatencyPoints) {
        this.latencyHistory.shift();
      }
    }
  }

  getMetrics(): Metrics {
    const now = Date.now();
    const oneMinuteAgo = now - 60000;
    
    // Eventos do último minuto
    const recentEvents = this.events.filter(e => e.receivedAt > oneMinuteAgo);
    
    // Calcular estatísticas de latência
    const latencies = this.events
      .map(e => e.latency)
      .filter((l): l is number => l !== undefined);
    
    const avgLatency = latencies.length > 0
      ? latencies.reduce((sum, l) => sum + l, 0) / latencies.length
      : 0;
    
    const minLatency = latencies.length > 0 ? Math.min(...latencies) : 0;
    const maxLatency = latencies.length > 0 ? Math.max(...latencies) : 0;
    
    // Último evento
    const lastEvent = this.events.length > 0 
      ? this.events[this.events.length - 1]
      : null;

    return {
      totalEvents: this.events.length,
      eventsPerMinute: recentEvents.length,
      averageLatency: Math.round(avgLatency),
      minLatency: Math.round(minLatency),
      maxLatency: Math.round(maxLatency),
      connectionUptime: now - this.connectionStartTime,
      lastEventTime: lastEvent ? lastEvent.receivedAt : null
    };
  }

  getLatencyHistory(): LatencyDataPoint[] {
    return [...this.latencyHistory];
  }

  clearEvents(): void {
    this.events = [];
  }

  startConnection(): void {
    this.connectionStartTime = Date.now();
  }
}
