import { useState, useRef, useEffect } from 'react';
import { motion } from 'motion/react';
import Hls from 'hls.js';
import { cn } from '../utils/cn';
import { mediaPreloader } from '../services/mediaPreloader';
import { logger } from '../utils/logger';

interface OptimizedVideoProps {
  src?: string;
  poster: string;
  className?: string;
  active?: boolean;
  preload?: boolean;
  onLoaded?: () => void;
}

/**
 * Оптимизированный видеоплеер с поддержкой HLS (как в Instagram) и MP4.
 * Обеспечивает мгновенный старт и адаптивное качество.
 *
 * Features:
 * - Использует предварительно загруженные медиа из mediaPreloader
 * - Мгновенное воспроизведение для закэшированных видео
 * - Плавный переход между загруженным и потоковым контентом
 * - Постер всегда виден пока видео не готово (нет чёрного экрана)
 * - Видео поверх постера с плавным появлением
 */
export function OptimizedVideo({ src, poster, className, active = true, preload = false, onLoaded }: OptimizedVideoProps) {
  const [isReady, setIsReady] = useState(false);
  const [shouldLoad, setShouldLoad] = useState(false);
  const [objectUrl, setObjectUrl] = useState<string | null>(null);
  const [videoOpacity, setVideoOpacity] = useState(0);
  const [hasError, setHasError] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);
  const hlsRef = useRef<Hls | null>(null);
  const isMounted = useRef(true);
  const prevSrcRef = useRef<string | undefined>(undefined);
  const objectUrlRef = useRef<string | null>(null);

  // Единый cleanup для всех ресурсов при размонтировании
  useEffect(() => {
    isMounted.current = true;
    return () => {
      isMounted.current = false;
      
      // Cleanup HLS instance
      if (hlsRef.current) {
        hlsRef.current.destroy();
        hlsRef.current = null;
      }
      
      // Cleanup object URL (не освобождаем если из mediaPreloader - там свой кэш)
      if (objectUrlRef.current && !mediaPreloader.isLoaded(src || '')) {
        URL.revokeObjectURL(objectUrlRef.current);
        objectUrlRef.current = null;
      }
    };
  }, []); // Только при mount/unmount

  // Сбрасываем состояние при смене источника
  useEffect(() => {
    if (src !== prevSrcRef.current) {
      setIsReady(false);
      setVideoOpacity(0);
      setHasError(false);
      prevSrcRef.current = src;

      // Cleanup old resources before loading new
      if (hlsRef.current) {
        hlsRef.current.destroy();
        hlsRef.current = null;
      }
      
      // Revoke old object URL only if it's not from preloader cache
      if (objectUrlRef.current && !mediaPreloader.isLoaded(src || '')) {
        URL.revokeObjectURL(objectUrlRef.current);
        objectUrlRef.current = null;
      }
      setObjectUrl(null);
    }
  }, [src]);

  // Управление загрузкой (начинаем сразу, если активно или разрешен предзагруз)
  useEffect(() => {
    if ((active || preload) && src && !objectUrlRef.current) {
      setShouldLoad(true);

      // Try to get preloaded media first
      const preloadedUrl = mediaPreloader.getMediaUrl(src);
      if (preloadedUrl) {
        setObjectUrl(preloadedUrl);
        objectUrlRef.current = preloadedUrl;
      }
    }
  }, [active, preload, src]);

  // Вызов колбэка при готовности
  useEffect(() => {
    if (isReady && onLoaded) {
      onLoaded();
    }
  }, [isReady, onLoaded]);

  // Инициализация видео (HLS или Native)
  useEffect(() => {
    if (shouldLoad && videoRef.current && src) {
      const video = videoRef.current;

      // Use preloaded blob if available (from ref to avoid stale state)
      const videoSource = objectUrlRef.current || mediaPreloader.getMediaUrl(src) || src;

      // Проверка на HLS (m3u8)
      if (src.includes('.m3u8')) {
        if (Hls.isSupported()) {
          const hls = new Hls({
            capLevelToPlayerSize: true,
            autoStartLoad: true,
            startLevel: 0, // Start with lowest quality for fast startup
          });
          hls.loadSource(videoSource);
          hls.attachMedia(video);
          hlsRef.current = hls;

          hls.on(Hls.Events.MANIFEST_PARSED, () => {
            if (active && isMounted.current) {
              video.play().catch((err) => {
                logger.debug('Autoplay prevented', err);
              });
            }
          });

          hls.on(Hls.Events.LEVEL_LOADED, () => {
            if (isMounted.current) {
              setIsReady(true);
              // Smooth fade in video over poster
              setVideoOpacity(1);
            }
          });
        } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
          // Native HLS (Safari)
          video.src = videoSource;
          video.onloadeddata = () => {
            if (isMounted.current) {
              setIsReady(true);
              setVideoOpacity(1);
              if (active) {
                video.play().catch((err) => {
                  logger.debug('Autoplay prevented', err);
                });
              }
            }
          };
        }
      } else {
        // Обычный MP4 or preloaded blob
        video.src = videoSource;
        video.onloadeddata = () => {
          if (isMounted.current) {
            setIsReady(true);
            setVideoOpacity(1);
            if (active) {
              video.play().catch((err) => {
                logger.debug('Autoplay prevented', err);
              });
            }
          }
        };
      }
    }

    // Cleanup при смене shouldLoad/src/active
    return () => {
      if (hlsRef.current) {
        hlsRef.current.destroy();
        hlsRef.current = null;
      }
    };
  }, [shouldLoad, src, active]);

  // Управление воспроизведением при переключении active
  useEffect(() => {
    const video = videoRef.current;
    if (video && isReady) {
      if (active) {
        // Reset opacity for smooth fade in when becoming active
        setVideoOpacity(0);
        // Force reflow
        void video.offsetWidth;
        setVideoOpacity(1);
        video.play().catch((err) => {
          logger.debug('Autoplay prevented', err);
        });
      } else {
        video.pause();
        setVideoOpacity(0);
      }
    }
  }, [active, isReady]);

  // Плавный переход в конце видео (crossfade к постеру)
  const [loopOpacity, setLoopOpacity] = useState(1);

  const handleTimeUpdate = () => {
    const video = videoRef.current;
    if (!video || video.duration === 0) return;

    const timeLeft = video.duration - video.currentTime;
    // Начинаем затухание за 0.4 секунды до конца
    if (timeLeft < 0.4) {
      setLoopOpacity(0);
    } else if (video.currentTime < 0.4) {
      // Плавное появление в начале
      setLoopOpacity(1);
    } else {
      setLoopOpacity(1);
    }
  };

  const handleVideoError = (e: React.SyntheticEvent<HTMLVideoElement>) => {
    logger.warn('Video failed to load:', e);
    setHasError(true);
    setIsReady(true); // Show poster
    setVideoOpacity(0);
  };

  // Timeout fallback - if video doesn't load in 10 seconds, show poster
  useEffect(() => {
    if (shouldLoad && !isReady && !hasError) {
      const timeout = setTimeout(() => {
        if (!isReady) {
          logger.warn('Video loading timeout - showing poster');
          setIsReady(true);
          setHasError(true);
          setVideoOpacity(0);
        }
      }, 10000);
      return () => clearTimeout(timeout);
    }
  }, [shouldLoad, isReady, hasError]);

  // Calculate final video opacity based on active state and loop
  const finalVideoOpacity = active && isReady && !hasError ? videoOpacity * loopOpacity : 0;

  return (
    <div className={cn("relative w-full h-full overflow-hidden", className)}>
      {/* Изображение-заглушка (всегда видно, пока видео не готово) */}
      <img
        src={poster}
        className={cn(
          "absolute inset-0 w-full h-full object-cover z-0",
          // Poster always visible when video is not ready or not active
          isReady && !hasError ? "opacity-100" : "opacity-100"
        )}
        alt="Poster"
        draggable={false}
        loading="eager"
        fetchPriority="high"
      />

      {/* Видео слой (поверх постера с плавным появлением) */}
      {shouldLoad && !hasError && (
        <motion.video
          ref={videoRef}
          muted
          playsInline
          loop
          preload="auto"
          autoPlay={active}
          onLoadedData={() => {
            setIsReady(true);
            setVideoOpacity(1);
          }}
          onError={handleVideoError}
          onTimeUpdate={handleTimeUpdate}
          onEnded={() => {
            if (videoRef.current) {
              videoRef.current.currentTime = 0;
              videoRef.current.play().catch((err) => {
                logger.debug('Video replay failed', err);
              });
            }
          }}
          style={{ opacity: finalVideoOpacity }}
          className="absolute inset-0 w-full h-full object-cover z-10"
        />
      )}
    </div>
  );
}
