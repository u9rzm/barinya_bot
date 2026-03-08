/**
 * Тип источника авторизации
 */
export type AuthSource = 'telegram' | 'external' | 'guest';

/**
 * Telegram пользователь
 */
export interface TelegramUser {
  id: number;
  firstName?: string;
  username?: string;
  lastName?: string;
  photoUrl?: string;
  isPremium?: boolean;
  isBot?: boolean;
  languageCode?: string;
}

/**
 * Внешний пользователь (для будущей интеграции с другими провайдерами)
 */
export interface ExternalUser {
  id: string;
  email?: string;
  name?: string;
  avatar?: string;
  [key: string]: any;
}

/**
 * Состояние авторизации через union type
 * Это устраняет ошибки с undefined и делает код типобезопасным
 */
export type AuthState =
  | { type: 'telegram'; user: TelegramUser }
  | { type: 'external'; user: ExternalUser }
  | { type: 'guest' };

/**
 * Проверка на премиум статус
 */
export function isPremiumUser(user: TelegramUser | null | undefined): boolean {
  return Boolean(user?.isPremium);
}

/**
 * Форматирование имени пользователя
 */
export function formatUserName(user: TelegramUser | null | undefined): string {
  if (!user) return 'Гость';

  if (user.username) {
    return `@${user.username}`;
  }

  const parts = [user.firstName, user.lastName].filter((name): name is string => Boolean(name));
  return parts.join(' ') || 'Пользователь';
}
