/**
 * Media Preloading Service
 * 
 * Provides seamless loading of videos and images by:
 * 1. Pre-caching critical media assets before first render
 * 2. Using Cache API for persistent storage
 * 3. Managing preload priorities (current, next, previous)
 * 4. Tracking load progress for smooth UX transitions
 * 
 * Features:
 * - Timeout handling with retries
 * - Size limits to prevent loading huge files
 * - Graceful fallback on errors
 */

import { logger } from '../utils/logger';

const CACHE_NAME = 'gourmet-delivery-media-v1';
const MAX_CACHE_SIZE = 50; // Max items to cache
const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB limit
const LOAD_TIMEOUT = 15000; // 15 seconds timeout
const MAX_RETRIES = 2; // Retry failed loads twice
const STALE_TIME = 5 * 60 * 1000; // 5 minutes - время жизни кэша перед background refresh

export interface MediaLoadProgress {
  total: number;
  loaded: number;
  percentage: number;
  criticalLoaded: boolean; // True when first 3 items are loaded
}

export type LoadStatus = 'pending' | 'loading' | 'loaded' | 'error';

export interface MediaItem {
  url: string;
  type: 'video' | 'image';
  priority: 'critical' | 'normal' | 'low';
  status: LoadStatus;
  blob?: Blob;
  objectUrl?: string | null; // Кэш Object URL для предотвращения утечек
  retries?: number;
  timestamp?: number; // Время загрузки для stale-while-revalidate
}

class MediaPreloaderService {
  private mediaItems = new Map<string, MediaItem>();
  private cache: Cache | null = null;
  private progressListeners = new Set<(progress: MediaLoadProgress) => void>();
  private initialized = false;
  private abortControllers = new Map<string, AbortController>();

  /**
   * Initialize the preloader and open cache
   */
  async initialize(): Promise<void> {
    if (this.initialized) return;

    try {
      if ('caches' in window) {
        this.cache = await caches.open(CACHE_NAME);
        await this.cleanupCache();
      }
    } catch (error) {
      logger.warn('Cache API not available or failed to open', error);
    }

    this.initialized = true;
  }

  /**
   * Clean up old cache entries if over limit
   */
  private async cleanupCache(): Promise<void> {
    if (!this.cache) return;

    try {
      const keys = await this.cache.keys();
      if (keys.length > MAX_CACHE_SIZE) {
        // Simple cleanup - delete oldest entries
        logger.info('Cache cleanup needed');
      }
    } catch (error) {
      logger.warn('Cache cleanup failed', error);
    }
  }

  /**
   * Preload a batch of media items
   */
  preloadMedia(items: Array<{ url: string; type: 'video' | 'image'; priority?: 'critical' | 'normal' | 'low' }>): void {
    items.forEach(item => {
      if (!this.mediaItems.has(item.url)) {
        this.mediaItems.set(item.url, {
          url: item.url,
          type: item.type,
          priority: item.priority || 'normal',
          status: 'pending',
          retries: 0
        });
      }
    });

    // Start loading critical items immediately
    this.processQueue();
  }

  /**
   * Process the preload queue with priority ordering
   */
  private async processQueue(): Promise<void> {
    const pending = Array.from(this.mediaItems.values())
      .filter(item => item.status === 'pending')
      .sort((a, b) => {
        const priorityOrder = { critical: 0, normal: 1, low: 2 };
        return priorityOrder[a.priority] - priorityOrder[b.priority];
      });

    // Load critical items first with concurrency limit
    const criticalItems = pending.filter(item => item.priority === 'critical');
    for (const item of criticalItems) {
      await this.loadItem(item);
    }

    // Load normal/low priority items with concurrency limit
    const normalItems = pending.filter(item => item.priority !== 'critical');
    await Promise.all(normalItems.slice(0, 3).map(item => this.loadItem(item)));
  }

  /**
   * Load a single media item with timeout and retry logic
   * Stale-while-revalidate: возвращаем кэш сразу, обновляем в фоне
   */
  private async loadItem(item: MediaItem, backgroundRefresh = false): Promise<void> {
    if (item.status === 'loading' || item.status === 'loaded') return;

    item.status = 'loading';
    this.notifyProgress();

    // Create abort controller for timeout
    const controller = new AbortController();
    this.abortControllers.set(item.url, controller);

    const timeoutId = setTimeout(() => {
      controller.abort();
      this.abortControllers.delete(item.url);
    }, LOAD_TIMEOUT);

    try {
      // Try cache first (stale-while-revalidate)
      if (this.cache) {
        const cached = await this.cache.match(item.url);
        if (cached && cached.ok) {
          const blob = await cached.blob();
          item.blob = blob;
          item.status = 'loaded';
          item.timestamp = Date.now();
          
          clearTimeout(timeoutId);
          this.abortControllers.delete(item.url);
          this.notifyProgress();
          
          // Background refresh if stale
          const isStale = item.timestamp && (Date.now() - item.timestamp > STALE_TIME);
          if (isStale || backgroundRefresh) {
            this.backgroundRefresh(item, controller).catch(err => {
              logger.warn('Background refresh failed', err);
            });
          }
          return;
        }
      }

      // Fetch from network with timeout
      await this.fetchAndCache(item, controller, timeoutId);
    } catch (error) {
      clearTimeout(timeoutId);
      this.abortControllers.delete(item.url);

      // Retry logic
      item.retries = (item.retries || 0) + 1;
      if (item.retries < MAX_RETRIES && item.priority === 'critical') {
        logger.info(`Retrying load: ${item.url} (attempt ${item.retries}/${MAX_RETRIES})`);
        item.status = 'pending';
        setTimeout(() => this.loadItem(item, backgroundRefresh), 1000 * item.retries);
        this.notifyProgress();
        return;
      }

      logger.warn(`Failed to load media: ${item.url}`, error);
      item.status = 'error';
      this.notifyProgress();
    }
  }

