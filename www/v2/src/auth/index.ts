/**
 * Auth module exports
 * 
 * @example
 * ```tsx
 * import { AuthProvider, useAuth, useAuthStatus, useAuthError } from '@/auth';
 * import { AuthErrorDisplay, AuthErrorBadge } from '@/auth';
 * import type { AuthState, TelegramUser, AuthSource, AuthError } from '@/auth';
 * ```
 */

// Provider & Hooks
export { AuthProvider } from './AuthProvider';
export { useAuth, useAuthStatus, useAuthError } from './useAuth';

// Error handling
export { AuthErrorDisplay, AuthErrorBadge } from './AuthErrorDisplay';
export {
  createAuthError,
  getAuthErrorFromException,
  getAuthErrorDisplay,
  isTelegramAvailable,
  hasTelegramUserData,
  AuthErrorClass,
} from './authError';

// Utilities
export { isPremiumUser, formatUserName } from './types';
export { clearTelegramUserCache } from './detectTelegramUser';

// Types
export type { 
  AuthState, 
  AuthSource, 
  TelegramUser, 
  ExternalUser,
} from './types';

export type {
  AuthError,
  AuthErrorCode,
  AuthErrorState,
} from './authError';
