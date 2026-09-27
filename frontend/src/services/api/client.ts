import axios, { AxiosError, InternalAxiosRequestConfig, AxiosResponse } from 'axios';
import { env } from '../../config/env';
import type { ApiErrorResponse } from '../../types';

/**
 * Centralized Axios client for all API communication.
 * Configured with base URL from environment, timeouts, and error handling.
 */
const apiClient = axios.create({
  baseURL: env.API_BASE_URL,
  timeout: 30000, // 30s — disease model inference can take time
  headers: {
    Accept: 'application/json',
  },
});

// Request interceptor for logging in development
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    if (env.IS_DEV) {
      console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
    }
    return config;
  },
  (error: AxiosError) => Promise.reject(error)
);

// Response interceptor for consistent error handling
apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError<ApiErrorResponse>) => {
    if (env.IS_DEV) {
      console.error('[API Error]', {
        url: error.config?.url,
        status: error.response?.status,
        data: error.response?.data,
      });
    }
    return Promise.reject(error);
  }
);

export default apiClient;

// ============================================================================
// Error Helpers
// ============================================================================

export interface ParsedApiError {
  code: string;
  message: string;
  fields?: Record<string, string[]>;
  status?: number;
}

/**
 * Extracts a human-readable error from an Axios error, handling both
 * API-formatted errors and network failures.
 */
export function parseApiError(error: unknown): ParsedApiError {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<ApiErrorResponse>;

    // Network error (no response)
    if (!axiosError.response) {
      return {
        code: 'NETWORK_ERROR',
        message:
          'Unable to connect to the agriculture service. Please make sure the backend is running and try again.',
      };
    }

    // Timeout
    if (axiosError.code === 'ECONNABORTED') {
      return {
        code: 'TIMEOUT',
        message: 'The request timed out. Please try again.',
      };
    }

    const { status, data } = axiosError.response;

    // API returned structured error
    if (data && typeof data === 'object' && 'error' in data && data.error) {
      return {
        code: data.error.code,
        message: data.error.message,
        fields: data.error.fields,
        status,
      };
    }

    // Fallback for unstructured responses
    const statusMessages: Record<number, string> = {
      400: 'Invalid request. Please check your input.',
      404: 'The requested resource was not found.',
      422: 'The request could not be processed.',
      500: 'A server error occurred. Please try again later.',
      503: 'The service is temporarily unavailable. Please try again later.',
    };

    return {
      code: `HTTP_${status}`,
      message: statusMessages[status] || `An unexpected error occurred (${status}).`,
      status,
    };
  }

  // Non-Axios error
  return {
    code: 'UNKNOWN_ERROR',
    message: 'An unexpected error occurred.',
  };
}
