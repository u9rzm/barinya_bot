import CryptoJS from 'crypto-js';
import { logger } from './logger';

/**
 * Secure storage utility with AES encryption
 * Uses environment variable for encryption key or falls back to a default (for development only)
 */

// WARNING: In production, use a proper secret from environment variables
// This is a fallback for development only
const STORAGE_KEY = (import.meta as { env?: { VITE_STORAGE_ENCRYPTION_KEY?: string } }).env?.VITE_STORAGE_ENCRYPTION_KEY
  || 'dev-key-change-in-production-2024-secure-key';

export const secureStorage = {
  /**
   * Encrypt and store data in localStorage
   */
  setItem: (key: string, value: unknown): void => {
    try {
      const stringValue = JSON.stringify(value);
      logger.debug('[secureStorage] setItem', { key, type: typeof value, hasValue: !!value });
      const encrypted = CryptoJS.AES.encrypt(stringValue, STORAGE_KEY).toString();
      localStorage.setItem(key, encrypted);
      logger.debug('[secureStorage] setItem encrypted success', { key, encryptedLength: encrypted.length });
    } catch (error) {
      logger.error('[secureStorage] setItem encryption failed', error);
      console.error('Failed to encrypt and store data:', error);
      // Fallback to unencrypted storage if encryption fails
      localStorage.setItem(key, JSON.stringify(value));
      logger.debug('[secureStorage] setItem fallback unencrypted', { key });
    }
  },

  /**
   * Retrieve and decrypt data from localStorage
   */
  getItem: <T>(key: string): T | null => {
    try {
      const encrypted = localStorage.getItem(key);
      logger.debug('[secureStorage] getItem', { key, hasEncrypted: !!encrypted });
      if (!encrypted) return null;

      const bytes = CryptoJS.AES.decrypt(encrypted, STORAGE_KEY);
      const decrypted = bytes.toString(CryptoJS.enc.Utf8);
      logger.debug('[secureStorage] getItem decrypted', { key, decryptedLength: decrypted?.length });

      if (!decrypted) return null;

      const parsed = JSON.parse(decrypted) as T;
      logger.debug('[secureStorage] getItem success', { key, parsedType: typeof parsed });
      return parsed;
    } catch (error) {
      logger.error('[secureStorage] getItem decryption failed', error);
      console.error('Failed to decrypt data:', error);
      // Fallback: try to read as unencrypted JSON
      try {
        const item = localStorage.getItem(key);
        if (!item) return null;
        const parsed = JSON.parse(item) as T;
        logger.debug('[secureStorage] getItem fallback unencrypted success', { key });
        return parsed;
      } catch (e) {
        logger.error('[secureStorage] getItem fallback failed', e);
        return null;
      }
    }
  },

  /**
   * Remove item from localStorage
   */
  removeItem: (key: string): void => {
    logger.debug('[secureStorage] removeItem', { key });
    localStorage.removeItem(key);
  },

  /**
   * Clear all items from localStorage
   */
  clear: (): void => {
    logger.info('[secureStorage] clear');
    localStorage.clear();
  },
};
