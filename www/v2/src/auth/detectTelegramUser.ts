import { TelegramUser } from './types';
import { secureStorage } from '../utils/secureStorage';
import { logger } from '../utils/logger';

/**
 * Очистка кэша пользователя
 */
export function clearTelegramUserCache(): void {
  console.log('[clearTelegramUserCache] Clearing cache...');
  secureStorage.removeItem('telegram_user');
  console.log('[clearTelegramUserCache] Done');
}
