import { useEffect } from 'react';
import { useAuth, useAuthStatus } from '../auth';
import { logger } from '../utils/logger';

/**
 * Debug компонент для отладки авторизации
 * Показывает текущее состояние auth контекста
 */
export function AuthDebug() {
  const { auth, error, isReady, refresh, clearError } = useAuth();
  const { isTelegram, isGuest, isAuthenticated } = useAuthStatus();

  useEffect(() => {
    logger.info('[AuthDebug] State changed', {
      auth: {
        type: auth.type,
        user: auth.type === 'telegram' ? {
          id: auth.user.id,
          username: auth.user.username,
          firstName: auth.user.firstName
        } : null
      },
      error: error ? { code: error.code, message: error.message } : null,
      isReady,
      isTelegram,
      isGuest,
      isAuthenticated,
    });
  }, [auth, error, isReady, isTelegram, isGuest, isAuthenticated]);

  return (
    <div style={{
      position: 'fixed',
      bottom: 10,
      left: 10,
      zIndex: 9999,
      background: 'rgba(0,0,0,0.8)',
      color: '#fff',
      padding: '10px 15px',
      borderRadius: 8,
      fontSize: 12,
      fontFamily: 'monospace',
      maxWidth: 400,
    }}>
      <div style={{ marginBottom: 8, fontWeight: 'bold', color: '#4CAF50' }}>
        AUTH DEBUG
      </div>
      <div>Ready: {String(isReady)}</div>
      <div>Type: {auth.type}</div>
      <div>Telegram: {String(isTelegram)}</div>
      <div>Guest: {String(isGuest)}</div>
      <div>Authenticated: {String(isAuthenticated)}</div>
      {auth.type === 'telegram' && (
        <div>User: {auth.user.username || auth.user.firstName} (ID: {auth.user.id})</div>
      )}
      {error && (
        <div style={{ color: '#f44336', marginTop: 8 }}>
          Error: {error.code} - {error.message}
        </div>
      )}
      <div style={{ marginTop: 8, display: 'flex', gap: 8 }}>
        <button
          onClick={refresh}
          style={{
            padding: '4px 8px',
            background: '#2196F3',
            color: '#fff',
            border: 'none',
            borderRadius: 4,
            cursor: 'pointer',
          }}
        >
          Refresh
        </button>
        {error && (
          <button
            onClick={clearError}
            style={{
              padding: '4px 8px',
              background: '#f44336',
              color: '#fff',
              border: 'none',
              borderRadius: 4,
              cursor: 'pointer',
            }}
          >
            Clear Error
          </button>
        )}
      </div>
    </div>
  );
}
