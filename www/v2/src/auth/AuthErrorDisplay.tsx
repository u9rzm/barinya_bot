import { motion, AnimatePresence } from 'motion/react';
import { AlertTriangle, RefreshCw, X, Wifi, Database, UserX, Smartphone } from 'lucide-react';
import { cn } from '../utils/cn';
import { AuthError } from './authError';

interface AuthErrorDisplayProps {
  error: AuthError;
  onRetry?: () => void;
  onDismiss?: () => void;
  theme?: 'light' | 'dark';
}

/**
 * Компонент отображения ошибки авторизации
 * 
 * @example
 * ```tsx
 * const { error, refresh, clearError } = useAuth();
 * 
 * if (error) {
 *   return <AuthErrorDisplay error={error} onRetry={refresh} onDismiss={clearError} />;
 * }
 * ```
 */
export function AuthErrorDisplay({
  error,
  onRetry,
  onDismiss,
  theme = 'dark',
}: AuthErrorDisplayProps) {
  const iconMap = {
    TELEGRAM_UNAVAILABLE: <Wifi size={24} />,
    NO_USER_DATA: <UserX size={24} />,
    INVALID_USER_DATA: <AlertTriangle size={24} />,
    STORAGE_ERROR: <Database size={24} />,
    NETWORK_ERROR: <Wifi size={24} />,
    UNKNOWN: <AlertTriangle size={24} />,
    DEV_MODE: <Smartphone size={24} />,
  };

  const colorMap = {
    TELEGRAM_UNAVAILABLE: 'text-yellow-500',
    NO_USER_DATA: 'text-orange-500',
    INVALID_USER_DATA: 'text-red-500',
    STORAGE_ERROR: 'text-purple-500',
    NETWORK_ERROR: 'text-yellow-500',
    UNKNOWN: 'text-red-500',
    DEV_MODE: 'text-blue-500',
  };

  const iconColor = colorMap[error.code] || 'text-red-500';

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        className={cn(
          "fixed top-4 left-4 right-4 z-[200] max-w-md mx-auto",
        )}
      >
        <div className={cn(
          "rounded-2xl shadow-2xl overflow-hidden border",
          theme === 'dark'
            ? "bg-[#1a1a1a] border-white/10"
            : "bg-white border-black/10"
        )}>
          {/* Header with Icon */}
          <div className={cn(
            "p-4 flex items-center gap-3",
            theme === 'dark' ? "bg-white/5" : "bg-black/5"
          )}>
            <div className={cn(
              "w-10 h-10 rounded-xl flex items-center justify-center",
              theme === 'dark' ? "bg-white/10" : "bg-black/5",
              iconColor
            )}>
              {iconMap[error.code]}
            </div>
            <div className="flex-1">
              <h3 className={cn(
                "font-bold text-sm",
                theme === 'dark' ? "text-white" : "text-black"
              )}>
                {error.code.replace(/_/g, ' ')}
              </h3>
              <p className={cn(
                "text-xs",
                theme === 'dark' ? "text-white/60" : "text-black/60"
              )}>
                {new Date(error.timestamp).toLocaleTimeString()}
              </p>
            </div>
            {onDismiss && (
              <button
                onClick={onDismiss}
                className={cn(
                  "w-8 h-8 rounded-lg flex items-center justify-center transition-colors",
                  theme === 'dark'
                    ? "hover:bg-white/10"
                    : "hover:bg-black/5"
                )}
              >
                <X size={16} className={cn(
                  theme === 'dark' ? "text-white/60" : "text-black/60"
                )} />
              </button>
            )}
          </div>

          {/* Message */}
          <div className="p-4">
            <p className={cn(
              "text-sm mb-3",
              theme === 'dark' ? "text-white/80" : "text-black/80"
            )}>
              {error.message}
            </p>
            
            {error.details && (
              <details className={cn(
                "text-xs mb-3 p-2 rounded-lg",
                theme === 'dark' ? "bg-white/5 text-white/50" : "bg-black/5 text-black/50"
              )}>
                <summary className="cursor-pointer font-medium">Детали</summary>
                <pre className="mt-2 whitespace-pre-wrap break-all font-mono">
                  {error.details}
                </pre>
              </details>
            )}

            {/* Actions */}
            <div className="flex gap-2">
              {onRetry && error.recoverable && (
                <button
                  onClick={onRetry}
                  className="flex-1 flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl bg-blue-500 hover:bg-blue-600 text-white font-medium text-sm transition-colors"
                >
                  <RefreshCw size={16} />
                  Повторить
                </button>
              )}
              {onDismiss && (
                <button
                  onClick={onDismiss}
                  className={cn(
                    "flex-1 py-2.5 px-4 rounded-xl font-medium text-sm transition-colors",
                    theme === 'dark'
                      ? "bg-white/10 hover:bg-white/20 text-white"
                      : "bg-black/5 hover:bg-black/10 text-black"
                  )}
                >
                  {error.recoverable ? 'Закрыть' : 'OK'}
                </button>
              )}
            </div>
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  );
}

/**
 * Компонент индикатора ошибки (компактный)
 */
interface AuthErrorBadgeProps {
  error: AuthError;
  onClick?: () => void;
  theme?: 'light' | 'dark';
}

export function AuthErrorBadge({ error, onClick, theme = 'dark' }: AuthErrorBadgeProps) {
  const colorMap = {
    TELEGRAM_UNAVAILABLE: 'bg-yellow-500',
    NO_USER_DATA: 'bg-orange-500',
    INVALID_USER_DATA: 'bg-red-500',
    STORAGE_ERROR: 'bg-purple-500',
    NETWORK_ERROR: 'bg-yellow-500',
    UNKNOWN: 'bg-red-500',
    DEV_MODE: 'bg-blue-500',
  };

  return (
    <button
      onClick={onClick}
      className={cn(
        "flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium transition-all",
        theme === 'dark'
          ? "bg-white/10 hover:bg-white/20"
          : "bg-black/5 hover:bg-black/10"
      )}
    >
      <span className={cn(
        "w-2 h-2 rounded-full animate-pulse",
        colorMap[error.code] || 'bg-red-500'
      )} />
      <span className={cn(
        theme === 'dark' ? "text-white/80" : "text-black/80"
      )}>
        Ошибка авторизации
      </span>
    </button>
  );
}
