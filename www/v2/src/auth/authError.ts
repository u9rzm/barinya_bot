/**
 * Типы ошибок авторизации
 */
export type AuthErrorCode =
  | 'TELEGRAM_UNAVAILABLE'      // Telegram WebApp недоступен
  | 'NO_USER_DATA'              // Нет данных пользователя в initData
  | 'INVALID_USER_DATA'         // Некорректные данные пользователя
  | 'STORAGE_ERROR'             // Ошибка хранилища
  | 'NETWORK_ERROR'             // Сетевая ошибка
  | 'UNKNOWN'                   // Неизвестная ошибка
  | 'DEV_MODE';                 // Режим разработки (не в Telegram)

/**
 * Структура ошибки авторизации
 */
export interface AuthError {
  code: AuthErrorCode;
  message: string;
  details?: string;
  recoverable: boolean;  // Можно ли восстановить без перезагрузки
  timestamp: number;
}

/**
 * Состояние ошибки авторизации
 */
export type AuthErrorState = AuthError | null;

/**
 * Коды ошибок и их сообщения
 */
const AUTH_ERROR_MESSAGES: Record<AuthErrorCode, { title: string; message: string; recoverable: boolean }> = {
  TELEGRAM_UNAVAILABLE: {
    title: 'Telegram недоступен',
    message: 'Не удалось подключиться к Telegram. Проверьте соединение.',
    recoverable: true,
  },
  NO_USER_DATA: {
    title: 'Нет данных пользователя',
    message: 'Telegram не передал данные пользователя. Попробуйте перезапустить приложение.',
    recoverable: true,
  },
  INVALID_USER_DATA: {
    title: 'Некорректные данные',
    message: 'Получены некорректные данные от Telegram.',
    recoverable: false,
  },
  STORAGE_ERROR: {
    title: 'Ошибка хранилища',
    message: 'Не удалось сохранить данные. Проверьте настройки браузера.',
    recoverable: true,
  },
  NETWORK_ERROR: {
    title: 'Ошибка сети',
    message: 'Проблемы с интернет-соединением.',
    recoverable: true,
  },
  UNKNOWN: {
    title: 'Ошибка авторизации',
    message: 'Произошла неизвестная ошибка при авторизации.',
    recoverable: true,
  },
  DEV_MODE: {
    title: 'Режим разработки',
    message: 'Приложение запущено вне Telegram. Авторизация невозможна.',
    recoverable: false,
  },
};

/**
 * Создание объекта ошибки авторизации
 */
export function createAuthError(
  code: AuthErrorCode,
  details?: string
): AuthError {
  const errorConfig = AUTH_ERROR_MESSAGES[code];
  
  return {
    code,
    message: errorConfig.message,
    details,
    recoverable: errorConfig.recoverable,
    timestamp: Date.now(),
  };
}

/**
 * Определение ошибки из исключения
 */
export function getAuthErrorFromException(error: unknown): AuthError {
  if (error instanceof AuthErrorClass) {
    return error.toAuthError();
  }

  if (error instanceof Error) {
    const message = error.message.toLowerCase();
    
    if (message.includes('network') || message.includes('fetch')) {
      return createAuthError('NETWORK_ERROR', error.message);
    }
    
    if (message.includes('storage') || message.includes('quota')) {
      return createAuthError('STORAGE_ERROR', error.message);
    }
  }

  return createAuthError('UNKNOWN', String(error));
}

/**
 * Класс ошибки авторизации для выбрасывания исключений
 */
export class AuthErrorClass extends Error {
  constructor(
    public code: AuthErrorCode,
    public details?: string
  ) {
    super(AUTH_ERROR_MESSAGES[code].message);
    this.name = 'AuthError';
  }

  toAuthError(): AuthError {
    return createAuthError(this.code, this.details);
  }
}

/**
 * Проверка доступности Telegram WebApp
 */
export function isTelegramAvailable(): boolean {
  if (typeof window === 'undefined') return false;
  return !!(window as any).Telegram?.WebApp;
}

/**
 * Проверка наличия данных пользователя в Telegram
 */
export function hasTelegramUserData(): boolean {
  if (!isTelegramAvailable()) return false;
  const tg = (window as any).Telegram.WebApp;
  return !!(tg.initDataUnsafe?.user?.id);
}

/**
 * Получение понятного сообщения об ошибке
 */
export function getAuthErrorDisplay(error: AuthError): {
  title: string;
  message: string;
  recoverable: boolean;
} {
  return AUTH_ERROR_MESSAGES[error.code];
}
