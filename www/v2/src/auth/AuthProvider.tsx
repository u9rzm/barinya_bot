import { createContext, useEffect, useState, useCallback, ReactNode } from 'react';
import { init} from "@tma.js/sdk";
import { 
  // useAndroidDeviceData,
  // useLaunchParams,
  // init,
  retrieveLaunchParams  } from '@tma.js/bridge';
import { AuthState, TelegramUser, ExternalUser } from './types';
import { secureStorage } from '../utils/secureStorage';
//import { logger } from '../utils/logger';
import {
  AuthErrorState,
  //createAuthError,
  getAuthErrorFromException,
  //AuthErrorClass
} from './authError';

interface AuthContextValue {
  auth: AuthState;
  error: AuthErrorState;
  refresh: () => void;
  logout: () => void;
  setExternalUser: (user: ExternalUser) => void;
  clearError: () => void;
  isReady: boolean;
}

export const AuthContext = createContext<AuthContextValue | null>(null);

/**
 * Извлекаем Telegram пользователя
 * Используем гибридный подход:
 * 1. Сначала пробуем window.Telegram.WebApp.initDataUnsafe (быстро, работает сразу)
 * 2. Если нет, пробуем initData из SDK (требует инициализации)
 */
function getTelegramUserFromInitData(): TelegramUser | null {
  try {
    console.log(retrieveLaunchParams());        
    const initData = retrieveLaunchParams()?.tgWebAppData;
    console.log('[AuthProvider] Launch params initData:', initData);

    if (!initData) {
      console.warn('[AuthProvider] initData not available');
      return null;
    }

    const userData = initData.user;
    console.log('[AuthProvider] User from initData.user():', userData);

    if (!userData) {
      console.warn('[AuthProvider] No user in initData.user() - SDK may not be initialized yet');
      return null;
    }

    const telegramUser: TelegramUser = {
      id: userData.id,
      firstName: userData.first_name,
      lastName: userData.last_name,
      username: userData.username,
      photoUrl: userData.photo_url,
      isPremium: userData.is_premium,
      isBot: userData.is_bot,
      languageCode: userData.language_code,
    };

    console.log('[AuthProvider] Extracted Telegram user from SDK:', telegramUser);
    return telegramUser;
  } catch (error) {
    console.error('[AuthProvider] getTelegramUserFromInitData error:', error);
    return null;
  }
}

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [auth, setAuth] = useState<AuthState>({ type: 'guest' });
  const [error, setError] = useState<AuthErrorState>(null);
  const [isReady, setIsReady] = useState(false);

  /**
   * Очистка ошибки
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  /**
   * Определение текущего состояния авторизации
   */
  const detectAuth = useCallback(() => {
    console.log('[AuthProvider] === DETECT AUTH START ===');
    
    try {
      // 1. Извлекаем пользователя из initData (Telegram)
      const tgUser = getTelegramUserFromInitData();
      console.log('[AuthProvider] User from initData:', tgUser ? tgUser.id : 'null');

      if (tgUser) {
        console.log('[AuthProvider] Setting telegram auth from WebApp:', tgUser.id);
        // Сохраняем в кэш для последующих загрузок
        secureStorage.setItem('telegram_user', tgUser);
        setAuth({ type: 'telegram', user: tgUser });
        setError(null);
        setIsReady(true);
        console.log('[AuthProvider] === DETECT AUTH END (telegram) ===');
        return;
      }

      // 2. Если нет данных из WebApp, пробуем кэш
      console.log('[AuthProvider] No user from WebApp, checking cache...');
      const cachedUser = secureStorage.getItem<TelegramUser>('telegram_user');
      console.log('[AuthProvider] Cached user:', cachedUser ? cachedUser.id : 'null');

      if (cachedUser) {
        console.log('[AuthProvider] Setting telegram auth from cache:', cachedUser.id);
        setAuth({ type: 'telegram', user: cachedUser });
        setError(null);
        setIsReady(true);
        console.log('[AuthProvider] === DETECT AUTH END (cache) ===');
        return;
      }

      // 3. Проверяем внешнего пользователя
      const externalUserRaw = secureStorage.getItem<ExternalUser>('external_user');
      console.log('[AuthProvider] External user check:', externalUserRaw ? externalUserRaw.id : 'null');

      if (externalUserRaw && externalUserRaw.id) {
        console.log('[AuthProvider] Setting external auth:', externalUserRaw.id);
        setAuth({ type: 'external', user: externalUserRaw });
        setError(null);
        setIsReady(true);
        console.log('[AuthProvider] === DETECT AUTH END (external) ===');
        return;
      }

      // 4. Гостевой режим
      console.log('[AuthProvider] Setting guest auth (no data)');
      setAuth({ type: 'guest' });
      setError(null);
      setIsReady(true);
      console.log('[AuthProvider] === DETECT AUTH END (guest) ===');
    } catch (err) {
      console.error('[AuthProvider] Auth detection failed', err);
      const authError = getAuthErrorFromException(err);
      setError(authError);
      setAuth({ type: 'guest' });
      setIsReady(true);
      console.log('[AuthProvider] === DETECT AUTH END (error) ===');
    }
  }, []);

  /**
   * Принудительное обновление данных авторизации
   * Перечитывает WebApp и обновляет кэш
   */
  const refresh = useCallback(() => {
    console.log('[AuthProvider] === REFRESH START ===');
    setError(null);
    setIsReady(false);

    // Пробуем получить свежие данные из initData
    const tgUser = getTelegramUserFromInitData();
    console.log('[AuthProvider] refresh - User from initData:', tgUser ? tgUser.id : 'null');

    if (tgUser) {
      console.log('[AuthProvider] Got fresh data, saving to cache');
      secureStorage.setItem('telegram_user', tgUser);
      setAuth({ type: 'telegram', user: tgUser });
      setError(null);
    } else {
      console.log('[AuthProvider] No fresh data, trying cache...');
      // Если нет свежих данных, пробуем кэш
      const cachedUser = secureStorage.getItem<TelegramUser>('telegram_user');
      console.log('[AuthProvider] From cache:', cachedUser ? cachedUser.id : 'null');
      
      if (cachedUser) {
        console.log('[AuthProvider] Returning cached user:', cachedUser.id);
        setAuth({ type: 'telegram', user: cachedUser });
      } else {
        console.warn('[AuthProvider] No data available, setting guest');
        setAuth({ type: 'guest' });
      }
    }

    setIsReady(true);
    console.log('[AuthProvider] === REFRESH END ===');
  }, []);

  /**
   * Выход из системы
   */
  const logout = useCallback(() => {
    console.log('[AuthProvider] Logging out...');
    try {
      secureStorage.removeItem('telegram_user');
    } catch (e) {
      console.error('[AuthProvider] Failed to clear telegram cache', e);
    }
    try {
      secureStorage.removeItem('external_user');
    } catch (e) {
      console.error('[AuthProvider] Failed to clear external user', e);
    }
    setAuth({ type: 'guest' });
    setError(null);
  }, []);

  /**
   * Установка внешнего пользователя
   */
  const setExternalUser = useCallback((user: ExternalUser) => {
    try {
      console.log('[AuthProvider] Setting external user', { userId: user.id });
      secureStorage.setItem('external_user', user);
      setAuth({ type: 'external', user });
      setError(null);
    } catch (err) {
      console.error('[AuthProvider] Failed to set external user', err);
      setError(getAuthErrorFromException(err));
    }
  }, []);

  /**
   * Инициализация при монтировании
   */
  useEffect(() => {
    // Инициализируем SDK
    try {
      init();
      console.log('[AuthProvider] SDK initialized');
    } catch (e) {
      console.warn('[AuthProvider] SDK init failed (may be not in Telegram)', e);
    }
    
    detectAuth();
  }, [detectAuth]);

  const value: AuthContextValue = {
    auth,
    error,
    refresh,
    logout,
    setExternalUser,
    clearError,
    isReady,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}
