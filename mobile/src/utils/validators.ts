/**
 * validators.ts
 *
 * Input validation functions for forms.
 */

// Email validation
export const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

// Password validation
export const validatePassword = (password: string): boolean => {
  // At least 8 characters
  // Must contain: uppercase, lowercase, digit, special character
  const passwordRegex =
    /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
  return passwordRegex.test(password);
};

// Username validation
export const validateUsername = (username: string): boolean => {
  // 3-50 characters, alphanumeric + underscore
  const usernameRegex = /^[a-zA-Z0-9_]{3,50}$/;
  return usernameRegex.test(username);
};

// Password strength calculator
export interface PasswordStrength {
  level: number; // 0-4
  label: string;
  color: string;
}

export const getPasswordStrength = (
  password: string,
): PasswordStrength => {
  if (!password) {
    return { level: 0, label: '', color: '#999' };
  }

  let strength = 0;

  // Length check
  if (password.length >= 8) strength++;
  if (password.length >= 12) strength++;

  // Complexity checks
  if (/[a-z]/.test(password)) strength++;
  if (/[A-Z]/.test(password)) strength++;
  if (/\d/.test(password)) strength++;
  if (/[@$!%*?&]/.test(password)) strength++;

  // Cap at 4
  strength = Math.min(4, Math.ceil(strength / 1.5));

  const strengthMap = {
    0: { level: 0, label: '', color: '#999' },
    1: { level: 1, label: 'Weak', color: '#FF3B30' },
    2: { level: 2, label: 'Fair', color: '#FF9500' },
    3: { level: 3, label: 'Good', color: '#FFD60A' },
    4: { level: 4, label: 'Strong', color: '#34C759' },
  };

  return strengthMap[strength as keyof typeof strengthMap];
};

// Required field validation
export const validateRequired = (value: string): boolean => {
  return value.trim().length > 0;
};

// Minimum length validation
export const validateMinLength = (
  value: string,
  minLength: number,
): boolean => {
  return value.length >= minLength;
};

// Maximum length validation
export const validateMaxLength = (
  value: string,
  maxLength: number,
): boolean => {
  return value.length <= maxLength;
};