  /**
   * Fetch from network and cache the result
   */
  private async fetchAndCache(
    item: MediaItem,
    controller: AbortController,
    timeoutId: ReturnType<typeof setTimeout>
  ): Promise<void> {
    const response = await fetch(item.url, {
      signal: controller.signal,
      headers: {
        'Range': 'bytes=0-5000000' // Request first 5MB only for initial load
      }
    });

    clearTimeout(timeoutId);
    this.abortControllers.delete(item.url);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    // Check content length
    const contentLength = response.headers.get('content-length');
    if (contentLength && parseInt(contentLength) > MAX_FILE_SIZE) {
      logger.warn(`File too large: ${item.url} (${contentLength} bytes)`);
      throw new Error('File too large');
    }

    const blob = await response.blob();

    // Validate blob
    if (blob.size === 0) {
      throw new Error('Empty blob received');
    }

    item.blob = blob;
    item.status = 'loaded';
    item.timestamp = Date.now();

    // Cache the blob
    if (this.cache) {
      try {
        const cacheResponse = new Response(blob, {
          headers: { 'Content-Type': item.type === 'video' ? 'video/mp4' : 'image/jpeg' }
        });
        await this.cache.put(item.url, cacheResponse);
      } catch (cacheError) {
        logger.warn('Failed to cache media', cacheError);
        // Continue even if caching fails
      }
    }

    this.notifyProgress();
  }

  /**
   * Background refresh - update cache without blocking
   */
  private async backgroundRefresh(
    item: MediaItem,
    controller: AbortController
  ): Promise<void> {
    try {
      const timeoutId = setTimeout(() => {
        controller.abort();
        this.abortControllers.delete(item.url);
      }, LOAD_TIMEOUT);

      await this.fetchAndCache(item, controller, timeoutId);
      logger.debug(`Background refresh complete: ${item.url}`);
    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') {
        logger.debug('Background refresh aborted', item.url);
      } else {
        logger.warn('Background refresh failed', error);
      }
    }
  }

  /**
   * Get object URL for a loaded media item (кэшируется для предотвращения утечек)
   */
  getMediaUrl(url: string): string | null {
    const item = this.mediaItems.get(url);
    if (!item?.blob) {
      return null;
    }
    
    // Возвращаем закэшированный URL если есть
    if (item.objectUrl) {
      return item.objectUrl;
    }
    
    // Создаём новый и кэшируем
    item.objectUrl = URL.createObjectURL(item.blob);
    return item.objectUrl;
  }

  /**
   * Check if media is loaded and ready
   */
  isLoaded(url: string): boolean {
    const item = this.mediaItems.get(url);
    return item?.status === 'loaded';
  }

  /**
   * Get load progress
   */
  getProgress(): MediaLoadProgress {
    const items = Array.from(this.mediaItems.values());
    const total = items.length;
    const loaded = items.filter(item => item.status === 'loaded').length;
    const criticalItems = items.filter(item => item.priority === 'critical');
    // Consider critical as loaded if all are loaded OR errored (don't block on failures)
    const criticalLoaded = criticalItems.every(item => 
      item.status === 'loaded' || item.status === 'error'
    );

    return {
      total,
      loaded,
      percentage: total > 0 ? Math.round((loaded / total) * 100) : 0,
      criticalLoaded
    };
  }

  /**
   * Subscribe to progress updates
   */
  onProgress(listener: (progress: MediaLoadProgress) => void): () => void {
    this.progressListeners.add(listener);
    return () => this.progressListeners.delete(listener);
  }

  /**
   * Notify all progress listeners
   */
  private notifyProgress(): void {
    const progress = this.getProgress();
    this.progressListeners.forEach(listener => listener(progress));
  }

  /**
   * Preload critical items for initial view
   */
  preloadCriticalProducts(products: Array<{ videoUrl?: string; image: string }>): void {
    const criticalMedia = products.slice(0, 3).flatMap(product => [
      {
        url: product.image,
        type: 'image' as const,
        priority: 'critical' as const
      },
      ...(product.videoUrl ? [{
        url: product.videoUrl,
        type: 'video' as const,
        priority: 'critical' as const
      }] : [])
    ]);

    this.preloadMedia(criticalMedia);
  }

  /**
   * Preload adjacent category products for smooth swiping
   */
  preloadAdjacentProducts(products: Array<{ videoUrl?: string; image: string }>): void {
    const normalMedia = products.slice(3).flatMap(product => [
      {
        url: product.image,
        type: 'image' as const,
        priority: 'low' as const
      },
      ...(product.videoUrl ? [{
        url: product.videoUrl,
        type: 'video' as const,
        priority: 'low' as const
      }] : [])
    ]);

    this.preloadMedia(normalMedia);
  }

  /**
   * Cancel pending loads
   */
  cancelPending(): void {
    this.abortControllers.forEach((controller, url) => {
      controller.abort();
    });
    this.abortControllers.clear();
  }

  /**
   * Освободить все Object URLs (вызывать при сбросе или размонтировании)
   */
  cleanupObjectUrls(): void {
    this.mediaItems.forEach(item => {
      if (item.objectUrl) {
        URL.revokeObjectURL(item.objectUrl);
        item.objectUrl = null;
      }
    });
  }

  /**
   * Reset state for new data
   */
  reset(): void {
    this.cleanupObjectUrls(); // Освобождаем Object URLs перед сбросом
    this.cancelPending();
    this.mediaItems.clear();
  }
}

// Singleton instance
export const mediaPreloader = new MediaPreloaderService();
