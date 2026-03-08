import { useContext } from 'react';
import { AuthContext } from './AuthProvider';

/**
 * Хук для использования контекста авторизации
 * 
 * @returns Объект с состоянием авторизации и методами управления
 * 
 * @throws Error если используется вне AuthProvider
 * 
 * @example
 * ```tsx
 * function MyComponent() {
 *   const { auth, error, refresh, logout, clearError } = useAuth();
 * 
 *   if (error) {
 *     return <ErrorDisplay error={error} onRetry={refresh} />;
 *   }
 * 
 *   switch (auth.type) {
 *     case 'telegram':
 *       return <div>Привет, {auth.user.username}!</div>;
 *     case 'external':
 *       return <div>Привет, {auth.user.name}!</div>;
 *     case 'guest':
 *       return <div>Гость</div>;
 *   }
 * }
 * ```
 */
export function useAuth() {
  const ctx = useContext(AuthContext);

  if (!ctx) {
    throw new Error(
      'useAuth must be used inside AuthProvider. ' +
      'Wrap your component tree with <AuthProvider>.'
    );
  }

  return ctx;
}

/**
 * Селектор для проверки статуса авторизации
 * 
 * @example
 * ```tsx
 * const { isTelegram, isGuest, isAuthenticated } = useAuthStatus();
 * 
 * if (isTelegram) {
 *   // Показываем премиум функции
 * }
 * ```
 */
export function useAuthStatus() {
  const { auth } = useAuth();

  return {
    isTelegram: auth.type === 'telegram',
    isExternal: auth.type === 'external',
    isGuest: auth.type === 'guest',
    isAuthenticated: auth.type !== 'guest',
  };
}

/**
 * Хук для обработки ошибок авторизации
 * 
 * @example
 * ```tsx
 * function MyComponent() {
 *   const { hasError, isRecoverable, retry, dismiss } = useAuthError();
 * 
 *   if (hasError) {
 *     return (
 *       <div>
 *         <p>Ошибка: {error.message}</p>
 *         {isRecoverable && <button onClick={retry}>Повторить</button>}
 *         <button onClick={dismiss}>Закрыть</button>
 *       </div>
 *     );
 *   }
 * 
 *   return <div>OK</div>;
 * }
 * ```
 */
export function useAuthError() {
  const { error, refresh, clearError } = useAuth();

  return {
    error,
    hasError: !!error,
    isRecoverable: error?.recoverable ?? false,
    retry: refresh,
    dismiss: clearError,
  };
}
