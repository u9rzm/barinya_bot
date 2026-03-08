/**
 * Validators for user input validation
 */

export const validators = {
  /**
   * Validates Russian phone number format (+7 or 8, 11 digits)
   * @example
   * validators.phone('+79991234567') // true
   * validators.phone('89991234567') // true
   * validators.phone('+7 (999) 123-45-67') // true
   */
  phone: (value: string): boolean => {
    const cleaned = value.replace(/\D/g, '');
    return /^(\+7|7|8)\d{10}$/.test(cleaned);
  },

  /**
   * Validates address (minimum 10 characters)
   */
  address: (value: string): boolean => {
    return value.trim().length >= 10;
  },

  /**
   * Validates name (2-50 characters, Cyrillic/Latin letters, spaces, hyphens)
   */
  name: (value: string): boolean => {
    return /^[a-zA-Zа-яА-ЯёЁ\s-]{2,50}$/.test(value.trim());
  },

  /**
   * Validates card number (16 digits, with or without spaces)
   */
  cardNumber: (value: string): boolean => {
    const cleaned = value.replace(/\s/g, '');
    return /^\d{16}$/.test(cleaned);
  },

  /**
   * Validates CVV (3 digits)
   */
  cvv: (value: string): boolean => {
    return /^\d{3}$/.test(value);
  },

  /**
   * Validates expiry date (MM/YY format)
   */
  expiryDate: (value: string): boolean => {
    return /^(0[1-9]|1[0-2])\/\d{2}$/.test(value);
  },
};

/**
 * Validation error messages in Russian
 */
export const validationMessages = {
  phone: 'Введите корректный номер телефона (например, +7 (999) 123-45-67)',
  address: 'Адрес должен содержать не менее 10 символов',
  name: 'Имя должно содержать от 2 до 50 символов (только буквы)',
  cardNumber: 'Введите корректный номер карты (16 цифр)',
  cvv: 'CVV должен содержать 3 цифры',
  expiryDate: 'Срок действия в формате ММ/ГГ',
  required: 'Это поле обязательно для заполнения',
};

/**
 * Helper to get validation error message
 * @returns Error message if invalid, null if valid
 */
export function validateField(
  value: string,
  validator: (v: string) => boolean,
  message: string,
  isRequired = true
): string | null {
  if (!value && isRequired) {
    return validationMessages.required;
  }
  if (!value && !isRequired) {
    return null;
  }
  return validator(value) ? null : message;
}
