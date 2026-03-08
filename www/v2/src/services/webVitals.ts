/**
 * Web Vitals Monitoring Service
 * 
 * Отслеживает ключевые метрики производительности:
 * - LCP (Largest Contentful Paint) - время рендера крупнейшего контента
 * - INP (Interaction to Next Paint) - задержка взаимодействия (замена FID)
 * - CLS (Cumulative Layout Shift) - кумулятивное смещение макета
 * - FCP (First Contentful Paint) - время первого рендера
 * - TTFB (Time To First Byte) - время до первого байта
 * 
 * @see https://web.dev/vitals/
 */

import { onLCP, onINP, onCLS, onFCP, onTTFB, type Metric } from 'web-vitals';
import { logger } from '../utils/logger';

export interface WebVitalsConfig {
  /** Отправлять метрики на сервер */
  sendToServer?: boolean;
  /** URL для отправки метрик */
  analyticsUrl?: string;
  /** Логировать в консоль */
  logToConsole?: boolean;
  /** Sample rate (0-1) для отправки на сервер */
  sampleRate?: number;
}

class WebVitalsService {
  private config: Required<WebVitalsConfig>;
  private metrics: Map<string, Metric[]> = new Map();

  constructor(config: WebVitalsConfig = {}) {
    this.config = {
      sendToServer: false,
      analyticsUrl: '/api/analytics/vitals',
      logToConsole: true,
      sampleRate: 1,
      ...config
    };
  }

  /**
   * Инициализация мониторинга Web Vitals
   */
  init(): void {
    if (typeof window === 'undefined') return;

    // Запускаем мониторинг всех метрик
    onLCP(this.handleMetric.bind(this));
    onINP(this.handleMetric.bind(this));  // INP заменил FID в web-vitals v5
    onCLS(this.handleMetric.bind(this));
    onFCP(this.handleMetric.bind(this));
    onTTFB(this.handleMetric.bind(this));

    logger.info('[WebVitals] Monitoring initialized');
  }

  /**
   * Обработчик новой метрики
   */
  private handleMetric(metric: Metric): void {
    // Сохраняем метрику в локальное хранилище
    const existing = this.metrics.get(metric.name) || [];
    existing.push(metric);
    this.metrics.set(metric.name, existing);

    // Логирование в консоль
    if (this.config.logToConsole) {
      this.logMetric(metric);
    }

    // Отправка на сервер
    if (this.config.sendToServer && Math.random() < this.config.sampleRate) {
      this.sendToServer(metric).catch(err => {
        logger.warn('[WebVitals] Failed to send metric', err);
      });
    }

    // Сохранение в localStorage для истории
    this.saveToLocalStorage(metric);
  }

  /**
   * Логирование метрики в консоль
   */
  private logMetric(metric: Metric): void {
    const color = this.getMetricColor(metric.name, metric.value);
    const formattedValue = this.formatValue(metric.name, metric.value);
    
    logger.info(
      `%c${metric.name}: ${formattedValue} (${metric.rating})`,
      `color: ${color}; font-weight: bold;`
    );
  }

  /**
   * Получение цвета для метрики на основе её значения
   */
  private getMetricColor(name: string, value: number): string {
    const thresholds = this.getThresholds(name);
    
    if (value <= thresholds.good) return '#00C853'; // green
    if (value <= thresholds.poor) return '#FFC107'; // yellow
    return '#FF5252'; // red
  }

  /**
   * Пороговые значения для метрик
   */
  private getThresholds(name: string): { good: number; poor: number } {
    switch (name) {
      case 'LCP':
        return { good: 2500, poor: 4000 };
      case 'INP':  // INP заменил FID в web-vitals v5
        return { good: 200, poor: 500 };
      case 'CLS':
        return { good: 0.1, poor: 0.25 };
      case 'FCP':
        return { good: 1800, poor: 3000 };
      case 'TTFB':
        return { good: 800, poor: 1800 };
      default:
        return { good: 0, poor: 0 };
    }
  }

  /**
   * Форматирование значения метрики
   */
  private formatValue(name: string, value: number): string {
    switch (name) {
      case 'CLS':
        return value.toFixed(3);
      case 'INP':  // INP в миллисекундах как FID
      case 'FID':
      case 'TTFB':
        return `${Math.round(value)}ms`;
      case 'LCP':
      case 'FCP':
        return `${(value / 1000).toFixed(2)}s`;
      default:
        return `${Math.round(value)}`;
    }
  }

  /**
   * Отправка метрики на сервер
   */
  private async sendToServer(metric: Metric): Promise<void> {
    try {
      const body = {
        ...metric,
        timestamp: Date.now(),
        url: window.location.href,
        userAgent: navigator.userAgent,
        connection: (navigator as any).connection ? {
          effectiveType: (navigator as any).connection.effectiveType,
          rtt: (navigator as any).connection.rtt,
          downlink: (navigator as any).connection.downlink,
        } : undefined,
      };

      await fetch(this.config.analyticsUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
        keepalive: true,
      });
    } catch (error) {
      logger.warn('[WebVitals] Send failed', error);
    }
  }

  /**
   * Сохранение метрики в localStorage
   */
  private saveToLocalStorage(metric: Metric): void {
    try {
      const key = 'web-vitals-metrics';
      const existing = JSON.parse(localStorage.getItem(key) || '[]');
      
      existing.push({
        ...metric,
        timestamp: Date.now(),
      });

      // Храним только последние 100 метрик
      const trimmed = existing.slice(-100);
      localStorage.setItem(key, JSON.stringify(trimmed));
    } catch (error) {
      logger.warn('[WebVitals] localStorage save failed', error);
    }
  }

  /**
   * Получить все сохранённые метрики
   */
  getMetrics(): Map<string, Metric[]> {
    return new Map(this.metrics);
  }

  /**
   * Получить среднее значение метрики
   */
  getAverage(name: string): number | null {
    const metrics = this.metrics.get(name);
    if (!metrics || metrics.length === 0) return null;
    
    const sum = metrics.reduce((acc, m) => acc + m.value, 0);
    return sum / metrics.length;
  }

  /**
   * Получить процент хороших метрик
   */
  getGoodPercentage(name: string): number | null {
    const metrics = this.metrics.get(name);
    if (!metrics || metrics.length === 0) return null;

    const thresholds = this.getThresholds(name);
    const good = metrics.filter(m => m.value <= thresholds.good).length;
    
    return (good / metrics.length) * 100;
  }

  /**
   * Очистить сохранённые метрики
   */
  clear(): void {
    this.metrics.clear();
    localStorage.removeItem('web-vitals-metrics');
  }
}

// Singleton instance
export const webVitals = new WebVitalsService({
  logToConsole: true,
  sendToServer: false, // Включить при наличии сервера
  sampleRate: 0.1, // 10% запросов
});

/**
 * Хук для использования Web Vitals в React компонентах
 */
export function useWebVitals() {
  return {
    metrics: webVitals.getMetrics(),
    getAverage: webVitals.getAverage.bind(webVitals),
    getGoodPercentage: webVitals.getGoodPercentage.bind(webVitals),
    clear: webVitals.clear.bind(webVitals),
  };
}
