/**
 * Centralized environment configuration.
 * All environment-dependent values are accessed through this module.
 */
export const env = {
  API_BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000',
  IS_DEV: import.meta.env.DEV,
  IS_PROD: import.meta.env.PROD,
} as const;
