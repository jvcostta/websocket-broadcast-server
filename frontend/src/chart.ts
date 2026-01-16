/**
 * Renderizador de gráfico de latência usando Canvas API
 */

import type { LatencyDataPoint } from './types';

export class LatencyChart {
  private canvas: HTMLCanvasElement;
  private ctx: CanvasRenderingContext2D;
  private data: LatencyDataPoint[] = [];
  private maxDataPoints = 50;
  private animationFrame: number | null = null;

  constructor(canvasId: string) {
    const canvas = document.getElementById(canvasId) as HTMLCanvasElement;
    if (!canvas) {
      throw new Error(`Canvas element ${canvasId} not found`);
    }
    
    this.canvas = canvas;
    const ctx = canvas.getContext('2d');
    if (!ctx) {
      throw new Error('Could not get 2D context');
    }
    
    this.ctx = ctx;
    this.setupCanvas();
    this.render();
  }

  private setupCanvas(): void {
    const container = this.canvas.parentElement;
    if (!container) return;

    const resizeCanvas = () => {
      const rect = container.getBoundingClientRect();
      const dpr = window.devicePixelRatio || 1;
      
      this.canvas.width = rect.width * dpr;
      this.canvas.height = rect.height * dpr;
      this.canvas.style.width = `${rect.width}px`;
      this.canvas.style.height = `${rect.height}px`;
      
      this.ctx.scale(dpr, dpr);
      this.render();
    };

    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
  }

  updateData(dataPoints: LatencyDataPoint[]): void {
    this.data = dataPoints.slice(-this.maxDataPoints);
    this.render();
  }

  private render(): void {
    if (this.animationFrame) {
      cancelAnimationFrame(this.animationFrame);
    }

    this.animationFrame = requestAnimationFrame(() => {
      this.clear();
      if (this.data.length > 0) {
        this.drawGrid();
        this.drawChart();
        this.drawLabels();
      } else {
        this.drawEmptyState();
      }
    });
  }

  private clear(): void {
    const rect = this.canvas.getBoundingClientRect();
    this.ctx.clearRect(0, 0, rect.width, rect.height);
  }

  private drawGrid(): void {
    const rect = this.canvas.getBoundingClientRect();
    const padding = 40;
    const width = rect.width - padding * 2;
    const height = rect.height - padding * 2;

    this.ctx.strokeStyle = '#334155';
    this.ctx.lineWidth = 1;

    // Linhas horizontais
    for (let i = 0; i <= 4; i++) {
      const y = padding + (height / 4) * i;
      this.ctx.beginPath();
      this.ctx.moveTo(padding, y);
      this.ctx.lineTo(padding + width, y);
      this.ctx.stroke();
    }

    // Linhas verticais
    for (let i = 0; i <= 10; i++) {
      const x = padding + (width / 10) * i;
      this.ctx.beginPath();
      this.ctx.moveTo(x, padding);
      this.ctx.lineTo(x, padding + height);
      this.ctx.stroke();
    }
  }

  private drawChart(): void {
    if (this.data.length === 0) return;

    const rect = this.canvas.getBoundingClientRect();
    const padding = 40;
    const width = rect.width - padding * 2;
    const height = rect.height - padding * 2;

    // Calcular escala
    const maxLatency = Math.max(...this.data.map(d => d.latency), 100);
    const minLatency = Math.min(...this.data.map(d => d.latency), 0);
    const latencyRange = maxLatency - minLatency || 1;

    const xStep = width / (this.maxDataPoints - 1);
    const startIndex = Math.max(0, this.data.length - this.maxDataPoints);

    // Desenhar área sob a linha
    this.ctx.beginPath();
    this.ctx.moveTo(padding, padding + height);

    this.data.slice(startIndex).forEach((point, index) => {
      const x = padding + index * xStep;
      const y = padding + height - ((point.latency - minLatency) / latencyRange) * height;
      
      if (index === 0) {
        this.ctx.lineTo(x, y);
      } else {
        this.ctx.lineTo(x, y);
      }
    });

    this.ctx.lineTo(padding + (this.data.length - startIndex - 1) * xStep, padding + height);
    this.ctx.closePath();

    const gradient = this.ctx.createLinearGradient(0, padding, 0, padding + height);
    gradient.addColorStop(0, 'rgba(99, 102, 241, 0.3)');
    gradient.addColorStop(1, 'rgba(99, 102, 241, 0.05)');
    this.ctx.fillStyle = gradient;
    this.ctx.fill();

    // Desenhar linha
    this.ctx.beginPath();
    this.data.slice(startIndex).forEach((point, index) => {
      const x = padding + index * xStep;
      const y = padding + height - ((point.latency - minLatency) / latencyRange) * height;
      
      if (index === 0) {
        this.ctx.moveTo(x, y);
      } else {
        this.ctx.lineTo(x, y);
      }
    });

    this.ctx.strokeStyle = '#6366f1';
    this.ctx.lineWidth = 2;
    this.ctx.stroke();

    // Desenhar pontos
    this.data.slice(startIndex).forEach((point, index) => {
      const x = padding + index * xStep;
      const y = padding + height - ((point.latency - minLatency) / latencyRange) * height;
      
      this.ctx.beginPath();
      this.ctx.arc(x, y, 3, 0, Math.PI * 2);
      this.ctx.fillStyle = '#6366f1';
      this.ctx.fill();
      
      this.ctx.beginPath();
      this.ctx.arc(x, y, 5, 0, Math.PI * 2);
      this.ctx.strokeStyle = '#818cf8';
      this.ctx.lineWidth = 2;
      this.ctx.stroke();
    });
  }

  private drawLabels(): void {
    if (this.data.length === 0) return;

    const rect = this.canvas.getBoundingClientRect();
    const padding = 40;
    const height = rect.height - padding * 2;

    const maxLatency = Math.max(...this.data.map(d => d.latency), 100);
    const minLatency = Math.min(...this.data.map(d => d.latency), 0);

    this.ctx.fillStyle = '#94a3b8';
    this.ctx.font = '11px Inter, sans-serif';
    this.ctx.textAlign = 'right';

    // Labels do eixo Y
    for (let i = 0; i <= 4; i++) {
      const value = maxLatency - (maxLatency - minLatency) * (i / 4);
      const y = padding + (height / 4) * i;
      this.ctx.fillText(`${Math.round(value)}ms`, padding - 10, y + 4);
    }

    // Label do eixo X
    this.ctx.textAlign = 'center';
    this.ctx.fillText('Tempo', rect.width / 2, rect.height - 10);
  }

  private drawEmptyState(): void {
    const rect = this.canvas.getBoundingClientRect();
    
    this.ctx.fillStyle = '#475569';
    this.ctx.font = '14px Inter, sans-serif';
    this.ctx.textAlign = 'center';
    this.ctx.textBaseline = 'middle';
    this.ctx.fillText('Aguardando dados de latência...', rect.width / 2, rect.height / 2);
  }

  destroy(): void {
    if (this.animationFrame) {
      cancelAnimationFrame(this.animationFrame);
    }
  }
}
