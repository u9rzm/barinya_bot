/**
 * Logger utility with different log levels.
 * Automatically disables debug logs in production.
 * 
 * @example
 * ```typescript
 * import { logger } from './utils/logger';
 * 
 * logger.debug('Debug message', { data: someData });
 * logger.info('User logged in', { userId: 123 });
 * logger.warn('Low stock warning', { productId: 'abc' });
 * logger.error('Failed to fetch data', error);
 * ```
 */

type LogLevel = 'debug' | 'info' | 'warn' | 'error';

interface LoggerOptions {
  prefix?: string;
  showTimestamp?: boolean;
}

class Logger {
  private isProduction: boolean;
  private minLevel: LogLevel;
  private prefix: string;
  private showTimestamp: boolean;

  private levelPriority: Record<LogLevel, number> = {
    debug: 0,
    info: 1,
    warn: 2,
    error: 3,
  };

  constructor(
    minLevel: LogLevel = 'debug',
    options: LoggerOptions = {}
  ) {
    this.isProduction = typeof import.meta !== 'undefined' && (import.meta as any).env?.PROD;
    this.minLevel = minLevel;
    this.prefix = options.prefix || '[App]';
    this.showTimestamp = options.showTimestamp ?? true;
  }

  private shouldLog(level: LogLevel): boolean {
    // Always log errors in production
    if (this.isProduction && level === 'error') {
      return true;
    }
    
    // In production, only log errors
    if (this.isProduction) {
      return false;
    }
    
    // In development, check level priority
    return this.levelPriority[level] >= this.levelPriority[this.minLevel];
  }

  private getTimestamp(): string {
    return new Date().toISOString();
  }

  private formatMessage(level: LogLevel, message: string, data?: any): any[] {
    const parts: any[] = [];
    
    if (this.showTimestamp) {
      parts.push(`%c${this.getTimestamp()}`, 'color: #888;');
    }
    
    parts.push(`%c${this.prefix}`, 'color: #007bff; font-weight: bold;');
    parts.push(`%c[${level.toUpperCase()}]`, `color: ${this.getLevelColor(level)}; font-weight: bold;`);
    parts.push(message);
    
    if (data !== undefined) {
      parts.push(data);
    }
    
    return parts;
  }

  private getLevelColor(level: LogLevel): string {
    switch (level) {
      case 'debug': return '#6c757d';
      case 'info': return '#007bff';
      case 'warn': return '#ffc107';
      case 'error': return '#dc3545';
      default: return '#000';
    }
  }

  debug(message: string, data?: any): void {
    if (this.shouldLog('debug')) {
      console.debug(...this.formatMessage('debug', message, data));
    }
  }

  info(message: string, data?: any): void {
    if (this.shouldLog('info')) {
      console.info(...this.formatMessage('info', message, data));
    }
  }

  warn(message: string, data?: any): void {
    if (this.shouldLog('warn')) {
      console.warn(...this.formatMessage('warn', message, data));
    }
  }

  error(message: string, error?: any): void {
    // Always log errors
    console.error(...this.formatMessage('error', message, error));
  }

  /**
   * Create a child logger with a different prefix
   */
  createChild(prefix: string): Logger {
    return new Logger(this.minLevel, {
      ...{ prefix: `${this.prefix}${prefix}`, showTimestamp: this.showTimestamp }
    });
  }

  /**
   * Set minimum log level
   */
  setLevel(level: LogLevel): void {
    this.minLevel = level;
  }
}

// Export a default logger instance
export const logger = new Logger('debug', { prefix: '[Gourmet]', showTimestamp: true });

// Export Logger class for custom instances
export { Logger };
export type { LogLevel, LoggerOptions };
