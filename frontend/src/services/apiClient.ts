import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from 'axios';

export interface CustomAxiosRequestConfig extends InternalAxiosRequestConfig {
  _retry?: boolean;
  _retryCount?: number;
}

export interface ApiErrorResponse {
  error_code: string;
  message: string;
  details?: Record<string, unknown>;
  timestamp: string;
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';
const MAX_RETRIES = 3;
const INITIAL_RETRY_DELAY = 1000; // 1 second

export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000, // 15s timeout
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
});

// Helper for Exponential Backoff
const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

// Request Interceptor: Attach JWT Token & Correlation ID
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('access_token');
    if (token && config.headers) {
      config.headers.set('Authorization', `Bearer ${token}`);
    }
    return config;
  },
  (error: AxiosError) => Promise.reject(error)
);

// Response Interceptor: Retries, Token Rotation, Unified Errors
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError<ApiErrorResponse>) => {
    const originalRequest = error.config as CustomAxiosRequestConfig | undefined;

    if (!originalRequest) {
      return Promise.reject(error);
    }

    // 1. Automatic Token Refresh on 401 Unauthorized
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const refreshResponse = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });

          const newAccessToken = refreshResponse.data.access_token;
          localStorage.setItem('access_token', newAccessToken);

          if (originalRequest.headers) {
            originalRequest.headers.set('Authorization', `Bearer ${newAccessToken}`);
          }
          return apiClient(originalRequest);
        }
      } catch (refreshErr) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login?expired=true';
        return Promise.reject(refreshErr);
      }
    }

    // 2. Exponential Backoff Retry on Network Error or 5xx Server Error
    const isNetworkOr5xx =
      !error.response || (error.response.status >= 500 && error.response.status <= 599);

    originalRequest._retryCount = originalRequest._retryCount || 0;

    if (isNetworkOr5xx && originalRequest._retryCount < MAX_RETRIES) {
      originalRequest._retryCount += 1;
      const backoffDelay = INITIAL_RETRY_DELAY * Math.pow(2, originalRequest._retryCount - 1);
      await delay(backoffDelay);
      return apiClient(originalRequest);
    }

    // 3. Format Unified Error Message
    const formattedError = {
      status: error.response?.status || 500,
      code: error.response?.data?.error_code || 'NETWORK_ERROR',
      message:
        error.response?.data?.message ||
        error.message ||
        'An unexpected network error occurred.',
      details: error.response?.data?.details || {},
    };

    return Promise.reject(formattedError);
  }
);

// Helper factory to create Cancellable API Requests
export const createCancellableRequest = <T>(
  requestFn: (signal: AbortSignal) => Promise<T>
) => {
  const controller = new AbortController();
  const promise = requestFn(controller.signal);
  return { promise, cancel: () => controller.abort() };
};

export default apiClient;