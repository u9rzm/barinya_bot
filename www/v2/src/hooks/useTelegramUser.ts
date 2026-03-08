import { useMemo } from 'react';
import { useLaunchParams } from '@tma.js/sdk-react';
import { logger } from '../utils/logger';
import { secureStorage } from '../utils/secureStorage';

/**
 * Расширенный интерфейс пользователя с данными из Telegram
 * Соответствует типам из @tma.js/bridge
 */
export interface TelegramUser {
  id: number;
  username?: string;
  firstName?: string;
  lastName?: string;
  photoUrl?: string;
  isPremium?: boolean;
  isBot?: boolean;
  languageCode?: string;
}

/**
 * Хук для получения и управления данными пользователя Telegram
 * Использует официальный TMA React SDK с правильными типами
 * 
 * @returns Объект с данными пользователя и методами управления
 * 
 * @example
 * ```typescript
 * const { user, isLoading, isAuthenticated, logout, refresh } = useTelegramUser();
 * ```
 */
export function useTelegramUser() {
  // Получаем launch params из официального SDK
  // useLaunchParams() автоматически парсит initData и возвращает типизированный объект
  // tgWebAppData.user уже распарсен из JSON благодаря SDK
  const launchParams = useLaunchParams();

  // Debug logging
  useMemo(() => {
    logger.info('Telegram Launch Params', {
      hasLaunchParams: !!launchParams,
      hasTgWebAppData: !!launchParams?.tgWebAppData,
      platform: launchParams?.tgWebAppPlatform,
      version: launchParams?.tgWebAppVersion
    });
  }, [launchParams]);

  // Извлекаем пользователя из launch params
  const telegramUser: TelegramUser | null = useMemo(() => {
    // Проверяем кэш в secureStorage
    const cachedUser = secureStorage.getItem<TelegramUser>('telegram_user');
    
    // Если есть tgWebAppData, извлекаем пользователя
    // SDK уже распарсил JSON, поэтому user - это объект с правильными типами
    if (launchParams?.tgWebAppData?.user) {
      const userData = launchParams.tgWebAppData.user;
      logger.info('Telegram user data from launch params', { 
        id: userData.id,
        username: userData.username,
        firstName: userData.first_name
      });
      
      const user: TelegramUser = {
        id: userData.id,
        username: userData.username || undefined,
        firstName: userData.first_name || undefined,
        lastName: userData.last_name || undefined,
        photoUrl: userData.photo_url || undefined,
        isPremium: Boolean(userData.is_premium),
        isBot: Boolean(userData.is_bot),
        languageCode: userData.language_code || undefined,
      };
      
      // Сохраняем в кэш
      secureStorage.setItem('telegram_user', user);
      
      logger.info('Telegram user loaded', { 
        userId: user.id,
        username: user.username 
      });
      
      return user;
    }
    
    // Возвращаем из кэша если нет данных из Telegram
    if (cachedUser) {
      return cachedUser;
    }
    
    // Возвращаем null - это нормально, приложение продолжит работу в гостевом режиме
    return null;
  }, [launchParams?.tgWebAppData]);

  // Определяем статус загрузки (false, так как мы всегда готовы работать)
  const isLoading = false;
  
  // Определяем статус аутентификации (true если есть пользователь из Telegram)
  const isAuthenticated = !!telegramUser;

  logger.debug('useTelegramUser state', { 
    hasUser: !!telegramUser, 
    isLoading, 
    isAuthenticated 
  });

  /**
   * Выход из системы (очистка данных пользователя)
   */
  const logout = () => {
    secureStorage.removeItem('telegram_user');
    logger.info('User logged out');
    // Перезагружаем страницу для сброса состояния SDK
    window.location.reload();
  };

  /**
   * Принудительная перезагрузка данных пользователя
   */
  const refresh = async () => {
    secureStorage.removeItem('telegram_user');
    logger.info('User data refreshed');
    // Перезагружаем страницу для получения актуальных данных
    window.location.reload();
  };

  return {
    user: telegramUser,
    isLoading,
    isAuthenticated,
    logout,
    refresh,
  };
}

/**
 * Утилита для форматирования имени пользователя
 */
export function formatUserName(user: TelegramUser | null): string {
  if (!user) return 'Гость';

  if (user.username) {
    return `@${user.username}`;
  }

  const parts = [user.firstName, user.lastName].filter((name): name is string => Boolean(name));
  return parts.join(' ') || 'Пользователь';
}

/**
 * Утилита для проверки премиум статуса
 */
export function isPremiumUser(user: TelegramUser | null): boolean {
  return Boolean(user?.isPremium);
}
