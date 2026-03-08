import { useState, useEffect, useRef } from 'react';
import { cn } from '../utils/cn';

interface OptimizedImageProps {
  src: string;
  alt?: string;
  className?: string;
  placeholder?: 'blur' | 'pulse' | 'color';
  placeholderColor?: string;
  blurDataURL?: string;
  aspectRatio?: string;
  priority?: boolean;
  onError?: () => void;
  onLoad?: () => void;
}

/**
 * Оптимизированный компонент изображения с lazy loading, placeholder и fallback.
 * 
 * Features:
 * - Lazy loading через Intersection Observer
 * - Placeholder (blur/pulse/color) до загрузки изображения
 * - Fallback на ошибку загрузки
 * - Плавное проявление после загрузки
 */
export function OptimizedImage({
  src,
  alt = '',
  className,
  placeholder = 'pulse',
  placeholderColor,
  blurDataURL,
  aspectRatio = 'aspect-square',
  priority = false,
  onError,
  onLoad
}: OptimizedImageProps) {
  const [isLoaded, setIsLoaded] = useState(false);
  const [hasError, setHasError] = useState(false);
  const [isVisible, setIsVisible] = useState(priority || false);
  const imgRef = useRef<HTMLImageElement>(null);

  // Intersection Observer для lazy loading
  useEffect(() => {
    if (priority) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.disconnect();
        }
      },
      {
        rootMargin: '50px', // Начинать загрузку за 50px до появления
        threshold: 0.01
      }
    );

    if (imgRef.current) {
      observer.observe(imgRef.current);
    }

    return () => observer.disconnect();
  }, [priority]);

  const handleLoad = () => {
    setIsLoaded(true);
    onLoad?.();
  };

  const handleError = () => {
    setHasError(true);
    onError?.();
  };

  // Placeholder styles
  const getPlaceholderStyle = () => {
    if (placeholderColor) {
      return { backgroundColor: placeholderColor };
    }

    switch (placeholder) {
      case 'blur':
        if (blurDataURL) {
          return {
            backgroundImage: `url(${blurDataURL})`,
            backgroundSize: 'cover',
            backgroundPosition: 'center',
            filter: 'blur(20px)',
          };
        }
        return { backgroundColor: '#e4e3e0' };
      case 'pulse':
        return {
          backgroundColor: '#e4e3e0',
          animation: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        };
      default:
        return { backgroundColor: '#e4e3e0' };
    }
  };

  return (
    <div
      ref={imgRef}
      className={cn(
        'relative w-full h-full overflow-hidden',
        aspectRatio,
        className
      )}
    >
      {/* Placeholder */}
      {!isLoaded && !hasError && (
        <div
          className="absolute inset-0 w-full h-full"
          style={getPlaceholderStyle()}
        >
          {placeholder === 'pulse' && (
            <style>{`
              @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
              }
            `}</style>
          )}
        </div>
      )}

      {/* Error fallback */}
      {hasError && (
        <div className="absolute inset-0 w-full h-full flex items-center justify-center bg-gray-100 text-gray-400">
          <svg
            className="w-12 h-12"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
            />
          </svg>
        </div>
      )}

      {/* Actual image */}
      {isVisible && !hasError && (
        <img
          src={src}
          alt={alt}
          onLoad={handleLoad}
          onError={handleError}
          className={cn(
            'w-full h-full object-cover transition-opacity duration-500',
            isLoaded ? 'opacity-100' : 'opacity-0'
          )}
          loading={priority ? 'eager' : 'lazy'}
          fetchPriority={priority ? 'high' : 'auto'}
          decoding="async"
        />
      )}
    </div>
  );
}
